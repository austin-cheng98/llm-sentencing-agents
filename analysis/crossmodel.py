"""Estimates per agent model, reported separately from the primary results."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, cluster_vcov, wild_bootstrap, factor_matrix, ROOT

MODELS = ["opus5", "sonnet5", "haiku45"]


def premium(recs, model, suf):
    d = [r for r in recs if r["model"] == model
         and r["arm"] in (f"peerdelta{suf}", f"tooldelta{suf}")]
    if len(d) < 24:
        return None
    y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
    peer = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
    X = np.column_stack([np.ones(len(y)), dl, peer, dl * peer, factor_matrix(d)])
    b = ols(X, y); cid = np.array([r["cid"] for r in d])
    return {"est": float(b[3]),
            "se": float(np.sqrt(cluster_vcov(X, y, b, cid)[3, 3])), "n": len(d)}


def guideline_effect(recs, model):
    d = [r for r in recs if r["model"] == model
         and r["arm"].startswith(("peerdelta", "tooldelta"))]
    y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
    ng = np.array([1.0 if r["arm"].endswith("_ng") else 0.0 for r in d])
    X = np.column_stack([np.ones(len(y)), dl, ng, dl * ng, factor_matrix(d)])
    b = ols(X, y); cid = np.array([r["cid"] for r in d])
    return {"guided_pull": float(b[1]), "extra": float(b[3]),
            "se": float(np.sqrt(cluster_vcov(X, y, b, cid)[3, 3])), "n": len(d)}


def pooled_small(recs):
    d = [r for r in recs if r["model"] in ("sonnet5", "haiku45")
         and r["arm"].startswith(("peerdelta", "tooldelta"))]
    y = np.array([r["dev"] for r in d]); dl = np.array([r["delta"] for r in d])
    peer = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
    ng = np.array([1.0 if r["arm"].endswith("_ng") else 0.0 for r in d])
    X = np.column_stack([np.ones(len(y)), dl, peer, ng, dl * peer, dl * ng,
                         factor_matrix(d)])
    b = ols(X, y); cid = np.array([r["cid"] for r in d])
    V = cluster_vcov(X, y, b, cid)
    _, p = wild_bootstrap(X, y, cid, 4, B=4999)
    return {"est": float(b[4]), "se": float(np.sqrt(V[4, 4])), "p": p, "n": len(d)}


def main():
    recs = [r for r in load() if r.get("delta") is not None]
    out = {"premium": {}, "guideline": {}}
    for m in MODELS:
        for suf, lab in (("", "guideline"), ("_ng", "no guideline")):
            r = premium(recs, m, suf)
            if r:
                out["premium"][f"{m}|{lab}"] = r
                print(f"  {m:8s} premium, {lab:13s} {r['est']:+.3f} "
                      f"(se {r['se']:.3f}) n={r['n']}")
    print()
    for m in MODELS:
        r = guideline_effect(recs, m)
        out["guideline"][m] = r
        print(f"  {m:8s} pull with guideline {r['guided_pull']:+.3f}   "
              f"extra without it {r['extra']:+.3f} (se {r['se']:.3f})")
    ps = pooled_small(recs)
    out["pooled_small"] = ps
    print(f"\n  smaller models pooled premium {ps['est']:+.3f} "
          f"(se {ps['se']:.3f}, p={ps['p']:.3f}, n={ps['n']})")
    json.dump(out, open(f"{ROOT}/analysis/out_crossmodel.json", "w"), indent=1)


if __name__ == "__main__":
    main()
