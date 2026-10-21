"""Checks on data integrity and on the internal consistency of the results.

Several tests recompute in pandas what the SQL produced, so that an error in
one implementation shows up as a disagreement with the other.
"""

import json

import numpy as np
import pandas as pd
import pytest
from scipy import stats

import build_report
import config
import database

YEARS = range(config.START_YEAR, config.END_YEAR + 1)


@pytest.fixture(scope="module")
def panel():
    return pd.read_csv(config.PANEL_CSV)


@pytest.fixture(scope="module")
def sample():
    return pd.read_csv(config.DATA_PROCESSED / "sample.csv")


@pytest.fixture(scope="module")
def in_sample(panel, sample):
    return panel[panel["iso3"].isin(sample["iso3"])]


@pytest.fixture(scope="module")
def key():
    return json.loads((config.ROOT / "outputs" / "key_numbers.json").read_text(encoding="utf-8"))


def table(name):
    return pd.read_csv(config.TABLES / f"{name}.csv")


# --- Raw data and panel -------------------------------------------------------

@pytest.mark.parametrize("name", ["imf_datamapper.csv", "wb_wdi.csv"])
def test_raw_snapshot_has_no_duplicate_observations(name):
    df = pd.read_csv(config.DATA_RAW / name, keep_default_na=False)
    assert not df.duplicated(["series_code", "iso3", "year"]).any()


def test_panel_has_one_row_per_country_year(panel):
    assert not panel.duplicated(["iso3", "year"]).any()


def test_burden_matches_its_definition(panel):
    d = panel.dropna(subset=["primary_balance_gdp", "overall_balance_gdp", "revenue_gdp"])
    rebuilt = 100 * (d["primary_balance_gdp"] - d["overall_balance_gdp"]) / d["revenue_gdp"]
    assert np.allclose(rebuilt, d["interest_burden"], atol=1e-9)


def test_identity_rate_times_debt_over_revenue(panel):
    d = panel[(panel["debt_gdp"] > 0) & panel["interest_burden"].notna()]
    assert np.allclose(d["implicit_rate"] * d["debt_gdp"] / d["revenue_gdp"], d["interest_burden"], atol=1e-9)


def test_sample_is_balanced(in_sample, sample):
    window = in_sample[in_sample["year"].isin(YEARS)]
    counts = window.groupby("iso3")["interest_burden"].count()
    assert len(counts) == len(sample)
    assert (counts == len(YEARS)).all()


def test_placeholder_zero_interest_economies_are_excluded(sample):
    assert not {"BRN", "LBY", "MAC"} & set(sample["iso3"])


def test_imf_codes_are_mapped_to_world_bank_codes(panel):
    assert {"XKX", "PSE"} <= set(panel["iso3"])
    assert not {"UVK", "WBG"} & set(panel["iso3"])


def test_no_blocking_validation_failures():
    results = database.run_validation()  # raises if an 'error' check returns rows
    assert all(len(df) == 0 for meta, df in results.values() if meta.get("severity") == "error")


# --- SQL results recomputed in pandas -------------------------------------------

def test_sql_medians_match_pandas(in_sample):
    sql = table("group_medians")
    d = in_sample.copy()
    d.loc[d["net_interest_gdp"] <= 0, "implicit_rate"] = np.nan  # as in 04_analysis.sql
    for (group, year, variable), value in sql.set_index(["income_group", "year", "variable"])["median"].items():
        sub = d if group == "All countries" else d[d["income_group"] == group]
        expected = sub.loc[sub["year"] == year, variable].median()
        assert value == pytest.approx(expected, abs=1e-9), (group, year, variable)


def test_sql_aggregate_matches_pandas(in_sample):
    sql = table("aggregate_burden").set_index(["income_group", "year"])["interest_burden"]
    d = in_sample[in_sample["gdp_usd_bn"].notna()]
    for year in YEARS:
        y = d[d["year"] == year]
        expected = 100 * (y["net_interest_gdp"] * y["gdp_usd_bn"]).sum() / (y["revenue_gdp"] * y["gdp_usd_bn"]).sum()
        assert sql[("All countries", year)] == pytest.approx(expected, rel=1e-9)


def test_ranking_is_sorted_and_complete(sample):
    r = table("burden_ranking")
    assert len(r) == len(sample)
    assert r["interest_burden"].is_monotonic_decreasing


# --- Statistics -------------------------------------------------------------------

def test_decomposition_adds_up_for_every_country():
    d = table("decomposition_by_country")
    total = d[["rate_effect", "debt_effect", "revenue_effect"]].sum(axis=1)
    assert np.allclose(total, d["change"], atol=1e-9)


def test_group_decomposition_means_add_up():
    d = table("decomposition_by_group")
    total = d[["mean_rate_effect", "mean_debt_effect", "mean_revenue_effect"]].sum(axis=1)
    assert np.allclose(total, d["mean_change"], atol=1e-9)


def test_spearman_in_key_numbers_reproduces(in_sample, key):
    e = in_sample[in_sample["year"] == config.END_YEAR]
    rho = stats.spearmanr(e["debt_gdp"], e["interest_burden"]).statistic
    assert key["correlation"]["All countries"]["spearman"] == pytest.approx(rho, abs=1e-12)


def test_bootstrap_interval_contains_estimate(key):
    c = key["correlation"]["All countries"]
    assert c["ci_low"] < c["spearman"] < c["ci_high"]


# --- Report and figures -------------------------------------------------------------

def test_figures_exist():
    names = sorted(p.name for p in config.FIGURES.glob("fig*.png"))
    assert len(names) == 8


@pytest.mark.parametrize("template, output", [
    ("README.md", "README.md"),
    ("economic_analysis.md", "report/economic_analysis.md"),
])
def test_documents_are_rendered_from_current_numbers(key, template, output):
    expected = build_report.render((build_report.TEMPLATES / template).read_text(encoding="utf-8"), key)
    actual = (config.ROOT / output).read_text(encoding="utf-8")
    assert "{{" not in actual
    assert actual == expected, f"{output} is stale: run `python run.py`"


def test_template_refuses_missing_numbers():
    with pytest.raises(KeyError):
        build_report.render("{{not/a/number}}", {})
