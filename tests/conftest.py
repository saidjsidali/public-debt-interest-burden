import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parents[1] / "src"))
os.environ.pop("SNAPSHOT_DIR", None)  # the tests always check the published snapshot and outputs

import config  # noqa: E402


def pytest_sessionstart(session):
    """Build the outputs first if `python run.py` has not been run yet."""
    if not config.KEY_NUMBERS.exists() or not config.DB_PATH.exists():
        import analyze, database, validate  # noqa: E401
        database.build()
        validate.run()
        analyze.run(database.run_analysis_queries())
