"""Yoked contrasts, three clustering units, and two placebo floors.
"""
import sys, os, json, glob, collections, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, cluster_vcov, PRIMARY, ROOT, factor_matrix

F4 = ("severity", "prior", "remorse", "cooperation")


def fm(d):
    return factor_matrix(d)


def contrast(recs, a1, a2, B=9999, seed=17):
    """Difference in pull. Null from swapping labels within an agent-case cell."""
    d = [r for r in recs if r["arm"] in (a1, a2)]
    # keep only agents contributing to both arms, so every cell is genuinely
    # paired and the label-swap null matches the estimator
    shared = ({r["judge"] for r in d if r["arm"] == a1} &
              {r["judge"] for r in d if r["arm"] == a2})
    d = [r for r in d if r["judge"] in shared]
    if len(d) < 32:
        return None
    y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
    g = np.array([1.0 if r["arm"] == a1 else 0.0 for r in d])
    F = fm(d)
    cell = np.array([f"{r['judge']}|{r['cid']}" for r in d])

    def est(gv):
        return ols(np.column_stack([np.ones(len(y)), dl, gv, dl * gv, F]), y)[3]

    obs = est(g)
    X = np.column_stack([np.ones(len(y)), dl, g, dl * g, F])
    b = ols(X, y)
    ses = {u: float(np.sqrt(cluster_vcov(X, y, b, np.array(v))[3, 3]))
           for u, v in (("case", [r["cid"] for r in d]),
                        ("agent", [r["judge"] for r in d]),
                        ("assignment", [f"{r['judge']}|{r['delta']}" for r in d]))}
    rng = np.random.default_rng(seed)
    cnt, draws = 0, []
    for _ in range(B):
        gv = g.copy()
        for c in np.unique(cell):
            m = cell == c
            if m.sum() > 1 and rng.random() < 0.5:
                gv[m] = 1.0 - gv[m]
        e = est(gv); draws.append(e)
        if abs(e) >= abs(obs) - 1e-12:
            cnt += 1
    return {"est": float(obs), "se": ses, "p": (cnt + 1) / (B + 1),
            "null_sd": float(np.std(draws, ddof=1)),
            "null_p95": float(np.percentile(np.abs(draws), 95)), "n": len(d)}


def between_agent_floor(recs, arms):
    """Split an arm's agents in half. Bounds a between-agent comparison."""
    out = []
    for arm in arms:
        d = [r for r in recs if r["arm"] == arm]
        js = sorted({r["judge"] for r in d})
        if len(js) < 4:
            continue
        for A in itertools.combinations(js, len(js) // 2):
            y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
            g = np.array([1.0 if r["judge"] in A else 0.0 for r in d])
            out.append(float(ols(np.column_stack(
                [np.ones(len(y)), dl, g, dl * g, fm(d)]), y)[3]))
    return out


def decoding_noise():
    """Spread across repeat draws on a byte-identical prompt."""
    path = os.path.join(ROOT, "data", "repeats.jsonl")
    if not os.path.exists(path):
        return {"cells": 0, "sd": None}
    raw = [json.loads(l) for l in open(path) if l.strip()]
    by = collections.defaultdict(list)
    for r in raw:
        if r["ok"] and r.get("delta") is not None:
            by[(r["model"], r["arm"], r["judge"], r["step"])].append(r["sentence"] / r["mid"])
    reps = [v for v in by.values() if len(v) > 1]
    return {"cells": len(reps),
            "sd": float(np.mean([np.std(v, ddof=1) for v in reps])) if reps else None}


if __name__ == "__main__":
    recs = [r for r in load(model=PRIMARY) if r.get("delta") is not None]
    res = {"contrast": {}}
    pairs = [("matched_struct", "peermatch_ng", "toolbare_ng"),
             ("matched_bare", "peerbare_ng", "toolbare_ng"),
             ("closing_sentence", "peerdelta_ng", "peerbare_ng"),
             ("para_free", "parafree_ng", "peerbare_ng"),
             ("para_own", "paraown_ng", "peerbare_ng"),
             ("original_sentences", "peerdelta_ng", "tooldelta_ng")]
    for name, a1, a2 in pairs:
        c = contrast(recs, a1, a2)
        if c:
            res["contrast"][name] = c
            print(f"  {name:17s} {c['est']:+.3f}  se(case {c['se']['case']:.3f}, "
                  f"agent {c['se']['agent']:.3f})  RI p={c['p']:.4f}  "
                  f"null p95 {c['null_p95']:.3f}  n={c['n']}")
    # every peer-side arm measured as a premium against the same bare forecast,
    # so the erasure claim is read at the level of the premium and not of pull
    res["vs_bare_forecast"] = {}
    for arm in ("peerbare_ng", "peermatch_ng", "parafree_ng", "paraown_ng",
                "peerdelta_ng"):
        c = contrast(recs, arm, "toolbare_ng")
        if c:
            res["vs_bare_forecast"][arm] = c
            print(f"  {arm:14s} vs bare forecast  {c['est']:+.3f}  "
                  f"RI p={c['p']:.4f}  null p95 {c['null_p95']:.3f}  n={c['n']}")
    fl = between_agent_floor(recs, ["peerbare_ng", "toolbare_ng", "peerdelta_ng",
                                    "tooldelta_ng", "clerdelta_ng"])
    res["between_agent_floor"] = {"n": len(fl), "sd": float(np.std(fl, ddof=1)),
                                  "p95": float(np.percentile(np.abs(fl), 95))}
    res["decoding"] = decoding_noise()
    print(f"\n  between-agent floor: sd {res['between_agent_floor']['sd']:.3f}, "
          f"p95 {res['between_agent_floor']['p95']:.3f} over {len(fl)} splits")
    print(f"  decoding noise: within-cell SD {res['decoding']['sd']:.3f} "
          f"over {res['decoding']['cells']} repeated cells")
    json.dump(res, open(f"{ROOT}/analysis/out_inference.json", "w"), indent=1)
