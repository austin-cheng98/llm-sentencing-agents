"""Plot confidence and exact adoption."""
import json
import os
import sys

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f"{ROOT}/analysis/out_confidence.json"))

MODEL_STYLE = {
    "opus5": ("#0072B2", "Claude Opus 5"),
    "sonnet5": ("#D55E00", "Claude Sonnet 5"),
    "haiku45": ("#009E73", "Claude Haiku 4.5"),
    "gpt6": ("#CC79A7", "GPT-6 Luna"),
    "gpt6sol": ("#555555", "GPT-6 Sol"),
}
ARM_MARKER = {
    "clerdelta_ng": "D",
    "tooldelta_ng": "^",
    "toolbare_ng": "v",
    "peerdelta_ng": "s",
    "peermatch_ng": "p",
    "peerbare_ng": "o",
}
ARM_TAG = {
    "clerdelta_ng": "D",
    "tooldelta_ng": "FH",
    "toolbare_ng": "FB",
    "peerdelta_ng": "PC",
    "peermatch_ng": "PM",
    "peerbare_ng": "PB",
}
ARM_NAME = {
    "clerdelta_ng": "Docketing",
    "tooldelta_ng": "Forecast hedged",
    "toolbare_ng": "Forecast bare",
    "peerdelta_ng": "Peer closing",
    "peermatch_ng": "Peer matched",
    "peerbare_ng": "Peer bare",
}
PROVIDER_STYLE = {"Claude": "#505050", "OpenAI": "#828282"}
SHARED_ARMS = ("peerbare_ng", "peermatch_ng", "toolbare_ng")

fig, (ax, bx) = plt.subplots(
    1, 2, figsize=(6.8, 5.0), gridspec_kw={"width_ratios": [1.12, 1], "wspace": 0.58}
)
fig.subplots_adjust(left=0.10, right=0.99, top=0.87, bottom=0.37)

primary = D["arms"]
p = np.array([a["pull"] for a in primary])
c = np.array([a["conf"] for a in primary])
fit = np.polyfit(p, c, 1)
gx = np.linspace(p.min() - 0.04, p.max() + 0.04, 24)
ax.plot(gx, np.polyval(fit, gx), color=F.MUTED, lw=0.9, ls=(0, (4, 2)), zorder=1)

points = [(a, "opus5") for a in primary]
points += [(a, a["model"]) for a in D["cross"]]
for a, model in points:
    ax.scatter(
        a["pull"], a["conf"], s=48, marker=ARM_MARKER[a["arm"]],
        color=MODEL_STYLE[model][0], edgecolors="white", linewidths=0.8, zorder=3,
    )

ax.set_xlim(-0.08, 1.14)
ax.set_ylim(5.72, 7.10)
ax.set_xticks([0, 0.25, 0.50, 0.75, 1.00])
ax.set_yticks([5.75, 6.00, 6.25, 6.50, 6.75, 7.00])
F.finish(ax, "pull  $\\hat{\\pi}$", "mean reported confidence", "a  Pull and confidence")
ax.title.set_fontsize(7.4)

model_handles = [
    Line2D([0], [0], color=color, lw=1.8, label=label)
    for color, label in MODEL_STYLE.values()
]
arm_handles = [
    Line2D([0], [0], marker=ARM_MARKER[arm], linestyle="None", color=F.INK,
           markersize=5.3, label=f"{ARM_TAG[arm]}  {ARM_NAME[arm]}")
    for arm in ("clerdelta_ng", "tooldelta_ng", "toolbare_ng", "peerdelta_ng",
                "peermatch_ng", "peerbare_ng")
]
fig.legend(handles=model_handles, loc="lower center", bbox_to_anchor=(0.5, 0.205),
           ncol=5, fontsize=6.5, handlelength=1.4, columnspacing=0.9,
           handletextpad=0.35, borderaxespad=0)
fig.legend(handles=arm_handles, loc="lower center", bbox_to_anchor=(0.5, 0.06),
           ncol=3, fontsize=6.2, handlelength=1.1, columnspacing=0.8,
           handletextpad=0.35, labelspacing=0.25, borderaxespad=0)

provider_rows = {
    (x["provider"], x["arm"]): x["exact"] for x in D["provider_exact"]
}
y = np.arange(len(SHARED_ARMS)) + 0.8
height = 0.30
claude = [provider_rows[("Claude", arm)] for arm in SHARED_ARMS]
openai = [provider_rows[("OpenAI", arm)] for arm in SHARED_ARMS]
bx.barh(y - height / 2, claude, height, color=PROVIDER_STYLE["Claude"], zorder=2)
bx.barh(y + height / 2, openai, height, color=PROVIDER_STYLE["OpenAI"],
        edgecolor=F.INK, linewidth=0.25, hatch="//", zorder=2)
for yi, values in zip(y, zip(claude, openai)):
    for offset, value in zip((-height / 2, height / 2), values):
        bx.text(value + 0.8, yi + offset, f"{value:.0f}%", va="center",
                fontsize=6.0, color=F.INK)
bx.set_yticks(y, [ARM_NAME[arm] for arm in SHARED_ARMS], fontsize=6.0)
bx.set_ylim(3.5, 0.1)
bx.set_xlim(0, 60)
bx.set_xticks([0, 20, 40, 60])
bx.tick_params(axis="y", pad=2)
F.finish(bx, "mean model-level exact adoption (%)", None, "b  Exact adoption")
bx.xaxis.label.set_size(6.5)
bx.title.set_fontsize(7.4)
bx.legend(
    handles=[Patch(facecolor=PROVIDER_STYLE["Claude"], label="Claude mean"),
             Patch(facecolor=PROVIDER_STYLE["OpenAI"], edgecolor=F.INK,
                   hatch="//", label="OpenAI mean")],
    loc="upper center", bbox_to_anchor=(0.53, 0.99), ncol=2, fontsize=5.8,
    handlelength=1.2, columnspacing=0.8, handletextpad=0.35, borderaxespad=0,
)

fig.savefig(f"{ROOT}/figures/fig_confidence.pdf")
print("wrote fig_confidence.pdf")
