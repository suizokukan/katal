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

from datetime import datetime
import os
from collections import namedtuple
import unittest

from katal import katal
katal.ARGS = namedtuple("ARGS", ("configfile", "mute",))

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
        katal.read_sieves()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 1)

        hashid = "O2TblctVx2M5HHBxCEia4YtBEteDMA3jjgM7TJjD3q8="
        self.assertTrue(hashid in katal.SELECT)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select2(self):
        """
		Tests.test__fill_select2()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile2.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.read_sieves()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 1)

        hashid = "O2TblctVx2M5HHBxCEia4YtBEteDMA3jjgM7TJjD3q8="
        self.assertTrue(hashid in katal.SELECT)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select3(self):
        """
		Tests.test__fill_select3()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile3.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.read_sieves()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 2)

        hashid = "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="
        self.assertTrue(hashid in katal.SELECT)

        hashid = "rc2y98HRxM0xEpm9nouE60nVk4TUq3ec9sr10UEwpnY="
        self.assertTrue(hashid in katal.SELECT)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select4(self):
        """
		Tests.test__fill_select4()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile4.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.read_sieves()
        katal.fill_select()

        self.assertEqual(len(katal.SELECT), 1)

        hashid = "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="
        self.assertTrue(hashid in katal.SELECT)
        self.assertTrue(katal.SELECT[hashid].complete_name, "ddddd.6")

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select5(self):
        """
		Tests.test__fill_select5()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile5.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.read_sieves()
        katal.fill_select({"tests/data1/a.0":"2015-09-17 20:01",
                           "tests/data1/a.1":"2015-09-17 20:01",
                           "tests/data1/b.2":"2015-09-17 20:01",
                           "tests/data1/b.3":"2015-09-17 20:01",
                           "tests/data1/c.4":"2015-09-17 20:01",
                           "tests/data1/c.5":"2015-09-17 20:01",
                           "tests/data1/ddddX.6":"2015-09-17 20:01",
                           "tests/data1/ddddd.6":"2015-09-17 20:01",})

        self.assertEqual(len(katal.SELECT), 0)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select6(self):
        """
		Tests.test__fill_select6()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile6.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.read_sieves()
        katal.fill_select({"tests/data1/a.0":"2015-09-17 20:01",
                           "tests/data1/a.1":"2015-09-17 20:01",
                           "tests/data1/b.2":"2015-09-17 20:01",
                           "tests/data1/b.3":"2015-09-17 20:01",
                           "tests/data1/c.4":"2015-09-17 20:01",
                           "tests/data1/c.5":"2015-09-17 20:01",
                           "tests/data1/ddddX.6":"2015-09-17 20:01",
                           "tests/data1/ddddd.6":"2015-09-17 20:01",})

        self.assertEqual(len(katal.SELECT), 3)

    #//////////////////////////////////////////////////////////////////////////
    def test__fill_select7(self):
        """
		Tests.test__fill_select7()

		Test of the katal.py::fill_select() function.
        """
        katal.ARGS.configfile = os.path.join("tests", "cfgfile7.ini")
        katal.PARAMETERS = katal.read_parameters_from_cfgfile(katal.ARGS.configfile)
        katal.read_sieves()
        katal.fill_select({"tests/data1/a.0":"2013-01-01 00:00",
                           "tests/data1/a.1":"2013-01-01 00:00",
                           "tests/data1/b.2":"2014-01-01 00:00",
                           "tests/data1/b.3":"2014-01-01 00:00",
                           "tests/data1/c.4":"2015-01-01 00:00",
                           "tests/data1/c.5":"2015-01-01 00:00",
                           "tests/data1/ddddX.6":"2015-09-01 00:00",
                           "tests/data1/ddddd.6":"2015-09-01 00:00",})

        self.assertEqual(len(katal.SELECT), 3)
