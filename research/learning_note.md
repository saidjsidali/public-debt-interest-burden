# Learning note

A plain-English guide to this project, to help you understand it, explain it and change it.
It describes what the project does. It does not describe work that you have done: record that
yourself, honestly, when you do it.

## 1. The question

Governments borrow, and they pay interest on what they borrow. The project asks:

1. How did the share of government revenue spent on net interest change between 2015 and 2024?
2. Why can the debt-to-GDP ratio and the interest-to-revenue ratio rank countries differently?
3. How do the definition of interest and the choice of countries change the results?

## 2. The measures

| Term | Meaning | Example (2024) |
|---|---|---|
| Net interest | Interest paid minus interest received, % of GDP. In the data: primary balance − overall balance. | India: 4.9% of GDP |
| Net interest burden | Net interest ÷ revenue × 100. The main measure. | Pakistan: 61%, Germany: 1.7% |
| Gross interest burden | Interest paid (before interest received) ÷ revenue, from another IMF database (FPP). | Canada: net 0.01%, gross 8.3% |
| Net-interest-to-debt factor | Net interest ÷ gross debt. An accounting ratio, **not** a borrowing rate. | Used only in the decomposition |
| Total net interest / total revenue | All countries added up in US dollars. Large economies count more. | 6.4% (2015: 4.9%) |
| Median | The middle country when all countries are sorted. Not affected by a few extreme values. | 5.8% (2015: 4.5%) |
| Percentage points | The difference between two percentages. 4.5% → 5.8% is +1.3 points. | |

Why primary balance − overall balance? The overall balance is revenue minus all spending. The
primary balance is the same thing without net interest. So the gap between them is net
interest.

## 3. The important SQL steps

1. **Load** (`sql/01_schema.sql`): one long table `observation(series_code, iso3, year, value)`.
   The primary key stops duplicate rows.
2. **Pivot** (`sql/02_build_panel.sql`): `MAX(CASE WHEN series_code = '...' THEN value END)`
   turns the long table into one row per country and year. Then the measures are calculated.
3. **Sample** (same file): `GROUP BY iso3 HAVING COUNT(revenue_gdp) = 10 AND ...` keeps
   countries with complete data.
4. **Checks** (`sql/03_validation.sql`): each query returns problem rows. "Error" checks stop
   the pipeline; "review" checks are listed in `audit/validation_report.md`.
5. **Medians** (`sql/04_analysis.sql`, `group_medians`): SQLite has no MEDIAN function, so
   `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY value)` numbers the rows and the middle one
   (or the average of the middle two) is kept. A test recomputes every median in pandas.
6. **Sample funnel** (`sample_funnel`): counts the countries left after each rule.

Try it: after `python run.py`, open `data/processed/fiscal.sqlite` with any SQLite tool and run

```sql
SELECT name, ROUND(interest_burden, 1) AS burden, ROUND(debt_gdp) AS debt
FROM panel JOIN sample USING (iso3)
WHERE year = 2024
ORDER BY burden DESC
LIMIT 10;
```

## 4. The main results (October 2026 IMF data)

- The median net burden rose from 4.5% of revenue (2015) to 5.8% (2024); it rose in 113 of 181
  countries. Low-income median: 3.6% → 8.4%.
- In high-income countries the median fell on the net measure (4.0% → 2.3%) but was almost
  unchanged on the gross measure (4.8% → 4.6%).
- Debt and burden are related (rank correlation 0.53), but 52 countries are above the median on
  one measure and below it on the other. Japan: high debt, low net burden. Nigeria: low debt,
  high burden because revenue is low.
- The gross median is 1.5 points higher than the net median, but about three-quarters of that
  difference comes from the smaller set of countries in the gross data.
- 2021–2024: net interest/GDP rose faster than revenue; in the three-factor split the
  net-interest-to-debt factor made the largest positive contribution. This is consistent with
  higher interest rates, but the split does not prove it.

## 5. The limits

- Descriptive, not causal.
- One data vintage; IMF data are revised twice a year.
- Net interest is lower than the interest actually paid when governments earn interest.
- Government coverage and accounting differ between countries.
- The burden is not a measure of default risk (no maturity, currency or principal repayments).

## 6. Questions you may be asked

Answer only what you can explain and reproduce yourself. The files in brackets contain the
material.

1. Why use interest/revenue and not only debt/GDP? *(report section 1.1)*
2. What is the difference between gross and net interest? How does it change the Canada or
   Japan example? *(section 1.2)*
3. Why does primary balance minus overall balance give net interest? *(section 2 above)*
4. What does the net-interest-to-debt factor measure, and why is it not a bond yield?
   *(Appendix A, `research/methodology.md`)*
5. What does R² = 0.25 refer to, and why does it change when Canada is left out?
   *(section 4, `outputs/tables/regression_influence.csv`)*
6. Why does adding revenue improve the regression partly by construction? *(section 4)*
7. What is the difference between the median burden and total interest ÷ total revenue?
   *(section 3)*
8. What information is lost when you require ten complete years? *(section 2, Table 1)*
9. What can the LMDI decomposition show, and what can it not show? *(Appendix A)*
10. Why does "interest larger than health spending" not prove that interest caused lower
    health spending? *(section 6)*
11. Why might a default lower the measured burden without making the debt sustainable?
    *(section 5)*
12. Which steps did Claude do, which choices did you make, and which results did you check
    yourself? *(README "Contributions"; answer truthfully)*

## 7. Exercises to build your own understanding

1. Reproduce three headline numbers yourself, for example with the SQL query above and with
   `audit/independent_check.py`, and compare them with the report.
2. Change `HIGH_BURDEN_THRESHOLD` in `src/config.py` from 20 to 15, run `python run.py`, and
   explain how the count changes. Then change it back.
3. Explain Figure 4 to someone without using notes.
4. Pick one flagged case in `audit/validation_report.md` (for example Lao PDR 2024), look for an
   IMF country report, and update `audit/reviewed_cases.csv` with what you find, your name and
   the date.
