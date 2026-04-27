"""
Regenerate all checked-in test fixtures: binary archives and example CSVs.

Run with:
    python scripts/generate_fixtures.py

Archive bytes (examples/example_content/testzip.zip, tests/test_archive.zip)
are pinned: their MD5s appear in examples/expected_outputs/*.csv and
README.md. Regeneration is deterministic on a single Python version but
may produce different bytes across versions or future archive types.
After running, diff the result and update dependent fixtures + README
if any MD5 changed.
"""

from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
EXAMPLE_CONTENT = EXAMPLES_DIR / "example_content"
EXPECTED_OUTPUTS = EXAMPLES_DIR / "expected_outputs"
TESTS_DIR = REPO_ROOT / "tests"

# Pinned timestamp shared by every member of every checked-in archive.
PINNED_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def _build_zip(out_path: Path, members: dict[str, bytes]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in members.items():
            info = zipfile.ZipInfo(filename=name, date_time=PINNED_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)


def build_example_zip() -> None:
    _build_zip(
        EXAMPLE_CONTENT / "testzip.zip",
        {
            "file.txt": b"test text file\n",
            "dir/file.txt": b"test text file\n",
        },
    )


def build_test_archive_zip() -> None:
    _build_zip(
        TESTS_DIR / "test_archive.zip",
        {
            "test_data/test_file.txt": b"This is a test file inside the zip\n",
            "test_data/nested_dir/nested_file.txt": b"This is a nested test file\n",
        },
    )


def generate_csv_fixtures() -> None:
    from sumbuddy import get_checksums
    from sumbuddy.exceptions import NoFilesAfterFilteringError

    EXPECTED_OUTPUTS.mkdir(parents=True, exist_ok=True)
    os.chdir(EXAMPLES_DIR)

    def _run(output_name: str, **kwargs) -> None:
        out = EXPECTED_OUTPUTS / output_name
        try:
            get_checksums("example_content", str(out), **kwargs)
        except NoFilesAfterFilteringError:
            # Filter excluded everything; write a header-only fixture so the file still exists.
            out.write_text("filepath,filename,md5\n")

    for ignore_path in sorted(EXAMPLES_DIR.glob(".sbignore_*")):
        suffix = ignore_path.name[len(".sbignore_"):]
        _run(f"ignore_{suffix}.csv", ignore_file=str(ignore_path))

    _run("default.csv")
    _run("include_hidden_true.csv", include_hidden=True)


def main() -> int:
    build_example_zip()
    build_test_archive_zip()
    generate_csv_fixtures()
    return 0


if __name__ == "__main__":
    sys.exit(main())
