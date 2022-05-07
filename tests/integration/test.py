import unittest
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


test_data_dir = Path(__file__).resolve().parent / '..' / 'data'


class TestLichen(unittest.TestCase):
    def testLichen(self):
        self.maxDiff = None
        for test_case in sorted(os.listdir(Path(test_data_dir, "test_lichen"))):
            print(f"running integration test for {test_case}...")

            with TemporaryDirectory() as temp_dir:
                # copy the input files from /data to the the new path
                data_path = Path(test_data_dir, "test_lichen", test_case, "input")
                shutil.copyfile(Path(data_path, "config.json"), Path(temp_dir, "config.json"))

                # change the group for the temporary directory such that it matches the input group
                subprocess.check_call(f"chgrp -R {data_path.group()} {temp_dir}", shell=True)

                # run Lichen
                subprocess.check_call(f"bash {str(Path(__file__).resolve().parent.parent.parent)}/bin/run_lichen.sh {str(temp_dir)} {str(data_path)}", shell=True)

                ex_output_path = Path(test_data_dir, "test_lichen", test_case, "expected_output")

                # compare the output and expected output directory structure and file contents
                ignored_files_count = 0
                ex_files_count = 0
                for root, dirs, files in os.walk(ex_output_path):
                    ex_files_count += len(dirs) + len(files)
                    for file in files:
                        if file == "lichen_job_output.txt":
                            continue
                        if file == "git_placeholder.txt":
                            ignored_files_count += 1
                            continue

                        ex_path = Path(root, file)
                        if root.replace(str(ex_output_path), "") == "":
                            act_path = Path(temp_dir, file)
                        else:
                            act_path = Path(temp_dir, root.replace(str(ex_output_path), "").strip("/"), file)

                        with open(ex_path) as ex_file:
                            with open(act_path) as act_file:
                                self.assertEqual(ex_file.read().strip(), act_file.read().strip())

                    for dir in dirs:
                        ex_path = Path(root, dir)
                        if root.replace(str(ex_output_path), "") == "":
                            act_path = Path(temp_dir, dir)
                        else:
                            act_path = Path(temp_dir, root.replace(str(ex_output_path), "").strip("/"), dir)
                        self.assertTrue(os.path.isdir(ex_path))
                        self.assertTrue(os.path.isdir(act_path))

                act_files_count = 0
                for _, dirs, files in os.walk(Path(temp_dir)):
                    act_files_count += len(dirs) + len(files)

                # ensure that we didn't miss any files by checking that there are the same number of files in each directory
                self.assertEqual(ex_files_count - ignored_files_count, act_files_count)
