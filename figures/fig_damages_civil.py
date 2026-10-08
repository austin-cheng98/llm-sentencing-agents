"""Regenerate Figure 6 from the reported civil-damages summary values."""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/fig_damages_civil.pdf"

mpl.rcParams.update({"font.family": "serif", "font.size": 6.5,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

samples = [
    {"title": "Opus 5 D1 confirm. (n=32)", "n": 32,
     "discordant": [(2, 14), (1, 15), (0, 21)],
     "estimate": .140, "ci": (.032, .248), "mde": .142,
     "color": "#1F4E79", "marker": "o"},
    {"title": "Opus 5 D1 full panel* (n=160)", "n": 160,
     "discordant": [(2, 69), (1, 58), (0, 47)],
     "estimate": .236, "ci": (.145, .328), "mde": .120,
     "color": "#5C6670", "marker": "D"},
    {"title": "GPT-6 Sol D2 (n=159)", "n": 159,
     "discordant": [(20, 18), (17, 18), (15, 24)],
     "estimate": .093, "ci": (.011, .174), "mde": .107,
     "color": "#6B4E9C", "marker": "s"},
]
outcomes = ["Inside band", "Within 2%", "Exact center"]
peer_color = "#1F4E79"
forecast_color = "#C1121F"

fig = plt.figure(figsize=(6.45, 2.636))
grid = fig.add_gridspec(2, 3, left=.25, right=.99, top=.912, bottom=.0991,
                        hspace=.5, wspace=.22, height_ratios=(1.08, 1.0))

for col, sample in enumerate(samples):
    ax = fig.add_subplot(grid[0, col])
    ax.axvline(0, color="#333333", linewidth=.65, zorder=1)
    for row, (peer_only, forecast_only) in enumerate(sample["discordant"]):
        y = 2 - row
        peer_pct = 100 * peer_only / sample["n"]
        forecast_pct = 100 * forecast_only / sample["n"]
        ax.barh(y, peer_pct, left=0, height=.42, color=peer_color, zorder=2)
        ax.barh(y, -forecast_pct, left=0, height=.42, color=forecast_color, zorder=2)
        ax.text(peer_pct + .9, y, str(peer_only), va="center", ha="left",
                color=peer_color, fontsize=6)
        if forecast_pct >= 10:
            ax.text(-forecast_pct / 2, y, str(forecast_only), va="center",
                    ha="center", color="white", fontsize=6, fontweight="bold")
        else:
            ax.text(-forecast_pct - 1.2, y, str(forecast_only), va="center",
                    ha="right", color=forecast_color, fontsize=6)
    ax.set_title(sample["title"], fontsize=6.4, pad=2)
    ax.set_xlim(-70, 22)
    ax.set_xticks([-60, -30, 0, 15])
    ax.set_xlabel("Share of pairs (%)", fontsize=6, labelpad=1)
    ax.grid(axis="x", color="#E8EAED", linewidth=.55, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=6, pad=2)
    ax.tick_params(axis="x", length=2, labelsize=6, pad=1)
    if col == 0:
        ax.set_yticks([2, 1, 0], outcomes)
    else:
        ax.set_yticks([2, 1, 0], ["", "", ""])

ax = fig.add_subplot(grid[1, :])
ax.axvline(0, color="#333333", linewidth=.7, zorder=1)
row_positions = [0.0, 0.9, 1.55]
for y, sample in enumerate(samples):
    y = row_positions[y]
    lo, hi = sample["ci"]
    ax.errorbar(sample["estimate"], y,
                xerr=[[sample["estimate"] - lo], [hi - sample["estimate"]]],
                fmt=sample["marker"], color=sample["color"],
                ecolor=sample["color"], capsize=2.5, markersize=5,
                linewidth=1.25, zorder=3)
    ax.scatter(sample["mde"], y, marker="D", s=18, facecolors="white",
               edgecolors=sample["color"], linewidths=.9, zorder=4)
    # each value label matches its own marker, except the cross-lineage row,
    # whose label stays in ink so no text is set in the lineage colour
    lab_col = "#1A1A1A" if sample["color"] == "#6B4E9C" else sample["color"]
    ax.text(sample["estimate"], y - .40, f"+{sample['estimate']:.3f}",
            color=lab_col, ha="center", va="top", fontsize=6.2)

ax.set_xlim(-.06, .36)
ax.set_xticks([-.05, 0, .05, .10, .15, .20, .25, .30, .35])
ax.set_xticklabels(["-0.05", "0.00", "0.05", "0.10", "0.15", "0.20",
                    "0.25", "0.30", "0.35"])
ax.set_yticks(row_positions, ["Opus 5 D1 confirmation", "Opus 5 D1 full panel*",
                              "GPT-6 Sol D2"])
ax.set_ylim(2.05, -.45)
ax.set_xlabel("Peer minus tool: proportional distance from displayed center",
              fontsize=7, labelpad=1)
ax.grid(axis="x", color="#E8EAED", linewidth=.55, zorder=0)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0, labelsize=6.5, pad=3)
ax.tick_params(axis="x", length=2, labelsize=6, pad=1)
ax.text(.995, .16, "Open diamonds: MDE", transform=ax.transAxes,
        ha="right", va="bottom", color="#8A8F98", fontsize=6.5)

fig.savefig(OUT, metadata={"Title": "Civil-damages proximity outcomes"})
plt.close(fig)
