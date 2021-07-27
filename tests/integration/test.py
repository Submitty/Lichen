import unittest
import os
import shutil
from filecmp import dircmp

lichen_installation_dir = "/usr/local/submitty/Lichen"
lichen_test_playground = "/usr/local/submitty/Lichen/test_output"


class TestLichen(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'test_lichen'), ignore_errors=True)
        os.makedirs(os.path.join(lichen_test_playground, 'test_lichen'))

    def tearDown(self):
        shutil.rmtree(os.path.join(lichen_test_playground, 'test_lichen'))

    def testLichen(self):
        for test_case in sorted(os.listdir('../data/test_lichen')):
            # make the fake directory where the config.json is saved
            base_path = f"{lichen_test_playground}/test_lichen/{test_case}"
            os.makedirs(base_path)

            # copy the input files from /data to the the new path
            data_path = f"../data/test_lichen/{test_case}/input"
            shutil.copyfile(f"{data_path}/config.json", f"{base_path}/config.json")

            # run Lichen
            os.system(f"bash {lichen_installation_dir}/bin/process_all.sh {base_path} {data_path}")

            dcmp = dircmp(f"../data/test_lichen/{test_case}/expected_output", base_path)
            #test = dcmp.report_full_closure()
            # self.assertEqual(len(dcmp.diff_files), 0)
