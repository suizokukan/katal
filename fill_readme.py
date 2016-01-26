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
        ________________________________________________________________________

        fill_readme.py fills README.md.template from the informations stored
        in katal.py and writes README.md
"""
# Pylint : disabling the "Using the global statement (global-statement)" warning
# pylint: disable=W0622

from codecs import open

from katal.katal import __projectname__, \
                        __version__, __laststableversion__, \
                        __author__, __email__, \
                        __license__, __licensepypi__, \
                        __status__, __statuspypi__

with open("README.md.template", mode="r", encoding='utf-8') as template, \
     open("README.md", mode="w", encoding='utf-8') as output:

    CONTENT = template.read()
    CONTENT = CONTENT.replace("__projectname__", __projectname__)
    CONTENT = CONTENT.replace("__laststableversion__", __laststableversion__)
    CONTENT = CONTENT.replace("__author__", __author__)
    CONTENT = CONTENT.replace("__email__", __email__)
    CONTENT = CONTENT.replace("__license__", __license__)
    CONTENT = CONTENT.replace("__licensepypi__", __licensepypi__)
    CONTENT = CONTENT.replace("__status__", __status__)
    CONTENT = CONTENT.replace("__statuspypi__", __statuspypi__)

    output.write(CONTENT)
