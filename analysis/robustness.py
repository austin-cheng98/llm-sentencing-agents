"""Robustness of the premium to round numbers, to linearity, and to the scale.

Three things a reader can reasonably doubt about the pull estimator, each
checked here against the same decisions the headline contrasts use.

Round numbers. Sentences cluster on year and half-year boundaries, so a
decision can land on a displayed number by taste rather than by copying. The
displayed numbers are themselves arbitrary, which bounds how much of the
premium that taste can explain, but the exact-match rate is not immune and the
split below says by how much.

Linearity. Pull is one slope through four displacements. Estimating the
premium separately at each magnitude says whether the single slope hides a
kink.

Scale. Deviation is a ratio, so the premium inherits the sentence scale.
Re-running the contrasts on within-case ranks and on log ratios says whether a
monotone change of scale moves the answer.
"""
import sys, os, json, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, cluster_vcov, PRIMARY, ROOT, factor_matrix

HEADLINE = [("matched_struct", "peermatch_ng", "toolbare_ng"),
            ("matched_bare", "peerbare_ng", "toolbare_ng"),
            ("original_sentences", "peerdelta_ng", "tooldelta_ng")]


def paired(recs, a1, a2):
    """The contrast sample: agents present in both arms, as inference.py uses."""
    d = [r for r in recs if r["arm"] in (a1, a2)]
    shared = ({r["judge"] for r in d if r["arm"] == a1} &
              {r["judge"] for r in d if r["arm"] == a2})
    return [r for r in d if r["judge"] in shared]


def premium(d, a1, outcome, B=9999, seed=17):
    """Difference in slope on `outcome`, with the label-swap randomisation null."""
    if len(d) < 32:
        return None
    y = np.asarray(outcome(d), dtype=float)
    dl = np.array([r["delta"] for r in d])
    g = np.array([1.0 if r["arm"] == a1 else 0.0 for r in d])
    F = factor_matrix(d)
    cell = np.array([f"{r['judge']}|{r['cid']}" for r in d])

    def est(gv):
        return ols(np.column_stack([np.ones(len(y)), dl, gv, dl * gv, F]), y)[3]

    obs = est(g)
    X = np.column_stack([np.ones(len(y)), dl, g, dl * g, F])
    b = ols(X, y)
    se = float(np.sqrt(cluster_vcov(X, y, b, np.array([r["cid"] for r in d]))[3, 3]))
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(B):
        gv = g.copy()
        for c in np.unique(cell):
            m = cell == c
            if m.sum() > 1 and rng.random() < 0.5:
                gv[m] = 1.0 - gv[m]
        if abs(est(gv)) >= abs(obs) - 1e-12:
            cnt += 1
    return {"est": float(obs), "se": se, "p": (cnt + 1) / (B + 1), "n": len(d)}


# ---------------------------------------------------------------- outcomes
def dev(d):
    return [r["dev"] for r in d]


def logratio(d):
    """log(sentence / midpoint). Same sign as dev, different spacing."""
    return [np.log(max(r["sentence"], 1) / r["mid"]) for r in d]


def caserank(d):
    """Within-case rank of the sentence, centred and scaled to unit width.

    Only the ordering of sentences inside a case survives, so any monotone
    redefinition of the sentence scale leaves this outcome untouched.
    """
    by = collections.defaultdict(list)
    for i, r in enumerate(d):
        by[r["cid"]].append((r["sentence"], i))
    out = np.zeros(len(d))
    for rows in by.values():
        rows.sort()
        vals = [s for s, _ in rows]
        for pos, (s, i) in enumerate(rows):
            # midrank, so ties (common here) do not invent an ordering
            tied = [p for p, v in enumerate(vals) if v == s]
            out[i] = (sum(tied) / len(tied)) / max(len(rows) - 1, 1) - 0.5
    return out


def main():
    recs = [r for r in load(model=PRIMARY) if r.get("delta") is not None]
    allrecs = [r for r in load() if r.get("delta") is not None]
    res = {}

    # ------------------------------------------------ 1. what agents choose
    s = [r["sentence"] for r in allrecs]
    res["sentences"] = {
        "n": len(s),
        "div6": 100 * sum(1 for x in s if x % 6 == 0) / len(s),
        "div12": 100 * sum(1 for x in s if x % 12 == 0) / len(s),
        "div5": 100 * sum(1 for x in s if x % 5 == 0) / len(s),
        "div10": 100 * sum(1 for x in s if x % 10 == 0) / len(s),
        "modes": collections.Counter(s).most_common(8),
        "distinct": len(set(s)),
    }
    print("sentences agents choose (n=%d, %d distinct)" % (len(s), len(set(s))))
    print("  divisible by 6: %.1f%%   by 12: %.1f%%   by 5: %.1f%%   by 10: %.1f%%"
          % (res["sentences"]["div6"], res["sentences"]["div12"],
             res["sentences"]["div5"], res["sentences"]["div10"]))
    print("  most common:", ", ".join(f"{v}mo x{c}" for v, c in res["sentences"]["modes"]))

    # ------------------------------------------------ 2. what they are shown
    shown = [v for r in allrecs for v in r["peer_vals"]]
    res["anchors"] = {
        "n": len(shown),
        "div6": 100 * sum(1 for v in shown if v % 6 == 0) / len(shown),
        "div12": 100 * sum(1 for v in shown if v % 12 == 0) / len(shown),
        "div5": 100 * sum(1 for v in shown if v % 5 == 0) / len(shown),
        "allthree_div6": 100 * sum(1 for r in allrecs
                                   if all(v % 6 == 0 for v in r["peer_vals"])) / len(allrecs),
    }
    print("\nnumbers agents are shown (n=%d)" % len(shown))
    print("  divisible by 6: %.1f%%   by 12: %.1f%%   by 5: %.1f%%"
          % (res["anchors"]["div6"], res["anchors"]["div12"], res["anchors"]["div5"]))
    print("  records where all three are divisible by 6: %.1f%%"
          % res["anchors"]["allthree_div6"])

    # ----------------------------------- 3. does roundness carry the copying
    eq = [r for r in allrecs if r["sentence"] in r["peer_vals"]]
    rnd = [r for r in eq if r["sentence"] % 6 == 0]
    base6 = res["anchors"]["div6"]
    res["exact"] = {
        "rate": 100 * len(eq) / len(allrecs),
        "n": len(eq),
        "round_share": 100 * len(rnd) / len(eq),
        "anchor_round_share": base6,
        "rate_on_round_anchors": 100 * sum(
            1 for r in allrecs if any(v % 6 == 0 for v in r["peer_vals"])
            and r["sentence"] in r["peer_vals"]) / max(sum(
                1 for r in allrecs if any(v % 6 == 0 for v in r["peer_vals"])), 1),
        "rate_no_round_anchor": 100 * sum(
            1 for r in allrecs if not any(v % 6 == 0 for v in r["peer_vals"])
            and r["sentence"] in r["peer_vals"]) / max(sum(
                1 for r in allrecs if not any(v % 6 == 0 for v in r["peer_vals"])), 1),
    }
    print("\nexact matches to a shown number: %.1f%% of decisions (n=%d)"
          % (res["exact"]["rate"], len(eq)))
    print("  of the matched values %.1f%% are divisible by 6, against %.1f%% of all shown"
          % (res["exact"]["round_share"], base6))
    print("  match rate when some shown number is round: %.1f%%   when none is: %.1f%%"
          % (res["exact"]["rate_on_round_anchors"], res["exact"]["rate_no_round_anchor"]))

    # ------------------------- 4. the premium with no round number in sight
    res["premium_nonround"] = {}
    print("\npremium on records where no shown number is divisible by 6")
    for name, a1, a2 in HEADLINE:
        d = [r for r in paired(recs, a1, a2)
             if not any(v % 6 == 0 for v in r["peer_vals"])]
        c = premium(d, a1, dev)
        if c:
            res["premium_nonround"][name] = c
            print("  %-19s %+.3f (se %.3f) RI p=%.4f n=%d"
                  % (name, c["est"], c["se"], c["p"], c["n"]))
        else:
            res["premium_nonround"][name] = None
            print("  %-19s too few records (%d)" % (name, len(d)))

    # ------------------------------------------- 5. is one slope enough
    res["by_magnitude"] = {}
    print("\npremium estimated separately at each displacement magnitude")
    for name, a1, a2 in HEADLINE:
        full = paired(recs, a1, a2)
        row = {}
        for mag in (0.15, 0.30):
            d = [r for r in full if abs(r["delta"]) == mag]
            c = premium(d, a1, dev, B=2999)
            row[f"{mag:g}"] = c
            if c:
                print("  %-19s |d|=%.2f  %+.3f (se %.3f) RI p=%.4f n=%d"
                      % (name, mag, c["est"], c["se"], c["p"], c["n"]))
            else:
                print("  %-19s |d|=%.2f  too few records (%d)" % (name, mag, len(d)))
        res["by_magnitude"][name] = row

    # --------------------------------- 6. does the scale carry the answer
    res["scale"] = {}
    print("\nheadline contrasts under a monotone change of outcome")
    for name, a1, a2 in HEADLINE:
        d = paired(recs, a1, a2)
        row = {}
        for label, fn in (("dev", dev), ("log", logratio), ("caserank", caserank)):
            c = premium(d, a1, fn, B=2999)
            row[label] = c
            if c:
                print("  %-19s %-9s %+.3f (se %.3f) RI p=%.4f"
                      % (name, label, c["est"], c["se"], c["p"]))
        res["scale"][name] = row

    # ------------------------------------------- 7. confidence as a report
    conf = [r["confidence"] for r in allrecs if r.get("confidence") is not None]
    res["confidence"] = {"n": len(conf), "distinct": len(set(conf)),
                         "dist": dict(sorted(collections.Counter(conf).items())),
                         "top2_share": 100 * sum(
                             1 for c in conf if c in (6, 7)) / len(conf)}
    print("\nconfidence ratings: %d values, %d distinct, %.1f%% are 6 or 7"
          % (len(conf), len(set(conf)), res["confidence"]["top2_share"]))
    print("  distribution:", res["confidence"]["dist"])

    json.dump(res, open(f"{ROOT}/analysis/out_robustness.json", "w"), indent=1)


if __name__ == "__main__":
    main()
