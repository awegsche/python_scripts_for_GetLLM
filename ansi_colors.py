"""
Module ansi_colors.py
------------------------------------

@author: awegsche

@version: 1.0

Helper functions to convert RGB and html colors to ansi escape sequences

"""

from matplotlib import colors

def ansi(colorstring="none"):
    """
    Converts ```colorstring``` into an ANSI escape sequence changing the color of the current
    terminal output.

    Args:
        colorstring (string): A string representing the color. This can be one of the following:
            - an HTML color in the format ```#RRGGBB``` or ```#RGB```
            - a matplotlib color name like ```"firebrick"```
            - the string 'none' to reset the color to default

    """
    if colorstring == "" or colorstring is None:
        return "\33[0m"
    if colorstring[0] == '#':
        esc = "\33[38;2;"
        if len(colorstring) == 7:
            esc += str(_hexbyte(colorstring[1:3])) + ";"
            esc += str(_hexbyte(colorstring[3:5])) + ";"
            esc += str(_hexbyte(colorstring[5:7])) + "m"
        elif len(colorstring) == 4:
            esc += str(16 * _hexbyte(colorstring[1])) + ";"
            esc += str(16 * _hexbyte(colorstring[2])) + ";"
            esc += str(16 * _hexbyte(colorstring[3])) + "m"
        return esc
    elif colorstring in colors.CSS4_COLORS:
        return ansi(colors.CSS4_COLORS[colorstring])
    elif colorstring in colors.BASE_COLORS:
        return ansi(colors.BASE_COLORS[colorstring])
    elif colorstring == "bold":
        return "\33[1m"
    elif colorstring == "/bold":
        return "\33[22m"
    return "\33[0m"


def _hexbyte(b):
    """ Converts the hex number b to integer

    Args:
        b (string): a string representation of a byte, like 01, FF, A0 etc.
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
