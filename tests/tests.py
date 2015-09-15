#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
#    Katal Copyright (C) 2012 Suizokukan
#    Contact: suizokukan _A.T._ orange dot fr
#
#    This file is part of Katal.
#    Katal is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Katal is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Katal.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
       Katal by suizokukan (suizokukan AT orange DOT fr)

       tests.py
"""

import os
from collections import namedtuple
import unittest

import katal
katal.ARGS = namedtuple("ARGS", ("configfile", "mute",))

class Tests(unittest.TestCase):
	def test__fill_select(self):
		katal.ARGS.configfile=os.path.join("tests", "cfgfile1.ini")
		katal.PARAMETERS = katal.get_parameters_from_cfgfile(katal.ARGS.configfile)
		katal.read_sieves()
		katal.fill_select()

		self.assertEqual(len(katal.SELECT), 1)
		self.assertTrue("O2TblctVx2M5HHBxCEia4YtBEteDMA3jjgM7TJjD3q8=" in katal.SELECT)
		self.assertEqual(katal.SELECT["O2TblctVx2M5HHBxCEia4YtBEteDMA3jjgM7TJjD3q8="].complete_name, 
				         os.path.join("tests","data1","b.2"))
