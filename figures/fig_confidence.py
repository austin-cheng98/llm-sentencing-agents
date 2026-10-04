"""Plot confidence and exact adoption by model family."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
import matplotlib.pyplot as plt

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f"{ROOT}/analysis/out_confidence.json"))
LAB = {"peerbare_ng": "Peer bare", "peermatch_ng": "Peer matched",
       "toolbare_ng": "Forecast bare"}
MARKER = {"peerbare_ng": "o", "peermatch_ng": "s", "toolbare_ng": "^"}
FAMILY_STYLE = {
    "Claude (pooled)": (F.PEER, "Claude, pooled"),
    "GPT-6 (pooled)": (F.CROSS, "GPT-6, pooled"),
}

fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 3.6),
                             gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.62))
p = np.array([a["pull"] for a in D["arms"]])
c = np.array([a["conf"] for a in D["arms"]])
b = np.polyfit(p, c, 1)
gx = np.linspace(min(p) - .05, max(p) + .05, 20)
ax.plot(gx, np.polyval(b, gx), color=F.MUTED, lw=0.9,
        ls=(0, (4, 2)), zorder=1)

for family, rows in (("Claude (pooled)", D["arms"]),
                     ("GPT-6 (pooled)", D["family"])):
    color = FAMILY_STYLE[family][0]
    for a in rows:
        ax.scatter(a["pull"], a["conf"], s=38, marker=MARKER[a["arm"]],
                   facecolors=color if family == "Claude (pooled)" else "none",
                   edgecolors=color, zorder=3 if family == "Claude (pooled)" else 4,
                   linewidths=1.0 if family == "GPT-6 (pooled)" else 0.7)

ax.set_ylim(5.70, 7.10)
ax.set_xlim(-0.12, 1.42)
F.finish(ax, "pull  $\\hat{\\pi}$", "mean reported confidence",
         f"a  Confidence and pull ($r={D['corr']:.2f}$)")
ax.title.set_fontsize(7.4)

order = sorted([(a, "Claude (pooled)") for a in D["arms"]] +
               [(a, "GPT-6 (pooled)") for a in D["family"]],
               key=lambda t: -t[0]["exact"])
y = np.arange(len(order))[::-1]
bx.barh(y, [a["exact"] for a, _ in order], 0.68,
        color=[FAMILY_STYLE[family][0] for _, family in order], zorder=3)
for yi, (a, _) in zip(y, order):
    bx.text(a["exact"] + 1, yi, f"{a['exact']:.0f}%", va="center",
            fontsize=6.4, color=F.INK)
bx.set_yticks(y)
bx.set_yticklabels([f"{LAB[a['arm']]}  ({FAMILY_STYLE[family][1]})"
                    for a, family in order], fontsize=5.7)
bx.tick_params(axis="y", pad=2)
bx.set_xlim(0, 56)
F.finish(bx, "decisions equal to a shown number (%)", None, "b  Exact adoption")
bx.xaxis.label.set_size(6.8)
bx.title.set_fontsize(7.4)

fig.savefig(f"{ROOT}/figures/fig_confidence.pdf")
print("wrote fig_confidence.pdf")
