-- Analytical queries. Each named block is exported by src/database.py to
-- outputs/tables/<name>.csv; the Python analysis and the figures read those
-- files, so every number in the report can be traced to one query here.

-- name: sample_composition
-- description: Countries in the analysis sample by income group and region.
SELECT income_group, region, COUNT(*) AS countries, SUM(is_small_state) AS small_states
FROM sample
GROUP BY income_group, region
ORDER BY income_group, region;

-- name: burden_ranking
-- description: Interest burden in the end year for every sample country, with its components.
SELECT
    RANK() OVER (ORDER BY p.interest_burden DESC) AS rank,
    p.iso3, p.name, p.income_group, p.region,
    p.interest_burden, p.interest_burden_gross, p.interest_burden_wb,
    p.net_interest_gdp, p.debt_gdp, p.revenue_gdp, p.implicit_rate
FROM panel AS p
JOIN sample AS s USING (iso3)
WHERE p.year = {{END_YEAR}}
ORDER BY rank;

-- name: group_medians
-- description: Median burden, debt, revenue and implicit rate by income group and year (unweighted: the typical country).
WITH long AS (
    SELECT p.income_group AS grp, p.year, 'interest_burden' AS variable, p.interest_burden AS value
    FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    SELECT p.income_group, p.year, 'debt_gdp', p.debt_gdp FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    SELECT p.income_group, p.year, 'revenue_gdp', p.revenue_gdp FROM panel AS p JOIN sample AS s USING (iso3)
    UNION ALL
    -- an implicit rate has no meaning for net creditors, whose net interest is negative
    SELECT p.income_group, p.year, 'implicit_rate', CASE WHEN p.net_interest_gdp > 0 THEN p.implicit_rate END
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

-- name: aggregate_burden
-- description: GDP-weighted aggregate burden, i.e. total net interest over total revenue in US dollars.
WITH base AS (
    SELECT p.income_group, p.year,
           p.net_interest_gdp * p.gdp_usd_bn / 100 AS interest_usd_bn,
           p.revenue_gdp      * p.gdp_usd_bn / 100 AS revenue_usd_bn,
           p.debt_gdp         * p.gdp_usd_bn / 100 AS debt_usd_bn,
           p.gdp_usd_bn
    FROM panel AS p JOIN sample AS s USING (iso3)
    WHERE p.year BETWEEN {{START_YEAR}} AND {{FORECAST_END}}
      AND p.gdp_usd_bn IS NOT NULL
),
grouped AS (
    SELECT income_group AS grp, year, interest_usd_bn, revenue_usd_bn, debt_usd_bn, gdp_usd_bn FROM base
    UNION ALL
    SELECT 'All countries', year, interest_usd_bn, revenue_usd_bn, debt_usd_bn, gdp_usd_bn FROM base
)
SELECT grp AS income_group, year,
       100.0 * SUM(interest_usd_bn) / SUM(revenue_usd_bn) AS interest_burden,
       100.0 * SUM(debt_usd_bn)     / SUM(gdp_usd_bn)     AS debt_gdp,
       SUM(interest_usd_bn)                                AS net_interest_usd_bn,
       COUNT(*)                                            AS countries
FROM grouped
GROUP BY grp, year
ORDER BY income_group, year;

-- name: burden_change
-- description: Each country's burden at the start, the break year, the end year and the latest estimate.
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
-- description: Countries spending more than the descriptive threshold share of revenue on interest, by year.
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
-- description: End-year debt and burden for each country, classified against the sample medians of both.
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
    e.debt_gdp, e.revenue_gdp, e.implicit_rate, e.interest_burden, e.gdp_usd_bn, e.population,
    m.median_debt, m.median_burden,
    CASE
        WHEN e.debt_gdp >= m.median_debt AND e.interest_burden >= m.median_burden THEN 'High debt, high burden'
        WHEN e.debt_gdp >= m.median_debt AND e.interest_burden <  m.median_burden THEN 'High debt, low burden'
        WHEN e.debt_gdp <  m.median_debt AND e.interest_burden >= m.median_burden THEN 'Low debt, high burden'
        ELSE 'Low debt, low burden'
    END AS quadrant
FROM end_year AS e CROSS JOIN med AS m
ORDER BY quadrant, e.interest_burden DESC;

-- name: interest_vs_social_spending
-- description: Net interest against government health and education spending, each in the latest year (from 2019) where both are reported.
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
-- description: Net (Fiscal Monitor), gross (FPP) and central-government (World Bank) burdens side by side.
SELECT p.iso3, p.name, p.income_group, p.year,
       p.interest_burden       AS net_general_government,
       p.interest_burden_gross AS gross_general_government,
       p.interest_burden_wb    AS gross_central_government
FROM panel AS p JOIN sample AS s USING (iso3)
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
ORDER BY p.iso3, p.year;
