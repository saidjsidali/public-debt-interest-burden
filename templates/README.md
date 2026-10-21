<!-- Generated from templates/README.md by src/build_report.py: edit the template, not this file. -->

# Public debt and interest burdens, 2015–2024

**How much government revenue goes to net interest, and what does the debt-to-GDP ratio not show?**
A reproducible analysis of {{sample/countries}} economies with SQL (SQLite) and Python, using IMF and World Bank data.

[![Reproduce analysis](https://github.com/saidjsidali/public-debt-interest-burden/actions/workflows/reproduce.yml/badge.svg)](https://github.com/saidjsidali/public-debt-interest-burden/actions/workflows/reproduce.yml)
&nbsp;**[Report (PDF)](report/economic_analysis.pdf)** · [Report (Markdown)](report/economic_analysis.md) · [Methodology](research/methodology.md) · [Data](data/README.md) · [Validation](audit/validation_report.md) · [Changes in this revision](audit/repair_register.md)

## The measure

The **net interest burden** is net interest paid by the government (interest paid minus interest received) divided by government revenue. It shows how much of the government's income goes to interest. Debt-to-GDP shows the size of the debt, not its yearly cost.

## Three findings

1. **Burdens rose in most countries, most of all in poorer ones.** The median net burden was {{median_burden/All countries/2015:.1f}}% of revenue in 2015 and {{median_burden/All countries/2024:.1f}}% in 2024. In low-income countries it rose from {{median_burden/Low income/2015:.1f}}% to {{median_burden/Low income/2024:.1f}}%. In high-income countries it fell on the net measure but was almost unchanged on a gross measure.
2. **Debt-to-GDP and interest-to-revenue often rank countries differently.** In all, {{quadrants/different_classification}} of {{sample/countries}} countries are above the median on one measure and below it on the other. Japan: debt {{country/JPN/debt_end:.0f}}% of GDP, net burden {{country/JPN/burden_end:.1f}}%. Nigeria: debt {{country/NGA/debt_end:.0f}}% of GDP, burden {{country/NGA/burden_end:.0f}}%, because revenue is only {{country/NGA/revenue_end:.0f}}% of GDP.
3. **Definitions and coverage change the numbers.** The 2024 median on the IMF gross measure is {{derived/fpp_gap_total:.1f}} points higher than the net median, but about {{derived/fpp_gap_sample_share:.0%}} of that gap comes from the smaller set of countries the gross series covers, not from the measure.

![Debt versus net burden, 2024](outputs/figures/fig4_debt_vs_burden.png)

![Median net burden by income group](outputs/figures/fig1_income_group_trend.png)

**Limits.** The results are descriptive and use one data vintage (IMF, October 2026). They do not show causes, and the burden is not a measure of default risk. Government coverage and accounting differ between countries; see [Appendix C of the report](report/economic_analysis.md#appendix-c-coverage-notes-for-highlighted-countries).

## Reproduce the results

Requires Python 3.11+ (tested with 3.14). The published results use the data snapshot in `data/raw/` (downloaded on 21 October 2026).

```bash
git clone https://github.com/saidjsidali/public-debt-interest-burden.git
cd public-debt-interest-burden
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # about 30 seconds; add --no-pdf if Chrome or Edge is not installed
pytest
```

`run.py` first checks the input files against `data/snapshot_manifest.json`, then builds the SQLite database, runs the data checks, the SQL queries and the statistics, draws the charts and writes this README and the report. After a run, `data/processed/fiscal.sqlite` contains the tables (`panel` has one row per country and year).

`python run.py --refresh` only downloads a **new** snapshot into `data/snapshots/<date>/`. It does not change the published results: a new IMF vintage needs a new review of the numbers, the flagged cases and the text. To look at a new snapshot, run `SNAPSHOT_DIR=data/snapshots/<date> python run.py` (PowerShell: `$env:SNAPSHOT_DIR="data/snapshots/<date>"; python run.py`). This is **draft mode**: it checks the new files against their own manifest and writes everything to separate files (`outputs_draft/`, `audit/draft/`, `README_draft.md`, `report/economic_analysis_draft.*`), each marked as an unreviewed draft. The published files are not changed.

**What CI checks.** On every push, GitHub Actions installs the pinned packages on Ubuntu 24.04, runs `python run.py --no-pdf` and `pytest`, compares the key numbers with the committed ones (with a small numeric tolerance) and checks that the README and Markdown report are unchanged. It does not rebuild or check the PDF; the PDF is built locally with Chrome or Edge and its links are checked by a test.

## Repository structure

```
run.py                  entry point: input check -> SQL -> checks -> statistics -> charts -> README/report
sql/                    schema, country-year panel and sample, data checks, analytical queries
src/                    Python modules (database, validate, analyze, figures, build_report, acquire, snapshot)
data/raw/               published data snapshot (tidy CSV extracts of the API responses)
data/                   README (sources, definitions, licences), data dictionary, snapshot manifest
research/               methodology, research decisions, literature notes, learning note
outputs/                tables (CSV), figures (PNG) and key_numbers.json (every number used in the text)
report/                 economic_analysis.pdf and .md
templates/              sources of this README and of the report
audit/                  validation report, reviewed cases, flagged rows, repair register
tests/                  checks on data, calculations, links and generated text
```

## Contributions

Sidali Saidj chose the research question, set the project requirements and asked for a revision after an external audit. Claude, an AI assistant made by Anthropic, did most of the data collection, SQL and Python code, charts and writing, in the first version and in this revision. The repository does not record which results the author has checked personally.

## Sources and licence

IMF Fiscal Monitor and World Economic Outlook (October 2026); IMF Public Finances in Modern History (December 2025); World Bank World Development Indicators. Details in [data/README.md](data/README.md). Code: [MIT licence](LICENSE). Data remain under the IMF's and the World Bank's terms. Fonts: Fira Sans and PT Serif (SIL Open Font License). The chart style follows common newspaper-graphics conventions; the project is not connected to any newspaper.
