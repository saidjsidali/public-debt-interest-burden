# Literature notes

Short notes on the sources used in the report: what each one says and which claim in the
report it supports. Full references are at the end of the
[report](../report/economic_analysis.md#references).

| Source | What it says | Used for |
|---|---|---|
| Blanchard (2019), *American Economic Review* 109(4) — [doi:10.1257/aer.109.4.1197](https://doi.org/10.1257/aer.109.4.1197) | When the safe interest rate is below the growth rate, debt can be rolled over at a low fiscal cost. | Background: the cost of debt can differ from its size. |
| Furman and Summers (2020), Brookings/PIIE discussion draft — [PDF](https://www.brookings.edu/wp-content/uploads/2020/11/furman-summers-fiscal-reconsideration-discussion-draft.pdf) | Real interest payments relative to GDP are a better guide to fiscal space than the debt stock, in a period of low rates. | Background: looking at the yearly cost of debt. This project uses revenue instead of GDP. |
| Escolano (2010), IMF Technical Notes and Manuals 10/02 — [PDF](https://www.imf.org/external/pubs/ft/tnm/2010/tnm1002.pdf) | Standard formulas for public debt dynamics and effective interest rates. | Background for the accounting identity. Note: the project's net-interest-to-debt factor is a simpler ratio than an effective interest rate. |
| Reinhart, Rogoff and Savastano (2003), *Brookings Papers on Economic Activity* — [link](https://www.brookings.edu/articles/debt-intolerance/) | Countries with a history of default and high inflation face debt stress at lower debt levels ("debt intolerance"). | A possible reason why middle-income countries have a higher net-interest-to-debt factor. Not tested here. |
| Eichengreen and Hausmann (1999), NBER Working Paper 7418 — [link](https://www.nber.org/papers/w7418) | Many countries cannot borrow abroad in their own currency ("original sin"), which creates exchange-rate risk. | The statement that foreign-currency debt can raise interest costs when the exchange rate falls. Not tested here. |
| Kose, Nagle, Ohnsorge and Sugawara (2021), World Bank — [link](http://hdl.handle.net/10986/32809) | Describes four waves of debt in developing economies; the wave since 2010 is the largest and fastest. | Background on debt growth before 2021. |
| Mauro, Romeu, Binder and Zaman (2015), *Journal of Monetary Economics* 76 — [IMF working-paper version](https://www.imf.org/en/publications/wp/issues/2016/12/31/a-modern-history-of-fiscal-prudence-and-profligacy-40222) | The paper behind the IMF Public Finances in Modern History database. | Source of the gross-interest check. |
| Ang (2004), *Energy Policy* 32(9) — [doi:10.1016/S0301-4215(03)00076-4](https://doi.org/10.1016/S0301-4215(03)00076-4) | Compares decomposition methods and recommends the log-mean Divisia index, which has no unexplained residual. | The decomposition method. |
| IMF (2024), *Fiscal Monitor, October 2024* — [link](https://www.imf.org/en/Publications/FM/Issues/2024/10/23/fiscal-monitor-october-2024) | Global public debt is high and risks to the outlook are tilted upwards. | Policy context. |
| IMF Fiscal Monitor, Methodological and Statistical Appendix — [October 2024](https://www.imf.org/-/media/files/publications/fiscal-monitor/2024/october/english/msa.pdf) | Fiscal data for advanced economies mostly cover general government; for many developing economies only central government. Country notes (e.g. fiscal years for Pakistan and Egypt). | Coverage statements in the report and Appendix C. The full country table could not be accessed for this revision. |
| UNCTAD (2024), news release for *A World of Debt 2024* — [link](https://unctad.org/news/global-public-debt-hits-record-97-trillion-2023-un-urges-action) | 3.3 billion people live in countries that spend more on interest than on education or health care. | Comparison with the health-spending result. Years and definitions differ. |
| Moody's (2019), *Sovereign Ratings Methodology* (replaced in 2022 by a version with the same factors) — [link](https://ratings.moodys.com/api/rmc-documents/63168) | Debt affordability is measured with interest payments relative to revenue and to GDP. | The statement that rating agencies use interest-to-revenue. |

## How this project relates to the sources

The sources above discuss the cost of debt, mostly with aggregates or for advanced economies.
This project is a small, reproducible descriptive study: it calculates the net interest
burden for 181 economies from one source, shows how it differs from debt-to-GDP, and shows
how much the definition of interest and the choice of countries change the results. It does
not test the mechanisms described in the sources.
