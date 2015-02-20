#!/usr/bin/env python

import inkex
import simplestyle
import unittest

from math import *

#Note: keep in mind that SVG coordinates start in the top-left corner i.e. with an inverted y-axis


default_style = simplestyle.formatStyle(
    {'stroke': '#000000',
    'stroke-width': '1',
    'fill': 'none'
    })

groove_style = simplestyle.formatStyle(
    {'stroke': '#0000FF',
    'stroke-width': '1',
    'fill': 'none'
    })

def draw_SVG_square(parent, w, h, x, y, style=default_style):
    attribs = {
        'style': style,
        'height': str(h),
        'width': str(w),
        'x': str(x),
        'y': str(y)
    }
    inkex.etree.SubElement(parent, inkex.addNS('rect', 'svg'), attribs)

def draw_SVG_ellipse(parent, rx, ry, center, start_end=(0, 2*pi), style=default_style, transform=''):
    ell_attribs = {'style': style,
        inkex.addNS('cx', 'sodipodi'): str(center.x),
        inkex.addNS('cy', 'sodipodi'): str(center.y),
        inkex.addNS('rx', 'sodipodi'): str(rx),
        inkex.addNS('ry', 'sodipodi'): str(ry),
        inkex.addNS('start', 'sodipodi'): str(start_end[0]),
        inkex.addNS('end', 'sodipodi'): str(start_end[1]),
        inkex.addNS('open', 'sodipodi'): 'true',  #all ellipse sectors we will draw are open
        inkex.addNS('type', 'sodipodi'): 'arc',
        'transform': transform
    }
    inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), ell_attribs)


def draw_SVG_arc(parent, rx, ry, x_axis_rot, style=default_style):
    arc_attribs = {'style': style,
        'rx': str(rx),
        'ry': str(ry),
        'x-axis-rotation': str(x_axis_rot),
        'large-arc': '',
        'sweep': '',
        'x': '',
        'y': ''
        }
        #name='part'
    style = {'stroke': '#000000', 'fill': 'none'}
    drw = {'style':simplestyle.formatStyle(style),inkex.addNS('label','inkscape'):name,'d':XYstring}
    inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), drw)
    inkex.addNS('', 'svg')

def draw_SVG_text(parent, coordinate, txt, style=default_style):
    text = inkex.etree.Element(inkex.addNS('text', 'svg'))
    text.text = txt
    text.set('x', str(coordinate.x))
    text.set('y', str(coordinate.y))
    style = {'text-align': 'center', 'text-anchor': 'middle'}
    text.set('style', simplestyle.formatStyle(style))
    parent.append(text)

#draw an SVG line segment between the given (raw) points
def draw_SVG_line(parent, start, end, style = default_style):
    line_attribs = {'style': style,
                    'd': 'M '+str(start.x)+','+str(start.y)+' L '+str(end.x)+','+str(end.y)}

    inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), line_attribs)


def SVG_move_to(x, y):
    return "M %d %d" % (x, y)

def SVG_line_to(x, y):
    return "L %d %d" % (x, y)

def SVG_arc_to(rx, ry, x, y):
    la = sw = 0
    return "A %d %d 0 %d %d" % (rx, ry, la, sw, x, y)

def SVG_path(components):
    return '<path d="' + ' '.join(components) + '">'

def SVG_curve(parent, segments, style, closed=True):
    #pathStr = 'M '+ segments[0]
    pathStr = ' '.join(segments)
    if closed:
        pathStr += ' z'
    attributes = {
      'style': style,
      'd': pathStr}
    inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attributes)

class IntersectionError(ValueError):
        """Raised when two lines do not intersect."""

def on_segment(pt, start, end):
    """Check if pt is between start and end. The three points are presumed to be collinear."""
    pt -= start
    end -= start
    ex, ey = end.x, end.y
    px, py = pt.x, pt.y
    px *= cmp(ex, 0)
    py *= cmp(ey, 0)
    return px >= 0 and px <= abs(ex) and py >= 0 and py <= abs(ey)

def intersection (s1, e1, s2, e2, on_segments = True):
    D = (s1.x - e1.x) * (s2.y - e2.y) - (s1.y - e1.y) * (s2.x - e2.x)
    if D == 0:
        raise IntersectionError("Lines from {s1} to {e1} and {s2} to {e2} are parallel")
    N1 = s1.x * e1.y - s1.y * e1.x
    N2 = s2.x * e2.y - s2.y * e2.x
    I = ((s2 - e2) * N1 - (s1 - e1) * N2) / D
 
    if not (on_segment(I, s1, e1) and on_segment(I, s2, e2)):
        if on_segments:
            raise IntersectionError("Intersection {} is not on line segments [{} -> {}] [{} -> {}]".format(I, s1, e1, s2, e2))
    return I
    
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

def inner_product(a, b):
    return a.x * b.x + a.y * b.y
        
class Coordinate:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    @property
    def t(self):
        return atan2(self.y, self.x)
    
    #@t.setter
    #def t(self, value):
    
    @property
    def r(self):
        return sqrt(self.x ** 2 + self.y ** 2)
    
    #@r.setter
    #def r(self, value):
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

    def __mul__(self, factor):
        return Coordinate(self.x * factor, self.y * factor)

    def __rmul__(self, other):
        return self * other

    def __div__(self, quotient):
        return Coordinate(self.x / quotient, self.y / quotient)

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

class Helper(inkex.Effect):
    """

    """
    def __init__(self, options):
        inkex.Effect.__init__(self)
        self.knownUnits = ['in', 'pt', 'px', 'mm', 'cm', 'm', 'km', 'pc', 'yd', 'ft']

        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'cm',
          help = 'Unit, should be one of ')

        self.OptionParser.add_option('--tool_diameter', action = 'store',
          type = 'float', dest = 'tool_diameter', default = '0.3',
          help = 'Tool diameter')

        self.OptionParser.add_option('--tolerance', action = 'store',
          type = 'float', dest = 'tolerance', default = '0.05',
          help = '')

        self.OptionParser.add_option('--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '1.2',
          help = 'Material thickness')

        self.OptionParser.add_option('--width', action = 'store',
          type = 'float', dest = 'width', default = '3.0',
          help = 'Box width')

        self.OptionParser.add_option('--height', action = 'store',
          type = 'float', dest = 'height', default = '10.0',
          help = 'Box height')

        self.OptionParser.add_option('--depth', action = 'store',
          type = 'float', dest = 'depth', default = '3.0',
          help = 'Box depth')

        self.OptionParser.add_option('--shelves', action = 'store',
          type = 'string', dest = 'shelve_list', default = '',
          help = 'semicolon separated list of shelve heigths')

        self.OptionParser.add_option('--groove_depth', action = 'store',
          type = 'float', dest = 'groove_depth', default = '0.5',
          help = 'Groove depth')

        self.OptionParser.add_option('--tab_size', action = 'store',
          type = 'float', dest = 'tab_size', default = '10',
          help = 'Approximate tab width (tabs will be evenly spaced along the length of the edge)')

    try:
        inkex.Effect.unittouu   # unitouu has moved since Inkscape 0.91
    except AttributeError:
        try:
            def unittouu(self, unit):
                return inkex.unittouu(unit)
        except AttributeError:
            pass

    def effect(self):
        """
        Draws a shelved cupboard, based on provided parameters
        """

        # input sanity check and unit conversion
        error = False

        if self.options.unit not in self.knownUnits:
            inkex.errormsg('Error: unknown unit. '+ self.options.unit)
            error = True
        unit = self.options.unit

        if min(self.options.height, self.options.width, self.options.depth) == 0:
            inkex.errormsg('Error: Dimensions must be non zero')
            error = True

        shelves = []

        for s in self.options.shelve_list.split(';'):
            try:
                shelves.append(self.unittouu(str(s).strip() + unit))
            except ValueError:
                inkex.errormsg('Error: nonnumeric value in shelves (' + s + ')')
                error = True

        if error:
            exit()

        height = self.unittouu(str(self.options.height) + unit)
        width = self.unittouu(str(self.options.width) + unit)
        depth = self.unittouu(str(self.options.depth) + unit)
        thickness = self.unittouu(str(self.options.thickness) + unit)
        groove_depth = self.unittouu(str(self.options.groove_depth) + unit)
        tab_size = self.unittouu(str(self.options.tab_size) + unit)
        tolerance = self.unittouu(str(self.options.tolerance) + unit)
        tool_diameter = self.unittouu(str(self.options.tool_diameter) + unit)

        svg = self.document.getroot()
        docWidth = self.unittouu(svg.get('width'))
        docHeigh = self.unittouu(svg.attrib['height'])

        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Shelves')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')


        def H(x):
            return Coordinate(x, 0)

        def V(x):
            return Coordinate(0, x)

        def tab_count(dist, desired_tab_size):
            F = int(dist // desired_tab_size)
            if F / 2 % 2 == 0:  # make sure we have an odd number of tabs
                n = F // 2
            else:
                n = (F - 1) // 2

            return 2 * n + 1

if __name__ == '__main__':
    coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
    intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
    suite = unittest.TestSuite([coordinate_t, intersection_t])
    unittest.TextTestRunner(verbosity=2).run(suite)    
#    unittest.main()
