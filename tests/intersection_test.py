import unittest
from inkscape_helper.Coordinate import *

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


