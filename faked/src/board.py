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
    ❏Capri❏ : ./capri/board.py

    Board class
"""

MAXIMAL_DISTANCE_FROM_0_0 = 32
MAXIMAL_X = MAXIMAL_DISTANCE_FROM_0_0
MAXIMAL_Y = MAXIMAL_DISTANCE_FROM_0_0
MINIMAL_X = -MAXIMAL_DISTANCE_FROM_0_0
MINIMAL_Y = -MAXIMAL_DISTANCE_FROM_0_0

import base64
import copy
import hashlib
from capri.tile import Tile
from capri.move import Move

#///////////////////////////////////////////////////////////////////////////////
def init_distance_and_circle():
    """
            init_distance_and_circle()

            ____________________________________________________________________

            RETURN VALUES : two dicts described infra used to initialize
                            Board.distance_from_0_0 and Board.circle_around_0_0.

            o distance_from_0_0 : (dict) { (x,y) : (int) distance }
            o circle_around_0_0 : (dict) { (int) distance : [ (x1, y1), (x2, y2), ...]
    """
    _distance_from_0_0 = dict()
    _circle_around_0_0 = dict()

    for distance in range(1, MAXIMAL_DISTANCE_FROM_0_0+1):
        _circle_around_0_0[distance] = []

        # Since order matters, there are 6 loops and not one unique loop.
        # The first loop deals with segment #1, the second loop with segment #2, etc.
        for index in range(distance):
            # (0, -5), (1, -5), (2, -4), (3, -4), (4, -3)
            xy = (index,
                  -distance + int(index/2))
            _circle_around_0_0[distance].append(xy)
            _distance_from_0_0[xy] = distance

        for index in range(distance):
            # (5, -3), (5, -2), (5, -1), (5, 0),  (5, 1)
            xy = (distance,
                  -int((distance-1)/2) -1 + index)
            _circle_around_0_0[distance].append(xy)
            _distance_from_0_0[xy] = distance

        for index in range(distance):
            # (5, 2),  (4,3),   (3,3),   (2,4),   (1, 4)
            xy = (distance - index,
                  int(distance/2) + int((index+(distance%2))/2))
            _circle_around_0_0[distance].append(xy)
            _distance_from_0_0[xy] = distance

        for index in range(distance):
            # (0, 5),  (-1,4),  (-2,4),  (-3,3),  (-4, 3)
            xy = (-index,
                  distance - int((index+1)/2))
            _circle_around_0_0[distance].append(xy)
            _distance_from_0_0[xy] = distance

        for index in range(distance):
            # (-5, 2),  (-5,  1), (-5, 0),  (-5, -1), (-5, -2)
            xy = (-distance,
                  int(distance/2) - index)
            _circle_around_0_0[distance].append(xy)
            _distance_from_0_0[xy] = distance

        for index in range(distance):
            # (-5, -3) (-4, -3), (-3, -4), (-2, -4), (-1, -5)
            xy = (-distance+index,
                  -distance + int((distance-index)/2))
            _circle_around_0_0[distance].append(xy)
            _distance_from_0_0[xy] = distance

    return (_distance_from_0_0,
            _circle_around_0_0)

################################################################################
class Board(dict):
    """
        Board class : a dictionary of tile.

        A dictionary of (x,y):Tile object

        The first player which has to play IS NOT THE FIRST item in self.players_id

        ________________________________________________________________________

        E.g. here are four tiles (a,b,c,d) :

           -01 +00 +01 +02
        +02 .   .   .   .+02            (0,0) : a
                   ddd                  (1,0) : b
                  ddddd                 (0,1) : c
               ccc ddd                  (1,1) : d
        +01 . ccccc .   .+01
               ccc bbb
                  bbbbb
               aaa bbb
        +00 . aaaaa .   .+00
               aaa


        -01 .   .   .   .-01



        -02 .   .   .   .-02

           -01 +00 +01 +02
    """

    # dicts initialized by self.init_distance_and_circle() :
    distance_from_0_0, circle_around_0_0 = init_distance_and_circle()

    #///////////////////////////////////////////////////////////////////////////
    def  __init__(self, players_id=None):
        """
                Board.__init__()
                ________________________________________________________________

                PARAMETER :

                o players_id    : list of strings
                                  If players_id is None, it should be initialized
                                  later, e.g. by calling .set_players_id_from_the_board()
        """
        dict.__init__(self)

        self.players_id = players_id    # see self.set_players_id_from_the_board() method

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                Board.__repr__()

                see Board.*digest*() functions for another way to repr(esent) the
                object trough a string.

                This function DOES NOT GIVE A HUMAN REPRESENTATION of the board.
                See e.g. UILinuxConsole.get_console_repr_of_board() if you want
                something like a human representation.

                ________________________________________________________________

                RETURN VALUE : the expected string representing the data in self.
        """
        return str(self.players_id) + " : " + self.board_repr__no_other_infos()

    #///////////////////////////////////////////////////////////////////////////
    def apply_a_dxdy_translation(self, dx, dy):
        """
                Board.apply_a_dxdy_translation()

                apply a translation to all tiles : add (dx,dy) to all (x,y)

                ________________________________________________________________

                PARAMETERS : (int)dx, (int)dy
                ________________________________________________________________

                The translation keeps the form of the tiles :

                E.g.
                                          (dx,dy) = (+1, -1)
                        (original tiles)       ----->                  (final tiles)

                   -01 +00 +01 +02 +03                             +00 +01 +02 +03 +04
                +01 .   .   .   .   .+01                        +00 .   .   .   .   .+00
                           ▢▢▢
                          ▢002▢
                       ▼▼▼ ▢▢▢ ▨▨▨                                         ▢▢▢
                +00 . ▼001▼ . ▨003▨ .+00                        -01 .   . ▢002▢ .   .-01
                       ▼▼▼ ■■■ ▨▨▨                                     ▼▼▼ ▢▢▢ ▨▨▨
                          ■001■                                       ▼001▼   ▨003▨
                           ■■■                                         ▼▼▼ ■■■ ▨▨▨
                -01 .   .   .   .   .-01                        -02 .   . ■001■ .   .-02
                           ■■■                                             ■■■
                          ■001■
                           ■■■                                             ■■■
                -02 .   .   .   .   .-02                        -03 .   . ■001■ .   .-03
                           ■■■                                             ■■■
                          ■001■
                           ■■■                                             ■■■
                -03 .   .   .   .   .-03                        -04 .   . ■001■ .   .-04
                                                                           ■■■
                   -01 +00 +01 +02 +03                             +00 +01 +02 +03 +04

        """
        # this test prevents an error : without this test the code would wrongly
        # compute a translation with (+0,+0), see below.
        if dx == 0 and dy == 0:
            return

        old_tiles = self.clone()

        # we clear the board (not the players or whatsoever in self)
        dict.clear(self)

        for (x, y) in old_tiles:

            x_plus_dx = x + dx
            y_plus_dy = y + dy

            if x_plus_dx%2 != 0:
                y_plus_dy -= 1

            self[(x_plus_dx, y_plus_dy)] = old_tiles[(x, y)]

    #///////////////////////////////////////////////////////////////////////////
    def apply_dz(self, dz):
        """
                Board.apply_dz()

                add dz to all heights
                ________________________________________________________________

                PARAMETER : (int)dz
        """
        for (x, y) in self:
            self[(x, y)].height += dz

    #///////////////////////////////////////////////////////////////////////////
    def apply_a_60_degrees_rotation(self):
        """
                Board.apply_a_60_degrees_rotation()

                ________________________________________________________________

                E.g. :

                                          60° rot.
                        (original tiles)  ------->      (final tiles)

                   -01 +00 +01 +02 +03             -01 +00 +01 +02 +03 +04
                +01 .   .   .   .   .+01        +02 .   .   .   .   .   .+02
                           ▢▢▢                             ▨▨▨
                          ▢002▢                           ▨003▨
                       ▼▼▼ ▢▢▢ ▨▨▨                     ▢▢▢ ▨▨▨
                +00 . ▼001▼ . ▨003▨ .+00        +01 . ▢002▢ .   .   .   .+01
                       ▼▼▼ ■■■ ▨▨▨                     ▢▢▢ ■■■
                          ■001■                           ■001■
                           ■■■                         ▼▼▼ ■■■ ■■■
                -01 .   .   .   .   .-01        +00 . ▼001▼ . ■001■ .   .+00
                           ■■■                         ▼▼▼     ■■■ ■■■
                          ■001■                                   ■001■
                           ■■■                                     ■■■
                -02 .   .   .   .   .-02        -01 .   .   .   .   .   .-01
                           ■■■
                          ■001■
                           ■■■
                -03 .   .   .   .   .-03        -02 .   .   .   .   .   .-02
                   -01 +00 +01 +02 +03             -01 +00 +01 +02 +03 +04

        """
        old_tiles = self.clone()

        # we clear the board (not the players or whatsoever in self)
        dict.clear(self)

        # rotation :
        for (x, y) in old_tiles:

            if (x, y) == (0, 0):
                new_x, new_y = (0, 0)
            else:
                distance = Board.distance_from_0_0[x, y]
                circle = Board.circle_around_0_0[distance]
                index = circle.index((x, y))
                new_x, new_y = circle[(index + distance)%(6*distance)]

            self[(new_x, new_y)] = old_tiles[(x, y)]

    #///////////////////////////////////////////////////////////////////////////
    def apply_a_move(self, move):
        """
                Board.apply_a_move()

                Apply the <move> on the board, the move being or not correct.

                ________________________________________________________________

                PARAMETERS :
                o move : a Move object
                no return value
        """
        source_tile = (move.x0, move.y0)
        destination_tile = (move.x1, move.y1)

        self[destination_tile].height += self[source_tile].height
        self[destination_tile].player_id = self[source_tile].player_id

        del self[source_tile]

    #///////////////////////////////////////////////////////////////////////////
    def clear(self):
        """
                Board.clear()

                Clear the board and the players.
                ________________________________________________________________

                no return value
        """
        dict.clear(self)
        if self.players_id is not None:
            self.players_id.clear()

    #///////////////////////////////////////////////////////////////////////////
    def clone(self):
        """
                Board.clone()
                ________________________________________________________________

                RETURN VALUE : a Board object
        """
        res = Board()
        res.players_id = copy.copy(self.players_id)

        for (x, y) in self:
            res[(x, y)] = copy.copy(self[(x, y)])

        return res

    #///////////////////////////////////////////////////////////////////////////
    def compare_after_normalization(self, aliud):
        """
                Board.compare_after_normalization()

                Compare self and (Board)aliud, both being normalized for the
                comparison.
                ________________________________________________________________

                PARAMETER :
                o aliud : Board object

                RETURN VALUE :
                o True if self and aliud are equal.
                ________________________________________________________________

                NB : I tried to speed up the code by calling self.essential_digest()
                     to compare the tiles after each rotation. The code was
                     slighlty slower. (2015, January)
        """
        _self = self.clone()
        _self.normalize()

        _aliud = aliud.clone()
        _aliud.normalize()

        equality = False
        for _ in range(5):      # _ : rotation number

            equality = True
            for (x, y) in _self:
                if (x, y) not in _aliud:
                    equality = False
                    break
                elif _self[(x, y)] != _aliud[(x, y)]:
                    equality = False

            for (x, y) in _aliud:
                if (x, y) not in _self:
                    equality = False
                    break
                elif _aliud[(x, y)] != _self[(x, y)]:
                    equality = False

            if equality:
                break
            else:
                # let's try with a rotated '_self' :
                _self.apply_a_60_degrees_rotation()

        return equality

    #///////////////////////////////////////////////////////////////////////////
    def copy(self):
        """
                Board.copy()

                Return a copied version of self.
        """
        res = Board(players_id=self.players_id.copy())
        for xy in self:
            res[xy]=self[xy].copy()
        return res

    #///////////////////////////////////////////////////////////////////////////
    def equ_through_essen_digest_to(self, aliud):
        """
                Board.equ_through_essen_digest_to()
                        -> is equivalent through essential digest to <aliud>.

                Return True if self and aliud are identical through their
                essential digest.
                ________________________________________________________________

                PARAMETER       : (Board)aliud
                RETURN VALUE    : a bool
        """
        d_self = self.essential_digests__nversions(digest_type=None)
        d_aliud = aliud.essential_digests__nversions(digest_type=None)
        return len(set(d_self) & set(d_aliud)) > 0

    #///////////////////////////////////////////////////////////////////////////
    def essential_digest(self, digest_type=None):
        """
                Board.essential_digest()

                Return the digest message of the (essential) parts of the object.
                "Essential" means "only the tiles=heights+players'ids" .
                ________________________________________________________________

                PARAMETER :
                o digest_type : if None, return a bytes object; if "base64" return an
                                hexadecimal string; if "base64" return a string made
                                of 64 characters (0-9, a-z, A-Z, /, =)

                RETURN VALUE :
                o either a string (digest!=None, either a bytes object)
        """
        data = hashlib.md5(self.board_repr__no_other_infos().encode())

        if digest_type is None:
            return data.digest()
        elif digest_type=="base16":
            return data.hexdigest()
        elif digest_type=="base64":
            return base64.b64encode(data.digest()).decode()
        else:
            # todo : error
            pass

    #///////////////////////////////////////////////////////////////////////////
    def essential_digests__nversions(self, digest_type=None):
        """
                Board.essential_digests__nversions()
                        -> essential digests of the normalized versions
                ________________________________________________________________

                PARAMETER :
                o digest_type : None or a string; see Board.essential_digest()

                RETURN VALUE :
                o either a list of strings (digest!=None), either a list of
                  bytes object (digest=None).
        """
        res = []

        _self = self.clone()

        res.append(_self.essential_digest(digest_type))

        _self.apply_a_60_degrees_rotation()
        res.append(_self.essential_digest(digest_type))

        _self.apply_a_60_degrees_rotation()
        res.append(_self.essential_digest(digest_type))

        _self.apply_a_60_degrees_rotation()
        res.append(_self.essential_digest(digest_type))

        _self.apply_a_60_degrees_rotation()
        res.append(_self.essential_digest(digest_type))

        _self.apply_a_60_degrees_rotation()
        res.append(_self.essential_digest(digest_type))

        return res

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def find_a_connection_betw_2_isl(island1, island2):
        """
                Board.find_a_connection_betw_2_isl()
                        -> find a connection between two islands

                Return True if there's (at lease) one tile of island1 connected to
                a tile of island2.

                ________________________________________________________________

                PARAMETERS :
                o island1, island2 : Board object with only one island per Board
                                     object.

                RETURN VALUE : a boolean
        """
        res = False

        for x1y1 in island1:
            around_x1y1 = Board.get_tiles_coordinates_around(x1y1)

            for x2y2 in island2:
                for _x1y1 in around_x1y1:

                    if _x1y1 == x2y2:
                        # (x2, y2) is connected to island1 :
                        res = True
                        break

                if res:
                    break

            if res:
                break

        return res

    #///////////////////////////////////////////////////////////////////////////
    def get_gains(self):
        """
                Board.get_gains()

                Return the gains for each player; if no more move can be played,
                the result is the final gain of the game.
                ________________________________________________________________

                RETURN VALUE : a dict { (str)player_id : (int)gain }
        """
        res = {key : 0 for key in self.players_id}

        for xy in self:
            res[self[xy].player_id] += self[xy].height

        return res

    #///////////////////////////////////////////////////////////////////////////
    def get_islands(self):
        """
                Board.get_islands()
                ________________________________________________________________

                RETURN VALUE : a list of Board objects
        """

        # 1/ the function roughly groups the tiles into islands :
        #
        # the following loop is very imperfect and divide the tiles into
        # many small islands which are in fact connected.
        res = []

        for (x, y) in sorted(self.keys()):

            if len(res) == 0:
                # let's add (x, y) in a first Board object :
                res.append(Board())
                res[-1][(x, y)] = self[(x, y)]

            else:
                connected = False

                for island in res:
                    if island.search_which_tile_is_connec_to((x, y))[0]:
                        island[(x, y)] = self[(x, y)]
                        connected = True
                        break

                if not connected:
                    res.append(Board())
                    res[-1][(x, y)] = self[(x, y)]

        # 2/ the function groups the islands if they are connected :
        index_of_the_connected_islands = [-1, -1]
        go_on = True
        while go_on == True:

            # will be set to True only if two islands are connected :
            go_on = False

            for index1, island1 in enumerate(res):
                for index2, island2 in enumerate(res):
                    if index1 != index2:

                        if self.find_a_connection_betw_2_isl(island1, island2):

                            # island1, island2 are connected :
                            go_on = True
                            index_of_the_connected_islands = [index1, index2]
                            break

                if go_on:
                    break

            if go_on:
                # let's copy island1 into island2:
                index1, index2 = index_of_the_connected_islands
                for (x, y) in res[index1]:
                    res[index2][(x, y)] = res[index1][(x, y)]

                # removing island1 :
                res.pop(index1)

        return res

    #///////////////////////////////////////////////////////////////////////////
    def get_min_max_heights(self):
        """
                Board.get_min_max_heights()

                return (zmin, zmax)
                ________________________________________________________________

                RETURN VALUE : ( (int)zmin, (int)zmax )
        """
        assert len(self) > 0

        zmin = 999999
        zmax = -999999

        for (x, y) in self:
            height = self[(x, y)].height

            if height < zmin:
                zmin = height

            elif height > zmax:
                zmax = height

        return (zmin, zmax)

    #///////////////////////////////////////////////////////////////////////////
    def get_min_max_positions(self):
        """
                Board.get_min_max_positions()

                return (xmin, ymin, xmax, ymax)
                ________________________________________________________________

                RETURN VALUE : ( (int)xmin, (int)ymin, (int)xmax, (int)ymax)
        """
        assert len(self) > 0

        xmin = 999999
        ymin = 999999
        xmax = -999999
        ymax = -999999

        for (x, y) in self:
            if x < xmin:
                xmin = x
            if y < ymin:
                ymin = y
            if x > xmax:
                xmax = x
            if y > ymax:
                ymax = y

        return (xmin, ymin, xmax, ymax)

    #///////////////////////////////////////////////////////////////////////////
    def get_the_moves_a_player_may_play(self, player_id):
        """
                Board.get_the_moves_a_player_may_play()

                Return a list of the moves that player_id may play.
                ________________________________________________________________

                PARAMETER : (str) player_id
                RETURN VALUE : a list of Moves object
        """
        res = []

        for xy in self:
            if self[xy].player_id == player_id:
                for around in self.get_tiles_coordinates_around(xy):

                    if around in self and self[around].height <= self[xy].height:
                        res.append(Move((xy, around)))

        return res

    #///////////////////////////////////////////////////////////////////////////
    def get_tiles_belonging_to_player(self, player_id):
        """
                Board.get_tiles_belonging_to_player()

                Return the tiles belonging to the player named player_id.
                ________________________________________________________________

                PARAMETER : (str)player_id
                RETURN VALUE : a Board object avec a players_id containing only
                               one player_id .
        """
        res = Board()

        for (x, y) in self:

            if self[(x, y)].player_id == player_id:
                res[(x, y)] = copy.copy(self[(x, y)])

        res.set_players_id_from_the_board()

        return res

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def get_tiles_coordinates_around(xy):
        """
                Board.get_tiles_coordinates_around()

                Return the coordinates of the tiles aroud the (x,y) tile.
                ________________________________________________________________

                PARAMETERS : (int)x, (int)y
                RETURN VALUE : a list of ( xy1, xy2, ... ) where xy = (int x, int y)
        """

        x = xy[0]
        y = xy[1]

        if x%2 == 0:
            return (
                (x-1, y-1),     # (2,1) -> (1,0)
                (x-1, y),       # (2,1) -> (1,1)
                (x, y+1),       # (2,1) -> (2,2)
                (x+1, y),       # (2,1) -> (3,1)
                (x+1, y-1),     # (2,1) -> (3,0)
                (x, y-1),       # (2,1) -> (2,0)
                )
        else:
            return (
                (x-1, y),       # (1,1) -> (0,1)
                (x-1, y+1),     # (1,1) -> (0,2)
                (x, y+1),       # (1,1) -> (1,2)
                (x+1, y+1),     # (1,1) -> (2,2)
                (x+1, y),       # (1,1) -> (2,1)
                (x, y-1),       # (1,1) -> (1,0)
                )

    #///////////////////////////////////////////////////////////////////////////
    def how_many_adjacent_tiles_around(self, xy):
        """
                Board.how_many_adjacent_tiles_around()

                Return the number of tiles existing around (xy).
        """
        number_of_adjacent_tiles = 0

        for xy_around in self.get_tiles_coordinates_around((xy[0], xy[1])):
            if xy_around in self:
                number_of_adjacent_tiles += 1

        return number_of_adjacent_tiles

    #///////////////////////////////////////////////////////////////////////////
    def is_the_game_over(self):
        """
                Board.is_the_game_over()

                Return True if no player has a move to play.
        """
        one_more_move_can_be_played = False
        for player_id in self.players_id:
            if len(self.get_the_moves_a_player_may_play(player_id)) > 0:
                one_more_move_can_be_played = True
                break

        return not one_more_move_can_be_played

    #///////////////////////////////////////////////////////////////////////////
    def is_it_a_correct_move(self, move):
        """
                Board.is_it_a_correct_move()

                Return a boolean : True if the <move> may be played, False
                                   otherwise.

                ________________________________________________________________

                PARAMETER :
                o move : a Move object.

                RETURN VALUE : the expected boolean

        """
        around_x0y0 = self.get_tiles_coordinates_around((move.x0, move.y0))

        if (move.x0, move.y0) not in self or (move.x1, move.y1) not in self:
            return False

        if (move.x1, move.y1) not in around_x0y0:
            return False

        if self[(move.x0, move.y0)].height < self[(move.x1, move.y1)].height:
            return False

        return True

    #///////////////////////////////////////////////////////////////////////////
    def normalize(self):
        """
                Board.normalize()

                Modify self to allow comparisons between Board objects.

                0/ if the object is empty, nothing to do.
                1/ players_id become "0", "1", "2", "3", ...
                2/ tiles are centered around (0,0)
                3/ heights are lowered if there's only ony island
        """
        # 0/ if the object is empty, nothing to do.
        if len(self) == 0:
            return

        # 1/ players_id become "0", "1", "2", "3", ...
        if self.players_id is not None:

            # translation dict :
            ancient_to_old_players_id = dict()
            for index, player_id in enumerate(self.players_id):
                ancient_to_old_players_id[player_id] = str(index)

            # modification in the tiles :
            for (x, y) in self:
                self[(x, y)].player_id = ancient_to_old_players_id[self[(x, y)].player_id]

            # modifications in self.players_id :
            self.players_id = [str(index) for index in range(0, len(self.players_id))]

        # 2/ tiles are centered around (0,0)
        dx = 0
        dy = 0
        for (x, y) in self:
            dx += x
            dy += y
        dx = int(dx / len(self))
        dy = int(dy / len(self))

        self.apply_a_dxdy_translation(-dx, -dy)

        # 3/ heights are lowered if there's only ony island
        if len(self.get_islands()) == 1:
            zmin = self.get_min_max_heights()[0]
            self.apply_dz(-(zmin-1))

    #///////////////////////////////////////////////////////////////////////////
    def search_which_tile_is_connec_to(self, xy0):
        """
                Board.search_which_tile_is_connec_to()

                Return the first tile found in self having a connection with (x0, y0).
                ________________________________________________________________

                PARAMETERS   : (int)x0, (int)y0
                RETURN VALUE : ( (bool)is connected, x1, y1)
        """
        res = (False, None, None)

        x0 = xy0[0]
        y0 = xy0[1]

        for x1y1 in self:

            coordinates_around = self.get_tiles_coordinates_around(x1y1)
            for (x_around, y_around) in coordinates_around:
                if x_around == x0 and y_around == y0:
                    res = (True, x1y1)
                    break
            if res[0]:
                break

        return res

    #///////////////////////////////////////////////////////////////////////////
    def set_a_tile(self, xy, player_id, height):
        """
                Board.set_a_tile()

                Initialize a non-yet-defined tile.
                ________________________________________________________________

                PARAMETERS :
                o xy            : ( (int)x, (int)y )
                o player_id     : str
                o height        : int
        """
        assert xy[0] >= MINIMAL_X and xy[0] <= MAXIMAL_X and xy[1] >= MINIMAL_Y and xy[1] <= MAXIMAL_Y
        assert xy not in self
        assert player_id in self.players_id
        assert height > 0

        self[xy] = Tile(player_id=player_id,
                        height=height)

    #///////////////////////////////////////////////////////////////////////////
    def set_players_id_from_the_board(self):
        """
                Board.set_players_id_from_the_board()

                Fill self.players_id by reading the tiles' content.
        """
        self.players_id = []

        for (x, y) in self:
            if self[(x, y)].player_id not in self.players_id:
                self.players_id.append(self[(x, y)].player_id)

    #///////////////////////////////////////////////////////////////////////////
    def board_repr__no_other_infos(self):
        """
                Board.board_repr__no_other_infos()

                Return a string with all informations about each tile :
                (x,y):player_id:height

                Other informations (e.g. the name of the players id) are not added
                to the returned string.
                ________________________________________________________________

                RETURN VALUE : a string
        """
        res = []
        for (x, y) in self:
            res.append("({0},{1})={2}+{3}".format(x, y, self[(x, y)].player_id, self[(x, y)].height))

        return ";".join(res)

    #///////////////////////////////////////////////////////////////////////////
    def who_is_the_winner(self):
        """
                Board.who_is_the_winner

                if self.is_the_game_over()==True, return a list of the player_id(s)
                having the best gain.
        """
        # if not self.is_the_game_over():
        #     # todo : error
        #     pass

        res = []

        gains = self.get_gains()
        maximal_gain = -1

        for player_id in self.players_id:
            if gains[player_id] > maximal_gain:
                res = [player_id,]
                maximal_gain = gains[player_id]
            elif gains[player_id] == maximal_gain:
                res.append(player_id)

        return res