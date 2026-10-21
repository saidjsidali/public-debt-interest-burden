# Review log

Issues found while building and reviewing this project, how each was fixed, and how the fix was
verified. Automated data checks are reported separately in
[validation_report.md](validation_report.md), which is regenerated on every run.

**Independence.** The reviews below were carried out by the same AI system that wrote the code
and the text, working through the roles one at a time (data and code, econometrics, economic
interpretation, communication, reproducibility). They are not independent expert reviews. The
automated tests, the cross-implementation checks (SQL against pandas) and the clean-machine run
on GitHub Actions are the parts that do not depend on that judgement. A human review is still
recommended before relying on the results.

Severity: **High** would change a conclusion or a published number; **Medium** would mislead
a reader or break reproduction; **Low** is presentation.

## Data and code

| # | Issue | Severity | Fix | Verified by |
|---|---|---|---|---|
| 1 | The World Bank interest/revenue series loses coverage after 2019 (142 economies in 2015, 91 in 2024) and misses Egypt, Pakistan and Sri Lanka | High | Primary measure switched to Fiscal Monitor net interest; World Bank and FPP kept as cross-checks (decision D1) | Robustness table; `test_sql_medians_match_pandas` |
| 2 | Brunei, Libya and Macao record net interest as exactly 0.000 in most years (placeholder, not data) | Medium | Sample rule excludes economies with five or more exact-zero years (D3) | `test_placeholder_zero_interest_economies_are_excluded` |
| 3 | IMF codes `UVK` and `WBG` do not match World Bank codes, so Kosovo and West Bank and Gaza would silently drop out | Medium | Mapped to `XKX` and `PSE` on load | `test_imf_codes_are_mapped_to_world_bank_codes` |
| 4 | First validation run failed: Kiribati and Tuvalu report revenue above 100% of GDP | Medium | Checked: plausible (fishing licences, grants). Blocking range widened to 0–200%; review check added (D7) | Validation report; small-states robustness row |
| 5 | Kuwait's implicit rate computed as −853% entered the rate medians | Medium | Implicit rates and the decomposition use only positive net interest (D8) | `group_medians` table; `test_sql_medians_match_pandas` applies the same rule independently |
| 6 | The SQLite file could not be created when the project sat under a Windows path longer than 260 characters (the path was resolved through an app-data redirect) | Low | Project root taken as the absolute path without resolving links | Pipeline runs from both the original folder and a fresh clone |
| 7 | World Bank region names carry trailing spaces | Low | Stripped on load | Region names in `panel.csv` |

## Econometrics and statistics

| # | Issue | Severity | Fix | Verified by |
|---|---|---|---|---|
| 8 | H2 predicted a "weak" association; the estimate is moderate (ρ = 0.53) | Medium | Hypothesis left as written; verdict reported as "partly supported" (D10) | Report section 5.3 |
| 9 | The decomposition needs positive burdens, so the number of countries varies by period (166–170) | Low | Counts reported in the output table; net creditors excluded explicitly | `decomposition_by_group.csv` |
| 10 | Low-income results rest on 20 economies; the rate premium and the within-group correlation have intervals that include zero | Medium | Text says "imprecise" and reports the interval instead of claiming an effect | Report sections 5.3–5.4 |
| 11 | Means and medians of decomposition effects differ in size | Low | Means used (additive), medians reported alongside | Report section 5.5 |

## Economic interpretation

| # | Issue | Severity | Fix | Verified by |
|---|---|---|---|---|
| 12 | The fall in the median high-income burden on the net measure could be read as rich countries' interest costs falling | High | Gross-measure medians added: roughly flat (4.8% in 2015, 4.6% in 2024). Executive summary, results, H1 verdict, conclusion and README now say so | `median_burden_gross` in `key_numbers.json` |
| 13 | Falling burdens after default (Lebanon, Ghana, Sri Lanka) could be read as improvement | High | Explicit caveat in framework, results and policy sections | Component data in validation report |
| 14 | Large annual swings were at first attributed to causes before checking components | Medium | Each swing checked against interest and revenue; Lao PDR left unexplained rather than guessed (D13) | Validation report, `large_annual_swings` |
| 15 | Interest-versus-health comparison could imply crowding out | Medium | Framed as descriptive, with the alternative explanation stated | Report section 5.7; reasoning journal entry 6 |
| 16 | Literature review linked "original sin" to Nigeria's swings, where the 2024 move was a revenue increase | Low | Claim narrowed to Egypt 2024 and Pakistan 2023 and labelled as plausible, not shown | Literature review |

## Communication

| # | Issue | Severity | Fix | Verified by |
|---|---|---|---|---|
| 17 | A hand-counted statistic in the draft ("fifteen of the top 20" low- or lower-middle-income) was wrong: the data give 14 | High | All numbers in the README and report now come from `key_numbers.json` through templates; a missing value is an error | `test_documents_are_rendered_from_current_numbers`, `test_template_refuses_missing_numbers` |
| 18 | In the draft robustness table, the baseline row pointed at the small-states value | High | Specification labels renamed so every row is addressable; row rebuilt | Table 2 matches `robustness.csv` |
| 19 | Signed numbers produced double negatives ("subtracted -1.1") | Low | Signed format with neutral wording ("contributed −1.1") | Report section 5.5 |
| 20 | Chart labels and notes overlapped; axis titles collided with gridline labels | Low | Layout rebuilt on fixed inch/point positions; every chart inspected visually after each change | `outputs/figures/` |
| 21 | Figure file numbers did not match report order | Low | Files renamed to follow the report | `test_figures_exist` |
| 22 | Several sentences began with numerals | Low | Rephrased | Rendered report |
| 23 | Moody's methodology citation needed checking | Medium | Verified title and date (November 2019, superseded 2022 with the same factors); citation updated | References |

## Reproducibility

| Check | Result |
|---|---|
| `python run.py` from the committed snapshot | Completes in about 25 seconds on Windows 10, Python 3.14 |
| `pytest` | 20 tests pass |
| Fresh clone into a new folder, new virtual environment built only from `requirements.txt`, then `python run.py` and `pytest` (Windows, 21 October 2026) | 20 tests pass. README, report, `key_numbers.json` and all 19 result tables are byte-identical to the committed versions after line-ending normalisation; only the PDF's embedded metadata differs |
| GitHub Actions on Ubuntu (clean machine): run, test, and fail if the README or report differ from the committed ones | See the badge on the README |
