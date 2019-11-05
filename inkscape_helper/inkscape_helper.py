#!/usr/bin/env python
from __future__ import division
import inkex
import simplestyle
import copy

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


def _format_1st(command, is_absolute):
    """Small helper function for the Path class"""
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

    def curve(self, parent, segments, style, closed=True):
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
        return length / self.length


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



class EllipticArc(PathSegment):

    ell_dict = {}

    def __init__(self, start, end, rx, ry, axis_rot, pos_dir=True, large_arc=False):
        self.rx = rx
        self.ry = ry
        # calculate ellipse center
        # the center is on two ellipses one with its center at the start point, the other at the end point
        # for simplicity take the  one ellipse at the origin and the other with offset (tx, ty),
        # find the center and translate back to the original offset at the end
        axis_rot *=  pi / 180 # convert to radians
        # start and end are mutable objects, copy to avoid modifying them
        r_start = copy.copy(start)
        r_end = copy.copy(end)
        r_start.t -= axis_rot
        r_end.t -= axis_rot
        end_o = r_end - r_start # offset end vector

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

        if end_o.cross_norm(c1 - r_start) < 0: # c1 is to the left of end_o
            left = c1
            right = c2
        else:
            left = c2
            right = c1

        if pos_dir != large_arc: #center should be on the left of end_o
            center_o = left
        else: #center should be on the right of end_o
            center_o = right

        #re-use ellipses with same rx, ry to save some memory
        if (rx, ry) in self.ell_dict:
            self.ellipse = self.ell_dict[(rx, ry)]
        else:
            self.ellipse = Ellipse(rx, ry)
            self.ell_dict[(rx, ry)] = self.ellipse

        self.start = start
        self.end = end
        self.axis_rot = axis_rot
        self.pos_dir = pos_dir
        self.large_arc = large_arc
        self.start_theta = self.ellipse.theta_at_angle((-center_o).t)
        self.end_theta = self.ellipse.theta_at_angle((end_o - center_o).t)

        # translate center back to original offset
        center_o.t += axis_rot
        self.center = center_o + start

    @property
    def length(self):
        return self.ellipse.dist_from_theta(self.start_theta, self.end_theta)

    def t_to_theta(self, t):
        """convert t (always between 0 and 1) to angle theta"""
        start = self.start_theta
        end = self.end_theta
        if self.pos_dir and end < start:
            end += 2 * pi
        #if !self.pos_dir and start < end:
        # TODO: handle negative direction arcs
        return start + (end - start) * t

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

