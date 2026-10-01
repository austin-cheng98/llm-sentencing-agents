"""Measure how much unguided spread depends on one agent."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, PRIMARY, ROOT


ARM = "nohist_ng"


def spread(recs, drop=None):
    d = [r for r in recs if r["arm"] == ARM and r["step"] < 16
         and r["judge"] != drop]
    bycase = {}
    for r in d:
        bycase.setdefault(r["cid"], []).append(r["sentence"] / r["mid"])
    vals = [np.std(v, ddof=1) for v in bycase.values() if len(v) > 1]
    return float(np.mean(vals)), len(vals)


def main():
    recs = load(model=PRIMARY)
    judges = sorted({r["judge"] for r in recs if r["arm"] == ARM})
    full, ncase = spread(recs)
    loo = {}
    print(f"between-agent spread in {ARM}: {full:.3f} over {ncase} cases, "
          f"agents {judges}")
    for j in judges:
        s, n = spread(recs, drop=j)
        loo[j] = s
        print(f"  dropping {j}: {s:.3f} over {n} cases")
    res = {"arm": ARM, "full": full, "loo": loo,
           "range": [min(loo.values()), max(loo.values())]}
    json.dump(res, open(f"{ROOT}/analysis/out_dispersion_loo.json", "w"), indent=1)


if __name__ == "__main__":
    main()
