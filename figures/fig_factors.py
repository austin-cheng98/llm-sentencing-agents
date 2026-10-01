"""Agents track the legal content of the cases throughout."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
from common import load, ols, cluster_vcov, PRIMARY
import matplotlib.pyplot as plt

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACTORS = [("severity", "Offense severity"), ("prior", "Prior record"),
           ("cooperation", "Substantial assistance"), ("remorse", "Expressed remorse")]


def effects(d):
    y = np.array([np.log(max(r["sentence"], 1.0)) for r in d])
    X = np.column_stack([np.ones(len(y))] +
                        [[r[f] for r in d] for f, _ in FACTORS])
    b = ols(X, y)
    V = cluster_vcov(X, y, b, np.array([r["judge"] for r in d]))
    return [((np.exp(b[i + 1]) - 1) * 100,
             (np.exp(b[i + 1]) - 1) * 100 * 1.96 * np.sqrt(V[i + 1, i + 1]))
            for i in range(len(FACTORS))]


recs = load(model=PRIMARY)
guided = [r for r in recs if r["arm"] in ("peerdelta", "tooldelta")]
unguided = [r for r in recs if r["arm"] == "nohist_ng" and r["step"] < 16]
eg, eu = effects(guided), effects(unguided)

fig, ax = plt.subplots(figsize=(5.6, 1.7))
y = np.arange(len(FACTORS))[::-1]; h = 0.32
ax.barh(y + h / 2, [e[0] for e in eg], h, color=F.NEUTRAL, zorder=3,
        label="guideline present")
ax.barh(y - h / 2, [e[0] for e in eu], h, color=F.PEER, zorder=3,
        label="guideline removed")
for yi, (a, b) in zip(y, zip(eg, eu)):
    for off, v in ((h / 2, a[0]), (-h / 2, b[0])):
        ax.text(v + (5 if v >= 0 else -5), yi + off, f"{v:+.0f}%", va="center",
                ha="left" if v >= 0 else "right", fontsize=6.6, color=F.INK)
ax.axvline(0, color=F.INK, lw=0.7)
ax.set_yticks(y); ax.set_yticklabels([n for _, n in FACTORS], fontsize=7.2)
ax.set_xlim(-45, 195)
ax.legend(loc="lower right", fontsize=6.8, handlelength=1.1)
F.finish(ax, "effect on sentence length (%)", None, None)
fig.savefig(f"{ROOT}/figures/fig_factors.pdf")
print("wrote fig_factors.pdf")
