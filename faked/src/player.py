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
    ❏Capri❏ : capri/player.py

    PlayersList and Player classes
"""

################################################################################
class PlayersList(list):
    """
        PlayersList class
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, src):
        """
                PlayersList.__init__
        """
        list.__init__(self, src)

    #///////////////////////////////////////////////////////////////////////////
    def next(self, _player_id):
        """
                PlayersList.next()

                Return the player_id after <_player_id> or the first one if
                _player_id is the last one.
        """
        index=list.index(self, _player_id)
        if index+1<len(self):
            return self[index+1]
        else:
            return self[0]

################################################################################
class Player(object):
    """
        Player class :

        o self.nature           # int (see PLAYER_NATURE__* constants)
        o self.player_id        # str (e.g. "HAL", "Xavier", ...)
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _player_id, _nature):
        """
                Player.__init__()

                ________________________________________________________________

                PARAMETERS :
                o _player_id                    (str, see the class documentation)
                o _nature                       (int, see the class documentation)
        """
        self.nature = _nature           # see the class documentation
        self.player_id = _player_id     # see the class documentation

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                Player.__repr__()
                ________________________________________________________________

                RETURNED VALUE : the expected string describing self.

        """
        return "'{0}' (nature={1})".format(self.player_id, self.nature)
