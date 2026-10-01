"""Checks that the design survived contact with the data."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ROOT, FACTORS


def main():
    recs = load()
    cells = {}
    for r in recs:
        if r.get("peer_vals"):
            cells.setdefault((r["model"], r["judge"], r["cid"]), {})[r["arm"]] = \
                tuple(r["peer_vals"])
    paired = {k: v for k, v in cells.items() if len(v) > 1}
    mism = sum(1 for v in paired.values() if len({tuple(x) for x in v.values()}) > 1)

    d = [r for r in recs if r.get("delta") is not None]
    bal = {}
    for f in FACTORS:
        by = collections.defaultdict(list)
        for r in d:
            by[r["delta"]].append(r[f])
        bal[f] = {str(k): sum(v) / len(v) for k, v in sorted(by.items())}
    worst = max(abs(x - 0.5) for v in bal.values() for x in v.values())

    print(f"  decisions: {len(recs)}")
    print(f"  yoked cells compared: {len(paired)}, numbers differing: {mism}")
    print(f"  largest departure from factor balance across displacements: {worst:.3f}")
    for f, v in bal.items():
        print(f"    {f:12s} " + "  ".join(f"{k}:{x:.2f}" for k, x in v.items()))
    json.dump({"n": len(recs), "paired_cells": len(paired), "mismatched": mism,
               "worst_imbalance": worst, "balance": bal},
              open(f"{ROOT}/analysis/out_integrity.json", "w"), indent=1)


if __name__ == "__main__":
    main()
