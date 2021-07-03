import unittest
import os

lichen_repository_dir = "/usr/local/submitty/GIT_CHECKOUT/Lichen"
lichen_installation_dir = "/usr/local/submitty/Lichen"
lichen_data_dir = "/var/local/submitty/courses"


class TestPlaintextTokenizer(unittest.TestCase):
    def testPlaintextTokenizer(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/plaintext_tokenizer_tests/output.json"
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

    def testPlaintextTokenizerIgnoreNewlines(self):
        self.maxDiff = None

        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/plaintext_tokenizer_tests/output.json"
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


if __name__ == '__main__':
    unittest.main()
