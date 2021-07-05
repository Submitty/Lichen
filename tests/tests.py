import unittest
import os

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


if __name__ == '__main__':
    unittest.main()
