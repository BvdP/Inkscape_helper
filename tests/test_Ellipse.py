from __future__ import division
#from inkscape_helper.Effect.Effect import Effect
from inkscape_helper.Ellipse import Ellipse
from inkscape_helper.Coordinate import Coordinate

from math import pi, atan

import unittest


class TestEllipse(unittest.TestCase):
    def setUp(self):
        self.circle = Ellipse(10, 10)

    def test_coordinate_at_theta(self):
        ell = Ellipse(12,8)
        self.assertEqual(ell.coordinate_at_theta(0), Coordinate(12, 0), 'coordinate at angle 0')
        self.assertTrue(Coordinate(0, 8).close_enough_to(ell.coordinate_at_theta(pi/2)), 'coordinate at angle pi/2')
        self.assertTrue(Coordinate(-12, 0).close_enough_to(ell.coordinate_at_theta(pi)), 'coordinate at angle pi')
        self.assertTrue(Coordinate(0, -8).close_enough_to(ell.coordinate_at_theta(3*pi/2)), 'coordinate at angle 3*pi/2')

    def test_circle(self):
        self.assertAlmostEqual(self.circle.circumference, 20 * pi, 3, 'circumference circle')
        self.assertAlmostEqual(self.circle.dist_from_theta(0, pi), 10 * pi, 3,'arc length 0 -> pi')
        self.assertAlmostEqual(self.circle.dist_from_theta(3 * pi / 2, 0), 5 * pi, 3, 'arc length 3 * pi / 2 -> 0')
        self.assertAlmostEqual(self.circle.theta_from_dist(0, 10 * pi), pi, 5)

    def test_theta_at_angle(self):
        ell = Ellipse(20, 10)
        # straight angles
        self.assertEqual(ell.theta_at_angle(0), 0, 'theta at 0')
        self.assertEqual(ell.theta_at_angle(pi / 2), pi / 2, 'theta at 90')
        self.assertAlmostEqual(ell.theta_at_angle(pi), pi, msg='theta at 180')
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
