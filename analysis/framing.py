"""Compare attributions and no-anchor behavior."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (load, ols, cluster_vcov, wild_bootstrap, factor_matrix,
                    PRIMARY, ROOT, FACTORS)


def three_way(recs):
    arms = ["peerdelta_ng", "tooldelta_ng", "clerdelta_ng"]
    d = [r for r in recs if r["arm"] in arms]
    y = np.array([r["dev"] for r in d])
    dl = np.array([r["delta"] for r in d])
    peer = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
    cler = np.array([1.0 if r["arm"].startswith("cler") else 0.0 for r in d])
    X = np.column_stack([np.ones(len(y)), dl, peer, cler, dl * peer, dl * cler,
                         factor_matrix(d)])
    b = ols(X, y)
    cid = np.array([r["cid"] for r in d])
    V = cluster_vcov(X, y, b, cid)
    _, pp = wild_bootstrap(X, y, cid, 4, B=4999)
    _, pc = wild_bootstrap(X, y, cid, 5, B=4999)
    return {"pull_tool": float(b[1]),
            "peer_vs_tool": float(b[4]), "peer_se": float(np.sqrt(V[4, 4])), "peer_p": pp,
            "cler_vs_tool": float(b[5]), "cler_se": float(np.sqrt(V[5, 5])), "cler_p": pc,
            "n": len(d)}


def no_anchor(recs):
    """Summarize no-anchor outcomes."""
    out = {}
    for arm in ("nohist", "nohist_ng"):
        d = [r for r in recs if r["arm"] == arm and r["step"] < 16]
        if len(d) < 16:
            continue
        cells = {}
        for r in d:
            cells.setdefault(r["cid"], []).append(r["sentence"] / r["mid"])
        sds = [np.std(v, ddof=1) for v in cells.values() if len(v) >= 3]
        y = np.array([np.log(max(r["sentence"], 1)) for r in d])
        X = np.column_stack([np.ones(len(y)), factor_matrix(d)])
        b = ols(X, y)
        out[arm] = {"n": len(d),
                    "mean_dev": float(np.mean([r["dev"] for r in d])),
                    "sd_between": float(np.mean(sds)) if sds else None,
                    "severity_pct": float((np.exp(b[1]) - 1) * 100)}
    return out


def main():
    recs = [r for r in load(model=PRIMARY)]
    anchor = [r for r in recs if r.get("delta") is not None]
    tw = three_way(anchor)
    print("three attributions, guideline removed")
    print(f"  pull, statistical forecast     {tw['pull_tool']:+.3f}")
    print(f"  peer bench minus forecast      {tw['peer_vs_tool']:+.3f} "
          f"(se {tw['peer_se']:.3f}, p={tw['peer_p']:.3f})")
    print(f"  docketing minus forecast       {tw['cler_vs_tool']:+.3f} "
          f"(se {tw['cler_se']:.3f}, p={tw['cler_p']:.3f})")
    na = no_anchor(recs)
    print("\nno numbers shown")
    for arm, v in na.items():
        lab = "guideline removed" if arm.endswith("_ng") else "guideline present"
        print(f"  {lab:20s} n={v['n']:3d}  mean deviation {v['mean_dev']:+.3f}  "
              f"between-agent SD {v['sd_between']:.3f}")
    json.dump({"three_way": tw, "no_anchor": na},
              open(f"{ROOT}/analysis/out_framing.json", "w"), indent=1)


if __name__ == "__main__":
    main()
