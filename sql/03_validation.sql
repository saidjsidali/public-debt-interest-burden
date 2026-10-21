-- Data-quality checks. Each block is one named query that returns the
-- offending rows, so an empty result means the check passed.
--   severity "error": the pipeline stops if any row is returned
--   severity "review": rows are expected and are explained in audit/validation_report.md

-- name: duplicate_country_years
-- severity: error
-- description: Each country appears at most once per year in the panel.
SELECT iso3, year, COUNT(*) AS n
FROM panel
GROUP BY iso3, year
HAVING COUNT(*) > 1;

-- name: identity_violations
-- severity: error
-- description: Interest burden must equal implicit rate x debt / revenue (the decomposition relies on it).
SELECT iso3, year, interest_burden, implicit_rate * debt_gdp / revenue_gdp AS rebuilt
FROM panel
WHERE debt_gdp > 0 AND revenue_gdp > 0
  AND ABS(interest_burden - implicit_rate * debt_gdp / revenue_gdp) > 1e-9;

-- name: sample_revenue_out_of_range
-- severity: error
-- description: General government revenue positive and below 200 per cent of GDP in the study window.
SELECT p.iso3, p.year, p.revenue_gdp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND (p.revenue_gdp <= 0 OR p.revenue_gdp >= 200);

-- name: revenue_above_gdp
-- severity: review
-- description: Revenue above 100 per cent of GDP: Pacific micro-states whose fishing-licence fees, grants and trust-fund income are large relative to GDP.
SELECT p.iso3, p.name, COUNT(*) AS years, ROUND(MAX(p.revenue_gdp), 1) AS max_revenue_gdp
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND p.revenue_gdp > 100
GROUP BY p.iso3, p.name;

-- name: sample_debt_out_of_range
-- severity: error
-- description: Gross debt non-negative and below 400 per cent of GDP in the study window.
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

-- name: unmatched_imf_codes
-- severity: review
-- description: IMF codes with no World Bank country match (regional aggregates, plus economies the World Bank does not list).
SELECT DISTINCT o.iso3
FROM observation AS o
JOIN series AS sr USING (series_code)
LEFT JOIN country AS c USING (iso3)
WHERE sr.source LIKE 'IMF%' AND c.iso3 IS NULL
ORDER BY o.iso3;

-- name: excluded_countries
-- severity: review
-- description: Economies with some fiscal data that fail the sample rules, and why.
SELECT
    p.iso3,
    MAX(p.name)                                AS name,
    MAX(p.income_group)                        AS income_group,
    COUNT(p.revenue_gdp)                       AS years_with_revenue,
    COUNT(p.debt_gdp)                          AS years_with_debt,
    COUNT(p.net_interest_gdp)                  AS years_with_interest,
    SUM(ABS(p.net_interest_gdp) < 1e-9)        AS zero_interest_years
FROM panel AS p
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
  AND p.iso3 NOT IN (SELECT iso3 FROM sample)
GROUP BY p.iso3
HAVING COUNT(p.revenue_gdp) > 0
ORDER BY p.iso3;

-- name: negative_net_interest
-- severity: review
-- description: Sample governments that earn more interest than they pay in the end year (net creditors).
SELECT p.iso3, p.name, ROUND(p.net_interest_gdp, 2) AS net_interest_gdp,
       ROUND(p.interest_burden, 1) AS interest_burden,
       ROUND(p.interest_burden_gross, 1) AS interest_burden_gross
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}} AND p.net_interest_gdp < 0
ORDER BY p.interest_burden;

-- name: large_net_gross_gaps
-- severity: review
-- description: End-year gaps above 5 points between the net (Fiscal Monitor) and gross (FPP) burden measures.
SELECT p.iso3, p.name, p.income_group,
       ROUND(p.interest_burden, 1)       AS net_burden,
       ROUND(p.interest_burden_gross, 1) AS gross_burden,
       ROUND(p.interest_burden_gross - p.interest_burden, 1) AS gap
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}}
  AND ABS(p.interest_burden_gross - p.interest_burden) > 5
ORDER BY gap DESC;

-- name: large_annual_swings
-- severity: review
-- description: Year-on-year changes in the burden above 15 points inside the study window.
SELECT cur.iso3, cur.name, cur.year,
       ROUND(prev.interest_burden, 1) AS previous,
       ROUND(cur.interest_burden, 1)  AS current
FROM panel AS cur
JOIN panel AS prev ON prev.iso3 = cur.iso3 AND prev.year = cur.year - 1
JOIN sample AS s ON s.iso3 = cur.iso3
WHERE cur.year BETWEEN {{START_YEAR}} + 1 AND {{END_YEAR}}
  AND ABS(cur.interest_burden - prev.interest_burden) > 15
ORDER BY ABS(cur.interest_burden - prev.interest_burden) DESC;
