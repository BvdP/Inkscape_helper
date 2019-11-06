import unittest

from inkscape_helper.Effect import Effect
from inkscape_helper.PathSegment import PathSegment
from inkscape_helper.BezierCurve import BezierCurve
from inkscape_helper.Line import Line
from inkscape_helper.Coordinate import Coordinate

from math import sqrt

C00 = Coordinate(0, 0)
C10 = Coordinate(1, 0)
C01 = Coordinate(0, 1)
C11 = Coordinate(1, 1)

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
