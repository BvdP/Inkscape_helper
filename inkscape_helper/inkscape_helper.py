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
