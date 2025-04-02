
import unittest
import os
from unittest.mock import patch
from sumbuddy.filter import Filter
from sumbuddy.hasher import Hasher

class TestFilter(unittest.TestCase):  
    def setUp(self):
        self.examples_folder = os.path.join(os.path.dirname(__file__), '..', 'examples')
        self.example_content_folder = os.path.join(self.examples_folder, 'example_content')
        self.expected_outputs_folder = os.path.join(self.examples_folder, 'expected_outputs')
        
        self.filter = Filter()

        self.hasher = Hasher()

    # Utilize the examples folder to test the filter class.
    def check_output(self, ignore_filename, expected_output_filename):
        ignore_filepath = os.path.join(self.examples_folder, ignore_filename)
        self.filter.read_ignore_patterns(ignore_filepath=ignore_filepath)
        
        # Read expected output from the specified file
        expected_output_filepath = os.path.join(self.expected_outputs_folder, expected_output_filename)
        with open(expected_output_filepath, 'r') as f:
            expected_output = f.read().splitlines()

        # Gather actual output
        actual_output = ['filepath,filename,md5']  
        for root, _, files in os.walk(self.example_content_folder):
            for file in files:
                if file == ".DS_Store":
                    continue
                filepath = os.path.join(root, file)
                include = self.filter.should_include(filepath, self.example_content_folder)

                if include:
                    filename = os.path.basename(filepath)
                    md5_hash = self.hasher.checksum_file(filepath)
                    relative_filepath = os.path.relpath(filepath, start=self.examples_folder)
                    actual_output.append(f"{relative_filepath},{filename},{md5_hash}")
        
        expected_output.sort()
        actual_output.sort()

        self.assertEqual(expected_output, actual_output)

    def test_ignore_all(self):
        self.check_output('.sbignore_all', 'ignore_all.csv')
    
    def test_ignore_all_except_dots(self):
        self.check_output('.sbignore_all_except_dots', 'ignore_all_except_dots.csv')

    def test_ignore_except_txt(self):
        self.check_output('.sbignore_except_txt', 'ignore_except_txt.csv')

    def test_ignore_all_except_subdir_but_ignore_hidden(self):
        self.check_output('.sbignore_all_except_subdir_but_ignore_hidden', 'ignore_all_except_subdir_but_ignore_hidden.csv')

    def test_ignore_hidden_files(self):
        self.check_output('.sbignore_hidden_files', 'ignore_hidden_files.csv')

    def test_ignore_nothing(self):
        self.check_output('.sbignore_nothing', 'ignore_nothing.csv')

    def test_ignore_specific_file(self):
        self.check_output('.sbignore_specific_file', 'ignore_specific_file.csv')

    def test_ignore_subdir(self):
        self.check_output('.sbignore_subdir', 'ignore_subdir.csv')

    def test_ignore_txt(self):
        self.check_output('.sbignore_txt', 'ignore_txt.csv')

    # To test other hashing algorithms.
    def check_output_with_hashing_algorithm(self, hash_algorithm, expected_output, ignore_filename):
        ignore_filepath = os.path.join(self.examples_folder, ignore_filename)
        self.filter.read_ignore_patterns(ignore_filepath=ignore_filepath)
        
        with patch.object(Hasher, 'checksum_file', return_value=hash_algorithm) as mock_method:
            actual_output = ['filepath,filename,hash']
            for root, _, files in os.walk(self.example_content_folder):
                for file in files:
                    if file == ".DS_Store":
                        continue
                    filepath = os.path.join(root, file)
                    include = self.filter.should_include(filepath, self.example_content_folder)
                    if include:
                        filename = os.path.basename(filepath)
                        hash_value = self.hasher.checksum_file(filepath)
                        relative_filepath = os.path.relpath(filepath, start=self.examples_folder)
                        actual_output.append(f"{relative_filepath},{filename},{hash_value}")
            
            self.assertTrue(mock_method.called)
            
            expected_output.sort()
            actual_output.sort()

            self.assertEqual(expected_output, actual_output)

    def test_sha256(self):
        expected_output = [
            'filepath,filename,hash',
            'example_content/file.txt,file.txt,sha256_hash',
            'example_content/dir/file.txt,file.txt,sha256_hash'
            
        ]
        self.check_output_with_hashing_algorithm('sha256_hash', expected_output, '.sbignore_hidden_files')

    def test_shake_128(self):
        expected_output = [
            'filepath,filename,hash',
            'example_content/.hidden_file,.hidden_file,shake_128',
            'example_content/.hidden_dir/.hidden_file,.hidden_file,shake_128',
            'example_content/dir/.hidden_file,.hidden_file,shake_128',
            'example_content/dir/.hidden_dir/.hidden_file,.hidden_file,shake_128'
        ]
        self.check_output_with_hashing_algorithm('shake_128', expected_output, '.sbignore_specific_file')

    def test_blake2b(self):
        expected_output = [
            'filepath,filename,hash',
            'example_content/file.txt,file.txt,blake2b_hash',
            'example_content/.hidden_dir/file.txt,file.txt,blake2b_hash',
            'example_content/dir/file.txt,file.txt,blake2b_hash',
            'example_content/dir/.hidden_dir/file.txt,file.txt,blake2b_hash'
        ]
        self.check_output_with_hashing_algorithm('blake2b_hash', expected_output, '.sbignore_except_txt')

    def test_sha3_256(self):
        expected_output = [
            'filepath,filename,hash',
            'example_content/.hidden_file,.hidden_file,sha3_256',
            'example_content/file.txt,file.txt,sha3_256',
            'example_content/.hidden_dir/.hidden_file,.hidden_file,sha3_256',
            'example_content/.hidden_dir/file.txt,file.txt,sha3_256'        
        ]
        self.check_output_with_hashing_algorithm('sha3_256', expected_output, '.sbignore_subdir')


if __name__ == '__main__':
    unittest.main()



