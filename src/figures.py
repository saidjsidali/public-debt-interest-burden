"""Produce every figure in the report from the output tables.

Figures 1-6 are in the main report and A1-A3 in the appendix. Each chart
answers one question. Label offsets for named countries are set by hand
because they depend on the fixed data snapshot; everything plotted comes from
outputs/tables/ or outputs/key_numbers.json, and source labels come from the
retrieval log.
"""

import json

import numpy as np
import pandas as pd
from matplotlib import patheffects
from matplotlib.transforms import blended_transform_factory

import config
import style
from style import (DEEP_BLUE, FORECAST_SHADE, GRID, INCOME_COLOURS, INCOME_SHORT, INK, LIGHT_BLUE,
                   NEUTRAL, PINK, RED, TEXT_SOFT)

S, B, E, X, F = (config.START_YEAR, config.BREAK_YEAR, config.END_YEAR,
                 config.ESTIMATE_YEAR, config.FORECAST_END)
GROUPS = config.INCOME_ORDER
DASH = (0, (2, 1.5))
WIDTH = 7.2
FORECAST_NOTE = f"*{X} mostly estimates; {X + 1}-{F % 100} IMF projections"


def _vintage(code):
    log = json.loads((config.DATA_RAW / "retrieval_log.json").read_text(encoding="utf-8"))
    return log["imf_datamapper"]["vintage_by_series"][code]


FM = _vintage("GGR_G01_GDP_PT")
FPP = _vintage("ie")
SOURCE = f"Source: IMF {FM}; World Bank (income groups)"


def table(name):
    return pd.read_csv(config.TABLES / f"{name}.csv")


def numbers():
    return json.loads(config.KEY_NUMBERS.read_text(encoding="utf-8"))


def short(name):
    return name.replace(", Arab Rep.", "").replace(" SAR, China", "")


def _line_with_forecast(ax, series, colour, lw=2.2, zorder=4):
    hist, fut = series.loc[:E], series.loc[E:]
    ax.plot(hist.index, hist.values, color=colour, lw=lw, solid_capstyle="round", zorder=zorder)
    ax.plot(fut.index, fut.values, color=colour, lw=lw, ls=DASH, zorder=zorder)


HALO = [patheffects.withStroke(linewidth=2.5, foreground="white")]  # keeps labels readable over dots and lines


def _annotate(ax, x, y, text, dx=6, dy=0, ha="left", colour=INK, size=8.5, leader=False):
    line = dict(arrowstyle="-", color=TEXT_SOFT, lw=0.6, shrinkA=1, shrinkB=3) if leader else None
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                fontsize=size, color=colour, zorder=6, arrowprops=line, path_effects=HALO)


def _label_points(ax, df, x, y, positions):
    """positions: name -> (dx, dy, ha) or (dx, dy, ha, True) for a thin line from label to dot."""
    for _, r in df[df["name"].isin(positions)].iterrows():
        dx, dy, ha, *leader = positions[r["name"]]
        _annotate(ax, r[x], r[y], short(r["name"]), dx=dx, dy=dy, ha=ha, leader=bool(leader))


# --- Figure 3: highest burdens -------------------------------------------------

def fig3_highest_burdens():
    rank = table("burden_ranking").head(20)
    change = table("burden_change").set_index("iso3")
    k = numbers()
    n = len(rank)
    h = 2.25 + n * 0.235
    fig, ax = style.figure(
        WIDTH, h,
        f"In {E}, {k['high_burden']['countries'][str(E)]} governments spent over a fifth "
        "of revenue on net interest",
        f"Net interest, % of government revenue, {E}, the 20 highest. Right: gross debt, % of GDP",
        SOURCE, key=True, axes_left=1.75, axes_right=1.0, footer_extra=-0.22,
        note="Fiscal coverage is general government for most countries but can be narrower for some")
    style.header_key(fig, [(INCOME_SHORT[g], INCOME_COLOURS[g], "square") for g in GROUPS]
                     + [(f"{S} value", INK, "dot")])
    ypos = np.arange(n)[::-1]
    ax.barh(ypos, rank["interest_burden"], color=[INCOME_COLOURS[g] for g in rank["income_group"]],
            height=0.66, zorder=3)
    ax.plot(change.loc[rank["iso3"], "burden_start"].values, ypos, "o", color=INK, ms=3.6, zorder=4)
    rows = blended_transform_factory(ax.transAxes, ax.transData)
    for y, v, name, debt in zip(ypos, rank["interest_burden"], rank["name"], rank["debt_gdp"]):
        ax.text(v + 0.8, y, f"{v:.1f}", va="center", fontsize=8.5)
        ax.text(-0.02, y, short(name), transform=rows, ha="right", va="center", fontsize=9.5)
        ax.text(1.10, y, f"{debt:.0f}", transform=rows, ha="right", va="center", fontsize=8.5,
                color=TEXT_SOFT)
    ax.text(1.10, n - 0.2, "Debt", transform=rows, ha="right", va="bottom", fontsize=8.5,
            color=TEXT_SOFT, fontweight="bold")
    ax.set_yticks([])
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks(range(0, 71, 10))
    ax.set_xticklabels([f"{t}%" if t == 70 else str(t) for t in range(0, 71, 10)])
    ax.set_xlim(0, 70)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=3, labelsize=9)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_linewidth(1.0)
    return style.save(fig, "fig3_highest_burdens")


# --- Figure 1: income-group medians ----------------------------------------------

def fig1_income_group_trend():
    med = table("group_medians")
    med = med[med["variable"] == "interest_burden"]
    fig, ax = style.figure(
        WIDTH, 4.9,
        "The median net burden rose most in low-income countries",
        "Median net interest, % of revenue, by World Bank income group (current classification)",
        SOURCE, note=FORECAST_NOTE, axes_right=1.75)
    ax.axvspan(E, F + 0.5, color=FORECAST_SHADE, zorder=0, lw=0)
    ax.text(E + 0.2, 11.7, "Estimates and\nprojections*", fontsize=8.5, color=TEXT_SOFT, va="top")
    ends = {}
    for g in GROUPS:
        d = med[med["income_group"] == g].set_index("year")["median"]
        _line_with_forecast(ax, d, INCOME_COLOURS[g])
        ends[g] = d.loc[F]
    style.value_axis(ax, [0, 2, 4, 6, 8, 10, 12], unit="%", zero=0)
    ax.set_xlim(S - 0.3, F + 0.5)
    style.year_axis(ax, list(range(S, F + 1, 2)))
    for g, y in zip(GROUPS, style.spread_labels([ends[g] for g in GROUPS], 0.8)):
        style.end_label(ax, F + 0.5, y, INCOME_SHORT[g], INCOME_COLOURS[g])
    return style.save(fig, "fig1_income_group_trend")


# --- Figure 2: pooled burden and count ---------------------------------------------

def fig2_pooled_and_count():
    pooled = table("pooled_burden")
    pooled = pooled[pooled["income_group"] == "All countries"].set_index("year")
    hb = table("high_burden_counts").set_index("year")
    k = numbers()
    fig, (a1, a2) = style.figure(
        WIDTH, 4.8,
        "Total net interest grew faster than total revenue after 2021",
        f"All {k['sample']['countries']} sample countries",
        SOURCE, note=FORECAST_NOTE + ". Dollar values at market exchange rates",
        ncols=2, wspace=0.35, header_extra=0.42)
    style.panel_title(a1, "Total net interest, % of total revenue",
                      "Equal to a revenue-weighted average of countries")
    a1.axvspan(E, F + 0.5, color=FORECAST_SHADE, zorder=0, lw=0)
    _line_with_forecast(a1, pooled["pooled_burden"], RED)
    for y in (S, B, E):
        v = pooled.loc[y, "pooled_burden"]
        a1.plot(y, v, "o", color=RED, ms=5, zorder=5)
        _annotate(a1, y, v, f"{v:.1f}", dx=0, dy=-11, ha="center")
    style.value_axis(a1, [0, 2, 4, 6, 8], unit="%", zero=0)
    a1.set_xlim(S - 0.5, F + 0.5)
    style.year_axis(a1, [2015, 2018, 2021, 2024, 2027])

    style.panel_title(a2, f"Net burden above {config.HIGH_BURDEN_THRESHOLD:.0f}% of revenue",
                      "Number of countries")
    years = list(range(S, X + 1))
    a2.bar(years, hb.loc[years, "countries_above"], width=0.72, zorder=3,
           color=[DEEP_BLUE if y <= E else NEUTRAL for y in years])
    for y in (S, E, X):
        v = hb.loc[y, "countries_above"]
        a2.text(y, v + 0.4, f"{v:.0f}" + ("*" if y == X else ""), ha="center", va="bottom",
                fontsize=8.5, color=INK if y <= E else TEXT_SOFT)
    style.value_axis(a2, [0, 5, 10, 15, 20, 25], zero=0)
    a2.set_xlim(S - 0.6, X + 0.6)
    style.year_axis(a2, [2015, 2017, 2019, 2021, 2023, 2025])
    return style.save(fig, "fig2_pooled_and_count")


# --- Figure 4: debt vs burden -----------------------------------------------------

LABELS_FIG4 = {  # name: (dx, dy, ha) in points
    "Japan": (0, 9, "center"), "Sudan": (0, 9, "center"), "Lebanon": (6, -7, "left"),
    "Greece": (6, 1, "left"), "Italy": (0, -10, "center"), "United States": (6, 5, "left"),
    "Pakistan": (6, 0, "left"), "Egypt, Arab Rep.": (-6, 0, "right"), "Sri Lanka": (6, 0, "left"),
    "Bahrain": (6, 0, "left"), "Malawi": (6, 0, "left"), "Bangladesh": (-6, 0, "right"),
    "Nigeria": (-6, 0, "right"), "Kenya": (6, 0, "left"), "Costa Rica": (-6, 0, "right"),
    "India": (6, 3, "left"), "Brazil": (6, -3, "left"), "China": (-6, -20, "right", True),
    "Zambia": (6, 0, "left"), "Norway": (-6, 0, "right"), "Canada": (0, -10, "center"),
}


def fig4_debt_vs_burden():
    q = table("debt_burden_quadrants")
    corr = numbers()["correlation"]["All countries"]
    fig, ax = style.figure(
        WIDTH, 5.9,
        "Debt ratios and interest burdens often rank countries differently",
        f"{E}. Vertical: net interest, % of revenue. Horizontal: gross debt, % of GDP. Each dot is a country",
        SOURCE, key=True, footer_extra=0.2,
        note=(f"Dashed lines show the sample medians. Spearman rank correlation {corr['spearman']:.2f} "
              f"(95% bootstrap interval {corr['ci_low']:.2f} to {corr['ci_high']:.2f})\n"
              "Kuwait (net interest of −33% of revenue: it received more interest than it paid) is not shown"))
    style.header_key(fig, [(INCOME_SHORT[g], INCOME_COLOURS[g], "dot") for g in GROUPS])
    shown = q[q["interest_burden"] > -12]
    for g in GROUPS[::-1]:
        d = shown[shown["income_group"] == g]
        ax.scatter(d["debt_gdp"], d["interest_burden"], s=30, color=INCOME_COLOURS[g],
                   edgecolor="white", linewidth=0.5, zorder=4)
    md, mb = q["median_debt"].iloc[0], q["median_burden"].iloc[0]
    ax.axvline(md, color=TEXT_SOFT, lw=0.9, ls=(0, (3, 2)), zorder=2)
    ax.axhline(mb, color=TEXT_SOFT, lw=0.9, ls=(0, (3, 2)), zorder=2)
    corner = dict(fontsize=8.5, color=TEXT_SOFT, style="italic", linespacing=1.2)
    ax.text(md - 3, 79, "Debt below median,\nburden above", va="top", ha="right", **corner)
    ax.text(md + 3, 79, "Debt and burden\nabove median", va="top", ha="left", **corner)
    ax.text(298, -1.5, "Debt above median,\nburden below", va="top", ha="right", **corner)
    _label_points(ax, shown, "debt_gdp", "interest_burden", LABELS_FIG4)
    style.value_axis(ax, [-10, 0, 10, 20, 30, 40, 50, 60, 70, 80], unit="%", zero=0)
    ax.set_xlim(0, 300)
    ax.set_xticks(range(0, 301, 50))
    ax.tick_params(axis="x", direction="out", length=4)
    style.x_title(ax, "Gross debt, % of GDP")
    return style.save(fig, "fig4_debt_vs_burden")


# --- Figure 5: sample vs measure ------------------------------------------------------

def fig5_sample_vs_measure():
    m = table("matched_sample_comparison")
    fig, axes = style.figure(
        WIDTH, 5.0,
        "Both the sample and the measure change the median burden",
        f"Median interest burden in {E}, % of revenue. Right: change in the median, percentage points",
        f"Sources: IMF {FM}; IMF Public Finances in Modern History ({FPP.split('(')[-1].rstrip(')')}); "
        "World Bank WDI",
        note="Each comparison changes one thing at a time: first the countries, then the measure on the "
             "same countries.\nDifferences between medians are descriptive, not a causal split",
        nrows=2, hspace=0.75, axes_left=2.6, axes_right=1.75, header_extra=0.3)
    colours = {1: NEUTRAL, 2: LIGHT_BLUE, 3: DEEP_BLUE}
    for ax, key, title in [(axes[0], "fpp", "Gross interest from the IMF FPP database"),
                           (axes[1], "wb", "Central-government gross interest from the World Bank")]:
        d = m[m["comparison"] == key].set_index("step")
        n = int(d.loc[3, "countries_level"])
        labels = {1: f"Net burden, all {int(d.loc[1, 'countries_level'])} countries",
                  2: f"Net burden, the same {n} countries", 3: f"Gross burden, the same {n} countries"}
        ypos = {1: 2, 2: 1, 3: 0}
        for step in (1, 2, 3):
            v = d.loc[step, "median_burden_end"]
            ax.barh(ypos[step], v, color=colours[step], height=0.62, zorder=3)
            ax.text(v + 0.12, ypos[step], f"{v:.1f}", va="center", fontsize=9)
            ax.text(-0.15, ypos[step], labels[step], va="center", ha="right", fontsize=9)
        sample_gap = d.loc[2, "median_burden_end"] - d.loc[1, "median_burden_end"]
        measure_gap = d.loc[3, "median_burden_end"] - d.loc[2, "median_burden_end"]
        right = blended_transform_factory(ax.transAxes, ax.transData)
        for y, text in [(1.5, f"Countries: {sample_gap:+.1f}"), (0.5, f"Measure: {measure_gap:+.1f}")]:
            ax.text(1.06, y, text.replace("-", "−"), transform=right, va="center", ha="left",
                    fontsize=9, color=TEXT_SOFT)
        style.panel_title(ax, title, top=10)
        ax.set_xlim(0, 8.5)
        ax.set_ylim(-0.5, 2.5)
        ax.set_yticks([])
        ax.set_xticks([0, 2, 4, 6, 8])
        ax.set_xticklabels(["0", "2", "4", "6", "8%"])
        ax.tick_params(axis="x", length=0, labelsize=8.5)
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        for s in ("top", "right", "bottom"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_linewidth(1.0)
    return style.save(fig, "fig5_sample_vs_measure")


# --- Figure 6: country cases ------------------------------------------------------------

def fig6_country_cases():
    panel = pd.read_csv(config.PANEL_CSV)
    cases = table("case_studies").sort_values("plot_order")
    med = table("group_medians")
    med = med[(med["variable"] == "interest_burden") & (med["income_group"] == "All countries")]
    med = med.set_index("year")["median"].loc[S:F]
    groups = {g: list(d["iso3"]) for g, d in cases.groupby("group", sort=False)}
    big, top = groups["Large economies"], groups["Highest burdens"]
    ncols = 4
    nrows = -(-len(big) // ncols) + -(-len(top) // ncols)
    fig, axes = style.figure(
        WIDTH, 2.1 + 1.85 * nrows,
        "Net burdens moved in different directions in the largest economies",
        f"Net interest, % of revenue, {S}-{F}. Figures show {S} → {E}",
        SOURCE, key=True, nrows=nrows, ncols=ncols, wspace=0.35, hspace=1.15,
        header_extra=0.45, axes_left=0.6,
        note="Large economies: the largest economy in each World Bank region. The two groups use different "
             "vertical scales\n" + FORECAST_NOTE)
    style.header_key(fig, [("Country", DEEP_BLUE, "line"), ("Estimate/projection*", DEEP_BLUE, "dash"),
                           ("Median of all sample countries", NEUTRAL, "line")])
    big_rows = -(-len(big) // ncols)
    layout = [(iso, r * ncols + c, [-20, 0, 20, 40])
              for i, iso in enumerate(big) for r, c in [divmod(i, ncols)]]
    layout += [(iso, (big_rows + r) * ncols + c, [0, 25, 50, 75, 100])
               for i, iso in enumerate(top) for r, c in [divmod(i, ncols)]]
    used = {pos for _, pos, _ in layout}
    for i, ax in enumerate(axes):
        if i not in used:
            ax.set_visible(False)
    for iso, pos, ticks in layout:
        ax = axes[pos]
        d = panel[(panel["iso3"] == iso) & panel["year"].between(S, F)].set_index("year")
        ax.axvspan(E, F + 0.5, color=FORECAST_SHADE, zorder=0, lw=0)
        ax.plot(med.index, med.values, color=NEUTRAL, lw=1.3, zorder=3)
        _line_with_forecast(ax, d["interest_burden"], DEEP_BLUE, lw=1.9)
        style.value_axis(ax, ticks, unit="%", zero=0, size=8)
        ax.set_xlim(S - 0.5, F + 0.5)
        style.year_axis(ax, [2015, 2020, 2025])
        ax.tick_params(axis="x", labelsize=8.5)
        start, end = d.loc[S, "interest_burden"], d.loc[E, "interest_burden"]
        ax.annotate(short(d["name"].iloc[0]), (0, 1), xycoords="axes fraction", xytext=(0, 17),
                    textcoords="offset points", fontsize=10, fontweight="bold", va="bottom")
        ax.annotate(f"{start:.1f} → {end:.1f}".replace("-", "−"), (0, 1),
                    xycoords="axes fraction", xytext=(0, 5), textcoords="offset points",
                    fontsize=8.5, color=TEXT_SOFT, va="bottom")
    first_top = axes[big_rows * ncols]
    for ax_, text in [(axes[0], "Large economies (scale −20% to 40%)"),
                      (first_top, f"Highest burdens in {E} (scale 0% to 100%)")]:
        ax_.annotate(text, (0, 1), xycoords="axes fraction", xytext=(-30, 36), textcoords="offset points",
                     fontsize=9.5, color=RED, fontweight="bold", va="bottom")
    return style.save(fig, "fig6_country_cases")


# --- Appendix A1: three-factor decomposition ---------------------------------------------

def figA1_decomposition():
    d = table("decomposition_three_factor_by_group")
    k = numbers()
    periods = [f"{S}-{B}", f"{B}-{E}"]
    groups = ["All countries"] + GROUPS
    parts = [("mean_nid_effect", "Net interest ÷ debt factor", RED),
             ("mean_debt_effect", "Debt ratio", DEEP_BLUE),
             ("mean_revenue_effect", "Revenue ratio", LIGHT_BLUE)]
    n1 = int(k["decomposition_three"]["All countries"][periods[0]]["countries"])
    n2 = int(k["decomposition_three"]["All countries"][periods[1]]["countries"])
    fig, axes = style.figure(
        WIDTH, 4.9,
        "After 2021, the net-interest-to-debt factor added the most",
        "Accounting contributions to the change in the net burden, percentage points, average country",
        f"Source: IMF {FM}; project calculations",
        note=(f"Log-mean Divisia split of: burden = (net interest ÷ gross debt) × debt/GDP ÷ revenue/GDP. "
              f"An accounting identity, not a causal estimate\nCountries with positive net interest at both ends: "
              f"{n1} ({periods[0].replace('-', '–')}), {n2} ({periods[1].replace('-', '–')})\n"
              "A negative revenue effect means that revenue rose as a share of GDP"),
        key=True, ncols=2, axes_left=1.65, axes_right=0.3, wspace=0.12, header_extra=0.3)
    style.header_key(fig, [(lab, c, "square") for _, lab, c in parts] + [("Total change", INK, "diamond")])
    ypos = np.arange(len(groups))[::-1]
    for ax, period in zip(axes, periods):
        sub = d[d["period"] == period].set_index("income_group").loc[groups]
        pos, neg = np.zeros(len(groups)), np.zeros(len(groups))
        for col, _, colour in parts:
            v = sub[col].values
            ax.barh(ypos, v, left=np.where(v >= 0, pos, neg), color=colour, height=0.62, zorder=3)
            pos += np.where(v >= 0, v, 0)
            neg += np.where(v < 0, v, 0)
        ax.plot(sub["mean_change"], ypos, "D", color=INK, ms=5.5, zorder=5, markeredgecolor="white", mew=0.6)
        for y, v in zip(ypos, sub["mean_change"]):
            ax.text(5.15, y, f"{v:+.1f}".replace("-", "−"), va="center", ha="right", fontsize=8.5)
        ax.set_xlim(-2.6, 5.2)
        ax.set_xticks(range(-2, 5))
        ax.set_xticklabels([str(t).replace("-", "−") for t in range(-2, 5)])
        ax.xaxis.tick_top()
        ax.tick_params(axis="x", length=0, pad=2)
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        ax.axvline(0, color=INK, lw=1, zorder=4)
        ax.set_yticks([])
        ax.set_ylim(-0.6, len(groups) - 0.4)
        for s in ("top", "right", "bottom", "left"):
            ax.spines[s].set_visible(False)
        style.panel_title(ax, period.replace("-", "–"), top=20)
    trans = blended_transform_factory(axes[0].transAxes, axes[0].transData)
    for y, g in zip(ypos, groups):
        axes[0].text(-0.03, y, INCOME_SHORT.get(g, g), transform=trans, ha="right", va="center",
                     fontsize=9.5, fontweight="bold" if g == "All countries" else "normal")
    return style.save(fig, "figA1_decomposition")


# --- Appendix A2: interest vs health -----------------------------------------------------

LABELS_FIGA2 = {
    "India": (19, 0, "left"), "Pakistan": (-10, 0, "right"), "Egypt, Arab Rep.": (8, 0, "left"),
    "Nigeria": (0, 12, "center"), "Bangladesh": (0, -14, "center"), "Indonesia": (15, -9, "left"),
    "Brazil": (9, 0, "left"), "Mexico": (8, 0, "left"), "United States": (-13, 0, "right"),
    "China": (0, 0, "center"), "Sri Lanka": (6, 0, "left"), "Kenya": (6, 0, "left"),
    "Japan": (-9, 0, "right"), "Germany": (8, 3, "left"),
}


def figA2_interest_vs_health():
    s = table("interest_vs_social_spending").dropna(subset=["health_gdp"])
    k = numbers()["social_spending"]
    s = s[s["interest_gdp_health_year"] >= 0]
    fig, ax = style.figure(
        WIDTH, 5.6,
        f"In {k['countries_interest_gt_health']} countries, net interest exceeded health spending",
        f"% of GDP, both values for the same year ({k['health_years_main']} for "
        f"{k['health_years_main_count']} of {k['countries_health']} countries). Circle area = population",
        "Sources: IMF Fiscal Monitor; World Health Organization via World Bank WDI",
        key=True, footer_extra=0.2,
        note=("Net interest (Fiscal Monitor) against domestic general-government health spending. "
              "Countries with negative net interest are not shown\n"
              f"Countries above the line had {k['population_interest_gt_health_bn']:.1f}bn people in "
              f"{k['population_year']}\nDescriptive comparison: it does not show that interest caused lower health spending"),
    )
    style.header_key(fig, [("Interest above health spending", RED, "dot"),
                           ("Interest below health spending", LIGHT_BLUE, "dot")])
    above = s["interest_exceeds_health"] == 1
    size = 6 + s["population"] / 1e6 * 0.55
    for mask, colour, z in [(~above, LIGHT_BLUE, 3), (above, RED, 4)]:
        ax.scatter(s.loc[mask, "health_gdp"], s.loc[mask, "interest_gdp_health_year"], s=size[mask],
                   color=colour, alpha=0.8, edgecolor="white", linewidth=0.5, zorder=z)
    ax.plot([0, 10], [0, 10], color=TEXT_SOFT, lw=0.9, ls=(0, (3, 2)), zorder=2)
    ax.text(7.6, 8.9, "Interest = health spending", fontsize=8.5, color=TEXT_SOFT, style="italic", ha="right")
    _label_points(ax, s, "health_gdp", "interest_gdp_health_year", LABELS_FIGA2)
    style.value_axis(ax, [0, 2, 4, 6, 8, 10], unit="%", zero=0)
    ax.set_xlim(0, 11)
    ax.set_xticks(range(0, 12))
    ax.tick_params(axis="x", direction="out", length=4)
    ax.text(0.01, 0.985, "Net interest", transform=ax.transAxes, fontsize=9, va="top", color=TEXT_SOFT)
    style.x_title(ax, "Government health spending, % of GDP")
    return style.save(fig, "figA2_interest_vs_health")


# --- Appendix A3: net vs gross -------------------------------------------------------------

LABELS_FIGA3 = {
    "Canada": (-6, 0, "right"), "Norway": (0, 9, "center"), "Brazil": (-6, 3, "right"),
    "Honduras": (-5, 8, "right"), "Myanmar": (-6, 3, "right"), "United States": (12, -16, "left", True),
    "Pakistan": (-6, 0, "right"),
}


def figA3_net_vs_gross():
    m = table("measure_comparison")
    m = m[(m["year"] == E)].dropna(subset=["gross_fpp"])
    agree = numbers()["measure_agreement"]["gross_fpp"]
    shown = m[m["net_fiscal_monitor"] > -12]
    fig, ax = style.figure(
        WIDTH, 5.3,
        "Net and gross burdens are close for most countries",
        f"% of revenue, {E}. Vertical: gross interest (IMF FPP). Horizontal: net interest (Fiscal Monitor)",
        f"Sources: IMF {FM}; IMF Public Finances in Modern History ({FPP.split('(')[-1].rstrip(')')})",
        key=True, footer_extra=0.2,
        note=(f"{agree['countries']} countries with both measures. Spearman rank correlation {agree['spearman']:.2f}; "
              f"{agree['within_2_points'] * 100:.0f}% of countries within 2 points\n"
              "The sources differ in vintage, revenue figures and coverage, so a gap is not a direct measure "
              "of interest income\nKuwait (net −33, gross 0.1) is not shown"))
    style.header_key(fig, [(INCOME_SHORT[g], INCOME_COLOURS[g], "dot") for g in GROUPS])
    ax.plot([-10, 65], [-10, 65], color=TEXT_SOFT, lw=0.9, ls=(0, (3, 2)), zorder=2)
    ax.text(48, 53, "Net = gross", fontsize=8.5, color=TEXT_SOFT, style="italic", ha="right")
    for g in GROUPS[::-1]:
        d = shown[shown["income_group"] == g]
        ax.scatter(d["net_fiscal_monitor"], d["gross_fpp"], s=26,
                   color=INCOME_COLOURS[g], edgecolor="white", linewidth=0.5, zorder=4)
    _label_points(ax, shown, "net_fiscal_monitor", "gross_fpp", LABELS_FIGA3)
    style.value_axis(ax, [0, 10, 20, 30, 40, 50, 60, 70], unit="%", zero=0, ylim=(-2, 70))
    ax.set_xlim(-10, 65)
    ax.set_xticks(range(-10, 61, 10))
    ax.set_xticklabels([str(t).replace("-", "−") for t in range(-10, 61, 10)])
    ax.tick_params(axis="x", direction="out", length=4)
    style.x_title(ax, "Net interest, % of revenue")
    return style.save(fig, "figA3_net_vs_gross")


ALL = [fig1_income_group_trend, fig2_pooled_and_count, fig3_highest_burdens, fig4_debt_vs_burden,
       fig5_sample_vs_measure, fig6_country_cases, figA1_decomposition, figA2_interest_vs_health,
       figA3_net_vs_gross]


def run():
    style.setup()
    return [f() for f in ALL]
