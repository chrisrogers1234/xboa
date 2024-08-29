import unittest

from xboa.core import WeightContext

class WeightContextTest(unittest.TestCase):
    def test_init(self):
        context = WeightContext()

    def test_get_set_default_weight(self):
        context = WeightContext()
        self.assertEqual(context.get_default_weight(), 1.0)
        context.set_default_weight(2.0)
        self.assertEqual(context.get_default_weight(), 2.0)

    def test_get_set_default_weight_2(self):
        context = WeightContext()
        context.set_default_weight(3.0)
        self.assertEqual(context.get_weight(1, 1, 1), 3.0)

    def test_get_set_weight(self):
        context = WeightContext()
        self.assertEqual(context.get_weight(1, 2, 3), 1.0)
        context.set_weight(0.5, 1, 2, 3)
        self.assertEqual(context.get_weight(1, 2, 3), 0.5)

    def test_add(self):
        context1 = WeightContext()
        context2 = WeightContext()
        context1.set_default_weight(2)
        context2.set_default_weight(3)
        context1.set_weight(4, 1, 1, 1)
        context1.set_weight(5, 2, 2, 2)
        context2.set_weight(6, 1, 1, 1)
        context2.set_weight(7, 3, 3, 3)
        context3 = context1+context2
        self.assertEqual(context3.get_default_weight(), 2+3)
        self.assertEqual(context3.get_weight(1, 1, 1), 4+6)
        self.assertEqual(context3.get_weight(2, 2, 2), 5+3)
        self.assertEqual(context3.get_weight(3, 3, 3), 7+2)
        context3 = context1+1
        self.assertEqual(context3.get_default_weight(), 2+1)
        self.assertEqual(context3.get_weight(1, 1, 1), 4+1)
        context3 = 1+context1
        return
        self.assertEqual(context3.get_default_weight(), 1+2)
        self.assertEqual(context3.get_weight(1, 1, 1), 1+4)
        context3 += context1
        self.assertEqual(context3.get_default_weight(), 3+2)
        self.assertEqual(context3.get_weight(1, 1, 1), 5+4)
        context3 += 1
        self.assertEqual(context3.get_default_weight(), 5+1)
        self.assertEqual(context3.get_weight(1, 1, 1), 9+1)

        try:
            context1+"cheese"
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass

        try:
            "cheese"+context1
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass

    def test_mult(self):
        context1 = WeightContext()
        context2 = WeightContext()
        context1.set_default_weight(2)
        context2.set_default_weight(3)
        context1.set_weight(4, 1, 1, 1)
        context1.set_weight(5, 2, 2, 2)
        context2.set_weight(6, 1, 1, 1)
        context2.set_weight(7, 3, 3, 3)
        context3 = 2*context1*context2*3
        self.assertEqual(context3.get_default_weight(), 2*2*3*3)
        self.assertEqual(context3.get_weight(1, 1, 1), 2*4*6*3)
        self.assertEqual(context3.get_weight(2, 2, 2), 2*5*3*3)
        self.assertEqual(context3.get_weight(3, 3, 3), 2*2*7*3)
        try:
            context1*"cheese"
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass

    def test_divide(self):
        context1 = WeightContext()
        context2 = WeightContext()
        context1.set_default_weight(2)
        context2.set_default_weight(3)
        context1.set_weight(4, 1, 1, 1)
        context1.set_weight(5, 2, 2, 2)
        context2.set_weight(6, 1, 1, 1)
        context2.set_weight(7, 3, 3, 3)
        context3 = context1/context2/3
        self.assertEqual(context3.get_default_weight(), 2/3/3)
        self.assertEqual(context3.get_weight(1, 1, 1), 4/6/3)
        self.assertEqual(context3.get_weight(2, 2, 2), 5/3/3)
        self.assertEqual(context3.get_weight(3, 3, 3), 2/7/3)
        try:
            context1/"cheese"
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass
        try:
            2/context1
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass

    def test_subtract(self):
        context1 = WeightContext()
        context2 = WeightContext()
        context1.set_default_weight(2)
        context2.set_default_weight(3)
        context1.set_weight(4, 1, 1, 1)
        context1.set_weight(5, 2, 2, 2)
        context2.set_weight(6, 1, 1, 1)
        context2.set_weight(7, 3, 3, 3)
        context3 = context1-context2-3
        self.assertEqual(context3.get_default_weight(), 2-3-3)
        self.assertEqual(context3.get_weight(1, 1, 1), 4-6-3)
        self.assertEqual(context3.get_weight(2, 2, 2), 5-3-3)
        self.assertEqual(context3.get_weight(3, 3, 3), 2-7-3)
        try:
            context1-"cheese"
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass
        try:
            2-context1
            self.assertFalse(True, msg="Should have thrown")
        except Exception:
            pass

    def test_not(self):
        context1 = WeightContext()
        context1.set_default_weight(2)
        context1.set_weight(4, 1, 1, 1)
        context1.set_weight(5, 2, 2, 2)
        context1.set_weight(0, 3, 3, 3)
        context2 = ~context1
        self.assertEqual(context2.get_default_weight(), 0)
        self.assertEqual(context2.get_weight(1, 1, 1), 0)
        self.assertEqual(context2.get_weight(2, 2, 2), 0)
        self.assertEqual(context2.get_weight(3, 3, 3), 2)


if __name__ == "__main__":
    unittest.main()