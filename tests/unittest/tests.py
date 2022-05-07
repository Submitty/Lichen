import unittest
import os
import shutil
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


test_data_dir = Path(__file__).resolve().parent / '..' / 'data'
lichen_installation_dir = Path("/usr", "local", "submitty", "Lichen")


################################################################################
# Tokenizer tests

class TestPlaintextTokenizer(unittest.TestCase):
    def testPlaintextTokenizer(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "plaintext", "input.txt")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "plaintext", "expected_output", "output.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'plaintext', 'plaintext_tokenizer.py'))} {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerIgnorePunctuation(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "plaintext", "input.txt")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "plaintext", "expected_output", "output_ignore_punctuation.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'plaintext', 'plaintext_tokenizer.py'))} --ignore_punctuation {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerToLower(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "plaintext", "input.txt")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "plaintext", "expected_output", "output_to_lower.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'plaintext', 'plaintext_tokenizer.py'))} --to_lower {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerIgnoreNewlines(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "plaintext", "input.txt")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "plaintext", "expected_output", "output_ignore_newlines.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'plaintext', 'plaintext_tokenizer.py'))} --ignore_newlines {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerIgnoreEverything(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "plaintext", "input.txt")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "plaintext", "expected_output", "output_ignore_everything.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'plaintext', 'plaintext_tokenizer.py'))} --ignore_punctuation --to_lower --ignore_numbers --ignore_newlines {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)


class TestMIPSTokenizer(unittest.TestCase):
    def testMIPSTokenizer(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "mips", "input.s")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "mips", "expected_output", "output.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'mips', 'mips_tokenizer.py'))} {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)


class TestJavaTokenizer(unittest.TestCase):
    def testJavaTokenizer(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "java", "input_with_error.java")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "java", "expected_output", "output.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'java', 'java_tokenizer.py'))} {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)


class TestCTokenizer(unittest.TestCase):
    def testCTokenizer(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "c", "input.cpp")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "c", "expected_output", "output.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'c', 'c_tokenizer.py'))} {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)

    def testCTokenizerIgnoreComments(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "c", "input.cpp")
            output_file_with_comments = Path(temp_dir, "output_with_comments.json")
            output_file_ignore_comments = Path(temp_dir, "output_ignore_comments.json")
            expected_output_file_ignore_comments = Path(test_data_dir, "tokenizer", "c", "expected_output", "output_ignore_comments.json")
            expected_output_file_with_comments = Path(test_data_dir, "tokenizer", "c", "expected_output", "output.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'c', 'c_tokenizer.py'))} {str(input_file)} --ignore_comments > {str(output_file_ignore_comments)}", shell=True)
            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'c', 'c_tokenizer.py'))} {str(input_file)} > {str(output_file_with_comments)}", shell=True)

            with open(output_file_with_comments) as file:
                actual_output_with_comments = json.load(file)
            with open(output_file_ignore_comments) as file:
                actual_output_ignore_comments = json.load(file)

            with open(expected_output_file_with_comments) as file:
                expected_output_with_comments = json.load(file)
            with open(expected_output_file_ignore_comments) as file:
                expected_output_ignore_comments = json.load(file)

            self.assertEqual(actual_output_with_comments, expected_output_with_comments)
            self.assertEqual(actual_output_ignore_comments, expected_output_ignore_comments)


class TestPythonTokenizer(unittest.TestCase):
    def testPythonTokenizer(self):
        self.maxDiff = None

        with TemporaryDirectory() as temp_dir:
            input_file = Path(test_data_dir, "tokenizer", "python", "input.py")
            output_file = Path(temp_dir, "output.json")
            expected_output_file = Path(test_data_dir, "tokenizer", "python", "expected_output", "output.json")

            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'tokenizer', 'python', 'python_tokenizer.py'))} {str(input_file)} > {str(output_file)}", shell=True)

            with open(output_file) as file:
                actual_output = json.load(file)

            with open(expected_output_file) as file:
                expected_output = json.load(file)

            self.assertEqual(actual_output, expected_output)


################################################################################
# Hasher tests

class TestHashAll(unittest.TestCase):
    def testHashAll(self):
        with TemporaryDirectory() as temp_dir:
            # make the fake directory structure hash_all.py expects
            os.makedirs(Path(temp_dir, "provided_code"))
            os.makedirs(Path(temp_dir, "other_gradeables"))
            os.makedirs(Path(temp_dir, "users", "student", "1"))
            open(Path(temp_dir, "config.json"), 'a').close()
            open(Path(temp_dir, "users", "student", "1", "tokens.json"), 'a').close()
            with open(Path(temp_dir, "provided_code", "tokens.json"), 'w') as file:
                file.write("null")

            # copy the input files from /data to the the new path
            shutil.copyfile(Path(test_data_dir, "hash_all", "config.json"), Path(temp_dir, "config.json"))
            shutil.copyfile(Path(test_data_dir, "hash_all", "tokens.json"), Path(temp_dir, "users", "student", "1", "tokens.json"))

            # save current working directory
            cwd = os.getcwd()

            # run hash_all
            os.chdir(Path(lichen_installation_dir, "bin"))
            subprocess.check_call(f"python3 {str(Path(lichen_installation_dir, 'hasher', 'hash_all.py'))} {temp_dir} > /dev/null", shell=True)
            os.chdir(cwd)

            # test output
            hashes_file = Path(temp_dir, "users", "student", "1", "hashes.txt")
            with open(hashes_file, 'r') as file:
                lines = file.readlines()
            lines = [x.strip() for x in lines]
            tokens_file = Path(temp_dir, "users", "student", "1", "tokens.json")
            with open(tokens_file, 'r') as file:
                tokens = json.load(file)

            # make sure the number of sequences and the number of hashes are the same
            self.assertEqual(len(lines), len(tokens) - 2 + 1)

            # make sure the same sequences hash to the same string, and
            # that different sequences hash to different strings
            for i in range(0, len(lines)):
                for j in range(i + 1, len(lines)):
                    if i == 4 and j == 9\
                     or i == 4 and j == 16\
                     or i == 9 and j == 16\
                     or i == 13 and j == 22\
                     or i == 14 and j == 23\
                     or i == 15 and j == 24:
                        self.assertEqual(lines[i], lines[j])
                    else:
                        self.assertNotEqual(lines[i], lines[j])


if __name__ == '__main__':
    unittest.main()
