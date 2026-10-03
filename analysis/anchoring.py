"""Main pull and premium estimates."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (load, ols, cluster_vcov, wild_bootstrap, factor_matrix,
                    pull, PRIMARY, ROOT)

ANCHOR = ["peerdelta", "tooldelta", "clerdelta_ng", "peerdelta_ng", "tooldelta_ng"]


def cells(recs):
    out = {}
    for arm in ANCHOR:
        d = [r for r in recs if r["arm"] == arm]
        if len(d) >= 8:
            b, se = pull(d)
            out[arm] = {"n": len(d), "pull": b, "se": se}
    return out


def premium(recs, suf=""):
    """Estimate the peer premium."""
    d = [r for r in recs if r["arm"] in (f"peerdelta{suf}", f"tooldelta{suf}")]
    y = np.array([r["dev"] for r in d])
    dl = np.array([r["delta"] for r in d])
    peer = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
    X = np.column_stack([np.ones(len(y)), dl, peer, dl * peer, factor_matrix(d)])
    b = ols(X, y)
    cid = np.array([r["cid"] for r in d])
    V = cluster_vcov(X, y, b, cid)
    _, p = wild_bootstrap(X, y, cid, 3)
    return {"est": float(b[3]), "se": float(np.sqrt(V[3, 3])), "p": p,
            "n": len(d), "clusters": int(len(set(cid)))}


def guideline_effect(recs):
    """Estimate the guideline effect."""
    d = [r for r in recs if r["arm"].startswith(("peerdelta", "tooldelta"))]
    y = np.array([r["dev"] for r in d])
    dl = np.array([r["delta"] for r in d])
    peer = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
    ng = np.array([1.0 if r["arm"].endswith("_ng") else 0.0 for r in d])
    X = np.column_stack([np.ones(len(y)), dl, peer, ng, dl * peer, dl * ng,
                         peer * ng, dl * peer * ng, factor_matrix(d)])
    b = ols(X, y)
    cid = np.array([r["cid"] for r in d])
    V = cluster_vcov(X, y, b, cid)
    _, p5 = wild_bootstrap(X, y, cid, 5)
    _, p7 = wild_bootstrap(X, y, cid, 7)
    return {"extra": float(b[5]), "se": float(np.sqrt(V[5, 5])), "p": p5,
            "triple": float(b[7]), "triple_se": float(np.sqrt(V[7, 7])),
            "triple_p": p7, "n": len(d)}


def main():
    recs = load(model=PRIMARY)
    anchor = [r for r in recs if r.get("delta") is not None]
    res = {"cells": cells(anchor)}
    print(f"{len(recs)} decisions on {PRIMARY}, {len(anchor)} in anchor arms\n")
    for a, v in res["cells"].items():
        print(f"  {a:15s} n={v['n']:3d}  pull={v['pull']:+.3f} (se {v['se']:.3f})")
    res["premium_guideline"] = premium(anchor, "")
    res["premium_no_guideline"] = premium(anchor, "_ng")
    for k in ("premium_guideline", "premium_no_guideline"):
        v = res[k]
        print(f"\n  {k}: {v['est']:+.3f} (se {v['se']:.3f}, p={v['p']:.3f}, n={v['n']})")
    g = guideline_effect(anchor)
    res["guideline_effect"] = g
    print(f"\n  extra pull without a guideline: {g['extra']:+.3f} "
          f"(se {g['se']:.3f}, p={g['p']:.4f})")
    print(f"  triple interaction: {g['triple']:+.3f} "
          f"(se {g['triple_se']:.3f}, p={g['triple_p']:.3f})")
    json.dump(res, open(f"{ROOT}/analysis/out_anchoring.json", "w"), indent=1)


if __name__ == "__main__":
    main()
