<!-- Generated from templates/economic_analysis.md by src/build_report.py. Edit the template, not this file. -->

<div class="masthead" markdown="1">

# The cost of public debt

<p class="standfirst">How much government revenue goes to interest, why it differs so much between countries, and what changed after 2021. A cross-country analysis of {{sample/countries}} economies, 2015–2024</p>

<p class="byline">Sidali Saidj · October 2026 · Data: IMF Fiscal Monitor (October 2026), World Bank</p>

</div>

## Executive summary

**Question.** How much government revenue is absorbed by interest payments, how has that share changed between 2015 and 2024, and is the debt-to-GDP ratio a reliable guide to which economies bear the heaviest burden?

**Approach.** Net interest as a share of general-government revenue, built from the IMF's October 2026 Fiscal Monitor for a balanced panel of {{sample/countries}} economies. The burden is split into three parts (the implicit interest rate, the debt ratio and the revenue ratio) to see which one drove each change. Two gross-interest series from the IMF and the World Bank serve as cross-checks.

**Main findings**

1. **Interest takes a growing share of revenue, but not everywhere.** The median government spent {{median_burden/All countries/2024:.1f}}% of its revenue on net interest in 2024, against {{median_burden/All countries/2015:.1f}}% in 2015; {{change/countries_up_start_end}} of {{sample/countries}} economies saw a rise. For all {{sample/countries}} combined, net interest went from {{aggregate_burden/All countries/2021:.1f}}% of total revenue in 2021 to {{aggregate_burden/All countries/2024:.1f}}% in 2024, about ${{net_interest_usd_trn/2024:.1f}}trn.
2. **Poorer countries carry the heavier and faster-growing load.** The median burden rose from {{median_burden/Low income/2015:.1f}}% to {{median_burden/Low income/2024:.1f}}% in low-income economies and from {{median_burden/Lower middle income/2015:.1f}}% to {{median_burden/Lower middle income/2024:.1f}}% in lower-middle-income ones, while in the typical high-income economy it fell from {{median_burden/High income/2015:.1f}}% to {{median_burden/High income/2024:.1f}}% (on a gross basis it was roughly flat, at {{median_burden_gross/High income/2015:.1f}}% and {{median_burden_gross/High income/2024:.1f}}%). The number of governments spending more than a fifth of their revenue on interest rose from {{high_burden/countries/2015}} in 2015 to {{high_burden/countries/2024}} in 2024; they govern {{high_burden/population_bn/2024:.1f}}bn people.
3. **Debt-to-GDP is only a partial guide.** Debt and burden are clearly related (rank correlation {{correlation/All countries/spearman:.2f}}), but debt alone accounts for about a quarter of the cross-country variation in burdens. Adding revenue nearly doubles the explained share. In all, {{derived/off_diagonal_countries}} economies sit in the "wrong" quadrant: above-median debt with a below-median burden (mostly rich countries), or the reverse (mostly poorer ones).
4. **Thin revenue is the main reason poor countries' burdens are high.** Low-income governments collect {{median_revenue/Low income/2024:.1f}}% of GDP in revenue, against {{median_revenue/High income/2024:.1f}}% in high-income ones. Middle-income governments also pay roughly twice the implicit interest rate of high-income ones at the same debt ratio.
5. **Since 2021, higher interest rates did the damage.** For the average country the burden rose by {{decomposition/All countries/2021-2024/mean_change:.1f}} points between 2021 and 2024. Higher implicit rates added {{decomposition/All countries/2021-2024/mean_rate_effect:.1f}} points; falling debt ratios and rising revenue took off {{derived/offset_2021_2024:.1f}}. Between 2015 and 2021 the driver was debt accumulation, while falling rates held the burden down.
6. **Interest now competes with health spending.** In {{social_spending/countries_interest_gt_health}} countries, home to {{social_spending/population_interest_gt_health_bn:.1f}}bn people, governments pay more in net interest than they spend on health.

**Implications.** Judging fiscal risk by debt-to-GDP alone misses where the pressure is: a government with modest debt but a narrow tax base can be more constrained than one with twice the debt. For the most burdened economies, raising revenue does more for affordability than any feasible cut in the debt ratio. Debt-management choices that lengthen maturities and reduce exposure to foreign-currency and short-term borrowing also slow how fast rate shocks feed into budgets. These are implications of the accounting and the cross-country patterns, not tested policy effects.

## 1. The problem

Interest is the one item in a budget that cannot be cut without a political or legal event. A finance ministry can trim wages, delay investment or reform transfers, but coupons are owed. The share of revenue that goes to interest therefore measures how much of a government's income is spoken for before it decides anything else. Rating agencies use it in exactly this way: Moody's, for example, scores "debt affordability" by interest payments relative to revenue alongside the debt-to-GDP ratio (Moody's, 2019).

The ratio had good reason to rise after 2021. Debt stocks jumped during the pandemic, and from 2022 central banks raised policy rates at the fastest pace in four decades. Because governments refinance gradually, higher market rates reach the interest bill with a lag. The IMF has warned that global public debt is set to keep rising and that risks are tilted towards worse outcomes (IMF, 2024). UNCTAD (2024) estimated that 3.3bn people live in countries that spend more on interest than on health or education.

This report asks three things: how large the burden is, how and why it changed between 2015 and 2024, and whether the familiar debt-to-GDP ratio identifies the governments under most pressure.

## 2. Economic framework

### 2.1 An identity with three moving parts

The burden can be written exactly as the product of three ratios (Escolano, 2010, sets out the related debt-dynamics algebra):

<p class="equation">interest / revenue = (interest / debt) × (debt / GDP) ÷ (revenue / GDP)</p>

The first term is the *implicit interest rate*: the average rate paid on the whole stock of debt. It moves more slowly than market yields because only maturing and new debt is repriced. The second is the debt ratio. The third is the government's capacity to raise revenue. The identity explains why the debt ratio alone can mislead: two countries with the same debt can face very different burdens if one borrows at 2% and collects 40% of GDP in revenue while the other borrows at 8% and collects 12%.

### 2.2 Mechanisms and competing explanations

Each term has its own economics:

- **Borrowing costs.** Rates depend on the global rate cycle, on country risk premia and on the structure of debt. Economies with a history of default or high inflation face higher premia and become stressed at lower debt levels ("debt intolerance"; Reinhart, Rogoff and Savastano, 2003). Governments that cannot borrow abroad in their own currency pay for exchange-rate risk ("original sin"; Eichengreen and Hausmann, 1999). Concessional loans from development lenders push the other way for the poorest countries.
- **Debt.** Deficits add to the stock. Inflation and growth reduce the *ratio* by raising nominal GDP, which is why high inflation in 2022–23 lowered many debt ratios even as rates rose.
- **Revenue.** A narrow tax base, a large informal sector or dependence on commodity revenue means a given interest bill absorbs a larger share of income.

A rise in the burden can also have a misleading counterpart: a fall. A government that defaults stops paying interest, so its burden drops without any improvement in its finances. Lebanon, Ghana and Sri Lanka all show this pattern in the data.

### 2.3 Hypotheses

| | Hypothesis, stated before the main analysis |
|---|---|
| H1 | The typical country's burden was higher in 2024 than in 2015, with most of the increase after 2021. |
| H2 | Debt-to-GDP is positively but only weakly associated with the burden across countries. |
| H3 | At comparable debt ratios, lower-income economies carry heavier burdens because they pay higher rates and collect less revenue. |
| H4 | Between 2021 and 2024 the rise came mainly from higher implicit rates, partly offset by falling debt ratios. |

## 3. Related research

The debate about how to judge public debt has shifted from stocks towards flows. Blanchard (2019) showed that when the interest rate is below the growth rate, debt can be rolled over at low fiscal cost, so high debt ratios need not imply high burdens. Furman and Summers (2020) argued that real interest payments relative to GDP are a better guide to fiscal space than the debt stock. This report applies the same logic to revenue rather than GDP, because revenue is what pays the bill. Their argument assumed persistently low rates; the period studied here includes the end of that era.

A second strand explains why emerging and developing economies face stress at lower debt levels: debt intolerance linked to default and inflation histories (Reinhart, Rogoff and Savastano, 2003) and currency mismatches (Eichengreen and Hausmann, 1999). Kose et al. (2021) document how the post-2010 wave of debt in developing economies differed from earlier ones in its speed and breadth. On the measurement side, the IMF's Public Finances in Modern History database (Mauro et al., 2015) provides long series of gross interest, used here as a cross-check.

UNCTAD (2024) and the IMF (2024) have documented the rising cost of debt with aggregate statistics. This report adds three things: a transparent, reproducible cross-country measure built from one consistent source; a formal test of how much the debt ratio explains; and an exact decomposition of changes in the burden into rate, debt and revenue effects before and after the 2022 tightening. The full review is in [research/literature_review.md](../research/literature_review.md).

## 4. Data and method

**Sources.** General-government revenue, gross debt, primary balance and overall balance come from the IMF Fiscal Monitor (October 2026), via the IMF DataMapper API. GDP in US dollars is from the October 2026 World Economic Outlook. Gross interest is from the IMF Public Finances in Modern History database (December 2025). The World Bank supplies the central-government interest series (`GC.XPN.INTP.RV.ZS`), health and education spending, population, regions and income groups. All data were retrieved on 21 October 2026 and are stored in the repository as a frozen snapshot.

**Measure.** Net interest equals the primary balance minus the overall balance; the burden is net interest divided by revenue. Net interest is lower than gross interest when governments earn interest on financial assets. The two agree closely for most economies (rank correlation {{measure_agreement/gross_general_government/spearman:.2f}} across {{measure_agreement/gross_general_government/countries}} countries; {{measure_agreement/gross_general_government/within_2_points:.0%}} within two points) but diverge for a few asset-rich governments, such as Canada (net {{country/CAN/burden_end:.1f}}%, gross {{country/CAN/gross_end:.1f}}%) and Japan (net {{country/JPN/burden_end:.1f}}%, gross {{country/JPN/gross_end:.1f}}%). The net measure is used because it covers far more countries and comes from the same vintage as the debt and revenue data.

**Sample.** Every economy with all four fiscal series in each year from 2015 to 2024: {{sample/countries}} economies ({{sample/by_income/High income}} high-income, {{sample/by_income/Upper middle income}} upper-middle, {{sample/by_income/Lower middle income}} lower-middle and {{sample/by_income/Low income}} low-income). Of the economies with some fiscal data, {{sample/excluded_with_some_data}} fail this rule, mostly because debt is not reported (for example Venezuela) or interest is not separately identified (Brunei, Libya, Macao). The full list and other data checks are in [audit/validation_report.md](../audit/validation_report.md). Values for 2025 are partly estimates and 2026–27 are IMF forecasts; they are shown as context only.

**Methods.** The typical country is described by medians, because burdens are strongly skewed. The total for all countries is a GDP-weighted aggregate (total net interest over total revenue, in US dollars). The relationship between debt and burden is measured by a Spearman rank correlation with a bootstrap confidence interval, and by log-log regressions with heteroskedasticity-robust (HC3) standard errors. Changes in the burden are split exactly into rate, debt and revenue effects with a log-mean Divisia index (Ang, 2004). Case studies were chosen by a rule fixed in advance: the largest economy in each World Bank region plus the three highest burdens in 2024. Details are in [research/methodology.md](../research/methodology.md).

## 5. Results

### 5.1 How much revenue goes to interest?

In 2024 the median government spent {{median_burden/All countries/2024:.1f}}% of its revenue on net interest. The distribution has a long right tail: {{high_burden/countries/2024}} economies spent more than 20%, and three spent more than half: Pakistan ({{country/PAK/burden_end:.1f}}%), Egypt ({{country/EGY/burden_end:.1f}}%) and Sri Lanka ({{country/LKA/burden_end:.1f}}%) (Figure 1). Of the top 20, {{top20_low_and_lower_middle}} are low- or lower-middle-income economies. Two high-income exceptions are instructive. Bahrain is a high-income economy whose debt has risen to {{country/BHR/debt_end:.0f}}% of GDP while its revenue, mostly from oil, is only {{country/BHR/revenue_end:.0f}}% of GDP. Costa Rica combines moderate debt with an implicit rate of {{country/CRI/implicit_rate_end:.1f}}% and revenue of {{country/CRI/revenue_end:.0f}}% of GDP.

<p class="fig-label">Figure 1</p>

![Highest interest burdens in 2024](../outputs/figures/fig1_highest_burdens.png)

The burden differs systematically by income. In 2024 the median low-income government spent {{median_burden/Low income/2024:.1f}}% of revenue on interest, {{derived/burden_multiple_low_vs_high:.1f}} times the {{median_burden/High income/2024:.1f}}% of the median high-income government, although their median debt ratios were similar ({{median_debt/Low income/2024:.0f}}% and {{median_debt/High income/2024:.0f}}% of GDP).

### 5.2 How has the burden changed?

For the typical country the burden rose steadily, from {{median_burden/All countries/2015:.1f}}% in 2015 to {{median_burden/All countries/2021:.1f}}% in 2021 and {{median_burden/All countries/2024:.1f}}% in 2024. Behind that median, income groups diverged (Figure 2). The median low-income burden more than doubled, from {{median_burden/Low income/2015:.1f}}% to {{median_burden/Low income/2024:.1f}}%, and rose in almost every year. The lower-middle-income median went from {{median_burden/Lower middle income/2015:.1f}}% to {{median_burden/Lower middle income/2024:.1f}}%. The high-income median fell, from {{median_burden/High income/2015:.1f}}% to {{median_burden/High income/2024:.1f}}%. Its median implicit rate barely moved after 2021 ({{median_implicit_rate/High income/2021:.1f}}% in 2021, {{median_implicit_rate/High income/2024:.1f}}% in 2024), which is consistent with long-dated debt locked in at low rates before 2022. Part of the fall is also a feature of the net measure: as rates rose, governments with financial assets earned more interest. On a gross basis the high-income median was roughly flat ({{median_burden_gross/High income/2015:.1f}}% in 2015, {{median_burden_gross/High income/2021:.1f}}% in 2021, {{median_burden_gross/High income/2024:.1f}}% in 2024), while the low-income one rose from {{median_burden_gross/Low income/2015:.1f}}% to {{median_burden_gross/Low income/2024:.1f}}%: the gap widened on either measure. IMF forecasts show the low-income median rising further, to {{median_burden/Low income/2027:.1f}}% by 2027.

<p class="fig-label">Figure 2</p>

![Median burden by income group](../outputs/figures/fig2_median_burden_by_income.png)

Weighting by GDP tells a different story about timing (Figure 3). Total net interest across the {{sample/countries}} economies was {{aggregate_burden/All countries/2015:.1f}}% of total revenue in 2015 and still {{aggregate_burden/All countries/2021:.1f}}% in 2021, then rose to {{aggregate_burden/All countries/2024:.1f}}% by 2024. That aggregate is dominated by large economies whose interest bills responded quickly to higher rates: the United States' burden went from {{country/USA/burden_break:.1f}}% in 2021 to {{country/USA/burden_end:.1f}}% in 2024. In dollars, net interest rose from ${{net_interest_usd_trn/2021:.2f}}trn in 2021 to ${{net_interest_usd_trn/2024:.2f}}trn in 2024 (nominal, at market exchange rates). The number of governments spending more than a fifth of revenue on interest rose from {{high_burden/countries/2015}} in 2015 to {{high_burden/countries/2024}} in 2024, and an estimated {{high_burden/countries/2025}} in 2025.

<p class="fig-label">Figure 3</p>

![Aggregate burden and count of high-burden countries](../outputs/figures/fig3_global_burden_and_count.png)

**Verdict on H1: partly supported.** The burden of the typical country was higher in 2024 than in 2015. But for the median country the rise was spread across the whole period, driven by poorer economies, rather than concentrated after 2021. The concentration after 2021 holds for the GDP-weighted total. The median high-income burden fell on the net measure and was roughly flat on the gross one.

### 5.3 Is debt-to-GDP a reliable guide?

Countries with more debt do tend to spend more of their revenue on interest. The Spearman rank correlation in 2024 is {{correlation/All countries/spearman:.2f}} (95% bootstrap interval {{correlation/All countries/ci_low:.2f}} to {{correlation/All countries/ci_high:.2f}}), and it is positive within each income group, though imprecisely estimated for the {{sample/by_income/Low income}} low-income economies. But the scatter is wide (Figure 4). Japan has the highest debt ratio among large economies ({{country/JPN/debt_end:.0f}}% of GDP) and a net burden of {{country/JPN/burden_end:.1f}}% ({{country/JPN/gross_end:.1f}}% gross). Nigeria's debt is {{country/NGA/debt_end:.0f}}% of GDP, yet interest absorbs {{country/NGA/burden_end:.0f}}% of revenue, because revenue is only {{country/NGA/revenue_end:.0f}}% of GDP. Bangladesh is similar (debt {{country/BGD/debt_end:.0f}}%, revenue {{country/BGD/revenue_end:.1f}}%, burden {{country/BGD/burden_end:.0f}}%).

<p class="fig-label">Figure 4</p>

![Debt versus interest burden, 2024](../outputs/figures/fig4_debt_vs_burden.png)

Of the {{sample/countries}} economies, {{quadrants/counts/High debt, low burden}} have above-median debt but below-median burdens, and {{quadrants/counts/Low debt, high burden}} the reverse. Of the first group, {{quadrants/high_debt_low_burden_hic_share:.0%}} are high-income economies; of the second, {{quadrants/low_debt_high_burden_lic_lmic_share:.0%}} are low- or lower-middle-income.

Table 1 makes the point formally. In logs, debt alone explains {{regression/debt_only/r_squared:.0%}} of the cross-country variation in burdens (model 1). Adding the revenue ratio raises this to {{regression/debt_with_revenue/r_squared:.0%}} (model 2). The coefficients sit close to what the identity implies: a 1% higher debt ratio goes with a burden about {{regression/debt_with_revenue/coef:.1f}}% higher, and a 1% higher revenue ratio with a burden about {{derived/revenue_elasticity_abs:.1f}}% lower. Neither differs significantly from one in magnitude. Model 4 confirms the implication: across countries, implicit rates are unrelated to the debt ratio (coefficient {{regression/rate_on_debt/coef:.2f}}, interval {{regression/rate_on_debt/ci_low:.2f}} to {{regression/rate_on_debt/ci_high:.2f}}), so more indebted governments do not systematically borrow more cheaply or more expensively.

<p class="table-label">Table 1. What explains cross-country differences in interest burdens, 2024</p>

| | (1) Debt only | (2) Debt and revenue | (3) Adding income group | (4) Implicit rate |
|---|---|---|---|---|
| Dependent variable | log burden | log burden | log burden | log implicit rate |
| log debt/GDP | {{regression/debt_only/coef:.2f}} [{{regression/debt_only/ci_low:.2f}}, {{regression/debt_only/ci_high:.2f}}] | {{regression/debt_with_revenue/coef:.2f}} [{{regression/debt_with_revenue/ci_low:.2f}}, {{regression/debt_with_revenue/ci_high:.2f}}] | {{regression/debt_full/coef:.2f}} [{{regression/debt_full/ci_low:.2f}}, {{regression/debt_full/ci_high:.2f}}] | {{regression/rate_on_debt/coef:.2f}} [{{regression/rate_on_debt/ci_low:.2f}}, {{regression/rate_on_debt/ci_high:.2f}}] |
| log revenue/GDP | | {{regression/revenue/coef:.2f}} [{{regression/revenue/ci_low:.2f}}, {{regression/revenue/ci_high:.2f}}] | {{regression/revenue_full/coef:.2f}} [{{regression/revenue_full/ci_low:.2f}}, {{regression/revenue_full/ci_high:.2f}}] | |
| Income-group dummies | No | No | Yes | Yes |
| R² | {{regression/debt_only/r_squared:.2f}} | {{regression/debt_with_revenue/r_squared:.2f}} | {{regression/debt_full/r_squared:.2f}} | {{regression/rate_on_debt/r_squared:.2f}} |
| Countries | {{regression/debt_only/countries}} | {{regression/debt_with_revenue/countries}} | {{regression/debt_full/countries}} | {{regression/rate_on_debt/countries}} |

<p class="table-note">OLS on 2024 cross-section; 95% confidence intervals from HC3 robust standard errors in brackets. Countries with positive net interest only. Full output, including income-group coefficients: <a href="../outputs/tables/regressions.csv">outputs/tables/regressions.csv</a>.</p>

**Verdict on H2: partly supported.** The association is positive and moderate rather than weak. But debt alone leaves three-quarters of the variation unexplained, and {{derived/off_diagonal_share:.0%}} of countries fall on the "wrong" side of the median on one measure or the other.

### 5.4 Why are poorer countries' burdens higher?

The identity points to two channels, and the data show both. Revenue is the larger one. The median low-income government raises {{median_revenue/Low income/2024:.1f}}% of GDP and the lower-middle-income one {{median_revenue/Lower middle income/2024:.1f}}%, against {{median_revenue/High income/2024:.1f}}% in high-income economies. With similar debt ratios, that gap alone roughly doubles the burden.

Rates are the second channel. Holding the debt ratio constant (Table 1, model 4), upper-middle-income governments pay implicit rates about {{derived/rate_multiple_upper_middle:.1f}} times, and lower-middle-income ones about {{derived/rate_multiple_lower_middle:.1f}} times, those of high-income governments. Both differences are statistically clear. For low-income economies the estimate is {{derived/rate_multiple_low_income:.1f}} times but imprecise (the interval includes no difference), probably because much of their debt is concessional. Their implicit rates are rising fastest: the median went from {{median_implicit_rate/Low income/2015:.1f}}% in 2015 to {{median_implicit_rate/Low income/2024:.1f}}% in 2024, overtaking the high-income median of {{median_implicit_rate/High income/2024:.1f}}%. The data cannot say whether this reflects more borrowing on commercial terms, more expensive domestic debt or higher rates on new loans.

**Verdict on H3: supported, with a qualification.** Lower-income economies carry much heavier burdens at similar debt levels. Weak revenue explains most of the gap; higher rates matter clearly for middle-income economies and, less certainly, for low-income ones.

### 5.5 What drove the change?

Figure 5 splits each country's change in burden into its three components, averaged by income group. The two periods look very different.

<p class="fig-label">Figure 5</p>

![Decomposition of the change in burden](../outputs/figures/fig5_decomposition.png)

Between 2015 and 2021 the burden of the average country rose by {{decomposition/All countries/2015-2021/mean_change:.1f}} points. Debt accumulation, much of it during the pandemic, contributed {{decomposition/All countries/2015-2021/mean_debt_effect:+.1f}} points; falling implicit rates contributed {{decomposition/All countries/2015-2021/mean_rate_effect:+.1f}}. Between 2021 and 2024 the roles reversed. Higher implicit rates contributed {{decomposition/All countries/2021-2024/mean_rate_effect:+.1f}} points and were the largest of the three contributions in {{decomposition/All countries/2021-2024/share_rate_largest_up:.0%}} of countries. Falling debt ratios contributed {{decomposition/All countries/2021-2024/mean_debt_effect:+.1f}} points, consistent with inflation raising nominal GDP faster than debt, and rising revenue {{decomposition/All countries/2021-2024/mean_revenue_effect:+.1f}}. The rate effect was largest for low-income economies ({{decomposition/Low income/2021-2024/mean_rate_effect:.1f}} points), whose revenue ratios also slipped. Upper-middle-income economies offset most of their rate shock with higher revenue and lower debt ratios.

Medians tell the same story with smaller magnitudes (2021–24 median rate effect {{decomposition/All countries/2021-2024/median_rate_effect:.1f}} points against a median change of {{decomposition/All countries/2021-2024/median_change:.1f}}; see `outputs/tables/decomposition_by_group.csv`).

**Verdict on H4: supported.** The rise after 2021 came from higher rates, with falling debt ratios and rising revenue offsetting about half of it.

### 5.6 Country cases

The ten case studies (Figure 6) show how the same shocks played out differently. In the **United States** the burden almost doubled, from {{country/USA/burden_start:.1f}}% to {{country/USA/burden_end:.1f}}%, as a high and rising debt ratio ({{country/USA/debt_end:.0f}}% of GDP) met higher rates; the IMF expects {{country/USA/burden_forecast_end:.1f}}% by 2027. **China**'s burden doubled from a low base ({{country/CHN/burden_start:.1f}}% to {{country/CHN/burden_end:.1f}}%) as general-government debt more than doubled, to {{country/CHN/debt_end:.0f}}% of GDP, at an implicit rate of only {{country/CHN/implicit_rate_end:.1f}}%. **Germany**'s fell, from {{country/DEU/burden_start:.1f}}% to {{country/DEU/burden_end:.1f}}%. **India**'s stayed high and roughly flat at about {{country/IND/burden_end:.0f}}%, reflecting an implicit rate of {{country/IND/implicit_rate_end:.1f}}% on debt of {{country/IND/debt_end:.0f}}% of GDP. **Brazil**'s fell from {{country/BRA/burden_start:.0f}}% to {{country/BRA/burden_end:.0f}}% on the net measure, though its gross burden was {{country/BRA/gross_end:.0f}}% in 2024. **South Africa**'s rose from {{country/ZAF/burden_start:.0f}}% to {{country/ZAF/burden_end:.0f}}% as debt climbed from {{country/ZAF/debt_start:.0f}}% to {{country/ZAF/debt_end:.0f}}% of GDP. **Saudi Arabia** moved from being a net earner of interest to a small net payer as it borrowed.

<p class="fig-label">Figure 6</p>

![Case studies](../outputs/figures/fig6_case_studies.png)

The three most burdened economies show crisis dynamics. **Pakistan**'s burden reached {{country/PAK/burden_end:.0f}}% in 2024, with an implicit rate of {{country/PAK/implicit_rate_end:.0f}}% and revenue of {{country/PAK/revenue_end:.0f}}% of GDP. **Egypt**'s reached {{country/EGY/burden_end:.0f}}%, and the IMF projects a peak of {{country/EGY/burden_max_forecast:.0f}}% in {{country/EGY/burden_max_forecast_year}}. **Sri Lanka**'s peaked at {{country/LKA/burden_peak:.0f}}% in {{country/LKA/burden_peak_year}} and fell to {{country/LKA/burden_end:.0f}}% in 2024 as it restructured its debt. Lebanon is the warning against reading a falling burden as good news: its burden dropped from {{country/LBN/burden_start:.0f}}% in 2015 to {{country/LBN/burden_end:.0f}}% in 2024 because it defaulted in 2020 and stopped servicing much of its debt.

### 5.7 Interest and social spending

Comparing net interest with government health spending, both as shares of GDP in the latest year with data (2023 for most), {{social_spending/countries_interest_gt_health}} of {{social_spending/countries_health}} countries spend more on interest (Figure 7). They are home to {{social_spending/population_interest_gt_health_bn:.1f}}bn people; the most populous are India (interest {{country/IND/interest_gdp_end:.1f}}% of GDP in 2024; health {{country/IND/health_gdp:.1f}}% in 2023), Indonesia, Pakistan, Nigeria and Brazil. For education the count is {{social_spending/countries_interest_gt_education}} countries, with {{social_spending/population_interest_gt_education_bn:.1f}}bn people. These figures are of the same order as UNCTAD's (2024) estimate of 3.3bn people, which used different years and definitions.

<p class="fig-label">Figure 7</p>

![Interest versus health spending](../outputs/figures/fig7_interest_vs_health.png)

The comparison is descriptive. It does not show that interest payments crowded out health spending; health budgets in these countries were low before interest costs rose.

## 6. Robustness

The main results hold under the alternatives set out in advance (Table 2). On the gross measure the median burden is higher, as expected, but the change since 2015, the share of high-burden countries and the debt–burden correlation are similar. Results also hold without net-creditor governments, without small states and with 2025 estimates as the end year. Dropping the top and bottom 5% of burdens leaves the rank correlation at {{spearman_trimmed:.2f}}. Figure 8 shows the agreement between net and gross measures country by country.

<p class="table-label">Table 2. Robustness of headline statistics</p>

| Specification | Countries | Median burden, % | Median change since 2015, points | Share above 20%, % | Debt–burden rank correlation |
|---|---|---|---|---|---|
| Baseline (net, general government) | {{robustness/Baseline (net interest, general government)/countries}} | {{robustness/Baseline (net interest, general government)/median_burden_end:.1f}} | {{robustness/Baseline (net interest, general government)/median_change_since_start:.1f}} | {{robustness/Baseline (net interest, general government)/share_above_threshold:.0f}} | {{robustness/Baseline (net interest, general government)/spearman_debt_burden:.2f}} |
| Gross interest, general government (IMF FPP) | {{robustness/Gross interest, general government (FPP)/countries}} | {{robustness/Gross interest, general government (FPP)/median_burden_end:.1f}} | {{robustness/Gross interest, general government (FPP)/median_change_since_start:.1f}} | {{robustness/Gross interest, general government (FPP)/share_above_threshold:.0f}} | {{robustness/Gross interest, general government (FPP)/spearman_debt_burden:.2f}} |
| Gross interest, central government (World Bank) | {{robustness/Gross interest, central government (World Bank)/countries}} | {{robustness/Gross interest, central government (World Bank)/median_burden_end:.1f}} | {{robustness/Gross interest, central government (World Bank)/median_change_since_start:.1f}} | {{robustness/Gross interest, central government (World Bank)/share_above_threshold:.0f}} | {{robustness/Gross interest, central government (World Bank)/spearman_debt_burden:.2f}} |
| Excluding net-creditor governments | {{robustness/Excluding net-creditor governments/countries}} | {{robustness/Excluding net-creditor governments/median_burden_end:.1f}} | {{robustness/Excluding net-creditor governments/median_change_since_start:.1f}} | {{robustness/Excluding net-creditor governments/share_above_threshold:.0f}} | {{robustness/Excluding net-creditor governments/spearman_debt_burden:.2f}} |
| Excluding small states | {{robustness/Excluding small states/countries}} | {{robustness/Excluding small states/median_burden_end:.1f}} | {{robustness/Excluding small states/median_change_since_start:.1f}} | {{robustness/Excluding small states/share_above_threshold:.0f}} | {{robustness/Excluding small states/spearman_debt_burden:.2f}} |
| End year 2025 (estimates) | {{robustness/End year 2025 (estimate)/countries}} | {{robustness/End year 2025 (estimate)/median_burden_end:.1f}} | {{robustness/End year 2025 (estimate)/median_change_since_start:.1f}} | {{robustness/End year 2025 (estimate)/share_above_threshold:.0f}} | {{robustness/End year 2025 (estimate)/spearman_debt_burden:.2f}} |

<p class="table-note">Gross-interest rows cover fewer countries. On exactly the same countries, the baseline median is {{robustness/Gross interest, general government (FPP)/baseline_median_same_countries:.1f}}% (FPP sample) and {{robustness/Gross interest, central government (World Bank)/baseline_median_same_countries:.1f}}% (World Bank sample), so most of the gap in levels is the net-versus-gross concept, not sample composition.</p>

<p class="fig-label">Figure 8</p>

![Net versus gross measure](../outputs/figures/fig8_net_vs_gross.png)

## 7. Limitations

- **Association, not causation.** The regressions describe cross-country patterns in one year. Debt, revenue and borrowing costs are shaped jointly by institutions, history and shocks the data do not measure.
- **Net versus gross.** Net interest understates the cash cost for governments with large financial assets; gross results are reported alongside.
- **Implicit rate.** Dividing interest by end-year debt gives an average rate that mixes old and new borrowing and is affected by exchange-rate movements on foreign-currency debt. It is not a market yield.
- **Coverage and comparability.** General-government coverage differs across countries (some report only the central or budgetary government), and data for 2025 are partly estimates. A different IMF vintage will revise the numbers.
- **What the ratio leaves out.** Interest-to-revenue says nothing about maturity, currency composition, who holds the debt or whether the government can roll it over, all of which matter for default risk. Principal repayments, often the binding constraint in a liquidity crisis, are excluded.

## 8. Policy implications

The evidence supports four practical conclusions. They follow from the identity and the patterns above; none is a tested estimate of a policy's effect.

1. **Monitor affordability, not just the debt stock.** A debt ceiling or anchor expressed only as a share of GDP would have flagged Japan and missed Nigeria and Bangladesh. Adding interest-to-revenue to fiscal rules and surveillance would point at where pressure is building.
2. **For the most burdened, revenue is the main lever.** Because the burden is inversely proportional to the revenue ratio, raising revenue from 12% to 15% of GDP cuts the burden by a fifth at unchanged debt. Debt reduction on that scale would take years of primary surpluses.
3. **Debt structure determines how fast rate shocks arrive.** Longer maturities and less reliance on short-term and foreign-currency debt slow the pass-through of rate rises. The rise in low-income economies' implicit rates is a reason for lenders and borrowers to watch borrowing terms, not only volumes.
4. **Read falling burdens with care.** A drop after default or restructuring (Lebanon, Ghana, Sri Lanka) reflects unpaid interest, not restored sustainability.

## 9. Conclusion

Interest took a larger share of government revenue in 2024 than in 2015 for most of the {{sample/countries}} economies studied. The typical burden rose from {{median_burden/All countries/2015:.1f}}% to {{median_burden/All countries/2024:.1f}}%, and the aggregate jumped after 2021. The increase was concentrated in poorer economies, while the typical rich economy's burden fell on a net basis and held steady on a gross one. The debt-to-GDP ratio is a useful but incomplete guide: it explains about a quarter of the cross-country differences, and weak revenue explains much of the rest. Since 2021, higher interest rates have been the main force pushing burdens up. With IMF forecasts showing the low-income median still rising, these pressures look set to continue.

Next steps that the data would support: extend the analysis to debt service including principal, separate domestic and external debt, and test whether high burdens precede cuts in public investment using a panel design with an identification strategy.

| | Verdict |
|---|---|
| H1: burden higher in 2024 than 2015, mostly after 2021 | Partly supported: higher, but for the median country the rise was spread over the decade |
| H2: debt weakly associated with burden | Partly supported: moderately associated, yet a poor guide on its own |
| H3: lower-income economies carry heavier burdens at similar debt | Supported: mainly through weaker revenue, also higher rates for middle-income economies |
| H4: rates drove the rise after 2021 | Supported |

## References

Ang, B. W. (2004). Decomposition analysis for policymaking in energy: which is the preferred method? *Energy Policy*, 32(9), 1131–1139.

Blanchard, O. (2019). Public debt and low interest rates. *American Economic Review*, 109(4), 1197–1229.

Eichengreen, B., and Hausmann, R. (1999). Exchange rates and financial fragility. NBER Working Paper 7418.

Escolano, J. (2010). *A Practical Guide to Public Debt Dynamics, Fiscal Sustainability, and Cyclical Adjustment of Budgetary Aggregates*. IMF Technical Notes and Manuals 10/02.

Furman, J., and Summers, L. (2020). A reconsideration of fiscal policy in the era of low interest rates. Discussion draft, Hutchins Center on Fiscal and Monetary Policy and Peterson Institute for International Economics.

IMF (2024). *Fiscal Monitor, October 2024: Putting a Lid on Public Debt*. Washington, DC: International Monetary Fund.

IMF (2026). *Fiscal Monitor database, October 2026*, and *World Economic Outlook database, October 2026*. Retrieved via the IMF DataMapper API, 21 October 2026.

IMF (2025). *Public Finances in Modern History database*, December 2025 update. Retrieved via the IMF DataMapper API, 21 October 2026.

Kose, M. A., Nagle, P., Ohnsorge, F., and Sugawara, N. (2021). *Global Waves of Debt: Causes and Consequences*. Washington, DC: World Bank.

Mauro, P., Romeu, R., Binder, A., and Zaman, A. (2015). A modern history of fiscal prudence and profligacy. *Journal of Monetary Economics*, 76, 55–70.

Moody's Investors Service (2019). *Sovereign Ratings Methodology*, November 2019. Superseded in November 2022 by a version that keeps the same factors and sub-factors.

Reinhart, C. M., Rogoff, K. S., and Savastano, M. A. (2003). Debt intolerance. *Brookings Papers on Economic Activity*, 2003(1), 1–74.

UNCTAD (2024). *A World of Debt 2024: A Growing Burden to Global Prosperity*. Geneva: United Nations.

World Bank (2026). *World Development Indicators*. Retrieved via the World Bank API, 21 October 2026.
