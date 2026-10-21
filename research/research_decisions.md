# Research decisions

A record of every consequential choice, why it was made, and whether it was made before or
after seeing results. The order is chronological.

**What was seen before the methodology was written.** Data coverage by source and year,
agreement between the net and gross measures, and a first look at 2024 burden levels and the
top of the ranking. **Not seen until after:** income-group trends, correlations, regressions,
the decomposition and the robustness checks.

---

### D1. Primary measure: IMF Fiscal Monitor net interest, not the World Bank series

- **Options.** (a) World Bank `GC.XPN.INTP.RV.ZS`, the indicator suggested in the project
  brief; (b) net interest derived from the IMF Fiscal Monitor; (c) gross interest from the IMF
  Public Finances in Modern History (FPP) database.
- **Evidence.** The World Bank series covers 142 economies in 2015 but only 91 in 2024, and
  misses several of the most burdened (Egypt, Pakistan, Sri Lanka, India in 2024). It also
  covers central government only. The Fiscal Monitor gives a balanced 2015–2024 panel for
  about 180 economies, from the same vintage as the debt and revenue data. FPP gross interest
  covers 151 economies to 2024 but misses Egypt, Malawi, Zambia and Sierra Leone.
- **Decision.** (b) as the primary measure; (a) and (c) as cross-checks. Taken before results.

### D2. Net versus gross interest

- **Evidence.** Across 149 countries with both, rank correlation 0.96 and 81% within two
  points. Large gaps occur only where governments hold big financial assets (Kuwait, Canada,
  Hong Kong, Norway) and in a few others (Brazil, Honduras, Oman, Myanmar).
- **Decision.** Keep net as primary; report gross alongside for high-income economies and in
  the robustness table; show the comparison in Figure 8.

### D3. Exclude economies whose net interest is a placeholder zero

- Brunei (10 of 10 years), Libya (10) and Macao (8) record net interest of exactly 0.000. That
  means interest is not separately identified, not that it is zero.
- **Rule.** Exclude economies with five or more exact-zero years. Timor-Leste (two zero years)
  stays in. Taken before results.

### D4. End year 2024, with 2025 as a check

2025 values in the October 2026 Fiscal Monitor are partly estimates, and the gross-interest
cross-checks stop in 2024. The study window is 2015–2024 as in the brief; 2025 is a robustness
check, and 2026–27 forecasts are shown only as labelled context.

### D5. Income groups fixed at the current World Bank classification

Holding classification fixed keeps group membership constant over time, so changes in group
medians reflect changes in burdens rather than countries moving between groups. Side effect:
a few countries are classified by their 2026 status (Costa Rica, for example, is high-income).

### D6. SQLite as the database

SQLite ships with Python, so a reviewer needs no database server. The SQL is standard apart from
token substitution for years. Medians are computed with window functions and cross-checked
against pandas in the tests.

### D7. Revenue above 100% of GDP is not an error (made after the validation check failed)

The first validation run stopped because Kiribati and Tuvalu report revenue above 100% of GDP.
On inspection this is plausible: fishing-licence fees, grants and trust-fund income are large
relative to GDP. The blocking range was widened to 0–200% and a review check lists these cases.
Both economies drop out in the small-states robustness check, which does not change the
conclusions.

### D8. No implicit rate for net creditors (made after inspecting medians)

Kuwait's "implicit rate" came out at −853% (large net interest income on a tiny debt). An
implicit rate means nothing when net interest is negative, so the rate medians and the
decomposition use only countries with positive net interest. The burden medians still include
net creditors.

### D9. Case-study selection rule

Fixed in advance: the largest economy in each World Bank region plus the three highest burdens
in 2024. This picked Saudi Arabia (a low-burden case) and left out Japan. Japan is discussed in
the text because it is the clearest example of high debt with a low burden, not because the
rule was changed.

### D10. Hypothesis H2 kept as originally worded

H2 predicted a "weak" association. The result is a moderate one (rank correlation 0.53). The
hypothesis was not reworded after the fact; the verdict is reported as "partly supported".

### D11. Decomposition summarised by means, with medians as a check

Means preserve the additivity of the LMDI contributions; medians do not. Medians are reported
in the output table and give the same qualitative picture.

### D12. The 20% threshold is descriptive

"More than a fifth of revenue" is a round, easily understood cut-off, not a risk threshold.
Counts above 10% and 30% are in `outputs/tables/high_burden_counts.csv`.

### D13. Swings are explained only where the components show why

Large year-on-year changes were checked against interest and revenue (see the validation
report). Lao PDR's 2024 jump has no explanation in the source and is flagged as uncertain
rather than explained.

### D14. Charts follow The Economist's conventions without its brand

The charts use The Economist's published conventions (red tag and rule, title stating the
finding, right-hand value axis, direct labels) and palette. They do not use its name, logo or
proprietary typeface; Fira Sans (open licence) stands in for Econ Sans.
