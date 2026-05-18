import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from sumbuddy.archive import ArchiveHandler
from sumbuddy.mapper import Mapper
from sumbuddy.hasher import Hasher


TEST_ZIP = Path(__file__).parent / "test_archive.zip"


class TestArchiveHandler:
    """Test cases for ArchiveHandler boundary."""

    def test_is_supported_archive_zip(self):
        handler = ArchiveHandler()
        assert handler.is_supported_archive(str(TEST_ZIP)) is True

    def test_is_supported_archive_rejects_non_zip(self):
        handler = ArchiveHandler()
        with tempfile.TemporaryDirectory() as temp_dir:
            non_zip = Path(temp_dir) / "not_a_zip.txt"
            non_zip.write_text("not a zip")
            assert handler.is_supported_archive(str(non_zip)) is False

    def test_is_supported_archive_rejects_zip_extension_with_bad_content(self):
        handler = ArchiveHandler()
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_zip = Path(temp_dir) / "fake.zip"
            fake_zip.write_text("not actually a zip")
            assert handler.is_supported_archive(str(fake_zip)) is False

    def test_is_supported_archive_rejects_zip_content_without_extension(self):
        # Files like .docx/.jar are valid ZIPs by content but should not be treated as archives.
        handler = ArchiveHandler()
        with tempfile.TemporaryDirectory() as temp_dir:
            disguised = Path(temp_dir) / "document.docx"
            shutil.copy2(TEST_ZIP, disguised)
            assert handler.is_supported_archive(str(disguised)) is False

    def test_iter_members_success(self):
        handler = ArchiveHandler()
        members = list(handler.iter_members(str(TEST_ZIP)))
        assert len(members) == 2
        names = [name for name, _ in members]
        assert any("test_file.txt" in n for n in names)
        assert any("nested_file.txt" in n for n in names)
        for _, file_obj in members:
            content = file_obj.read()
            assert isinstance(content, bytes)
            file_obj.close()

    def test_iter_members_invalid_file(self):
        handler = ArchiveHandler()
        with tempfile.TemporaryDirectory() as temp_dir:
            non_zip_file = Path(temp_dir) / "not_a_zip.txt"
            non_zip_file.write_text("This is not a zip file")
            with pytest.raises(zipfile.BadZipFile):
                list(handler.iter_members(str(non_zip_file)))

    def test_count_members(self):
        handler = ArchiveHandler()
        assert handler.count_members(str(TEST_ZIP)) == 2


class TestMapperWithArchives:
    """Mapper.gather_file_paths interaction with archive files."""

    def test_gather_file_paths_with_archive(self):
        mapper = Mapper()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            shutil.copy2(TEST_ZIP, temp_zip_path)
            regular_files, archive_files = mapper.gather_file_paths(temp_dir)
            assert str(temp_zip_path) in archive_files
            assert isinstance(regular_files, list)
            assert isinstance(archive_files, list)

    def test_gather_file_paths_with_archive_dive_disabled(self):
        mapper = Mapper()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            shutil.copy2(TEST_ZIP, temp_zip_path)
            regular_files, archive_files = mapper.gather_file_paths(temp_dir, archive_dive=False)
            assert str(temp_zip_path) in regular_files
            assert archive_files == []

    def test_gather_file_paths_with_archive_and_filter(self):
        mapper = Mapper()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            shutil.copy2(TEST_ZIP, temp_zip_path)
            ignore_file = Path(temp_dir) / ".ignore"
            ignore_file.write_text("**/nested_dir/**")
            regular_files, archive_files = mapper.gather_file_paths(temp_dir, ignore_file=str(ignore_file))
            assert str(temp_zip_path) in archive_files
            assert isinstance(regular_files, list)
            assert isinstance(archive_files, list)


class TestHasherWithZip:
    """Hasher accepts both file paths and file-like objects from archive members."""

    def test_checksum_file_with_file_like_object(self):
        hasher = Hasher()
        with zipfile.ZipFile(TEST_ZIP, "r") as zip_file:
            file_name = zip_file.namelist()[0]
            with zip_file.open(file_name) as file_obj:
                checksum = hasher.checksum_file(file_obj)
                assert isinstance(checksum, str)
                assert len(checksum) > 0

    def test_checksum_file_with_zip_file_path(self):
        hasher = Hasher()
        checksum = hasher.checksum_file(str(TEST_ZIP))
        assert isinstance(checksum, str)
        assert len(checksum) > 0


def test_integration_archive_support_matches_default_fixture(monkeypatch, tmp_path):
    """End-to-end: get_checksums against examples/example_content/ matches the committed default.csv fixture."""
    from sumbuddy import get_checksums

    examples_dir = Path(__file__).parent.parent / "examples"
    monkeypatch.chdir(examples_dir)
    output_file = tmp_path / "checksums.csv"
    get_checksums("example_content", str(output_file))

    actual = output_file.read_text().splitlines()
    expected = (examples_dir / "expected_outputs" / "default.csv").read_text().splitlines()
    assert sorted(actual) == sorted(expected)


def test_integration_no_archive_dive_omits_members(monkeypatch, tmp_path):
    """End-to-end: get_checksums with archive_dive=False matches the no_archive_dive.csv fixture (archive present, members absent)."""
    from sumbuddy import get_checksums

    examples_dir = Path(__file__).parent.parent / "examples"
    monkeypatch.chdir(examples_dir)
    output_file = tmp_path / "checksums.csv"
    get_checksums("example_content", str(output_file), archive_dive=False)

    actual = output_file.read_text().splitlines()
    expected = (examples_dir / "expected_outputs" / "no_archive_dive.csv").read_text().splitlines()
    assert sorted(actual) == sorted(expected)


def test_get_checksums_skips_iter_members_when_dive_disabled(monkeypatch, tmp_path):
    """archive_dive=False must not invoke ArchiveHandler.iter_members on any discovered archive."""
    from sumbuddy import get_checksums

    examples_dir = Path(__file__).parent.parent / "examples"
    monkeypatch.chdir(examples_dir)
    output_file = tmp_path / "checksums.csv"

    with patch("sumbuddy.__main__.ArchiveHandler.iter_members") as mock_iter:
        get_checksums("example_content", str(output_file), archive_dive=False)
        mock_iter.assert_not_called()


def test_main_passes_archive_dive_false_to_get_checksums(monkeypatch, tmp_path):
    """--no-archive-dive on the CLI threads archive_dive=False into get_checksums."""
    from sumbuddy import __main__ as sb_main

    examples_dir = Path(__file__).parent.parent / "examples"
    monkeypatch.chdir(examples_dir)
    output_file = tmp_path / "checksums.csv"

    monkeypatch.setattr(sys, "argv", ["sum-buddy", "--no-archive-dive", "-o", str(output_file), "example_content"])
    with patch("sumbuddy.__main__.get_checksums") as mock_gc:
        sb_main.main()
        mock_gc.assert_called_once()
        assert mock_gc.call_args.kwargs["archive_dive"] is False


def test_main_passes_archive_dive_true_by_default(monkeypatch, tmp_path):
    """Without the flag, get_checksums receives archive_dive=True (the default)."""
    from sumbuddy import __main__ as sb_main

    examples_dir = Path(__file__).parent.parent / "examples"
    monkeypatch.chdir(examples_dir)
    output_file = tmp_path / "checksums.csv"

    monkeypatch.setattr(sys, "argv", ["sum-buddy", "-o", str(output_file), "example_content"])
    with patch("sumbuddy.__main__.get_checksums") as mock_gc:
        sb_main.main()
        mock_gc.assert_called_once()
        assert mock_gc.call_args.kwargs["archive_dive"] is True
