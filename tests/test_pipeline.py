"""Checks on data integrity, calculations, review flags, links and generated text.

Several tests recompute in pandas what the SQL produced, or check a result
against a small example calculated by hand, so that an error in one
implementation shows up as a disagreement with the other. Passing tests show
that the pipeline is internally consistent; they do not show that the
economic interpretation is right.
"""

import json
import math

import numpy as np
import pandas as pd
import pytest
from scipy import stats

import acquire
import analyze
import build_report
import compare_numbers
import config
import database
import snapshot
import validate

YEARS = range(config.START_YEAR, config.END_YEAR + 1)
E = config.END_YEAR


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

def test_snapshot_matches_manifest():
    assert snapshot.check_inputs()


def test_refresh_never_overwrites_published_snapshot():
    with pytest.raises(ValueError):
        acquire.main(config.DATA_RAW)


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


def test_identity_factor_times_debt_over_revenue(panel):
    d = panel[(panel["debt_gdp"] > 0) & panel["interest_burden"].notna()]
    assert np.allclose(d["net_interest_to_debt"] * d["debt_gdp"] / d["revenue_gdp"], d["interest_burden"], atol=1e-9)


def test_sample_is_balanced(in_sample, sample):
    window = in_sample[in_sample["year"].isin(YEARS)]
    counts = window.groupby("iso3")["interest_burden"].count()
    assert len(counts) == len(sample)
    assert (counts == len(YEARS)).all()


def test_sample_funnel_adds_up(sample):
    f = table("sample_funnel").sort_values("step")
    assert f["countries"].iloc[-1] == len(sample)
    assert (f["countries"].shift(1).iloc[1:] - f["countries"].iloc[1:] == f["dropped"].iloc[1:]).all()
    # the repeated-zero rule removes only Brunei; Libya and Macao fail the complete-data step first
    assert f.loc[f["step"] == 4, "dropped_economies"].iloc[0] == "BRN"
    assert {"LBY", "MAC"} <= set(f.loc[f["step"] == 3, "dropped_economies"].iloc[0].split())


def test_imf_codes_are_mapped_to_world_bank_codes(panel):
    assert {"XKX", "PSE"} <= set(panel["iso3"])
    assert not {"UVK", "WBG"} & set(panel["iso3"])


def test_no_blocking_validation_failures():
    results = database.run_validation()  # raises if an 'error' check returns rows
    assert all(len(df) == 0 for meta, df in results.values() if meta.get("severity") == "error")


# --- Review flags -------------------------------------------------------------------

def test_every_flagged_row_is_exported():
    for name, (meta, df) in database.run_validation().items():
        if meta.get("severity") == "review":
            exported = pd.read_csv(config.AUDIT / "flags" / f"{name}.csv")
            assert len(exported) == len(df), name


def test_new_flags_are_unreviewed_and_old_reviews_need_the_same_vintage():
    register = validate.load_register()
    vintage = validate.source_vintage()
    new_flag = pd.DataFrame({"iso3": ["ZZZ"], "year": [E]})
    assert validate.attach_reviews("large_annual_swings", new_flag, register, vintage)["review_status"].iloc[0] == "UNREVIEWED"
    known = pd.DataFrame({"iso3": ["LBN"], "year": [2020]})
    assert validate.attach_reviews("large_annual_swings", known, register, vintage)["review_status"].iloc[0] != "UNREVIEWED"
    assert validate.attach_reviews("large_annual_swings", known, register, "Fiscal Monitor (April 2027)")["review_status"].iloc[0] == "UNREVIEWED"


# --- SQL results recomputed in pandas -------------------------------------------

def test_sql_medians_match_pandas(in_sample):
    sql = table("group_medians")
    d = in_sample.copy()
    d.loc[d["net_interest_gdp"] <= 0, "net_interest_to_debt"] = np.nan  # as in 04_analysis.sql
    for (group, year, variable), value in sql.set_index(["income_group", "year", "variable"])["median"].items():
        sub = d if group == "All countries" else d[d["income_group"] == group]
        expected = sub.loc[sub["year"] == year, variable].median()
        assert value == pytest.approx(expected, abs=1e-9), (group, year, variable)


def test_pooled_burden_is_total_over_total_and_revenue_weighted(in_sample):
    sql = table("pooled_burden").set_index(["income_group", "year"])["pooled_burden"]
    d = in_sample[in_sample["gdp_usd_bn"].notna()]
    for year in YEARS:
        y = d[d["year"] == year]
        total = 100 * (y["net_interest_gdp"] * y["gdp_usd_bn"]).sum() / (y["revenue_gdp"] * y["gdp_usd_bn"]).sum()
        revenue_weighted = np.average(y["interest_burden"], weights=y["revenue_gdp"] * y["gdp_usd_bn"])
        assert sql[("All countries", year)] == pytest.approx(total, rel=1e-9)
        assert total == pytest.approx(revenue_weighted, rel=1e-9)


def test_ranking_is_sorted_and_complete(sample):
    r = table("burden_ranking")
    assert len(r) == len(sample)
    assert r["interest_burden"].is_monotonic_decreasing


def test_social_spending_pairs_values_from_the_same_year(panel):
    s = table("interest_vs_social_spending").dropna(subset=["health_year"])
    p = panel.set_index(["iso3", "year"])["net_interest_gdp"]
    for _, r in s.iterrows():
        assert r["interest_gdp_health_year"] == pytest.approx(p[(r["iso3"], int(r["health_year"]))])


# --- Decomposition ------------------------------------------------------------------

def test_lmdi_hand_calculated_example():
    # burden 10% -> 20%: net interest/GDP 2 -> 3, revenue/GDP 20 -> 15
    out = analyze.lmdi({"ni": 2.0, "rev": 20.0}, {"ni": 3.0, "rev": 15.0},
                       {"ni_effect": ("ni", 1), "rev_effect": ("rev", -1)}, scale=100.0)
    weight = 10 / math.log(2)  # logarithmic mean of 10 and 20
    assert float(out["ni_effect"]) == pytest.approx(weight * math.log(1.5), abs=1e-12)    # 5.8496...
    assert float(out["rev_effect"]) == pytest.approx(weight * math.log(20 / 15), abs=1e-12)  # 4.1504...
    assert float(out["ni_effect"] + out["rev_effect"]) == pytest.approx(10.0, abs=1e-12)


def test_lmdi_equal_endpoints_are_finite_and_sum_to_zero():
    out = analyze.lmdi({"a": 2.0, "b": 5.0}, {"a": 4.0, "b": 10.0}, {"ea": ("a", 1), "eb": ("b", -1)})
    total = float(out["ea"] + out["eb"])
    assert np.isfinite(total) and total == pytest.approx(0.0, abs=1e-12)
    assert float(out["ea"]) == pytest.approx(0.4 * math.log(2), abs=1e-12)


@pytest.mark.parametrize("label, effects", [
    ("two_factor", ["net_interest_gdp_effect", "revenue_effect"]),
    ("three_factor", ["nid_effect", "debt_effect", "revenue_effect"]),
])
def test_decomposition_adds_up_for_every_country(label, effects):
    d = table(f"decomposition_{label}_by_country")
    assert np.allclose(d[effects].sum(axis=1), d["change"], atol=1e-9)


def test_two_and_three_factor_splits_are_consistent():
    two = table("decomposition_two_factor_by_country").set_index(["iso3", "period"])
    three = table("decomposition_three_factor_by_country").set_index(["iso3", "period"]).loc[two.index]
    assert np.allclose(two["net_interest_gdp_effect"], three["nid_effect"] + three["debt_effect"], atol=1e-9)
    assert np.allclose(two["revenue_effect"], three["revenue_effect"], atol=1e-9)


def test_decomposition_uses_only_positive_burdens():
    d = table("decomposition_three_factor_by_country")
    assert (d["burden_start"] > 0).all() and (d["burden_end"] > 0).all()


def test_dominance_counts_only_positive_largest_contributions():
    d = table("decomposition_three_factor_by_country")
    dom = table("decomposition_dominance").set_index("period")
    for period, g in d.groupby("period"):
        eff = g[["nid_effect", "debt_effect", "revenue_effect"]]
        largest_positive = ((eff.idxmax(axis=1) == "nid_effect") & (g["nid_effect"] > 0)).sum()
        largest_absolute = (eff.abs().idxmax(axis=1) == "nid_effect").sum()
        assert dom.loc[period, "largest_positive"] == largest_positive
        assert dom.loc[period, "largest_absolute"] == largest_absolute
        assert dom.loc[period, "countries"] == len(g)


def test_common_sample_uses_countries_present_in_both_periods():
    d = table("decomposition_three_factor_by_country")
    common = table("decomposition_three_factor_common_sample")
    a = set(d.loc[d["period"] == f"{config.START_YEAR}-{config.BREAK_YEAR}", "iso3"])
    b = set(d.loc[d["period"] == f"{config.BREAK_YEAR}-{E}", "iso3"])
    assert (common["countries"] == len(a & b)).all()


# --- Matched samples and regressions ---------------------------------------------

@pytest.mark.parametrize("key_, col", [("fpp", "interest_burden_gross"), ("wb", "interest_burden_wb")])
def test_matched_samples_change_one_thing_at_a_time(in_sample, key_, col):
    m = table("matched_sample_comparison")
    m = m[m["comparison"] == key_].set_index("step")
    e = in_sample[in_sample["year"] == E]
    covered = e[e[col].notna()]
    assert m.loc[1, "median_burden_end"] == pytest.approx(e["interest_burden"].median())
    assert m.loc[2, "median_burden_end"] == pytest.approx(covered["interest_burden"].median())
    assert m.loc[3, "median_burden_end"] == pytest.approx(covered[col].median())
    assert m.loc[2, "countries_level"] == m.loc[3, "countries_level"] == len(covered)


def test_log_regressions_use_only_positive_net_interest(in_sample, key):
    e = in_sample[in_sample["year"] == E]
    positive = int((e["net_interest_gdp"] > 0).sum())
    reg = table("regressions")
    assert (reg["countries"] == positive).all()
    assert key["regression"]["countries_positive"] + key["regression"]["countries_excluded_nonpositive"] == len(e)


def test_leave_one_out_range_contains_the_full_sample_fit(key):
    infl = key["influence"]
    r2 = key["regression"]["debt_only"]["r_squared"]
    assert infl["debt_only_r2_without_min"] <= r2 <= infl["debt_only_r2_without_max"]


def test_spearman_in_key_numbers_reproduces(in_sample, key):
    e = in_sample[in_sample["year"] == E]
    rho = stats.spearmanr(e["debt_gdp"], e["interest_burden"]).statistic
    assert key["correlation"]["All countries"]["spearman"] == pytest.approx(rho, abs=1e-12)


def test_bootstrap_interval_contains_estimate(key):
    c = key["correlation"]["All countries"]
    assert c["ci_low"] < c["spearman"] < c["ci_high"]


# --- Report, links and numbers ---------------------------------------------------------

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


def test_relative_links_become_public_urls():
    html = ('<a href="../research/methodology.md">x</a> <a href="#summary">y</a> '
            '<a href="https://doi.org/10.1/x">z</a> <img src="../outputs/figures/a.png">')
    out = build_report.public_links(html)
    assert f'href="{config.REPO_URL}/blob/{config.REPO_LINK_REF}/research/methodology.md"' in out
    assert 'href="#summary"' in out and 'href="https://doi.org/10.1/x"' in out
    assert 'src="../outputs/figures/a.png"' in out


def test_pdf_has_no_local_paths_or_local_links():
    pdf = config.REPORT / "economic_analysis.pdf"
    if not pdf.exists():
        pytest.skip("PDF not built (run.py --no-pdf)")
    pypdf = pytest.importorskip("pypdf")
    raw = pdf.read_bytes()
    for marker in (b"AppData", b"scratch-workspaces", b"file://", b"/Users/"):
        assert marker not in raw, marker
    uris = []
    for page in pypdf.PdfReader(str(pdf)).pages:
        for annot in page.get("/Annots") or []:
            action = annot.get_object().get("/A") or {}
            if "/URI" in action:
                uris.append(str(action["/URI"]))
    assert uris, "expected links in the PDF"
    assert all(u.startswith(("https://", "http://hdl.handle.net/")) for u in uris), uris


def test_number_comparison_uses_a_tolerance():
    assert compare_numbers.differences({"a": 1.0, "b": [2.0]}, {"a": 1.0 + 1e-12, "b": [2.0]}) == []
    assert compare_numbers.differences({"a": 1.0}, {"a": 1.01}) != []
    assert compare_numbers.differences({"a": "x"}, {"a": "y"}) != []
