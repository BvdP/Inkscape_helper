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

mark_style = simplestyle.formatStyle(
    {'stroke': '#00FF00',
    'stroke-width': '1',
    'fill': 'none'
    })

def draw_square(parent, w, h, x, y, style=default_style):
    attribs = {
        'style': style,
        'height': str(h),
        'width': str(w),
        'x': str(x),
        'y': str(y)
    }
    inkex.etree.SubElement(parent, inkex.addNS('rect', 'svg'), attribs)

def draw_ellipse(parent, rx, ry, center, start_end=(0, 2*pi), style=default_style, transform=''):
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


def draw_arc(parent, rx, ry, x_axis_rot, style=default_style):
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

def draw_text(parent, coordinate, txt, style=default_style):
    text = inkex.etree.Element(inkex.addNS('text', 'svg'))
    text.text = txt
    text.set('x', str(coordinate.x))
    text.set('y', str(coordinate.y))
    style = {'text-align': 'center', 'text-anchor': 'middle'}
    text.set('style', simplestyle.formatStyle(style))
    parent.append(text)

#draw an SVG line segment between the given (raw) points
def draw_line(parent, start, end, style = default_style):
    line_attribs = {'style': style,
                    'd': 'M '+str(start.x)+','+str(start.y)+' L '+str(end.x)+','+str(end.y)}

    inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), line_attribs)


def layer(parent, layer_name):
    layer = inkex.etree.SubElement(parent, 'g')
    layer.set(inkex.addNS('label', 'inkscape'), layer_name)
    layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
    return layer

def group(parent):
    return inkex.etree.SubElement(parent, 'g')


class IntersectionError(ValueError):
        """Raised when two lines do not intersect."""

def _on_segment(pt, start, end):
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

    if on_segments and not (_on_segment(I, s1, e1) and _on_segment(I, s2, e2)):
        raise IntersectionError("Intersection {0} is not on line segments [{1} -> {2}] [{3} -> {4}]".format(I, s1, e1, s2, e2))
    return I

class TestIntersection(unittest.TestCase):
    def setUp(self):
        self.C00 = Coordinate(0, 0)
        self.C10 = Coordinate(1, 0)
        self.C01 = Coordinate(0, 1)
        self.C11 = Coordinate(1, 1)

    def test_on_segment(self):
        self.assertTrue(_on_segment(self.C11, self.C00, self.C11), 'Endpoint on segment')
        self.assertTrue(_on_segment(self.C00, self.C00, self.C11), 'Start point on segment')
        self.assertTrue(_on_segment(self.C11 / 2, self.C00, self.C11), 'Midpoint on segment')
        self.assertFalse(_on_segment(self.C11 * 2, self.C00, self.C11), 'Beyond endpoint')
        self.assertFalse(_on_segment(self.C11 * -1, self.C00, self.C11), 'Before start point')


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


class Effect(inkex.Effect):
    """

    """
    def __init__(self):
        inkex.Effect.__init__(self)
        self.knownUnits = ['in', 'pt', 'px', 'mm', 'cm', 'm', 'km', 'pc', 'yd', 'ft']

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

        """
        pass


def _format_1st(command, is_absolute):
    return command.upper() if is_absolute else command.lower()

class Path:
    def __init__(self):
        self.nodes = []

    def move_to(self, coord, absolute=False):
        self.nodes.append("{0} {1} {2}".format(_format_1st('m', absolute), coord.x, coord.y))

    def line_to(self, coord, absolute=False):
        self.nodes.append("{0} {1} {2}".format(_format_1st('l', absolute), coord.x, coord.y))

    def h_line_to(self, dist, absolute=False):
        self.nodes.append("{0} {1}".format(_format_1st('h', absolute), dist))

    def v_line_to(self, dist, absolute=False):
        self.nodes.append("{0} {1}".format(_format_1st('v', absolute), dist))

    def arc_to(self, rx, ry, x, y):
        la = sw = 0
        return "A %d %d 0 %d %d" % (rx, ry, la, sw, x, y)

    def close(self):
        self.nodes.append('z')

    def path(self, parent, style):
        attribs = {'style': style,
                    'd': ' '.join(self.nodes)}
        inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attribs)

    def curve(parent, segments, style, closed=True):
        #pathStr = 'M '+ segments[0]
        pathStr = ' '.join(segments)
        if closed:
            pathStr += ' z'
        attributes = {
          'style': style,
          'd': pathStr}
        inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attributes)

    def remove_last(self):
        self.nodes.pop()

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
        self.C00 = Coordinate(0, 0)
        self.C10 = Coordinate(1, 0)
        self.C01 = Coordinate(0, 1)
        self.C11 = Coordinate(1, 1)

    def test_line(self):
        p = Path()
        parent = self.document.getroot()
        p.move_to(self.C00, True)
        p.line_to(self.C11)
        p.path(parent, default_style)
        p_str = inkex.etree.tostring(self.document)
        #print(p_str, p.nodes)
        self.assertEqual(p.nodes, ['M {0} {1}'.format(0.0, 0.0), 'l {0} {1}'.format(1.0, 1.0)])


if __name__ == '__main__':
    coordinate_t = unittest.TestLoader().loadTestsFromTestCase(TestCoordinate)
    intersection_t = unittest.TestLoader().loadTestsFromTestCase(TestIntersection)
    path_t = unittest.TestLoader().loadTestsFromTestCase(TestPath)

    suite = unittest.TestSuite([coordinate_t, intersection_t, path_t])
    unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()
