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
    ❏Capri❏ : ./capri/tile.py

    Tile class
"""

################################################################################
class Tile(object):
    """
        Tile object :
                self.player_id (str)
                self.height (int >= 0)
    """

    #///////////////////////////////////////////////////////////////////////////
    def __eq__(self, aliud):
        """
                Tile.__eq__()

                Compare self with (Tile)'aliud'.

                ________________________________________________________________

                RETURN VALUE : a boolean.
        """
        return (self.player_id == aliud.player_id) and (self.height == aliud.height)

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, player_id, height):
        """
                Tile.__init__()

                ________________________________________________________________

                PARAMETERS :
                o player_id     : (str)
                o height        : (int)>=0
        """
        self.player_id = player_id
        self.height = height

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                Tile.__repr__()
        """
        return "Tile::player_id={0}+height={1}".format(self.player_id,
                                                       self.height)

    #///////////////////////////////////////////////////////////////////////////
    def copy(self):
        """
                Tile.copy()

                Return a copied version of self.
        """
        return Tile(player_id=self.player_id,
                    height=self.height)
