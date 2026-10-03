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
LAB = {"peerbare_ng": "Peer, bare", "peermatch_ng": "Peer, structure-matched",
       "peerdelta_ng": "Peer, closing line", "tooldelta_ng": "Forecast, hedged",
       "toolbare_ng": "Forecast, bare", "clerdelta_ng": "Docketing"}
OFF = {"clerdelta_ng": (0, 7, "center"), "toolbare_ng": (-5, 2, "right"),
       "tooldelta_ng": (4, 3, "left"), "peerdelta_ng": (-4, -7, "right"),
       "peermatch_ng": (-4, -7, "right"), "peerbare_ng": (0, -9, "center")}
XLAB = {"peerbare_ng": "Peer, bare (GPT-6)",
        "peermatch_ng": "Peer, matched (GPT-6)",
        "toolbare_ng": "Forecast, bare (GPT-6)"}
XOFF = {"toolbare_ng": (0, 8, "center"), "peerbare_ng": (4, 6, "left"),
        "peermatch_ng": (5, -5, "left")}
COL = {"peerbare_ng": F.PEER, "peermatch_ng": F.PEER, "peerdelta_ng": F.PEER,
       "toolbare_ng": F.TOOL, "tooldelta_ng": F.TOOL, "clerdelta_ng": F.ACCENT}

fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 3.0),
                             gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.62))
p = np.array([a["pull"] for a in D["arms"]]); c = np.array([a["conf"] for a in D["arms"]])
b = np.polyfit(p, c, 1)
gx = np.linspace(min(p) - .05, max(p) + .05, 20)
ax.plot(gx, np.polyval(b, gx), color=F.MUTED, lw=0.9, ls=(0, (4, 2)), zorder=1)
for a in D["arms"]:
    ax.scatter(a["pull"], a["conf"], s=34, color=COL[a["arm"]], zorder=3,
               linewidths=0.7, edgecolors="white")
    dx, dy, ha = OFF[a["arm"]]
    ax.annotate(LAB[a["arm"]], (a["pull"], a["conf"]), textcoords="offset points",
                xytext=(dx, dy), ha=ha, fontsize=6.2, color=F.INK)
for a in D.get("cross", []):
    ax.scatter(a["pull"], a["conf"], s=30, marker="D", color=F.CROSS, zorder=4,
               linewidths=0.7, edgecolors="white")
    dx, dy, ha = XOFF[a["arm"]]
    ax.annotate(XLAB[a["arm"]], (a["pull"], a["conf"]), textcoords="offset points",
                xytext=(dx, dy), ha=ha, fontsize=6.2, color=F.INK)
ax.set_ylim(5.70, 7.10); ax.set_xlim(-0.12, 1.42)
F.finish(ax, "pull  $\\hat{\\pi}$", "mean reported confidence",
         f"a  Confidence falls as pull rises ($r={D['corr']:.2f}$)")
ax.title.set_fontsize(7.4)

order = sorted([(x, False) for x in D["arms"]] +
               [(x, True) for x in D.get("cross", [])],
               key=lambda t: -t[0]["exact"])
y = np.arange(len(order))[::-1]
bx.barh(y, [a["exact"] for a, _ in order], 0.68,
        color=[F.CROSS if x else COL[a["arm"]] for a, x in order], zorder=3)
for yi, (a, _) in zip(y, order):
    bx.text(a["exact"] + 1, yi, f"{a['exact']:.0f}%", va="center", fontsize=6.4,
            color=F.INK)
bx.set_yticks(y)
bx.set_yticklabels([LAB[a["arm"]] + ("  (GPT-6)" if x else "") for a, x in order],
                   fontsize=6.2)
bx.tick_params(axis="y", pad=2)
bx.set_xlim(0, 52)
F.finish(bx, "decisions equal to a shown number (%)", None, "b  Exact adoption")
bx.xaxis.label.set_size(6.8)
bx.title.set_fontsize(7.4)
fig.savefig(f"{ROOT}/figures/fig_confidence.pdf")
print("wrote fig_confidence.pdf")
