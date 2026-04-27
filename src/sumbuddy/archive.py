import zipfile


class ArchiveHandler:
    """
    Boundary for archive-format handling. Generic API; ZIP-backed today.

    When TAR/7z support is added, dispatch grows inside each method;
    callers in __main__.py and mapper.py are unaffected.
    """

    _ZIP_EXTENSIONS = (".zip",)

    def is_supported_archive(self, path):
        """
        Return True if `path` points to a supported archive file.

        Parameters:
        ------------
        path - String. Filesystem path to check.

        Returns:
        ---------
        Boolean.
        """
        lowered = path.lower()
        if lowered.endswith(self._ZIP_EXTENSIONS):
            return zipfile.is_zipfile(path)
        return False

    def iter_members(self, path):
        """
        Yield (member_name, file-like object) for each non-directory member of the archive.

        Parameters:
        ------------
        path - String. Filesystem path to a supported archive.

        Yields:
        ---------
        Tuples of (String, file-like object). The file-like object reads decompressed bytes.
        """
        with zipfile.ZipFile(path, "r") as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("/"):
                    continue
                yield member, zip_ref.open(member)

    def count_members(self, path):
        """
        Return the number of non-directory members in the archive.

        Reads only the archive's central directory; member contents are not opened.

        Parameters:
        ------------
        path - String. Filesystem path to a supported archive.

        Returns:
        ---------
        Integer.
        """
        with zipfile.ZipFile(path) as zf:
            return sum(1 for n in zf.namelist() if not n.endswith("/"))
