"""Checksums and provenance for a data snapshot.

The CSV files in data/raw/ are tidy extracts made from the IMF and World Bank
API responses (one row per series, economy and year). The original JSON
responses were not kept for the published snapshot; new downloads keep them
(see acquire.py). The manifest records a SHA-256 checksum for each input
file, so a changed or missing file is detected before the analysis runs.
"""

import hashlib
import json

import config

NOTE = ("CSV files are tidy extracts of the IMF DataMapper and World Bank API responses "
        "(series_code, iso3, year, value). The original JSON responses were not kept for "
        "this snapshot.")


def sha256(path):
    """Checksum of the file with line endings normalised to LF.

    Git stores these text files with LF endings, but a Windows checkout can
    have CRLF; normalising makes the checksum the same on every platform.
    """
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def build_manifest(raw_dir, note=NOTE):
    log = json.loads((raw_dir / "retrieval_log.json").read_text(encoding="utf-8"))
    files = {}
    for name in config.REQUIRED_RAW_FILES:
        path = raw_dir / name
        files[name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    return {"retrieved_utc": log["retrieved_utc"], "note": note, "files": files,
            "sources": {"imf_vintage_by_series": log["imf_datamapper"]["vintage_by_series"],
                        "world_bank_last_updated": log["world_bank_wdi"]["last_updated_by_series"]}}


def write_manifest(raw_dir, path, note=NOTE):
    path.write_text(json.dumps(build_manifest(raw_dir, note), indent=2), encoding="utf-8")


def check_inputs(raw_dir=None, manifest_path=None):
    """Stop early if a required input is missing or differs from the manifest."""
    raw_dir = raw_dir or config.DATA_RAW
    manifest_path = manifest_path or config.SNAPSHOT_MANIFEST
    missing = [n for n in config.REQUIRED_RAW_FILES if not (raw_dir / n).exists()]
    if missing:
        raise FileNotFoundError(f"Missing input files in {raw_dir}: {', '.join(missing)}")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        changed = [n for n, meta in manifest["files"].items() if sha256(raw_dir / n) != meta["sha256"]]
        if changed:
            raise RuntimeError(f"Input files differ from {manifest_path.name}: {', '.join(changed)}")
    return True
