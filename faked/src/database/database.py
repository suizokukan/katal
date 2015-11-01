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
    ❏Capri❏ : ./capri/database/database.py
"""

import sqlite3
import os

################################################################################
class DB(object):
    """
        DB class : interface with the databases
    """

    # db_names
    #
    # (int)number of tiles : (str)name of the file
    #
    db_names = { 2 : "capri_2.db", }

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                DB.__init__()
        """
        # { (int)nbr : sqlite3.connect object }
        self.db = dict()

        # { (int)nbr : .cursor() object }
        self.cur = dict()

    #///////////////////////////////////////////////////////////////////////////
    def create_connexions(self):
        """
                DB.create_connexions()

                Fill self.db from DB.db_names
        """
        self.db.clear()

        for nbr in DB.db_names:
            self.db[nbr] = sqlite3.connect( DB.db_names[nbr] )

    #///////////////////////////////////////////////////////////////////////////
    def create_cursors(self):
        """
                DB.create_cursors()

                Erase and fill self.cur from self.db.
        """
        self.cur.clear()

        for nbr in DB.db_names:
            self.cur[nbr] = self.db[nbr].cursor()

    #///////////////////////////////////////////////////////////////////////////
    def create_db_structures(self):
        """
                DB.create_db_structures

                Create the tables in the databases.
        """
        for nbr in self.cur:
            cursor = self.cur[nbr]
            cursor.execute('''CREATE TABLE data (id BIGINT, digest CHAR(16), value TEXT)''')

    #///////////////////////////////////////////////////////////////////////////
    def end(self):
        """
                DB.end()

                Function to be called at the end of the program.
        """
        for nbr in self.cur:
            cursor = self.cur[nbr]
            cursor.close()

    #///////////////////////////////////////////////////////////////////////////
    def reset_all_db(self):
        """
                DB.reset_all_db()

                Remove every database file, create them anew and fill them with
                an (empty) structure.
        """
        for nbr in DB.db_names:
            name = DB.db_names[nbr]
            if os.path.exists(name):
                os.remove(name)

        self.create_connexions()
        self.create_cursors()
        self.create_db_structures()
