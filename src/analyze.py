"""Statistical analysis on top of the SQL tables.

Correlations, regressions, the LMDI decomposition, case-study selection and
robustness checks. Results go to outputs/tables/; the numbers quoted in the
report are collected in outputs/key_numbers.json so the report can be built
from them rather than typed by hand.
"""

import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

import config

SEED = 2026
N_BOOT = 2000


def load():
    panel = pd.read_csv(config.PANEL_CSV)
    sample = pd.read_csv(config.DATA_PROCESSED / "sample.csv")
    return panel[panel["iso3"].isin(sample["iso3"])].copy(), sample


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
    "(4) Implicit rate": "log_rate ~ log_debt + C(income_group)",
}


def regressions(end):
    d = end[end["net_interest_gdp"] > 0].copy()
    d["log_burden"] = np.log(d["interest_burden"])
    d["log_debt"] = np.log(d["debt_gdp"])
    d["log_revenue"] = np.log(d["revenue_gdp"])
    d["log_rate"] = np.log(d["implicit_rate"])
    d["income_group"] = pd.Categorical(d["income_group"], categories=config.INCOME_ORDER)
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


# --- Decomposition -----------------------------------------------------------

def lmdi(panel, y0, y1):
    """Split each country's change in burden into rate, debt and revenue effects."""
    cols = ["interest_burden", "implicit_rate", "debt_gdp", "revenue_gdp"]
    a, b = year(panel, y0)[cols], year(panel, y1)[cols]
    d = a.join(b, lsuffix="_0", rsuffix="_1").dropna()
    d = d[(d["interest_burden_0"] > 0) & (d["interest_burden_1"] > 0)]
    b0, b1 = d["interest_burden_0"], d["interest_burden_1"]
    same = np.isclose(b0, b1)
    weight = np.where(same, b0, (b1 - b0) / np.where(same, 1, np.log(b1 / b0)))
    out = pd.DataFrame({
        "period": f"{y0}-{y1}",
        "burden_start": b0,
        "burden_end": b1,
        "change": b1 - b0,
        "rate_effect": weight * np.log(d["implicit_rate_1"] / d["implicit_rate_0"]),
        "debt_effect": weight * np.log(d["debt_gdp_1"] / d["debt_gdp_0"]),
        "revenue_effect": -weight * np.log(d["revenue_gdp_1"] / d["revenue_gdp_0"]),
    })
    gap = out["change"] - out[["rate_effect", "debt_effect", "revenue_effect"]].sum(axis=1)
    assert gap.abs().max() < 1e-9, "LMDI contributions do not add up"
    return out


def decomposition(panel, sample):
    periods = [(config.START_YEAR, config.BREAK_YEAR), (config.BREAK_YEAR, config.END_YEAR),
               (config.START_YEAR, config.END_YEAR)]
    by_country = pd.concat([lmdi(panel, *p) for p in periods]).reset_index()
    by_country = by_country.merge(sample[["iso3", "name", "income_group"]], on="iso3")
    effects = ["change", "rate_effect", "debt_effect", "revenue_effect"]
    frames = []
    for grp, d in [("All countries", by_country)] + list(by_country.groupby("income_group")):
        for period, g in d.groupby("period"):
            row = {"income_group": grp, "period": period, "countries": len(g)}
            row.update({f"mean_{e}": g[e].mean() for e in effects})
            row.update({f"median_{e}": g[e].median() for e in effects})
            row["share_rate_largest_up"] = (
                g[["rate_effect", "debt_effect", "revenue_effect"]].idxmax(axis=1) == "rate_effect"
            ).mean()
            frames.append(row)
    return by_country, pd.DataFrame(frames)


# --- Case studies ------------------------------------------------------------

def case_studies(panel):
    end = year(panel, config.END_YEAR).reset_index()
    largest = end.loc[end.groupby("region")["gdp_usd_bn"].idxmax()].assign(
        reason="Largest economy in region")
    top = end.nlargest(3, "interest_burden").assign(reason="Highest burden in end year")
    chosen = pd.concat([largest, top]).drop_duplicates("iso3")
    return chosen[["iso3", "name", "region", "income_group", "gdp_usd_bn", "interest_burden", "reason"]]


# --- Robustness --------------------------------------------------------------

def _summary(label, end_values, start_values, debt):
    both = pd.concat([start_values.rename("s"), end_values.rename("e")], axis=1).dropna()
    corr = pd.concat([debt.rename("d"), end_values.rename("e")], axis=1).dropna()
    return {
        "specification": label,
        "countries": int(end_values.notna().sum()),
        "median_burden_end": end_values.median(),
        "median_change_since_start": (both["e"] - both["s"]).median(),
        "share_above_threshold": 100 * (end_values.dropna() > config.HIGH_BURDEN_THRESHOLD).mean(),
        "spearman_debt_burden": stats.spearmanr(corr["d"], corr["e"]).statistic,
    }


def robustness(panel, sample):
    s, e = year(panel, config.START_YEAR), year(panel, config.END_YEAR)
    est = year(panel, config.ESTIMATE_YEAR)
    small = sample.set_index("iso3")["is_small_state"].fillna(0).astype(bool)
    creditors = e.index[e["net_interest_gdp"] <= 0]
    rows = [
        _summary("Baseline (net interest, general government)", e["interest_burden"], s["interest_burden"], e["debt_gdp"]),
        _summary("Gross interest, general government (FPP)", e["interest_burden_gross"], s["interest_burden_gross"], e["debt_gdp"]),
        _summary("Gross interest, central government (World Bank)", e["interest_burden_wb"], s["interest_burden_wb"], e["debt_gdp"]),
        _summary("Excluding net-creditor governments", e["interest_burden"].drop(creditors), s["interest_burden"].drop(creditors), e["debt_gdp"]),
        _summary("Excluding small states", e["interest_burden"][~small.reindex(e.index, fill_value=False)],
                 s["interest_burden"], e["debt_gdp"]),
        _summary(f"End year {config.ESTIMATE_YEAR} (estimate)", est["interest_burden"], s["interest_burden"], est["debt_gdp"]),
    ]
    out = pd.DataFrame(rows)
    # The same statistics for the baseline measure on exactly the countries each
    # alternative covers, to separate a change of measure from a change of sample.
    same = []
    for label, col in [("Gross interest, general government (FPP)", "interest_burden_gross"),
                       ("Gross interest, central government (World Bank)", "interest_burden_wb")]:
        idx = e.index[e[col].notna()]
        same.append({"specification": label, "baseline_median_same_countries": e.loc[idx, "interest_burden"].median()})
    out = out.merge(pd.DataFrame(same), on="specification", how="left")

    trimmed = e[e["interest_burden"].between(*e["interest_burden"].quantile([0.05, 0.95]))]
    out.attrs["spearman_trimmed"] = stats.spearmanr(trimmed["debt_gdp"], trimmed["interest_burden"]).statistic
    return out


def measure_agreement(panel):
    """How closely the alternative burden measures track the baseline in the end year."""
    e = year(panel, config.END_YEAR)
    out = {}
    for label, col in [("gross_general_government", "interest_burden_gross"),
                       ("gross_central_government", "interest_burden_wb")]:
        d = e[["interest_burden", col]].dropna()
        out[label] = {
            "countries": len(d),
            "spearman": stats.spearmanr(d["interest_burden"], d[col]).statistic,
            "pearson": stats.pearsonr(d["interest_burden"], d[col]).statistic,
            "median_gap": (d[col] - d["interest_burden"]).median(),
            "within_2_points": float(((d[col] - d["interest_burden"]).abs() <= 2).mean()),
        }
    return out


# --- Interest vs social spending ----------------------------------------------

def social_spending_summary(tbl):
    h = tbl.dropna(subset=["health_gdp"])
    ed = tbl.dropna(subset=["education_gdp"])
    both = tbl.dropna(subset=["health_gdp", "education_gdp"])
    either = both[(both["interest_exceeds_health"] == 1) | (both["interest_exceeds_education"] == 1)]
    pop = lambda d: d["population"].sum() / 1e9
    return {
        "countries_health": len(h),
        "countries_interest_gt_health": int(h["interest_exceeds_health"].sum()),
        "population_interest_gt_health_bn": pop(h[h["interest_exceeds_health"] == 1]),
        "countries_education": len(ed),
        "countries_interest_gt_education": int(ed["interest_exceeds_education"].sum()),
        "population_interest_gt_education_bn": pop(ed[ed["interest_exceeds_education"] == 1]),
        "countries_both_reported": len(both),
        "countries_interest_gt_either": len(either),
        "population_interest_gt_either_bn": pop(either),
        "health_year_median": float(h["health_year"].median()),
        "education_year_median": float(ed["education_year"].median()),
    }


# --- Key numbers -------------------------------------------------------------

def key_numbers(panel, sample, tables, corr, reg, decomp, robust, social):
    med = tables["group_medians"]
    agg = tables["aggregate_burden"]
    hb = tables["high_burden_counts"].set_index("year")
    change = tables["burden_change"]
    rank = tables["burden_ranking"]
    quad = tables["debt_burden_quadrants"]

    def m(group, y, var="interest_burden"):
        r = med[(med["income_group"] == group) & (med["year"] == y) & (med["variable"] == var)]
        return float(r["median"].iloc[0])

    def a(group, y):
        return float(agg[(agg["income_group"] == group) & (agg["year"] == y)]["interest_burden"].iloc[0])

    def coef(model, term):
        r = reg[(reg["model"] == model) & (reg["term"] == term)].iloc[0]
        return {k: float(r[k]) for k in ["coef", "ci_low", "ci_high", "p_value", "r_squared"]} | {"countries": int(r["countries"])}

    def dec(group, period):
        r = decomp[(decomp["income_group"] == group) & (decomp["period"] == period)].iloc[0]
        return {k: (float(v) if not isinstance(v, str) else v) for k, v in r.items()}

    S, B, E, X = config.START_YEAR, config.BREAK_YEAR, config.END_YEAR, config.ESTIMATE_YEAR
    groups = ["All countries"] + config.INCOME_ORDER
    full = pd.read_csv(config.PANEL_CSV)
    with_data = full[full["year"].between(S, E) & full["revenue_gdp"].notna()]["iso3"].unique()
    top20 = rank.head(20)["income_group"].value_counts()
    k = {
        "years": {"start": S, "break": B, "end": E, "estimate": X, "forecast_end": config.FORECAST_END},
        "sample": {
            "countries": len(sample),
            "by_income": sample["income_group"].value_counts().reindex(config.INCOME_ORDER).astype(int).to_dict(),
            "excluded_with_some_data": int(len(set(with_data) - set(sample["iso3"]))),
        },
        "top20_by_income": {g: int(top20.get(g, 0)) for g in config.INCOME_ORDER},
        "top20_low_and_lower_middle": int(top20.get("Low income", 0) + top20.get("Lower middle income", 0)),
        "median_burden": {g: {y: m(g, y) for y in range(S, config.FORECAST_END + 1)} for g in groups},
        "median_burden_gross": {g: {y: m(g, y, "interest_burden_gross") for y in (S, B, E)} for g in groups},
        "median_debt": {g: {y: m(g, y, "debt_gdp") for y in (S, B, E)} for g in groups},
        "median_revenue": {g: {y: m(g, y, "revenue_gdp") for y in (S, B, E)} for g in groups},
        "median_implicit_rate": {g: {y: m(g, y, "implicit_rate") for y in (S, B, E)} for g in groups},
        "aggregate_burden": {g: {y: a(g, y) for y in range(S, config.FORECAST_END + 1)} for g in groups},
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
            "largest_increases": change.nlargest(10, "change_start_end")[["name", "burden_start", "burden_end", "change_start_end"]].to_dict("records"),
            "largest_decreases": change.nsmallest(5, "change_start_end")[["name", "burden_start", "burden_end", "change_start_end"]].to_dict("records"),
        },
        "top_burden": rank.head(15)[["name", "income_group", "interest_burden", "debt_gdp", "revenue_gdp", "implicit_rate"]].to_dict("records"),
        "quadrants": {
            "median_debt": float(quad["median_debt"].iloc[0]),
            "median_burden": float(quad["median_burden"].iloc[0]),
            "counts": quad["quadrant"].value_counts().to_dict(),
            "low_debt_high_burden_lic_lmic_share": float(
                quad[quad["quadrant"] == "Low debt, high burden"]["income_group"].isin(["Low income", "Lower middle income"]).mean()),
            "high_debt_low_burden_hic_share": float(
                quad[quad["quadrant"] == "High debt, low burden"]["income_group"].eq("High income").mean()),
        },
        "correlation": corr.set_index("group").to_dict("index"),
        "spearman_trimmed": float(robust.attrs["spearman_trimmed"]),
        "regression": {
            "debt_only": coef("(1) Debt only", "log_debt"),
            "debt_with_revenue": coef("(2) Debt and revenue", "log_debt"),
            "revenue": coef("(2) Debt and revenue", "log_revenue"),
            "debt_full": coef("(3) Adding income group", "log_debt"),
            "revenue_full": coef("(3) Adding income group", "log_revenue"),
            "rate_on_debt": coef("(4) Implicit rate", "log_debt"),
            "rate_low_income": coef("(4) Implicit rate", "C(income_group)[T.Low income]"),
            "rate_lower_middle": coef("(4) Implicit rate", "C(income_group)[T.Lower middle income]"),
            "rate_upper_middle": coef("(4) Implicit rate", "C(income_group)[T.Upper middle income]"),
            "r2_full": coef("(3) Adding income group", "log_debt")["r_squared"],
        },
        "decomposition": {g: {p: dec(g, p) for p in decomp["period"].unique()} for g in groups},
        "robustness": robust.set_index("specification").to_dict("index"),
        "social_spending": social,
        "net_interest_usd_bn": {
            y: float(agg[(agg["income_group"] == "All countries") & (agg["year"] == y)]["net_interest_usd_bn"].iloc[0])
            for y in (S, B, E, X)
        },
    }
    k["net_interest_usd_trn"] = {y: v / 1000 for y, v in k["net_interest_usd_bn"].items()}
    reg_k = k["regression"]
    k["derived"] = {
        # log-point coefficients turned into multiples relative to high-income economies
        "rate_multiple_upper_middle": float(np.exp(reg_k["rate_upper_middle"]["coef"])),
        "rate_multiple_lower_middle": float(np.exp(reg_k["rate_lower_middle"]["coef"])),
        "rate_multiple_low_income": float(np.exp(reg_k["rate_low_income"]["coef"])),
        "r2_gain_from_revenue": reg_k["debt_with_revenue"]["r_squared"] - reg_k["debt_only"]["r_squared"],
        "revenue_elasticity_abs": abs(reg_k["revenue"]["coef"]),
        "off_diagonal_share": (k["quadrants"]["counts"].get("High debt, low burden", 0)
                               + k["quadrants"]["counts"].get("Low debt, high burden", 0)) / len(sample),
        "burden_multiple_low_vs_high": m("Low income", E) / m("High income", E),
        "revenue_ratio_high_vs_low": m("High income", E, "revenue_gdp") / m("Low income", E, "revenue_gdp"),
        "off_diagonal_countries": int(k["quadrants"]["counts"].get("High debt, low burden", 0)
                                      + k["quadrants"]["counts"].get("Low debt, high burden", 0)),
        "rate_effect_share_2021_2024": k["decomposition"]["All countries"][f"{B}-{E}"]["mean_rate_effect"]
                                        / k["decomposition"]["All countries"][f"{B}-{E}"]["mean_change"],
        "offset_2021_2024": -(k["decomposition"]["All countries"][f"{B}-{E}"]["mean_debt_effect"]
                              + k["decomposition"]["All countries"][f"{B}-{E}"]["mean_revenue_effect"]),
    }
    return k


NAMED_COUNTRIES = ["JPN", "NGA", "BGD", "LBN", "GHA", "CAN", "KWT", "SDN", "ITA", "GRC", "NOR",
                   "CRI", "BHR", "MWI", "KEN", "ZMB", "MEX", "IDN", "GBR", "FRA", "LAO"]


def country_facts(panel, isos):
    """Values for the countries the report discusses by name."""
    out = {}
    for iso in isos:
        d = panel[panel["iso3"] == iso].set_index("year")
        if d.empty:
            continue
        get = lambda col, y: (float(d.loc[y, col]) if y in d.index and pd.notna(d.loc[y, col]) else None)
        health = d["health_gdp"].loc[:config.END_YEAR].dropna()
        hist = d["interest_burden"].loc[config.START_YEAR:config.END_YEAR].dropna()
        future = d["interest_burden"].loc[config.ESTIMATE_YEAR:config.FORECAST_END].dropna()
        out[iso] = {
            "name": d["name"].iloc[0],
            "burden_start": get("interest_burden", config.START_YEAR),
            "burden_break": get("interest_burden", config.BREAK_YEAR),
            "burden_end": get("interest_burden", config.END_YEAR),
            "burden_estimate": get("interest_burden", config.ESTIMATE_YEAR),
            "burden_forecast_end": get("interest_burden", config.FORECAST_END),
            "burden_peak": float(hist.max()),
            "burden_peak_year": int(hist.idxmax()),
            "burden_max_forecast": float(future.max()) if len(future) else None,
            "burden_max_forecast_year": int(future.idxmax()) if len(future) else None,
            "gross_end": get("interest_burden_gross", config.END_YEAR),
            "wb_end": get("interest_burden_wb", config.END_YEAR),
            "debt_start": get("debt_gdp", config.START_YEAR),
            "debt_end": get("debt_gdp", config.END_YEAR),
            "revenue_end": get("revenue_gdp", config.END_YEAR),
            "implicit_rate_end": get("implicit_rate", config.END_YEAR),
            "interest_gdp_end": get("net_interest_gdp", config.END_YEAR),
            "health_gdp": float(health.iloc[-1]) if len(health) else None,
        }
    return out


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
    panel, sample = load()
    end = year(panel, config.END_YEAR).reset_index()

    corr = correlations(end)
    reg = regressions(end)
    by_country, decomp = decomposition(panel, sample)
    cases = case_studies(panel)
    robust = robustness(panel, sample)
    social = social_spending_summary(tables["interest_vs_social_spending"])

    corr.to_csv(config.TABLES / "correlations.csv", index=False)
    reg.to_csv(config.TABLES / "regressions.csv", index=False)
    by_country.to_csv(config.TABLES / "decomposition_by_country.csv", index=False)
    decomp.to_csv(config.TABLES / "decomposition_by_group.csv", index=False)
    cases.to_csv(config.TABLES / "case_studies.csv", index=False)
    robust.to_csv(config.TABLES / "robustness.csv", index=False)

    numbers = key_numbers(panel, sample, tables, corr, reg, decomp, robust, social)
    numbers["case_studies"] = cases[["name", "reason"]].to_dict("records")
    numbers["measure_agreement"] = measure_agreement(panel)
    numbers["country"] = country_facts(panel, list(cases["iso3"]) + NAMED_COUNTRIES)
    path = config.ROOT / "outputs" / "key_numbers.json"
    path.write_text(json.dumps(_jsonable(numbers), indent=2), encoding="utf-8")
    return numbers
