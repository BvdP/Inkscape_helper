import unittest

import inkex
from inkscape_helper.Effect import Effect
from inkscape_helper.SVG_Path import SVG_Path
from inkscape_helper.Coordinate import Coordinate

C00 = Coordinate(0, 0)
C10 = Coordinate(1, 0)
C01 = Coordinate(0, 1)
C11 = Coordinate(1, 1)

class TestPath(unittest.TestCase, SVG_Path):

    def setUp(self):
        self.eff = inkex.Effect()
        self.eff.affect(['empty.svg'])

    def test_line(self):
        p = SVG_Path()
        parent = self.eff.document.getroot()
        p.move_to(C00, True)
        p.line_to(C11)
        p.path(parent)

        self.assertEqual(p.nodes, ['M {0} {1}'.format(0.0, 0.0), 'l {0} {1}'.format(1.0, 1.0)])
