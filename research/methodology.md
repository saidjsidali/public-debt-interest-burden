# Methodology

Written before the main results were computed. Changes made after looking at
the data are logged in [research_decisions.md](research_decisions.md).

## Unit of observation and coverage

- **Unit:** country-year, general government.
- **Study window:** 2015–2024. The October 2026 Fiscal Monitor reports
  outturns for most countries up to 2024. Values for 2025 (partly estimates)
  and 2026–27 (IMF projections) are shown only as context and are always
  labelled as such.
- **Sample:** every economy on the World Bank country list with revenue, gross
  debt, primary balance and overall balance in all ten years, excluding
  economies whose net interest is recorded as exactly zero in five or more
  years (interest not separately identified). Income groups are the World
  Bank's current classification, held fixed over time so that group
  composition does not change.

## Measures

**Primary measure: net interest burden (general government)**

```
net interest (% GDP)  = primary balance (% GDP) − overall balance (% GDP)
interest burden (%)   = 100 × net interest / revenue
```

The primary balance excludes net interest, so the gap between the two
balances is net interest paid. All three inputs come from the same Fiscal
Monitor vintage, which keeps the burden consistent with the debt and revenue
series used alongside it.

**Cross-checks**

| Measure | Coverage | Concept | Source |
|---|---|---|---|
| Gross interest ÷ revenue | 151 economies, to 2024 | Gross interest, general government | IMF Public Finances in Modern History |
| `GC.XPN.INTP.RV.ZS` | ~90–140 economies, falling over time | Gross interest, central government | World Bank WDI (IMF GFS) |

Net and gross interest differ when governments hold large financial assets
(net interest is lower or negative). This mainly affects a few high-income
economies, so results for that group are reported on both bases.

## The accounting framework

The burden is the product of three terms:

```
interest / revenue  =  (interest / debt)  ×  (debt / GDP)  ÷  (revenue / GDP)
       burden       =   implicit rate     ×   debt ratio   ÷  revenue ratio
```

The implicit rate is net interest divided by the end-year gross debt stock.
It is an average over the whole debt stock, so it moves more slowly than
market yields. Because the identity is exact, changes in the burden can be
split exactly into the contributions of the three terms.

**Decomposition.** For each country with a positive burden at both ends of a
period, the change is split with the log-mean Divisia index (LMDI-I; Ang,
2004):

```
Δburden = L × [Δln(rate) + Δln(debt) − Δln(revenue)],   L = (B₁ − B₀) / (ln B₁ − ln B₀)
```

Each contribution is in percentage points of revenue, and they add up exactly
to the observed change. Periods: 2015–2021 (low rates, pandemic borrowing) and
2021–2024 (tightening). Group results are means of country contributions
(means preserve additivity), with medians reported as a check.

## Statistical methods

| Question | Method |
|---|---|
| Level and trend | Median by income group and year (the typical country); GDP-weighted aggregate (the share of all revenue in the sample, in US dollars) |
| Debt vs burden (H2) | Spearman rank correlation in 2024, with a 95% bootstrap interval (2,000 resamples, seed 2026), overall and within income groups |
| Explaining burdens (H2, H3) | Cross-section OLS of log burden on log debt, then adding log revenue and income-group dummies; HC3 robust standard errors; countries with positive net interest |
| Borrowing costs (H3) | OLS of log implicit rate on log debt and income-group dummies |
| Typology | Countries classified by whether debt and burden are above or below the 2024 sample medians |
| Drivers (H4) | LMDI decomposition, as above |

Medians are used for the typical country because the distribution of burdens
is strongly right-skewed. The regressions describe associations across
countries. They do not identify causal effects: debt, revenue and borrowing
costs are determined jointly by institutions, history and shocks that the
data do not measure.

## Case studies (selection rule fixed in advance)

To avoid picking countries for dramatic results, case studies are chosen by
rule: the largest economy (2024 GDP in US dollars) in each of the seven World
Bank regions, plus the three economies with the highest burden in 2024.

## Robustness checks

1. Gross instead of net interest (FPP), and the World Bank central-government series.
2. Excluding governments with negative net interest (net creditors).
3. Excluding small states (population below 1.5 million).
4. Using the 2025 estimate instead of 2024 as the end year.
5. Pearson instead of Spearman correlation, and excluding the top and bottom 5% of burdens.
6. Decomposition summarised by medians instead of means.

## What this design cannot establish

- Whether high interest burdens *cause* cuts in health or education spending.
  Comparisons of interest with social spending are descriptive.
- Default risk. An interest-to-revenue ratio says nothing about debt maturity,
  currency composition, the investor base or institutional credibility, all of
  which matter for sustainability.
- Effects inside a year or below the general-government level.
