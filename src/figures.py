"""Produce every figure in the report from the output tables.

Each function draws one chart that answers one question; the figure number
matches the report. Label offsets for named countries are set by hand
because they depend on the frozen data snapshot, but everything plotted comes
from outputs/tables/ or outputs/key_numbers.json.
"""

import json

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory

import config
import style
from style import (BLUE1, BLUE2, FORECAST_SHADE, GREY, GRID, INCOME_COLOURS, INCOME_SHORT,
                   LABEL_COLOURS, MUTED, PALE_BLUE, RED, TEXT, TEXT_SOFT)

S, B, E, X, F = (config.START_YEAR, config.BREAK_YEAR, config.END_YEAR,
                 config.ESTIMATE_YEAR, config.FORECAST_END)
GROUPS = config.INCOME_ORDER
SOURCE = "Sources: IMF Fiscal Monitor (October 2026); World Bank"
FORECAST_NOTE = f"*{X} estimate; {X + 1}-{F % 100} IMF forecasts"
DASH = (0, (2, 1.5))
WIDTH = 7.2


def table(name):
    return pd.read_csv(config.TABLES / f"{name}.csv")


def numbers():
    return json.loads((config.ROOT / "outputs" / "key_numbers.json").read_text(encoding="utf-8"))


def short(name):
    return name.replace(", Arab Rep.", "").replace(" SAR, China", "")


def _line_with_forecast(ax, series, colour, lw=2.2, zorder=4):
    hist, fut = series.loc[:E], series.loc[E:]
    ax.plot(hist.index, hist.values, color=colour, lw=lw, solid_capstyle="round", zorder=zorder)
    ax.plot(fut.index, fut.values, color=colour, lw=lw, ls=DASH, zorder=zorder)


def _annotate(ax, x, y, text, dx=6, dy=0, ha="left", colour=TEXT, size=8.5):
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                fontsize=size, color=colour, zorder=6)


def _label_points(ax, df, x, y, positions):
    for _, r in df[df["name"].isin(positions)].iterrows():
        dx, dy, ha = positions[r["name"]]
        _annotate(ax, r[x], r[y], short(r["name"]), dx=dx, dy=dy, ha=ha)


# --- Figure 2 (median trend) -----------------------------------------------

def fig2_median_trend():
    med = table("group_medians")
    med = med[med["variable"] == "interest_burden"]
    fig, ax = style.figure(
        WIDTH, 4.8,
        "Interest is taking a bigger bite out of poorer countries' revenue",
        "Net interest payments, % of general government revenue, median country by income group",
        SOURCE, note=FORECAST_NOTE, axes_right=1.6)
    ax.axvspan(E, F + 0.9, color=FORECAST_SHADE, zorder=0, lw=0)
    ax.text(E + 0.2, 11.8, "Estimate and\nforecasts*", fontsize=8.5, color=TEXT_SOFT, va="top")
    ends = {}
    for g in GROUPS:
        d = med[med["income_group"] == g].set_index("year")["median"]
        _line_with_forecast(ax, d, INCOME_COLOURS[g])
        ends[g] = d.loc[F]
    style.value_axis(ax, [0, 2, 4, 6, 8, 10, 12], zero=0)
    ax.set_xlim(S - 0.3, F + 0.9)
    style.year_axis(ax, list(range(S, F + 1)))
    trans = blended_transform_factory(ax.transAxes, ax.transData)
    for g, y in zip(GROUPS, style.spread_labels([ends[g] for g in GROUPS], 0.75)):
        ax.text(1.03, y, INCOME_SHORT[g], transform=trans, color=LABEL_COLOURS[g],
                fontsize=9.5, fontweight="medium", va="center")
    return style.save(fig, "fig2_median_burden_by_income")


# --- Figure 3 (aggregate) -------------------------------------------------

def fig3_aggregate_and_count():
    agg = table("aggregate_burden")
    agg = agg[agg["income_group"] == "All countries"].set_index("year")
    hb = table("high_burden_counts").set_index("year")
    k = numbers()
    fig, (a1, a2) = style.figure(
        WIDTH, 4.7,
        "Since 2021 the global interest bill has climbed steeply",
        f"General government, {k['sample']['countries']} countries",
        SOURCE, note=FORECAST_NOTE + ". Totals converted to US dollars at market exchange rates",
        ncols=2, wspace=0.3, header_extra=0.42)

    style.panel_title(a1, "Total net interest, % of total revenue", "Countries weighted by GDP")
    a1.axvspan(E, F + 0.5, color=FORECAST_SHADE, zorder=0, lw=0)
    _line_with_forecast(a1, agg["interest_burden"], BLUE1)
    for y in (S, B, E):
        v = agg.loc[y, "interest_burden"]
        a1.plot(y, v, "o", color=BLUE1, ms=5, zorder=5)
        _annotate(a1, y, v, f"{v:.1f}", dx=0, dy=-11, ha="center")
    style.value_axis(a1, [0, 2, 4, 6, 8], zero=0)
    a1.set_xlim(S - 0.5, F + 0.5)
    style.year_axis(a1, [2015, 2018, 2021, 2024, 2027])

    style.panel_title(a2, f"Burdens above {config.HIGH_BURDEN_THRESHOLD:.0f}% of revenue",
                      "Number of countries")
    years = list(range(S, X + 1))
    a2.bar(years, hb.loc[years, "countries_above"], width=0.72, zorder=3,
           color=[BLUE2 if y <= E else MUTED for y in years])
    for y in (S, E, X):
        v = hb.loc[y, "countries_above"]
        a2.text(y, v + 0.4, f"{v:.0f}" + ("*" if y == X else ""), ha="center", va="bottom",
                fontsize=8.5, color=TEXT if y <= E else TEXT_SOFT)
    style.value_axis(a2, [0, 5, 10, 15, 20, 25], zero=0)
    a2.set_xlim(S - 0.6, X + 0.6)
    style.year_axis(a2, [2015, 2017, 2019, 2021, 2023, 2025])
    return style.save(fig, "fig3_global_burden_and_count")


# --- Figure 1 (highest burdens) --------------------------------------------

def fig1_top_burdens():
    rank = table("burden_ranking").head(20)
    change = table("burden_change").set_index("iso3")
    n = len(rank)
    h = 2.0 + n * 0.235
    fig, ax = style.figure(
        WIDTH, h,
        "Pakistan, Egypt and Sri Lanka spend more than half their revenue on interest",
        f"Net interest payments, % of general government revenue, {E}, highest 20",
        SOURCE, key=True, axes_left=1.75, axes_right=0.45, footer_extra=-0.25)
    style.header_key(fig, [(INCOME_SHORT[g], INCOME_COLOURS[g], "square") for g in GROUPS]
                     + [(str(S), TEXT, "dot")])
    ypos = np.arange(n)[::-1]
    ax.barh(ypos, rank["interest_burden"], color=[INCOME_COLOURS[g] for g in rank["income_group"]],
            height=0.68, zorder=3)
    ax.plot(change.loc[rank["iso3"], "burden_start"].values, ypos, "o", color=TEXT, ms=3.8, zorder=4)
    names = blended_transform_factory(ax.transAxes, ax.transData)
    for y, v, name in zip(ypos, rank["interest_burden"], rank["name"]):
        ax.text(v + 0.8, y, f"{v:.1f}", va="center", fontsize=8.5)
        ax.text(-0.02, y, short(name), transform=names, ha="right", va="center", fontsize=9.5)
    ax.set_yticks([])
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks(range(0, 71, 10))
    ax.set_xlim(0, 70)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=3)
    ax.grid(axis="x", color=GRID, lw=0.75, zorder=0)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_linewidth(1.0)
    return style.save(fig, "fig1_highest_burdens")


# --- Figure 4 ---------------------------------------------------------------

LABELS_FIG4 = {  # name: (dx, dy, ha) in points
    "Japan": (0, 9, "center"), "Sudan": (0, 9, "center"), "Lebanon": (6, -7, "left"),
    "Greece": (6, 1, "left"), "Italy": (0, -10, "center"), "United States": (6, 5, "left"),
    "Pakistan": (6, 0, "left"), "Egypt, Arab Rep.": (-6, 0, "right"), "Sri Lanka": (6, 0, "left"),
    "Bahrain": (6, 0, "left"), "Malawi": (6, 0, "left"), "Bangladesh": (-6, 0, "right"),
    "Nigeria": (-6, 0, "right"), "Kenya": (6, 0, "left"), "Costa Rica": (-6, 0, "right"),
    "India": (6, 3, "left"), "Brazil": (6, -3, "left"), "China": (0, -10, "center"),
    "Zambia": (6, 0, "left"), "Norway": (-6, 0, "right"),
}


def fig4_debt_vs_burden():
    q = table("debt_burden_quadrants")
    corr = numbers()["correlation"]["All countries"]
    fig, ax = style.figure(
        WIDTH, 5.7,
        "More debt does not always mean a heavier interest bill",
        f"General government, {E}: net interest, % of revenue (vertical) against gross debt, % of GDP",
        SOURCE, key=True, axes_right=0.45, footer_extra=0.2,
        note=(f"Dashed lines show sample medians. Spearman rank correlation {corr['spearman']:.2f} "
              f"(95% bootstrap interval {corr['ci_low']:.2f} to {corr['ci_high']:.2f})\n"
              "Kuwait, a net creditor whose net interest income equals 33% of its revenue, is not shown"))
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
    ax.text(md - 3, 79, "Low debt,\nhigh burden", va="top", ha="right", **corner)
    ax.text(md + 3, 79, "High debt,\nhigh burden", va="top", ha="left", **corner)
    ax.text(268, -1.5, "High debt,\nlow burden", va="top", ha="right", **corner)
    _label_points(ax, shown, "debt_gdp", "interest_burden", LABELS_FIG4)
    style.value_axis(ax, [-10, 0, 10, 20, 30, 40, 50, 60, 70, 80], zero=0)
    ax.set_xlim(0, 300)
    ax.set_xticks(range(0, 301, 50))
    ax.tick_params(axis="x", direction="out", length=4)
    style.x_title(ax, "Gross debt, % of GDP")
    return style.save(fig, "fig4_debt_vs_burden")


# --- Figure 5 ---------------------------------------------------------------

def fig5_decomposition():
    d = table("decomposition_by_group")
    periods = [f"{S}-{B}", f"{B}-{E}"]
    groups = ["All countries"] + GROUPS
    parts = [("mean_rate_effect", "Interest rate", RED),
             ("mean_debt_effect", "Debt ratio", BLUE1),
             ("mean_revenue_effect", "Revenue ratio", BLUE2)]
    fig, axes = style.figure(
        WIDTH, 4.7,
        "Since 2021, higher interest rates have done the damage",
        "Contributions to the change in net interest as % of revenue, percentage points, average country",
        "Sources: IMF Fiscal Monitor (October 2026); World Bank; author's calculations",
        note=("Log-mean Divisia decomposition of: burden = implicit interest rate × debt/GDP ÷ revenue/GDP\n"
              "A negative revenue effect means that revenue rose as a share of GDP"),
        key=True, ncols=2, axes_left=1.65, axes_right=0.3, wspace=0.12, header_extra=0.3)
    style.header_key(fig, [(lab, c, "square") for _, lab, c in parts] + [("Total change", TEXT, "diamond")])
    ypos = np.arange(len(groups))[::-1]
    for ax, period in zip(axes, periods):
        sub = d[d["period"] == period].set_index("income_group").loc[groups]
        pos, neg = np.zeros(len(groups)), np.zeros(len(groups))
        for col, _, colour in parts:
            v = sub[col].values
            ax.barh(ypos, v, left=np.where(v >= 0, pos, neg), color=colour, height=0.62, zorder=3)
            pos += np.where(v >= 0, v, 0)
            neg += np.where(v < 0, v, 0)
        ax.plot(sub["mean_change"], ypos, "D", color=TEXT, ms=5.5, zorder=5, markeredgecolor="white", mew=0.6)
        for y, v in zip(ypos, sub["mean_change"]):
            ax.text(5.15, y, f"{v:+.1f}", va="center", ha="right", fontsize=8.5)
        ax.set_xlim(-2.6, 5.2)
        ax.set_xticks(range(-2, 5))
        ax.set_xticklabels([str(t).replace("-", "−") for t in range(-2, 5)])
        ax.xaxis.tick_top()
        ax.tick_params(axis="x", length=0, pad=2)
        ax.grid(axis="x", color=GRID, lw=0.75, zorder=0)
        ax.axvline(0, color=TEXT, lw=1, zorder=4)
        ax.set_yticks([])
        ax.set_ylim(-0.6, len(groups) - 0.4)
        for s in ("top", "right", "bottom", "left"):
            ax.spines[s].set_visible(False)
        ax.add_artist(Line2D([0, 1], [1, 1], transform=ax.transAxes + style.offset(ax, 34),
                             color=TEXT, lw=0.8, clip_on=False))
        ax.annotate(period.replace("-", "–"), (0, 1), xycoords="axes fraction", xytext=(0, 31),
                    textcoords="offset points", fontsize=10.5, fontweight="bold", va="top")
    trans = blended_transform_factory(axes[0].transAxes, axes[0].transData)
    for y, g in zip(ypos, groups):
        axes[0].text(-0.03, y, INCOME_SHORT.get(g, g), transform=trans, ha="right", va="center",
                     fontsize=9.5, fontweight="bold" if g == "All countries" else "normal")
    return style.save(fig, "fig5_decomposition")


# --- Figure 6 ---------------------------------------------------------------

def fig6_case_studies():
    panel = pd.read_csv(config.PANEL_CSV)
    cases = table("case_studies")
    med = table("group_medians")
    med = med[(med["variable"] == "interest_burden") & (med["income_group"] == "All countries")]
    med = med.set_index("year")["median"].loc[S:F]
    order = ["USA", "CHN", "DEU", "IND", "BRA", "ZAF", "SAU"]
    order += [c for c in cases["iso3"] if c not in order]
    fig, axes = style.figure(
        WIDTH, 6.2,
        "Large economies have diverged; crisis-hit ones carry the heaviest load",
        f"Net interest payments, % of general government revenue. Figures show {S} → {E}",
        SOURCE, key=True, nrows=2, ncols=5, wspace=0.28, hspace=0.55, axes_right=0.35,
        header_extra=0.32,
        note=f"Largest economy in each World Bank region, plus the three highest burdens in {E}\n" + FORECAST_NOTE)
    style.header_key(fig, [("Country", BLUE1, "line"), ("Estimate/forecast*", BLUE1, "dash"),
                           ("Median of all sample countries", GREY, "line")])
    for ax, iso in zip(axes, order):
        d = panel[(panel["iso3"] == iso) & panel["year"].between(S, F)].set_index("year")
        ax.axvspan(E, F + 0.5, color=FORECAST_SHADE, zorder=0, lw=0)
        ax.plot(med.index, med.values, color=GREY, lw=1.2, zorder=3)
        _line_with_forecast(ax, d["interest_burden"], BLUE1, lw=1.9)
        style.value_axis(ax, [-25, 0, 25, 50, 75, 100], zero=0, size=8)
        ax.set_xlim(S - 0.5, F + 0.5)
        style.year_axis(ax, [2015, 2020, 2025])
        ax.tick_params(axis="x", labelsize=8.5)
        start, end = d.loc[S, "interest_burden"], d.loc[E, "interest_burden"]
        ax.annotate(short(d["name"].iloc[0]), (0, 1), xycoords="axes fraction", xytext=(0, 16),
                    textcoords="offset points", fontsize=10, fontweight="bold", va="bottom")
        ax.annotate(f"{start:.1f} → {end:.1f}".replace("-", "−"), (0, 1), xycoords="axes fraction", xytext=(0, 4),
                    textcoords="offset points", fontsize=8.5, color=TEXT_SOFT, va="bottom")
    return style.save(fig, "fig6_case_studies")


# --- Figure 7 ---------------------------------------------------------------

LABELS_FIG7 = {
    "India": (19, 0, "left"), "Pakistan": (-10, 0, "right"), "Egypt, Arab Rep.": (8, 0, "left"),
    "Nigeria": (0, 12, "center"), "Bangladesh": (0, -14, "center"), "Indonesia": (0, -14, "center"),
    "Brazil": (9, 0, "left"), "Mexico": (8, 0, "left"), "United States": (-13, 0, "right"),
    "China": (0, -21, "center"), "Sri Lanka": (6, 0, "left"), "Kenya": (6, 0, "left"),
    "Japan": (-9, 0, "right"), "Germany": (8, 3, "left"),
}


def fig7_interest_vs_health():
    s = table("interest_vs_social_spending").dropna(subset=["health_gdp"])
    k = numbers()["social_spending"]
    s = s[s["interest_gdp_health_year"] >= 0]
    fig, ax = style.figure(
        WIDTH, 5.5,
        f"In {k['countries_interest_gt_health']} countries, governments pay more in interest than on health",
        "General government, % of GDP, latest year with data (2023 for most). Circle area = population",
        "Sources: IMF Fiscal Monitor (October 2026); World Health Organization via World Bank",
        key=True, axes_right=0.45, footer_extra=0.2,
        note=("Interest is net interest; health is domestic general-government health spending. "
              "Net creditors (negative net interest) not shown\n"
              f"Countries above the line are home to {k['population_interest_gt_health_bn']:.1f}bn people"))
    style.header_key(fig, [("Interest above health spending", RED, "dot"),
                           ("Interest below health spending", PALE_BLUE, "dot")])
    above = s["interest_exceeds_health"] == 1
    size = 6 + s["population"] / 1e6 * 0.55
    for mask, colour, z in [(~above, PALE_BLUE, 3), (above, RED, 4)]:
        ax.scatter(s.loc[mask, "health_gdp"], s.loc[mask, "interest_gdp_health_year"], s=size[mask],
                   color=colour, alpha=0.8, edgecolor="white", linewidth=0.5, zorder=z)
    ax.plot([0, 10], [0, 10], color=TEXT_SOFT, lw=0.9, ls=(0, (3, 2)), zorder=2)
    ax.text(7.6, 8.9, "Interest = health spending", fontsize=8.5, color=TEXT_SOFT, style="italic", ha="right")
    _label_points(ax, s, "health_gdp", "interest_gdp_health_year", LABELS_FIG7)
    style.value_axis(ax, [0, 2, 4, 6, 8, 10], zero=0)
    ax.set_xlim(0, 11)
    ax.set_xticks(range(0, 12))
    ax.tick_params(axis="x", direction="out", length=4)
    ax.text(0.01, 0.985, "Net interest", transform=ax.transAxes, fontsize=9, va="top", color=TEXT_SOFT)
    style.x_title(ax, "Government health spending")
    return style.save(fig, "fig7_interest_vs_health")


# --- Figure 8 ---------------------------------------------------------------

LABELS_FIG8 = {
    "Canada": (-6, 0, "right"), "Norway": (0, 9, "center"), "Brazil": (-6, 3, "right"),
    "Honduras": (-5, 8, "right"), "Myanmar": (-6, 3, "right"), "United States": (6, -4, "left"),
    "Pakistan": (-6, 0, "right"),
}


def fig8_measure_check():
    m = table("measure_comparison")
    m = m[(m["year"] == E)].dropna(subset=["gross_general_government"])
    agree = numbers()["measure_agreement"]["gross_general_government"]
    shown = m[m["net_general_government"] > -12]
    fig, ax = style.figure(
        WIDTH, 5.2,
        "Net and gross measures agree, except where governments hold large assets",
        f"Interest as % of general government revenue, {E}: gross (vertical) against net (horizontal)",
        "Sources: IMF Fiscal Monitor (October 2026); IMF Public Finances in Modern History (December 2025)",
        key=True, axes_right=0.45, footer_extra=0.2,
        note=(f"{agree['countries']} countries with both measures. Spearman rank correlation {agree['spearman']:.2f}; "
              f"{agree['within_2_points'] * 100:.0f}% of countries within 2 points of each other\n"
              "Kuwait (net −33, gross 0.1) not shown"))
    style.header_key(fig, [(INCOME_SHORT[g], INCOME_COLOURS[g], "dot") for g in GROUPS])
    ax.plot([-10, 65], [-10, 65], color=TEXT_SOFT, lw=0.9, ls=(0, (3, 2)), zorder=2)
    ax.text(48, 53, "Net = gross", fontsize=8.5, color=TEXT_SOFT, style="italic", ha="right")
    for g in GROUPS[::-1]:
        d = shown[shown["income_group"] == g]
        ax.scatter(d["net_general_government"], d["gross_general_government"], s=26,
                   color=INCOME_COLOURS[g], edgecolor="white", linewidth=0.5, zorder=4)
    _label_points(ax, shown, "net_general_government", "gross_general_government", LABELS_FIG8)
    style.value_axis(ax, [0, 10, 20, 30, 40, 50, 60, 70], zero=0, ylim=(-2, 70))
    ax.set_xlim(-10, 65)
    ax.set_xticks(range(-10, 61, 10))
    ax.set_xticklabels([str(t).replace("-", "−") for t in range(-10, 61, 10)])
    ax.tick_params(axis="x", direction="out", length=4)
    style.x_title(ax, "Net interest (baseline measure)")
    return style.save(fig, "fig8_net_vs_gross")


ALL = [fig1_top_burdens, fig2_median_trend, fig3_aggregate_and_count, fig4_debt_vs_burden,
       fig5_decomposition, fig6_case_studies, fig7_interest_vs_health, fig8_measure_check]


def run():
    style.setup()
    return [f() for f in ALL]
