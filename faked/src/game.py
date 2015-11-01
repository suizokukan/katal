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
    ❏Capri❏ : capri/game.py

    Game class
"""
from collections import OrderedDict
from capri.board import Board
from capri.constants import PLAYER_NATURE__HUMAN, \
                            PLAYER_NATURE__RANDOM
from capri.gamebackupfile import GameBackupFile
from capri.move import Move

import operator
import random

################################################################################
class Game(object):
    """
        Game class
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self,
                 _ui,
                 _initial_number_of_tokens=0,
                 _players=None,
                 _backup_file=None):
        """
                _players : a list of Player objects; the first player in the list plays the first.
        """
        self.current_ui = _ui

        self.initial_number_of_tokens = _initial_number_of_tokens

        self.players = OrderedDict()    # player_id : Player object
        if _players is not None:
            for player in _players:
                self.players[player.player_id] = player

        self.backup_file = _backup_file
        if _backup_file is None:
            self.current_ui.debug("no backup file.")
        else:
            self.current_ui.debug("backup file : "+self.backup_file.name())

        self.board = Board()
        self.board.players_id = list(self.players.keys())

        # (int, str) : player_id of the player who has to play to next move.
        #
        # the integer is the index in self.players matching player_id.
        #
        # e.g. (0, "HAL")
        #
        if _players is None:
            self.who_plays_the_next_move = []
        else:
            self.who_plays_the_next_move = [0, list(self.players.keys())[0]]

        self.game_over = False          # True when the game is over.
        self.current_gameturn = 0

        self.played_moves = []          # [((str)player_id, (Move)played move), ...]

    #///////////////////////////////////////////////////////////////////////////
    def begin(self):
        """
                Game.begin()

                Function to be called at the beginning of a game, just before
                the first move.
        """
        self.current_ui.debug("================")
        self.current_ui.debug("=== new game ===")
        self.current_ui.debug("================")
        self.current_ui.debug("players : "+repr(self.players))
        self.current_ui.debug("initial number of tokens : "+str(self.initial_number_of_tokens))

        self.current_gameturn = 1

        self.backup_file.write_the_settings(self.players, self.initial_number_of_tokens)
        self.backup_file.write_the_initial_position(self.board)
        self.backup_file.write_new_turn(self.current_gameturn)

    #///////////////////////////////////////////////////////////////////////////
    def compute_who_plays_the_next_move(self):
        """
                Game.compute_who_plays_the_next_move()

                Initialize self.who_plays_the_next_move and self.current_gameturn
                from the current state of self.
        """
        if self.who_plays_the_next_move[0]+1 != len(self.players):
            # let's go on with the next player :
            self.who_plays_the_next_move[0] += 1
            self.who_plays_the_next_move[1] = list(self.players.keys())[self.who_plays_the_next_move[0]]
        else:
            # we go on with the first player :
            self.who_plays_the_next_move = [0, list(self.players.keys())[0]]
            self.current_gameturn += 1

    #///////////////////////////////////////////////////////////////////////////
    def end(self):
        """
                Game.end()

                Function to be called at the end of a game, just after the last
                move.
        """
        self.current_ui.debug("=======================")
        self.current_ui.debug("=== end of the game ===")
        self.current_ui.debug("gains : ")

        sorted_gains = sorted(self.board.get_gains().items(), key=operator.itemgetter(1))
        sorted_gains.reverse()
        for player_id, gain in sorted_gains:
            self.current_ui.debug("  {0} : {1}".format(player_id, gain))

        self.current_ui.debug("winner(s) : " + str(self.board.who_is_the_winner()))
        self.current_ui.debug("number of turn(s) : "+str(self.current_gameturn))
        self.current_ui.debug("=======================")

        self.backup_file.write_the_gains(winners=self.board.who_is_the_winner(),
                                         sorted_gains=sorted_gains)

    #///////////////////////////////////////////////////////////////////////////
    def is_the_game_over(self):
        """
                Game.is_the_game_over()

                Initialize and return the content of self.game_over .
        """
        self.game_over = self.board.is_the_game_over()
        return self.game_over

    #///////////////////////////////////////////////////////////////////////////
    def load(self, _file_name):
        """
                Game.load()

                !! self.backup_file will not be modified.

                Load a backup file and initialize self from it.

                ________________________________________________________________

                RETURNED VALUE : a boolean (True if the file has been successfully
                                 loaded, False otherwhise)
        """
        self.current_ui.debug("Game.load() : loading a backup file from "+_file_name)

        # resetting some data :
        #
        #   NB : self.backup_file is not modified by this function.
        #
        self.initial_number_of_tokens = 0
        self.players = OrderedDict()
        self.board = Board()
        self.board.players_id = []
        self.game_over = False          # False if there's no section "results". See below.
        self.current_gameturn = 0
        self.played_moves = []          # a list of Move objects

        return GameBackupFile.load(_file_name=_file_name,
                                   _game_obj=self)

    #///////////////////////////////////////////////////////////////////////////
    def next_move(self):
        """
                Game.next_move()

                The player <self.who_plays_the_next_move> plays.
        """
        current_player = self.players[self.who_plays_the_next_move[1]]

        self.current_ui.debug("turn #{0}, current player being {1}".format(self.current_gameturn,
                                                                           current_player))

        if current_player.nature == PLAYER_NATURE__HUMAN:
            move = self.current_ui.your_move_please(_player_object=current_player,
                                                    _board_object=self.board,
                                                    _game=self)

            if not move.is_null():
                self.board.apply_a_move(move)

                self.backup_file.write_a_move(move_number=len(self.played_moves),
                                              move=move,
                                              player_id=current_player.player_id)
                self.backup_file.write_a_board(self.board)
                self.backup_file.write("\n")

                self.played_moves.append((current_player.player_id, move))

        elif current_player.nature == PLAYER_NATURE__RANDOM:
            moves = self.board.get_the_moves_a_player_may_play(current_player.player_id)

            len_moves = len(moves)
            if len_moves > 0:
                randomly_selected_move = moves[random.randrange(len_moves)]
                self.current_ui.message("Player {0} " \
                                        "randomly choosed to play {1}.".format(current_player,
                                                                               randomly_selected_move))
                self.board.apply_a_move(randomly_selected_move)

                self.backup_file.write_a_move(move_number=len(self.played_moves),
                                              move=randomly_selected_move,
                                              player_id=current_player.player_id)
                self.backup_file.write_a_board(self.board)
                self.backup_file.write("\n")

                self.played_moves.append((current_player.player_id, randomly_selected_move))

                self.current_ui.pause_to_see_the_last_move()
            else:
                self.current_ui.message("Player {0} can't play.".format(current_player))

        else:
            # todo : error
            pass

        # next player ?
        self.compute_who_plays_the_next_move()

        if self.who_plays_the_next_move[0] == 0:
            self.backup_file.write_new_turn(self.current_gameturn)

    #///////////////////////////////////////////////////////////////////////////
    def set_randomly_the_initial_pos(self):
        """
                Game.set_randomly_the_initial_pos()

                    -> set randomly the initial position for the current players

                set the initial position on self.board according to self.players
        """
        self.board.clear()
        self.board.players_id = [player_id for player_id in self.players]

        number_of_players = len(self.players)

        # first token :
        if number_of_players == 2:
            self.board.set_a_tile(xy=(0, 0), player_id=self.board.players_id[0], height=1)
            self.board.set_a_tile(xy=(1, 0), player_id=self.board.players_id[1], height=1)

        elif number_of_players == 3:
            self.board.set_a_tile(xy=(0, 0), player_id=self.board.players_id[0], height=1)
            self.board.set_a_tile(xy=(1, 0), player_id=self.board.players_id[1], height=1)
            self.board.set_a_tile(xy=(0, 1), player_id=self.board.players_id[2], height=1)

        elif number_of_players == 4:
            self.board.set_a_tile(xy=(0, 0), player_id=self.board.players_id[0], height=1)
            self.board.set_a_tile(xy=(1, 0), player_id=self.board.players_id[1], height=1)
            self.board.set_a_tile(xy=(0, 1), player_id=self.board.players_id[2], height=1)
            self.board.set_a_tile(xy=(1, 1), player_id=self.board.players_id[3], height=1)

        else:
            # $$$ todo :error
            pass

        # other tokens :
        # ... for each player, for each token to be put on the board ...
        for _ in range(1, self.initial_number_of_tokens):       # _ : token_number
            for player_id in self.players:

                # ... we get all the available coordinates where the player could put a token :
                available_xy = []

                for xy_center in self.board:
                    for xy in self.board.get_tiles_coordinates_around(xy_center):
                        # if xy is free and is connected to (at least) two other tokens, it's ok :
                        if xy not in self.board and self.board.how_many_adjacent_tiles_around(xy) >= 2:
                            available_xy.append(xy)

                # ... and we choose randomly the coordinates :
                self.board.set_a_tile(xy=available_xy[random.randrange(len(available_xy))],
                                      player_id=player_id,
                                      height=1)
