"""Chart style in the manner of Wall Street Journal and New York Times graphics.

Anatomy of every chart: a serif headline that states the finding, a sans
subtitle with the measure and units, light grey gridlines with value labels
on the left (the unit is written only on the top label, as in "40%"),
abbreviated years ('16, '17), keys made of small coloured squares, direct
labels at the end of lines where possible, and the source in the bottom-left
corner. No newspaper names or logos are used.

Fonts are bundled in assets/fonts under the SIL Open Font License: PT Serif
for headlines and Fira Sans for everything else.

Layout is fixed in inches (figure level) and points (axes level), so text
positions do not depend on the size of the plotting area.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter
from matplotlib.transforms import ScaledTranslation

import config

# Palette: newspaper-graphics reds, blues and neutrals
DEEP_BLUE = "#1D5E9B"
LIGHT_BLUE = "#7FB5DC"
RED = "#C7253E"
SALMON = "#EE7C6B"
PINK = "#F4B6AE"
KHAKI = "#B9AE76"
GREEN = "#8DB33A"
ORANGE = "#E3812B"

INK = "#121212"
TEXT_SOFT = "#5A5A5A"
GRID = "#DDDDDD"
NEUTRAL = "#BDBDBD"
LIGHT_NEUTRAL = "#E3E3E3"
FORECAST_SHADE = "#F3F3F3"

INCOME_COLOURS = {
    "High income": DEEP_BLUE,
    "Upper middle income": LIGHT_BLUE,
    "Lower middle income": SALMON,
    "Low income": RED,
}
# Text in a pale colour is hard to read on white; labels use darker shades.
LABEL_COLOURS = {**INCOME_COLOURS, "Upper middle income": "#3F86BC", "Lower middle income": "#D2553F"}
INCOME_SHORT = {
    "High income": "High income",
    "Upper middle income": "Upper-middle income",
    "Lower middle income": "Lower-middle income",
    "Low income": "Low income",
}

SANS = "Fira Sans"
SERIF = "PT Serif"
DPI = 200

# Vertical layout, inches from the top or bottom edge of the figure
TITLE_Y = 0.22        # top of the headline
SUBTITLE_Y = 0.56     # top of the subtitle
LEGEND_Y = 0.92       # centre of the one-line key, when there is one
HEADER = 1.08         # top of the plotting area without a key
KEY = 0.28            # extra room taken by the key
SOURCE_Y = 0.12       # baseline of the source line
NOTE_LINE = 0.17      # height of one line of footnote
FOOTER = 0.60         # bottom of the plotting area without a note (room for tick labels)
MARGIN = 0.25         # left and right page margin


def setup():
    for path in sorted(config.FONTS.glob("*.ttf")):
        font_manager.fontManager.addfont(str(path))
    plt.rcParams.update({
        "font.family": SANS,
        "font.size": 9.5,
        "text.color": INK,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "axes.linewidth": 0.8,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.major.size": 4,
        "xtick.major.width": 0.7,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.frameon": False,
        "svg.fonttype": "none",
    })


def figure(width, height, title, subtitle, source, note=None, key=False, nrows=1, ncols=1,
           left=MARGIN, axes_left=None, axes_right=MARGIN, wspace=0.4, hspace=0.6,
           header_extra=0.0, footer_extra=0.0, height_ratios=None, **subplot_kw):
    """Create a figure with headline, subtitle and source, and lay out the axes between them.

    Margins are in inches. `left` aligns the text; `axes_left` and
    `axes_right` set the plotting area, which may need extra room for value
    labels, category names or end-of-line labels. `key=True` reserves a line
    under the subtitle for header_key(). A note may span several lines.
    """
    fig = plt.figure(figsize=(width, height))
    note_lines = note.count("\n") + 1 if note else 0
    top_in = HEADER + (KEY if key else 0) + header_extra
    bottom_in = FOOTER + footer_extra + NOTE_LINE * note_lines
    grid = fig.add_gridspec(
        nrows, ncols,
        left=(axes_left if axes_left is not None else left + 0.42) / width, right=1 - axes_right / width,
        top=1 - top_in / height, bottom=bottom_in / height,
        wspace=wspace, hspace=hspace, height_ratios=height_ratios,
    )
    axes = [[fig.add_subplot(grid[r, c], **subplot_kw) for c in range(ncols)] for r in range(nrows)]

    fig.text(left / width, 1 - TITLE_Y / height, title, fontsize=15, family=SERIF,
             va="top", ha="left", color=INK)
    fig.text(left / width, 1 - SUBTITLE_Y / height, subtitle, fontsize=10.5,
             va="top", ha="left", color="#333333")
    fig.text(left / width, SOURCE_Y / height, source, fontsize=8, color=TEXT_SOFT,
             va="bottom", ha="left")
    if note:
        fig.text(left / width, (SOURCE_Y + NOTE_LINE) / height, note, fontsize=8, color=TEXT_SOFT,
                 va="bottom", ha="left", linespacing=1.35)

    flat = [a for row in axes for a in row]
    return fig, (flat[0] if len(flat) == 1 else flat)


def header_key(fig, items, left=MARGIN):
    """A one-line key under the subtitle: items are (label, colour, kind) with kind in
    square, line, dash, dot or diamond."""
    w, h = fig.get_figwidth(), fig.get_figheight()
    x = left / w
    y = 1 - LEGEND_Y / h
    renderer = fig.canvas.get_renderer()
    for label, colour, kind in items:
        if kind == "square":
            fig.add_artist(Rectangle((x, y - 0.05 / h), 0.10 / w, 0.10 / h,
                                     transform=fig.transFigure, color=colour, lw=0))
            x += 0.15 / w
        elif kind in ("line", "dash"):
            fig.add_artist(Line2D([x, x + 0.26 / w], [y, y], transform=fig.transFigure, color=colour,
                                  lw=2.2, ls="-" if kind == "line" else (0, (2, 1.5))))
            x += 0.32 / w
        else:
            marker = {"dot": "o", "diamond": "D"}[kind]
            fig.add_artist(Line2D([x + 0.05 / w], [y], transform=fig.transFigure,
                                  marker=marker, ms=5.5, color=colour, lw=0))
            x += 0.15 / w
        t = fig.text(x, y, label, fontsize=9, va="center", ha="left")
        x += t.get_window_extent(renderer).width / fig.dpi / w + 0.22 / w


def offset(ax, points):
    return ScaledTranslation(0, points / 72, ax.figure.dpi_scale_trans)


def panel_title(ax, title, subtitle=None, top=None):
    """Bold sans panel heading above a small multiple or a chart panel."""
    top = top if top is not None else (30 if subtitle else 16)
    ax.annotate(title, (0, 1), xycoords="axes fraction", xytext=(0, top), textcoords="offset points",
                fontsize=10.5, fontweight="bold", va="bottom", ha="left")
    if subtitle:
        ax.annotate(subtitle, (0, 1), xycoords="axes fraction", xytext=(0, top - 14),
                    textcoords="offset points", fontsize=9, va="bottom", ha="left", color=TEXT_SOFT)


def value_axis(ax, ticks, unit="", zero=None, ylim=None, size=9.5, fmt="{:g}"):
    """Grey gridlines with value labels on the left; the unit appears only on the top label."""
    ax.set_ylim(*(ylim or (min(ticks), max(ticks))))
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    top = max(ticks)

    def label(v, _):
        text = fmt.format(v).replace("-", "−")
        return text + unit if v == top else text

    ax.yaxis.set_major_formatter(FuncFormatter(label))
    ax.tick_params(axis="y", length=0, pad=4, labelsize=size, labelcolor=INK)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.axhline(zero if zero is not None else min(ticks), color=INK, lw=1.0, zorder=3)


def x_title(ax, text):
    """Axis title under the tick labels at the right end of the x-axis (needs ~0.2in of footer)."""
    ax.annotate(text, (1, 0), xycoords="axes fraction", xytext=(0, -22), textcoords="offset points",
                ha="right", va="top", fontsize=9, color=INK)


def year_axis(ax, years, first_full=True):
    """Newspaper-style year ticks: 2015, '17, '19, ..."""
    ax.set_xticks(years)
    labels = [str(y) if (i == 0 and first_full) else f"’{y % 100:02d}" for i, y in enumerate(years)]
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", direction="out", length=4, color=INK)


def end_label(ax, x, y, text, colour, transform=None, size=9.5):
    """WSJ-style direct label: a small coloured square followed by the series name."""
    tr = transform or ax.transData
    shift = ScaledTranslation(10 / 72, 0, ax.figure.dpi_scale_trans)
    ax.plot([x], [y], marker="s", ms=6.5, color=colour, lw=0, transform=tr + shift, clip_on=False)
    ax.annotate(text, (x, y), xycoords=tr, xytext=(17, 0), textcoords="offset points",
                color=INK, fontsize=size, va="center", ha="left", annotation_clip=False)


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
    fig.savefig(path, dpi=DPI, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return path
