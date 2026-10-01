"""Headline figure: seven estimates of one quantity."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
import matplotlib.pyplot as plt

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = json.load(open(f"{ROOT}/analysis/out_inference.json"))
TR = json.load(open(f"{ROOT}/analysis/out_trailer.json"))
# the cross-lineage arm, copied from analysis/out_crosslineage.json in the
# artifact repository. It is exploratory and was not pre-registered, so it
# carries no label-swap null and is drawn without a design-null band.
XL = json.load(open(f"{ROOT}/analysis/out_crosslineage.json"))["rows"]
C, BM = IN["contrast"], TR["by_model"]

# every row carries the design null of its own contrast, not a shared band
rows = [
    ("Bare blocks", "Opus 5", C["matched_bare"]["est"], C["matched_bare"]["se"]["case"],
     F.PEER, C["matched_bare"]["null_p95"]),
    ("Structure-matched blocks", "Opus 5", C["matched_struct"]["est"],
     C["matched_struct"]["se"]["case"], F.PEER, C["matched_struct"]["null_p95"]),
    ("With original closing lines", "Opus 5", C["original_sentences"]["est"],
     C["original_sentences"]["se"]["case"], F.NEUTRAL,
     C["original_sentences"]["null_p95"]),
    ("Bare blocks", "Haiku 4.5", BM["haiku45"]["est"], BM["haiku45"]["se"], F.ACCENT,
     BM["haiku45"].get("null_p95")),
    ("Bare blocks", "Sonnet 5", BM["sonnet5"]["est"], BM["sonnet5"]["se"], F.ACCENT,
     BM["sonnet5"].get("null_p95")),
    ("Structure-matched blocks", "GPT-6 Luna", XL["gpt6|matched_struct"]["est"],
     XL["gpt6|matched_struct"]["se"], F.CROSS, None),
    ("Bare blocks", "GPT-6 Luna", XL["gpt6|matched_bare"]["est"],
     XL["gpt6|matched_bare"]["se"], F.CROSS, None),
]

# flatter than it is tall: at \textwidth the rendered height is the aspect
# ratio times the text width, so widening the canvas buys vertical space in the
# paper without shrinking the type
fig, ax = plt.subplots(figsize=(6.9, 1.62))
ax.text(0.0, 1.02, "design null, per contrast", transform=ax.get_xaxis_transform(),
        fontsize=9.6, color=F.MUTED, va="bottom", ha="center", style="italic")
ax.axvline(0, color=F.INK, lw=0.7, zorder=1)
for k, (lab, mdl, e, se, col, nl) in enumerate(rows):
    y = len(rows) - 1 - k
    if nl:
        ax.barh(y, 2 * nl, left=-nl, height=0.70, color=F.FAINT, zorder=0,
                linewidth=0)
    ax.plot([e - 1.96 * se, e + 1.96 * se], [y, y], color=col, lw=1.6,
            solid_capstyle="round", zorder=3)
    ax.plot([e], [y], "o", ms=5.5, color=col, mec="white", mew=0.9, zorder=4)
    ax.text(0.74, y, f"{e:+.2f}", fontsize=10.8, va="center", ha="right",
            color=F.INK, fontweight="bold" if (nl and abs(e) > nl) else "normal")
ax.set_yticks(range(len(rows)))
# one line per row, so seven rows stand no taller than the original five
ax.set_yticklabels([f"{l}, {m}" for l, m, *_ in rows][::-1], fontsize=10.8)
ax.set_ylim(-0.6, len(rows) - 0.35)
ax.set_xlim(-0.26, 0.76)
ax.set_xticks([-0.2, 0.0, 0.2, 0.4])
ax.tick_params(axis="x", labelsize=10.2)
ax.xaxis.label.set_size(10.8)
F.finish(ax, "peer premium (95% CI)", None, None)
fig.savefig(f"{ROOT}/figures/fig_forest.pdf")
print("wrote fig_forest.pdf")
