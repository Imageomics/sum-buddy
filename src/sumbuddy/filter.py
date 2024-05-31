import pathspec
import os

class Filter:
    def __init__(self):
        self.spec = None

    def read_patterns(self, filepath=None, ignore_hidden=False):
        """
        Read patterns from an ignore file and compile them into a PathSpec object.
        """
        if ignore_hidden:
            patterns = ['.*']
        elif filepath:
            with open(filepath, 'r') as f:
                patterns = f.read().splitlines()
        else:
            patterns = []

        if patterns:
            self.spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
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

