# Repair register

Revision of the project after an external audit (reviewed version: commit `22e772a`). The
repairs were implemented by Claude (an AI assistant) on 21 October 2026 on the branch
`repair/audit-fixes`; they have not been published. Statuses: **fixed**, **qualified** (claim
narrowed or labelled), **unresolved** (needs information that was not available), **not done**
(optional item, with the reason).

## Baseline

| Item | Result |
|---|---|
| Version and environment | Commit `22e772a`; Windows 10, Python 3.14.7, packages as in `requirements.txt` |
| `python run.py` and `pytest` on the baseline | Ran; 20 tests passed; README, report Markdown and all tables identical to the committed files (the PDF differs only in export metadata) |
| Audit numbers re-checked with a separate script | All confirmed: PDF links to a local workspace (4, on pages 3, 4, 4, 7); matched medians 5.828 / 6.957 / 7.359; total 6.358 vs GDP-weighted 7.469; Canada burden 0.0139%; R² 0.250 → 0.321 without Canada; Japan and Canada largest Cook's distances; decomposition samples 166 / 170 / 169, common 165; 123 largest-signed (2 not positive) vs 107 largest-absolute; India prose paired 2024 interest with 2023 health |

## Register

| # | Issue | Evidence | Decision | Main files | Verification | Status |
|---|---|---|---|---|---|---|
| 1 | Robustness note said the measure explained most of the net–FPP gap | Matched medians 5.8 → 7.0 (same countries) → 7.4 (gross) | Rewrote note; added matched-sample table and Figure 5 | `analyze.py`, template, `fig5` | `test_matched_samples_change_one_thing_at_a_time`; independent check | fixed |
| 2 | Net interest ÷ gross debt called an "implicit rate" | Uses net interest and gross debt; Canada and Kuwait cases | Renamed `net_interest_to_debt`; described as an accounting factor | SQL, `analyze.py`, dictionary, figures, text | Stale-term search; identity test | fixed |
| 3 | Causal wording about interest rates | LMDI is an identity | Two-factor split in the main text; three-factor in the appendix; neutral titles | template, `figA1` | Text review | fixed |
| 4 | Decomposition samples not reported; no common-sample check | 166 / 170 / 169 countries | Samples reported; common sample (165) added | `analyze.py`, template | `test_common_sample_...` | fixed |
| 5 | "72%" dominance counted negative contributions | 2 of 123 were not positive | Defined "largest positive" (121) and "largest absolute" (107) | `analyze.py`, template | `test_dominance_counts_only_positive_...` | fixed |
| 6 | R² headline unstable; no influence checks | R² 0.25 → 0.32 without Canada | Cook's distance, leverage, leave-one-out range (0.22–0.32), levels model; Canada kept | `analyze.py`, template | `test_leave_one_out_range_...`; `test_log_regressions_use_only_positive_...` | fixed |
| 7 | Revenue fit and coefficient presented as a mechanism | Revenue is the denominator of the burden | Stated that the fit is partly by construction | template | Text review | qualified |
| 8 | "Unrelated" claim from an imprecise coefficient | 0.10 (−0.26 to 0.46) | "Cannot estimate this relationship precisely" | template | Text review | fixed |
| 9 | "Revenue is the strongest lever" | The identity does not rank policies | Removed; illustrative arithmetic with stated assumptions | template, README | Stale-term search | fixed |
| 10 | Aggregate called GDP-weighted | Total/total = revenue-weighted (6.36 vs 7.47) | Renamed "total net interest / total revenue"; table `pooled_burden` | SQL, template, `fig2` | `test_pooled_burden_is_total_over_total_and_revenue_weighted` | fixed |
| 11 | India sentence paired different years | 2024 interest vs 2023 health | Uses matched 2023 values (5.29% and 1.30%); year distribution stated | template | `test_social_spending_pairs_values_from_the_same_year`; independent check | fixed |
| 12 | Claim that interest "cannot be cut" | Interest changes with refinancing, floating rates, asset income | Reworded | template | Text review | fixed |
| 13 | Falling burdens after default read as unpaid interest | Cash vs accrual not checked | Narrowed: data alone do not show the reason | template, `reviewed_cases.csv` | Text review | qualified |
| 14 | Cross-source gaps called interest income | Different vintages, revenue, coverage | Renamed "cross-source differences"; Myanmar revenue difference noted | SQL, register, `figA3` | Validation report | fixed |
| 15 | "Net creditor" from a flow | A negative flow does not show the balance sheet | Literal flow wording | SQL, text | Stale-term search | fixed |
| 16 | Repeated zeros called placeholders | Only Brunei is removed by the rule; Libya and Macao fail earlier | Treated as a review flag; Brunei sensitivity added | SQL, `analyze.py`, text | `test_sample_funnel_adds_up` | qualified (cause unresolved) |
| 17 | No full sample funnel | 217 → 193 → 182 → 181 | `sample_funnel` query and Table 1 | SQL, template | `test_sample_funnel_adds_up` | fixed |
| 18 | Hard-coded review explanations would certify new data | Text in `validate.py` | `reviewed_cases.csv` keyed by vintage; new flags are UNREVIEWED; full CSV export of flags | `validate.py`, `audit/` | `test_new_flags_are_unreviewed_...`; `test_every_flagged_row_is_exported` | fixed |
| 19 | `--refresh` overwrote the published snapshot | `acquire.py` wrote to `data/raw` | Refresh writes `data/snapshots/<date>/` with JSON responses and a manifest; startup checksum check | `acquire.py`, `snapshot.py`, `run.py` | `test_snapshot_matches_manifest`; `test_refresh_never_overwrites_...` | fixed |
| 19a | No safe way to analyse a new snapshot | The first fix told users to change `config.DATA_RAW`; the checksum check would then stop the run, and a run would overwrite the published README, report and outputs | Draft mode: `SNAPSHOT_DIR=<folder> python run.py` checks the snapshot against its own manifest (now required) and writes only to `*_draft` paths, each document with a DRAFT banner; draft paths are git-ignored | `config.py`, `run.py`, `snapshot.py`, `validate.py`, `build_report.py`, README, `data/README.md` | `test_check_inputs_detects_...`; `test_draft_mode_writes_every_output_to_separate_paths`; `test_draft_documents_are_marked_...`; full draft run on a copy of `data/raw` (see Verification) | fixed |
| 20 | PDF links pointed to a local workspace | 4 annotations | Relative links rewritten to GitHub URLs | `build_report.py` | `test_pdf_has_no_local_paths_or_local_links`; annotation scan (18 links, all public) | fixed |
| 21 | Case-study order hard-coded | `figures.py` list | Order taken from `case_studies.csv` | `analyze.py`, `figures.py` | Visual check | fixed |
| 22 | Ten case panels on one −25 to 100 scale | Large economies looked flat | Two groups with labelled scales | `fig6` | Visual check | fixed |
| 23 | Config claimed all assumptions were central | Text and scales are fixed elsewhere | Docstring rewritten; fixed scope stated | `config.py`, README | Text review | fixed |
| 24 | CI scope described too broadly | No PDF check | CI scope described; numeric-tolerance comparison added | workflow, `compare_numbers.py`, README | CI not run in this revision (not pushed) | fixed (CI pending) |
| 25 | Contribution statement inaccurate | Disclosure removed in `ad16a94` | Accurate statement in README and report; no claims about the author's checks | templates | Text review | fixed |
| 26 | Unsupported chronology ("written before results") | Not shown by Git history | Described as retrospective, with the known order stated as unverifiable | research docs, template | Text review | fixed |
| 27 | Repeated material across documents | Problem statement, reasoning journal, review log | Removed these three; one purpose per document; this register replaces the review log | `research/`, `audit/` | – | fixed |
| 28 | References without links | – | DOI or institutional links; each source linked to the claim it supports | template, `literature_review.md` | Links checked by web search | fixed |
| 29 | Coverage of highlighted countries undocumented | IMF appendix returned "Access Denied" | Partial table with sources; rest marked unresolved | template (Appendix C) | – | unresolved |
| 30 | Chart style | Author's request | Newspaper style (PT Serif headlines, grey grid, left labels); no newspaper names. Final pass: white halo behind point labels, shorter quadrant labels in Figure 4, leader lines for China (Figure 4) and the United States (Figure A3), China labelled inside its bubble (Figure A2) | `style.py`, `figures.py`, CSS | Every chart and PDF page inspected after the last change | fixed |
| 31 | Gross effective-rate sensitivity | Optional in the audit | Not built: comparable lagged debt and GDP denominators would be needed | – | – | not done |
| 32 | Historical income-group sensitivity | Optional | Not built | – | – | not done |
| 33 | Table A2 "median change" could be read as the change in the median | Baseline row shows 0.9; the median itself rose 4.5 → 5.8 (1.3 points) | Note under Table A2 states that it is the median of country changes | template | Visual check of page 11 | fixed |
| 34 | PDF links to repository files point to `main` | `regression_influence.csv` exists only on this branch | Kept: links are correct once the branch is merged into `main`; until then that link returns "not found" on GitHub | `config.REPO_LINK_REF` | Annotation scan | open until merge |
| 35 | Report length | The repair brief suggests a main report of about 6–8 pages | Main text is 10 pages (plus 5 pages of appendices and references) because it now includes the sample funnel, the matched comparison and the influence checks; not shortened further | template | Page count | not done |

## Before and after

| Item | Before | After | Reason |
|---|---|---|---|
| Gap between net and FPP gross medians | "Mostly the net-versus-gross concept" | About 74% from country coverage (+1.13 of 1.53 points), 26% from the measure | Matched-sample comparison |
| 2021–24 "rate" statistic | Rate largest in 72% of countries | Largest positive in 121 of 170 (71%); largest absolute in 107 | Definition corrected |
| R² of debt alone | "About a quarter of cross-country differences" | 0.25 for log burdens of 175 countries; 0.22–0.32 leaving out one country; 0.32 without Canada | Scope and sensitivity stated |
| Model 4 debt coefficient | "Implicit rates are unrelated to debt" | Not estimated precisely (0.10, −0.26 to 0.46) | Uncertainty |
| 2024 total burden (6.4%) | "GDP-weighted" | Total net interest / total revenue (revenue-weighted); GDP-weighted average would be 7.5% | Label |
| India example | Interest 4.9% (2024) vs health 1.3% (2023) | 5.29% vs 1.30%, both 2023 | Same-year values |
| Repeated-zero exclusions | Brunei, Libya and Macao excluded for zero interest | Only Brunei removed by this rule; cause unresolved; median with Brunei 5.80% vs 5.83% | Funnel |
| H3 verdict | Supported | Supported for revenue (partly by construction); factor differences for middle income; low income imprecise | Regression interpretation |
| H4 verdict | Supported | Accounting pattern consistent; interest-rate effect not estimated | Identity, not causal |
| Policy implications | "Revenue is the main lever" | Illustration with stated assumptions; no ranking of policies | Not estimated |
| Contribution statement | "Analysis, code and report by Sidali Saidj" | Accurate account of Claude's role | Accuracy |
| Headline levels and trends | — | Unchanged (same data and formulas): median 4.5% → 5.8%; 20 countries above 20%; Spearman 0.53 | — |

## Verification (21 October 2026)

| Check | Command | Result |
|---|---|---|
| Full pipeline with PDF | `python run.py` | Completed |
| Tests | `pytest` | 40 passed |
| Independent recomputation from the raw CSVs | `python audit/independent_check.py` | 17 of 17 headline numbers match |
| Clean environment (before draft mode) | Fresh clone of the branch, new virtual environment from `requirements.txt`, `python run.py --no-pdf`, `pytest` | 37 passed (all tests at that time); `compare_numbers.py`: 0 differences; README, report Markdown, tables and validation report unchanged |
| Draft mode | Copy of `data/raw` without a manifest, then with one, run with `SNAPSHOT_DIR` | Without a manifest the run stops; with one it completes. SHA-256 of all 100 published files identical before and after; draft key numbers 0 differences from the published ones; draft README, report and validation report carry the DRAFT banner; draft files removed afterwards |
| PDF links and paths | Annotation scan with pypdf and byte search | 18 link annotations (16 distinct), all public URLs; 2 point to files in the repository (see row 34); no local paths |
| Visual inspection | All 9 charts and all 15 PDF pages viewed after the last change | No clipped or overlapping text; every table note is on the same page as its table |
| Stale-claim search | Text search for old terms in tracked files | Remaining matches are intentional (explaining what is not claimed, or quoting the original H4) |
| GitHub Actions | – | Not run: nothing was pushed |

## Unresolved

1. Country coverage, fiscal-year and accounting notes for most highlighted countries (IMF appendix not accessible).
2. Whether Brunei's zero net interest means "not recorded" or "zero".
3. Cause of Lao PDR's 2024 jump in net interest.
4. Cash versus accrual treatment of interest after the Lebanon, Ghana and Sri Lanka defaults.
5. Original JSON responses of the published snapshot (not kept in 2026-10-21 download).
6. Review notes in `audit/reviewed_cases.csv` were written by Claude; none has been checked by the author.
7. The author's own verification and ownership steps (see `research/learning_note.md`, section 7).
8. GitHub Actions has not run on this branch, and the PDF link to `regression_influence.csv` works only after the branch is merged into `main` (row 34).
