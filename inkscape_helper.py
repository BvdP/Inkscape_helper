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
    """
    Basic (x, y) coordinate class (or should it be called vector?) which allows some simple operations.
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    #polar coordinates
    @property
    def t(self):
        return atan2(self.y, self.x)

    @t.setter
    def t(self, value):
        length = self.r
        self.x = cos(value) * length
        self.y = sit(value) * length


    @property
    def r(self):
        return hypot(self.x, self.y)

    @r.setter
    def r(self, value):
        angle = self.t
        self.x = cos(angle) * value
        self.y = sit(angle) * value

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

    def dot(self, other):
        """dot product"""
        return self.x * other.x + self.y * other.y

    def cross_norm(self, other):
        """"the norm of the cross product"""
        self.x * other.y - self.y * other.x


    def close_enough_to(self, other, limit=1E-9):
        return (self - other).r < limit


class Effect(inkex.Effect):
    """
    Provides some extra features to inkex.Effect:
    - Allows you to pass a list of options in stead of setting them one by one
    - acces to unittouu() that is compatible between Inkscape versions 0.48 and 0.91
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
    """
    Generates SVG paths
    """
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

    def pathpoint_at_t(self, t):
        raise NotImplementedError

    def t_at_length(self, length):
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
        self.pp = lambda t : PathPoint(t, self.start + t * (self.end - self.start), self.end - self.start, 0, t * self.length)

    @property
    def length(self):
        return (self.end - self.start).r

    def subdivide(self, part_length, start_offset=0): # note: start_offset should be smaller than part_length
        nr_parts = int((self.length - start_offset) // part_length)
        k_o = start_offset / self.length
        k2t = lambda k : k_o + k * part_length / self.length
        points = [self.pp(k2t(k)) for k in range(nr_parts + 1)]
        return(points, self.length - points[-1].c_dist)

    def pathpoint_at_t(self, t):
        return self.pp(t)

    def t_at_length(self, length):
        return length / self.length()


class BezierCurve(PathSegment):
    nr_points = 10
    def __init__(self, P): # number of points is limited to 3 or 4

        if len(P) == 3: # quadratic
            self.B = lambda t : (1 - t)**2 * P[0] + 2 * (1 - t) * t * P[1] + t**2 * P[2]
            self.Bd = lambda t : 2 * (1 - t) * (P[1] - P[0]) + 2 * t * (P[2] - P[1])
            self.Bdd = lambda t : 2 * (P[2] - 2 * P[1] + P[0])
        elif len(P) == 4: #cubic
            self.B = lambda t : (1 - t)**3 * P[0] + 3 * (1 - t)**2 * t * P[1] + 3 * (1 - t) * t**2 * P[2] + t**3 * P[3]
            self.Bd = lambda t : 3 * (1 - t)**2 * (P[1] - P[0]) + 6 * (1 - t) * t * (P[2] - P[1]) + 3 * t**2 * (P[3] - P[2])
            self.Bdd = lambda t : 6 * (1 - t) * (P[2] - 2 * P[1] + P[0]) + 6 * t * (P[3] - 2 * P[2] + P[1])

        self.tangent = lambda t : self.Bd(t)
 #       self.curvature = lambda t : (Bd(t).x * Bdd(t).y - Bd(t).y * Bdd(t).x) / hypot(Bd(t).x, Bd(t).y)**3


        self.distances = [0]    # cumulative distances for each 't'
        prev_pt = self.B(0)
        for i in range(self.nr_points):
            t = (i + 1) / self.nr_points
            pt = self.B(t)
            self.distances.append(self.distances[-1] + hypot(prev_pt.x - pt.x, prev_pt.y - pt.y))
            prev_pt = pt
        self.length = self.distances[-1]

    def curvature(self, t):
        n = self.Bd(t).x * self.Bdd(t).y - self.Bd(t).y * self.Bdd(t).x
        d = hypot(self.Bd(t).x, self.Bd(t).y)**3
        if d == 0:
            return n * float('inf')
        else:
            return n / d

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
        nr_parts = int((self.length - start_offset) // part_length)
        k_o = start_offset / self.length
        k2t = lambda k : k_o + k * part_length / self.length
        points = [self.pathpoint_at_t(k2t(k)) for k in range(nr_parts + 1)]
        return(points, self.length - points[-1].c_dist)


    def pathpoint_at_t(self, t):
        """pathpoint on the curve from t=0 to point at t."""
        step = 1 / self.nr_points
        pt_idx = int(t / step)
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
    """Used as a base class for EllipticArc."""
    nr_points = 1024 #used for piecewise linear circumference calculation (ellipse circumference is tricky to calculate)
    # approximate circumfere: c = pi * (3 * (a + b) - sqrt(10 * a * b + 3 * (a ** 2 + b ** 2)))

    def __init__(self, x_radius, y_radius):
        self.y_radius = y_radius
        self.x_radius = x_radius
        self.distances = [0]
        theta = 0
        self.angle_step = 2 * pi / self.nr_points

        for i in range(self.nr_points):
            prev_dist = self.distances[-1]
            prev_coord = self.coordinate_at_theta(theta)
            theta += self.angle_step
            x, y = x_radius * cos(theta), y_radius * sin(theta)
            self.distances.append(prev_dist + hypot(prev_coord.x - x, prev_coord.y - y))

    @property
    def circumference(self):
        return self.distances[-1]

    def curvature(self, theta):
        c = self.coordinate_at_theta(theta)
        return (self.x_radius*self.y_radius)/((cos(theta)**2*self.y_radius**2 + sin(theta)**2*self.x_radius**2)**(3/2))

    def tangent(self, theta):
        angle = self.theta_at_angle(theta)
        return Coordinate(cos(angle), sin(angle))

    def coordinate_at_theta(self, theta):
        """Coordinate of the point at theta."""
        return Coordinate(self.x_radius * cos(theta), self.y_radius * sin(theta))

    def dist_from_theta(self, theta_start, theta_end):
        """Distance accross the surface from point at angle theta_end to point at angle theta_end. Measured in positive(CCW) sense."""
        i1 = int(theta_start / self.angle_step)
        p1 = theta_start % self.angle_step
        l1 = self.distances[i1 + 1] - self.distances[i1]
        i2 = int(theta_end / self.angle_step)
        p2 = theta_end % self.angle_step
        l2 = self.distances[i2 + 1] - self.distances[i2]
        if theta_start <= theta_end:
            len = self.distances[i2] - self.distances[i1] + l2 * p2 - l1 * p1
        else:
            len = self.circumference + self.distances[i2] - self.distances[i1]
        return len

    def theta_from_dist(self, theta_start, dist):
        """Returns the angle that you get when starting at theta_start and moving a distance (dist) in CCW direction"""
        si = int(theta_start / self.angle_step)
        p = theta_start % self.angle_step

        piece_length = self.distances[si + 1] - self.distances[si]
        start_dist = self.distances[si] + p * piece_length
        end_dist = dist + start_dist

        if end_dist > self.circumference:  # wrap around zero angle
            end_dist -= self.circumference

        min_idx = 0
        max_idx = self.nr_points
        while max_idx - min_idx > 1:  # binary search
            half_idx = min_idx + (max_idx - min_idx) // 2
            if self.distances[half_idx] < end_dist:
                min_idx = half_idx
            else:
                max_idx = half_idx
        step_dist = self.distances[max_idx] - self.distances[min_idx]
        return (min_idx + (end_dist - self.distances[min_idx]) / step_dist) * self.angle_step

    def theta_at_angle(self, angle):
        cf = 0
        if angle > pi / 2:
            cf = pi
        if angle > 3 * pi / 2:
            cf = 2 * pi
        return atan(self.x_radius/self.y_radius * tan(angle)) + cf


class EllipticArc(PathSegment):

    ell_dict = {}

    def __init__(self, start, end, rx, ry, axis_rot, pos_dir=True, large_arc=False):
        self.rx = rx
        self.ry = ry
        # calculate ellipse center
        # the center is on two ellipses one with its center at the start point, the other at the end point
        # for simplicity take the  one ellipse at the origin and the other with offset (tx, ty),
        # find the center and translate back to the original offset at the end
        end_o = end - start # offset end vector
        end_o.t += axis_rot # take axis rotation into account
        tx = end_o.x
        ty = end_o.y

        # some helper variables for the intersection points
        # used sympy to come up with the equations
        ff = (rx**2*ty**2 + ry**2*tx**2)
        cx = rx**2*ry*tx*ty**2 + ry**3*tx**3
        cy = rx*ty*ff
        sx = rx*ty*sqrt(4*rx**4*ry**2*ty**2 - rx**4*ty**4 + 4*rx**2*ry**4*tx**2 - 2*rx**2*ry**2*tx**2*ty**2 - ry**4*tx**4)
        sy = ry*tx*sqrt(-ff*(-4*rx**2*ry**2 + rx**2*ty**2 + ry**2*tx**2))

        # intersection points
        c1 = Coordinate((cx - sx) / (2*ry*ff), (cy + sy) / (2*rx*ff))
        c2 = Coordinate((cx + sx) / (2*ry*ff), (cy - sy) / (2*rx*ff))

        if end_o.dot(c1) < 0: # c1 is to the left of end_o
            left = c1
            right = c2
        else:
            left = c2
            right = c1

        if pos_dir != large_arc: #center should be on the left of end_o
            center = left
        else: #center should be on the right of end_o
            center = right
        # translate back to original offset
        self.center = center + start

        #re-use ellipses with same rx, ry to save some memory
        if (rx, ry) in self.ell_dict:
            self.ellipse = self.ell_dict[(rx, ry)]
        else:
            self.ellipse = Ellipse(rx, ry)
            self.ell_dict[(rx, ry)] = self.ellipse

        self.start = start
        self.end = end
        self.axis_rot = axis_rot
        self.start_theta = self.ellipse.theta_at_angle((start - self.center).t)
        self.end_theta = self.ellipse.theta_at_angle((end - self.center).t)

    @property
    def length(self):
        return self.ellipse.dist_from_theta(self.start_theta, self.end_theta)

    def t_to_theta(self, t):
        """convert t (always between 0 and 1) to angle theta"""
        return self.start_theta + (self.end_theta - self.start_theta) * t

    def theta_to_t(self, theta):
        return (theta - self.start_theta)/(self.end_theta - self.start_theta)

    def curvature(self, t):
        theta = self.t_to_theta(t)
        return self.ellipse.curvature(theta)

    def tangent(self, t):
        theta = self.t_to_theta(t)
        return self.ellipse.tangent(theta)

    def t_at_length(self, length):
        """interpolated t where the curve is at the given length"""
        theta = self.ellipse.theta_from_dist(length, self.start_theta)
        return self.theta_to_t(theta)

    def length_at_t(self, t):
        return self.ellipse.dist_from_theta(self.start_theta, self.t_to_theta(t))

    def pathpoint_at_t(self, t):
        """pathpoint on the curve from t=0 to point at t."""
        centered = self.ellipse.coordinate_at_theta(self.t_to_theta(t))
        centered.t += self.axis_rot
        return PathPoint(t, centered + self.center, self.tangent(t), self.curvature(t), self.length_at_t(t))

    # identical to Bezier code
    def subdivide(self, part_length, start_offset=0):
        nr_parts = int((self.length - start_offset) // part_length)
        k_o = start_offset / self.length
        k2t = lambda k : k_o + k * part_length / self.length
        points = [self.pathpoint_at_t(k2t(k)) for k in range(nr_parts + 1)]
        return(points, self.length - points[-1].c_dist)

