# Data

All inputs come from two public APIs and were downloaded on **21 October 2026**. The files in
`raw/` are the published snapshot: every result in this repository is calculated from them,
and the code never overwrites them. `snapshot_manifest.json` stores a SHA-256 checksum for
each file (line endings normalised to LF), and `run.py` stops if a file is missing or changed.

## Sources

| Series | Code | Concept | Source and vintage |
|---|---|---|---|
| Revenue | `GGR_G01_GDP_PT` | General government revenue, % of GDP | IMF Fiscal Monitor, October 2026 |
| Gross debt | `G_XWDG_G01_GDP_PT` | General government gross debt, % of GDP | IMF Fiscal Monitor, October 2026 |
| Primary balance | `GGXONLB_G01_GDP_PT` | Budget balance before net interest, % of GDP | IMF Fiscal Monitor, October 2026 |
| Overall balance | `GGXCNL_G01_GDP_PT` | Net lending (+) / borrowing (−), % of GDP | IMF Fiscal Monitor, October 2026 |
| GDP | `NGDPD` | GDP at current prices, US$ billions (only used to add up countries) | IMF World Economic Outlook, October 2026 |
| Gross interest | `ie` | Interest paid on public debt, % of GDP (check) | IMF Public Finances in Modern History, December 2025 |
| Revenue (FPP) | `rev` | Government revenue, % of GDP, used with `ie` | IMF Public Finances in Modern History, December 2025 |
| Interest / revenue | `GC.XPN.INTP.RV.ZS` | Interest payments, central government, % of revenue (check) | World Bank WDI (IMF Government Finance Statistics) |
| Health spending | `SH.XPD.GHED.GD.ZS` | Domestic general government health expenditure, % of GDP | World Bank WDI (WHO) |
| Education spending | `SE.XPD.TOTL.GD.ZS` | Government expenditure on education, % of GDP | World Bank WDI (UNESCO) |
| Population | `SP.POP.TOTL` | Total population | World Bank WDI |
| Country metadata | – | Region and income group (classification at download) | World Bank country API |

Endpoints: `https://www.imf.org/external/datamapper/api/v1/<code>` and
`https://api.worldbank.org/v2/country/all/indicator/<code>`.

## Files

| File | Content |
|---|---|
| `raw/imf_datamapper.csv` | All IMF series, long format: `series_code, iso3, year, value` (2010–2031, with IMF projections and regional groups) |
| `raw/wb_wdi.csv` | All World Bank series, long format, 2010–2025 |
| `raw/wb_countries.csv` | 217 economies with region and income group |
| `raw/retrieval_log.json` | Download time, endpoints and the vintage of each series |
| `snapshot_manifest.json` | Checksums of the four raw files |
| `processed/panel.csv` | Country-year panel built by `sql/02_build_panel.sql` (generated) |
| `processed/sample.csv` | The 181 economies in the sample (generated) |
| `processed/fiscal.sqlite` | SQLite database with all tables (generated, not committed) |
| `data_dictionary.csv` | Every panel variable: definition, unit, source, formula |

The CSV files are tidy extracts made from the API responses. The original JSON responses were
not kept for this snapshot. New downloads (`python run.py --refresh`) go to
`data/snapshots/<date>/` and keep the JSON responses, a retrieval log and a manifest
(`data/snapshots/` is not committed). A new snapshot can be analysed in draft mode with
`SNAPSHOT_DIR=data/snapshots/<date> python run.py`: the files are checked against that
snapshot's own `manifest.json`, and all outputs go to separate draft files (`data/processed_draft/`,
`outputs_draft/`, `audit/draft/`, `README_draft.md`, `report/economic_analysis_draft.*`). The
published results change only if `data/raw/` and `data/snapshot_manifest.json` are replaced on
purpose, after a new review of the flagged cases (`audit/reviewed_cases.csv`) and of the report text.

## Definitions that matter

- **Net interest** = primary balance − overall balance: interest paid minus interest received.
  It is negative when a government receives more interest than it pays. A negative flow does
  not by itself show that the government has more assets than debts.
- **Net interest burden** = 100 × net interest ÷ revenue.
- **Net-interest-to-debt factor** = 100 × net interest ÷ end-year gross debt. An accounting
  ratio used in the decomposition, not a borrowing rate.
- **Coverage.** The series are labelled general government, but the IMF notes that data for
  many emerging and developing economies cover only central or budgetary central government.
  The World Bank series covers central government only, so it can differ a lot (the United
  States: about 20% of revenue on that series against about 11% on the net general-government
  measure in 2024).
- **Gross versus net.** The gross and net burdens come from two IMF databases with different
  vintages and revenue figures. Their difference is not a direct measure of interest income.
- **Years.** IMF fiscal data follow each country's reporting basis; some countries (for example
  Pakistan and Egypt) report fiscal years. Years up to 2024 may include IMF staff estimates;
  2025 is mostly estimates; 2026 onwards are projections.

## Licences and reuse

- **World Bank** data: [Creative Commons Attribution 4.0](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).
- **IMF** data: [IMF copyright and usage terms](https://www.imf.org/en/About/copyright-and-terms).
  The snapshot is included with attribution so that the results can be reproduced. If you reuse
  it, cite the IMF and check the current terms.
- The MIT licence of the code does not cover the data.
