"""Live cascade estimates."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, cluster_vcov, PRIMARY, ROOT

F4 = ("severity", "prior", "remorse", "cooperation")


def rows(recs):
    d = [r for r in recs if r["arm"] == "cascade_ng" and r["ok"]]
    out = []
    for r in d:
        pv = r.get("peer_vals") or []
        out.append({"cid": r["cid"], "judge": r["judge"], "pos": len(pv), "pv": pv,
                    "sent": r["sentence"], "mid": r["mid"], "dev": r["dev"],
                    "peer_mean": (np.mean(pv) / r["mid"]) if pv else None,
                    "conf": r.get("confidence")})
    return out


def following(rs):
    """Estimate following of the observed peer mean."""
    d = [r for r in rs if r["peer_mean"] is not None]
    if len(d) < 20:
        return None
    y = np.array([r["dev"] for r in d])
    x = np.array([r["peer_mean"] - 1.0 for r in d])
    g = np.array([r["cid"] for r in d])
    cids = sorted(set(g))
    D = np.column_stack([[1.0 if r["cid"] == c else 0.0 for r in d] for c in cids[1:]])
    out = {"n": len(d)}
    for lab, X in (("plain", np.column_stack([np.ones(len(y)), x])),
                   ("case_fe", np.column_stack([np.ones(len(y)), x, D]))):
        b = ols(X, y)
        out[lab] = {"beta": float(b[1]),
                    "se": float(np.sqrt(cluster_vcov(X, y, b, g)[1, 1]))}
    ex = sum(1 for r in d if r["sent"] in (r.get("pv") or []))
    out["exact_copy"] = ex / len(d)
    return out


def position(rs):
    """Summarize outcomes by speaking position."""
    out = {}
    for p in sorted({r["pos"] for r in rs}):
        v = [r["dev"] for r in rs if r["pos"] == p]
        if len(v) >= 4:
            out[p] = {"n": len(v), "mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))}
    return out


def convergence(rs):
    """Compare early and late within-case spread."""
    early, late = [], []
    for c in {r["cid"] for r in rs}:
        g = sorted([r for r in rs if r["cid"] == c], key=lambda r: r["pos"])
        if len(g) < 4:
            continue
        early.append(np.std([x["sent"] / x["mid"] for x in g[:2]], ddof=1))
        late.append(np.std([x["sent"] / x["mid"] for x in g[-2:]], ddof=1))
    if not early:
        return None
    return {"early_sd": float(np.mean(early)), "late_sd": float(np.mean(late)),
            "cases": len(early),
            "ratio": float(np.mean(late) / np.mean(early)) if np.mean(early) else None}


def placebo(recs, reps=400, seed=3):
    """Estimate cascade statistics after shuffling agents within case."""
    base = [r for r in recs if r["arm"] == "nohist_ng" and r["step"] < 16]
    bycase = {}
    for r in base:
        bycase.setdefault(r["cid"], []).append(r)
    rng = np.random.default_rng(seed)
    copies, betas, fes = [], [], []
    for _ in range(reps):
        ys, xs, cs, nc, tot = [], [], [], 0, 0
        for g in bycase.values():
            if len(g) < 3:
                continue
            o = list(g)
            rng.shuffle(o)
            seen = []
            for r in o:
                if seen:
                    tot += 1
                    if r["sentence"] in [q["sentence"] for q in seen]:
                        nc += 1
                    ys.append(r["dev"]); cs.append(r["cid"])
                    xs.append(np.mean([q["sentence"] for q in seen]) / r["mid"] - 1)
                seen.append(r)
        copies.append(nc / tot)
        ys = np.array(ys); xs = np.array(xs)
        betas.append(ols(np.column_stack([np.ones(len(ys)), xs]), ys)[1])
        ks = sorted(set(cs))
        D = np.column_stack([[1.0 if c == k else 0.0 for c in cs] for k in ks[1:]])
        fes.append(ols(np.column_stack([np.ones(len(ys)), xs, D]), ys)[1])
    return {"copy": float(np.mean(copies)),
            "beta": float(np.mean(betas)),
            "beta_lo": float(np.percentile(betas, 2.5)),
            "beta_hi": float(np.percentile(betas, 97.5)),
            "beta_fe": float(np.mean(fes)),
            "beta_fe_lo": float(np.percentile(fes, 2.5)),
            "beta_fe_hi": float(np.percentile(fes, 97.5))}


def first_speaker_gap(recs):
    """Compare first cascade speakers with the no-peer arm."""
    first = [r for r in recs if r["arm"] == "cascade_ng" and not (r.get("peer_vals") or [])]
    nopeer = [r for r in recs if r["arm"] == "nohist_ng" and r["step"] < 16]
    cases = sorted({r["cid"] for r in first} & {r["cid"] for r in nopeer})
    d = [r for r in first + nopeer if r["cid"] in cases]
    y = np.array([r["dev"] for r in d])
    g = np.array([1.0 if r["arm"] == "cascade_ng" else 0.0 for r in d])
    D = np.column_stack([[1.0 if r["cid"] == c else 0.0 for r in d] for c in cases[1:]])
    X = np.column_stack([np.ones(len(y)), g, D])
    b = ols(X, y)
    V = cluster_vcov(X, y, b, np.array([r["cid"] for r in d]))
    return {"gap": float(b[1]), "se": float(np.sqrt(V[1, 1])),
            "n_first": len(first), "n_nopeer": len(nopeer), "cases": len(cases)}


def main():
    recs = load(model=PRIMARY)
    rs = rows(recs)
    print(f"cascade decisions: {len(rs)}")
    if len(rs) < 20:
        print("  not enough yet")
        return
    res = {"n": len(rs)}
    f = following(rs)
    if f:
        res["following"] = f
        print(f"  following, no fixed effects: beta={f['plain']['beta']:+.3f} "
              f"(se {f['plain']['se']:.3f}, n={f['n']})")
        print(f"  following, case fixed effects: beta={f['case_fe']['beta']:+.3f} "
              f"(se {f['case_fe']['se']:.3f})   [leave-out-mean bias]")
        print(f"  decisions exactly copying a predecessor: {100*f['exact_copy']:.0f}%")
    unan = sum(1 for c in {r["cid"] for r in rs}
               if len({r["sent"] for r in rs if r["cid"] == c}) == 1)
    res["unanimous"] = unan
    print(f"  cases where every agent returns the same sentence: {unan}/16")
    bypos = {}
    for k in range(1, 6):
        dd = [r for r in rs if r["pos"] == k]
        if dd:
            bypos[k] = sum(1 for r in dd if r["sent"] in (r.get("pv") or [])) / len(dd)
    res["copy_by_pos"] = bypos
    print("  copying by position: " +
          ", ".join(f"{k}:{100*v:.0f}%" for k, v in bypos.items()))
    pl = placebo(recs)
    res["placebo"] = pl
    print(f"  placebo on independent agents: copying {100*pl['copy']:.0f}%, "
          f"beta {pl['beta']:+.2f} [{pl['beta_lo']:+.2f},{pl['beta_hi']:+.2f}]")
    res["position"] = position(rs)
    print("  by speaking position (0 = decides blind)")
    for p, v in res["position"].items():
        print(f"    pos {p}: n={v['n']:3d}  mean dev {v['mean']:+.3f}  sd {v['sd']:.3f}")
    cv = convergence(rs)
    res["convergence"] = cv
    if cv:
        print(f"  within-case spread: first two {cv['early_sd']:.3f}, "
              f"last two {cv['late_sd']:.3f}, ratio {cv['ratio']:.2f} "
              f"over {cv['cases']} cases")
    base = [r for r in recs if r["arm"] == "nohist_ng" and r["step"] < 16]
    if base:
        cells = {}
        for r in base:
            cells.setdefault(r["cid"], []).append(r["sentence"] / r["mid"])
        sd = np.mean([np.std(v, ddof=1) for v in cells.values() if len(v) >= 3])
        res["baseline_sd"] = float(sd)
        print(f"  no-interaction baseline spread on the same cases: {sd:.3f}")
    fs = first_speaker_gap(recs)
    res["first_speaker"] = fs
    print("\n=== first speaker against the no-peer arm ===")
    print(f"  gap {fs['gap']:+.3f} (SE {fs['se']:.3f}) over {fs['cases']} cases")
    json.dump(res, open(f"{ROOT}/analysis/out_cascade.json", "w"), indent=1)


if __name__ == "__main__":
    main()
