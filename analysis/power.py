"""Compute minimum detectable effects."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

Z = 1.959963985 + 0.8416212336
BENCH = 0.323


def row(label, est, se, n, bench=BENCH):
    mde = Z * se
    lo, hi = est - 1.96 * se, est + 1.96 * se
    return {"label": label, "est": est, "se": se, "n": n, "mde": mde,
            "ci": [lo, hi], "excludes_bench": bool(hi < bench),
            "powered_for_bench": bool(mde <= bench)}


def main():
    inf = json.load(open(f"{ROOT}/analysis/out_inference.json"))
    cm = json.load(open(f"{ROOT}/analysis/out_crossmodel.json"))
    rows = []

    for name, c in inf["contrast"].items():
        rows.append(row(f"opus5 {name}", c["est"], c["se"]["case"], c["n"]))
    for key, c in cm["premium"].items():
        rows.append(row(f"premium {key}", c["est"], c["se"], c["n"]))
    p = cm["pooled_small"]
    rows.append(row("premium pooled small models", p["est"], p["se"], p["n"]))
    for m, g in cm["guideline"].items():
        rows.append(row(f"guideline removal {m}", g["extra"], g["se"], g["n"]))

    print(f"{'estimate':34s} {'n':>4s} {'est':>7s} {'se':>6s} {'MDE':>6s}  "
          f"{'95% CI':>17s}  powered")
    for r in sorted(rows, key=lambda r: r["n"]):
        flag = "yes" if r["powered_for_bench"] else "NO"
        print(f"{r['label']:34s} {r['n']:4d} {r['est']:+7.3f} {r['se']:6.3f} "
              f"{r['mde']:6.3f}  [{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}]  {flag}")

    small = [r for r in rows if not r["powered_for_bench"]]
    print(f"\n{len(small)} of {len(rows)} estimates cannot detect a premium the size of "
          f"the {BENCH:+.2f} measured on Opus 5 with bare blocks:")
    for r in small:
        print(f"  {r['label']:34s} needs a true premium of {r['mde']:+.2f} or larger")

    res = {"z": Z, "benchmark": BENCH, "rows": rows,
           "n_underpowered": len(small), "n_total": len(rows)}
    json.dump(res, open(f"{ROOT}/analysis/out_power.json", "w"), indent=1)


if __name__ == "__main__":
    main()
