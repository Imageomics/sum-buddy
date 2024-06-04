import pathspec
import os

class Filter:
    def __init__(self):
        self.spec = None

    def read_ignore_patterns(self, ignore_filepath=None, include_hidden=False):
        """
        Read patterns from an ignore file and compile them into a PathSpec object.
        """
        if include_hidden:
            ignore_patterns = []
        elif ignore_filepath:
            with open(ignore_filepath, 'r') as f:
                ignore_patterns = f.read().splitlines()
        else:
            ignore_patterns = ['.*']

        if ignore_patterns:
            self.spec = pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns)
        else:
            self.spec = None

    def should_include(self, filepath, root):
        """
        Determine if a file should be included based on compiled PathSpec patterns and the root directory.
        """
        if not self.spec:
            return True  # If no spec is provided, include all files by default.
        
        relative_filepath = os.path.relpath(filepath, start=root)
        return not self.spec.match_file(relative_filepath)

