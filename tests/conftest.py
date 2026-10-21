import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parents[1] / "src"))

import config  # noqa: E402


def pytest_sessionstart(session):
    """Build the outputs first if `python run.py` has not been run yet."""
    if not (config.ROOT / "outputs" / "key_numbers.json").exists() or not config.DB_PATH.exists():
        import analyze, database, validate  # noqa: E401
        database.build()
        validate.run()
        analyze.run(database.run_analysis_queries())
