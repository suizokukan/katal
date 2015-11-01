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
    ❏Capri❏ : ./capri/gamebackupfile.py

    GameBackupFile class
"""
from datetime import datetime
import configparser

from texttable import Texttable

from capri.board_txtrepr import get_board_textrepr
from capri.configfile import CONFIGPARSER
from capri.player import Player
from capri.tile import Tile
from capri.move import Move

from capri.constants import NAME_OF_THE_PROJECT

################################################################################
class GameBackupFile(object):
    """
        GameBackupFile class

        Use this class in a "with" block to save a game.
    """

    COMMENT_PREFIX = "# "

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                GameBackupFile.__init__()
        """
        self.srcfile = None

    #///////////////////////////////////////////////////////////////////////////
    def __enter__(self):
        """
                GameBackupFile.__enter__()
        """
        return self

    #///////////////////////////////////////////////////////////////////////////
    def __exit__(self, typ, value, traceback):
        """
                GameBackupFile.__exit__()
        """
        self.srcfile.close()

    #///////////////////////////////////////////////////////////////////////////
    def flush(self):
        """
                GameBackupFile.flush()
        """
        self.srcfile.flush()

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def load(_file_name, _game_obj):
        """
                GameBackupFile.load()
        """
        res = True
        try:
            parser = configparser.ConfigParser()
            parser.read(_file_name)

            # settings .........................................................
            _game_obj.current_ui.debug("  o reading the settings :")
            _game_obj.initial_number_of_tokens = parser["settings"]["initial_number_of_tokens"]
            _game_obj.current_ui.debug("    ... initial_number_of_tokens : "+_game_obj.initial_number_of_tokens)

            for player_index in range(int(parser["settings"]["players_number"])):
                player_id = parser["settings"]["player"+str(player_index)+".player_id"]
                player_nature = int(parser["settings"]["player"+str(player_index)+".nature"])
                _game_obj.players[player_id] = Player(_player_id=player_id,
                                                      _nature=player_nature)
                _game_obj.board.players_id.append(player_id)
                _game_obj.current_ui.debug("    ... player_id={0}, nature={1}".format(player_id,
                                                                                      player_nature))

            _game_obj.who_plays_the_next_move = [0, list(_game_obj.players.keys())[0]]
            _game_obj.current_ui.debug("    ... _game_obj.who_plays_the_next_move=" + \
                                       str(_game_obj.who_plays_the_next_move))

            # initial position .................................................
            _game_obj.current_ui.debug("  o reading the initial position :")
            stop = False
            position_index = 0
            while not stop:
                if not parser.has_option("initial position",
                                         "initial position{0}.player_id".format(position_index)):
                    stop = True
                else:
                    x = int(parser["initial position"]["initial position{0}.x".format(position_index)])
                    y = int(parser["initial position"]["initial position{0}.y".format(position_index)])
                    height = int(parser["initial position"]["initial position{0}.height".format(position_index)])
                    player_id = parser["initial position"]["initial position{0}.player_id".format(position_index)]
                    _game_obj.board[(x, y)] = Tile(player_id=player_id,
                                                   height=height)

                    _game_obj.current_ui.debug("    ... {0},{1} (height={2}) : {3}".format(x, y, height, player_id))

                    position_index += 1

            # moves ............................................................
            _game_obj.current_ui.debug("  o reading the moves :")
            stop = False
            move_index = 0
            while not stop:
                if not parser.has_section("move"+str(move_index)):
                    stop = True
                else:
                    current_player_id = parser["move"+str(move_index)]["player_id"]
                    move = Move((int(parser["move"+str(move_index)]["x0"]),
                                 int(parser["move"+str(move_index)]["y0"])),
                                (int(parser["move"+str(move_index)]["x1"]),
                                 int(parser["move"+str(move_index)]["y1"])))
                    _game_obj.played_moves.append(move)
                    _game_obj.current_ui.debug("    ... move #{0} " \
                                               "by {1} : {2}".format(move_index,
                                                                     current_player_id,
                                                                     move))
                    _game_obj.board.apply_a_move(move)
                    _game_obj.compute_who_plays_the_next_move()

                    move_index += 1

            _game_obj.current_ui.debug("    ... no more moves to read.")

            # results ..........................................................
            if parser.has_section("results"):
                _game_obj.current_ui.debug("  o a 'results' section exists.")
                _game_obj.game_over = True

        except BaseException:
            res = False

        return res

    #///////////////////////////////////////////////////////////////////////////
    def name(self):
        """
                GameBackupFile.name()
        """
        return self.srcfile.name

    #///////////////////////////////////////////////////////////////////////////
    def open(self,
             filename,
             mode='r'):
        """
                GameBackupFile.open()
        """
        self.srcfile = open(file=filename,
                            mode=mode)
        return self

    #///////////////////////////////////////////////////////////////////////////
    def write(self, data):
        """
                GameBackupFile.write()
        """
        self.srcfile.write(data)

    #///////////////////////////////////////////////////////////////////////////
    def write_a_board(self, board_object):
        """
                GameBackupFile.write_a_board()

                Write the board <board_object> in the backup file.
        """
        if CONFIGPARSER["game.backup file"]["add comments"] != "True":
            return

        symbs = CONFIGPARSER["game.backup file"]["console symbols for players"]
        self.srcfile.write(GameBackupFile.COMMENT_PREFIX + \
                           get_board_textrepr(board_object=board_object,
                                              add_ansi_colors=False,
                                              console_symbols_for_players=symbs,
                                              console_colors_for_players=None,
                                              startstring=GameBackupFile.COMMENT_PREFIX) + \
                           "\n")

        self.flush() # since it's a backupfile, we force the writing.

    #///////////////////////////////////////////////////////////////////////////
    def write_a_move(self, move_number, move, player_id):
        """
                GameBackupFile.write_a_move()

                Write the <move> played by <player_id> in the backup file.
        """
        if CONFIGPARSER["game.backup file"]["add comments"] == "True":
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       "."*17 + \
                       "\n")

        self.write("[move{0}]\n".format(move_number))
        self.write("player_id={0}\n".format(player_id))
        self.write("x0={0}\n".format(move.x0))
        self.write("y0={0}\n".format(move.y0))
        self.write("x1={0}\n".format(move.x1))
        self.write("y1={0}\n".format(move.y1))

        self.flush() # since it's a backupfile, we force the writing.

    #///////////////////////////////////////////////////////////////////////////
    def write_new_turn(self, gameturn):
        """
                GameBackupFile.write_new_turn()

                write the turn number in the backup file
        """
        if CONFIGPARSER["game.backup file"]["add comments"] == "True":
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       "%%% turn #{0:03d} %%%".format(gameturn) + \
                       "\n\n")

        self.flush() # since it's a backupfile, we force the writing.

    #///////////////////////////////////////////////////////////////////////////
    def write_the_gains(self, winners, sorted_gains):
        """
                GameBackupFile.write_the_gains
        """
        if CONFIGPARSER["game.backup file"]["add comments"] == "True":
            table = Texttable()
            table.set_cols_dtype(['t', 'i'])
            table.set_cols_align(["l", "m"])
            rows = [["player", "gain"]]
            for player_id, gain in sorted_gains:
                rows.append([player_id, gain])
            table.add_rows(rows)
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       "=== results ===\n\n")
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       str("\n"+GameBackupFile.COMMENT_PREFIX).join(table.draw().split("\n")))
            self.write("\n")

        self.write("[results]\n")
        self.write("winners_number={0}\n".format(len(winners)))
        for i, winner_id in enumerate(winners):
            self.write("winner{0}={1}\n".format(i, winner_id))

        self.flush() # since it's a backupfile, we force the writing.

    #///////////////////////////////////////////////////////////////////////////
    def write_the_settings(self, players, initial_number_of_tokens):
        """
                GameBackupFile.write_the_settings()

                Write the first lines of the backup file
        """
        if CONFIGPARSER["game.backup file"]["add comments"] == "True":
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       "=== {0} game ({1}) ===\n".format(NAME_OF_THE_PROJECT,
                                                         datetime.now().strftime("%Y.%m.%d %H:%M:%S")))

            self.write("\n")

            self.write(GameBackupFile.COMMENT_PREFIX + "%%% settings %%%\n")
            self.write(GameBackupFile.COMMENT_PREFIX + "\n")
            table = Texttable()
            table.set_cols_dtype(['t', 'i'])
            table.set_cols_align(["l", "m"])
            rows = [["player", "nature"]]
            for player_id in players:
                rows.append([player_id, players[player_id].nature])
            table.add_rows(rows)
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       str("\n"+GameBackupFile.COMMENT_PREFIX).join(table.draw().split("\n")))
            self.write("\n")

        self.write("[settings]\n")
        self.write("players_number={0}\n".format(len(players)))
        for i, player_id in enumerate(players):
            self.write("player{0}.player_id={1}\n".format(i, player_id))
            self.write("player{0}.nature={1}\n".format(i, players[player_id].nature))
        self.write("initial_number_of_tokens={0}".format(initial_number_of_tokens))

        self.write("\n\n")

        self.flush() # since it's a backupfile, we force the writing.

    #///////////////////////////////////////////////////////////////////////////
    def write_the_initial_position(self, _board_object):
        """
                GameBackupFile.write_the_initial_position()

                Write the first position (before any move) into the backup file.
        """
        if CONFIGPARSER["game.backup file"]["add comments"] == "True":
            self.write(GameBackupFile.COMMENT_PREFIX + \
                       " %%% initial position %%%" + \
                       "\n\n")
            self.write_a_board(_board_object)

        self.write("[initial position]\n")
        for i, xy in enumerate(_board_object):
            self.write("initial position{0}.player_id={1}\n".format(i, _board_object[xy].player_id))
            self.write("initial position{0}.x={1}\n".format(i, xy[0]))
            self.write("initial position{0}.y={1}\n".format(i, xy[1]))
            self.write("initial position{0}.height={1}\n".format(i, _board_object[xy].height))

        self.write("\n")

        self.flush() # since it's a backupfile, we force the writing.
