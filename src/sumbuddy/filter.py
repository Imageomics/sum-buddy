import os
import fnmatch

class Filter:
    def __init__(self):
        pass

    @staticmethod
    def read_patterns(filepath):
        """
        Read patterns from an include or ignore file, one pattern per line.
        """
        with open(filepath, 'r') as f:
            patterns = [line.strip() for line in f if line.strip()]
        return patterns

    @staticmethod
    def should_include(filepath, patterns, root, include_mode=False):
        """
        Determine if a file should be included based on patterns and the root directory.
        Excludes hidden files and directories by default unless explicitly included.
        """
        relative_filepath = os.path.relpath(filepath, start=root)

        # Default behavior when no patterns are passed: exclude all hidden files and directories
        if not patterns:
            return not relative_filepath.split(os.sep)[0].startswith('.')

        # Handle include mode
        if include_mode:
            # Include files that match any pattern
            return any(fnmatch.fnmatch(relative_filepath, pattern) for pattern in patterns)

        # Handle exclude mode with negation
        for pattern in patterns:
            if pattern.startswith('!'):
                if fnmatch.fnmatch(relative_filepath, pattern[1:]):
                    # Negation pattern matches, include this file
                    return True  

        # Handle exclude mode
        for pattern in patterns:
            if fnmatch.fnmatch(relative_filepath, pattern):
                # Pattern matches for ignore, exclude this file
                return False  

        return not relative_filepath.split(os.sep)[0].startswith('.')
