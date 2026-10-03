"""Analyze memory arms."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, cluster_vcov, factor_matrix, PRIMARY, ROOT


def drift(recs, arm):
    """Estimate drift across positions."""
    d = [r for r in recs if r["arm"] == arm and r["step"] < 16]
    if len(d) < 20:
        return None
    y = np.array([r["dev"] for r in d])
    t = np.array([r["step"] for r in d], float)
    X = np.column_stack([np.ones(len(y)), t, factor_matrix(d)])
    b = ols(X, y)
    se = np.sqrt(cluster_vcov(X, y, b, np.array([r["cid"] for r in d]))[1, 1])
    return {"per_case": float(b[1]), "over_16": float(b[1] * 16),
            "se_16": float(se * 16), "n": len(d)}


def reexposure(recs, arm):
    """Estimate change on returning cases."""
    d = [r for r in recs if r["arm"] == arm]
    first = {(r["judge"], r["cid"]): r for r in d if r["step"] < 16}
    sh = [(r["sentence"] - first[(r["judge"], r["cid"])]["sentence"]) / r["mid"]
          for r in d if r["step"] >= 16 and (r["judge"], r["cid"]) in first]
    if len(sh) < 4:
        return None
    p = np.array(sh)
    return {"mean": float(p.mean()), "se": float(p.std(ddof=1) / np.sqrt(len(p))),
            "mean_abs": float(np.abs(p).mean()), "n": len(p)}


def spread(recs, arm):
    d = [r for r in recs if r["arm"] == arm]
    cells = {}
    for r in d:
        cells.setdefault(r["cid"], []).append(r["sentence"] / r["mid"])
    sds = [np.std(v, ddof=1) for v in cells.values() if len(v) >= 3]
    return {"sd": float(np.mean(sds)), "cases": len(sds)} if sds else None


def paired_gap(recs):
    a = {(r["judge"][-1], r["step"]): r for r in recs if r["arm"] == "ownhist"}
    b = {(r["judge"][-1], r["step"]): r for r in recs if r["arm"] == "nohist"}
    ks = sorted(set(a) & set(b))
    if len(ks) < 10:
        return None
    diff = np.array([(a[k]["sentence"] - b[k]["sentence"]) / a[k]["mid"] for k in ks])
    return {"mean": float(diff.mean()),
            "se": float(diff.std(ddof=1) / np.sqrt(len(diff))), "n": len(ks)}


def main():
    recs = load(model=PRIMARY)
    out = {}
    for arm in ("nohist", "ownhist"):
        d, rx, sp = drift(recs, arm), reexposure(recs, arm), spread(recs, arm)
        out[arm] = {"drift": d, "reexposure": rx, "spread": sp}
        print(f"\n  {arm}")
        if d:
            print(f"    drift over 16 cases  {d['over_16']:+.3f} (se {d['se_16']:.3f})")
        if rx:
            print(f"    returning cases      {rx['mean']:+.3f} (se {rx['se']:.3f}), n={rx['n']}")
        if sp:
            print(f"    between-agent SD     {sp['sd']:.3f}")
    g = paired_gap(recs)
    out["paired_gap"] = g
    if g:
        print(f"\n  own-memory minus no-memory: {g['mean']:+.3f} (se {g['se']:.3f}, n={g['n']})")
    json.dump(out, open(f"{ROOT}/analysis/out_memory.json", "w"), indent=1)


if __name__ == "__main__":
    main()
