"""Between-agent spread with the guideline and without, and how far the larger
figure rests on any one agent.

The spread is the mean over cases of the standard deviation across agents of the
sentence in units of the case midpoint. It is read on the arms that show no
numbers at all, so nothing but the guideline differs. Dropping each agent in turn
bounds how far the unguided figure depends on a single one.

The two arms carry different agents, three with the guideline and four without,
so the comparison is between arms and not within an agent.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, PRIMARY, ROOT


ARM = "nohist_ng"          # no numbers shown, guideline removed
GUIDED = "nohist"          # no numbers shown, guideline present


def spread(recs, arm=ARM, drop=None):
    d = [r for r in recs if r["arm"] == arm and r["step"] < 16
         and r["judge"] != drop]
    bycase = {}
    for r in d:
        bycase.setdefault(r["cid"], []).append(r["sentence"] / r["mid"])
    vals = [np.std(v, ddof=1) for v in bycase.values() if len(v) > 1]
    return float(np.mean(vals)), len(vals)


def main():
    recs = load(model=PRIMARY)
    judges = sorted({r["judge"] for r in recs if r["arm"] == ARM})
    guided, gcase = spread(recs, arm=GUIDED)
    full, ncase = spread(recs)
    print(f"between-agent spread in {GUIDED}: {guided:.3f} over {gcase} cases")
    print(f"between-agent spread in {ARM}: {full:.3f} over {ncase} cases, "
          f"agents {judges}")
    loo = {}
    for j in judges:
        s, n = spread(recs, drop=j)
        loo[j] = s
        print(f"  dropping {j}: {s:.3f} over {n} cases")
    res = {"arm": ARM, "full": full, "loo": loo,
           "range": [min(loo.values()), max(loo.values())],
           "guided_arm": GUIDED, "guided": guided}
    json.dump(res, open(f"{ROOT}/analysis/out_dispersion_loo.json", "w"), indent=1)


if __name__ == "__main__":
    main()
