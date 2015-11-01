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
    ❏Capri❏ : capri/ui/linuxconsole/linuxconsole.py
"""
import random
import re

import capri.board_txtrepr as board_txtrepr
from capri.configfile import CONFIGPARSER
from capri.move import Move

################################################################################
class UILinuxConsole(object):
    """
        UILinuxConsole class

        UI for console input/output.
    """

    # regex used to analyse the human input giving a move :
    RE__MOVE = re.compile(r"\s*([-]?\d)\s*,\s*([-]?\d)\s*->\s*([-]?\d)\s*,\s*([-]?\d)\s*")

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                UILinuxConsole.__init__
        """
        assert "ui.linuxconsole" in CONFIGPARSER
        assert "allow ANSI colors" in CONFIGPARSER["ui.linuxconsole"]
        assert "console symbols for players" in CONFIGPARSER["ui.linuxconsole"]
        assert "console colors for players" in CONFIGPARSER["ui.linuxconsole"]

        self.use_ansi_colors_on_console = CONFIGPARSER["ui.linuxconsole"]["allow ANSI colors"] == "true"
        self.console_symbols_for_players = CONFIGPARSER["ui.linuxconsole"]["console symbols for players"]
        self.console_colors_for_players = CONFIGPARSER["ui.linuxconsole"]["console colors for players"].split(";")

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def debug(msg):
        """
                UILinuxConsole.debug()
        """
        print(msg)

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def end():
        """
                UILinuxConsole.end

                Function to be called at the end of the program.
        """
        print(board_txtrepr.get_default_console_color())

    #///////////////////////////////////////////////////////////////////////////
    def get_console_repr_of_board(self, board_object):
        """
                UILinuxConsole.get_console_repr_of_board()

                Return a string representing the Board object "board_object".
        """
        return board_txtrepr.get_board_textrepr(board_object=board_object,
                                                add_ansi_colors=self.use_ansi_colors_on_console,
                                                console_symbols_for_players=self.console_symbols_for_players,
                                                console_colors_for_players=self.console_colors_for_players)

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def message(msg):
        """
                UILinuxConsole.message()
        """
        print(msg)


    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def pause_to_see_the_last_move():
        """
                UILinuxConsole.pause_to_see_the_last_move()
        """
        input()

    #///////////////////////////////////////////////////////////////////////////
    def your_move_please(self,
                         _player_object,
                         _board_object,
                         _game):
        """
                UILinuxConsole.your_move_please()

                return a Move object.
        """
        print("UILinuxConsole.your_move_please()", _player_object)

        moves = _board_object.get_the_moves_a_player_may_play(_player_object.player_id)

        if len(moves) == 0:
            print("You have no available move")
            return Move(None)

        stop = False
        move_to_be_returned = Move(((0, 0), (0, 0)))      # (faked initialization)

        # character used to symbolize _player_object.player_id :
        symb = board_txtrepr.get_player_ansiconsolechar(_player_id=_player_object.player_id,
                                                        _board_object=_board_object,
                                                        add_ansi_colors=self.use_ansi_colors_on_console,
                                                        console_symbols_for_players=self.console_symbols_for_players,
                                                        console_colors_for_players=self.console_colors_for_players)

        while not stop:
            print("Please enter your move, {1}({0}) : ".format(symb,
                                                               _player_object.player_id))
            inputstring = input("> ")

            stop, move_to_be_returned = self.your_move_please__interpret(inputstring,
                                                                         _player_object,
                                                                         _board_object,
                                                                         _game)

        return move_to_be_returned

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def your_move_please__interpret(inputstring, _player_object, _board_object, _game):
        """
                UILinuxConsole.your_move_please__interpret()
        """
        moves = _board_object.get_the_moves_a_player_may_play(_player_object.player_id)
        move_to_be_returned = Move(((0, 0), (0, 0)))      # (faked initialization)
        stop = False

        if inputstring.strip() in ("", "?", "h", "help"):
            print("expected format : a string like :")
            print("    0,1->-3,2")
            print()
            print("commands : ")
            print("    ?, h, help : display this help")
            print("    r, random : play randomly")
            print("    m, moves : show the available moves")
            print("    pm       : show the played moves")

        elif inputstring.strip() in ("r", "random"):
            move_to_be_returned = moves[random.randrange(len(moves))]
            print("You choosed to play randomly : {0},{1} -> {2},{3}".format(move_to_be_returned.x0,
                                                                             move_to_be_returned.y0,
                                                                             move_to_be_returned.x1,
                                                                             move_to_be_returned.y1))
            input()
            stop = True

        elif inputstring.strip() in ("m", "moves"):
            print("available moves : ")
            for move in moves:
                print("o  {0}".format(move))

        elif inputstring.strip() in ("pm",):
            print("played moves : ")
            for player_id, move in _game.played_moves:
                print("o  {0} : {1}".format(player_id, move))

        else:
            match = re.match(UILinuxConsole.RE__MOVE, inputstring)

            if match is None:
                print("error : wrong entry. Please try again. " \
                      "See the help message if you don't know what to do.")
            else:
                groups = match.groups()

                if len(groups) != 4:
                    print("error : wrong entry. Please try again. " \
                          "See the help message if you don't know what to do.")
                else:
                    move_to_be_returned = Move((int(groups[0]), int(groups[1])),
                                               (int(groups[2]), int(groups[3])))

                    if not _board_object.is_it_a_correct_move(move_to_be_returned):
                        print("Your move is incorrect. Please try again.")
                        print("available moves : ")
                        for move in moves:
                            print("o  {0}".format(move))
                    else:
                        stop = True

        return stop, move_to_be_returned
