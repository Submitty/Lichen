import unittest
import os
import shutil

lichen_installation_dir = "/usr/local/submitty/Lichen"
lichen_test_playground = "/usr/local/submitty/Lichen/test_output"


class TestLichen(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'test_lichen'), ignore_errors=True)
        os.makedirs(os.path.join(lichen_test_playground, 'test_lichen'))

    def tearDown(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'test_lichen'))

    def testLichen(self):
        self.maxDiff = None
        for test_case in sorted(os.listdir('../data/test_lichen')):
            print(f"running integration test for {test_case}...")
            # make the fake directory where the config.json is saved
            base_path = f"{lichen_test_playground}/test_lichen/{test_case}"
            os.makedirs(base_path)

            # copy the input files from /data to the the new path
            data_path = f"{os.getcwd()}/../data/test_lichen/{test_case}/input"
            shutil.copyfile(f"{data_path}/config.json", f"{base_path}/config.json")

            # run Lichen
            os.system(f"bash {lichen_installation_dir}/bin/process_all.sh {base_path} {data_path}")

            ex_output_path = f"../data/test_lichen/{test_case}/expected_output"

            # compare the output and expected output directory structure and file contents
            ex_files_count = 0
            for root, dirs, files in os.walk(ex_output_path):
                ex_files_count += len(dirs) + len(files)
                for file in files:
                    if file != "lichen_job_output.txt":
                        ex_path = f"{root}/{file}"
                        if root.replace(ex_output_path, '') == "":
                            act_path = f"{base_path}/{file}"
                        else:
                            act_path = f"{base_path}/{root.replace(ex_output_path, '')}/{file}"

                        with open(ex_path) as ex_file:
                            with open(act_path) as act_file:
                                self.assertEqual(ex_file.read().strip(), act_file.read().strip())

                for dir in dirs:
                    ex_path = f"{root}/{dir}"
                    act_path = f"{base_path}/{root.replace(ex_output_path, '')}/{dir}"
                    self.assertTrue(os.path.isdir(ex_path))
                    self.assertTrue(os.path.isdir(act_path))

            act_files_count = 0
            for _, dirs, files in os.walk(base_path):
                act_files_count += len(dirs) + len(files)

            # NOTE: We must subtract two here because git doesn't store empty directories
            # This will have to change in the future when we add more test gradeables
            # may not have empty directories
            self.assertEqual(ex_files_count, act_files_count - 2)
