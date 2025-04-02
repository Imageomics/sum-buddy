import os
import tempfile
import unittest
from unittest.mock import patch, mock_open
from sumbuddy.mapper import Mapper
from sumbuddy.filter import Filter
from sumbuddy.exceptions import EmptyInputDirectoryError, NoFilesAfterFilteringError, NotADirectoryError

class TestMapper(unittest.TestCase):
    @patch('sumbuddy.filter.open', new_callable=mock_open, read_data="# This is a sample ignore file\n")
    def test_reset_filter(self, mock_file):
        mapper = Mapper()
        mapper.reset_filter()
        self.assertIsInstance(mapper.filter_manager, Filter)
        
        mapper.reset_filter(ignore_file='ignore_file')
        self.assertIsInstance(mapper.filter_manager, Filter)
        
        mapper.reset_filter(include_hidden=True)
        self.assertIsInstance(mapper.filter_manager, Filter)
        
    def test_gather_file_paths(self):
        mapper = Mapper()
        with tempfile.TemporaryDirectory() as temp_dir:
            subdir_path = os.path.join(temp_dir, 'subdir')
            os.makedirs(subdir_path, exist_ok=True)
            with open(os.path.join(temp_dir, 'file1.txt'), 'w') as file:
                file.write('Some content')
            with open(os.path.join(temp_dir, 'file2.txt'), 'w') as file:
                file.write('Some content')
            with open(os.path.join(temp_dir, '.hidden.txt'), 'w') as file:
                file.write('Some content')
            with open(os.path.join(subdir_path, 'file3.txt'), 'w') as file:
                file.write('Some content')
            with open(os.path.join(subdir_path, '.hidden.txt'), 'w') as file:
                file.write('Some content')
            
            file_paths = mapper.gather_file_paths(temp_dir)
            self.assertEqual(len(file_paths), 3)
            self.assertIn(os.path.join(temp_dir, 'file1.txt'), file_paths)
            self.assertIn(os.path.join(temp_dir, 'file2.txt'), file_paths)
            self.assertIn(os.path.join(subdir_path, 'file3.txt'), file_paths)
            
            # Create ignore file and test with it, if we ignore the .txt files, we will
            # only have the ignore file in the list of file paths.
            ignore_file_path = os.path.join(temp_dir, 'ignore_file')
            with open(ignore_file_path, 'w') as ignore_file:
                ignore_file.write("*.txt")

            file_paths = mapper.gather_file_paths(temp_dir, ignore_file=ignore_file_path)
            self.assertEqual(len(file_paths), 1)
            self.assertIn(os.path.join(temp_dir, 'ignore_file'), file_paths)
            
            # Test including hidden files
            file_paths = mapper.gather_file_paths(temp_dir, include_hidden=True)
            self.assertEqual(len(file_paths), 6)
            self.assertIn(os.path.join(temp_dir, 'file1.txt'), file_paths)
            self.assertIn(os.path.join(temp_dir, 'file2.txt'), file_paths)
            self.assertIn(os.path.join(temp_dir, 'ignore_file'), file_paths)
            self.assertIn(os.path.join(temp_dir, '.hidden.txt'), file_paths)
            self.assertIn(os.path.join(subdir_path, 'file3.txt'), file_paths)
            self.assertIn(os.path.join(subdir_path, '.hidden.txt'), file_paths)
            
            file_paths = mapper.gather_file_paths(temp_dir)
            self.assertEqual(len(file_paths), 4)
            self.assertIn(os.path.join(temp_dir, 'file1.txt'), file_paths)
            self.assertIn(os.path.join(temp_dir, 'file2.txt'), file_paths)
            self.assertIn(os.path.join(temp_dir, 'ignore_file'), file_paths)
            self.assertIn(os.path.join(subdir_path, 'file3.txt'), file_paths)

    def test_gather_file_paths_empty(self):
        mapper = Mapper()
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(EmptyInputDirectoryError):
                mapper.gather_file_paths(temp_dir)
    
    def test_gather_file_paths_filtered_files(self):
        mapper = Mapper()
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, 'file1.dat'), 'w') as file:
                file.write('Some content')
            with open(os.path.join(temp_dir, 'file2.dat'), 'w') as file:
                file.write('Some content')
            with open(os.path.join(temp_dir, '.hidden.txt'), 'w') as file:
                file.write('Some content')

            ignore_file_path = os.path.join(temp_dir, '.ignore_file')
            with open(ignore_file_path, 'w') as ignore_file:
                ignore_file.write("*.dat\n.*")

            with self.assertRaises(NoFilesAfterFilteringError):
                mapper.gather_file_paths(temp_dir, ignore_file=ignore_file_path)
    
    def test_gather_file_paths_input_not_a_directory(self):
        mapper = Mapper()
        with tempfile.NamedTemporaryFile() as temp_file:
            with self.assertRaises(NotADirectoryError):
                mapper.gather_file_paths(temp_file.name)
           

if __name__ == '__main__':
    unittest.main()
