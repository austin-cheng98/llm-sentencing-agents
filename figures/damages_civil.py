"""Plot civil-damages proximity outcomes and central-distance estimates."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figstyle as F


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    with path.open() as stream:
        return json.load(stream)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("fig_damages_civil.pdf"))
    args = parser.parse_args()

    confirmation = load(ROOT / "analysis" / "damages_d1_prox.json")
    pooled = load(ROOT / "analysis" / "damages_d2.json")
    samples = [
        {
            "title": "Opus 5 D1 confirmation\n32 matched pairs",
            "data": confirmation,
            "keys": ("estimand1_inside_band", "estimand3_within_two_percent", "estimand4_equals_central"),
            "distance": confirmation["estimand2_paired_distance"],
            "color": F.PEER,
            "marker": "o",
        },
        {
            "title": "Opus 5 D1 full panel*\n160 matched pairs",
            "data": pooled["D1_Opus5"]["proximity"]["measures"],
            "keys": ("inside_band", "within_tol", "equals_central"),
            "distance": pooled["D1_Opus5"]["proximity"]["measures"]["dist_central"],
            "color": F.NEUTRAL,
            "marker": "D",
        },
        {
            "title": "GPT-6 Sol D2\n159 matched pairs",
            "data": pooled["D2_GPT6Sol_high"]["proximity"]["measures"],
            "keys": ("inside_band", "within_tol", "equals_central"),
            "distance": pooled["D2_GPT6Sol_high"]["proximity"]["measures"]["dist_central"],
            "color": F.CROSS,
            "marker": "s",
        },
    ]
    metric_names = ("Inside displayed band", "Within 2% of center", "Exactly at center")

    F.setup()
    fig = plt.figure(figsize=(6.8, 3.0))
    grid = fig.add_gridspec(2, 3, height_ratios=(1.65, 1.0), hspace=0.35, wspace=0.36)
    top_axes = [fig.add_subplot(grid[0, i]) for i in range(3)]

    for ax, sample in zip(top_axes, samples):
        for row, (name, key) in enumerate(zip(metric_names, sample["keys"])):
            value = sample["data"][key]
            n = value["n_pairs"]
            peer = 100 * value["peer_total"] / n
            tool = 100 * value["tool_total"] / n
            y = 2 - row
            yp, yt = y + 0.12, y - 0.12
            ax.plot([peer, tool], [yp, yt], color=F.MUTED, linewidth=0.8, zorder=1)
            ax.scatter(peer, yp, color=F.PEER, marker="o", s=25, zorder=3)
            ax.scatter(tool, yt, color=F.TOOL, marker="s", s=23, zorder=3)
            ax.annotate(f"{peer + 1e-8:.1f}%", (peer, yp), xytext=(0, 5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=6.7, color=F.PEER)
            ax.annotate(f"{tool + 1e-8:.1f}%", (tool, yt), xytext=(0, -5), textcoords="offset points",
                        ha="center", va="top", fontsize=6.7, color=F.TOOL)
        ax.set_title(sample["title"], loc="left", fontsize=8, fontweight="bold", pad=1)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.58, 2.58)
        ax.set_xticks((0, 50, 100), labels=("0", "50", "100"))
        ax.set_yticks((2, 1, 0), metric_names)
        ax.grid(axis="x", color=F.FAINT, linewidth=0.7)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0, labelsize=7)
        ax.tick_params(axis="x", labelsize=7)
        if ax is not top_axes[0]:
            ax.tick_params(axis="y", labelleft=False)
        ax.spines["left"].set_visible(False)

    top_axes[0].set_ylabel("Award proximity", fontsize=7.5, labelpad=5)
    ax = fig.add_subplot(grid[1, :])
    distance_samples = [
        ("Opus 5 D1 confirmation", samples[0]["distance"], F.PEER, "o"),
        ("Opus 5 D1 full panel*", samples[1]["distance"], F.NEUTRAL, "D"),
        ("GPT-6 Sol D2", samples[2]["distance"], F.CROSS, "s"),
    ]
    for row, (label, result, color, marker) in enumerate(distance_samples):
        y = 2 - row
        lo, hi = result["ci95_t"]
        estimate = result.get("est", result.get("peer_minus_tool"))
        mde = result["mde"]
        ax.errorbar(estimate, y, xerr=[[estimate - lo], [hi - estimate]], fmt=marker,
                    color=color, markersize=5, capsize=2.7, linewidth=1.0, zorder=3)
        ax.scatter(mde, y, marker="D", s=17, facecolor="white", edgecolor=color,
                   linewidth=0.9, zorder=4)
        ax.annotate(f"{estimate:+.3f}", (estimate, y), xytext=(0, 7), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, color=color)
    ax.axvline(0, color=F.MUTED, linewidth=0.8, linestyle=(0, (2, 2)), zorder=0)
    ax.set_yticks((2, 1, 0), [item[0] for item in distance_samples])
    ax.set_xlim(-0.06, 0.36)
    ax.set_ylim(-0.55, 2.55)
    ax.set_xlabel("Peer minus tool: proportional distance from displayed center", fontsize=7.5, labelpad=3)
    ax.grid(axis="x", color=F.FAINT, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, labelsize=7.3)
    ax.tick_params(axis="x", labelsize=7)
    ax.spines["left"].set_visible(False)
    ax.text(0.99, -0.34, "Open diamonds: MDE", transform=ax.transAxes, ha="right",
            va="top", fontsize=6.8, color=F.MUTED)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output)
    plt.close(fig)


if __name__ == "__main__":
    main()
