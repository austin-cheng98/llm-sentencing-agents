"""What each closing sentence costs, numbers held identical."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
from common import load, ols, PRIMARY
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F4 = ("severity", "prior", "remorse", "cooperation")


def endpoints(recs, treated, base):
    """Pull in the base arm and in the treated arm, on the agents shared by both.

    Same balanced sample and same specification as the contrast in
    analysis10, so the gap between the two points is the reported estimate.
    """
    d = [r for r in recs if r["arm"] in (treated, base)]
    shared = ({r["judge"] for r in d if r["arm"] == treated} &
              {r["judge"] for r in d if r["arm"] == base})
    d = [r for r in d if r["judge"] in shared]
    y = np.array([r["dev"] for r in d])
    dl = np.array([r["delta"] for r in d])
    g = np.array([1.0 if r["arm"] == treated else 0.0 for r in d])
    fac = np.column_stack([[r[f] for r in d] for f in F4]).astype(float)
    b = ols(np.column_stack([np.ones(len(y)), dl, g, dl * g, fac]), y)
    return float(b[1]), float(b[1] + b[3])


F.setup()
recs = [r for r in load(model=PRIMARY) if r.get("delta") is not None]
C = json.load(open(f"{ROOT}/analysis/out_inference.json"))["contrast"]
TR = json.load(open(f"{ROOT}/analysis/out_trailer.json"))["contrast"]

rows = [("“You are deciding the same case independently.”",
         "peerdelta_ng", "peerbare_ng", C["closing_sentence"]["est"], F.PEER),
        ("“Form your own view of what this case warrants.”",
         "parafree_ng", "peerbare_ng", C["para_free"]["est"], F.PEER),
        ("“Your sentence should reflect your own judgment of the case.”",
         "paraown_ng", "peerbare_ng", C["para_own"]["est"], F.PEER),
        ("Forecast hedge, added to the forecast block",
         "tooldelta_ng", "toolbare_ng", TR["tool_trailer"]["est"], F.TOOL)]
SE = {"peerdelta_ng": C["closing_sentence"]["se"]["agent"],
      "parafree_ng": C["para_free"]["se"]["agent"],
      "paraown_ng": C["para_own"]["se"]["agent"],
      "tooldelta_ng": TR["tool_trailer"]["se"]}

LBL = {"peerdelta_ng": "“You are deciding the same\ncase independently.”",
       "parafree_ng": "“Form your own view of what\nthis case warrants.”",
       "paraown_ng": "“Your sentence should reflect your\nown judgment of the case.”",
       "tooldelta_ng": "Forecast hedge, added to\nthe forecast block"}


def spread(vals, gap):
    """Nudge label positions apart, keeping their order and centre of mass."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = list(vals)
    for k in range(1, len(order)):
        i, j = order[k - 1], order[k]
        if out[j] - out[i] < gap:
            out[j] = out[i] + gap
    shift = (sum(vals) - sum(out)) / len(vals)
    return [v + shift for v in out]


fig, ax = plt.subplots(figsize=(5.1, 2.3))
pts = [(lab, treated, base, est, col) + endpoints(recs, treated, base) for
       lab, treated, base, est, col in rows]
left = spread([p[5] for p in pts], 0.052)
right = spread([p[6] for p in pts], 0.088)

for k, (lab, treated, base, est, col, a, b) in enumerate(pts):
    ax.plot([0, 1], [a, b], color=col, lw=1.7, alpha=0.9,
            solid_capstyle="round", zorder=3)
    ax.plot([0], [a], "o", ms=4.4, color="white", mec=col, mew=1.3, zorder=4)
    ax.plot([1], [b], "o", ms=4.4, color=col, mec="white", mew=0.8, zorder=4)
    ax.plot([-0.075, -0.02], [left[k], a], color=col, lw=0.5, alpha=0.5, zorder=2)
    ax.plot([1.02, 1.075], [b, right[k]], color=col, lw=0.5, alpha=0.5, zorder=2)
    ax.text(-0.085, left[k], f"{a:.2f}", fontsize=7.2, ha="right", va="center",
            color=col)
    ax.text(1.085, right[k], f"{b:.2f}", fontsize=7.2, ha="left", va="center",
            color=col, fontweight="bold")
    ax.text(1.235, right[k], LBL[treated], fontsize=6.4, ha="left", va="center",
            color=F.INK, linespacing=1.3)

ax.plot([-0.30, 1.10], [1.0, 1.0], color=F.MUTED, lw=0.7, ls=":",
        zorder=1, clip_on=False)
ax.text(-0.28, 1.008, "full adoption of the shown numbers", fontsize=6.4,
        color=F.MUTED, ha="left", va="bottom", style="italic")
ax.set_xlim(-0.30, 2.28)
ax.set_ylim(0.42, 1.06)
ax.set_xticks([0, 1])
ax.set_xticklabels(["block as written", "sentence appended"], fontsize=7.6)
ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.tick_params(axis="x", length=0, pad=6)
ax.spines["bottom"].set_visible(False)
F.finish(ax, None, "pull  $\\hat{\\pi}$", None)
fig.savefig(f"{ROOT}/figures/fig_sentences.pdf")
fig.savefig(f"{ROOT}/figures/fig_sentences.png")
for lab, treated, base, est, col, a, b in pts:
    print(f"  {treated:14s} {a:+.3f} -> {b:+.3f}  (delta {b-a:+.3f}, reported {est:+.3f})")
