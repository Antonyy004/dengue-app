"""
utils/charts.py — Konstanta warna & helper styling chart matplotlib
"""

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")

# ── Color palette ─────────────────────────────────────────────────────────────
DARK_BG   = "#0a192f"
GRID_COL  = "#1d3461"
TEXT_COL  = "#ccd6f6"
MUTED_COL = "#8892b0"
ACCENT    = "#64ffda"
PALETTE   = [
    "#64ffda", "#ff6b6b", "#ffd166", "#a29bfe",
    "#74b9ff", "#fd79a8", "#00b894", "#e17055",
]


def style_ax(ax, fig, title=""):
    """Terapkan dark theme ke matplotlib axes."""
    ax.set_facecolor(DARK_BG)
    fig.patch.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT_COL)
    ax.spines[:].set_color(GRID_COL)
    ax.xaxis.label.set_color(MUTED_COL)
    ax.yaxis.label.set_color(MUTED_COL)
    if title:
        ax.set_title(title, color=TEXT_COL, fontsize=13)
    ax.grid(alpha=0.12, color=MUTED_COL)


def new_fig(w=10, h=4):
    """Shortcut buat figure baru dengan ukuran default."""
    return plt.subplots(figsize=(w, h))
