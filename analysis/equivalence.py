"""Is the peer premium still there when both sources are told to know the same thing?

The premium contrasts two blocks that differ in attribution, but nothing in the
earlier arms stops them differing in how much the source could plausibly know:
a bench of judges has seen a case, a fitted model has seen a table. A reader can
therefore read the premium as deference to better information rather than as
anything about peers.

The equivalence arms settle that by assertion. peereqv_ng and tooleqv_ng carry a
sentence that is identical word for word, stating that the figures came from this
case file and from nothing else, so the header and the row labels are the only
remaining contrast. peerrel_ng and toolrel_ng add a second identical sentence
asserting past accuracy, which moves stated reliability without moving either
attribution or information.

Pre-registered in experiment/prereg-equivalence.md and frozen before collection.
The primary test, the estimator, the null, and the decision rule are all fixed
there; this file implements them and adds nothing that was not written down.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, PRIMARY, ROOT
from robustness import paired, premium, dev

Z = 1.959963985 + 0.8416212336   # MDE multiplier, as in power.py

# The primary contrast, then the reliability pair, then the benchmarks the
# primary result is compared against. Order is the pre-registered order.
PAIRS = [("equivalence", "peereqv_ng", "tooleqv_ng"),
         ("reliability", "peerrel_ng", "toolrel_ng"),
         ("matched_struct", "peermatch_ng", "toolbare_ng"),
         ("matched_bare", "peerbare_ng", "toolbare_ng")]

# Does asserting past accuracy change the pull within a source type? Same
# estimator, with the reliability sentence rather than the source as the contrast.
WITHIN = [("peer_reliability", "peerrel_ng", "peereqv_ng"),
          ("tool_reliability", "toolrel_ng", "tooleqv_ng")]


def contrast(recs, name, a1, a2):
    d = paired(recs, a1, a2)
    r = premium(d, a1, dev)
    if r is None:
        return {"label": name, "arms": [a1, a2], "n": len(d), "status": "not collected"}
    r.update({"label": name, "arms": [a1, a2], "status": "ok",
              "mde": Z * r["se"],
              "ci": [r["est"] - 1.96 * r["se"], r["est"] + 1.96 * r["se"]]})
    return r


def main():
    recs = load(PRIMARY)
    out = {"model": PRIMARY, "primary": None, "rows": []}
    for name, a1, a2 in PAIRS + WITHIN:
        out["rows"].append(contrast(recs, name, a1, a2))

    by = {r["label"]: r for r in out["rows"]}
    eq, ms = by["equivalence"], by["matched_struct"]

    print(f"{'contrast':20s} {'n':>4s} {'est':>7s} {'se':>6s} {'p':>7s} "
          f"{'MDE':>6s}  {'95% CI':>17s}")
    for r in out["rows"]:
        if r["status"] != "ok":
            print(f"{r['label']:20s} {r['n']:4d}  not collected")
            continue
        print(f"{r['label']:20s} {r['n']:4d} {r['est']:+7.3f} {r['se']:6.3f} "
              f"{r['p']:7.4f} {r['mde']:6.3f}  "
              f"[{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}]")

    # ------------------------------------------- the pre-registered decision
    if eq["status"] == "ok" and ms["status"] == "ok":
        v = {"est": eq["est"], "p": eq["p"], "ci": eq["ci"],
             "benchmark": ms["est"],
             "positive_and_significant": bool(eq["est"] > 0 and eq["p"] < 0.05),
             "ci_includes_benchmark": bool(eq["ci"][0] <= ms["est"] <= eq["ci"][1]),
             "ci_excludes_zero": bool(eq["ci"][0] > 0 or eq["ci"][1] < 0),
             "powered_for_benchmark": bool(eq["mde"] <= abs(ms["est"]))}
        if v["positive_and_significant"]:
            v["verdict"] = ("confirmed: the premium survives an explicit statement "
                            "that both sources saw the same case file and nothing else")
        elif not v["powered_for_benchmark"]:
            v["verdict"] = ("inconclusive: the arm cannot detect a premium the size "
                            "of the structure-matched estimate")
        elif v["ci"][1] < ms["est"]:
            v["verdict"] = ("refuted: the premium is smaller than the "
                            "structure-matched estimate once information is equalised")
        else:
            v["verdict"] = "null but consistent with the benchmark"
        out["primary"] = v
        print(f"\nprimary: {v['verdict']}")
        print(f"  premium {v['est']:+.3f} (p={v['p']:.4f}), benchmark "
              f"{v['benchmark']:+.3f}, powered={v['powered_for_benchmark']}")
    else:
        print("\nprimary: equivalence arms not collected")

    json.dump(out, open(f"{ROOT}/analysis/out_equivalence.json", "w"), indent=1)


if __name__ == "__main__":
    main()
