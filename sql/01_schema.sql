-- Relational store for the raw inputs.
-- One long observation table keeps every source in the same shape; the
-- primary key makes duplicate country-year-series rows impossible to load.

DROP TABLE IF EXISTS observation;
DROP TABLE IF EXISTS series;
DROP TABLE IF EXISTS country;

CREATE TABLE country (
    iso3          TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    region        TEXT NOT NULL,
    income_group  TEXT NOT NULL      -- World Bank classification at retrieval date
);

CREATE TABLE series (
    series_code   TEXT PRIMARY KEY,
    source        TEXT NOT NULL,
    label         TEXT NOT NULL,
    unit          TEXT NOT NULL
);

CREATE TABLE observation (
    series_code   TEXT    NOT NULL REFERENCES series (series_code),
    iso3          TEXT    NOT NULL,  -- not a foreign key: IMF files also carry regional aggregates
    year          INTEGER NOT NULL,
    value         REAL    NOT NULL,
    PRIMARY KEY (series_code, iso3, year)
);

CREATE INDEX idx_observation_country_year ON observation (iso3, year);
