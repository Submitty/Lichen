import unittest
import os

lichen_repository_dir = "/usr/local/submitty/GIT_CHECKOUT/Lichen/"
lichen_installation_dir = "/usr/local/submitty/Lichen/"
lichen_data_dir = "/var/local/submitty/courses/"


class TestPlaintextTokenizer(unittest.TestCase):
    def testPlaintextTokenizer(self):
        input_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/input.txt"
        output_file = f"{lichen_data_dir}/f21/test_tokenizers/lichen/plaintext_tokenizer_tests/output.json"
        # expected_output_file = f"{lichen_repository_dir}/tests/data/tokenizer/plaintext/output.json"

        command = f"{lichen_installation_dir}/plaintext_tokenizer.out {input_file} > {output_file}"
        os.system(command)

        with open(output_file) as file:
            print(file.read())

        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
