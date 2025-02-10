import unittest

import xboa.common.utils


class TestUtils(unittest.TestCase):
    def test_require_modules(self):
        xboa.common.utils.require_modules("unittest")
        xboa.common.utils.require_modules(["unittest"])
        xboa.common.utils.require_modules(["unittest", "xboa.common.utils"])
        try:
            xboa.common.utils.require_modules(["bob"])
            self.assertTrue(False, "should have thrown")
        except ImportError:
            pass
        try:
            xboa.common.utils.require_modules(["unittest", "bob"])
            self.assertTrue(False, "should have thrown")
        except ImportError:
            pass

if __name__ == "__main__":
    unittest.main()
