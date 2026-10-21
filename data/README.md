# Data

All inputs come from two public APIs and were retrieved on **21 October 2026** (see
[`raw/retrieval_log.json`](raw/retrieval_log.json) for the exact timestamp, endpoints and
source vintages). The snapshot in `raw/` is what every result in this repository is computed
from. `python run.py --refresh` replaces it with the latest data.

## Sources

| Series | Code | Concept and coverage | Source and vintage |
|---|---|---|---|
| Revenue | `GGR_G01_GDP_PT` | General government revenue, % of GDP | IMF Fiscal Monitor, October 2026 |
| Gross debt | `G_XWDG_G01_GDP_PT` | General government gross debt, % of GDP | IMF Fiscal Monitor, October 2026 |
| Primary balance | `GGXONLB_G01_GDP_PT` | Overall balance excluding net interest, % of GDP | IMF Fiscal Monitor, October 2026 |
| Overall balance | `GGXCNL_G01_GDP_PT` | Net lending (+) / borrowing (−), % of GDP | IMF Fiscal Monitor, October 2026 |
| GDP | `NGDPD` | GDP at current prices, US$ billions (used only to weight aggregates) | IMF World Economic Outlook, October 2026 |
| Gross interest | `ie` | Interest paid on public debt, % of GDP (cross-check) | IMF Public Finances in Modern History, December 2025 |
| Revenue (FPP) | `rev` | Government revenue, % of GDP, used with `ie` | IMF Public Finances in Modern History, December 2025 |
| Interest / revenue | `GC.XPN.INTP.RV.ZS` | Interest payments, central government, % of revenue (cross-check) | World Bank WDI (IMF Government Finance Statistics) |
| Health spending | `SH.XPD.GHED.GD.ZS` | Domestic general government health expenditure, % of GDP | World Bank WDI (WHO Global Health Expenditure Database) |
| Education spending | `SE.XPD.TOTL.GD.ZS` | Government expenditure on education, % of GDP | World Bank WDI (UNESCO Institute for Statistics) |
| Population | `SP.POP.TOTL` | Total population | World Bank WDI |
| Country metadata | – | Region and income group (World Bank classification current at retrieval) | World Bank country API |

Endpoints: `https://www.imf.org/external/datamapper/api/v1/<code>` and
`https://api.worldbank.org/v2/country/all/indicator/<code>`.

## Files

| File | Content |
|---|---|
| `raw/imf_datamapper.csv` | All IMF series, long format: `series_code, iso3, year, value` (2010–2031, includes IMF projections and regional aggregates) |
| `raw/wb_wdi.csv` | All World Bank series, long format, 2010–2025 |
| `raw/wb_countries.csv` | 217 economies with region and income group |
| `raw/retrieval_log.json` | Retrieval time, endpoints, vintage of every series |
| `processed/panel.csv` | Country-year panel built by `sql/02_build_panel.sql` (generated) |
| `processed/sample.csv` | The 181 economies in the analysis sample (generated) |
| `processed/fiscal.sqlite` | SQLite database with all tables (generated, not committed) |
| `data_dictionary.csv` | Every variable in the panel: definition, unit, source, derivation |

## Definitions that matter

- **Net interest** = primary balance − overall balance. The primary balance excludes net
  interest, so the difference is interest paid minus interest received. It is negative for
  governments that earn more on their financial assets than they pay on their debt.
- **Interest burden** = 100 × net interest ÷ revenue (both % of GDP, so GDP cancels).
- **Implicit interest rate** = 100 × net interest ÷ gross debt (same year). An average over
  the whole debt stock, not a market yield; only computed for positive net interest.
- **General government** includes central, state and local governments and social security
  funds where the IMF has the data; coverage varies across countries (see the IMF's country
  notes). The World Bank series covers central government only, which is why its values can
  differ (the US: 20% central government against 11% general government in 2024).
- **Years**: IMF fiscal data are on each country's fiscal-year basis as reported in the
  Fiscal Monitor. Values for 2025 are partly estimates; 2026 onwards are IMF projections.

## Sample rule

Economies with revenue, gross debt, primary balance and overall balance for every year
2015–2024 and with net interest that is not recorded as exactly zero in five or more of those
years. Economies with some data that fail the rule are listed, with reasons, in
[`../audit/validation_report.md`](../audit/validation_report.md).

## Licences and reuse

- **World Bank** data are published under the
  [Creative Commons Attribution 4.0 licence](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).
- **IMF** data are subject to the [IMF's copyright and usage terms](https://www.imf.org/en/About/copyright-and-terms);
  the raw snapshot is included, with attribution, so that the analysis can be reproduced
  exactly. If you reuse it, cite the IMF as the source and check the current terms.
- The code in this repository is MIT-licensed; that licence does not cover the data.
