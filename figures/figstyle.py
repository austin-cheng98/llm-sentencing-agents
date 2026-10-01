"""Shared plotting style.

Serif type at the paper's own size, thin axes, no gridlines competing with the
data, and a small palette that stays legible in greyscale.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#1a1a1a"
MUTED = "#8a8f98"
PEER = "#1f4e79"      # peer framing
TOOL = "#c1121f"      # tool framing
NEUTRAL = "#5c6670"
ACCENT = "#2a7f62"
CROSS = "#6b4e9c"     # a lineage outside the Claude family
FAINT = "#e8eaed"

def setup():
    plt.rcParams.update({
        # NeurIPS prohibits Type 3 fonts; 42 embeds TrueType instead of
        # matplotlib's default Type 3 glyph procedures
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 8.5,
        "axes.labelsize": 8.5,
        "axes.titlesize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.7,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.dpi": 400,
        "savefig.dpi": 400,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "lines.solid_capstyle": "round",
    })

def finish(ax, xlabel=None, ylabel=None, title=None):
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if title: ax.set_title(title, loc="left", fontweight="bold", pad=6)
    ax.tick_params(direction="out")
    return ax
