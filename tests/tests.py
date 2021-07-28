import unittest
import os
import shutil
import json

lichen_installation_dir = "/usr/local/submitty/Lichen"
lichen_test_playground = "/usr/local/submitty/Lichen/test_output"


class TestPlaintextTokenizer(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(os.path.join(lichen_test_playground, 'plaintext_tokenizer')):
            os.makedirs(os.path.join(lichen_test_playground, 'plaintext_tokenizer'))

    def tearDown(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'plaintext_tokenizer'))

    def testPlaintextTokenizer(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_test_playground}/plaintext_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/plaintext/expected_output/output.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerIgnorePunctuation(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_test_playground}/plaintext_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/plaintext/expected_output/output_ignore_punctuation.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_punctuation < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerToLower(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_test_playground}/plaintext_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/plaintext/expected_output/output_to_lower.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --to_lower < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerIgnoreNewlines(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_test_playground}/plaintext_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/plaintext/expected_output/output_ignore_newlines.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_newlines < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)

    def testPlaintextTokenizerIgnoreEverything(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_test_playground}/plaintext_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/plaintext/expected_output/output_ignore_everything.json"

        command = f"{lichen_installation_dir}/bin/plaintext_tokenizer.out --ignore_punctuation --to_lower --ignore_numbers --ignore_newlines  < {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)


class TestMIPSTokenizer(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(os.path.join(lichen_test_playground, 'mips_tokenizer')):
            os.makedirs(os.path.join(lichen_test_playground, 'mips_tokenizer'))

    def tearDown(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'mips_tokenizer'))

    def testMIPSTokenizer(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/mips/input.s"
        output_file = f"{lichen_test_playground}/mips_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/mips/expected_output/output.json"

        command = f"python3 {lichen_installation_dir}/bin/mips_tokenizer.py {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)


class TestCTokenizer(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(os.path.join(lichen_test_playground, 'c_tokenizer')):
            os.makedirs(os.path.join(lichen_test_playground, 'c_tokenizer'))

    def tearDown(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'c_tokenizer'))

    def testMIPSTokenizer(self):
        self.maxDiff = None

        input_file = "./data/tokenizer/c/input.cpp"
        output_file = f"{lichen_test_playground}/c_tokenizer/output.json"
        expected_output_file = "./data/tokenizer/c/expected_output/output.json"

        command = f"python {lichen_installation_dir}/bin/c_tokenizer.py {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            actual_output = file.read()

        with open(expected_output_file) as file:
            expected_output = file.read()

        self.assertEqual(actual_output, expected_output)


class TestHashAll(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(lichen_test_playground):
            os.makedirs(lichen_test_playground)

    def tearDown(self):
        shutil.rmtree(lichen_test_playground)

    def testHashAll(self):
        # make the fake directory structure hash_all.py expects
        os.makedirs(f"{lichen_test_playground}/test_hash_all/provided_code")
        os.makedirs(f"{lichen_test_playground}/test_hash_all/other_gradeables")
        os.makedirs(f"{lichen_test_playground}/test_hash_all/users/student/1")
        open(f"{lichen_test_playground}/test_hash_all/config.json", 'a').close()
        open(f"{lichen_test_playground}/test_hash_all/users/student/1/tokens.json", 'a').close()
        with open(f"{lichen_test_playground}/test_hash_all/provided_code/tokens.json", 'w') as file:
            file.write("null")

        # copy the input files from /data to the the new path
        shutil.copyfile("data/hash_all/config.json", f"{lichen_test_playground}/test_hash_all/config.json")
        shutil.copyfile("data/hash_all/tokens.json", f"{lichen_test_playground}/test_hash_all/users/student/1/tokens.json")

        # save current working directory
        cwd = os.getcwd()

        # run hash_all
        os.chdir(f"{lichen_installation_dir}/bin")
        os.system(f"python3 {lichen_installation_dir}/bin/hash_all.py {lichen_test_playground}/test_hash_all > /dev/null")
        os.chdir(cwd)

        # test output
        hashes_file = f"{lichen_test_playground}/test_hash_all/users/student/1/hashes.txt"
        with open(hashes_file, 'r') as file:
            lines = file.readlines()
        lines = [x.strip() for x in lines]
        tokens_file = f"{lichen_test_playground}/test_hash_all/users/student/1/tokens.json"
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
