import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from sumbuddy import __main__ as sb_main
from sumbuddy import get_checksums
from sumbuddy.exceptions import OutputFileExistsError

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_get_checksums_refuses_existing_output(monkeypatch, tmp_path):
    """Without force, an existing output file raises before any walking or hashing, leaving the file untouched."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("sentinel content")

    with patch("sumbuddy.Mapper.gather_file_paths") as mock_gather, pytest.raises(OutputFileExistsError) as excinfo:
        get_checksums("example_content", str(output_file))

    mock_gather.assert_not_called()
    assert isinstance(excinfo.value, FileExistsError)
    assert output_file.read_text() == "sentinel content"
    assert "force=True" in str(excinfo.value)
    assert "--force" in str(excinfo.value)


def test_get_checksums_overwrites_with_force(monkeypatch, tmp_path):
    """With force=True, an existing output file is regenerated from scratch."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("stale content")

    get_checksums("example_content", str(output_file), force=True)

    actual = output_file.read_text()
    assert "stale content" not in actual
    expected = (EXAMPLES_DIR / "expected_outputs" / "default.csv").read_text().splitlines()
    assert sorted(actual.splitlines()) == sorted(expected)


def test_main_exits_when_output_exists(monkeypatch, tmp_path):
    """CLI exits with a clear message, without prompting, when the output file exists."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("sentinel content")

    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("CLI prompted for input"))
    monkeypatch.setattr(sys, "argv", ["sum-buddy", "-o", str(output_file), "example_content"])
    with pytest.raises(SystemExit) as excinfo:
        sb_main.main()

    assert "already exists" in str(excinfo.value)
    assert "--force" in str(excinfo.value)
    assert output_file.read_text() == "sentinel content"


@pytest.mark.parametrize("flag", ["-f", "--force"])
def test_main_force_overwrites_existing_output(monkeypatch, tmp_path, flag):
    """Both force spellings overwrite an existing output file end-to-end."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("stale content")

    monkeypatch.setattr(sys, "argv", ["sum-buddy", flag, "-o", str(output_file), "example_content"])
    sb_main.main()

    assert output_file.read_text().startswith("filepath,filename,md5")
