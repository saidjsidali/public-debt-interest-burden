-- Analytical queries. Each named block is exported by src/database.py to
-- outputs/tables/<name>.csv. The Python analysis and the figures read those
-- files, so each number in the report can be traced to a query here or to a
-- function in src/analyze.py.

-- name: sample_funnel
-- description: How the 217 economies on the World Bank list become the analysis sample, step by step.
WITH per_country AS (
    SELECT
        c.iso3,
        c.income_group,
        SUM(p.revenue_gdp IS NOT NULL)                   AS revenue_years,
        SUM(p.debt_gdp IS NOT NULL)                      AS debt_years,
        SUM(p.net_interest_gdp IS NOT NULL)              AS net_interest_years,
        COALESCE(SUM(ABS(p.net_interest_gdp) < 1e-9), 0) AS zero_years
    FROM country AS c
    LEFT JOIN panel AS p
           ON p.iso3 = c.iso3 AND p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
    GROUP BY c.iso3, c.income_group
),
steps AS (
    SELECT
        iso3,
        1                                                         AS s1,
        revenue_years > 0                                         AS s2,
        revenue_years = {{END_YEAR}} - {{START_YEAR}} + 1
            AND debt_years = {{END_YEAR}} - {{START_YEAR}} + 1
            AND net_interest_years = {{END_YEAR}} - {{START_YEAR}} + 1 AS s3,
        zero_years <= {{MAX_ZERO_INTEREST_YEARS}}                 AS zero_ok,
        income_group <> 'Not classified'                          AS income_ok
    FROM per_country
)
SELECT 1 AS step, 'Economies on the World Bank country list' AS stage,
       SUM(s1) AS countries, 0 AS dropped, '' AS dropped_economies
FROM steps
UNION ALL
SELECT 2, 'With at least one year of Fiscal Monitor revenue data, 2015-2024',
       SUM(s2), SUM(s1) - SUM(s2),
       GROUP_CONCAT(CASE WHEN NOT s2 THEN iso3 END, ' ')
FROM steps
UNION ALL
SELECT 3, 'With revenue, gross debt and both balances in all ten years',
       SUM(s2 AND s3), SUM(s2) - SUM(s2 AND s3),
       GROUP_CONCAT(CASE WHEN s2 AND NOT s3 THEN iso3 END, ' ')
FROM steps
UNION ALL
SELECT 4, 'Net interest not exactly zero in five or more years',
       SUM(s3 AND zero_ok), SUM(s3) - SUM(s3 AND zero_ok),
       GROUP_CONCAT(CASE WHEN s3 AND NOT zero_ok THEN iso3 END, ' ')
FROM steps
UNION ALL
SELECT 5, 'With a World Bank income group (final sample)',
       SUM(s3 AND zero_ok AND income_ok), SUM(s3 AND zero_ok) - SUM(s3 AND zero_ok AND income_ok),
       GROUP_CONCAT(CASE WHEN s3 AND zero_ok AND NOT income_ok THEN iso3 END, ' ')
FROM steps
ORDER BY step;

-- name: sample_composition
-- description: Countries in the analysis sample by income group and region.
SELECT income_group, region, COUNT(*) AS countries, SUM(is_small_state) AS small_states
FROM sample
GROUP BY income_group, region
ORDER BY income_group, region;

-- name: burden_ranking
-- description: Net interest burden in the end year for every sample country, with its components.
SELECT
    RANK() OVER (ORDER BY p.interest_burden DESC) AS rank,
    p.iso3, p.name, p.income_group, p.region,
    p.interest_burden, p.interest_burden_gross, p.interest_burden_wb,
    p.net_interest_gdp, p.debt_gdp, p.revenue_gdp, p.net_interest_to_debt
FROM panel AS p
JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}}
ORDER BY rank;

-- name: group_medians
-- description: Median net burden, gross burden, debt, revenue and net-interest-to-debt factor by income group and year. Unweighted: the typical country.
WITH long AS (
    SELECT p.income_group AS grp, p.year, 'interest_burden' AS variable, p.interest_burden AS value
    FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    SELECT p.income_group, p.year, 'debt_gdp', p.debt_gdp FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    SELECT p.income_group, p.year, 'revenue_gdp', p.revenue_gdp FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    -- only defined where net interest is positive
    SELECT p.income_group, p.year, 'net_interest_to_debt',
           CASE WHEN p.net_interest_gdp > 0 THEN p.net_interest_to_debt END
    FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    SELECT p.income_group, p.year, 'net_interest_gdp', p.net_interest_gdp FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    SELECT p.income_group, p.year, 'interest_burden_gross', p.interest_burden_gross FROM panel AS p JOIN sample AS s USING (iso3)
),
with_total AS (
    SELECT * FROM long
    UNION ALL
    SELECT 'All countries', year, variable, value FROM long
),
ranked AS (
    SELECT grp, year, variable, value,
           ROW_NUMBER() OVER (PARTITION BY grp, year, variable ORDER BY value) AS rn,
           COUNT(*)     OVER (PARTITION BY grp, year, variable)                AS n
    FROM with_total
    WHERE value IS NOT NULL
      AND year BETWEEN {{START_YEAR}} AND {{FORECAST_END}}
)
SELECT grp AS income_group, year, variable, AVG(value) AS median, MAX(n) AS countries
FROM ranked
WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
GROUP BY grp, year, variable
ORDER BY variable, income_group, year;

-- name: pooled_burden
-- description: Total net interest as a share of total revenue across the sample, after converting both to US dollars. This equals a revenue-weighted average of country burdens (not a GDP-weighted average).
WITH base AS (
    SELECT p.income_group, p.year,
           p.net_interest_gdp * p.gdp_usd_bn / 100 AS net_interest_usd_bn,
           p.revenue_gdp      * p.gdp_usd_bn / 100 AS revenue_usd_bn,
           p.debt_gdp         * p.gdp_usd_bn / 100 AS debt_usd_bn,
           p.gdp_usd_bn
    FROM panel AS p JOIN sample AS s USING (iso3)
    WHERE p.year BETWEEN {{START_YEAR}} AND {{FORECAST_END}}
      AND p.gdp_usd_bn IS NOT NULL
),
grouped AS (
    SELECT income_group AS grp, year, net_interest_usd_bn, revenue_usd_bn, debt_usd_bn, gdp_usd_bn FROM base
    UNION ALL
    SELECT 'All countries', year, net_interest_usd_bn, revenue_usd_bn, debt_usd_bn, gdp_usd_bn FROM base
)
SELECT grp AS income_group, year,
       100.0 * SUM(net_interest_usd_bn) / SUM(revenue_usd_bn) AS pooled_burden,
       100.0 * SUM(debt_usd_bn)         / SUM(gdp_usd_bn)     AS pooled_debt_gdp,
       SUM(net_interest_usd_bn)                                AS net_interest_usd_bn,
       COUNT(*)                                                AS countries
FROM grouped
GROUP BY grp, year
ORDER BY income_group, year;

-- name: burden_change
-- description: Each country's net burden at the start, the break year, the end year and the latest estimate.
SELECT
    s.iso3, s.name, s.income_group, s.region,
    MAX(CASE WHEN p.year = {{START_YEAR}}    THEN p.interest_burden END) AS burden_start,
    MAX(CASE WHEN p.year = {{BREAK_YEAR}}    THEN p.interest_burden END) AS burden_break,
    MAX(CASE WHEN p.year = {{END_YEAR}}      THEN p.interest_burden END) AS burden_end,
    MAX(CASE WHEN p.year = {{ESTIMATE_YEAR}} THEN p.interest_burden END) AS burden_estimate,
    MAX(CASE WHEN p.year = {{END_YEAR}}      THEN p.interest_burden END)
      - MAX(CASE WHEN p.year = {{START_YEAR}} THEN p.interest_burden END) AS change_start_end,
    MAX(CASE WHEN p.year = {{END_YEAR}}      THEN p.interest_burden END)
      - MAX(CASE WHEN p.year = {{BREAK_YEAR}} THEN p.interest_burden END) AS change_break_end,
    MAX(CASE WHEN p.year = {{END_YEAR}}   THEN p.debt_gdp END)
      - MAX(CASE WHEN p.year = {{START_YEAR}} THEN p.debt_gdp END)        AS debt_change_start_end
FROM sample AS s
JOIN panel AS p USING (iso3)
GROUP BY s.iso3, s.name, s.income_group, s.region
ORDER BY change_start_end DESC;

-- name: high_burden_counts
-- description: Countries whose net burden is above the descriptive threshold, by year. Population uses each year's value, or the end-year value for later years.
WITH latest_pop AS (
    SELECT iso3, population FROM panel WHERE year = {{END_YEAR}}
)
SELECT
    p.year,
    COUNT(*)                                                         AS countries,
    SUM(p.interest_burden > {{HIGH_BURDEN_THRESHOLD}})               AS countries_above,
    100.0 * SUM(p.interest_burden > {{HIGH_BURDEN_THRESHOLD}}) / COUNT(*) AS share_countries_above,
    SUM(CASE WHEN p.interest_burden > {{HIGH_BURDEN_THRESHOLD}}
             THEN COALESCE(p.population, lp.population) ELSE 0 END) / 1e9 AS population_above_bn,
    SUM(p.interest_burden > 10)                                      AS countries_above_10,
    SUM(p.interest_burden > 30)                                      AS countries_above_30
FROM panel AS p
JOIN sample AS s USING (iso3)
LEFT JOIN latest_pop AS lp USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{FORECAST_END}}
GROUP BY p.year
ORDER BY p.year;

-- name: debt_burden_quadrants
-- description: End-year debt and net burden for each country, classified against the sample medians of both. A descriptive grouping only.
WITH end_year AS (
    SELECT p.* FROM panel AS p JOIN sample AS s USING (iso3) WHERE p.year = {{END_YEAR}}
),
med AS (
    SELECT
        (SELECT AVG(debt_gdp) FROM (
            SELECT debt_gdp FROM end_year ORDER BY debt_gdp
            LIMIT 2 - (SELECT COUNT(*) FROM end_year) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM end_year))) AS median_debt,
        (SELECT AVG(interest_burden) FROM (
            SELECT interest_burden FROM end_year ORDER BY interest_burden
            LIMIT 2 - (SELECT COUNT(*) FROM end_year) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM end_year))) AS median_burden
)
SELECT
    e.iso3, e.name, e.income_group, e.region,
    e.debt_gdp, e.revenue_gdp, e.net_interest_to_debt, e.interest_burden, e.gdp_usd_bn, e.population,
    m.median_debt, m.median_burden,
    CASE
        WHEN e.debt_gdp >= m.median_debt AND e.interest_burden >= m.median_burden THEN 'Above-median debt, above-median burden'
        WHEN e.debt_gdp >= m.median_debt AND e.interest_burden <  m.median_burden THEN 'Above-median debt, below-median burden'
        WHEN e.debt_gdp <  m.median_debt AND e.interest_burden >= m.median_burden THEN 'Below-median debt, above-median burden'
        ELSE 'Below-median debt, below-median burden'
    END AS group_label
FROM end_year AS e CROSS JOIN med AS m
ORDER BY group_label, e.interest_burden DESC;

-- name: interest_vs_social_spending
-- description: Net interest against government health and education spending, both in the same year: the latest year from 2019 where both values exist. Health and education can use different years. Population is the end-year value.
WITH health AS (
    SELECT p.iso3, p.year, p.net_interest_gdp, p.health_gdp,
           ROW_NUMBER() OVER (PARTITION BY p.iso3 ORDER BY p.year DESC) AS rn
    FROM panel AS p JOIN sample AS s USING (iso3)
    WHERE p.year BETWEEN 2019 AND {{END_YEAR}}
      AND p.health_gdp IS NOT NULL AND p.net_interest_gdp IS NOT NULL
),
education AS (
    SELECT p.iso3, p.year, p.net_interest_gdp, p.education_gdp,
           ROW_NUMBER() OVER (PARTITION BY p.iso3 ORDER BY p.year DESC) AS rn
    FROM panel AS p JOIN sample AS s USING (iso3)
    WHERE p.year BETWEEN 2019 AND {{END_YEAR}}
      AND p.education_gdp IS NOT NULL AND p.net_interest_gdp IS NOT NULL
)
SELECT
    s.iso3, s.name, s.income_group, s.region,
    pop.population,
    h.year              AS health_year,
    h.net_interest_gdp  AS interest_gdp_health_year,
    h.health_gdp,
    h.net_interest_gdp > h.health_gdp       AS interest_exceeds_health,
    e.year              AS education_year,
    e.net_interest_gdp  AS interest_gdp_education_year,
    e.education_gdp,
    e.net_interest_gdp > e.education_gdp    AS interest_exceeds_education
FROM sample AS s
LEFT JOIN health    AS h ON h.iso3 = s.iso3 AND h.rn = 1
LEFT JOIN education AS e ON e.iso3 = s.iso3 AND e.rn = 1
LEFT JOIN panel     AS pop ON pop.iso3 = s.iso3 AND pop.year = {{END_YEAR}}
ORDER BY s.iso3;

-- name: measure_comparison
-- description: Net burden (Fiscal Monitor), gross burden (IMF FPP) and central-government gross burden (World Bank) side by side.
SELECT p.iso3, p.name, p.income_group, p.year,
       p.interest_burden       AS net_fiscal_monitor,
       p.interest_burden_gross AS gross_fpp,
       p.interest_burden_wb    AS gross_central_wb
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
ORDER BY p.iso3, p.year;
