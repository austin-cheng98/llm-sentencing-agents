"""Reported confidence and exact adoption, arm by arm.

Both quantities are read off the primary model's static arms in run R1, the
only arms in which every agent sees three displayed numbers under a stated
attribution. Exact adoption counts a decision whose sentence equals one of the
numbers it was shown.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, PRIMARY, FACTORS, ROOT

ARMS = ["peerbare_ng", "peermatch_ng", "peerdelta_ng", "tooldelta_ng",
        "toolbare_ng", "clerdelta_ng"]
# the second lineage was collected in three arms only, all with the guideline
# removed. It is reported beside the primary model and not pooled with it.
CROSS = "gpt6"
CROSS_ARMS = ["peerbare_ng", "peermatch_ng", "toolbare_ng"]


def pull(d):
    y = np.array([r["dev"] for r in d])
    x = np.array([r["delta"] for r in d])
    F = np.column_stack([[r[f] for r in d] for f in FACTORS]).astype(float)
    return float(ols(np.column_stack([np.ones(len(y)), x, F]), y)[1])


def cells(recs, arms):
    out = []
    for arm in arms:
        d = [r for r in recs if r["arm"] == arm and r.get("confidence")]
        if len(d) < 16:
            continue
        ex = sum(1 for r in d if r.get("peer_vals") and r["sentence"] in r["peer_vals"])
        out.append({"arm": arm, "pull": pull(d),
                    "conf": float(np.mean([r["confidence"] for r in d])),
                    "exact": 100 * ex / len(d), "n": len(d)})
    return out


def main():
    recs = [r for r in load(model=PRIMARY) if r["run"] == "R1"]
    rows = []
    for arm in ARMS:
        d = [r for r in recs if r["arm"] == arm and r.get("confidence")]
        if len(d) < 16:
            continue
        p = pull(d)
        c = float(np.mean([r["confidence"] for r in d]))
        ex = sum(1 for r in d if r.get("peer_vals") and r["sentence"] in r["peer_vals"])
        rows.append((arm, p, c, 100 * ex / len(d), len(d)))
        print(f"  {arm:14s} pull {p:+.3f}  confidence {c:.2f}  "
              f"exact adoption {100 * ex / len(d):4.1f}%  n={len(d)}")

    P = np.array([r[1] for r in rows])
    C = np.array([r[2] for r in rows])
    corr = float(np.corrcoef(P, C)[0, 1])
    print(f"\n  pull against reported confidence: r = {corr:+.2f} over {len(rows)} arms")

    g = [r for r in recs if r["arm"] in ("peerdelta", "tooldelta") and r.get("confidence")]
    u = [r for r in recs if r["arm"].endswith("_ng") and r.get("confidence")]
    cg = float(np.mean([r["confidence"] for r in g]))
    cu = float(np.mean([r["confidence"] for r in u]))
    print(f"  confidence with a guideline {cg:.2f}, without {cu:.2f}")

    cross = cells([r for r in load(model=CROSS)], CROSS_ARMS)
    for a in cross:
        print(f"  {CROSS}/{a['arm']:12s} pull {a['pull']:+.3f}  confidence "
              f"{a['conf']:.2f}  exact adoption {a['exact']:4.1f}%  n={a['n']}")

    out = {"arms": [{"arm": a, "pull": p, "conf": c, "exact": e, "n": n}
                    for a, p, c, e, n in rows],
           "corr": corr, "conf_guided": cg, "conf_unguided": cu,
           "cross_model": CROSS, "cross": cross}
    json.dump(out, open(os.path.join(ROOT, "analysis", "out_confidence.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
