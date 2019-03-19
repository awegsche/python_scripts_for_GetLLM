"""
Module ansi_colors.py
------------------------------------

@author: awegsche

@version: 1.0

Helper functions to convert RGB and html colors to ansi escape sequences

"""

import re
from matplotlib import colors

ONE_OVER_256 = 0.00390625
ONE_OVER_16 = 0.0625


def ansi(color="none"):
    """
    Converts ```color``` into an ANSI escape sequence changing the color of the current
    terminal output.

    Args:
        color (string or tuple): A string representing the color. This can be one of the following:
            - an HTML color in the format ```#RRGGBB``` or ```#RGB```
            - a matplotlib color name like ```"firebrick"```
            - an RGB color in the format ```rgb:r,g,b``` where r,g,b \in [0,1)
            example: ```rgb:1.0,0.0,0.0```
            - the string 'none' to reset the color to default
            - a tuple (r, g, b) where r,g,b \n [0,255]

    """
    if color == "" or color is None:
        return "\33[0m"
    if isinstance(color, tuple):
        return "\33[38;2;{:d};{:d};{:d}m".format(int(255 * color[0]),
                                                 int(255 * color[1]),
                                                 int(255 * color[2]))
    tupl = _clr_tuple(color)
    if tupl is not None:
        return ansi(tupl)
    if color == "bold":
        return "\33[1m"
    if color == "/bold":
        return "\33[22m"
    return "\33[0m"


def clr_multiply(clr1, clr2):
    """ multiplies two colors

    Args:
        clr1 (string): representation (see ansi) of first color
        clr2 (string): representation of the second color
    """
    a = _clr_tuple(clr1)
    b = _clr_tuple(clr2)

    return (max(0.0, min(1.0, a[0] * b[0])),
            max(0.0, min(1.0, a[1] * b[1])),
            max(0.0, min(1.0, a[2] * b[2])))


def _clr_tuple(colorstring):
    """ converts colorstring into a tuple of ints (r,g,b)

    Args:
        colorstring (string): string representation of the color, see ansi
    """

    if colorstring[0] == '#':
        if len(colorstring) == 7:
            return (ONE_OVER_256 * float(_hexbyte(colorstring[1:3])),
                    ONE_OVER_256 * float(_hexbyte(colorstring[3:5])),
                    ONE_OVER_256 * float(_hexbyte(colorstring[5:7])))
        if len(colorstring) == 4:
            return (16 * _hexbyte(colorstring[1]),
                    16 * _hexbyte(colorstring[2]),
                    16 * _hexbyte(colorstring[3]))
    if colorstring in colors.CSS4_COLORS:
        return _clr_tuple(colors.CSS4_COLORS[colorstring])
    if colorstring in colors.BASE_COLORS:
        return _clr_tuple(colors.BASE_COLORS[colorstring])

    rgb_re = re.compile("rgb:(.*),(.*),(.*)")

    rgb_match = rgb_re.search(colorstring)
    if rgb_match:
        return (float(rgb_match.group(1)),
                float(rgb_match.group(2)),
                float(rgb_match.group(3)))
    return None


def _hexbyte(b):
    """ Converts the hex number b to integer

    Args:
        b (string): a two-character representation of a byte, like 01, FF, A0 etc.
    """
    return _hexchar(b[0]) * 16 + _hexchar(b[1])


def _hexchar(c):
    """ Converts the character b into a number.

    Args:
        c (char): character in base 16: 1, ... 9, A, ... F
        accepts lower case letters a, ... f
    """
    if c == '1': return 1
    if c == '2': return 2
    if c == '3': return 3
    if c == '4': return 4
    if c == '5': return 5
    if c == '6': return 6
    if c == '7': return 7
    if c == '8': return 8
    if c == '9': return 9
    if c == 'A' or c == 'a': return 10
    if c == 'B' or c == 'b': return 11
    if c == 'C' or c == 'c': return 12
    if c == 'D' or c == 'd': return 13
    if c == 'E' or c == 'e': return 14
    if c == 'F' or c == 'f': return 15
    return 0
