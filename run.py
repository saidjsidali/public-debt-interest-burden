"""Reproduce the whole study: data -> SQL -> checks -> statistics -> figures -> report.

    python run.py              # use the data snapshot in data/raw (default)
    python run.py --refresh    # download the latest data first (numbers will change)
    python run.py --no-pdf     # skip printing the PDF (needs Chrome or Edge)
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parent / "src"))

import acquire  # noqa: E402
import analyze  # noqa: E402
import build_report  # noqa: E402
import config  # noqa: E402
import database  # noqa: E402
import figures  # noqa: E402
import validate  # noqa: E402


def step(label, fn, *args, **kwargs):
    t = time.perf_counter()
    print(f"-> {label} ...", flush=True)
    out = fn(*args, **kwargs)
    print(f"   done in {time.perf_counter() - t:.1f}s")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--refresh", action="store_true", help="download the latest data before running")
    parser.add_argument("--no-pdf", action="store_true", help="do not print the PDF report")
    args = parser.parse_args()

    if args.refresh or not (config.DATA_RAW / "imf_datamapper.csv").exists():
        step("Downloading data from the IMF and World Bank APIs", acquire.main)
    step("Loading the snapshot into SQLite and building the panel", database.build)
    step("Running data-quality checks", validate.run)
    tables = step("Running the analytical SQL queries", database.run_analysis_queries)
    step("Estimating statistics and decompositions", analyze.run, tables)
    step("Drawing figures", figures.run)
    step("Writing README and report", build_report.run, pdf=not args.no_pdf)
    print("Finished. See README.md, report/ and outputs/.")


if __name__ == "__main__":
    main()
