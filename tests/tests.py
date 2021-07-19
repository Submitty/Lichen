import unittest
import os
import shutil

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

        # clean up the files
        os.remove(output_file)

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

        # clean up the files
        os.remove(output_file)

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

        # clean up the files
        os.remove(output_file)

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

        # clean up the files
        os.remove(output_file)

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

        # clean up the files
        os.remove(output_file)


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

        # clean up the files
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
