import unittest 

import xboa.common.config as config


class TestConfig(unittest.TestCase):
    def test_print_config(self):
        config.print_config()

    def test_has_root(self):
        try:
            config.has_root()
        except ImportError:
            pass

    def test_has_numpy(self):
        try:
          config.has_numpy()
        except ImportError:
            pass

    def test_has_scipy(self):
        try:
            config.has_scipy()
        except ImportError:
            pass

    def test_has_json(self):
        try:
            config.has_json()
        except ImportError:
            pass

    def test_has_multiprocessing(self):
        try:
            config.has_multiprocessing()
        except ImportError:
            pass

    def test_has_maus(self):
        try:
            config.has_maus()
        except ImportError:
            pass

    def test_has_matplot(self):
        try:
            config.has_matplot()
        except ImportError:
            pass

if __name__ == "__main__":
    unittest.main()


