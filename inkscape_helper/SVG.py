import inkex
import simplestyle

def _format_1st(command, is_absolute):
    """Small helper function for the Path class"""
    return command.upper() if is_absolute else command.lower()

default_style = simplestyle.formatStyle(
    {'stroke': '#000000',
    'stroke-width': '0.1',
    'fill': 'none'
    })

red_style = simplestyle.formatStyle(
    {'stroke': '#FF0000',
    'stroke-width': '0.1',
    'fill': 'none'
    })

green_style = simplestyle.formatStyle(
    {'stroke': '#00FF00',
    'stroke-width': '0.1',
    'fill': 'none'
    })

blue_style = simplestyle.formatStyle(
    {'stroke': '#0000FF',
    'stroke-width': '0.1',
    'fill': 'none'
    })

def layer(parent, layer_name):
    layer = inkex.etree.SubElement(parent, 'g')
    layer.set(inkex.addNS('label', 'inkscape'), layer_name)
    layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
    return layer

def group(parent):
    return inkex.etree.SubElement(parent, 'g')

class Path(object):
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

    def arc_to(self, radius, coord, rotation=0, pos_sweep=True, large_arc=False, absolute=False):
        self.nodes.append("{0} {1} {2} {3} {4} {5} {6} {7}"
            .format(_format_1st('a', absolute), radius.x, radius.y, rotation,
                   1 if large_arc else 0, 1 if pos_sweep else 0, coord.x, coord.y))

    def close(self):
        self.nodes.append('z')

    def path(self, parent, style=default_style):
        attribs = {'style': style,
                    'd': ' '.join(self.nodes)}
        inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attribs)

    def curve(self, parent, segments, style, closed=True):
        pathStr = ' '.join(segments)
        if closed:
            pathStr += ' z'
        attributes = {
          'style': style,
          'd': pathStr}
        inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attributes)

    def remove_last(self):
        self.nodes.pop()
