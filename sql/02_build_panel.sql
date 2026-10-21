-- Build the country-year analytical panel and the analysis sample.
-- Tokens in double braces ({{START_YEAR}} etc.) are filled in from
-- src/config.py by src/database.py before the script runs.

DROP TABLE IF EXISTS panel;
DROP TABLE IF EXISTS sample;

-- 1. Pivot the long observation table into one row per country-year and
--    derive the indicators. Net interest is the gap between the primary
--    balance (which excludes net interest) and the overall balance.
CREATE TABLE panel AS
WITH wide AS (
    SELECT
        iso3,
        year,
        MAX(CASE WHEN series_code = 'GGR_G01_GDP_PT'     THEN value END) AS revenue_gdp,
        MAX(CASE WHEN series_code = 'G_XWDG_G01_GDP_PT'  THEN value END) AS debt_gdp,
        MAX(CASE WHEN series_code = 'GGXONLB_G01_GDP_PT' THEN value END) AS primary_balance_gdp,
        MAX(CASE WHEN series_code = 'GGXCNL_G01_GDP_PT'  THEN value END) AS overall_balance_gdp,
        MAX(CASE WHEN series_code = 'NGDPD'              THEN value END) AS gdp_usd_bn,
        MAX(CASE WHEN series_code = 'ie'                 THEN value END) AS gross_interest_gdp_fpp,
        MAX(CASE WHEN series_code = 'rev'                THEN value END) AS revenue_gdp_fpp,
        MAX(CASE WHEN series_code = 'GC.XPN.INTP.RV.ZS'  THEN value END) AS interest_burden_wb,
        MAX(CASE WHEN series_code = 'SH.XPD.GHED.GD.ZS'  THEN value END) AS health_gdp,
        MAX(CASE WHEN series_code = 'SE.XPD.TOTL.GD.ZS'  THEN value END) AS education_gdp,
        MAX(CASE WHEN series_code = 'SP.POP.TOTL'        THEN value END) AS population
    FROM observation
    GROUP BY iso3, year
),
derived AS (
    SELECT
        w.*,
        w.primary_balance_gdp - w.overall_balance_gdp AS net_interest_gdp
    FROM wide AS w
)
SELECT
    c.iso3,
    c.name,
    c.region,
    c.income_group,
    d.year,
    CASE
        WHEN d.year <= {{END_YEAR}}      THEN 'historical'
        WHEN d.year =  {{ESTIMATE_YEAR}} THEN 'estimate'
        ELSE 'projection'
    END                                                          AS period_type,
    d.revenue_gdp,
    d.debt_gdp,
    d.primary_balance_gdp,
    d.overall_balance_gdp,
    d.net_interest_gdp,
    100.0 * d.net_interest_gdp / NULLIF(d.revenue_gdp, 0)        AS interest_burden,
    100.0 * d.net_interest_gdp / NULLIF(d.debt_gdp, 0)           AS implicit_rate,
    d.gross_interest_gdp_fpp,
    100.0 * d.gross_interest_gdp_fpp / NULLIF(d.revenue_gdp_fpp, 0) AS interest_burden_gross,
    d.interest_burden_wb,
    d.gdp_usd_bn,
    d.health_gdp,
    d.education_gdp,
    d.population
FROM derived AS d
JOIN country AS c USING (iso3);

CREATE UNIQUE INDEX idx_panel_country_year ON panel (iso3, year);

-- 2. Analysis sample: complete fiscal data for every year of the study
--    window, and net interest that is actually reported (not a placeholder
--    zero in most years). Small states are flagged for a robustness check.
CREATE TABLE sample AS
SELECT
    p.iso3,
    MAX(p.name)                                                   AS name,
    MAX(p.income_group)                                           AS income_group,
    MAX(p.region)                                                 AS region,
    MAX(CASE WHEN p.year = {{END_YEAR}} THEN p.population END)
        < {{SMALL_STATE_POPULATION}}                              AS is_small_state
FROM panel AS p
WHERE p.year BETWEEN {{START_YEAR}} AND {{END_YEAR}}
GROUP BY p.iso3
HAVING COUNT(p.revenue_gdp)         = {{END_YEAR}} - {{START_YEAR}} + 1
   AND COUNT(p.debt_gdp)            = {{END_YEAR}} - {{START_YEAR}} + 1
   AND COUNT(p.net_interest_gdp)    = {{END_YEAR}} - {{START_YEAR}} + 1
   AND SUM(ABS(p.net_interest_gdp) < 1e-9) <= {{MAX_ZERO_INTEREST_YEARS}}
   AND MAX(p.income_group) <> 'Not classified';
