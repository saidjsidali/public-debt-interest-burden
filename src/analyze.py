"""Statistical analysis on top of the SQL tables.

Correlations, regressions with influence checks, the accounting
decompositions, matched-sample comparisons, case-study selection and other
sensitivity checks. Results go to outputs/tables/. The numbers quoted in the
README and the report are collected in outputs/key_numbers.json, and the text
is built from that file rather than typed by hand.
"""

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

import config

SEED = 2026
N_BOOT = 2000
S, B, E, X = config.START_YEAR, config.BREAK_YEAR, config.END_YEAR, config.ESTIMATE_YEAR


def load():
    full = pd.read_csv(config.PANEL_CSV)
    sample = pd.read_csv(config.DATA_PROCESSED / "sample.csv")
    return full[full["iso3"].isin(sample["iso3"])].copy(), sample, full


def year(panel, y):
    return panel[panel["year"] == y].set_index("iso3")


# --- Correlation -------------------------------------------------------------

def bootstrap_spearman(x, y, n_boot=N_BOOT, seed=SEED):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(x), size=(n_boot, len(x)))
    boot = [stats.spearmanr(x[i], y[i]).statistic for i in draws]
    low, high = np.nanpercentile(boot, [2.5, 97.5])
    return stats.spearmanr(x, y).statistic, low, high


def correlations(end):
    groups = [("All countries", end)] + [(g, end[end["income_group"] == g]) for g in config.INCOME_ORDER]
    rows = []
    for name, d in groups:
        rho, low, high = bootstrap_spearman(d["debt_gdp"], d["interest_burden"])
        rows.append({
            "group": name, "countries": len(d), "spearman": rho, "ci_low": low, "ci_high": high,
            "pearson": stats.pearsonr(d["debt_gdp"], d["interest_burden"]).statistic,
        })
    return pd.DataFrame(rows)


# --- Regressions -------------------------------------------------------------

REG_SPECS = {
    "(1) Debt only": "log_burden ~ log_debt",
    "(2) Debt and revenue": "log_burden ~ log_debt + log_revenue",
    "(3) Adding income group": "log_burden ~ log_debt + log_revenue + C(income_group)",
    "(4) Net-interest-to-debt factor": "log_nid ~ log_debt + C(income_group)",
}


def regression_data(end):
    """Logs need positive values, so only countries with positive net interest enter."""
    d = end[end["net_interest_gdp"] > 0].copy()
    d["log_burden"] = np.log(d["interest_burden"])
    d["log_debt"] = np.log(d["debt_gdp"])
    d["log_revenue"] = np.log(d["revenue_gdp"])
    d["log_nid"] = np.log(d["net_interest_to_debt"])
    d["income_group"] = pd.Categorical(d["income_group"], categories=config.INCOME_ORDER)
    return d


def regressions(end):
    d = regression_data(end)
    rows = []
    for name, formula in REG_SPECS.items():
        fit = smf.ols(formula, data=d).fit(cov_type="HC3")
        ci = fit.conf_int()
        for term in fit.params.index:
            rows.append({
                "model": name, "term": term, "coef": fit.params[term], "se": fit.bse[term],
                "ci_low": ci.loc[term, 0], "ci_high": ci.loc[term, 1], "p_value": fit.pvalues[term],
                "r_squared": fit.rsquared, "countries": int(fit.nobs),
            })
    return pd.DataFrame(rows)


def regression_influence(end):
    """Cook's distance and leverage for models 1 and 2, plus fit when each country is left out."""
    d = regression_data(end).reset_index()
    infl_rows, loo_rows = [], []
    for name in ["(1) Debt only", "(2) Debt and revenue"]:
        fit = smf.ols(REG_SPECS[name], data=d).fit()
        infl = fit.get_influence()
        cooks = infl.cooks_distance[0]
        for i, r in d.iterrows():
            refit = smf.ols(REG_SPECS[name], data=d.drop(index=i)).fit()
            infl_rows.append({
                "model": name, "iso3": r["iso3"], "name": r["name"], "net_burden": r["interest_burden"],
                "cooks_distance": cooks[i], "leverage": infl.hat_matrix_diag[i],
                "r_squared_without_country": refit.rsquared,
            })
        loo_rows.append({"model": name, "r_squared_all": fit.rsquared})
    table = pd.DataFrame(infl_rows).sort_values(["model", "cooks_distance"], ascending=[True, False])
    return table, pd.DataFrame(loo_rows)


def regression_levels(end):
    """Levels model on all sample countries, including zero and negative net burdens."""
    d = end.reset_index()
    fit = smf.ols("interest_burden ~ debt_gdp + revenue_gdp", data=d).fit(cov_type="HC3")
    ci = fit.conf_int()
    return pd.DataFrame([{
        "term": t, "coef": fit.params[t], "ci_low": ci.loc[t, 0], "ci_high": ci.loc[t, 1],
        "r_squared": fit.rsquared, "countries": int(fit.nobs),
    } for t in fit.params.index])


# --- Decomposition -----------------------------------------------------------

def lmdi(start, end, factors, scale=1.0):
    """Exact log-mean Divisia split of a change in a product of factors.

    start, end: dicts {factor: value} (scalars or aligned arrays), all positive.
    factors: {effect_name: (factor_name, exponent)}; the burden equals
    scale x the product of factor ** exponent. Returns {effect_name:
    contribution}; the contributions add up exactly to the change in the burden.
    """
    b0 = scale * np.prod([np.asarray(start[f], float) ** p for f, p in factors.values()], axis=0)
    b1 = scale * np.prod([np.asarray(end[f], float) ** p for f, p in factors.values()], axis=0)
    same = np.isclose(b0, b1, rtol=1e-12, atol=0)
    weight = np.where(same, b0, (b1 - b0) / np.where(same, 1.0, np.log(b1 / np.where(same, 1.0, b0))))
    return {name: weight * p * np.log(np.asarray(end[f], float) / np.asarray(start[f], float))
            for name, (f, p) in factors.items()}


# burden (%) = 100 x net interest/GDP / revenue/GDP
TWO_FACTOR = {"net_interest_gdp_effect": ("net_interest_gdp", 1), "revenue_effect": ("revenue_gdp", -1)}
# burden (%) = (net interest / debt, %) x debt/GDP / revenue/GDP
THREE_FACTOR = {"nid_effect": ("net_interest_to_debt", 1), "debt_effect": ("debt_gdp", 1),
                "revenue_effect": ("revenue_gdp", -1)}
SCALES = {"two_factor": 100.0, "three_factor": 1.0}
PERIODS = [(S, B), (B, E), (S, E)]


def decompose(panel, y0, y1, factors, scale):
    cols = sorted({f for f, _ in factors.values()} | {"interest_burden"})
    a, b = year(panel, y0)[cols], year(panel, y1)[cols]
    d = a.join(b, lsuffix="_0", rsuffix="_1").dropna()
    d = d[(d["interest_burden_0"] > 0) & (d["interest_burden_1"] > 0)]
    effects = lmdi({f: d[f"{f}_0"] for f in cols}, {f: d[f"{f}_1"] for f in cols}, factors, scale)
    out = pd.DataFrame({"period": f"{y0}-{y1}", "burden_start": d["interest_burden_0"],
                        "burden_end": d["interest_burden_1"]})
    out["change"] = out["burden_end"] - out["burden_start"]
    for k, v in effects.items():
        out[k] = v
    gap = out["change"] - out[list(factors)].sum(axis=1)
    assert gap.abs().max() < 1e-9, "LMDI contributions do not add up"
    return out


def summarise(by_country, factors, sample):
    by_country = by_country.merge(sample[["iso3", "income_group"]], on="iso3")
    effects = ["change"] + list(factors)
    rows = []
    for grp, d in [("All countries", by_country)] + list(by_country.groupby("income_group")):
        for period, g in d.groupby("period"):
            row = {"income_group": grp, "period": period, "countries": len(g)}
            row.update({f"mean_{e}": g[e].mean() for e in effects})
            row.update({f"median_{e}": g[e].median() for e in effects})
            rows.append(row)
    return pd.DataFrame(rows)


def dominance(by_country, effect="nid_effect", others=("debt_effect", "revenue_effect")):
    """How often one effect is (a) the largest positive contribution and (b) the largest in absolute size."""
    rows = []
    for period, g in by_country.groupby("period"):
        eff = g[[effect, *others]]
        largest_signed = eff.idxmax(axis=1) == effect
        rows.append({
            "period": period, "countries": len(g),
            "largest_positive": int((largest_signed & (g[effect] > 0)).sum()),
            "largest_signed_but_not_positive": int((largest_signed & (g[effect] <= 0)).sum()),
            "largest_absolute": int((eff.abs().idxmax(axis=1) == effect).sum()),
        })
    return pd.DataFrame(rows)


def common_sample(by_country, factors):
    """Means for the two sub-periods using only countries present in both."""
    p1, p2 = f"{S}-{B}", f"{B}-{E}"
    a = by_country[by_country["period"] == p1].set_index("iso3")
    b = by_country[by_country["period"] == p2].set_index("iso3")
    common = a.index.intersection(b.index)
    rows = []
    for period, d in [(p1, a.loc[common]), (p2, b.loc[common])]:
        row = {"period": period, "countries": len(common)}
        row.update({f"mean_{e}": d[e].mean() for e in ["change", *factors]})
        rows.append(row)
    return pd.DataFrame(rows)


def decompositions(panel, sample):
    out = {}
    for label, factors in [("two_factor", TWO_FACTOR), ("three_factor", THREE_FACTOR)]:
        by_country = pd.concat([decompose(panel, y0, y1, factors, SCALES[label])
                                for y0, y1 in PERIODS]).reset_index()
        by_country = by_country.merge(sample[["iso3", "name"]], on="iso3")
        out[label] = {
            "by_country": by_country,
            "by_group": summarise(by_country, factors, sample),
            "common": common_sample(by_country, factors),
        }
    out["three_factor"]["dominance"] = dominance(out["three_factor"]["by_country"])
    return out


# --- Case studies ------------------------------------------------------------

def case_studies(panel):
    """Rule: the largest economy in each World Bank region, plus the three highest burdens."""
    end = year(panel, E).reset_index()
    largest = (end.loc[end.groupby("region")["gdp_usd_bn"].idxmax()]
               .sort_values("gdp_usd_bn", ascending=False)
               .assign(reason="Largest economy in its region", group="Large economies"))
    top = (end.nlargest(3, "interest_burden")
           .assign(reason=f"One of the three highest burdens in {E}", group="Highest burdens"))
    chosen = pd.concat([largest, top]).drop_duplicates("iso3").reset_index(drop=True)
    chosen["plot_order"] = range(1, len(chosen) + 1)
    return chosen[["plot_order", "group", "iso3", "name", "region", "income_group", "gdp_usd_bn",
                   "interest_burden", "reason"]]


# --- Matched samples and other sensitivity checks ------------------------------

def _stats(end_values, start_values, debt):
    level = end_values.dropna()
    both = pd.concat([start_values.rename("s"), end_values.rename("e")], axis=1).dropna()
    corr = pd.concat([debt.rename("d"), level.rename("e")], axis=1).dropna()
    return {
        "countries_level": len(level),
        "median_burden_end": level.median(),
        "share_above_threshold": 100 * (level > config.HIGH_BURDEN_THRESHOLD).mean(),
        "spearman_debt_burden": stats.spearmanr(corr["d"], corr["e"]).statistic,
        "countries_change": len(both),
        "median_change_since_start": (both["e"] - both["s"]).median(),
    }


def matched_comparisons(panel):
    """Separate a change of sample from a change of measure.

    For each alternative measure: the net burden on all countries, the net
    burden on exactly the countries the alternative covers, and the
    alternative on those same countries. Changes use countries with values
    in both years for that measure.
    """
    s, e = year(panel, S), year(panel, E)
    rows = []
    for key, label, col in [("fpp", "Gross interest, IMF FPP", "interest_burden_gross"),
                            ("wb", "Gross interest, central government, World Bank", "interest_burden_wb")]:
        level_idx = e.index[e[col].notna()]
        change_idx = level_idx.intersection(s.index[s[col].notna()])
        net_level = e["interest_burden"].where(e.index.isin(level_idx))
        net_start = s["interest_burden"].where(s.index.isin(change_idx))
        alt_start = s[col].where(s.index.isin(change_idx))
        for step, measure, sample_label, end_v, start_v in [
            (1, "Net (Fiscal Monitor)", "All sample countries", e["interest_burden"], s["interest_burden"]),
            (2, "Net (Fiscal Monitor)", f"Countries covered by {label}", net_level, net_start),
            (3, label, "Same countries", e[col], alt_start),
        ]:
            rows.append({"comparison": key, "step": step, "measure": measure, "sample": sample_label,
                         **_stats(end_v, start_v, e["debt_gdp"])})
    return pd.DataFrame(rows)


def sensitivity(panel, sample, full):
    s, e, est = year(panel, S), year(panel, E), year(panel, X)
    small = sample.set_index("iso3")["is_small_state"].fillna(0).astype(bool)
    negative = e.index[e["net_interest_gdp"] <= 0]
    not_small = e.index[~small.reindex(e.index, fill_value=False)]
    # Brunei is the only repeated-zero case with otherwise complete data.
    full_s, full_e = year(full, S), year(full, E)
    with_brn = e.index.union(["BRN"])
    rows = [
        ("Baseline: net burden, all sample countries", e["interest_burden"], s["interest_burden"], e["debt_gdp"]),
        ("Excluding countries with negative net interest", e["interest_burden"].drop(negative),
         s["interest_burden"], e["debt_gdp"]),
        ("Excluding small states", e["interest_burden"].loc[not_small], s["interest_burden"], e["debt_gdp"]),
        (f"End year {X} (mostly estimates)", est["interest_burden"], s["interest_burden"], est["debt_gdp"]),
        ("Adding Brunei (repeated-zero case)", full_e["interest_burden"].reindex(with_brn),
         full_s["interest_burden"].reindex(with_brn), full_e["debt_gdp"].reindex(with_brn)),
    ]
    out = pd.DataFrame([{"specification": n, **_stats(a, b_, c)} for n, a, b_, c in rows])
    trimmed = e[e["interest_burden"].between(*e["interest_burden"].quantile([0.05, 0.95]))]
    out.attrs["spearman_trimmed"] = stats.spearmanr(trimmed["debt_gdp"], trimmed["interest_burden"]).statistic
    return out


def measure_agreement(panel):
    """How closely the alternative burden measures track the net burden in the end year."""
    e = year(panel, E)
    out = {}
    for label, col in [("gross_fpp", "interest_burden_gross"), ("gross_central_wb", "interest_burden_wb")]:
        d = e[["interest_burden", col]].dropna()
        out[label] = {
            "countries": len(d),
            "spearman": stats.spearmanr(d["interest_burden"], d[col]).statistic,
            "median_difference": (d[col] - d["interest_burden"]).median(),
            "within_2_points": float(((d[col] - d["interest_burden"]).abs() <= 2).mean()),
        }
    return out


# --- Interest vs social spending ----------------------------------------------

def social_spending_summary(tbl):
    h = tbl.dropna(subset=["health_gdp"])
    ed = tbl.dropna(subset=["education_gdp"])
    pop = lambda d: d["population"].sum() / 1e9
    return {
        "countries_health": len(h),
        "countries_interest_gt_health": int(h["interest_exceeds_health"].sum()),
        "population_interest_gt_health_bn": pop(h[h["interest_exceeds_health"] == 1]),
        "health_years": {str(int(k)): int(v) for k, v in h["health_year"].value_counts().sort_index().items()},
        "health_years_main": int(h["health_year"].mode().iloc[0]),
        "health_years_main_count": int((h["health_year"] == h["health_year"].mode().iloc[0]).sum()),
        "countries_education": len(ed),
        "countries_interest_gt_education": int(ed["interest_exceeds_education"].sum()),
        "population_interest_gt_education_bn": pop(ed[ed["interest_exceeds_education"] == 1]),
        "education_years": {str(int(k)): int(v) for k, v in ed["education_year"].value_counts().sort_index().items()},
        "population_year": E,
    }


# --- Key numbers -------------------------------------------------------------

NAMED_COUNTRIES = ["JPN", "NGA", "BGD", "LBN", "GHA", "CAN", "KWT", "SDN", "ITA", "GRC", "NOR",
                   "CRI", "BHR", "MWI", "KEN", "ZMB", "MEX", "IDN", "GBR", "FRA", "LAO"]


def country_facts(panel, social, isos):
    """Values for the countries the report discusses by name."""
    soc = social.set_index("iso3")
    out = {}
    for iso in isos:
        d = panel[panel["iso3"] == iso].set_index("year")
        if d.empty:
            continue
        get = lambda col, y: (float(d.loc[y, col]) if y in d.index and pd.notna(d.loc[y, col]) else None)
        hist = d["interest_burden"].loc[S:E].dropna()
        future = d["interest_burden"].loc[X:config.FORECAST_END].dropna()
        row = soc.loc[iso] if iso in soc.index else None
        out[iso] = {
            "name": d["name"].iloc[0],
            "burden_start": get("interest_burden", S),
            "burden_break": get("interest_burden", B),
            "burden_end": get("interest_burden", E),
            "burden_estimate": get("interest_burden", X),
            "burden_forecast_end": get("interest_burden", config.FORECAST_END),
            "burden_peak": float(hist.max()),
            "burden_peak_year": int(hist.idxmax()),
            "burden_max_forecast": float(future.max()) if len(future) else None,
            "burden_max_forecast_year": int(future.idxmax()) if len(future) else None,
            "gross_end": get("interest_burden_gross", E),
            "wb_end": get("interest_burden_wb", E),
            "debt_start": get("debt_gdp", S),
            "debt_end": get("debt_gdp", E),
            "revenue_end": get("revenue_gdp", E),
            "revenue_fpp_end": get("revenue_gdp_fpp", E),
            "net_interest_to_debt_end": get("net_interest_to_debt", E),
            "net_interest_gdp_end": get("net_interest_gdp", E),
            "health_year": int(row["health_year"]) if row is not None and pd.notna(row["health_year"]) else None,
            "interest_gdp_health_year": float(row["interest_gdp_health_year"]) if row is not None and pd.notna(row["interest_gdp_health_year"]) else None,
            "health_gdp": float(row["health_gdp"]) if row is not None and pd.notna(row["health_gdp"]) else None,
        }
    return out


def _records(df):
    return json.loads(df.to_json(orient="records"))


def key_numbers(panel, sample, tables, res):
    med = tables["group_medians"]
    pooled = tables["pooled_burden"]
    hb = tables["high_burden_counts"].set_index("year")
    change = tables["burden_change"]
    rank = tables["burden_ranking"]
    quad = tables["debt_burden_quadrants"]
    funnel = tables["sample_funnel"]
    reg = res["regressions"]

    def m(group, y, var="interest_burden"):
        r = med[(med["income_group"] == group) & (med["year"] == y) & (med["variable"] == var)]
        return float(r["median"].iloc[0])

    def pb(group, y, col="pooled_burden"):
        return float(pooled[(pooled["income_group"] == group) & (pooled["year"] == y)][col].iloc[0])

    def coef(model, term):
        r = reg[(reg["model"] == model) & (reg["term"] == term)].iloc[0]
        return {k: float(r[k]) for k in ["coef", "ci_low", "ci_high", "p_value", "r_squared"]} | {"countries": int(r["countries"])}

    def dec(label, group, period):
        t = res["decomp"][label]["by_group"]
        r = t[(t["income_group"] == group) & (t["period"] == period)].iloc[0]
        return {k: (float(v) if not isinstance(v, str) else v) for k, v in r.items()}

    groups = ["All countries"] + config.INCOME_ORDER
    periods = [f"{a}-{b}" for a, b in PERIODS]
    infl, loo = res["influence"]
    infl1 = infl[infl["model"] == "(1) Debt only"]
    infl2 = infl[infl["model"] == "(2) Debt and revenue"]
    levels = res["levels"].set_index("term")
    e = year(panel, E).dropna(subset=["gdp_usd_bn"])
    top20 = rank.head(20)["income_group"].value_counts()
    quad_counts = quad["group_label"].value_counts().to_dict()
    off_diag = (quad_counts.get("Above-median debt, below-median burden", 0)
                + quad_counts.get("Below-median debt, above-median burden", 0))
    dom = res["decomp"]["three_factor"]["dominance"].set_index("period")

    k = {
        "years": {"start": S, "break": B, "end": E, "estimate": X, "forecast_end": config.FORECAST_END},
        "sample": {
            "countries": len(sample),
            "by_income": sample["income_group"].value_counts().reindex(config.INCOME_ORDER).astype(int).to_dict(),
            "funnel": _records(funnel),
            "world_bank_list": int(funnel.loc[funnel["step"] == 1, "countries"].iloc[0]),
            "with_any_revenue": int(funnel.loc[funnel["step"] == 2, "countries"].iloc[0]),
            "excluded_with_some_data": int(funnel.loc[funnel["step"] == 2, "countries"].iloc[0]) - len(sample),
        },
        "median_burden": {g: {y: m(g, y) for y in range(S, config.FORECAST_END + 1)} for g in groups},
        "median_burden_gross": {g: {y: m(g, y, "interest_burden_gross") for y in (S, B, E)} for g in groups},
        "median_debt": {g: {y: m(g, y, "debt_gdp") for y in (S, B, E)} for g in groups},
        "median_revenue": {g: {y: m(g, y, "revenue_gdp") for y in (S, B, E)} for g in groups},
        "median_net_interest_gdp": {g: {y: m(g, y, "net_interest_gdp") for y in (S, B, E)} for g in groups},
        "median_net_interest_to_debt": {g: {y: m(g, y, "net_interest_to_debt") for y in (S, B, E)} for g in groups},
        "pooled_burden": {g: {y: pb(g, y) for y in range(S, config.FORECAST_END + 1)} for g in groups},
        "net_interest_usd_trn": {y: pb("All countries", y, "net_interest_usd_bn") / 1000 for y in (S, B, E, X)},
        "gdp_weighted_average_burden_end": float(np.average(e["interest_burden"], weights=e["gdp_usd_bn"])),
        "high_burden": {
            "threshold": config.HIGH_BURDEN_THRESHOLD,
            "countries": {int(y): int(hb.loc[y, "countries_above"]) for y in hb.index},
            "population_bn": {int(y): float(hb.loc[y, "population_above_bn"]) for y in hb.index},
        },
        "change": {
            "countries_up_start_end": int((change["change_start_end"] > 0).sum()),
            "countries_up_break_end": int((change["change_break_end"] > 0).sum()),
            "median_change_start_end": float(change["change_start_end"].median()),
            "median_change_break_end": float(change["change_break_end"].median()),
        },
        "top_burden": _records(rank.head(20)[["name", "income_group", "interest_burden", "debt_gdp", "revenue_gdp"]]),
        "top20_low_and_lower_middle": int(top20.get("Low income", 0) + top20.get("Lower middle income", 0)),
        "top20_debt": {
            "min": float(rank.head(20)["debt_gdp"].min()),
            "min_country": rank.head(20).loc[rank.head(20)["debt_gdp"].idxmin(), "name"],
            "max": float(rank.head(20)["debt_gdp"].max()),
            "max_country": rank.head(20).loc[rank.head(20)["debt_gdp"].idxmax(), "name"],
        },
        "quadrants": {
            "median_debt": float(quad["median_debt"].iloc[0]),
            "median_burden": float(quad["median_burden"].iloc[0]),
            "counts": quad_counts,
            "different_classification": off_diag,
            "different_classification_share": off_diag / len(sample),
            "debt_high_burden_low_hic_share": float(
                quad[quad["group_label"] == "Above-median debt, below-median burden"]["income_group"].eq("High income").mean()),
            "debt_low_burden_high_lic_lmic_share": float(
                quad[quad["group_label"] == "Below-median debt, above-median burden"]["income_group"]
                .isin(["Low income", "Lower middle income"]).mean()),
        },
        "correlation": res["correlations"].set_index("group").to_dict("index"),
        "spearman_trimmed": float(res["sensitivity"].attrs["spearman_trimmed"]),
        "regression": {
            "debt_only": coef("(1) Debt only", "log_debt"),
            "debt_with_revenue": coef("(2) Debt and revenue", "log_debt"),
            "revenue": coef("(2) Debt and revenue", "log_revenue"),
            "debt_full": coef("(3) Adding income group", "log_debt"),
            "revenue_full": coef("(3) Adding income group", "log_revenue"),
            "low_income_full": coef("(3) Adding income group", "C(income_group)[T.Low income]"),
            "nid_on_debt": coef("(4) Net-interest-to-debt factor", "log_debt"),
            "nid_low_income": coef("(4) Net-interest-to-debt factor", "C(income_group)[T.Low income]"),
            "nid_lower_middle": coef("(4) Net-interest-to-debt factor", "C(income_group)[T.Lower middle income]"),
            "nid_upper_middle": coef("(4) Net-interest-to-debt factor", "C(income_group)[T.Upper middle income]"),
            "countries_positive": int(len(regression_data(year(panel, E)))),
            "countries_excluded_nonpositive": int((year(panel, E)["net_interest_gdp"] <= 0).sum()),
        },
        "influence": {
            "debt_only_top": _records(infl1.head(3)[["name", "net_burden", "cooks_distance", "leverage"]]),
            "debt_only_r2_without_min": float(infl1["r_squared_without_country"].min()),
            "debt_only_r2_without_max": float(infl1["r_squared_without_country"].max()),
            "debt_only_r2_without_max_country": infl1.loc[infl1["r_squared_without_country"].idxmax(), "name"],
            "debt_only_r2_without_canada": float(infl1.loc[infl1["iso3"] == "CAN", "r_squared_without_country"].iloc[0]),
            "with_revenue_r2_without_canada": float(infl2.loc[infl2["iso3"] == "CAN", "r_squared_without_country"].iloc[0]),
            "with_revenue_r2_without_min": float(infl2["r_squared_without_country"].min()),
            "with_revenue_r2_without_max": float(infl2["r_squared_without_country"].max()),
        },
        "levels_model": {
            "countries": int(levels.loc["debt_gdp", "countries"]),
            "r_squared": float(levels.loc["debt_gdp", "r_squared"]),
            "debt_coef": float(levels.loc["debt_gdp", "coef"]),
            "debt_ci_low": float(levels.loc["debt_gdp", "ci_low"]),
            "debt_ci_high": float(levels.loc["debt_gdp", "ci_high"]),
            "revenue_coef": float(levels.loc["revenue_gdp", "coef"]),
            "revenue_ci_low": float(levels.loc["revenue_gdp", "ci_low"]),
            "revenue_ci_high": float(levels.loc["revenue_gdp", "ci_high"]),
        },
        "decomposition_two": {g: {p: dec("two_factor", g, p) for p in periods} for g in groups},
        "decomposition_three": {g: {p: dec("three_factor", g, p) for p in periods} for g in groups},
        "decomposition_common": {
            label: _records(res["decomp"][label]["common"]) for label in ("two_factor", "three_factor")},
        "dominance": {p: {kk: int(v) for kk, v in dom.loc[p].items()} for p in dom.index},
        "matched": _records(res["matched"]),
        "sensitivity": res["sensitivity"].set_index("specification").to_dict("index"),
        "social_spending": res["social"],
        "measure_agreement": res["agreement"],
        "case_studies": _records(res["cases"][["plot_order", "group", "name", "reason"]]),
    }
    reg_k = k["regression"]
    fpp = res["matched"][res["matched"]["comparison"] == "fpp"].set_index("step")["median_burden_end"]
    wb = res["matched"][res["matched"]["comparison"] == "wb"].set_index("step")["median_burden_end"]
    k["derived"] = {
        # coefficients in log points turned into multiples relative to high-income economies
        "nid_multiple_upper_middle": float(np.exp(reg_k["nid_upper_middle"]["coef"])),
        "nid_multiple_lower_middle": float(np.exp(reg_k["nid_lower_middle"]["coef"])),
        "nid_multiple_low_income": float(np.exp(reg_k["nid_low_income"]["coef"])),
        "revenue_elasticity_abs": abs(reg_k["revenue"]["coef"]),
        "burden_multiple_low_vs_high": m("Low income", E) / m("High income", E),
        "revenue_ratio_high_vs_low": m("High income", E, "revenue_gdp") / m("Low income", E, "revenue_gdp"),
        "fpp_gap_total": fpp[3] - fpp[1],
        "fpp_gap_sample": fpp[2] - fpp[1],
        "fpp_gap_measure": fpp[3] - fpp[2],
        "fpp_gap_sample_share": (fpp[2] - fpp[1]) / (fpp[3] - fpp[1]),
        "wb_gap_total": wb[3] - wb[1],
        "wb_gap_sample": wb[2] - wb[1],
        "wb_gap_measure": wb[3] - wb[2],
        "pooled_change_break_end": pb("All countries", E) - pb("All countries", B),
    }
    return k


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(key): _jsonable(v) for key, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj


def run(tables):
    panel, sample, full = load()
    end = year(panel, E).reset_index()

    res = {
        "correlations": correlations(end),
        "regressions": regressions(end),
        "influence": regression_influence(end),
        "levels": regression_levels(year(panel, E)),
        "decomp": decompositions(panel, sample),
        "cases": case_studies(panel),
        "matched": matched_comparisons(panel),
        "sensitivity": sensitivity(panel, sample, full),
        "social": social_spending_summary(tables["interest_vs_social_spending"]),
        "agreement": measure_agreement(panel),
    }

    res["correlations"].to_csv(config.TABLES / "correlations.csv", index=False)
    res["regressions"].to_csv(config.TABLES / "regressions.csv", index=False)
    res["influence"][0].to_csv(config.TABLES / "regression_influence.csv", index=False)
    res["levels"].to_csv(config.TABLES / "regression_levels.csv", index=False)
    for label, parts in res["decomp"].items():
        parts["by_country"].to_csv(config.TABLES / f"decomposition_{label}_by_country.csv", index=False)
        parts["by_group"].to_csv(config.TABLES / f"decomposition_{label}_by_group.csv", index=False)
        parts["common"].to_csv(config.TABLES / f"decomposition_{label}_common_sample.csv", index=False)
    res["decomp"]["three_factor"]["dominance"].to_csv(config.TABLES / "decomposition_dominance.csv", index=False)
    res["cases"].to_csv(config.TABLES / "case_studies.csv", index=False)
    res["matched"].to_csv(config.TABLES / "matched_sample_comparison.csv", index=False)
    res["sensitivity"].to_csv(config.TABLES / "sensitivity.csv", index=False)

    numbers = key_numbers(panel, sample, tables, res)
    numbers["country"] = country_facts(panel, tables["interest_vs_social_spending"],
                                       list(res["cases"]["iso3"]) + NAMED_COUNTRIES)
    path = config.ROOT / "outputs" / "key_numbers.json"
    path.write_text(json.dumps(_jsonable(numbers), indent=2), encoding="utf-8")
    return numbers
