"""Structure-matched premium on smaller models."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ROOT
from robustness import paired, premium

MODELS = ["opus5", "sonnet5", "haiku45"]
PAIRS = [("matched_struct", "peermatch_ng", "toolbare_ng"),
         ("matched_bare", "peerbare_ng", "toolbare_ng")]
Z = 1.959963985 + 0.8416212336
BENCH = 0.206


def dev(d):
    return [r["dev"] for r in d]


def main():
    recs = [r for r in load() if r.get("delta") is not None]
    out = {"benchmark": BENCH, "z": Z, "rows": {}}
    print(f"{'model':9s} {'contrast':15s} {'n':>4s} {'est':>7s} {'se':>6s} "
          f"{'p':>7s} {'MDE':>6s}  {'95% CI':>17s}  powered")
    for m in MODELS:
        sub = [r for r in recs if r["model"] == m]
        for lab, a1, a2 in PAIRS:
            d = paired(sub, a1, a2)
            r = premium(d, a1, dev)
            if r is None:
                out["rows"][f"{m}|{lab}"] = {"n": len(d), "est": None}
                print(f"{m:9s} {lab:15s} {len(d):4d}   too small to estimate")
                continue
            e, se, p = r["est"], r["se"], r["p"]
            mde = Z * se
            lo, hi = e - 1.96 * se, e + 1.96 * se
            out["rows"][f"{m}|{lab}"] = {
                "n": r["n"], "est": e, "se": se, "p": p, "mde": mde,
                "ci": [lo, hi], "powered_for_bench": bool(mde <= BENCH),
                "excludes_bench": bool(hi < BENCH)}
            flag = ("bench" if (m == "opus5" and lab == "matched_struct")
                    else "yes" if mde <= BENCH else "NO")
            print(f"{m:9s} {lab:15s} {r['n']:4d} {e:+7.3f} {se:6.3f} {p:7.4f} "
                  f"{mde:6.3f}  [{lo:+.3f},{hi:+.3f}]  {flag}")

    print()
    for m in ("sonnet5", "haiku45"):
        r = out["rows"].get(f"{m}|matched_struct")
        if not r or r.get("est") is None:
            continue
        if r["powered_for_bench"] and r["excludes_bench"]:
            verdict = f"excludes the {BENCH:+.3f} measured on Opus 5"
        elif r["powered_for_bench"]:
            verdict = f"consistent with the {BENCH:+.3f} measured on Opus 5"
        elif r["excludes_bench"]:
            verdict = ("suggestive, not decisive: the interval lies below the "
                       f"{BENCH:+.3f} measured on Opus 5, but the arm's MDE is "
                       "marginally larger than that figure")
        else:
            verdict = ("inconclusive: cannot detect a premium the size of the "
                       f"{BENCH:+.3f} measured on Opus 5")
        print(f"  {m}: {r['est']:+.3f} (p={r['p']:.4f}, MDE {r['mde']:.3f}) "
              f"-- {verdict}")

    json.dump(out, open(f"{ROOT}/analysis/out_balanced.json", "w"), indent=1)


if __name__ == "__main__":
    main()
