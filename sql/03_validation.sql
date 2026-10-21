-- Data-quality checks. Each block is one named query that returns the rows it
-- flags, so an empty result means the check passed.
--   severity "error":  the pipeline stops if any row is returned
--   severity "review": rows are listed for review. A flag only says that a
--                      value is unusual, not why. Explanations live in
--                      audit/reviewed_cases.csv; rows without a matching
--                      entry are reported as UNREVIEWED.
-- Every review query returns the columns iso3 and year (year is NULL when the
-- flag applies to a country rather than a single year).

-- name: duplicate_country_years
-- severity: error
-- description: Each country appears at most once per year in the panel.
SELECT iso3, year, COUNT(*) AS n
FROM panel
GROUP BY iso3, year
HAVING COUNT(*) > 1;

-- name: identity_violations
-- severity: error
-- description: Burden must equal (net interest / debt) x debt / revenue, the identity used in the decomposition.
SELECT iso3, year, interest_burden, net_interest_to_debt * debt_gdp / revenue_gdp AS rebuilt
FROM panel
WHERE debt_gdp > 0 AND revenue_gdp > 0
  AND ABS(interest_burden - net_interest_to_debt * debt_gdp / revenue_gdp) > 1e-9;

-- name: sample_revenue_out_of_range
-- severity: error
-- description: General government revenue is positive and below 200% of GDP in the study window.
SELECT p.iso3, p.year, p.revenue_gdp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND (p.revenue_gdp <= 0 OR p.revenue_gdp >= 200);

-- name: sample_debt_out_of_range
-- severity: error
-- description: Gross debt is between 0% and 400% of GDP in the study window.
SELECT p.iso3, p.year, p.debt_gdp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND (p.debt_gdp < 0 OR p.debt_gdp > 400);

-- name: sample_incomplete_years
-- severity: error
-- description: Every sample country has a burden value in every year of the study window.
SELECT s.iso3, COUNT(p.interest_burden) AS years_with_data
FROM sample AS s
LEFT JOIN panel AS p
       ON p.iso3 = s.iso3 AND p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
GROUP BY s.iso3
HAVING COUNT(p.interest_burden) <> {{END_YEAR}} - {{START_YEAR}} + 1;

-- name: revenue_above_gdp
-- severity: review
-- description: Sample countries with revenue above 100% of GDP in at least one year of the study window.
SELECT p.iso3, NULL AS year, p.name, COUNT(*) AS years, ROUND(MAX(p.revenue_gdp), 1) AS max_revenue_gdp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND p.revenue_gdp > 100
GROUP BY p.iso3, p.name
ORDER BY p.iso3;

-- name: unmatched_imf_codes
-- severity: review
-- description: IMF codes with no match in the World Bank country list.
SELECT DISTINCT o.iso3, NULL AS year
FROM observation AS o
JOIN series AS sr USING (series_code)
LEFT JOIN country AS c USING (iso3)
WHERE sr.source LIKE 'IMF%' AND c.iso3 IS NULL
ORDER BY o.iso3;

-- name: excluded_countries
-- severity: review
-- description: Economies with some fiscal data in the study window that fail the sample rules.
SELECT
    p.iso3,
    NULL                                       AS year,
    MAX(p.name)                                AS name,
    MAX(p.income_group)                        AS income_group,
    COUNT(p.revenue_gdp)                       AS years_with_revenue,
    COUNT(p.debt_gdp)                          AS years_with_debt,
    COUNT(p.net_interest_gdp)                  AS years_with_net_interest,
    SUM(ABS(p.net_interest_gdp) < 1e-9)        AS zero_net_interest_years
FROM panel AS p
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND p.iso3 NOT IN (SELECT iso3 FROM sample)
GROUP BY p.iso3
HAVING COUNT(p.revenue_gdp) > 0
ORDER BY p.iso3;

-- name: negative_net_interest
-- severity: review
-- description: Sample countries whose net interest was negative in the end year (interest received exceeded interest paid).
SELECT p.iso3, p.year, p.name, ROUND(p.net_interest_gdp, 2) AS net_interest_gdp,
       ROUND(p.interest_burden, 1) AS net_burden,
       ROUND(p.interest_burden_gross, 1) AS gross_burden_fpp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}} AND p.net_interest_gdp < 0
ORDER BY p.interest_burden;

-- name: near_zero_net_burden
-- severity: review
-- description: Sample countries with a positive end-year net burden below {{NEAR_ZERO_BURDEN}}% of revenue; their logarithms are extreme and can drive log regressions.
SELECT p.iso3, p.year, p.name, ROUND(p.interest_burden, 4) AS net_burden,
       ROUND(p.interest_burden_gross, 1) AS gross_burden_fpp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}} AND p.interest_burden > 0 AND p.interest_burden < {{NEAR_ZERO_BURDEN}}
ORDER BY p.interest_burden;

-- name: cross_source_differences
-- severity: review
-- description: End-year differences above 5 points between the gross burden (IMF FPP, Dec 2025) and the net burden (Fiscal Monitor, Oct 2026). Interest income can explain part of a difference; so can different revenue figures, coverage, accounting and data vintage.
SELECT p.iso3, p.year, p.name, p.income_group,
       ROUND(p.interest_burden, 1)       AS net_burden,
       ROUND(p.interest_burden_gross, 1) AS gross_burden_fpp,
       ROUND(p.revenue_gdp, 1)           AS revenue_gdp_fm,
       ROUND(p.revenue_gdp_fpp, 1)       AS revenue_gdp_fpp,
       ROUND(p.interest_burden_gross - p.interest_burden, 1) AS difference
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}}
  AND ABS(p.interest_burden_gross - p.interest_burden) > 5
ORDER BY difference DESC;

-- name: large_annual_swings
-- severity: review
-- description: Year-on-year changes in the net burden above 15 points inside the study window.
SELECT cur.iso3, cur.year, cur.name,
       ROUND(prev.interest_burden, 1)  AS previous_burden,
       ROUND(cur.interest_burden, 1)   AS current_burden,
       ROUND(prev.net_interest_gdp, 2) AS previous_net_interest_gdp,
       ROUND(cur.net_interest_gdp, 2)  AS current_net_interest_gdp,
       ROUND(prev.revenue_gdp, 1)      AS previous_revenue_gdp,
       ROUND(cur.revenue_gdp, 1)       AS current_revenue_gdp
FROM panel AS cur
JOIN panel AS prev ON prev.iso3 = cur.iso3 AND prev.year = cur.year - 1
JOIN sample AS s ON s.iso3 = cur.iso3
WHERE cur.year BETWEEN {{START_YEAR}} + 1 AND {{END_YEAR}}
  AND ABS(cur.interest_burden - prev.interest_burden) > 15
ORDER BY ABS(cur.interest_burden - prev.interest_burden) DESC;
