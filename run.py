"""Reproduce the study from the published data snapshot.

    python run.py              # snapshot in data/raw -> SQL -> checks -> statistics -> figures -> report
    python run.py --no-pdf     # the same, without printing the PDF (needs Chrome or Edge)
    python run.py --refresh    # only download a NEW snapshot into data/snapshots/<date>/ and stop
    SNAPSHOT_DIR=data/snapshots/<date> python run.py   # analyse a new snapshot in draft mode

Reproducing the published snapshot is the default. Downloading new data is a
separate step: it does not change the published results. In draft mode all
outputs go to *_draft folders and files, because a new vintage needs a new
review of the numbers, the flagged cases and the report text before use.
"""

import argparse
import shutil
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
import snapshot  # noqa: E402
import validate  # noqa: E402


def step(label, fn, *args, **kwargs):
    t = time.perf_counter()
    print(f"-> {label} ...", flush=True)
    out = fn(*args, **kwargs)
    print(f"   done in {time.perf_counter() - t:.1f}s")
    return out


def clear_outputs():
    """Remove generated tables and figures so no stale file survives a rerun."""
    for folder in (config.TABLES, config.FIGURES):
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--refresh", action="store_true",
                        help="download a new snapshot into data/snapshots/<date>/ and stop")
    parser.add_argument("--no-pdf", action="store_true", help="do not print the PDF report")
    args = parser.parse_args()

    if args.refresh:
        out = step("Downloading a new snapshot (the published one is not changed)", acquire.main)
        rel = out.relative_to(config.ROOT).as_posix()
        print(f"Saved to {rel}. To analyse it in draft mode (published files are not changed):\n"
              f"    SNAPSHOT_DIR={rel} python run.py\n"
              "Then review the flagged cases, audit/reviewed_cases.csv and the report text before "
              "publishing anything.")
        return

    if config.DRAFT:
        print(f"DRAFT MODE: analysing {config.DATA_RAW}. Outputs go to *_draft folders and files; "
              "the published results are not changed.")
    manifest = config.SNAPSHOT_MANIFEST.relative_to(config.ROOT).as_posix() \
        if config.SNAPSHOT_MANIFEST.is_relative_to(config.ROOT) else config.SNAPSHOT_MANIFEST
    step(f"Checking the input files against {manifest}", snapshot.check_inputs)
    clear_outputs()
    step("Loading the snapshot into SQLite and building the panel", database.build)
    step("Running data-quality checks", validate.run)
    tables = step("Running the analytical SQL queries", database.run_analysis_queries)
    step("Estimating statistics and decompositions", analyze.run, tables)
    step("Drawing figures", figures.run)
    step("Writing README and report", build_report.run, pdf=not args.no_pdf)
    if config.DRAFT:
        print("Finished (draft). See README_draft.md, report/economic_analysis_draft.*, outputs_draft/ "
              "and audit/draft/.")
    else:
        print("Finished. See README.md, report/ and outputs/.")


if __name__ == "__main__":
    main()
