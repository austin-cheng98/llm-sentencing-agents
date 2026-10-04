"""Plot confidence and exact adoption."""
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
       "peerdelta_ng": "Peer closing line", "tooldelta_ng": "Forecast hedged",
       "toolbare_ng": "Forecast bare", "clerdelta_ng": "Docketing"}
MODEL_STYLE = {"opus5": (F.PEER, "Opus 5"),
               "gpt6": (F.CROSS, "GPT-6 Luna"),
               "gpt6sol": (F.CROSS_SOL, "GPT-6 Sol")}
MODEL_TAG = {"opus5": "O", "gpt6": "L", "gpt6sol": "S"}
TAG = {"peerbare_ng": "PB", "peermatch_ng": "PM", "peerdelta_ng": "PC",
       "tooldelta_ng": "FH", "toolbare_ng": "FB", "clerdelta_ng": "D"}
LABEL_OFF = {
    ("opus5", "clerdelta_ng"): (5, 5, "left"),
    ("opus5", "toolbare_ng"): (-8, -11, "right"),
    ("opus5", "tooldelta_ng"): (-8, 11, "right"),
    ("opus5", "peerdelta_ng"): (-8, -13, "right"),
    ("opus5", "peermatch_ng"): (-8, -13, "right"),
    ("opus5", "peerbare_ng"): (0, -12, "center"),
    ("gpt6", "peerbare_ng"): (7, 10, "left"),
    ("gpt6", "peermatch_ng"): (7, -11, "left"),
    ("gpt6", "toolbare_ng"): (8, -11, "left"),
    ("gpt6sol", "peerbare_ng"): (8, 10, "left"),
    ("gpt6sol", "peermatch_ng"): (7, -11, "left"),
    ("gpt6sol", "toolbare_ng"): (7, 10, "left"),
}

fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 3.6),
                             gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.62))
p = np.array([a["pull"] for a in D["arms"]]); c = np.array([a["conf"] for a in D["arms"]])
b = np.polyfit(p, c, 1)
gx = np.linspace(min(p) - .05, max(p) + .05, 20)
ax.plot(gx, np.polyval(b, gx), color=F.MUTED, lw=0.9, ls=(0, (4, 2)), zorder=1)
points = [(a, "opus5") for a in D["arms"]] + [
    (a, a["model"]) for a in D.get("cross", [])]
for a, model in points:
    color = MODEL_STYLE[model][0]
    ax.scatter(a["pull"], a["conf"], s=34, marker="o", color=color, zorder=3,
               linewidths=0.7, edgecolors="white")
    dx, dy, ha = LABEL_OFF[(model, a["arm"])]
    ax.annotate(f"{MODEL_TAG[model]} {TAG[a['arm']]}", (a["pull"], a["conf"]),
                textcoords="offset points", xytext=(dx, dy), ha=ha, fontsize=5.6,
                color=color, arrowprops=dict(arrowstyle="-", lw=0.45,
                                             color=F.MUTED, shrinkA=0, shrinkB=2))
ax.set_ylim(5.70, 7.10); ax.set_xlim(-0.12, 1.42)
F.finish(ax, "pull  $\\hat{\\pi}$", "mean reported confidence",
         f"a  Confidence falls as pull rises ($r={D['corr']:.2f}$)")
ax.title.set_fontsize(7.4)

order = sorted([(x, "opus5") for x in D["arms"]] +
               [(x, x["model"]) for x in D.get("cross", [])],
               key=lambda t: -t[0]["exact"])
y = np.arange(len(order))[::-1]
bx.barh(y, [a["exact"] for a, _ in order], 0.68,
        color=[MODEL_STYLE[model][0] for _, model in order], zorder=3)
for yi, (a, _) in zip(y, order):
    bx.text(a["exact"] + 0.7, yi, f"{a['exact']:.0f}%", va="center", fontsize=6.4,
            color=F.INK)
bx.set_yticks(y)
bx.set_yticklabels([LAB[a["arm"]] +
                    (f"  ({MODEL_STYLE[model][1]})" if model != "opus5" else "")
                    for a, model in order], fontsize=5.7)
bx.tick_params(axis="y", pad=2)
bx.set_xlim(0, 62)
F.finish(bx, "decisions equal to a shown number (%)", None, "b  Exact adoption")
bx.xaxis.label.set_size(6.8)
bx.title.set_fontsize(7.4)
fig.savefig(f"{ROOT}/figures/fig_confidence.pdf")
print("wrote fig_confidence.pdf")
