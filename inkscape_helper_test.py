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

C20_0 = Coordinate(20, 0)
C0_10 = Coordinate(0, 10)
C10_0 = Coordinate(10, 0)
C20_10 = Coordinate(20, 10)

class TestEllipticArc(unittest.TestCase, Effect):
    def test_elliptic_arc_center(self):
        arc = EllipticArc(C20_0, C0_10, 20, 10, 0)
        self.assertEqual(arc.center, C00, 'ellipse center')
        large_arc = EllipticArc(C20_0, C0_10, 20, 10, 0, large_arc = True)
        self.assertEqual(large_arc.center, C20_10, 'ellipse center large arc')
        neg_arc = EllipticArc(C20_0, C0_10, 20, 10, 0, pos_dir = False)
        self.assertEqual(neg_arc.center, C20_10, 'ellipse center large arc')

    def test_t_to_theta(self):
        arc = EllipticArc(C10_0, C0_10, 10, 10, 2) # quarter circle, axis rotated by 2 rad
        self.assertEqual(arc.t_to_theta(1), pi/2)
        self.assertEqual(arc.t_to_theta(0.5), pi/4)

    def test_theta_to_t(self):
        arc = EllipticArc(C10_0, C0_10, 10, 10, 2)
        self.assertEqual(arc.theta_to_t(pi/2), 1)
        self.assertEqual(arc.theta_to_t(pi/4), 0.5)

    def test_elliptic_arc_length(self):
        arc = EllipticArc(C10_0, C0_10, 10, 10, 2)
        self.assertTrue(pretty_close(arc.length, 10 * pi/2))

    def test_pathpoint_at_t(self):
        arc = EllipticArc(C10_0, Coordinate(-10, 0), 10, 20, 2)
        self.assertTrue(arc.pathpoint_at_t(0.5).coord.close_enough_to(Coordinate(0, 20)), 'coordinate at 90')
        self.assertEqual(arc.tangent(0.5).t, pi/2, 'tangent at 90')

    def test_elliptic_arc_subdivide(self):
        pass


    def test_real_world(self):
        #c1 = Coordinate(540.00001999999995, 566.64795000000004)
        #c2 = Coordinate(368.57144, 672.36224000000004)
        #c3 = Coordinate(197.14286999999999, 566.64795000000004)
        #c4 = Coordinate(368.57144, 460.93365999999997)
        #rx, ry = 171.42857000000001, 105.71429000000001
        c1 = Coordinate(600, 500)
        c2 = Coordinate(400, 600)
        c3 = Coordinate(200, 500)
        c4 = Coordinate(400, 400)
        rx, ry = 200, 100
        e1 = EllipticArc(c1, c2, rx, ry, 0, True, False)
        e2 = EllipticArc(c2, c3, rx, ry, 0, True, False)
        e3 = EllipticArc(c3, c4, rx, ry, 0, True, False)
        e4 = EllipticArc(c4, c1, rx, ry, 0, True, False)

        # start & end points
        self.assertTrue(c1.close_enough_to(e1.pathpoint_at_t(0).coord), 'start e1')
        self.assertTrue(c2.close_enough_to(e1.pathpoint_at_t(1).coord), 'end e1')
        self.assertTrue(c2.close_enough_to(e2.pathpoint_at_t(0).coord), 'start e2')
        self.assertTrue(c3.close_enough_to(e2.pathpoint_at_t(1).coord), 'end e2')
        self.assertTrue(c3.close_enough_to(e3.pathpoint_at_t(0).coord), 'start e3')
        self.assertTrue(c4.close_enough_to(e3.pathpoint_at_t(1).coord), 'end e3')
        self.assertTrue(c4.close_enough_to(e4.pathpoint_at_t(0).coord), 'start e4')
        self.assertTrue(c1.close_enough_to(e4.pathpoint_at_t(1).coord), 'end e4')

        #centers
        center = (c1 + c2 + c3 + c4) / 4
        self.assertEqual(center, e1.center, 'center e1')
        self.assertEqual(center, e2.center, 'center e2')
        self.assertEqual(center, e3.center, 'center e3')
        self.assertEqual(center, e4.center, 'center e4')

        #angles
        self.assertEqual(e1.start_theta, 0, 'e1 start theta')
        self.assertEqual(e1.end_theta, pi / 2, 'e1 end theta')
        self.assertEqual(e2.start_theta, pi / 2, 'e2 start theta')
        self.assertTrue(pretty_close(e2.end_theta, pi) , 'e2 end theta')
        self.assertTrue(pretty_close(e3.start_theta, pi) , 'e3 start theta')
        #self.assertEqual(e3.start_theta, pi, 'e3 start theta')
        self.assertEqual(e3.end_theta, 3 * pi / 2, 'e3 end theta')
        self.assertEqual(e4.start_theta, 3 * pi / 2, 'e4 start theta')
        self.assertEqual(e4.end_theta, 0, 'e4 end theta')

        #halfway points
        he1 = e1.pathpoint_at_t(0.5).coord
        hl1 = (c1 + c2) / 2
        self.assertTrue((c1.x > he1.x > hl1.x) and (c2.y > he1.y > hl1.y), 'h1')
        he2 = e2.pathpoint_at_t(0.5).coord
        hl2 = (c2 + c3) / 2
        self.assertTrue((hl2.x > he2.x > c3.x) and (c2.y > he2.y > hl2.y), 'h2')
        he3 = e3.pathpoint_at_t(0.5).coord
        hl3 = (c3 + c4) / 2
        self.assertTrue((hl3.x > he3.x > c3.x) and (hl3.y > he3.y > c4.y), 'h3')
        he4 = e1.pathpoint_at_t(0.5).coord
        hl4 = (c4 + c1) / 2
        self.assertTrue((c1.x > he4.x > hl4.x) and (hl4.y > he4.y > c4.y), 'h4')

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
        self.assertTrue(pretty_close(self.circle.dist_from_theta(0, pi), 10 * pi), 'arc length 0 -> pi')
        self.assertTrue(pretty_close(self.circle.dist_from_theta(3 * pi / 2, 0), 5 * pi), 'arc length 3 * pi / 2 -> 0')
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

    def test_dist_from_theta(self):
        pass

    def test_theta_from_dist(self):
        pass


coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
path_t = unittest.TestLoader().loadTestsFromTestCase(TestPath)
ellipse_t = unittest.TestLoader().loadTestsFromTestCase(TestEllipse)
ell_arc_t = unittest.TestLoader().loadTestsFromTestCase(TestEllipticArc)
segment_t = unittest.TestLoader().loadTestsFromTestCase(TestPathSegment)


suite = unittest.TestSuite([coordinate_t, intersection_t, path_t, segment_t, ellipse_t, ell_arc_t])
unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()
