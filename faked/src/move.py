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
    ❏Capri❏ : capri/move.py
"""

################################################################################
class Move(object):
    """
        A move is either a null move (=None) either a real move from a point
        (x0, y0) to another point (x1, y1).
    """

    #///////////////////////////////////////////////////////////////////////////
    def __eq__(self, _move):
        """
                Move.__eq__()

                todo : cette fonction est peut-être inutile
        """
        return (self.x0 == _move.x0) and \
               (self.y0 == _move.y0) and \
               (self.x1 == _move.x1) and \
               (self.y1 == _move.y1)

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _xy0xy1=None):
        """
                Move.__init__()
        """
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None

        if _xy0xy1 is not None:
            self.x0 = _xy0xy1[0][0]
            self.y0 = _xy0xy1[0][1]
            self.x1 = _xy0xy1[1][0]
            self.y1 = _xy0xy1[1][1]

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                Move.__repr__()
        """
        if self.x0 is None:
            return "Move(no move)"
        else:
            return "Move({0},{1}),({2},{3})".format(self.x0,
                                                    self.y0,
                                                    self.x1,
                                                    self.y1)

    #///////////////////////////////////////////////////////////////////////////
    def is_null(self):
        """
                Move.is_null()
        """
        return self.x0 is None
