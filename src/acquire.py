"""Download the raw data from the IMF DataMapper and World Bank APIs.

The files written to data/raw/ are the frozen inputs of the study. The
repository ships with a snapshot taken in October 2026; re-running this
script replaces it with whatever the providers publish today, which will
change the numbers once a new IMF vintage is released (each April and
October). The retrieval log records exactly what was downloaded and when.
"""

import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from config import (DATA_RAW, IMF_API, IMF_FIRST_YEAR, IMF_SERIES, WB_API,
                    WB_FIRST_YEAR, WB_LAST_YEAR, WB_SERIES)

TIMEOUT = 120


def _get(url, params=None, attempts=4):
    for i in range(attempts):
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError):
            if i == attempts - 1:
                raise
            time.sleep(2 ** i)


def fetch_imf():
    """All countries and years for each IMF series, in long format."""
    meta = _get(f"{IMF_API}/indicators")["indicators"]
    rows, vintages = [], {}
    for code in IMF_SERIES:
        values = _get(f"{IMF_API}/{code}")["values"][code]
        vintages[code] = meta[code].get("source")
        for iso3, by_year in values.items():
            for year, value in by_year.items():
                if value is not None and int(year) >= IMF_FIRST_YEAR:
                    rows.append((code, iso3, int(year), float(value)))
    df = pd.DataFrame(rows, columns=["series_code", "iso3", "year", "value"])
    return df.sort_values(["series_code", "iso3", "year"]), vintages


def fetch_wb():
    rows, updated = [], {}
    for code in WB_SERIES:
        page = 1
        while True:
            meta, data = _get(
                f"{WB_API}/country/all/indicator/{code}",
                {"format": "json", "date": f"{WB_FIRST_YEAR}:{WB_LAST_YEAR}",
                 "per_page": 20000, "page": page},
            )
            updated[code] = meta.get("lastupdated")
            for d in data or []:
                if d["value"] is not None and d["countryiso3code"]:
                    rows.append((code, d["countryiso3code"], int(d["date"]), float(d["value"])))
            if page >= meta["pages"]:
                break
            page += 1
    df = pd.DataFrame(rows, columns=["series_code", "iso3", "year", "value"])
    return df.sort_values(["series_code", "iso3", "year"]), updated


def fetch_wb_countries():
    """Country list with World Bank region and current income classification."""
    _, data = _get(f"{WB_API}/country", {"format": "json", "per_page": 400})
    df = pd.DataFrame(
        [(c["id"], c["name"], c["region"]["value"], c["incomeLevel"]["value"]) for c in data],
        columns=["iso3", "name", "region", "income_group"],
    )
    return df[df["region"] != "Aggregates"].sort_values("iso3")


def main():
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    imf, imf_vintages = fetch_imf()
    wb, wb_updated = fetch_wb()
    countries = fetch_wb_countries()

    imf.to_csv(DATA_RAW / "imf_datamapper.csv", index=False)
    wb.to_csv(DATA_RAW / "wb_wdi.csv", index=False)
    countries.to_csv(DATA_RAW / "wb_countries.csv", index=False)

    log = {
        "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "imf_datamapper": {
            "endpoint": f"{IMF_API}/<series_code>",
            "vintage_by_series": imf_vintages,
            "rows": len(imf),
        },
        "world_bank_wdi": {
            "endpoint": f"{WB_API}/country/all/indicator/<series_code>",
            "years": f"{WB_FIRST_YEAR}-{WB_LAST_YEAR}",
            "last_updated_by_series": wb_updated,
            "rows": len(wb),
        },
        "world_bank_countries": {"endpoint": f"{WB_API}/country", "rows": len(countries)},
    }
    (DATA_RAW / "retrieval_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"IMF rows {len(imf):,} | WB rows {len(wb):,} | countries {len(countries)}")


if __name__ == "__main__":
    main()
