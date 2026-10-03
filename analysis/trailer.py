"""Analyze closing-sentence effects."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, cluster_vcov, wild_bootstrap, PRIMARY, ROOT

F4 = ("severity", "prior", "remorse", "cooperation")


def pull(d):
    y = np.array([r["dev"] for r in d]); x = np.array([r["delta"] for r in d])
    F = np.column_stack([[r[f] for r in d] for f in F4]).astype(float)
    X = np.column_stack([np.ones(len(y)), x, F])
    b = ols(X, y)
    se = np.sqrt(cluster_vcov(X, y, b, np.array([r["cid"] for r in d]))[1, 1])
    return {"pull": float(b[1]), "se": float(se), "n": len(d)}


def contrast(recs, a1, a2):
    """Compute the pull difference."""
    d = [r for r in recs if r["arm"] in (a1, a2)]
    shared = ({r["judge"] for r in d if r["arm"] == a1} &
              {r["judge"] for r in d if r["arm"] == a2})
    d = [r for r in d if r["judge"] in shared]
    y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
    g = np.array([1.0 if r["arm"] == a1 else 0.0 for r in d])
    F = np.column_stack([[r[f] for r in d] for f in F4]).astype(float)
    X = np.column_stack([np.ones(len(y)), dl, g, dl * g, F])
    b = ols(X, y)
    cid = np.array([r["cid"] for r in d])
    V = cluster_vcov(X, y, b, cid)
    unit = np.array([f"{r['judge']}|{r['delta']}" for r in d])
    _, p = wild_bootstrap(X, y, cid, 3, B=4999)
    return {"est": float(b[3]), "se": float(np.sqrt(V[3, 3])),
            "se_assign": float(np.sqrt(cluster_vcov(X, y, b, unit)[3, 3])),
            "p": p, "n": len(d)}


def by_model(recs):
    """Estimate the premium by model."""
    out = {}
    for m in ("opus5", "sonnet5", "haiku45"):
        d = [r for r in recs if r["model"] == m
             and r["arm"] in ("peerbare_ng", "toolbare_ng")]
        sh = ({r["judge"] for r in d if r["arm"] == "peerbare_ng"} &
              {r["judge"] for r in d if r["arm"] == "toolbare_ng"})
        d = [r for r in d if r["judge"] in sh]
        if len(d) < 24:
            continue
        y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
        g = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
        F = np.column_stack([[r[f] for r in d] for f in F4]).astype(float)
        X = np.column_stack([np.ones(len(y)), dl, g, dl * g, F])
        b = ols(X, y)
        cid = np.array([r["cid"] for r in d])
        cell = np.array([f"{r['judge']}|{r['cid']}" for r in d])
        rng = np.random.default_rng(19)
        draws = []
        for _ in range(2999):
            gv = g.copy()
            for c in np.unique(cell):
                msk = cell == c
                if msk.sum() > 1 and rng.random() < 0.5:
                    gv[msk] = 1.0 - gv[msk]
            draws.append(ols(np.column_stack(
                [np.ones(len(y)), dl, gv, dl * gv, F]), y)[3])
        out[m] = {"est": float(b[3]),
                  "se": float(np.sqrt(cluster_vcov(X, y, b, cid)[3, 3])), "n": len(d),
                  "null_p95": float(np.percentile(np.abs(draws), 95))}
    return out


def main():
    allm = [r for r in load() if r.get("delta") is not None]
    recs = [r for r in load(model=PRIMARY) if r.get("delta") is not None]
    out = {"pull": {}, "contrast": {}}
    print("pull by arm")
    for arm in ("peerbare_ng", "toolbare_ng", "peerdelta_ng", "tooldelta_ng"):
        d = [r for r in recs if r["arm"] == arm]
        if len(d) >= 16:
            out["pull"][arm] = pull(d)
            v = out["pull"][arm]
            print(f"  {arm:14s} {v['pull']:+.3f} (se {v['se']:.3f}) n={v['n']}")

    pairs = [("matched", "peerbare_ng", "toolbare_ng"),
             ("original", "peerdelta_ng", "tooldelta_ng"),
             ("peer_trailer", "peerdelta_ng", "peerbare_ng"),
             ("tool_trailer", "tooldelta_ng", "toolbare_ng")]
    print("\ncontrasts")
    for name, a1, a2 in pairs:
        c = contrast(recs, a1, a2)
        out["contrast"][name] = c
        print(f"  {name:14s} {a1} minus {a2}: {c['est']:+.3f} "
              f"(se {c['se']:.3f}, assignment se {c['se_assign']:.3f}, "
              f"p={c['p']:.4f}, n={c['n']})")
    bm = by_model(allm)
    out["by_model"] = bm
    if bm:
        print("\nmatched-prompt premium by model")
        for m, v in bm.items():
            print(f"  {m:8s} {v['est']:+.3f} (se {v['se']:.3f}) n={v['n']}")
    json.dump(out, open(f"{ROOT}/analysis/out_trailer.json", "w"), indent=1)


if __name__ == "__main__":
    main()
