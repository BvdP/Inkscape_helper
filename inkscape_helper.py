#!/usr/bin/env python
from __future__ import division
import inkex
import simplestyle


from math import *
from collections import namedtuple


#Note: keep in mind that SVG coordinates start in the top-left corner i.e. with an inverted y-axis

errormsg = inkex.errormsg
debug = inkex.debug

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

def draw_rectangle(parent, w, h, x, y, rx=0, ry=0, style=default_style):
    attribs = {
        'style': style,
        'height': str(h),
        'width': str(w),
        'x': str(x),
        'y': str(y)
    }
    if rx != 0 and ry != 0:
        attribs['rx'] = str(rx)
        attribs['ry'] = str(ry)
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

    if on_segments and not (on_segment(I, s1, e1) and on_segment(I, s2, e2)):
        raise IntersectionError("Intersection {0} is not on line segments [{1} -> {2}] [{3} -> {4}]".format(I, s1, e1, s2, e2))
    return I


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
        return hypot(self.x, self.y)

    #@r.setter
    #def r(self, value):

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

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

    def __truediv__(self, quotient):
        return self.__div__(quotient)



class Effect(inkex.Effect):
    """

    """
    def __init__(self, options=None):
        inkex.Effect.__init__(self)
        self.knownUnits = ['in', 'pt', 'px', 'mm', 'cm', 'm', 'km', 'pc', 'yd', 'ft']

        if options != None:
            for opt in options:
                if len(opt) == 2:
                    self.OptionParser.add_option('--' + opt[0], type = opt[1], dest = opt[0])
                else:
                    self.OptionParser.add_option('--' + opt[0], type = opt[1], dest = opt[0],default = opt[2], help = opt[3])

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

    def arc_to(self, rx, ry, x, y, rotation=0, pos_sweep=True, large_arc=False, absolute=False):
        self.nodes.append("{0} {1} {2} {3} {4} {5} {6} {7}".format(_format_1st('a', absolute), rx, ry, rotation, 1 if large_arc else 0, 1 if pos_sweep else 0, x, y))

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


PathPoint = namedtuple('PathPoint', 't coord tangent curvature c_dist')

class PathSegment():

    def __init__(self):
        raise NotImplementedError

    @property
    def lenth(self):
        raise NotImplementedError

    def subdivide(self, part_length):
        raise NotImplementedError
    # also need:

    #   find a way do do curvature dependent spacing
    #       - based on deviation from a standard radius?
    #       - or ratio between thickness and curvature?
    #def point_at_distance(d):
    #    pass


class Line(PathSegment):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def length(self):
        return (self.end - self.start).r

    def subdivide(self, part_length, start_offset=0): # note: start_offset should be smaller than part_length
        nr_parts = int((self.length - start_offset) // part_length)
        k_o = start_offset / self.length
        k2t = lambda k : k_o + k * part_length / self.length
        pp = lambda t : PathPoint(t, self.start + t * (self.end - self.start), self.end - self.start, 0, t * self.length)
        points = [pp(k2t(k)) for k in range(nr_parts + 1)]
        return(points, self.length - points[-1].c_dist)



class BezierCurve(PathSegment):
    nr_points = 10
    def __init__(self, P): # number of points is limited to 3 or 4

        if len(P) == 3: # quadratic
            self.B = lambda t : (1 - t)**2 * P[0] + 2 * (1 - t) * t * P[1] + t**2 * P[2]
            Bd = lambda t : 2 * (1 - t) * (P[1] - P[0]) + 2 * t * (P[2] - P[1])
            Bdd = lambda t : 2 * (P[2] - 2 * P[1] + P[0])
        elif len(P) == 4: #cubic
            self.B = lambda t : (1 - t)**3 * P[0] + 3 * (1 - t)**2 * t * P[1] + 3 * (1 - t) * t**2 * P[2] + t**3 * P[3]
            Bd = lambda t : 3 * (1 - t)**2 * (P[1] - P[0]) + 6 * (1 - t) * t * (P[2] - P[1]) + 3 * t**2 * (P[3] - P[2])
            Bdd = lambda t : 6 * (1 - t) * (P[2] - 2 * P[1] + P[0]) + 6 * t * (P[3] - 2 * P[2] + P[1])

        self.tangent = lambda t : Bd(t)
        self.curvature = lambda t : (Bd(t).x * Bdd(t).y - Bd(t).y * Bdd(t).x) / hypot(Bd(t).x, Bd(t).y)**3

        self.distances = [0]    # cumulative distances for each 't'
        prev_pt = self.B(0)
        for i in range(self.nr_points):
            t = (i + 1) / self.nr_points
            pt = self.B(t)
            self.distances.append(self.distances[-1] + hypot(prev_pt.x - pt.x, prev_pt.y - pt.y))
            prev_pt = pt
        self.length = self.distances[-1]

    @classmethod
    def quadratic(cls, start, c, end):
        bezier = cls()

    @classmethod
    def cubic(cls, start, c1, c2, end):
        bezier = cls()

    def __make_eq__(self):
        pass

    @property
    def length(self):
        return self.length

    def subdivide(self, part_length, start_offset=0):
        nr_parts = int((self.length - start_offset) / part_length + 10E-10)
        print "NR PARTS:", nr_parts, self.length, start_offset, part_length, int(self.length / part_length), self.length - 2 * part_length
        k_o = start_offset / self.length
        k2t = lambda k : k_o + k * part_length / self.length
        points = [self.pathpoint_at_t(k2t(k)) for k in range(nr_parts + 1)]
        return(points, self.length - points[-1].c_dist)


    def pathpoint_at_t(self, t):
        """pathpoint on the curve from t=0 to point at t."""
        step = 1 / self.nr_points
        pt_idx = int(t / step)
        #print "index", pt_idx, self.distances[pt_idx]
        length = self.distances[pt_idx]
        ip_fact = (t - pt_idx * step) / step

        if ip_fact > 0 and t < 1: # not a perfect match, need to interpolate
            length += ip_fact * (self.distances[pt_idx + 1] - self.distances[pt_idx])

        return PathPoint(t, self.B(t), self.tangent(t), self.curvature(t), length)


    def t_at_length(self, length):
        """interpolated t where the curve is at the given length"""
        if length == self.length:
            return 1
        i_small = 0
        i_big = self.nr_points + 1

        while i_big - i_small > 1:  # binary search
            i_half = i_small + (i_big - i_small) // 2
            if self.distances[i_half] <= length:
                i_small = i_half
            else:
                i_big = i_half

        small_dist = self.distances[i_small]
        return  i_small / self.nr_points + (length - small_dist) * (self.distances[i_big] - small_dist) # interpolated length

class Ellipse():
    nrPoints = 1000 #used for piecewise linear circumference calculation (ellipse circumference is tricky to calculate)
    # approximate circumfere: c = pi * (3 * (a + b) - sqrt(10 * a * b + 3 * (a ** 2 + b ** 2)))

    def __init__(self, w, h):
        self.h = h
        self.w = w
        EllipsePoint = namedtuple('EllipsePoint', 'angle coord cDist')
        self.ellData = [EllipsePoint(0, Coordinate(w/2, 0), 0)] # (angle, x, y, cumulative distance from angle = 0)
        angle = 0
        self.angleStep = 2 * pi / self.nrPoints
        #note: the render angle (ra) corresponds to the angle from the ellipse center (ca) according to:
        # ca = atan(w/h * tan(ra))
        for i in range(self.nrPoints):
            angle += self.angleStep
            prev = self.ellData[-1]
            x, y = w / 2 * cos(angle), h / 2 * sin(angle)
            self.ellData.append(EllipsePoint(angle, Coordinate(x, y), prev.cDist + hypot(prev.coord.x - x, prev.coord.y - y)))
        self.circumference = self.ellData[-1].cDist
        #inkex.debug("circ: %d" % self.circumference)

    def rAngle(self, a):
        """Convert an angle measured from ellipse center to the angle used to generate ellData (used for lookups)"""
        cf = 0
        if a > pi / 2:
            cf = pi
        if a > 3 * pi / 2:
            cf = 2 * pi
        return atan(self.w / self.h * tan(a)) + cf

    def coordinateFromAngle(self, angle):
        """Coordinate of the point at angle."""
        return Coordinate(self.w / 2 * cos(angle), self.h / 2 * sin(angle))

    def notchCoordinate(self, angle, notchHeight):
        """Coordinate for a notch at the given angle. The notch is perpendicular to the ellipse."""
        angle %= (2 * pi)
        #some special cases to avoid divide by zero:
        if angle == 0:
            return (0, Coordinate(self.w / 2 + notchHeight, 0))
        elif angle == pi:
            return (pi, Coordinate(-self.w / 2 - notchHeight, 0))
        elif angle == pi / 2:
            return(pi / 2, doc.Coordinate(0, self.h / 2 + notchHeight))
        elif angle == 3 * pi / 2:
            return(3 * pi / 2, Coordinate(0, -self.h / 2 - notchHeight))

        x = self.w / 2 * cos(angle)
        derivative = self.h / self.w * -x / sqrt((self.w / 2) ** 2 - x ** 2)
        if angle > pi:
            derivative = -derivative

        normal = -1 / derivative
        nAngle = atan(normal)
        if angle > pi / 2 and angle < 3 * pi / 2:
            nAngle += pi

        nCoordinate = self.coordinateFromAngle(angle) + Coordinate(cos(nAngle), sin(nAngle)) * notchHeight
        return nCoordinate


    def distFromAngles(self, a1, a2):
        """Distance accross the surface from point at angle a2 to point at angle a2. Measured in CCW sense."""
        i1 = int(self.rAngle(a1) / self.angleStep)
        p1 = self.rAngle(a1) % self.angleStep
        l1 = self.ellData[i1 + 1].cDist - self.ellData[i1].cDist
        i2 = int(self.rAngle(a2) / self.angleStep)
        p2 = self.rAngle(a2) % self.angleStep
        l2 = self.ellData[i2 + 1].cDist - self.ellData[i2].cDist
        if a1 <= a2:
            len = self.ellData[i2].cDist - self.ellData[i1].cDist + l2 * p2 - l1 * p1
        else:
            len = self.circumference + self.ellData[i2].cDist - self.ellData[i1].cDist
        return len

    def angleFromDist(self, startAngle, relDist):
        """Returns the angle that you get when starting at startAngle and moving a distance (dist) in CCW direction"""
        si = int(self.rAngle(startAngle) / self.angleStep)
        p = self.rAngle(startAngle) % self.angleStep

        l = self.ellData[si + 1].cDist - self.ellData[si].cDist

        startDist = self.ellData[si].cDist + p * l

        absDist = relDist + startDist

        if absDist > self.ellData[-1].cDist:  # wrap around zero angle
            absDist -= self.ellData[-1].cDist

        iMin = 0
        iMax = self.nrPoints
        count = 0
        while iMax - iMin > 1:  # binary search
            count += 1
            iHalf = iMin + (iMax - iMin) // 2
            if self.ellData[iHalf].cDist < absDist:
                iMin = iHalf
            else:
                iMax = iHalf

        stepDist = self.ellData[iMax].cDist - self.ellData[iMin].cDist
        return self.ellData[iMin].angle + self.angleStep * (absDist - self.ellData[iMin].cDist)/stepDist
