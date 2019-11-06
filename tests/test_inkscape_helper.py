from __future__ import division
import sys
sys.path.append("C:\\Program Files\\Inkscape\\share\\extensions")
sys.path.append("/usr/share/inkscape/extensions")
import unittest
from inkscape_helper.inkscape_helper import *
from inkscape_helper.Coordinate import Coordinate
from inkscape_helper.Effect import Effect

C00 = Coordinate(0, 0)
C10 = Coordinate(1, 0)
C01 = Coordinate(0, 1)
C11 = Coordinate(1, 1)


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


C20_0 = Coordinate(20, 0)
C0_10 = Coordinate(0, 10)
C10_0 = Coordinate(10, 0)
C20_10 = Coordinate(20, 10)



def pretty_close(a ,b, tolerance=1E-4):
    return abs(a - b) < tolerance  #TODO: current ellipse and bezier interpolation is always on the short side


#coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
#intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
#ellipse_t = unittest.TestLoader().loadTestsFromTestCase(TestEllipse)
#path_t = unittest.TestLoader().loadTestsFromTestCase(TestPath)
#ell_arc_t = unittest.TestLoader().loadTestsFromTestCase(TestEllipticArc)
#segment_t = unittest.TestLoader().loadTestsFromTestCase(TestPathSegment)
#matrix_t = unittest.TestLoader().loadTestsFromTestCase(TestMatrix)


#suite = unittest.TestSuite([path_t, segment_t, ell_arc_t])
#unittest.TextTestRunner(verbosity=2).run(suite)
unittest.main()
