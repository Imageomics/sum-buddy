import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from sumbuddy import get_checksums
from sumbuddy.exceptions import OutputFileExistsError

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_get_checksums_raises_when_output_exists(monkeypatch, tmp_path):
    """Without force, an existing output file raises and is left untouched."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("sentinel content")

    with pytest.raises(OutputFileExistsError) as excinfo:
        get_checksums("example_content", str(output_file))

    assert output_file.read_text() == "sentinel content"
    assert "force=True" in str(excinfo.value)
    assert "--force" in str(excinfo.value)


def test_get_checksums_raises_builtin_file_exists_error(monkeypatch, tmp_path):
    """OutputFileExistsError is catchable as the builtin FileExistsError."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("sentinel content")

    with pytest.raises(FileExistsError):
        get_checksums("example_content", str(output_file))


def test_get_checksums_overwrites_with_force(monkeypatch, tmp_path):
    """With force=True, an existing output file is overwritten."""
    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"
    output_file.write_text("stale content")

    get_checksums("example_content", str(output_file), force=True)

    assert output_file.read_text().startswith("filepath,filename,md5")


def test_get_checksums_stdout_unaffected(monkeypatch, capsys):
    """Output to stdout (no output_filepath) never triggers the overwrite guard."""
    monkeypatch.chdir(EXAMPLES_DIR)

    get_checksums("example_content")

    assert "filepath,filename,md5" in capsys.readouterr().out


def test_main_exits_when_output_exists(monkeypatch, tmp_path):
    """CLI exits with a clear message, without prompting, when the output file exists."""
    from sumbuddy import __main__ as sb_main

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


def test_main_force_passes_force_true(monkeypatch, tmp_path):
    """-f/--force on the CLI threads force=True into get_checksums."""
    from sumbuddy import __main__ as sb_main

    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"

    monkeypatch.setattr(sys, "argv", ["sum-buddy", "-f", "-o", str(output_file), "example_content"])
    with patch("sumbuddy.__main__.get_checksums") as mock_gc:
        sb_main.main()
        mock_gc.assert_called_once()
        assert mock_gc.call_args.kwargs["force"] is True


def test_main_default_passes_force_false(monkeypatch, tmp_path):
    """Without the flag, get_checksums receives force=False (the default)."""
    from sumbuddy import __main__ as sb_main

    monkeypatch.chdir(EXAMPLES_DIR)
    output_file = tmp_path / "checksums.csv"

    monkeypatch.setattr(sys, "argv", ["sum-buddy", "-o", str(output_file), "example_content"])
    with patch("sumbuddy.__main__.get_checksums") as mock_gc:
        sb_main.main()
        mock_gc.assert_called_once()
        assert mock_gc.call_args.kwargs["force"] is False
