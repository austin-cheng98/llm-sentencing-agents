"""Figure: how the anchor is displaced, and how the two framings differ."""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LO, HI, MID = 51, 63, 57.0
DELTAS = [-0.30, -0.15, 0.15, 0.30]


def anchors(mid, d):
    t = mid * (1 + d)
    return [int(round(t * 0.94)), int(round(t)), int(round(t * 1.06))]


fig = plt.figure(figsize=(6.6, 1.78))
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.02)
ax = fig.add_subplot(gs[0, 0])

ax.axvspan(LO, HI, color=F.FAINT, zorder=0)
ax.text((LO + HI) / 2, 1.015, "advisory range", transform=ax.get_xaxis_transform(),
        ha="center", va="bottom", fontsize=6.8, color=F.NEUTRAL)
ax.axvline(MID, color=F.NEUTRAL, lw=0.8, ls=(0, (3, 2)), zorder=1)

ylab = []
for i, d in enumerate(DELTAS):
    y = 3.4 - i * 0.95
    a = anchors(MID, d)
    # the band runs from the midpoint to the mean of the three shown numbers,
    # so its width is the displacement and the side it falls on is the direction
    lo, hi = sorted([MID, float(np.mean(a))])
    ax.barh(y, hi - lo, left=lo, height=0.34, color="#d6e2ee", linewidth=0,
            zorder=1)
    ax.scatter(a, [y] * 3, s=17, color=F.PEER, zorder=3, linewidths=0)
    ylab.append((y, f"$\\delta={d:+.0%}$".replace("%", r"\%")))
ax.set_xlim(34, 82.5); ax.set_ylim(-0.35, 5.05)
ax.set_yticks([p for p, _ in ylab])
ax.set_yticklabels([t for _, t in ylab], fontsize=7.2)
ax.tick_params(axis="y", length=0, pad=2)
ax.spines["left"].set_visible(False)
ax.set_xlabel("months")
ax.set_title("a  Displaced anchors, one case", loc="left", fontweight="bold", pad=17)
ax.tick_params(axis="y", length=0)


ax2 = fig.add_subplot(gs[0, 1])
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.axis("off")


def box(x, y, w, h, text, color, fc="white", bold=False):
    ax2.add_patch(FancyBboxPatch((x, y), w, h,
                  boxstyle="round,pad=0.008,rounding_size=0.035",
                  linewidth=0.8, edgecolor=color, facecolor=fc, zorder=2))
    ax2.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=6.5,
             color=F.INK, zorder=3, linespacing=1.25,
             fontweight="bold" if bold else "normal")


box(0.05, 0.60, 0.34, 0.20, "one case\none agent", F.NEUTRAL, fc=F.FAINT)
box(0.05, 0.28, 0.34, 0.20, "46  48  51\nmonths", F.NEUTRAL, bold=True)
box(0.56, 0.62, 0.40, 0.20, "\u201cother judges\nof this bench\u201d", F.PEER)
box(0.56, 0.16, 0.40, 0.20, "\u201ca regression model\nfitted to past cases\u201d", F.TOOL)
ax2.add_patch(FancyArrowPatch((0.22, 0.60), (0.22, 0.50), arrowstyle="-|>",
                              mutation_scale=7, color=F.NEUTRAL, lw=0.7))
for y0, col in ((0.72, F.PEER), (0.26, F.TOOL)):
    ax2.add_patch(FancyArrowPatch((0.40, 0.38), (0.55, y0), arrowstyle="-|>",
                                  mutation_scale=7, color=col, lw=0.9,
                                  connectionstyle="arc3,rad=0.12"))
# bracket marking the contrast the two labels identify
ax2.plot([0.995, 0.995], [0.26, 0.72], color=F.INK, lw=0.8)
ax2.plot([0.975, 0.995], [0.26, 0.26], color=F.INK, lw=0.8)
ax2.plot([0.975, 0.995], [0.72, 0.72], color=F.INK, lw=0.8)
ax2.text(0.76, 0.02, "difference in slope = peer premium", fontsize=6.3,
         color=F.INK, ha="center", style="italic")
ax2.set_title("b  The same numbers under two labels", loc="left",
              fontweight="bold", pad=17)

fig.savefig(f"{ROOT}/figures/fig_design.pdf")
fig.savefig(f"{ROOT}/figures/fig_design.png")
print("wrote figures/fig_design.pdf")
