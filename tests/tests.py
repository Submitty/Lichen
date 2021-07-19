import unittest
import os
import shutil
import subprocess
import json

lichen_repository_dir = "/usr/local/submitty/GIT_CHECKOUT/Lichen"
lichen_installation_dir = "/usr/local/submitty/Lichen"
lichen_data_dir = "/var/local/submitty/courses"


class TestPlaintextTokenizer(unittest.TestCase):
    def testPlaintextTokenizer(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/expected_output/output.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)

    def testPlaintextTokenizerIgnorePunctuation(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/expected_output/output_ignore_punctuation.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_punctuation < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)

    def testPlaintextTokenizerToLower(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/expected_output/output_to_lower.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_punctuation < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)

    def testPlaintextTokenizerIgnoreNewlines(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/expected_output/output_ignore_newlines.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_newlines < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)

    def testPlaintextTokenizerIgnoreEverything(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/expected_output/output_ignore_everything.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_punctuation --to_lower --ignore_numbers --ignore_newlines  < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)


class TestCTokenizer(unittest.TestCase):
    def testCTokenizer(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/c/input.cpp"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/c/expected_output/output.json"

        command = f"python3 {lichen_installation_dir}/bin/c_tokenizer.py {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)


class TestMIPSTokenizer(unittest.TestCase):
    def testMIPSTokenizer(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/mips/input.s"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/output.json"
        expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/mips/expected_output/output.json"

        command = f"python3 {lichen_installation_dir}/bin/mips_tokenizer.py {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

        # clean up the files
        os.remove(output_file)


class TestHashAll(unittest.TestCase):
    def setUp(self):
        os.makedirs("/usr/local/submitty/Lichen/test_output")

    def tearDown(self):
        shutil.rmtree("/usr/local/submitty/Lichen/test_output")

    def testHashAll(self):
        # make the fake directory structure hash_all.p expects
        os.makedirs("/usr/local/submitty/Lichen/test_output/test_hash_all/provided_code")
        os.makedirs("/usr/local/submitty/Lichen/test_output/test_hash_all/other_gradeables")
        os.makedirs("/usr/local/submitty/Lichen/test_output/test_hash_all/users/student/1")
        open("/usr/local/submitty/Lichen/test_output/test_hash_all/config.json", 'a').close()
        open("/usr/local/submitty/Lichen/test_output/test_hash_all/users/student/1/tokens.json", 'a').close()
        with open("/usr/local/submitty/Lichen/test_output/test_hash_all/provided_code/tokens.json", 'w') as file:
            file.write("null")

        # copy the input files from /data to the the new path
        shutil.copyfile("data/hash_all/a/config.json", "/usr/local/submitty/Lichen/test_output/test_hash_all/config.json")
        shutil.copyfile("data/hash_all/a/tokens.json", "/usr/local/submitty/Lichen/test_output/test_hash_all/users/student/1/tokens.json")

        # save current working directory
        cwd = os.getcwd()

        # run hash_all
        os.chdir("/usr/local/submitty/Lichen/bin")
        os.system("python3 /usr/local/submitty/Lichen/bin/hash_all.py /usr/local/submitty/Lichen/test_output/test_hash_all")
        os.chdir(cwd)

        # test output
        hashes_file = "/usr/local/submitty/Lichen/test_output/test_hash_all/users/student/1/hashes.txt"
        with open(hashes_file, 'r') as file:
            lines = file.readlines()

        lines = [x.strip() for x in lines]

        tokens_file = "/usr/local/submitty/Lichen/test_output/test_hash_all/users/student/1/tokens.json"
        with open(tokens_file, 'r') as file:
            tokens = json.load(file)
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
