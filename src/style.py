"""Chart style modelled on The Economist's data-visualisation conventions.

Anatomy of every chart: a red rule and tag at the top, a bold title that
states the finding, a subtitle that gives the measure and units, horizontal
gridlines with value labels sitting on the right above each line, direct
labels instead of legends where possible, and the source in the bottom-left
corner. Fira Sans (SIL Open Font License, bundled in assets/fonts) stands in
for The Economist's proprietary Econ Sans.

Layout is fixed in inches (figure level) and points (axes level) so that
text never depends on the size of the plotting area.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory

import config

# Palette
RED_TAG = "#E3120B"    # brand red: the tag and top rule only
BLUE1 = "#006BA2"
BLUE2 = "#3EBCD2"
GREEN = "#379A8B"
YELLOW = "#EBB434"
OLIVE = "#B4BA39"
PURPLE = "#9A607F"
GOLD = "#D1B07C"
RED = "#DB444B"
GREY = "#758D99"

TEXT = "#0C0C0C"
TEXT_SOFT = "#4D5A62"
GRID = "#B7C6CF"
MUTED = "#C9D3D9"
PALE_BLUE = "#8FB3C8"
FORECAST_SHADE = "#EEF2F4"

INCOME_COLOURS = {
    "High income": BLUE1,
    "Upper middle income": BLUE2,
    "Lower middle income": YELLOW,
    "Low income": RED,
}
# Yellow is too pale for text on white; labels use a darker shade of it.
LABEL_COLOURS = {**INCOME_COLOURS, "Lower middle income": "#A9790F"}
INCOME_SHORT = {
    "High income": "High income",
    "Upper middle income": "Upper-middle income",
    "Lower middle income": "Lower-middle income",
    "Low income": "Low income",
}

FONT = "Fira Sans"
DPI = 200

# Vertical layout, inches from the top or bottom edge of the figure
TITLE_Y = 0.30        # top of the title
SUBTITLE_Y = 0.54     # top of the subtitle
LEGEND_Y = 0.88       # centre of the one-line key, when there is one
HEADER = 0.98         # top of the plotting area without a key
KEY = 0.30            # extra room taken by the key
SOURCE_Y = 0.14       # baseline of the source line
NOTE_LINE = 0.17      # height of one line of footnote
FOOTER = 0.62         # bottom of the plotting area without a note (leaves room for tick labels)


def setup():
    for path in sorted(config.FONTS.glob("*.ttf")):
        font_manager.fontManager.addfont(str(path))
    plt.rcParams.update({
        "font.family": FONT,
        "font.size": 9.5,
        "text.color": TEXT,
        "axes.edgecolor": TEXT,
        "axes.labelcolor": TEXT,
        "axes.linewidth": 0.9,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "xtick.major.size": 4,
        "xtick.major.width": 0.8,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.frameon": False,
        "svg.fonttype": "none",
    })


def figure(width, height, title, subtitle, source, note=None, key=False, nrows=1, ncols=1,
           left=0.25, axes_left=None, axes_right=0.25, wspace=0.55, hspace=0.6,
           header_extra=0.0, footer_extra=0.0, **subplot_kw):
    """Create a figure with the header and footer drawn, and the axes laid out between them.

    Margins are in inches. `left` aligns the title, subtitle and source;
    `axes_left` and `axes_right` set the plotting area, which may need extra
    room for category names or end-of-line labels. `key=True` reserves a line
    under the subtitle for header_key(). A note may span several lines.
    """
    fig = plt.figure(figsize=(width, height))
    note_lines = note.count("\n") + 1 if note else 0
    top_in = HEADER + (KEY if key else 0) + header_extra
    bottom_in = FOOTER + footer_extra + NOTE_LINE * note_lines
    grid = fig.add_gridspec(
        nrows, ncols,
        left=(axes_left if axes_left is not None else left) / width, right=1 - axes_right / width,
        top=1 - top_in / height, bottom=bottom_in / height,
        wspace=wspace, hspace=hspace,
    )
    axes = [[fig.add_subplot(grid[r, c], **subplot_kw) for c in range(ncols)] for r in range(nrows)]

    # Red rule across the top and the red tag at the left.
    fig.add_artist(Line2D([0, 1], [1 - 0.006 / height] * 2, transform=fig.transFigure,
                          color=RED_TAG, lw=1.2))
    fig.add_artist(Rectangle((left / width, 1 - 0.11 / height), 0.38 / width, 0.11 / height,
                             transform=fig.transFigure, color=RED_TAG, lw=0))
    fig.text(left / width, 1 - TITLE_Y / height, title, fontsize=13.5, fontweight="bold",
             va="top", ha="left")
    fig.text(left / width, 1 - SUBTITLE_Y / height, subtitle, fontsize=10.5,
             va="top", ha="left", color=TEXT)
    fig.text(left / width, SOURCE_Y / height, source, fontsize=8, color=TEXT_SOFT,
             va="bottom", ha="left")
    if note:
        fig.text(left / width, (SOURCE_Y + NOTE_LINE) / height, note, fontsize=8, color=TEXT_SOFT,
                 va="bottom", ha="left", linespacing=1.35)

    flat = [a for row in axes for a in row]
    return fig, (flat[0] if len(flat) == 1 else flat)


def header_key(fig, items, left=0.25):
    """A one-line key under the subtitle: items are (label, colour, kind) with kind in
    square, line, dash, dot or diamond."""
    w, h = fig.get_figwidth(), fig.get_figheight()
    x = left / w
    y = 1 - LEGEND_Y / h
    renderer = fig.canvas.get_renderer()
    for label, colour, kind in items:
        if kind == "square":
            fig.add_artist(Rectangle((x, y - 0.055 / h), 0.11 / w, 0.11 / h,
                                     transform=fig.transFigure, color=colour, lw=0))
            x += 0.16 / w
        elif kind in ("line", "dash"):
            fig.add_artist(Line2D([x, x + 0.26 / w], [y, y], transform=fig.transFigure, color=colour,
                                  lw=2, ls="-" if kind == "line" else (0, (2, 1.5))))
            x += 0.32 / w
        else:
            marker = {"dot": "o", "diamond": "D"}[kind]
            fig.add_artist(Line2D([x + 0.05 / w], [y], transform=fig.transFigure,
                                  marker=marker, ms=5.5, color=colour, lw=0))
            x += 0.15 / w
        t = fig.text(x, y, label, fontsize=9, va="center", ha="left")
        x += t.get_window_extent(renderer).width / fig.dpi / w + 0.22 / w


def panel_title(ax, title, subtitle=None):
    """Bold panel heading under a thin black rule, as in multi-panel Economist charts.
    Needs about 0.62in above the axes (0.45in without a subtitle)."""
    top = 44 if subtitle else 32
    ax.add_artist(Line2D([0, 1], [1, 1], transform=ax.transAxes + offset(ax, top),
                         color=TEXT, lw=0.8, clip_on=False))
    ax.annotate(title, (0, 1), xycoords="axes fraction", xytext=(0, top - 3), textcoords="offset points",
                fontsize=10.5, fontweight="bold", va="top", ha="left")
    if subtitle:
        ax.annotate(subtitle, (0, 1), xycoords="axes fraction", xytext=(0, top - 18),
                    textcoords="offset points", fontsize=9, va="top", ha="left", color=TEXT_SOFT)


def offset(ax, points):
    from matplotlib.transforms import ScaledTranslation
    return ScaledTranslation(0, points / 72, ax.figure.dpi_scale_trans)


def value_axis(ax, ticks, fmt="{:g}", zero=None, ylim=None, size=9.5):
    """Horizontal gridlines with labels sitting on top of each line at the right edge."""
    ax.set_yticks(ticks)
    ax.set_ylim(*(ylim or (min(ticks), max(ticks))))
    ax.tick_params(axis="y", length=0, labelleft=False, labelright=False)
    ax.grid(axis="y", color=GRID, lw=0.75, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    trans = blended_transform_factory(ax.transAxes, ax.transData)
    for t in ticks:
        ax.text(1, t, fmt.format(t).replace("-", "−"), transform=trans, ha="right", va="bottom",
                fontsize=size, color=TEXT, clip_on=False)
    ax.axhline(zero if zero is not None else min(ticks), color=TEXT, lw=1.0, zorder=3)


def x_title(ax, text):
    """Axis title under the tick labels at the right end of the x-axis (needs ~0.2in of footer)."""
    ax.annotate(text, (1, 0), xycoords="axes fraction", xytext=(0, -22), textcoords="offset points",
                ha="right", va="top", fontsize=9, color=TEXT)


def year_axis(ax, years, first_full=True):
    """Economist-style year ticks: 2015, 16, 17, ..."""
    ax.set_xticks(years)
    labels = [str(y) if (i == 0 and first_full) else f"{y % 100:02d}" for i, y in enumerate(years)]
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", direction="out", length=4, color=TEXT)


def spread_labels(positions, min_gap):
    """Nudge label y-positions apart so that none are closer than min_gap."""
    order = sorted(range(len(positions)), key=lambda i: positions[i])
    out = list(positions)
    for _ in range(50):
        moved = False
        for a, b in zip(order, order[1:]):
            if out[b] - out[a] < min_gap:
                shift = (min_gap - (out[b] - out[a])) / 2
                out[a] -= shift
                out[b] += shift
                moved = True
        if not moved:
            break
    return out


def save(fig, name):
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES / f"{name}.png"
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    return path
