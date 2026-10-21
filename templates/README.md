<!-- Generated from templates/README.md by src/build_report.py: edit the template, not this file. -->

# The cost of public debt

**How much government revenue goes to interest, and is debt-to-GDP a reliable guide to who is under pressure?**
A reproducible cross-country analysis of {{sample/countries}} economies, 2015–2024, using SQL and Python.

[![Reproduce analysis](https://github.com/saidjsidali/public-debt-interest-burden/actions/workflows/reproduce.yml/badge.svg)](https://github.com/saidjsidali/public-debt-interest-burden/actions/workflows/reproduce.yml)
&nbsp;**[Read the report (PDF)](report/economic_analysis.pdf)** · [Report on GitHub](report/economic_analysis.md) · [Methodology](research/methodology.md) · [Data sources](data/README.md) · [Validation](audit/validation_report.md) · [Reproduce](#reproduce-the-analysis)

## Why it matters

Interest is the one budget item a government cannot cut without a default or a renegotiation. The share of revenue it absorbs shows how much of a government's income is committed before any other spending decision. That share was pushed up after 2021 by pandemic-era debt and the fastest rise in interest rates in decades. Rating agencies use the ratio to judge debt affordability. Finance ministries, debt managers and international lenders need to know where the pressure is, and whether the usual yardstick, debt-to-GDP, finds it.

## Key findings

- **Interest takes a growing share of revenue.** The median government spent **{{median_burden/All countries/2024:.1f}}%** of revenue on net interest in 2024, against {{median_burden/All countries/2015:.1f}}% in 2015. Across all {{sample/countries}} economies, net interest rose from {{aggregate_burden/All countries/2021:.1f}}% of total revenue in 2021 to {{aggregate_burden/All countries/2024:.1f}}% in 2024, about **${{net_interest_usd_trn/2024:.1f}}trn**.
- **The load has shifted to poorer countries.** The median burden rose from {{median_burden/Low income/2015:.1f}}% to **{{median_burden/Low income/2024:.1f}}%** in low-income economies, while in high-income ones it fell from {{median_burden/High income/2015:.1f}}% to {{median_burden/High income/2024:.1f}}% (roughly flat on a gross-interest basis). In 2024, {{high_burden/countries/2024}} governments ruling {{high_burden/population_bn/2024:.1f}}bn people spent more than a fifth of revenue on interest; Pakistan, Egypt and Sri Lanka spent more than half.
- **Debt-to-GDP is only a partial guide.** It explains about a quarter of cross-country differences in burdens (R² {{regression/debt_only/r_squared:.2f}}). Adding revenue raises this to {{regression/debt_with_revenue/r_squared:.2f}}. Japan ({{country/JPN/debt_end:.0f}}% debt, {{country/JPN/burden_end:.1f}}% net burden) and Nigeria ({{country/NGA/debt_end:.0f}}% debt, {{country/NGA/burden_end:.0f}}% burden) sit at opposite corners.
- **Since 2021, higher interest rates did the damage.** For the average country the burden rose {{decomposition/All countries/2021-2024/mean_change:.1f}} points between 2021 and 2024: higher implicit rates added {{decomposition/All countries/2021-2024/mean_rate_effect:.1f}}, while falling debt ratios and rising revenue offset about half of that. Before 2021, debt accumulation was the driver.
- **Interest competes with health.** In {{social_spending/countries_interest_gt_health}} countries, home to {{social_spending/population_interest_gt_health_bn:.1f}}bn people, governments pay more in net interest than they spend on health.

![Debt versus interest burden, 2024](outputs/figures/fig4_debt_vs_burden.png)

![Median burden by income group](outputs/figures/fig2_median_burden_by_income.png)

## What this means

- Watch **affordability (interest/revenue), not just the debt stock**. A rule based only on debt-to-GDP flags Japan and misses Nigeria and Bangladesh.
- For the most burdened economies, **revenue is the strongest lever**: the burden is inversely proportional to the revenue ratio, so raising revenue from 12% to 15% of GDP cuts it by a fifth at unchanged debt.
- **Debt structure decides how fast rate shocks arrive.** Longer maturities and less short-term and foreign-currency debt slow the pass-through.
- **A falling burden is not always good news.** Lebanon's dropped from {{country/LBN/burden_start:.0f}}% to {{country/LBN/burden_end:.0f}}% because it defaulted.

These follow from the accounting identity and the cross-country patterns; they are not estimated policy effects. See the [limitations](report/economic_analysis.md#7-limitations).

## Data and method

| | |
|---|---|
| **Measure** | Net interest (primary balance minus overall balance) as % of general-government revenue |
| **Main source** | IMF Fiscal Monitor, October 2026 (revenue, gross debt, primary and overall balance) |
| **Cross-checks** | Gross interest from the IMF Public Finances in Modern History database; World Bank `GC.XPN.INTP.RV.ZS` (central government) |
| **Context** | World Bank income groups, regions, population, health and education spending; IMF WEO GDP in US dollars |
| **Sample** | {{sample/countries}} economies with complete data for 2015–2024 (balanced panel); 2025 estimates and 2026–27 IMF forecasts shown as context |
| **Methods** | Medians and GDP-weighted aggregates; Spearman correlation with bootstrap interval; log-log OLS with HC3 errors; exact log-mean Divisia decomposition of burden = implicit rate × debt ÷ revenue |
| **Tools** | SQLite (data integration, validation, aggregation, window-function medians) and Python (pandas, statsmodels, matplotlib) |

The burden identity, the hypotheses and the case-study selection rule were written down before the main results were computed ([methodology](research/methodology.md)); later changes are logged in [research decisions](research/research_decisions.md).

**Limitations.** These are cross-country associations, not causal effects. Net interest understates the cash cost for governments with large financial assets, which is why gross measures are reported alongside. The ratio ignores maturity, currency and principal repayments, so it is not a measure of default risk.

## Reproduce the analysis

Requires Python 3.11+ (tested with 3.14). Every table, figure and number in the report is regenerated from the data snapshot in `data/raw/`.

```bash
git clone https://github.com/saidjsidali/public-debt-interest-burden.git
cd public-debt-interest-burden
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # ~1 minute; add --no-pdf if Chrome/Edge is not installed
pytest                           # data-quality and consistency tests
```

`python run.py --refresh` downloads the latest IMF and World Bank data instead of using the snapshot. Expect the numbers to change when the IMF publishes a new vintage (April and October).

To query the data yourself, open `data/processed/fiscal.sqlite` after a run: the `panel` table has one row per country and year.

## Repository structure

```
├── run.py                     single entry point: data → SQL → checks → statistics → figures → report
├── sql/
│   ├── 01_schema.sql          tables and keys for the raw observations
│   ├── 02_build_panel.sql     pivot to a country-year panel, derive indicators, define the sample
│   ├── 03_validation.sql      data-quality checks (blocking and review)
│   └── 04_analysis.sql        rankings, medians, aggregates, quadrants, social-spending comparison
├── src/                       Python: acquire, database, validate, analyze, figures, style, build_report
├── data/
│   ├── raw/                   frozen API snapshot (October 2026) and retrieval log
│   ├── data_dictionary.csv    every variable, unit and source
│   └── README.md              sources, licences, definitions
├── research/                  problem statement, literature review, methodology, decisions, reasoning journal
├── outputs/
│   ├── figures/               eight charts
│   ├── tables/                every result table (CSV)
│   └── key_numbers.json       every number quoted in the report and this README
├── report/                    economic_analysis.pdf and .md
├── templates/                 sources for this README and the report
├── audit/                     generated validation report and review log
└── tests/                     pytest checks on data integrity and internal consistency
```

## Sources and citation

IMF Fiscal Monitor and World Economic Outlook (October 2026); IMF Public Finances in Modern History (December 2025); World Bank World Development Indicators (October 2026). Full references and licences are in [data/README.md](data/README.md). To cite this work, use the "Cite this repository" button (from [CITATION.cff](CITATION.cff)).

Code is released under the [MIT licence](LICENSE). Data remain subject to the IMF's and the World Bank's terms of use. Charts use Fira Sans (SIL Open Font Licence) and follow The Economist's published chart conventions; they are not affiliated with The Economist.

## About

Analysis, code and report by Sidali Saidj, October 2026. Every number and chart is generated by the scripts in this repository from the official sources listed, and can be checked by running `python run.py`.
