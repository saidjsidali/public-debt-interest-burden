# Methodology

This file defines the measures, the sample and the methods. It is a description of the
project as it is now, written after the analysis. It is not a pre-registered plan. Choices
and changes are explained in [research_decisions.md](research_decisions.md).

## Unit, period and sample

- **Unit:** one country in one year.
- **Period:** 2015–2024. Values for 2025 are mostly IMF estimates and 2026–27 are IMF
  projections; they are shown only as context.
- **Sample:** every economy on the World Bank country list with revenue, gross debt, primary
  balance and overall balance in all ten years, and with net interest that is not exactly zero
  in five or more years. The result is 181 economies. The full selection path is in
  `outputs/tables/sample_funnel.csv` and in Table 1 of the report.
- **Income groups:** the World Bank's current classification, held fixed for all years. The
  results therefore describe the past experience of countries grouped by their *current*
  income level.

## Measures

| Measure | Formula | Notes |
|---|---|---|
| Net interest (% of GDP) | primary balance − overall balance | Interest paid minus interest received. Negative when a government receives more interest than it pays. |
| Net interest burden (%) | 100 × net interest ÷ revenue | Main measure. Both inputs are % of GDP, so GDP cancels out. |
| Gross interest burden (%) | 100 × FPP gross interest ÷ FPP revenue | Check. Different database (Dec 2025) and fewer countries. |
| Central-government burden (%) | World Bank `GC.XPN.INTP.RV.ZS` | Check. Central government only; coverage falls after 2019. |
| Net-interest-to-debt factor (%) | 100 × net interest ÷ end-year gross debt | Used only in the accounting split and in model 4. It is **not** a borrowing rate: it also moves with interest income, the timing of debt flows and valuation changes. |
| Total net interest / total revenue (%) | Σ(net interest in US$) ÷ Σ(revenue in US$) | Equal to a revenue-weighted average of country burdens. Not a GDP-weighted average. |

## Methods

| Question | Method | Output |
|---|---|---|
| How did burdens change? | Medians by income group and year; the total for all countries; counts above 20% of revenue | `group_medians.csv`, `pooled_burden.csv`, `high_burden_counts.csv` |
| What changed: net interest or revenue? | Log-mean Divisia (LMDI) split of burden = 100 × (net interest/GDP) ÷ (revenue/GDP); three-factor version in the appendix | `decomposition_*` tables |
| How do debt and burden relate? | Spearman rank correlation with a 2,000-draw bootstrap interval (seed 2026); grouping by the two medians | `correlations.csv`, `debt_burden_quadrants.csv` |
| What describes cross-country differences? | OLS on logs with HC3 standard errors, for countries with positive net interest; influence checks (Cook's distance, leverage, leave-one-country-out); a levels model on all countries | `regressions.csv`, `regression_influence.csv`, `regression_levels.csv` |
| Do definitions and coverage matter? | Medians compared on matched country sets: all countries → countries covered by the other measure → other measure on the same countries | `matched_sample_comparison.csv` |
| How sensitive are the headlines? | Excluding countries with negative net interest; excluding small states; 2025 as end year; adding Brunei | `sensitivity.csv` |

**LMDI.** For a burden B that is a product of factors, each factor's contribution to the
change from B₀ to B₁ is L(B₀, B₁) × e × ln(f₁/f₀), where L(a, b) = (b − a)/ln(b/a) and e is
the factor's exponent (+1 or −1). The contributions add up exactly to B₁ − B₀. The split
needs positive values, so it uses countries with positive net interest at both ends of a
period. It is an accounting tool: it does not show causes.

**Regressions.** The models describe the 2024 cross-section. R² is the in-sample fit for log
burdens among countries with positive net interest. Revenue is the denominator of the burden,
so a negative revenue coefficient and a better fit with revenue are partly built into the
measure.

**Case studies.** Chosen by a rule: the largest economy (2024 GDP in US dollars) in each World
Bank region, plus the three highest burdens in 2024 (`case_studies.csv`). The chart order
follows this table.

## What the design cannot show

- The causal effect of debt, revenue or interest rates on burdens.
- Whether high interest payments caused lower health or education spending.
- Default risk: the ratio ignores maturity, currency, creditors and principal repayments.
- Results for a different data vintage: the reviewed cases in `audit/` and the report text
  were written for the October 2026 IMF data.
