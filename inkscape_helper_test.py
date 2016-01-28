import sys
sys.path.append("C:\\Program Files\\Inkscape\\share\\extensions")

import unittest
from inkscape_helper import *

class TestIntersection(unittest.TestCase):
    def setUp(self):
        self.C00 = Coordinate(0, 0)
        self.C10 = Coordinate(1, 0)
        self.C01 = Coordinate(0, 1)
        self.C11 = Coordinate(1, 1)

    def test_on_segment(self):
        self.assertTrue(on_segment(self.C11, self.C00, self.C11), 'Endpoint on segment')
        self.assertTrue(on_segment(self.C00, self.C00, self.C11), 'Start point on segment')
        self.assertTrue(on_segment(self.C11 / 2, self.C00, self.C11), 'Midpoint on segment')
        self.assertFalse(on_segment(self.C11 * 2, self.C00, self.C11), 'Beyond endpoint')
        self.assertFalse(on_segment(self.C11 * -1, self.C00, self.C11), 'Before start point')


    def test_parallel(self):
        self.assertRaises(IntersectionError, intersection, self.C00, self.C01, self.C10, self.C11)

    def test_out_segment_error(self):
        self.assertRaises(IntersectionError, intersection, self.C01, self.C01 * 2, self.C10, self.C10 * 2)

    def test_out_segment_intersection(self):
        self.assertEqual(intersection(self.C01, self.C01 * 2, self.C10, self.C10 * 2, False), self.C00)

    def test_in_segment_intersection(self):
        self.assertEqual(intersection(self.C00, self.C11, self.C10, self.C01), Coordinate(.5, .5))


class TestCoordinate(unittest.TestCase):
    def setUp(self):
        self.CX = Coordinate(1, 0)
        self.CY = Coordinate(0, 1)
        self.C11 = Coordinate(1, 1)

    def test_eq(self):
        self.assertEqual(Coordinate(1, 2), Coordinate(1, 2))

    def test_add(self):
        sum = self.CX + self.CY
        self.assertEqual(sum, self.C11)

    def test_sub(self):
        diff = self.C11 - self.CX
        self.assertEqual(diff, self.CY)

    def test_mul(self):
        prod = self.C11 * 2
        self.assertEqual(prod, Coordinate(2, 2))

    def test_rmul(self):
        prod = 2 * self.C11
        self.assertEqual(prod, Coordinate(2, 2))

    def test_div(self):
        quot = self.C11 / 2
        self.assertEqual(quot, Coordinate(.5, .5))

    def test_r(self):
        self. assertEqual(self.C11.r, sqrt(2))

    def test_t(self):
        self.assertEqual(self.C11.t, pi/4)


class TestPath(unittest.TestCase, Effect):
    # def __init__(self, *args, **kwargs):
        # print args, kwargs
        # unittest.TestCase.__init__(*args, **kwargs)
        # Effect.__init__()

    def setUp(self):
        #eff = inkex.Effect()
        Effect.__init__(self)
        self.affect(['empty.svg'])
        #self.doc_root = eff.document.getroot()
        self.C00 = Coordinate(0, 0)
        self.C10 = Coordinate(1, 0)
        self.C01 = Coordinate(0, 1)
        self.C11 = Coordinate(1, 1)

    def test_line(self):
        p = Path()
        parent = self.document.getroot()
        p.move_to(self.C00, True)
        p.line_to(self.C11)
        p.path(parent, default_style)
        p_str = inkex.etree.tostring(self.document)
        #print(p_str, p.nodes)
        self.assertEqual(p.nodes, ['M {0} {1}'.format(0.0, 0.0), 'l {0} {1}'.format(1.0, 1.0)])



coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
path_t = unittest.TestLoader().loadTestsFromTestCase(TestPath)

suite = unittest.TestSuite([coordinate_t, intersection_t, path_t])
unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()
