#!/usr/bin/python3
# -*- coding: utf-8 -*-
################################################################################
#    Capri Copyright (C) 2014 Suizokukan
#    Contact: suizokukan _A.T._ orange dot fr
#
#    This file is part of Capri.
#    Capri is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Capri is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Capri.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
    ❏Capri❏ : capri/board_textrepr.py

        function get_board_textrepr() and some functions required to produce
        ansi colors.

        Use get_board_textrepr() to have an ASCII-based, textual representation of
        a Board object, with or without ANSI colors.
"""
import operator

#///////////////////////////////////////////////////////////////////////////////
def get_board_textrepr(board_object,
                       add_ansi_colors,
                       console_symbols_for_players,
                       console_colors_for_players,
                       startstring=""):
    """

            get_board_textrepr()

            Return a string representing the Board object "board_object".

            ▨▨▨
           ▨▨1▨▨
            ▨▨▨ ▣▣▣
               ▣▣2▣▣
            ▢▢▢ ▣▣▣
           ▢▢3▢▢
            ▢▢▢

           all lines returned will begin with <startstring>, allowing to prefix
           all the lines.
    """
    # a special case : if there's no tile on the board, the function returns an
    # empty string; otherwise, an error would occur.
    if len(board_object) == 0:
        return ""

    #.......................................................................
    # computing (xmin, ymin), (xmax, ymax) and adding a margin :
    xmin, ymin, xmax, ymax = board_object.get_min_max_positions()
    xmin -= 1
    ymin -= 1
    xmax += 1
    ymax += 1

    #.......................................................................
    # filling consolecharacters_table
    #
    # consolecharacters_table is a dictionary (x,y) : (str)one_character
    #
    #
    # BEWARE : for the moment (see infra, the negative y are 'above' the
    # positive ones : e.g. -5 at line 0, -4 at line 1 and so on.
    consolecharacters_table = {}
    consolecharacters_table = get_console_repr_of_board__1(consolecharacters_table,
                                                           xmin, ymin, xmax, ymax)
    consolecharacters_table = get_console_repr_of_board__2(consolecharacters_table,
                                                           xmin, ymin, xmax, ymax)
    consolecharacters_table = get_console_repr_of_board__3(consolecharacters_table,
                                                           board_object,
                                                           add_ansi_colors,
                                                           console_symbols_for_players,
                                                           console_colors_for_players)

    #.......................................................................
    # consolecharacters_table > res
    res = get_console_repr_of_board__4(consolecharacters_table,
                                       xmin, ymin, xmax, ymax)

    #.......................................................................
    # let's add the players :
    res.append(get_console_repr_of_board__5(board_object,
                                            console_colors_for_players,
                                            console_symbols_for_players,
                                            add_ansi_colors))

    #.......................................................................
    # let's add the gains :
    res.append(get_console_repr_of_board__6(board_object))

    # let's add the startstring at the beginning of all lines :
    _string = "\n"+startstring
    return _string.join(res)

#///////////////////////////////////////////////////////////////////////////
def get_console_repr_of_board__6(board_object):
    """
        return a string describing the gains.
    """
    res = "gains :"
    sorted_gains = sorted(board_object.get_gains().items(), key=operator.itemgetter(1))
    sorted_gains.reverse()
    for player_id, gain in sorted_gains:
        res += " {0}:{1};".format(player_id, gain)

    return res

#///////////////////////////////////////////////////////////////////////////
def get_console_repr_of_board__5(board_object,
                                 console_colors_for_players,
                                 console_symbols_for_players,
                                 add_ansi_colors):
    """
        add the players
    """
    res = "players : "
    plstr = "'{1}'({2}) (#{0});  "   # players' string

    for player_index, player_id in enumerate(board_object.players_id):
        player_symbol = get_player_ansiconsolechar(_player_id=player_id,
                                                   _board_object=board_object,
                                                   add_ansi_colors=add_ansi_colors,
                                                   console_symbols_for_players=console_symbols_for_players,
                                                   console_colors_for_players=console_colors_for_players)

        res += plstr.format(player_index,
                            add_console_playeransicolor(string=player_id,
                                                        player_id=player_id,
                                                        board_object=board_object,
                                                        console_colors_for_players=console_colors_for_players,
                                                        add_ansi_colors=add_ansi_colors),
                            player_symbol)
    return res

#///////////////////////////////////////////////////////////////////////////
def add_console_playeransicolor(string, player_id, board_object, add_ansi_colors, console_colors_for_players):
    """
            Add a color to the string 'string' and add the default color
            code at the end of the res string.

            Return the resulting string.
    """
    assert player_id in board_object.players_id

    color_before = ""
    color_after = ""

    if add_ansi_colors:
        targetcolor = console_colors_for_players[board_object.players_id.index(player_id)]
        color_before = get_console_ansicolor(targetcolor)

        color_after = get_default_console_color()

    return color_before + string + color_after

#///////////////////////////////////////////////////////////////////////////
def get_console_ansicolor(color_name):
    """
            get_console_ansicolor()

            Add a color to the string 'string'.
    """
    res = ""
    if color_name == 'red':
        res = "\033[0;31;1m"
    elif color_name == 'green':
        res = "\033[0;32;1m"
    elif color_name == 'yellow':
        res = "\033[0;33;1m"
    elif color_name == 'blue':
        res = "\033[0;34;1m"
    elif color_name == 'magenta':
        res = "\033[0;35;1m"
    elif color_name == 'cyan':
        res = "\033[0;36;1m"
    elif color_name == 'white':
        res = "\033[0;37;1m"

    return res

#///////////////////////////////////////////////////////////////////////////
def get_console_repr_of_board__1(consolecharacters_table, xmin, ymin, xmax, ymax):
    """
            get_console_repr_of_board__1()

            first layer : background character + lines characters

            function called by get_board_textrepr().
    """
    consolecharacters_table = consolecharacters_table
    for y in range((ymin-1)*4, (ymax+1)*4):
        for x in range((xmin-1)*4, (xmax+1)*4):

            # background character :
            consolecharacters_table[(x, y)] = " "

            # lines character :
            if x%4 == 0 and (y-2)%4 == 0:
                consolecharacters_table[(x, y)] = "."

    return consolecharacters_table

#///////////////////////////////////////////////////////////////////////////
def get_console_repr_of_board__2(consolecharacters_table, xmin, ymin, xmax, ymax):
    """
            second layer : the digits()

            function called by get_board_textrepr().
    """
    for y in range((ymin-1)*4, (ymax+1)*4):
        y_index = int((y-2) / 4)
        for x in range((xmin-1)*4, (xmax+1)*4):
            x_index = int(x / 4)

            if x == (xmin-1)*4 and (y-2)%4 == 0:
                y_index_repr = "{0:+03}".format(y_index)
                consolecharacters_table[(x, y)] = y_index_repr[0]
                consolecharacters_table[(x+1, y)] = y_index_repr[1]
                consolecharacters_table[(x+2, y)] = y_index_repr[2]

            if x == ((xmax+1)*4)-2 and (y-2)%4 == 0:
                y_index_repr = "{0:+03}".format(y_index)
                consolecharacters_table[(x-1, y)] = y_index_repr[0]
                consolecharacters_table[(x, y)] = y_index_repr[1]
                consolecharacters_table[(x+1, y)] = y_index_repr[2]

            if x%4 == 0 and x != (xmin-1)*4 and y == (ymin-1)*4:
                x_index_repr = "{0:+03}".format(x_index)
                consolecharacters_table[(x-1, y)] = x_index_repr[0]
                consolecharacters_table[(x, y)] = x_index_repr[1]
                consolecharacters_table[(x+1, y)] = x_index_repr[2]

            if x%4 == 0 and x != (xmin-1)*4 and y == ((ymax+1)*4)-1:
                x_index_repr = "{0:+03}".format(x_index)
                consolecharacters_table[(x-1, y)] = x_index_repr[0]
                consolecharacters_table[(x, y)] = x_index_repr[1]
                consolecharacters_table[(x+1, y)] = x_index_repr[2]

    return consolecharacters_table

#///////////////////////////////////////////////////////////////////////////
def get_console_repr_of_board__3(consolecharacters_table,
                                 board_object,
                                 add_ansi_colors,
                                 console_symbols_for_players,
                                 console_colors_for_players):
    """
            third layer : tiles

            function called by get_board_textrepr().
    """
    for (x, y) in board_object:

        player_id = board_object[(x, y)].player_id

        fill_character = get_player_ansiconsolechar(player_id,
                                                    board_object,
                                                    add_ansi_colors,
                                                    console_symbols_for_players,
                                                    console_colors_for_players)
        yshift = (x%2)*2

        # foreground :
        consolecharacters_table[((x*4)-1, (y*4)+2-1+yshift)] = fill_character
        consolecharacters_table[(x*4, (y*4)+2-1+yshift)] = fill_character
        consolecharacters_table[((x*4)+1, (y*4)+2-1+yshift)] = fill_character

        consolecharacters_table[((x*4)-2, (y*4)+2+yshift)] = fill_character
        consolecharacters_table[((x*4)-1, (y*4)+2+yshift)] = fill_character
        consolecharacters_table[((x*4)+1, (y*4)+2+yshift)] = fill_character
        consolecharacters_table[((x*4)+2, (y*4)+2+yshift)] = fill_character

        consolecharacters_table[((x*4)-1, (y*4)+2+1+yshift)] = fill_character
        consolecharacters_table[(x*4, (y*4)+2+1+yshift)] = fill_character
        consolecharacters_table[((x*4)+1, (y*4)+2+1+yshift)] = fill_character

        # height :
        height = "{0:03}".format(board_object[(x, y)].height)
        consolecharacters_table[((x*4)-1, (y*4)+2+yshift)] = add_console_playeransicolor(height[0],
                                                                                         player_id,
                                                                                         board_object,
                                                                                         add_ansi_colors,
                                                                                         console_colors_for_players)
        consolecharacters_table[((x*4)+0, (y*4)+2+yshift)] = add_console_playeransicolor(height[1],
                                                                                         player_id,
                                                                                         board_object,
                                                                                         add_ansi_colors,
                                                                                         console_colors_for_players)
        consolecharacters_table[((x*4)+1, (y*4)+2+yshift)] = add_console_playeransicolor(height[2],
                                                                                         player_id,
                                                                                         board_object,
                                                                                         add_ansi_colors,
                                                                                         console_colors_for_players)

    return consolecharacters_table

#///////////////////////////////////////////////////////////////////////////
def get_console_repr_of_board__4(consolecharacters_table, xmin, ymin, xmax, ymax):
    """
            We have to invert the y : negative y are in the last lines, not
            in the first lines.

            function called by get_board_textrepr().
    """
    res = []
    for y in range((ymin-1)*4, (ymax+1)*4):
        res.insert(0, [])
        for x in range((xmin-1)*4, (xmax+1)*4):
            res[0].append(consolecharacters_table[x, y])
        res[0] = "".join(res[0])
    return res

#///////////////////////////////////////////////////////////////////////////
def get_default_console_color():
    """
            get_default_console_color()
    """
    return "\033[0m"

#///////////////////////////////////////////////////////////////////////////
def get_player_ansiconsolechar(_player_id,
                               _board_object,
                               add_ansi_colors,
                               console_symbols_for_players,
                               console_colors_for_players):
    """
            get_player_ansiconsolechar()

                    -> get console character representing a player

            Return console character + color for the player number '_player_id' .
    """
    symbol = console_symbols_for_players[_board_object.players_id.index(_player_id)]
    return add_console_playeransicolor(symbol,
                                       _player_id,
                                       _board_object,
                                       add_ansi_colors,
                                       console_colors_for_players)
