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
    xl = json.load(open(f"{ROOT}/analysis/out_crosslineage.json"))
    rows = []

    for name, c in inf["contrast"].items():
        rows.append(row(f"opus5 {name}", c["est"], c["se"]["case"], c["n"]))
    for key, c in cm["premium"].items():
        rows.append(row(f"premium {key}", c["est"], c["se"], c["n"]))
    p = cm["pooled_small"]
    rows.append(row("premium pooled small models", p["est"], p["se"], p["n"]))
    for contrast, label in (("matched_struct", "GPT-6 Luna, structure-matched"),
                            ("matched_bare", "GPT-6 Luna, bare blocks")):
        c = xl["rows"].get(f"{xl['lineage']}|{contrast}")
        if c and c.get("est") is not None:
            rows.append(row(label, c["est"], c["se"], c["n"], c["bench"]))
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

    tex = [
        r"\begin{table}[t]", r"\centering",
        r"\caption{What each estimate can exclude. MDE is the smallest true effect the arm",
        r"would detect in four samples out of five at the two-sided 5\% level, computed as",
        r"$2.80\times\mathrm{SE}$ from the standard error each contrast reports. The final",
        r"column compares each estimate with its corresponding Claude benchmark.}",
        r"\label{tab:power}", r"\small", r"\begin{tabular}{lrrrrc}", r"\toprule",
        r"Estimate & $n$ & Est. & SE & MDE & Powered \\", r"\midrule"
    ]
    table_labels = {
        "opus5 matched_struct": "Structure-matched premium, Opus 5",
        "opus5 matched_bare": "Bare-block premium, Opus 5",
        "opus5 closing_sentence": "Cost of the peer closing sentence",
        "opus5 original_sentences": "Premium with both original closings",
        "opus5 para_free": "Cost of paraphrase one",
        "opus5 para_own": "Cost of paraphrase two",
        "premium sonnet5|guideline": "Premium, Sonnet 5, guideline present",
        "premium sonnet5|no guideline": "Premium, Sonnet 5, guideline removed",
        "premium haiku45|guideline": "Premium, Haiku 4.5, guideline present",
        "premium haiku45|no guideline": "Premium, Haiku 4.5, guideline removed",
        "premium opus5|guideline": "Premium, Opus 5, guideline present",
        "premium opus5|no guideline": "Premium, Opus 5, guideline removed",
        "premium pooled small models": "Premium, smaller models pooled",
        "guideline removal sonnet5": "Extra pull from removing guideline, Sonnet 5",
        "guideline removal haiku45": "Extra pull from removing guideline, Haiku 4.5",
        "guideline removal opus5": "Extra pull from removing guideline, Opus 5",
    }
    for r in rows:
        powered = "yes" if r["powered_for_bench"] else r"\textbf{no}"
        label = table_labels.get(r["label"], r["label"])
        tex.append(f"{label} & {r['n']} & ${r['est']:+.3f}$ & "
                   f"{r['se']:.3f} & {r['mde']:.3f} & {powered} " + "\\\\")
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(f"{ROOT}/analysis/out_power_table.tex", "w").write("\n".join(tex) + "\n")

    res = {"z": Z, "benchmark": BENCH, "rows": rows,
           "n_underpowered": len(small), "n_total": len(rows)}
    json.dump(res, open(f"{ROOT}/analysis/out_power.json", "w"), indent=1)


if __name__ == "__main__":
    main()
