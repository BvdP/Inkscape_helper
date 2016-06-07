from __future__ import division
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
        curve_points = [[C00, C01, C01 * 2, C01 * 3], [C00, C10, C10 * 2, C10 * 3], [C00, C11, C11 * 2, C11 * 3]]
        for points in curve_points:
            quadr = BezierCurve(points[:-1])
            twoparts, rest = quadr.subdivide(points[1].r)
            self.assertTrue(points[1].close_enough_to(twoparts[1].coord) , 'subdivide quadratic bezier in two parts')
            cubic = BezierCurve(points)
            threeparts, rest = cubic.subdivide(points[1].r)
            self.assertTrue(points[1].close_enough_to(threeparts[1].coord), 'subdivide cubic bezier in three parts, 1st point')
            self.assertTrue(points[2].close_enough_to(threeparts[2].coord), 'subdivide cubic bezier in three parts, 2nd point')

    def test_elliptic_arc_center(self):
        C20_0 = Coordinate(20, 0)
        C0_10 = Coordinate(0, 10)
        C20_10 = Coordinate(20, 10)
        arc = EllipticArc(C20_0, C0_10, 20, 10, 0)
        self.assertEqual(arc.center, C00, 'ellipse center')
        large_arc = EllipticArc(C20_0, C0_10, 20, 10, 0, large_arc = True)
        self.assertEqual(large_arc.center, C20_10, 'ellipse center large arc')
        neg_arc = EllipticArc(C20_0, C0_10, 20, 10, 0, pos_dir = False)
        self.assertEqual(neg_arc.center, C20_10, 'ellipse center large arc')

    def test_elliptic_arc_length(self):
        pass

    def test_elliptic_arc_subdivide(self):
        pass

def pretty_close(a ,b, tolerance=1E-4):
    return abs(a - b) < tolerance  #TODO: current ellipse and bezier interpolation is always on the short side

class TestEllipse(unittest.TestCase, Effect):
    def setUp(self):
        self.circle = Ellipse(10, 10)

    def test_coordinate_at_theta(self):
        ell = Ellipse(12,8)
        self.assertEqual(ell.coordinate_at_theta(0), Coordinate(12, 0), 'coordinate at angle 0')
        self.assertTrue(Coordinate(0, 8).close_enough_to(ell.coordinate_at_theta(pi/2)), 'coordinate at angle pi/2')
        self.assertTrue(Coordinate(-12, 0).close_enough_to(ell.coordinate_at_theta(pi)), 'coordinate at angle pi')
        self.assertTrue(Coordinate(0, -8).close_enough_to(ell.coordinate_at_theta(3*pi/2)), 'coordinate at angle 3*pi/2')

    def test_circle(self):
        self.assertTrue(pretty_close(self.circle.circumference, 20 * pi), 'circumference circle')
        self.assertTrue(pretty_close(self.circle.dist_from_theta(0, pi), 10 * pi))
        self.assertTrue(pretty_close(self.circle.theta_from_dist(0, 10 * pi), pi))

    def test_theta_at_angle(self):
        ell = Ellipse(20, 10)
        # straight angles
        self.assertEqual(ell.theta_at_angle(0), 0, 'theta at 0')
        self.assertEqual(ell.theta_at_angle(pi / 2), pi / 2, 'theta at 90')
        self.assertTrue(pretty_close(ell.theta_at_angle(pi), pi, 1e-15), 'theta at 180')
        self.assertEqual(ell.theta_at_angle(3 * pi / 2), 3 * pi / 2, 'theta at 270')
        # 45 degrees
        self.assertEqual(ell.theta_at_angle(pi / 4), atan(2), 'theta at 45')

    def test_curvature(self):
        ell = Ellipse(20, 10)
        self.assertEqual(ell.curvature(0), 1/5, 'curvature at 0')
        self.assertEqual(ell.curvature(pi / 2), 1/40, 'curvature at 90')
        self.assertEqual(ell.curvature(pi), 1/5, 'curvature at 180')
        self.assertEqual(ell.curvature(3 * pi / 2), 1/40, 'curvature at 270')


coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
path_t = unittest.TestLoader().loadTestsFromTestCase(TestPath)
ellipse_t = unittest.TestLoader().loadTestsFromTestCase(TestEllipse)
segment_t = unittest.TestLoader().loadTestsFromTestCase(TestPathSegment)


suite = unittest.TestSuite([coordinate_t, intersection_t, path_t, segment_t, ellipse_t])
unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()
