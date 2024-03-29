import unittest

from inkscape_helper.Effect import Effect
from inkscape_helper.EllipticArc import EllipticArc
from inkscape_helper.Coordinate import Coordinate

from math import pi

C00 = Coordinate(0, 0)
C20_0 = Coordinate(20, 0)
C0_10 = Coordinate(0, 10)
C10_0 = Coordinate(10, 0)
C20_10 = Coordinate(20, 10)

def between(mid, end1, end2):
    small = min(end1, end2)
    large = max(end1, end2)
    return small < mid < large

class TestEllipticArc(unittest.TestCase, Effect):
    def test_elliptic_arc_center(self):
        arc = EllipticArc(C20_0, C0_10, 20, 10, 0)
        self.assertTrue(arc.center.close_enough_to(C00), 'ellipse center')
        large_arc = EllipticArc(C20_0, C0_10, 20, 10, 0, large_arc = True)
        self.assertEqual(large_arc.center, C20_10, 'ellipse center large arc')
        neg_arc = EllipticArc(C20_0, C0_10, 20, 10, 0, pos_dir = False)
        self.assertEqual(neg_arc.center, C20_10, 'ellipse center neg dir')

    def test_t_to_theta(self):
        #arc = EllipticArc(C10_0, C0_10, 10, 10, 45) # quarter circle, axis rotated by 45 degree
        s = Coordinate (20, 0)
        s.t += pi / 4
        e = Coordinate(0, 10)
        e.t += pi / 4
        #arc = EllipticArc(C10_0, C0_10, 10, 10, 45) # quarter circle, axis rotated by 45 degree
        arc = EllipticArc(s, e, 20, 10, 45) # quarter circle, axis rotated by 45 degree
        self.assertEqual(arc.t_to_theta(0), 0)
        self.assertEqual(arc.t_to_theta(1), pi/2)
        self.assertEqual(arc.t_to_theta(0.5), pi/4)

    def test_theta_to_t_not_rot(self):
        arc = EllipticArc(C10_0, C0_10, 10, 10, 0) #quarter circle, not rotated
        self.assertEqual(arc.theta_to_t(pi/2), 1)
        self.assertEqual(arc.theta_to_t(pi/4), 0.5)

    def test_theta_to_t_rot(self):
        # NOTE: we're mixing degrees and radians here, not great
        arc = EllipticArc(C10_0, C0_10, 10, 10, -45) #quarter circle, rotated 45 degrees
        self.assertEqual(arc.theta_to_t(pi/2), 0.5)

    def test_elliptic_arc_length(self):
        arc = EllipticArc(C10_0, C0_10, 10, 10, 45)
        self.assertAlmostEqual(arc.length, 10 * pi / 2, 4)

    def test_pathpoint_at_t(self):
        arc = EllipticArc(C10_0, Coordinate(-10, 0), 10, 20, 0)
        self.assertTrue(arc.pathpoint_at_t(0.5).coord.close_enough_to(Coordinate(0, 20)), 'coordinate at 90')
        self.assertAlmostEqual(arc.tangent(0.5).t, pi/2)

    def test_elliptic_arc_subdivide(self):
        pass


    def test_real_world(self):
        rx, ry = 136.87567000000001, 46.467018000000003
        rot_deg = 11.8225
        c1 = Coordinate(400.32499000000001, 546.23693000000003)
        c2 = Coordinate(256.83267000000001, 563.67507999999998)
        c3 = Coordinate(132.38073, 490.15062999999998)
        c4 = Coordinate(275.87304, 472.71246000000002)

        center = Coordinate(300, 400)
        x = 200
        y = 100
        rot_deg = 3
        rot_rad = rot_deg * pi / 180
        right = Coordinate(x, 0)
        top = Coordinate(0, y)
        left = Coordinate(-x, 0)
        bottom = Coordinate(0, -y)
        right.t += rot_rad
        top.t += rot_rad
        left.t += rot_rad
        bottom.t += rot_rad

        self.rw_tests(right, top, left, bottom, x, y, rot_deg, True)
        self.rw_tests(right, bottom, left, top, x, y, rot_deg, False)

    def rw_tests(self, c1, c2, c3, c4, rx, ry, rot, pos_dir):
        e1 = EllipticArc(c1, c2, rx, ry, rot, pos_dir, False)
        e2 = EllipticArc(c2, c3, rx, ry, rot, pos_dir, False)
        e3 = EllipticArc(c3, c4, rx, ry, rot, pos_dir, False)
        e4 = EllipticArc(c4, c1, rx, ry, rot, pos_dir, False)

        # start & end points
        e1s = e1.pathpoint_at_t(0)
        e1e = e1.pathpoint_at_t(1)
        e2s = e2.pathpoint_at_t(0)
        e2e = e2.pathpoint_at_t(1)
        e3s = e3.pathpoint_at_t(0)
        e3e = e3.pathpoint_at_t(1)
        e4s = e4.pathpoint_at_t(0)
        e4e = e4.pathpoint_at_t(1)
        # coordinates
        self.assertTrue(c1.close_enough_to(e1s.coord), 'start e1')
        self.assertTrue(c2.close_enough_to(e1e.coord), 'end e1')
        self.assertTrue(c2.close_enough_to(e2s.coord), 'start e2')
        self.assertTrue(c3.close_enough_to(e2e.coord), 'end e2')
        self.assertTrue(c3.close_enough_to(e3s.coord), 'start e3')
        self.assertTrue(c4.close_enough_to(e3e.coord), 'end e3')
        self.assertTrue(c4.close_enough_to(e4s.coord), 'start e4')
        self.assertTrue(c1.close_enough_to(e4e.coord), 'end e4')

        #centers
        center = (c1 + c2 + c3 + c4) / 4
        self.assertTrue(center.close_enough_to(e1.center), 'center e1')
        self.assertTrue(center.close_enough_to(e2.center), 'center e2')
        self.assertTrue(center.close_enough_to(e3.center), 'center e3')
        self.assertTrue(center.close_enough_to(e4.center), 'center e4')

        #angles
        angle = 0
        increase = (pi / 2) if pos_dir else (-pi / 2)
        self.assertEqual(e1.start_theta, angle, 'e1 start theta')
        angle = (angle + increase) % (2 * pi)
        self.assertEqual(e1.end_theta, angle, 'e1 end theta')
        self.assertEqual(e2.start_theta, angle, 'e2 start theta')
        angle = (angle + increase) % (2 * pi)
        self.assertAlmostEqual(e2.end_theta, angle)
        self.assertAlmostEqual(e3.start_theta, angle)
        angle = (angle + increase) % (2 * pi)
        self.assertEqual(e3.end_theta, angle, 'e3 end theta')
        self.assertEqual(e4.start_theta, angle, 'e4 start theta')
        angle = (angle + increase) % (2 * pi)
        self.assertEqual(e4.end_theta, angle, 'e4 end theta')

        #halfway points
        he1 = e1.pathpoint_at_t(0.5).coord
        hl1 = (c1 + c2) / 2
        self.assertTrue(between(he1.x, c1.x, hl1.x))
        self.assertTrue(between(he1.y, c2.y, hl1.y))
        he2 = e2.pathpoint_at_t(0.5).coord
        hl2 = (c2 + c3) / 2
        self.assertTrue(between(he2.x, c3.x, hl2.x))
        self.assertTrue(between(he2.y, c2.y, hl2.y))
        he3 = e3.pathpoint_at_t(0.5).coord
        hl3 = (c3 + c4) / 2
        self.assertTrue(between(he3.x, c3.x, hl3.x))
        self.assertTrue(between(he3.y, c4.y, hl3.y))
        he4 = e4.pathpoint_at_t(0.5).coord
        hl4 = (c4 + c1) / 2
        self.assertTrue(between(he4.x, c1.x, hl4.x))
        self.assertTrue(between(he4.y, c4.y, hl4.y))

        #tangents
        self.assertEqual(e1e.tangent, e2s.tangent, 'tangents e1 e2')
        self.assertEqual(e2e.tangent, e3s.tangent, 'tangents e2 e3')
        self.assertEqual(e3e.tangent, e4s.tangent, 'tangents e3 e4')
        self.assertTrue(e4e.tangent.close_enough_to(e1s.tangent), 'tangents e4 e1')

if __name__ == '__main__':
    unittest.main()