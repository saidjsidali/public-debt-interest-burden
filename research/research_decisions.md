# Research decisions

The important choices in this project, and why they were made. This is a retrospective
record. All decisions were made by Claude (an AI assistant) while building the project at the
author's request, on 21 October 2026. The Git history does not record the order in which they
were made.

**Order of work in the first version.** Data coverage, the agreement between net and gross
measures and the 2024 ranking were checked first. The hypotheses and the case-study rule were
written after that, but before the correlations, regressions and decomposition were run. This
order is stated for transparency; it cannot be verified from the repository.

## First version

| # | Decision | Reason |
|---|---|---|
| D1 | Use net interest from the IMF Fiscal Monitor as the main measure, not the World Bank series named in the project brief | The World Bank series covers 142 economies in 2015 but only 91 in 2024, and misses Egypt, Pakistan and Sri Lanka in 2024. The Fiscal Monitor gives a balanced panel and uses the same vintage for debt and revenue. |
| D2 | Keep two gross-interest series as checks | Net and gross burdens differ for governments with large interest income. |
| D3 | Remove countries whose net interest is exactly zero in five or more of ten years | Repeated exact zeros may mean that interest is not recorded separately. Only Brunei is removed by this rule (Libya and Macao fail the complete-data rule first). Five years is half of the period. |
| D4 | End the study in 2024 | 2025 values are mostly estimates and the gross-interest checks stop in 2024. 2025 is a sensitivity check. |
| D5 | Hold income groups fixed at the current classification | Group membership stays the same over time. |
| D6 | Use SQLite | It ships with Python, so no database server is needed. |
| D7 | Keep Kiribati and Tuvalu although their revenue is above 100% of GDP | The values are plausible for these economies (not verified in IMF documents); both are removed in the small-states check. |
| D8 | Do not compute the net-interest-to-debt factor when net interest is not positive | A negative value has no useful meaning (Kuwait's would be −853%). |
| D9 | Choose case studies by a fixed rule | To avoid choosing countries because their results are striking. Japan is discussed because it is the clearest example of high debt with a low net burden. |
| D10 | Keep the original wording of hypothesis H2 | H2 predicted a "weak" relationship; the result is moderate, and the verdict says so. |

## This revision (after an external audit)

| # | Decision | Reason |
|---|---|---|
| R1 | Rename `implicit_rate` to `net_interest_to_debt` and stop describing it as a borrowing rate | It uses net interest and gross debt, so it also moves with interest income, timing and valuation. |
| R2 | Put a two-factor split (net interest/GDP and revenue/GDP) in the main report and move the three-factor split to the appendix | The two-factor split needs no constructed rate. |
| R3 | Report the sample of each decomposition period and add a common-sample check | Period samples differ (166, 170 and 169 countries). |
| R4 | Define the dominance statistic as "largest positive contribution" and also report "largest in absolute size" | The old code counted the largest signed value, which included two negative contributions. |
| R5 | Correct the robustness note with matched-sample comparisons | The old note said the measure explained most of the gap between the net and FPP medians; the matched comparison shows that country coverage explains most of it. |
| R6 | Keep Canada in the regressions and add influence checks and a levels model | Canada's near-zero net burden has a large influence on log models. Removing it only to improve the fit would not be justified. |
| R7 | Remove claims that revenue is the "strongest lever" and that higher interest rates "did the damage" | The accounting identity does not rank policies or identify causes. |
| R8 | Call the total burden "total net interest as a share of total revenue" | It is a revenue-weighted average, not a GDP-weighted average. |
| R9 | Pair India's interest and health spending in the same year (2023) | The old text paired 2024 interest with 2023 health spending. |
| R10 | Separate automatic flags from reviewed explanations | Old explanations were hard-coded and would have been applied to new data automatically. |
| R11 | Never overwrite the published snapshot; add a checksum manifest | Reproducing the published results and updating the data are different tasks. |
| R12 | Rewrite PDF links to public GitHub URLs | The old PDF linked to a folder on the computer that built it. |
| R13 | Replace "net creditor" with a description of the flow | A negative interest flow does not prove that assets exceed debts. |
| R14 | Mark the coverage table and the Brunei, Lao PDR and default cases as unresolved | IMF country documentation could not be accessed (Access Denied), and claims were not invented. |
| R15 | Change the chart style to a newspaper style (serif headlines, grey grid, left value labels) | Requested by the author. No newspaper names or logos are used. |
