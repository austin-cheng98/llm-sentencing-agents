"""Report confidence and exact adoption by model family."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load, ols, FACTORS, ROOT

FAMILIES = {
    "Claude (pooled)": ("opus5", "sonnet5", "haiku45"),
    "GPT-6 (pooled)": ("gpt6", "gpt6sol"),
}
ARMS = ["peerbare_ng", "peermatch_ng", "toolbare_ng"]


def pull(d):
    y = np.array([r["dev"] for r in d])
    x = np.array([r["delta"] for r in d])
    F = np.column_stack([[r[f] for r in d] for f in FACTORS]).astype(float)
    return float(ols(np.column_stack([np.ones(len(y)), x, F]), y)[1])


def cells(recs, models, family):
    out = []
    for arm in ARMS:
        by_model = {
            model: [r for r in recs if r["model"] == model and r["arm"] == arm
                    and r.get("confidence") is not None]
            for model in models
        }
        by_model = {model: d for model, d in by_model.items() if d}
        n_by_model = {model: len(d) for model, d in by_model.items()}
        n = sum(n_by_model.values())
        if n < 16:
            continue
        slopes = [pull(d) for d in by_model.values()]
        weights = np.array(list(n_by_model.values()), dtype=float)
        exact = sum(1 for d in by_model.values() for r in d
                    if r.get("peer_vals") and r["sentence"] in r["peer_vals"])
        decisions = [r for d in by_model.values() for r in d]
        out.append({
            "arm": arm,
            "model": family,
            "pull": float(np.average(slopes, weights=weights)),
            "conf": float(np.mean([r["confidence"] for r in decisions])),
            "exact": 100 * exact / n,
            "n": n,
            "n_by_model": n_by_model,
        })
    return out


def main():
    recs = load()
    rows = cells(recs, FAMILIES["Claude (pooled)"], "Claude (pooled)")
    family = cells(recs, FAMILIES["GPT-6 (pooled)"], "GPT-6 (pooled)")
    P = np.array([r["pull"] for r in rows])
    C = np.array([r["conf"] for r in rows])
    corr = float(np.corrcoef(P, C)[0, 1])

    for group in (rows, family):
        for a in group:
            ns = ", ".join(f"{m}={n}" for m, n in a["n_by_model"].items())
            print(f"  {a['model']}/{a['arm']:12s} pull {a['pull']:+.3f}  "
                  f"confidence {a['conf']:.2f}  exact adoption {a['exact']:4.1f}%  "
                  f"n={a['n']} ({ns})")
    print(f"\n  Claude pooled-arm pull/confidence correlation: r = {corr:+.2f} over 3 arms")

    out = {"arms": rows, "family": family, "corr": corr,
           "pooling": {name: list(models) for name, models in FAMILIES.items()}}
    with open(os.path.join(ROOT, "analysis", "out_confidence.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
