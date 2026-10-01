"""Figure: how far agents move when the numbers in front of them are displaced."""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "analysis")]
import figstyle as F
from common import load, ols, cluster_vcov, PRIMARY
import matplotlib.pyplot as plt

F.setup()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = {"peerdelta": "Peer judges", "tooldelta": "Statistical forecast",
       "clerdelta": "Docketing artifact",
       "peerdelta_ng": "Peer judges", "tooldelta_ng": "Statistical forecast",
       "clerdelta_ng": "Docketing artifact",
       "peerbare_ng": "Peer judges", "toolbare_ng": "Statistical forecast"}
COL = {"peerdelta": F.PEER, "tooldelta": F.TOOL, "clerdelta": F.ACCENT,
       "peerdelta_ng": F.PEER, "tooldelta_ng": F.TOOL, "clerdelta_ng": F.ACCENT,
       "peerbare_ng": F.PEER, "toolbare_ng": F.TOOL}
CTX = {False: "guideline present", True: "guideline removed"}


def slope(d):
    x = np.array([r["delta"] for r in d]); y = np.array([r["dev"] for r in d])
    F = np.column_stack([[r[f] for r in d] for f in
                         ("severity", "prior", "remorse", "cooperation")]).astype(float)
    X = np.column_stack([np.ones(len(x)), x, F])
    b = ols(X, y)
    g = np.array([r["cid"] for r in d])
    V = cluster_vcov(X, y, b, g)
    return b[0] + F.mean(0) @ b[2:], b[1], np.sqrt(V[1, 1])


def panel(ax, recs, arms, title, xlabel=None, adopt_x=0.358):
    for arm in arms:
        d = [r for r in recs if r["arm"] == arm]
        if len(d) < 6:
            continue
        # fix the order so the scatter jitter below does not depend on how the
        # records happened to arrive from disk
        d.sort(key=lambda r: (r["judge"], r["step"]))
        a, b, se = slope(d)
        xs = np.array([r["delta"] for r in d]); ys = np.array([r["dev"] for r in d])
        # jitter only along x, so the vertical reading stays exact
        jit = (np.random.default_rng(3).random(len(xs)) - 0.5) * 0.022
        ax.scatter(xs + jit, ys, s=7, alpha=0.30, color=COL[arm], linewidths=0,
                   zorder=2)
        for dv in sorted(set(xs)):
            m = xs == dv
            ax.plot([dv], [ys[m].mean()], "o", ms=5, color=COL[arm],
                    mec="white", mew=0.8, zorder=4)
        gx = np.linspace(-0.34, 0.34, 20)
        ax.plot(gx, a + b * gx, color=COL[arm], lw=1.6, zorder=3,
                label=f"{LAB[arm]}  $\\hat{{\\pi}}$={b:+.2f}")
    ax.axhline(0, color=F.MUTED, lw=0.6, ls=(0, (3, 3)), zorder=1)
    # reference line: an agent that simply adopts the displayed numbers
    ax.plot([-0.32, 0.32], [-0.32, 0.32], color=F.MUTED, lw=0.8, ls=":", zorder=1)
    ax.text(adopt_x, 0.30, "full\nadoption", fontsize=6.2, color=F.MUTED,
            ha="left", va="center", style="italic", linespacing=1.1, clip_on=False)
    ax.set_xlim(-0.42, 0.46); ax.set_xticks([-0.30, -0.15, 0.15, 0.30])
    ax.set_xticklabels(["$-$30", "$-$15", "+15", "+30"], fontsize=7.5)
    ax.legend(loc="upper left", handlelength=1.3, borderpad=0.15, labelspacing=0.2,
              fontsize=7, handletextpad=0.5)
    F.finish(ax, xlabel, None, title)


def main():
    allrecs = [r for r in load() if r.get("delta") is not None]
    recs = [r for r in allrecs if r["model"] == PRIMARY]
    gpt = [r for r in allrecs if r["model"] == "gpt6"]
    fig = plt.figure(figsize=(8.7, 2.05))
    # a narrow empty column sets the pull panel off from the three scatters
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 0.04, 0.80], wspace=0.62)
    a1 = fig.add_subplot(gs[0, 0])
    a2 = fig.add_subplot(gs[0, 1], sharey=a1)
    a3 = fig.add_subplot(gs[0, 2], sharey=a1)
    a4 = fig.add_subplot(gs[0, 4])
    panel(a1, recs, ["peerdelta", "tooldelta", "clerdelta"], "a  Guideline present")
    panel(a2, recs, ["peerbare_ng", "toolbare_ng", "clerdelta_ng"],
          "b  Guideline removed",
          xlabel="displacement $\\delta$ of the shown numbers (%)", adopt_x=0.392)
    panel(a3, gpt, ["peerbare_ng", "toolbare_ng"],
          "c  GPT-6 Luna, guideline removed", adopt_x=0.392)
    a2.xaxis.set_label_coords(0.5, -0.20)
    # nudge the pull panel left, closer to the scatters
    bb = a4.get_position()
    a4.set_position([bb.x0 - 0.014, bb.y0, bb.width, bb.height])
    a1.set_ylabel("sentence, deviation from\nguideline midpoint")
    plt.setp(a2.get_yticklabels(), visible=False)
    plt.setp(a3.get_yticklabels(), visible=False)

    rows = []
    for model, arm in [(PRIMARY, "peerbare_ng"), (PRIMARY, "toolbare_ng"),
                       (PRIMARY, "peerdelta_ng"), (PRIMARY, "tooldelta_ng"),
                       (PRIMARY, "clerdelta_ng"),
                       ("gpt6", "peerbare_ng"), ("gpt6", "toolbare_ng")]:
        d = [r for r in allrecs if r["model"] == model and r["arm"] == arm]
        if len(d) >= 6:
            _, b, se = slope(d)
            rows.append((model, arm, b, se, len(d)))
    ypos = np.arange(len(rows))[::-1]
    for y, (model, arm, b, se, n) in zip(ypos, rows):
        col = F.CROSS if model == "gpt6" else COL[arm]
        a4.plot([b - 1.96 * se, b + 1.96 * se], [y, y], color=col, lw=1.5,
                solid_capstyle="butt")
        a4.plot([b], [y], "o", ms=5, color=col, mec="white", mew=0.8)
    a4.axvline(0, color=F.MUTED, lw=0.6, ls=(0, (3, 3)))
    a4.set_yticks(ypos)
    short = {"peerbare_ng": "Peer, bare", "toolbare_ng": "Forecast, bare",
             "peerdelta_ng": "Peer, closing line", "tooldelta_ng": "Forecast, hedged",
             "clerdelta_ng": "Docketing"}
    a4.set_yticklabels([short[a] + ("  (GPT-6)" if m == "gpt6" else "")
                        for m, a, _, _, _ in rows], fontsize=6.4)
    a4.tick_params(axis="y", pad=1.5)
    a4.set_ylim(-0.6, len(rows) - 0.4)
    F.finish(a4, "pull  $\\hat{\\pi}$  (95% CI)", None, "d  Pull")
    fig.savefig(f"{ROOT}/figures/fig_main.pdf")
    fig.savefig(f"{ROOT}/figures/fig_main.png")
    print("wrote figures/fig_main.pdf")
    for model, arm, b, se, n in rows:
        print(f"  {model:7s} {arm:14s} pull={b:+.3f} se={se:.3f} n={n}")


if __name__ == "__main__":
    main()
