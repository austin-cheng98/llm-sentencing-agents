"""Live cascade: disagreement collapses, and static pull predicts live herding."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
from common import load, PRIMARY
import matplotlib.pyplot as plt

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(f"{ROOT}/analysis/out_cascade.json"))
IN = json.load(open(f"{ROOT}/analysis/out_inference.json"))
TR = json.load(open(f"{ROOT}/analysis/out_trailer.json"))

recs = load(model=PRIMARY)
casc = [r for r in recs if r["arm"] == "cascade_ng" and r["ok"]]

fig, (ax, bx) = plt.subplots(1, 2, figsize=(5.9, 1.75),
                             gridspec_kw=dict(width_ratios=[1.3, 1], wspace=0.5))

# --- panel a: the funnel, each case centred on its own mean ---
bycase = {}
for r in casc:
    bycase.setdefault(r["cid"], []).append((len(r.get("peer_vals") or []),
                                            r["sentence"] / r["mid"]))
spread = {k: [] for k in range(6)}
for cid, v in bycase.items():
    v.sort()
    m = np.mean([y for _, y in v])
    xs = [p for p, _ in v]; ys = [y - m for _, y in v]
    ax.plot(xs, ys, "-", color=F.MUTED, lw=0.5, alpha=0.45, zorder=2)
    ax.scatter(xs, ys, s=8, color=F.PEER, alpha=0.65, zorder=3, linewidths=0)
    for p, y in zip(xs, ys):
        spread[p].append(abs(y))
mp = [np.mean(spread[k]) for k in range(6) if spread[k]]
ax.plot(range(len(mp)), mp, "-o", color=F.ACCENT, lw=1.4, ms=4, zorder=4,
        mec="white", mew=0.8, label="mean $|$deviation$|$")
ax.axhline(0, color=F.INK, lw=0.7, ls=(0, (3, 3)), zorder=1)
ax.legend(loc="upper right", fontsize=6.4, handlelength=1.2)
ax.set_xticks(range(6)); ax.set_xlim(-0.3, 5.3)
F.finish(ax, "speaking position", "sentence, centred on the case mean",
         "a  Agents converge as the cascade proceeds")
ax.title.set_fontsize(7.4)

# --- panel b: spread, and static pull vs live herding ---
base = C.get("baseline_sd"); e, l = C["convergence"]["early_sd"], C["convergence"]["late_sd"]
bars = [("No peers\n(independent)", base, F.NEUTRAL),
        ("Cascade,\nfirst two", e, F.PEER),
        ("Cascade,\nlast two", l, F.PEER)]
xs = np.arange(len(bars))
bx.bar(xs, [b for _, b, _ in bars], 0.6, color=[c for _, _, c in bars], zorder=3)
for x, (_, v, _) in zip(xs, bars):
    bx.text(x, v + 0.008, f"{v:.3f}", ha="center", fontsize=6.6, color=F.INK)
bx.set_xticks(xs); bx.set_xticklabels([n for n, _, _ in bars], fontsize=6.3)
bx.set_ylim(0, base * 1.22)
F.finish(bx, None, "between-agent SD", "b  Disagreement collapses")
bx.title.set_fontsize(7.4)

fig.savefig(f"{ROOT}/figures/fig_cascade.pdf")
print("wrote fig_cascade.pdf")
print(f"  following beta {C['following']['plain']['beta']:+.3f} (se {C['following']['plain']['se']:.3f})")
print(f"  static bare-peer pull {TR['pull']['peerbare_ng']['pull']:+.3f}")
