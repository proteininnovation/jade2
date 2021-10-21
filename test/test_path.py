import unittest
import warnings
import shutil

import jade2.basic.path as jade_path

class TestPath(unittest.TestCase):
    def test_find_database(self):
        s = jade_path.get_database_path()
        self.assertTrue(isinstance(s, str))

        contents = jade_path.parse_contents(jade_path.get_database_testing_path())
        self.assertEqual(contents[0], "TEST_ASSERT")


if __name__ == '__main__':
    unittest.main()