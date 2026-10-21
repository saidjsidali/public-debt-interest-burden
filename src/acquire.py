"""Download a new data snapshot from the IMF DataMapper and World Bank APIs.

The published results use the snapshot in data/raw/ (retrieved 21 October
2026). This script never overwrites it. Each run writes a new dated folder
under data/snapshots/ with:

- tidy CSV extracts in the same format as data/raw/,
- the original JSON responses (json/),
- a retrieval log and a checksum manifest.

Using a new snapshot is a separate step: the IMF revises its data twice a
year, so the numbers, the reviewed cases in audit/ and the report text all
need a new review before publication.
"""

import gzip
import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

import config
import snapshot

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


class Recorder:
    """Keeps every API response so the snapshot can be traced to its source."""

    def __init__(self, folder):
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)
        self.count = 0

    def get(self, url, params=None):
        data = _get(url, params)
        self.count += 1
        name = f"{self.count:03d}_" + url.rstrip("/").split("/")[-1].replace(".", "_") + ".json.gz"
        with gzip.open(self.folder / name, "wt", encoding="utf-8") as f:
            json.dump({"url": url, "params": params, "response": data}, f)
        return data


def fetch_imf(rec):
    """All countries and years for each IMF series, in long format."""
    meta = rec.get(f"{config.IMF_API}/indicators")["indicators"]
    rows, vintages = [], {}
    for code in config.IMF_SERIES:
        values = rec.get(f"{config.IMF_API}/{code}")["values"][code]
        vintages[code] = meta[code].get("source")
        for iso3, by_year in values.items():
            for year, value in by_year.items():
                if value is not None and int(year) >= config.IMF_FIRST_YEAR:
                    rows.append((code, iso3, int(year), float(value)))
    df = pd.DataFrame(rows, columns=["series_code", "iso3", "year", "value"])
    return df.sort_values(["series_code", "iso3", "year"]), vintages


def fetch_wb(rec):
    rows, updated = [], {}
    for code in config.WB_SERIES:
        page = 1
        while True:
            meta, data = rec.get(
                f"{config.WB_API}/country/all/indicator/{code}",
                {"format": "json", "date": f"{config.WB_FIRST_YEAR}:{config.WB_LAST_YEAR}",
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


def fetch_wb_countries(rec):
    """Country list with World Bank region and current income classification."""
    _, data = rec.get(f"{config.WB_API}/country", {"format": "json", "per_page": 400})
    df = pd.DataFrame(
        [(c["id"], c["name"], c["region"]["value"], c["incomeLevel"]["value"]) for c in data],
        columns=["iso3", "name", "region", "income_group"],
    )
    return df[df["region"] != "Aggregates"].sort_values("iso3")


def main(out_dir=None):
    stamp = datetime.now(timezone.utc)
    out_dir = out_dir or config.SNAPSHOTS / stamp.strftime("%Y-%m-%d")
    if out_dir.resolve() == config.DATA_RAW.resolve():
        raise ValueError("The published snapshot in data/raw/ is never overwritten.")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"{out_dir} already contains files; choose another folder.")
    rec = Recorder(out_dir / "json")

    imf, imf_vintages = fetch_imf(rec)
    wb, wb_updated = fetch_wb(rec)
    countries = fetch_wb_countries(rec)

    imf.to_csv(out_dir / "imf_datamapper.csv", index=False, lineterminator="\n")
    wb.to_csv(out_dir / "wb_wdi.csv", index=False, lineterminator="\n")
    countries.to_csv(out_dir / "wb_countries.csv", index=False, lineterminator="\n")

    log = {
        "retrieved_utc": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "imf_datamapper": {"endpoint": f"{config.IMF_API}/<series_code>",
                           "vintage_by_series": imf_vintages, "rows": len(imf)},
        "world_bank_wdi": {"endpoint": f"{config.WB_API}/country/all/indicator/<series_code>",
                           "years": f"{config.WB_FIRST_YEAR}-{config.WB_LAST_YEAR}",
                           "last_updated_by_series": wb_updated, "rows": len(wb)},
        "world_bank_countries": {"endpoint": f"{config.WB_API}/country", "rows": len(countries)},
    }
    (out_dir / "retrieval_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    snapshot.write_manifest(out_dir, out_dir / "manifest.json",
                            note="Tidy CSV extracts; the original JSON responses are in json/.")
    print(f"New snapshot in {out_dir}: IMF rows {len(imf):,} | WB rows {len(wb):,} | "
          f"countries {len(countries)}")
    return out_dir


if __name__ == "__main__":
    main()
