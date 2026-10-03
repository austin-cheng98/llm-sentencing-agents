"""Estimate the premium on the second model lineage."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ROOT
from robustness import paired, premium

LINEAGE = "gpt6"
REF = "opus5"
PAIRS = [("matched_struct", "peermatch_ng", "toolbare_ng"),
         ("matched_bare", "peerbare_ng", "toolbare_ng")]
Z = 1.959963985 + 0.8416212336
BENCH = {"matched_struct": 0.206, "matched_bare": 0.323}


def dev(d):
    return [r["dev"] for r in d]


def main():
    recs = [r for r in load() if r.get("delta") is not None]
    out = {"lineage": LINEAGE, "reference": REF, "z": Z,
           "benchmark": BENCH, "rows": {}}
    print(f"{'model':8s} {'contrast':16s} {'n':>4s} {'est':>7s} {'se':>6s} "
          f"{'p':>7s} {'MDE':>6s}  {'95% CI':>17s}  vs bench")
    for m in (REF, LINEAGE):
        for lab, a1, a2 in PAIRS:
            d = paired([r for r in recs if r["model"] == m], a1, a2)
            c = premium(d, a1, dev)
            key = f"{m}|{lab}"
            if not c:
                out["rows"][key] = {"n": len(d), "est": None}
                print(f"{m:8s} {lab:16s} {len(d):4d}   too few records")
                continue
            mde = Z * c["se"]
            lo, hi = c["est"] - 1.96 * c["se"], c["est"] + 1.96 * c["se"]
            b = BENCH[lab]
            flag = ("bench" if m == REF else
                    "excludes" if hi < b or lo > b else
                    "contains" if lo <= b <= hi else "?")
            out["rows"][key] = {**c, "mde": mde, "ci": [lo, hi],
                                "bench": b, "powered": bool(mde <= b),
                                "vs_bench": flag}
            print(f"{m:8s} {lab:16s} {c['n']:4d} {c['est']:+7.3f} {c['se']:6.3f} "
                  f"{c['p']:7.4f} {mde:6.3f}  [{lo:+.3f},{hi:+.3f}]  {flag}")

    print()
    for lab, _, _ in PAIRS:
        r = out["rows"].get(f"{LINEAGE}|{lab}")
        if not r or r.get("est") is None:
            print(f"  {lab}: not estimable on {LINEAGE}")
            continue
        b, est, p, mde = r["bench"], r["est"], r["p"], r["mde"]
        lo, hi = r["ci"]
        if lo > 0:
            v = (f"a premium of the same sign appears outside Claude: {est:+.3f} "
                 f"(p={p:.4f}), interval {lo:+.3f} to {hi:+.3f}")
        elif hi < b and r["powered"]:
            v = (f"excludes the {b:+.3f} Claude figure: {est:+.3f} (p={p:.4f}), "
                 f"MDE {mde:.3f}")
        elif hi < b:
            v = (f"suggestive, not decisive: the interval lies below the {b:+.3f} "
                 f"Claude figure, but the arm's MDE ({mde:.3f}) is larger than "
                 f"that figure")
        else:
            v = (f"inconclusive: {est:+.3f} (p={p:.4f}), MDE {mde:.3f} -- the arm "
                 f"cannot detect a premium the size of the Claude {b:+.3f}")
        print(f"  {lab}: {v}")

    json.dump(out, open(f"{ROOT}/analysis/out_crosslineage.json", "w"), indent=1)


if __name__ == "__main__":
    main()
