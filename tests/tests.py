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
# Pylint : disabling the "Class 'ARGS' has no 'configfile' member" error
#          since there IS a 'configfile' member for the ARGS class.
# pylint: disable=E1101

from collections import namedtuple
import os
import unittest

from katal import katal
katal.ARGS = namedtuple("ARGS", ("configfile", "mute", "targetpath",))
katal.ARGS.mute = True
katal.ARGS.targetpath = "tests"

################################################################################
class Tests(unittest.TestCase):
    """
        Tests class

	Testing the katal.py script
    """

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select1(self):
        """
		Tests.test__fill_select1()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile1.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.SOURCE_PATH = os.path.join("tests", "data1")
        katal.read_filters()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 1)

        # hashid of b.2 :
        hashid = 'fFsjifi6rXXQ7BEqBzrwKovKZGESFJAP+THGBqmCtyA='
        self.assertTrue(hashid in katal.SELECT)

   #//////////////////////////////////////////////////////////////////////////
    def test__fill_select2(self):
        """
		Tests.test__fill_select2()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile2.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.SOURCE_PATH = os.path.join("tests", "data1")
        katal.read_filters()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 2)

        # hashid of b.2 :
        hashid = "fFsjifi6rXXQ7BEqBzrwKovKZGESFJAP+THGBqmCtyA="
        self.assertTrue(hashid in katal.SELECT)

        # hashid of b.3 :
        hashid = "3yCV06Q93bvCGYVjiadtyRSdffL2Bz62S2YwcY9TfMI="
        self.assertTrue(hashid in katal.SELECT)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select3(self):
        """
		Tests.test__fill_select3()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile3.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.SOURCE_PATH = os.path.join("tests", "data1")
        katal.read_filters()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 5)

        # hashid of ddddX.6 :
        hashid = "D8CiKgUN5TgUbdon0KBqaXyjqSuG1G8n2a8iIamT3qQ="
        self.assertTrue(hashid in katal.SELECT)

        # hashid of c.5 :
        hashid = "nPuC9f72wvN6FGgAuL6VLEHVD77w3+Bri6IuRLzIzOw="
        self.assertTrue(hashid in katal.SELECT)

        # hashid of a.0 :
        hashid = "Bl9mkkkXB5xinUl/a0lAP5zHucJeTwAtd07OoEmvSOU="
        self.assertTrue(hashid in katal.SELECT)

        # hashid of ddddd.6 :
        hashid = "PvWbVu8eNHn1U5QWeBneT+90HeNL2ZpqXBd2XGmtZ30="
        self.assertTrue(hashid in katal.SELECT)

        # hashid of a.1 :
        hashid = "MXK7fPzl9feGlmmG0uzmKOOrjC3lFCa4imyFbDSpfqg="
        self.assertTrue(hashid in katal.SELECT)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select4(self):
        """
		Tests.test__fill_select4()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile4.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.SOURCE_PATH = os.path.join("tests", "data1")
        katal.read_filters()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 1)
        
        hashid = "PvWbVu8eNHn1U5QWeBneT+90HeNL2ZpqXBd2XGmtZ30="
        self.assertTrue(hashid in katal.SELECT)
        self.assertTrue(katal.SELECT[hashid].fullname, "ddddd.6")
