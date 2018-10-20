#!/usr/bin/env python3 -O
"""
    Game rink rendering functions for nhlapi library
"""

import sys

# ANSI color constant escape sequences:
ANSI_PRE = '\x1b['
ANSI_POST = 'm'
ANSI_RESET = ANSI_PRE + '0' + ANSI_POST
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
PURPLE = 35
CYAN = 36
WHITE = 37

def color(clr, text):
    """
        function to wrap ANSI escape sequences around text
        to set the display color of the text

        :param clr: one of the color constants above
        :param text: the text string to color
        :return: the text with the proper ANSI prefix and suffix bytes
    """
#   if not USE_COLOR:
#       return text
    background_color = ''
#   if BLACK_BACKGROUND:
#       background_color = ';40'
    prefix = '0;'
#   if USE_BRIGHT:
#       prefix = '1;'

    return ''.join([ANSI_PRE, prefix, str(clr), background_color, ANSI_POST, text, ANSI_RESET])


def add_circle(game, center: (tuple, list, set), radius: int, cchar='o'):
    """
    Set the bytes around the specified point to the proper characters
    to be a circle when drawn using ASCII characters

    :param game: list of lists containing the game display contents
    :param center: container holding an x and y center point of the desired circle
    :param radious: radious of circle to be added
    """
    if (not isinstance(game, list) or not game or not isinstance(game[0], list)):
        raise ValueError('A very specific bad thing happened.')

    center_x = center[0]
    center_y = center[1]
    if center_y < 0 or center_y >= len(game):
        return
    if center_x < 0 or center_x >= len(game[center_y]):
        return
    game[center_y][center_x] = cchar

    def add_horizontal(row, offset, start_char, fill_char, end_char):
        if row <= 0 or row >= len(game) - 1:
            return
        # The top radius row is valid:
        game[row][center_x] = fill_char
        if center_x - offset > 0:
            # The left side of the top center column is valid:
            if offset == radius * 2 - 1:
                game[row][center_x - offset] = start_char
            else:
                game[row][center_x - offset] = fill_char
        if center_x + offset < len(game[row]) - 1:
            # The right side of the top center column is valid:
            if offset == radius * 2 - 1:
                game[row][center_x + offset] = end_char
            else:
                game[row][center_x + offset] = fill_char

    def add_vertical(column, offset):
        if column <= 0 or column >= len(game[center_y]) - 1:
            return
        # The left radius column is valid:
        game[center_y][column] = '|'
        if center_y - int(offset / 2) > 0:
            # The top side of the left center column is valid:
            game[center_y - int(offset / 2)][column] = '|'
        if center_y + int(offset / 2) < len(game) - 1:
            # The bottom side of the left center column is valid:
            game[center_y + int(offset / 2)][column] = '|'

    for offset in range(1, radius * 2):
        add_horizontal(center_y - radius, offset, '/', '`', '\\')   # Top:
        add_horizontal(center_y + radius, offset, '\\', '_', '/')   # Bottom:
        add_vertical(center_x - radius * 2, offset)                 # Left:
        add_vertical(center_x + radius * 2, offset)                 # Right:

def create(width, height):
    """
    Create a display object for a hockey game with the specified width and height

    :param width: width of the desired display
    :param height: height of the desired display
    :return: the initialized game as a list of lists of display characters
    """
    glx = int(width * 0.055)
    gly = int(height * 0.5)

    bllx = int(width * 0.375)
    clx = int(width * 0.5)
    blrx = width - (bllx + 1)

    grx = width - (glx + 1)

    fo1x = int(width * 0.155)
    fo2x = int(width * 0.4)
    fo3x = int(width * 0.6)
    fo4x = int(width * 0.845)

    fo_upper = int(height * 0.1)
    fo_lower = int(height * 0.9)

    fo_dots = [(fo1x, fo_upper), (fo2x, fo_upper), (fo3x, fo_upper), (fo4x, fo_upper),
               (clx, gly),
               (fo1x, fo_lower), (fo2x, fo_lower), (fo3x, fo_lower), (fo4x, fo_lower)]

    result = []
    for row in range(height):
        # Horizontal border row, middle rows, border row at bottom
        content = [x for x in ' ' * width]
        if row == 0:
            content = ['/'] + [x for x in '`' * (width - 2)] + ['\\']
        elif row == height - 1:
            content = ['\\'] + [x for x in '_' * (width - 2)] + ['/']
        result.append(content)

    for row in range(height):
        for col in range(width):
            # Vertical lines: border lines, goal lines, blue lines, and center line
            if  row > 0 and row < height - 1 and col in (0, glx, bllx, clx, blrx, grx, width - 1):
                result[row][col] = '|'
            # Goals
            if (col == glx and row == gly) or (col == grx and row == gly):
                result[row][col] = '#'
            # Faceoff dots
            for dot in fo_dots:
                if col == dot[0] and row == dot[1]:
                    add_circle(result, (col, row), int(width / 75))
    add_circle(result, (clx, height - 1), 2)
    return result


def render(result, play=None):
    """
    Display the specified game

    :param result: the hockey rink for a game to display
    :param play: (optional) the move to be displayed on top of the game rink
    :return: Nothing
    """
    assert play is None

    for row in result:
        for column in row:
            print(str(column), end='')
        print()


def crsr_set(col, row):
    """
        Get the terminal cursor position
    """
#   Cursor Position:
#
#   Esc[Line;ColumnH
#   Esc[Line;Columnf
#
#   Moves the cursor to the specified position (coordinates).
#   If you do not specify a position, the cursor moves to the home position at
#   the upper-left corner of the screen (line 0, column 0).

    sys.stdout.write('\x1b[{:d};{:d}H'.format(col, row))
#   sys.stdout.write('\x1b[{:d};{:d}f'.format(col, row))


def crsr_get():
    """
    i   Set the terminal cursor position
    """
    sys.stdout.write('\x1b[6n')
    value = sys.stdin.read(10)
    return value


if __name__ == '__main__':
    def run_test(shapes: list):
        """
        Run the code in this module to test for issues

        :param shapes: a list of tuples containing the desired game widths and heights
        :return: Nothing
        """
        for pair in shapes:
            result = create(pair[0], pair[1])
            render(result)
#       value = crsr_get()
#       print([c for c in value])

#   exit(run_test([]))

#   exit(run_test([(101, 25),
#                  (77, 21)]))

#   exit(run_test([(201, 43)]))

    exit(run_test([(101, 25)]))

#   exit(run_test([(77, 21)]))

#   exit(run_test([(17, 5)]))
