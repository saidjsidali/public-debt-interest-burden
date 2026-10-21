"""Load the raw snapshot into SQLite, build the panel and run the SQL files.

SQLite ships with Python, so the database needs no server and the whole
pipeline runs on a clean machine with only the packages in requirements.txt.
"""

import re
import sqlite3

import pandas as pd

import config

TOKENS = {
    "START_YEAR": config.START_YEAR,
    "BREAK_YEAR": config.BREAK_YEAR,
    "END_YEAR": config.END_YEAR,
    "ESTIMATE_YEAR": config.ESTIMATE_YEAR,
    "FORECAST_END": config.FORECAST_END,
    "MAX_ZERO_INTEREST_YEARS": config.MAX_ZERO_INTEREST_YEARS,
    "SMALL_STATE_POPULATION": config.SMALL_STATE_POPULATION,
    "HIGH_BURDEN_THRESHOLD": config.HIGH_BURDEN_THRESHOLD,
}


def render(sql):
    """Fill {{TOKEN}} placeholders with values from config."""
    def sub(match):
        key = match.group(1)
        if key not in TOKENS:
            raise KeyError(f"Unknown SQL token {{{{{key}}}}}")
        return str(TOKENS[key])
    return re.sub(r"\{\{(\w+)\}\}", sub, sql)


def read_sql(name):
    return render((config.SQL_DIR / name).read_text(encoding="utf-8"))


def named_queries(name):
    """Split a SQL file into {name: (metadata, query)} using '-- name:' headers."""
    blocks = re.split(r"^-- name:\s*", read_sql(name), flags=re.M)[1:]
    out = {}
    for block in blocks:
        header, _, body = block.partition("\n")
        meta = dict(re.findall(r"^-- (\w+):\s*(.+)$", body, flags=re.M))
        query = "\n".join(l for l in body.splitlines() if not l.startswith("--")).strip()
        out[header.strip()] = (meta, query.rstrip(";"))
    return out


def connect():
    return sqlite3.connect(config.DB_PATH)


def _load_raw(con):
    countries = pd.read_csv(config.DATA_RAW / "wb_countries.csv", keep_default_na=False)
    countries = countries.apply(lambda s: s.str.strip())
    countries.to_sql("country", con, if_exists="append", index=False)

    series = [(code, *meta) for code, meta in {**config.IMF_SERIES, **config.WB_SERIES}.items()]
    con.executemany("INSERT INTO series VALUES (?, ?, ?, ?)", series)

    imf = pd.read_csv(config.DATA_RAW / "imf_datamapper.csv", keep_default_na=False)
    imf["iso3"] = imf["iso3"].replace(config.IMF_TO_WB_ISO)
    wb = pd.read_csv(config.DATA_RAW / "wb_wdi.csv", keep_default_na=False)
    obs = pd.concat([imf, wb], ignore_index=True)
    # The primary key rejects duplicates, so a clash here is a data error.
    obs.to_sql("observation", con, if_exists="append", index=False)


def build():
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()
    with connect() as con:
        con.executescript(read_sql("01_schema.sql"))
        _load_raw(con)
        con.executescript(read_sql("02_build_panel.sql"))
        panel = pd.read_sql("SELECT * FROM panel ORDER BY iso3, year", con)
        sample = pd.read_sql("SELECT * FROM sample ORDER BY iso3", con)
    panel.to_csv(config.PANEL_CSV, index=False)
    sample.to_csv(config.DATA_PROCESSED / "sample.csv", index=False)
    print(f"Panel: {len(panel):,} country-years | sample: {len(sample)} countries")
    return panel, sample


def run_validation():
    """Run every check in 03_validation.sql; stop on any failed 'error' check."""
    results = {}
    with connect() as con:
        for name, (meta, query) in named_queries("03_validation.sql").items():
            df = pd.read_sql(query, con)
            results[name] = (meta, df)
    failed = [n for n, (m, df) in results.items() if m.get("severity") == "error" and len(df)]
    if failed:
        raise RuntimeError(f"Data validation failed: {', '.join(failed)}")
    return results


def run_analysis_queries():
    config.TABLES.mkdir(parents=True, exist_ok=True)
    tables = {}
    with connect() as con:
        for name, (_, query) in named_queries("04_analysis.sql").items():
            df = pd.read_sql(query, con)
            df.to_csv(config.TABLES / f"{name}.csv", index=False)
            tables[name] = df
    return tables
