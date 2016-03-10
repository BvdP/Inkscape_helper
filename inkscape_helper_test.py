import sys
sys.path.append("C:\\Program Files\\Inkscape\\share\\extensions")
sys.path.append("/usr/share/inkscape/extensions")

import unittest
from inkscape_helper import *

C00 = Coordinate(0, 0)
C10 = Coordinate(1, 0)
C01 = Coordinate(0, 1)
C11 = Coordinate(1, 1)


class TestIntersection(unittest.TestCase):

    def test_on_segment(self):
        self.assertTrue(on_segment(C11, C00, C11), 'Endpoint on segment')
        self.assertTrue(on_segment(C00, C00, C11), 'Start point on segment')
        self.assertTrue(on_segment(C11 / 2, C00, C11), 'Midpoint on segment')
        self.assertFalse(on_segment(C11 * 2, C00, C11), 'Beyond endpoint')
        self.assertFalse(on_segment(C11 * -1, C00, C11), 'Before start point')


    def test_parallel(self):
        self.assertRaises(IntersectionError, intersection, C00, C01, C10, C11)

    def test_out_segment_error(self):
        self.assertRaises(IntersectionError, intersection, C01, C01 * 2, C10, C10 * 2)

    def test_out_segment_intersection(self):
        self.assertEqual(intersection(C01, C01 * 2, C10, C10 * 2, False), C00)

    def test_in_segment_intersection(self):
        self.assertEqual(intersection(C00, C11, C10, C01), Coordinate(.5, .5))


class TestCoordinate(unittest.TestCase):
    def setUp(self):
        self.CX = Coordinate(1, 0)
        self.CY = Coordinate(0, 1)

    def test_eq(self):
        self.assertEqual(Coordinate(1, 2), Coordinate(1, 2))

    def test_add(self):
        sum = self.CX + self.CY
        self.assertEqual(sum, C11)

    def test_sub(self):
        diff = C11 - self.CX
        self.assertEqual(diff, self.CY)

    def test_mul(self):
        prod = C11 * 2
        self.assertEqual(prod, Coordinate(2, 2))

    def test_rmul(self):
        prod = 2 * C11
        self.assertEqual(prod, Coordinate(2, 2))

    def test_div(self):
        quot = C11 / 2
        self.assertEqual(quot, Coordinate(.5, .5))

    def test_r(self):
        self. assertEqual(C11.r, sqrt(2))

    def test_t(self):
        self.assertEqual(C11.t, pi/4)


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

    def test_line(self):
        p = Path()
        parent = self.document.getroot()
        p.move_to(C00, True)
        p.line_to(C11)
        p.path(parent, default_style)
        p_str = inkex.etree.tostring(self.document)
        #print(p_str, p.nodes)
        self.assertEqual(p.nodes, ['M {0} {1}'.format(0.0, 0.0), 'l {0} {1}'.format(1.0, 1.0)])


class TestPathSegment(unittest.TestCase, Effect):
    #def setUp(self):

    def test_quadratic_bezier(self):
        quadratic = BezierCurve([C10, C11, C01])
        self.assertEqual(quadratic.pathpoint_at_t(0).coord, C10, 'start point')
        self.assertEqual(quadratic.pathpoint_at_t(1).coord, C01, 'end point')

    def test_cubic_bezier(self):
        cubic = BezierCurve([C10, C11, C00, C01])
        self.assertEqual(cubic.pathpoint_at_t(0).coord, C10, 'start point')
        self.assertEqual(cubic.pathpoint_at_t(1).coord, C01, 'end point')

    def test_bezier_length(self):
        line = BezierCurve([C00, C10, C10 * 2])
        self.assertEqual(line.pathpoint_at_t(0.5).coord, C10, 'midpoint by t')
        self.assertEqual(line.t_at_length(0), 0, 'starting point t by length')
        self.assertEqual(line.t_at_length(1), 0.5, 'midpoint t by length')
        self.assertEqual(line.t_at_length(2), 1, 'endpoint t by length')

    def test_line_subdivide(self):
        line = Line(C01, C10)
        self.assertEqual(line.subdivide(0.4, 0.05)[-1],sqrt(2) - 0.05 - 3 * 0.4, 'remaining length of subdivided line')

    def test_bezier_subdivide(self):
        quadr = BezierCurve([C00, C11, C11 * 2])
        twoparts, rest = quadr.subdivide(sqrt(2))
        #print twoparts, rest
        self.assertEqual(twoparts[1].coord, C11, 'subdivide quadratic bezier in two parts')
        cubic = BezierCurve([C00, C11, C11 * 2, C11 * 3])
        threeparts, rest = cubic.subdivide(sqrt(2))
        self.assertEqual(threeparts[1].coord, C11, 'subdivide cubic bezier in three parts')

coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
path_t = unittest.TestLoader().loadTestsFromTestCase(TestPath)
segment_t = unittest.TestLoader().loadTestsFromTestCase(TestPathSegment)


suite = unittest.TestSuite([coordinate_t, intersection_t, path_t, segment_t])
unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()
