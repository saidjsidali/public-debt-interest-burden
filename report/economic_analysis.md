<!-- Generated from templates/economic_analysis.md by src/build_report.py. Edit the template, not this file. -->

<div class="masthead" markdown="1">

# Public debt and interest burdens, 2015–2024

<p class="standfirst">How much government revenue goes to net interest in 181 economies, and what the debt-to-GDP ratio does not show</p>

<p class="byline">Sidali Saidj · Revised October 2026 · Data: IMF Fiscal Monitor (October 2026), IMF Public Finances in Modern History (December 2025), World Bank · Prepared with substantial help from Claude, an AI assistant (see Contributions)</p>

</div>

## Summary

**Questions.** (1) How did net interest burdens change between 2015 and 2024? (2) How do the debt-to-GDP ratio and the interest-to-revenue ratio describe countries differently? (3) How do the definition of interest and the choice of countries change the picture?

**Measure.** The *net interest burden* is net interest paid by the government divided by government revenue, in percent. Net interest is interest paid minus interest received. Data come from the IMF Fiscal Monitor for 181 economies with complete data for 2015–2024. Two gross-interest series are used as checks.

**Main findings**

1. **Burdens rose in most countries, and most in poorer ones.** The median net burden was 4.5% of revenue in 2015 and 5.8% in 2024; it rose in 113 of 181 countries. In low-income countries the median rose from 3.6% to 8.4%. In high-income countries it fell from 4.0% to 2.3% on the net measure, but it was almost unchanged on a gross measure (4.8% and 4.6%). For all countries together, total net interest was 4.9% of total revenue in 2021 and 6.4% in 2024.
2. **Debt-to-GDP and interest-to-revenue often rank countries differently.** The two measures are clearly related (Spearman rank correlation 0.53), but 52 of 181 countries (29%) are above the median on one measure and below it on the other. Japan has very high debt and a very low net burden; Nigeria has moderate debt and a high burden because its revenue is low.
3. **Definitions and coverage matter.** Net and gross burdens are close for most countries, but not for governments with large interest income, such as Canada. When the net and gross medians are compared, most of the difference for the IMF gross series comes from the smaller set of countries it covers (+1.1 points), not from the measure itself (+0.4 points).

**Limits.** These are descriptive results for one data vintage. They do not show causes, and the burden is not a measure of default risk. Fiscal coverage and accounting rules differ between countries.

## 1. The question and the measure

### 1.1 Why compare interest with revenue?

Debt-to-GDP measures the *stock* of debt. It does not show what the debt costs each year or how easily the government can pay that cost. Interest compared with revenue does this: it shows how much of the government's income goes to interest. Interest payments are contractual obligations, so they can limit the room for other spending. They are not completely fixed, however: the interest bill changes when debt is repaid or refinanced, when floating rates change and, for the net measure, when interest income changes. Credit-rating agencies use the interest-to-revenue ratio; for example, Moody's 2019 sovereign methodology uses it as a measure of "debt affordability" (Moody's, 2019).

### 1.2 Net and gross interest

<p class="equation">net interest burden (%) = 100 × (primary balance − overall balance) ÷ revenue</p>

The primary balance is the budget balance before net interest, so the difference between the two balances is net interest. All three series come from the same Fiscal Monitor vintage.

*Gross* interest is the interest the government pays before interest income is subtracted. The two measures can be very different for governments with large financial assets. In 2024, Canada's net burden was 0.01% of revenue but its gross burden (IMF Public Finances in Modern History, "FPP") was 8.3%. For Japan the figures were 0.3% and 4.0%. A low net burden therefore does not mean a low gross interest bill. In 6 sample countries net interest was negative in 2024: they received more interest than they paid. This flow alone does not show that their governments hold more assets than debts, so the report does not call them "net creditors".

The report uses the net measure as its main measure because it covers more countries and comes from the same source as the debt and revenue data. Gross results are shown where they change the interpretation.

## 2. Data and sample

**Sources.** Revenue, gross debt and the two budget balances come from the IMF Fiscal Monitor (October 2026); GDP in US dollars from the World Economic Outlook (October 2026). Gross interest and FPP revenue come from the IMF Public Finances in Modern History database (December 2025). The World Bank provides central-government interest payments (`GC.XPN.INTP.RV.ZS`), health and education spending, population, regions and income groups. All data were downloaded on 21 October 2026 and are kept in the repository; a checksum file confirms that they have not changed.

**Sample.** A country is included if it has all four fiscal series in every year from 2015 to 2024. A balanced panel keeps the same countries in every year, but it may leave out countries with weaker statistics.

<p class="table-label">Table 1. From the World Bank country list to the analysis sample</p>

| Step | Countries | Removed | Removed economies |
|---|---|---|---|
| Economies on the World Bank country list | 217 | | |
| With at least one year of Fiscal Monitor revenue data, 2015-2024 | 193 | 24 | Mostly territories and small economies without IMF fiscal data (full list in `outputs/tables/sample_funnel.csv`) |
| With revenue, gross debt and both balances in all ten years | 182 | 11 | ERI LBY MAC NRU PLW SGP SOM TKM VEN WSM YEM |
| Net interest not exactly zero in five or more years | 181 | 1 | BRN |
| With a World Bank income group (final sample) | 181 | 0 | |

<p class="table-note">Brunei has complete data but net interest of exactly zero in every year. It is unclear whether interest is not recorded separately or is really zero, so this case is unresolved; adding it back gives a 2024 median of 5.80% instead of 5.83% (Appendix A). Libya and Macao also show repeated zeros, but they already fail the complete-data step.</p>

**Coverage.** The IMF notes that fiscal data for most advanced economies cover general government, while data for many emerging and developing economies cover only central or budgetary central government (IMF Fiscal Monitor methodological appendix). Some countries report on fiscal years: for example Pakistan and Egypt. India's data cover central and state governments. Appendix C lists what could be documented for the countries named in this report.

**Other choices.** Income groups are the World Bank's current classification, used for all years: the results describe the past experience of countries grouped by their current status. Years up to 2024 are treated as past data, but the IMF may still use staff estimates for some of them; 2025 values are mostly estimates and 2026–27 are IMF projections, shown only as context.

## 3. How did net interest burdens change?

<p class="fig-label">Figure 1</p>

![Median net burden by income group](../outputs/figures/fig1_income_group_trend.png)

The median net burden of all countries rose from 4.5% of revenue in 2015 to 5.4% in 2021 and 5.8% in 2024. The rise was spread over the whole period, not only after 2021. It was largest in low-income countries (3.6% to 8.4%) and lower-middle-income countries (4.3% to 7.9%) (Figure 1).

The high-income median fell on the net measure, from 4.0% to 2.3%. On the gross measure it was almost unchanged (4.8%, 3.3% and 4.6% in 2015, 2021 and 2024). So part of the fall reflects more interest income, not a lower interest bill. The gross series covers fewer countries (149 of 181), so this comparison is indicative.

<p class="fig-label">Figure 2</p>

![Total net interest and number of high-burden countries](../outputs/figures/fig2_pooled_and_count.png)

Total net interest as a share of total revenue across all countries was stable at 4.9% in 2015 and 4.9% in 2021, then rose to 6.4% in 2024 (Figure 2). This total is calculated after converting both values to US dollars. It equals an average of country burdens weighted by revenue, so large economies such as the United States dominate it. It is not a GDP-weighted average of country burdens, which would be 7.5% in 2024. In dollars, total net interest was about $2.24trn in 2024, against $1.55trn in 2021 (nominal, at market exchange rates). The number of countries with a net burden above 20% of revenue rose from 12 in 2015 to 20 in 2024. The 20% line is a simple descriptive threshold, not a risk limit.

**What changed: net interest or revenue?** The burden equals net interest/GDP divided by revenue/GDP, so a change in the burden can be split exactly into these two parts (log-mean Divisia method; Appendix A). The split uses countries with positive net interest at the start and end of each period.

<p class="table-label">Table 2. Contributions to the change in the net burden, percentage points, average country</p>

| Period | Countries | Change in burden | From net interest/GDP | From revenue/GDP |
|---|---|---|---|---|
| 2015–2021 | 166 | +1.46 | +1.31 | +0.16 |
| 2021–2024 | 170 | +1.00 | +1.56 | -0.56 |

<p class="table-note">A negative revenue contribution means that revenue rose as a share of GDP. On the 165 countries present in both periods the pattern is the same (Appendix A). Medians are smaller than means: see <code>outputs/tables/decomposition_two_factor_by_group.csv</code>.</p>

In both periods the average burden rose because net interest grew faster than GDP. After 2021, higher revenue offset part of this (-0.6 points). Appendix A splits net interest/GDP further into a *net-interest-to-debt factor* (net interest divided by gross debt) and the debt ratio. Between 2021 and 2024 this factor made the largest positive contribution on average (+2.0 points), while falling debt ratios reduced the burden (-0.5 points). The factor was the largest positive contribution in 121 of 170 countries. This pattern is consistent with the rise in interest rates after 2021. However, the factor is not a borrowing rate: it also changes with interest income on assets, the timing of debt flows and valuation changes. The split is accounting, so it cannot measure how much higher policy rates caused.

## 4. How do debt-to-GDP and interest-to-revenue describe countries differently?

<p class="fig-label">Figure 3</p>

![Highest net burdens in 2024 with debt ratios](../outputs/figures/fig3_highest_burdens.png)

In 2024, 20 countries had a net burden above 20% of revenue (Figure 3). Pakistan (61.3%), Egypt (55.8%) and Sri Lanka (55.6%) were above 50%. Of the top 20, 14 are low- or lower-middle-income countries. Their debt ratios vary a lot: from 39% of GDP (Nigeria) to 136% (Senegal).

<p class="fig-label">Figure 4</p>

![Debt versus net burden](../outputs/figures/fig4_debt_vs_burden.png)

Countries with more debt tend to have higher burdens: the Spearman rank correlation is 0.53 (95% bootstrap interval 0.41 to 0.65). The relationship is far from exact (Figure 4). Of the 181 countries, 26 have above-median debt but a below-median burden; 62% of them are high-income. Another 26 have below-median debt but an above-median burden; 65% of them are low- or lower-middle-income. Japan's debt is 214% of GDP and its net burden 0.3% (gross 4.0%). Nigeria's debt is 39% of GDP, but its burden is 23% because revenue is only 11% of GDP. Bangladesh is similar (debt 41%, revenue 8.3%, burden 28%).

**Regressions.** Table 3 describes the 2024 cross-section with ordinary least squares on logarithms. Logarithms need positive values, so the models use the 175 countries with positive net interest; 6 countries are left out.

<p class="table-label">Table 3. Cross-country regressions, 2024 (95% confidence intervals in brackets)</p>

| | (1) Debt only | (2) Debt and revenue | (3) Adding income group |
|---|---|---|---|
| Dependent variable | log net burden | log net burden | log net burden |
| log debt/GDP | 1.12 [0.74, 1.50] | 1.01 [0.61, 1.40] | 1.07 [0.71, 1.43] |
| log revenue/GDP | | -1.32 [-1.91, -0.73] | -1.28 [-1.85, -0.70] |
| R² | 0.25 | 0.48 | 0.54 |
| R² range when one country is left out | 0.22–0.32 | 0.46–0.56 | |
| Countries | 175 | 175 | 175 |

<p class="table-note">Heteroskedasticity-robust (HC3) standard errors. R² is the in-sample fit for log burdens among countries with positive net interest in 2024. It is not the share of variation in burdens explained for all 181 countries, and it is not a forecast accuracy. Full results: <a href="../outputs/tables/regressions.csv">regressions.csv</a>, <a href="../outputs/tables/regression_influence.csv">regression_influence.csv</a>.</p>

In model 1, debt explains 25% of the variation in log burdens. This number depends on a few countries. Japan and Canada have the largest influence (Cook's distance 0.28 and 0.25). Canada's net burden is close to zero (0.014% of revenue), so its logarithm is extreme. Without Canada, R² is 0.32; leaving out any single country gives values between 0.22 and 0.32. Canada stays in the main results: it is a valid observation, and removing it only to improve the fit would not be justified. A model in levels that keeps all 181 countries, including those with negative net interest, gives R² = 0.32, a debt coefficient of 0.079 (-0.004 to 0.161) and a revenue coefficient of -0.35 (-0.48 to -0.21).

Adding revenue raises R² to 0.48. This is partly built into the measure: revenue is the denominator of the burden, so a negative coefficient on revenue is expected by construction. The result shows that low revenue and high burdens go together at similar debt levels. It does not show which policy would lower burdens most.

A fourth model (Appendix A) relates the net-interest-to-debt factor to debt and income group. Its debt coefficient is 0.10 (95% interval -0.26 to 0.46): the model cannot estimate this relationship precisely. At similar debt, the factor is about 2.2 times higher in upper-middle-income countries and 1.9 times higher in lower-middle-income countries than in high-income countries. For low-income countries the estimate (1.4 times) is imprecise.

## 5. How do definitions and coverage change the picture?

<p class="fig-label">Figure 5</p>

![Sample and measure effects on the median](../outputs/figures/fig5_sample_vs_measure.png)

The gross FPP median in 2024 (7.4%) is 1.5 points higher than the net median for all countries (5.8%). Figure 5 changes one thing at a time. First, the net median on the same 149 countries that FPP covers is 7.0% (+1.1 points). Second, the gross measure on those countries is 7.4% (+0.4 points). So about 74% of the difference comes from country coverage. The World Bank central-government series shows a different pattern: its 88 countries have a *lower* net median (5.4%, -0.4 points), and its measure is higher (6.2%, +0.8 points); central-government coverage is one possible reason. These are descriptive comparisons of medians, not a causal split.

Across the 149 countries with both values, the net and gross burdens have a rank correlation of 0.96, and 81% differ by 2 points or less (Appendix B, Figure A3). Larger differences can come from interest income, but also from different revenue figures, coverage, accounting and data vintages in the two IMF databases, so they are not a direct measure of interest income.

<p class="fig-label">Figure 6</p>

![Country cases](../outputs/figures/fig6_country_cases.png)

Among the largest economies (Figure 6), the net burden rose in the United States (5.8% to 10.7%), China (1.8% to 3.7%) and South Africa (11.4% to 18.9%). It fell in Germany (2.4% to 1.7%) and Brazil (22.8% to 15.1%; Brazil's gross FPP burden was 21.0% in 2024). India's stayed close to 23%. Saudi Arabia moved from negative net interest to a small positive burden. Among the three highest burdens, Egypt's is projected by the IMF to reach 88% in 2026. Sri Lanka's peaked at 80% in 2023 and was 56% in 2024.

**Falling burdens after a default.** Measured burdens fell sharply in Lebanon (2020), Ghana (2023) and Sri Lanka (2024), around default or debt restructuring. The data alone do not show whether this reflects interest that was not paid, the accounting treatment of the restructured debt or other changes; this was not checked in country documents. A lower measured burden does not by itself mean that debt became sustainable.

## 6. Interest and health spending

Net interest was larger than government health spending in 45 of the 177 countries with data (Appendix B, Figure A2). Each comparison uses the same year for both values: 169 countries use 2023, 7 use 2024 and 1 uses 2021. These countries had 3.7bn people in 2024. For example, in 2023 India's net interest was 5.29% of GDP and its government health spending 1.30%. For education, net interest was larger in 26 of 169 countries (2.8bn people); education data are older for many countries (2019–2024). UNCTAD (2024) reported a similar order of magnitude with different data: 3.3 billion people in countries that spend more on interest than on education or health care.

This comparison is descriptive. It does not show that interest payments caused lower health spending. Low revenue could explain both a high interest burden and low health spending; this was not tested.

## 7. Limitations

- **Descriptive, not causal.** The results describe patterns. They do not identify the effect of debt, revenue or interest rates.
- **One data vintage.** IMF data are revised twice a year. The results apply to the October 2026 Fiscal Monitor.
- **Net interest.** The net measure is lower than the gross interest bill when governments earn interest. Gross data cover fewer countries and come from a different database.
- **Coverage and accounting.** Government coverage, fiscal years and accounting rules differ by country, and some values are IMF estimates.
- **Not a default-risk measure.** The ratio says nothing about debt maturity, currency, creditors or principal repayments.
- **Small groups.** Only 20 low-income countries are in the sample, so their estimates are less precise.

## 8. What the results suggest

These points follow from the measures and patterns above. None is an estimated effect of a policy.

1. **Look at both indicators.** Debt-to-GDP and interest-to-revenue answer different questions. Using only debt-to-GDP would flag Japan and miss Nigeria and Bangladesh.
2. **Low revenue goes with high burdens.** At similar debt levels, countries with low revenue tend to have higher burdens. As an illustration, if the interest bill stays the same, raising revenue from 12% to 15% of GDP lowers the burden by 20%; a 20% lower interest bill would have the same effect. The study does not compare how feasible or costly these options are. The right response depends on each country's tax capacity, spending needs, growth and borrowing terms.
3. **Debt composition matters.** Debt in foreign currency can make interest costs rise when the exchange rate falls (Eichengreen and Hausmann, 1999). This study does not measure debt composition or maturity.
4. **Read falling burdens with care.** A fall after a default or restructuring is not, by itself, evidence of sustainable debt.

## 9. Conclusion

Net interest took a larger share of revenue in 2024 than in 2015 in most of the 181 countries studied. The median rose from 4.5% to 5.8%, with the largest increases in poorer countries. Debt-to-GDP and interest-to-revenue are related, but they often rank countries differently, mainly because revenue and the net-interest-to-debt factor differ widely between countries. How interest is defined and which countries are covered change the size of the results, so both should be stated with every headline number.

The first version of this project stated four hypotheses. They were written by Claude after the data coverage and the 2024 ranking had been checked, but before the correlations, regressions and decomposition were run. The Git history does not record this order, so a reader cannot verify it.

| Hypothesis | Verdict in this revision |
|---|---|
| H1: the typical burden was higher in 2024 than in 2015, with most of the rise after 2021 | Partly supported: higher, but the median rose over the whole period |
| H2: debt-to-GDP is positively but weakly related to the burden | Partly supported: moderately related; debt alone describes the burden incompletely, and the size of R² depends on a few countries |
| H3: at similar debt, poorer countries have higher burdens because of higher rates and lower revenue | Supported for revenue (partly by construction of the measure); the net-interest-to-debt factor is higher in middle-income countries; the low-income estimate is imprecise |
| H4: after 2021 the rise came mainly from higher implicit rates | The accounting pattern is consistent with this, but the factor is not a borrowing rate and the effect of interest rates was not estimated |

## Contributions

Sidali Saidj chose the research question, set the project requirements and asked for this revision after an external audit. Claude, an AI assistant made by Anthropic, did most of the data collection, SQL and Python code, charts and writing, in the first version and in this revision. The repository does not record which results the author has checked personally.

<div class="page-break"></div>

## Appendix A. Methods and sensitivity checks

**Three-factor accounting split.** The net burden can also be written as

<p class="equation">burden = (net interest ÷ gross debt) × (debt ÷ GDP) ÷ (revenue ÷ GDP)</p>

The first term, the *net-interest-to-debt factor*, uses net interest and end-year gross debt. It is an accounting ratio, not the interest rate paid on borrowing: it falls when interest income rises, and it is affected by the timing of debt flows and by valuation changes. The log-mean Divisia index (Ang, 2004) splits each country's change into contributions that add up exactly to the change. Countries need positive net interest at both ends of a period. Results by income group are in Figure A1 and in <code>outputs/tables/decomposition_three_factor_by_group.csv</code>.

<p class="table-label">Table A1. Three-factor split, average country, percentage points</p>

| Sample | Period | Countries | Change | Net interest ÷ debt | Debt ratio | Revenue ratio |
|---|---|---|---|---|---|---|
| Each period | 2015–2021 | 166 | +1.46 | -1.12 | +2.42 | +0.16 |
| Each period | 2021–2024 | 170 | +1.00 | +2.02 | -0.46 | -0.56 |
| Each period | 2015–2024 | 169 | +2.46 | +0.87 | +1.97 | -0.39 |
| Common countries | 2015–2021 | 165 | +1.48 | -1.12 | +2.44 | +0.16 |
| Common countries | 2021–2024 | 165 | +1.05 | +2.10 | -0.47 | -0.58 |

<p class="table-note">The net-interest-to-debt and debt contributions add up to the net interest/GDP contribution in Table 2. "Largest positive contribution" means that the factor's contribution is above zero and larger than the other two. For 2021–2024 this is true in 121 of 170 countries. In 2 more, all three contributions are negative and the factor's is the least negative; these are not counted. The factor has the largest contribution in absolute size in 107 countries.</p>

**Regressions.** Models 1–3 are in Table 3. Model 4 uses the log of the net-interest-to-debt factor as the dependent variable, with log debt and income-group dummies (high income is the base). All use HC3 standard errors. Influence checks use Cook's distance and leverage from models 1 and 2 without robust errors, and refit each model leaving out one country at a time.

<p class="table-label">Table A2. Sensitivity of headline statistics, 2024</p>

| Specification | Countries | Median burden, % | Median change since 2015, points | Share above 20%, % | Debt–burden rank correlation |
|---|---|---|---|---|---|
| Baseline: net burden, all sample countries | 181 | 5.8 | 0.9 | 11 | 0.53 |
| Net burden, countries covered by FPP | 149 | 7.0 | 1.0 | 11 | 0.48 |
| Gross burden (FPP), same countries | 149 | 7.4 | 1.2 | 11 | 0.50 |
| Net burden, countries covered by the World Bank series | 88 | 5.4 | 0.7 | 9 | 0.45 |
| Central-government gross burden (World Bank), same countries | 88 | 6.2 | 0.7 | 10 | 0.52 |
| Excluding countries with negative net interest | 175 | 6.5 | 1.1 | 11 | 0.50 |
| Excluding small states (population below 1.5 million) | 142 | 5.9 | 1.4 | 14 | 0.45 |
| End year 2025 (mostly estimates) | 181 | 6.6 | 1.1 | 12 | 0.52 |
| Adding Brunei (repeated-zero case) | 182 | 5.8 | 0.9 | 11 | 0.54 |

<p class="table-note">Median change: the median of country changes since 2015, not the change in the median; countries with values in both years (149 for FPP, 83 for World Bank). Trimming the top and bottom 5% of 2024 burdens gives a rank correlation of 0.52.</p>

## Appendix B. Additional figures

<p class="fig-label">Figure A1</p>

![Three-factor decomposition](../outputs/figures/figA1_decomposition.png)

<p class="fig-label">Figure A2</p>

![Interest versus health spending](../outputs/figures/figA2_interest_vs_health.png)

<p class="fig-label">Figure A3</p>

![Net versus gross burdens](../outputs/figures/figA3_net_vs_gross.png)

## Appendix C. Coverage notes for highlighted countries

The table lists only what could be documented in this revision. The IMF Fiscal Monitor methodological appendix has a full table by country, but it could not be downloaded for this revision (the IMF website returned "Access Denied"). The other cells are unresolved and should be checked in that appendix before any country comparison is used.

| Country | What is documented | Source |
|---|---|---|
| Advanced economies (general) | Fiscal data mostly cover general government | IMF Fiscal Monitor, Methodological and Statistical Appendix |
| Emerging and developing economies (general) | Data often cover only central or budgetary central government | IMF Fiscal Monitor, Methodological and Statistical Appendix |
| Pakistan | Data on a fiscal-year basis | IMF Fiscal Monitor, October 2024, appendix notes |
| Egypt | Data on a fiscal-year basis | IMF Fiscal Monitor, October 2024, appendix notes |
| India | Data cover central and state governments | IMF Fiscal Monitor, April 2026, appendix notes |
| United States, China, Germany, Brazil, South Africa, Saudi Arabia, Sri Lanka, Japan, Canada, Nigeria, Bangladesh, Lebanon, Ghana | Not documented in this revision (unresolved) | — |

## References

Ang, B. W. (2004). Decomposition analysis for policymaking in energy: which is the preferred method? *Energy Policy*, 32(9), 1131–1139. <https://doi.org/10.1016/S0301-4215(03)00076-4>

Blanchard, O. (2019). Public debt and low interest rates. *American Economic Review*, 109(4), 1197–1229. <https://doi.org/10.1257/aer.109.4.1197>

Eichengreen, B., and Hausmann, R. (1999). Exchange rates and financial fragility. NBER Working Paper 7418. <https://www.nber.org/papers/w7418>

Escolano, J. (2010). *A Practical Guide to Public Debt Dynamics, Fiscal Sustainability, and Cyclical Adjustment of Budgetary Aggregates*. IMF Technical Notes and Manuals 10/02. <https://www.imf.org/external/pubs/ft/tnm/2010/tnm1002.pdf>

Furman, J., and Summers, L. (2020). A reconsideration of fiscal policy in the era of low interest rates. Discussion draft, Brookings Institution and Peterson Institute for International Economics. <https://www.brookings.edu/wp-content/uploads/2020/11/furman-summers-fiscal-reconsideration-discussion-draft.pdf>

IMF (2024). *Fiscal Monitor, October 2024: Putting a Lid on Public Debt*. <https://www.imf.org/en/Publications/FM/Issues/2024/10/23/fiscal-monitor-october-2024>

IMF (2024, 2026). *Fiscal Monitor, Methodological and Statistical Appendix* (October 2024; April 2026). <https://www.imf.org/-/media/files/publications/fiscal-monitor/2024/october/english/msa.pdf>

IMF (2025, 2026). *Fiscal Monitor* and *World Economic Outlook* databases (October 2026) and *Public Finances in Modern History* database (December 2025), via the IMF DataMapper API. <https://www.imf.org/external/datamapper/>

Kose, M. A., Nagle, P., Ohnsorge, F., and Sugawara, N. (2021). *Global Waves of Debt: Causes and Consequences*. World Bank. <http://hdl.handle.net/10986/32809>

Mauro, P., Romeu, R., Binder, A., and Zaman, A. (2015). A modern history of fiscal prudence and profligacy. *Journal of Monetary Economics*, 76, 55–70. Working-paper version: IMF WP/13/5. <https://www.imf.org/en/publications/wp/issues/2016/12/31/a-modern-history-of-fiscal-prudence-and-profligacy-40222>

Moody's Investors Service (2019). *Sovereign Ratings Methodology*, November 2019 (replaced in November 2022 by a version with the same factors). <https://ratings.moodys.com/api/rmc-documents/63168>

Reinhart, C. M., Rogoff, K. S., and Savastano, M. A. (2003). Debt intolerance. *Brookings Papers on Economic Activity*, 2003(1), 1–74. <https://www.brookings.edu/articles/debt-intolerance/>

UNCTAD (2024). Global public debt hits record $97 trillion in 2023, UN urges action (news release for *A World of Debt 2024*). <https://unctad.org/news/global-public-debt-hits-record-97-trillion-2023-un-urges-action>

World Bank (2026). *World Development Indicators*, via the World Bank API. <https://data.worldbank.org/>
