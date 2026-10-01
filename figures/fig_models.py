"""Figure: pull across models, and across a second lineage.

Panel a keeps the guideline contrast, which only the Claude models were run in
both ways. Panel b holds the blocks bare on both sides, the one condition every
model including GPT-6 Luna was collected in, so the four sit on one scale.
"""
import sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
from common import load, ols, cluster_vcov
import matplotlib.pyplot as plt

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORT = {"opus5": "Opus 5", "sonnet5": "Sonnet 5", "haiku45": "Haiku 4.5",
         "gpt6": "GPT-6 Luna"}
# panel a: the guideline contrast, on the arms carrying the original closing lines
GUIDE = [("opus5", "Claude Opus 5"), ("sonnet5", "Claude Sonnet 5"),
         ("haiku45", "Claude Haiku 4.5")]
ARMS = [("peerdelta", "guideline", F.PEER), ("tooldelta", "guideline", F.TOOL),
        ("peerdelta_ng", "no guideline", F.PEER),
        ("tooldelta_ng", "no guideline", F.TOOL)]
# panel b: bare blocks, no guideline. The only condition shared by all four
BARE = [("opus5", "Opus 5"), ("sonnet5", "Sonnet 5"), ("haiku45", "Haiku 4.5"),
        ("gpt6", "GPT-6 Luna")]
BARMS = [("peerbare_ng", F.PEER), ("toolbare_ng", F.TOOL)]


def slope(d):
    x = np.array([r["delta"] for r in d]); y = np.array([r["dev"] for r in d])
    X = np.column_stack([np.ones(len(x)), x]); b = ols(X, y)
    return b[1], np.sqrt(cluster_vcov(X, y, b, np.array([r["cid"] for r in d]))[1, 1])


recs = [r for r in load() if r.get("delta") is not None]
fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.6, 1.8),
                             gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.26))

avail = [m for m, _ in GUIDE if any(r["model"] == m for r in recs)]
width = 0.19
for k, (arm, ctx, col) in enumerate(ARMS):
    vals, errs, pos = [], [], []
    for i, m in enumerate(avail):
        d = [r for r in recs if r["model"] == m and r["arm"] == arm]
        if len(d) < 8:
            continue
        b, se = slope(d)
        vals.append(b); errs.append(1.96 * se); pos.append(i + (k - 1.5) * width)
    if not vals:
        continue
    ax.bar(pos, vals, width * 0.88, yerr=errs, capsize=1.8,
           color=col if ctx == "guideline" else "white",
           edgecolor=col, linewidth=0.9, hatch="" if ctx == "guideline" else "////",
           error_kw=dict(lw=0.8, ecolor=F.INK), zorder=3)
ax.set_xticks(np.arange(len(avail)))
ax.set_xticklabels([dict(GUIDE)[m] for m in avail])

bwidth = 0.30
bavail = [m for m, _ in BARE if any(r["model"] == m for r in recs)]
for k, (arm, col) in enumerate(BARMS):
    vals, errs, pos = [], [], []
    for i, m in enumerate(bavail):
        d = [r for r in recs if r["model"] == m and r["arm"] == arm]
        if len(d) < 8:
            continue
        b, se = slope(d)
        vals.append(b); errs.append(1.96 * se); pos.append(i + (k - 0.5) * bwidth)
    bx.bar(pos, vals, bwidth * 0.86, yerr=errs, capsize=1.8, color="white",
           edgecolor=col, linewidth=0.9, hatch="////",
           error_kw=dict(lw=0.8, ecolor=F.INK), zorder=3)
bx.set_xticks(np.arange(len(bavail)))
bx.set_xticklabels([dict(BARE)[m] for m in bavail], fontsize=7.4)

for a, title in ((ax, "a  Original closing lines, guideline present and removed"),
                 (bx, "b  Bare blocks, no guideline")):
    a.axhline(0, color=F.INK, lw=0.7)
    a.axhline(1.0, color=F.MUTED, lw=0.7, ls=":")
    a.set_ylim(-0.15, 1.28)
    a.set_title(title, loc="left", fontweight="bold", pad=5, fontsize=7.4)
ax.text(0.008, 1.015, "full adoption of the shown numbers",
        transform=ax.get_yaxis_transform(), fontsize=6.6, color=F.MUTED,
        ha="left", va="bottom", style="italic")
F.finish(ax, None, "pull  $\\hat{\\pi}$  (95% CI)", None)
F.finish(bx, None, None, None)
# the two panels share a scale but not an axis, so panel b keeps its own labels
bx.tick_params(axis="y", labelsize=7.4)

h = [plt.Rectangle((0, 0), 1, 1, fc=F.PEER, ec=F.PEER),
     plt.Rectangle((0, 0), 1, 1, fc=F.TOOL, ec=F.TOOL),
     plt.Rectangle((0, 0), 1, 1, fc="white", ec=F.INK, hatch="////")]
ax.legend(h, ["Peer framing", "Tool framing", "Guideline removed"],
          loc="lower left", bbox_to_anchor=(0.0, 1.23), borderaxespad=0.0,
          frameon=False, ncol=3, handlelength=1.3, columnspacing=1.1,
          handleheight=0.9, fontsize=7)
fig.savefig(f"{ROOT}/figures/fig_models.pdf")
fig.savefig(f"{ROOT}/figures/fig_models.png")
print("wrote figures/fig_models.pdf")
for m in bavail:
    for arm, _ in BARMS:
        d = [r for r in recs if r["model"] == m and r["arm"] == arm]
        if len(d) >= 8:
            b, se = slope(d)
            print(f"  {m:9s} {arm:14s} pull={b:+.3f} se={se:.3f} n={len(d)}")
