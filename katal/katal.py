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

        A (Python3/GPLv3/OSX-Linux-Windows/CLI) project, using no additional
        modules than the ones installed with Python3.
        ________________________________________________________________________

        Read a directory, select some files according to a configuration file
        (leaving aside the duplicates), copy the selected files in a target
        directory.
        Once the target directory is filled with some files, a database is added
        to the directory to avoid future duplicates. You can add new files to
        the target directory by using Katal one more time, with a different
        source directory.
        ________________________________________________________________________

        see README.md for more documentation.
"""
import argparse
from base64 import b64encode
from collections import namedtuple
import configparser
import ctypes
import hashlib
from datetime import datetime
import filecmp
import fnmatch
import itertools
import os
import platform
import re
import shutil
import sqlite3
import urllib.request
import sys
import unicodedata

__projectname__ = "Katal"
__author__ = "Xavier Faure (suizokukan)"
__copyright__ = "Copyright 2015, suizokukan"
__license__ = "GPL-3.0"
# see https://pypi.python.org/pypi?%3Aaction=list_classifiers
__licensepipy__ = 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
# see https://www.python.org/dev/peps/pep-0440/ e.g 0.1.2.dev1
__version__ = "0.2.3"
__maintainer__ = "Xavier Faure (suizokukan)"
__email__ = "suizokukan @T orange D@T fr"
__status__ = "Beta"
# see https://pypi.python.org/pypi?%3Aaction=list_classifiers
__statuspypi__ = 'Development Status :: 5 - Production/Stable'

ARGS = None # initialized by main()

# when the program verifies that there's enough free space on disk, it multiplies
# the required amount of space by these coefficient
FREESPACE_MARGIN = 1.1

DEFAULT_CONFIGFILE_NAME = "katal.ini"
DEFAULTCFGFILE_URL = "https://raw.githubusercontent.com/suizokukan/katal/master/katal/katal.ini"
DATABASE_NAME = "katal.db"
DATABASE_FULLNAME = ""  # initialized by main_warmup()
TAG_SEPARATOR = ";"  # symbol used in the database between two tags.

TIMESTAMP_BEGIN = datetime.now()  # timestamp used to compute the total time of execution.

PARAMETERS = None # see documentation:configuration file

SOURCE_PATH = ""  # initialized from the configuration file.
INFOS_ABOUT_SRC_PATH = (None, None, None)  # initialized by show_infos_about_source_path()
                                           # ((int)total_size, (int)files_number, (dict)extensions)

TARGET_PATH = "."  # initialized from the configuration file.
TARGET_DB = dict()  # see documentation:database; initialized by read_target_db()
KATALSYS_SUBDIR = ".katal"
TRASH_SUBSUBDIR = "trash"
TASKS_SUBSUBDIR = "tasks"
LOG_SUBSUBDIR = "logs"

# The following values are default values and will be set by the config file.
HASHID_MAXLENGTH = 20  # maximal length of the hashids displayed. Can't be greater than 44.
TAGSSTR_MAXLENGTH = 20  # maximal length of the tags' string displayed.
SOURCENAME_MAXLENGTH = 20  # maximal length of the source's filename
TARGETNAME_MAXLENGTH = 20  # maximal length of the target's filename

# How many bytes have to be read to compute the partial hashid ?
# See the hashfile64() function.
PARTIALHASHID_BYTESNBR = 1000000

LOGFILE = None  # the file descriptor, initialized by logfile_opening()
USE_LOGFILE = False  # (bool) initialized from the configuration file

# SELECT is made of SELECTELEMENT objects, where data about the original files
# are stored.
SELECTELEMENT = namedtuple('SELECTELEMENT', ["fullname",
                                             "partialhashid",
                                             "path",
                                             "filename_no_extens",
                                             "extension",
                                             "size",
                                             "date",
                                             "targetname",
                                             "targettags",])

SELECT = {} # see documentation:selection; initialized by action__select()
SELECT_SIZE_IN_BYTES = 0  # initialized by action__select()
FILTERS = {}  # see documentation:selection; initialized by read_filters()

# date's string format, e.g. "2015-09-17 20:01"
DTIME_FORMAT = "%Y-%m-%d %H:%M"
DTIME_FORMAT_LENGTH = 16

# this minimal subset of characters are the only characters to be used in the
# eval() function. Other characters are forbidden to avoid malicious code execution.
# keywords an symbols : filter, parentheses, and, or, not, xor, True, False
#                       space, &, |, ^, (, ), 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
AUTHORIZED_EVALCHARS = " TFasdlfiteruxnot0123456789&|^()"

# string used to create the database :
SQL__CREATE_DB = 'CREATE TABLE dbfiles (' \
                 'hashid varchar(44) PRIMARY KEY UNIQUE, ' \
                 'partialhashid varchar(44), ' \
                 'size INTEGER, ' \
                 'name TEXT UNIQUE, ' \
                 'sourcename TEXT, sourcedate INTEGER, tagsstr TEXT)'

# suffix, multiple :
# about the multiples of bytes, see e.g. https://en.wikipedia.org/wiki/Megabyte
MULTIPLES = (("kB", 1000),
             ("KB", 1000),
             ("MB", 1000**2),
             ("GB", 1000**3),
             ("TB", 1000**4),
             ("PB", 1000**5),
             ("EB", 1000**6),
             ("ZB", 1000**7),
             ("YB", 1000**8),
             ("KiB", 1024),
             ("MiB", 1024**2),
             ("GiB", 1024**3),
             ("TiB", 1024**4),
             ("PiB", 1024**5),
             ("EiB", 1024**6),
             ("ZiB", 1024**7),
             ("YiB", 1024**8))

################################################################################
class KatalError(BaseException):
    """
        KatalError class

        A very basic class called when an error is raised by the program.
    """
    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, value):
        BaseException.__init__(self)
        self.value = value
    #///////////////////////////////////////////////////////////////////////////
    def __str__(self):
        return repr(self.value)

#///////////////////////////////////////////////////////////////////////////////
def action__add():
    """
        action__add()
        ________________________________________________________________________

        Add the source files described in SELECT/SELECT_SIZE_IN_BYTES to the
        target path.
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                (int) 0 if success, -1 if an error occured.
    """
    msg("  = copying data =")

    db_connection = sqlite3.connect(DATABASE_FULLNAME)
    db_cursor = db_connection.cursor()

    if get_disk_free_space(TARGET_PATH) < SELECT_SIZE_IN_BYTES*FREESPACE_MARGIN:
        msg("    ! Not enough space on disk. Stopping the program.")
        # returned value : -1 = error
        return -1

    files_to_be_added = []
    len_select = len(SELECT)
    for index, hashid in enumerate(SELECT):

        complete_source_filename = SELECT[hashid].fullname
        target_name = os.path.join(normpath(TARGET_PATH), SELECT[hashid].targetname)

        sourcedate = datetime.utcfromtimestamp(os.path.getmtime(complete_source_filename))
        sourcedate = sourcedate.replace(second=0, microsecond=0)

        # converting the datetime object in epoch value (=the number of seconds from 1970-01-01 :
        sourcedate -= datetime(1970, 1, 1)
        sourcedate = sourcedate.total_seconds()

        msg("    ... ({0}/{1}) copying \"{2}\" to \"{3}\" .".format(index+1,
                                                                    len_select,
                                                                    complete_source_filename,
                                                                    target_name))
        if not ARGS.off:
            if not ARGS.move:
                shutil.copyfile(complete_source_filename, target_name)
            else:
                shutil.move(complete_source_filename, target_name)
            os.utime(target_name, (sourcedate, sourcedate))

        files_to_be_added.append((hashid,
                                  SELECT[hashid].partialhashid,
                                  SELECT[hashid].size,
                                  SELECT[hashid].targetname,
                                  complete_source_filename,
                                  sourcedate,
                                  SELECT[hashid].targettags))

    msg("    = all files have been copied, let's update the database... =")

    try:
        if not ARGS.off:
            db_cursor.executemany('INSERT INTO dbfiles VALUES (?,?,?,?,?,?,?)', files_to_be_added)

    except sqlite3.IntegrityError as exception:
        msg("!!! An error occured while writing the database : "+str(exception))
        msg("!!! files_to_be_added : ")
        for file_to_be_added in files_to_be_added:
            msg("     ! hashid={0}; partialhashid={1}; size={2}; name={3}; sourcename={4}; " \
                "sourcedate={5}; tagsstr={6}".format(*file_to_be_added))
        raise KatalError("An error occured while writing the database : "+str(exception))

    db_connection.commit()
    db_connection.close()

    msg("    = ... database updated =")

    # returned value : 0 = success
    return 0

#///////////////////////////////////////////////////////////////////////////////
def action__addtag(_tag, _to):
    """
        action__addtag()
        ________________________________________________________________________

        Add a tag to the files given by the _to parameter.
        ________________________________________________________________________

        PARAMETERS
                o _tag          : (str) new tag to be added
                o _to           : (str) a regex string describing what files are
                                  concerned
    """
    msg("  = let's add the tag string \"{0}\" to {1}".format(_tag, _to))
    modify_the_tag_of_some_files(_tag=_tag, _to=_to, _mode="append")

#///////////////////////////////////////////////////////////////////////////////
def action__cleandbrm():
    """
        action__cleandbrm()
        ________________________________________________________________________

        Remove from the database the missing files, i.e. the files that do not
        exist in the target directory.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    msg("  = clean the database : remove missing files from the target directory =")

    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        msg("    ! no database found.")
        return

    db_connection = sqlite3.connect(DATABASE_FULLNAME)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    files_to_be_rmved_from_the_db = []  # hashid of the files
    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        if not os.path.exists(os.path.join(normpath(TARGET_PATH), db_record["name"])):
            files_to_be_rmved_from_the_db.append(db_record["hashid"])
            msg("    o about to remove \"{0}\" " \
                "from the database".format(os.path.join(normpath(TARGET_PATH),
                                                        db_record["name"])))

    if len(files_to_be_rmved_from_the_db) == 0:
        msg("    ! no file to be removed : the database is ok.")
    else:
        for hashid in files_to_be_rmved_from_the_db:
            if not ARGS.off:
                msg("    o removing \"{0}\" record " \
                    "from the database".format(hashid))
                db_cursor.execute("DELETE FROM dbfiles WHERE hashid=?", (hashid,))
                db_connection.commit()

    db_connection.close()
    if not ARGS.off:
        msg("    o ... done : removed {0} " \
            "file(s) from the database".format(len(files_to_be_rmved_from_the_db)))

#///////////////////////////////////////////////////////////////////////////////
def action__downloadefaultcfg(newname=DEFAULT_CONFIGFILE_NAME):
    """
        action__downloadefaultcfg()
        ________________________________________________________________________

        Download the default configuration file and give to it the name "newname"
        ________________________________________________________________________

        PARAMETER :
            (str) newname : the new name of the downloaded file

        RETURNED VALUE :
            (bool) success
    """
    msg("  = downloading the default configuration file =")
    msg("  ... trying to download {0} from {1}".format(newname, DEFAULTCFGFILE_URL))

    try:
        if not ARGS.off:
            with urllib.request.urlopen(DEFAULTCFGFILE_URL) as response, \
                 open(newname, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        msg("  * download completed.")
        return True

    except urllib.error.URLError as exception:
        msg("  ! An error occured : "+str(exception))
        msg("  ... if you can't download the default config file, what about simply")
        msg("  ... copy another config file to the target directory ?")
        msg("  ... In a target directory, the config file is " \
            "in the \"{0}\" directory.".format(os.path.join(KATALSYS_SUBDIR)))
        return False

#///////////////////////////////////////////////////////////////////////////////
def action__findtag(_tag):
    """
        action__findtag()
        ________________________________________________________________________

        Display the files tagged with _tag. _tag is a simple string, not a
        regex. The function searches a substring _tag in the tags' string.
        ________________________________________________________________________

        PARAMETER
            o _tag : (str)the searched tag

        no RETURNED VALUE
    """
    msg("  = searching the files with the tag \"{0}\" =".format(_tag))

    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        msg("    ! no database found.")
        return

    db_connection = sqlite3.connect(DATABASE_FULLNAME)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    res = []
    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        if _tag in db_record["tagsstr"]:

            res.append(db_record["name"])
            msg("    o \"{0}\" : \"{1}\"".format(db_record["name"],
                                                 tagsstr_repr(db_record["tagsstr"])))

    len_res = len(res)
    if len_res == 0:
        msg("    o no file matches the tag \"{0}\" .".format(_tag))
    elif len_res == 1:
        msg("    o one file matches the tag \"{0}\" .".format(_tag))
    else:
        msg("    o {0} files match the tag \"{1}\" .".format(len_res, _tag))

    db_connection.commit()
    db_connection.close()

    # --copyto argument :
    if ARGS.copyto:
        msg("    o copying the files into \"{0}\" (path: \"{1}\")".format(ARGS.copyto,
                                                                          normpath(ARGS.copyto)))

        if not os.path.exists(normpath(ARGS.copyto)):
            msg("    * let's create \"{0}\" (path: \"{1}\"".format(ARGS.copyto,
                                                                   normpath(ARGS.copyto)))
            if not ARGS.off:
                os.mkdir(normpath(ARGS.copyto))

        for i, filename in enumerate(res):
            src = os.path.join(normpath(TARGET_PATH), filename)
            dest = os.path.join(normpath(ARGS.copyto), filename)
            msg("    o ({0}/{1}) copying \"{2}\" as \"{3}\"...".format(i+1, len_res, src, dest))
            if not ARGS.off:
                shutil.copy(src, dest)

#///////////////////////////////////////////////////////////////////////////////
def action__infos():
    """
        action__infos()
        ________________________________________________________________________

        Display informations about the source and the target directory
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                (int) 0 if ok, -1 if an error occured
    """
    msg("  = informations =")
    show_infos_about_source_path()
    return show_infos_about_target_path()

#///////////////////////////////////////////////////////////////////////////////
def action__new(targetname):
    """
        action__new()
        ________________________________________________________________________

        Create a new target directory
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    msg("  = about to create a new target directory " \
        "named \"{0}\" (path : \"{1}\")".format(targetname,
                                                normpath(targetname)))
    if os.path.exists(normpath(targetname)):
        msg("  ! can't go further : the directory already exists.")
        return

    if not ARGS.off:
        msg("  ... creating the target directory with its sub-directories...")
        os.mkdir(normpath(targetname))
        os.mkdir(os.path.join(normpath(targetname), KATALSYS_SUBDIR))
        os.mkdir(os.path.join(normpath(targetname), KATALSYS_SUBDIR, TRASH_SUBSUBDIR))
        os.mkdir(os.path.join(normpath(targetname), KATALSYS_SUBDIR, TASKS_SUBSUBDIR))
        os.mkdir(os.path.join(normpath(targetname), KATALSYS_SUBDIR, LOG_SUBSUBDIR))

        create_empty_db(os.path.join(normpath(targetname),
                                     KATALSYS_SUBDIR,
                                     DATABASE_NAME))

    if not ARGS.mute:
        answer = \
            input("\nDo you want to download the default config file " \
                  "into the expected directory ? (y/N) ")

        if answer in ("y", "yes"):
            if action__downloadefaultcfg(os.path.join(normpath(targetname),
                                                      KATALSYS_SUBDIR,
                                                      DEFAULT_CONFIGFILE_NAME)):
                msg("  ... done.")
            else:
                print("  ! A problem occured : " \
                      "the creation of the target directory has been aborted.")

    msg("  ... done with the creation of \"{0}\" as a new target directory.".format(targetname))

#///////////////////////////////////////////////////////////////////////////////
def action__rebase(_newtargetpath):
    """
        action__rebase()
        ________________________________________________________________________

        Copy the current target directory into a new one, modifying the filenames.
        ________________________________________________________________________

        PARAMETER :
                o _newtargetpath        : (str) path to the new target directory.

        no RETURNED VALUE
    """
    msg("  = copying the current target directory into a new one =")
    msg("    o from {0} (path : \"{1}\")".format(SOURCE_PATH,
                                                 normpath(SOURCE_PATH)))

    msg("    o to   {0} (path : \"{1}\")".format(_newtargetpath,
                                                 normpath(_newtargetpath)))

    to_configfile = os.path.join(_newtargetpath,
                                 KATALSYS_SUBDIR,
                                 DEFAULT_CONFIGFILE_NAME)
    msg("    o trying to read dest config file {0} " \
        "(path : \"{1}\") .".format(to_configfile,
                                    normpath(to_configfile)))
    dest_params = read_parameters_from_cfgfile(normpath(to_configfile))

    if dest_params is None:
        msg("    ! can't read the dest config file !")
        return

    msg("    o config file found and read (ok)")
    msg("    o new filenames' format : " \
        "{0}".format(dest_params["target"]["name of the target files"]))
    msg("    o tags to be added : " \
        "{0}".format(dest_params["target"]["tags"]))

    new_db = os.path.join(normpath(_newtargetpath), KATALSYS_SUBDIR, DATABASE_NAME)
    if not ARGS.off:
        if os.path.exists(new_db):
            # let's delete the previous new database :
            os.remove(new_db)

    # let's compute the new names :
    olddb_connection = sqlite3.connect(DATABASE_FULLNAME)
    olddb_connection.row_factory = sqlite3.Row
    olddb_cursor = olddb_connection.cursor()

    files, anomalies_nbr = action__rebase__files(olddb_cursor, dest_params, _newtargetpath)

    go_on = True
    if anomalies_nbr != 0:
        go_on = False
        answer = \
            input("\nAt least one anomaly detected (see details above) " \
                  "Are you sure you want to go on ? (y/N) ")

        if answer in ("y", "yes"):
            go_on = True

    if not go_on:
        olddb_connection.close()
        return
    else:
        action__rebase__write(new_db, files)
        olddb_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def action__rebase__files(_olddb_cursor, _dest_params, _newtargetpath):
    """
        action__rebase__files()
        ________________________________________________________________________

        Return a dict of the files to be copied (old name, new name, ...) and
        the number of anomalies.
        ________________________________________________________________________

        PARAMETER :
                o _olddb_cursor         : cursor to the source database
                o _dest_params          : an object returned by read_parameters_from_cfgfile(),
                                          like PARAMETERS
                o _newtargetpath        : (str) path to the new target directory.

        RETURNED VALUE :
                (files, (int)number of anomalies)

                files : a dict hashid::( (0)source name,
                                         (1)new name,
                                         (2)source date,
                                         (3)source tagsstr,
                                         (4)size,
                                         (5)partialhashid)
    """
    files = dict()      # dict to be returned.
    filenames = set()   # to be used to avoid duplicates.

    anomalies_nbr = 0
    for index, olddb_record in enumerate(_olddb_cursor.execute('SELECT * FROM dbfiles')):
        fullname = normpath(os.path.join(SOURCE_PATH, olddb_record["name"]))
        filename_no_extens, extension = get_filename_and_extension(fullname)

        size = olddb_record["size"]
        date = olddb_record["sourcedate"]
        new_name = \
            create_target_name(_parameters=_dest_params,
                               _hashid=olddb_record["hashid"],
                               _filename_no_extens=filename_no_extens,
                               _path=olddb_record["sourcename"],
                               _extension=extension,
                               _size=size,
                               _date=datetime.utcfromtimestamp(date).strftime(DTIME_FORMAT),
                               _database_index=index)
        new_name = normpath(os.path.join(_newtargetpath, new_name))
        tagsstr = olddb_record["tagsstr"]

        msg("      o {0} : {1} would be copied as {2}".format(olddb_record["hashid"],
                                                              olddb_record["name"],
                                                              new_name))

        if new_name in filenames:
            msg("      ! anomaly : ancient file {1} should be renamed as {0} " \
                "but this name would have been already created in the new target directory ! " \
                "".format(new_name, fullname))
            msg("        Two different files from the ancient target directory " \
                "can't bear the same name in the new target directory !")
            anomalies_nbr += 1
        elif os.path.exists(new_name):
            msg("      ! anomaly : ancient file {1} should be renamed as {0} " \
                "but this name already exists in new target directory !".format(new_name, fullname))
            anomalies_nbr += 1
        else:
            files[olddb_record["hashid"]] = (fullname, new_name, date, tagsstr)
            filenames.add(new_name)

    return files, anomalies_nbr

#///////////////////////////////////////////////////////////////////////////////
def action__rebase__write(_new_db, _files):
    """
        action__rebase__write()
        ________________________________________________________________________

        Write the files described by _files in the new target directory.
        ________________________________________________________________________

        PARAMETER :
                o _new_db               : (str) new database's name
                o _files                : (dict) see action__rebase__files()

        no RETURNED VALUE
    """
    # let's write the new database :
    newdb_connection = sqlite3.connect(_new_db)
    newdb_connection.row_factory = sqlite3.Row
    newdb_cursor = newdb_connection.cursor()

    try:
        if not ARGS.off:
            newdb_cursor.execute(SQL__CREATE_DB)

        for index, futurefile_hashid in enumerate(_files):
            futurefile = _files[futurefile_hashid]
            file_to_be_added = (futurefile_hashid,      # hashid
                                futurefile[5],          # partial hashid
                                futurefile[4],          # size
                                futurefile[1],          # new name
                                futurefile[0],          # sourcename
                                futurefile[2],          # sourcedate
                                futurefile[3])          # tags

            strdate = datetime.utcfromtimestamp(futurefile[2]).strftime(DTIME_FORMAT)
            msg("    o ({0}/{1}) adding a file in the new database".format(index+1, len(_files)))
            msg("      o hashid      : {0}".format(futurefile_hashid))
            msg("      o source name : \"{0}\"".format(futurefile[0]))
            msg("      o desti. name : \"{0}\"".format(futurefile[1]))
            msg("      o source date : {0}".format(strdate))
            msg("      o size        : {0}".format(futurefile[4]))
            msg("      o tags        : \"{0}\"".format(futurefile[3]))

            if not ARGS.off:
                newdb_cursor.execute('INSERT INTO dbfiles VALUES (?,?,?,?,?,?,?)', file_to_be_added)
                newdb_connection.commit()

    except sqlite3.IntegrityError as exception:
        msg("!!! An error occured while writing the new database : "+str(exception))
        raise KatalError("An error occured while writing the new database : "+str(exception))

    newdb_connection.close()

    # let's copy the files :
    for index, futurefile_hashid in enumerate(_files):
        futurefile = _files[futurefile_hashid]
        old_name, new_name = futurefile[0], futurefile[1]

        msg("    o ({0}/{1}) copying \"{2}\" as \"{3}\"".format(index+1, len(_files),
                                                                old_name, new_name))
        if not ARGS.off:
            shutil.copyfile(old_name, new_name)

    msg("    ... done")

#///////////////////////////////////////////////////////////////////////////////
def action__reset():
    """
        action__reset()
        ________________________________________________________________________

        Delete the files in the target directory and the database.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    msg("    = about to delete (=move in the trash) the target files and the database.")

    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        msg("    ! no database found, nothing to do .")
        return

    if not ARGS.mute:
        answer = \
            input("\nDo you really want to delete (=move to the katal trash directory)" \
                  "the files in the target directory and the database (y/N) ")
        if answer not in ("y", "yes"):
            return

    db_connection = sqlite3.connect(DATABASE_FULLNAME)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    files_to_be_removed = []  # a list of (hashid, fullname)
    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        files_to_be_removed.append((db_record["hashid"], db_record["name"]))

    for hashid, name in files_to_be_removed:
        msg("   o removing {0} from the database and from the target path".format(name))
        if not ARGS.off:
            # let's remove the file from the target directory :
            shutil.move(os.path.join(normpath(TARGET_PATH), name),
                        os.path.join(normpath(TARGET_PATH),
                                     KATALSYS_SUBDIR, TRASH_SUBSUBDIR, name))
            # let's remove the file from the database :
            db_cursor.execute("DELETE FROM dbfiles WHERE hashid=?", (hashid,))

            db_connection.commit()

    db_connection.close()

    msg("    = ... done : the database should be empty, the target files should no longer exist.")

#///////////////////////////////////////////////////////////////////////////////
def action__rmnotags():
    """
        action__rmnotags
        ________________________________________________________________________

        Remove all files (from the target directory and from the database) if
        they have no tags.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    msg("  = removing all files with no tags (=moving them to the trash) =")

    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        msg("    ! no database found.")
    else:
        db_connection = sqlite3.connect(DATABASE_FULLNAME)
        db_connection.row_factory = sqlite3.Row
        db_cursor = db_connection.cursor()

        files_to_be_removed = []    # list of (hashid, name)
        for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
            if db_record["tagsstr"] == "":
                files_to_be_removed.append((db_record["hashid"], db_record["name"]))

        if len(files_to_be_removed) == 0:
            msg("   ! no files to be removed.")
        else:
            for hashid, name in files_to_be_removed:
                msg("   o removing {0} from the database and from the target path".format(name))
                if not ARGS.off:
                    # let's remove the file from the target directory :
                    shutil.move(os.path.join(normpath(TARGET_PATH), name),
                                os.path.join(normpath(TARGET_PATH),
                                             KATALSYS_SUBDIR, TRASH_SUBSUBDIR, name))
                    # let's remove the file from the database :
                    db_cursor.execute("DELETE FROM dbfiles WHERE hashid=?", (hashid,))

        db_connection.commit()
        db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def action__rmtags(_to):
    """
        action__rmtags()
        ________________________________________________________________________

        Remove the tags' string(s) in the target directory, overwriting ancient tags.
        ________________________________________________________________________

        PARAMETERS
                o _to           : (str) a regex string describing what files are
                                  concerned
    """
    msg("  = let's remove the tags' string(s) in {0}".format(_to))
    action__settagsstr(_tagsstr="", _to=_to)

#///////////////////////////////////////////////////////////////////////////////
def action__select():
    """
        action__select()
        ________________________________________________________________________

        fill SELECT and SELECT_SIZE_IN_BYTES and display what's going on.
        This function will always be called before a call to action__add().
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE.
    """
    msg("  = selecting files according to the instructions " \
                "in the config file... =")

    msg("  o the files will be copied in \"{0}\" " \
        "(path: \"{1}\")".format(TARGET_PATH,
                                 normpath(TARGET_PATH)))
    msg("  o the files will be renamed according " \
        "to the \"{0}\" pattern.".format(PARAMETERS["target"]["name of the target files"]))

    msg("  o filters :")

    for filter_index in FILTERS:
        msg("    o filter #{0} : {1}".format(filter_index,
                                             FILTERS[filter_index]))
    msg("  o file list :")

    # let's initialize SELECT and SELECT_SIZE_IN_BYTES :
    number_of_discarded_files = fill_select()

    msg("    o size of the selected file(s) : {0}".format(size_as_str(SELECT_SIZE_IN_BYTES)))

    if len(SELECT) == 0:
        msg("    ! no file selected ! " \
            "You have to modify the config file to get some files selected.")
    else:
        ratio = len(SELECT)/(len(SELECT)+number_of_discarded_files)*100.0
        msg("    o number of selected files " \
                  "(after discarding {1} file(s)) : {0}, " \
                  "{2:.2f}% of the source files.".format(len(SELECT),
                                                         number_of_discarded_files,
                                                         ratio))

    # let's check that the target path has sufficient free space :
    available_space = get_disk_free_space(TARGET_PATH)
    if available_space > SELECT_SIZE_IN_BYTES*FREESPACE_MARGIN:
        size_ok = "ok"
    else:
        size_ok = "!!! problem !!!"
    msg("    o required space : {0}; " \
        "available space on disk : {1} ({2})".format(size_as_str(SELECT_SIZE_IN_BYTES),
                                                     size_as_str(available_space),
                                                     size_ok))

    # if there's no --add option, let's give some examples of the target names :
    if not ARGS.add:
        example_index = 0
        for hashid in SELECT:

            complete_source_filename = SELECT[hashid].fullname

            target_name = os.path.join(normpath(TARGET_PATH), SELECT[hashid].targetname)

            msg("    o e.g. ... \"{0}\" " \
                "would be copied as \"{1}\" .".format(complete_source_filename,
                                                      target_name))

            example_index += 1

            if example_index > 5:
                break

#///////////////////////////////////////////////////////////////////////////////
def action__settagsstr(_tagsstr, _to):
    """
        action__settagsstr()
        ________________________________________________________________________

        Set the tags' string(s) in the target directory, overwriting ancient tags.
        ________________________________________________________________________

        PARAMETERS
                o _tagsstr      : (str) the new tags' strings
                o _to           : (str) a regex string describing what files are
                                  concerned
    """
    msg("  = let's apply the tag string\"{0}\" to {1}".format(_tagsstr, _to))
    modify_the_tag_of_some_files(_tag=_tagsstr, _to=_to, _mode="set")

#///////////////////////////////////////////////////////////////////////////////
def action__target_kill(_filename):
    """
        action__target_kill()
        ________________________________________________________________________

        Delete _filename from the target directory and from the database.
        ________________________________________________________________________

        PARAMETER
                o  _filename    : (str) file's name to be deleted.
                                  DO NOT GIVE A PATH, just the file's name,
                                  without the path to the target directory

        RETURNED VALUE
                (int) : 0 if success, -1 if the file doesn't exist in the target
                        directory, -2 if the file doesn't exist in the database,
                        -3 if there's no database.
    """
    msg("  = about to remove \"{0}\" from the target directory (=file moved to the trash) " \
        "and from its database =".format(_filename))
    if not os.path.exists(os.path.join(normpath(TARGET_PATH), _filename)):
        msg("    ! can't find \"{0}\" file on disk.".format(_filename))
        return -1

    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        msg("    ! no database found.")
        return -3
    else:
        db_connection = sqlite3.connect(DATABASE_FULLNAME)
        db_connection.row_factory = sqlite3.Row
        db_cursor = db_connection.cursor()

        filename_hashid = None
        for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
            if db_record["name"] == os.path.join(normpath(TARGET_PATH), _filename):
                filename_hashid = db_record["hashid"]

        if filename_hashid is None:
            msg("    ! can't find \"{0}\" file in the database.".format(_filename))
            res = -2
        else:
            if not ARGS.off:
                # let's remove _filename from the target directory :
                shutil.move(os.path.join(normpath(TARGET_PATH), _filename),
                            os.path.join(normpath(TARGET_PATH),
                                         KATALSYS_SUBDIR, TRASH_SUBSUBDIR, _filename))

                # let's remove _filename from the database :
                db_cursor.execute("DELETE FROM dbfiles WHERE hashid=?", (filename_hashid,))

            res = 0  # success.

        db_connection.commit()
        db_connection.close()

        msg("    ... done")
        return res

#///////////////////////////////////////////////////////////////////////////////
def action__whatabout(_src):
    """
        action__whatabout()
        ________________________________________________________________________

        Take a look at the _src file/directory and answer the following question :
        is(are) this(these) file(s) already in the target directory ?
        ________________________________________________________________________

        PARAMETER
            o _src : (str) the source file's name

        RETURNED VALUE : (bool)is everything ok (=no error) ?
    """
    #. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    def show_infos_about_a_srcfile(_srcfile_name):
        """
                Display the expected informations about a file named _srcfile_name .
        """
        msg("  = what about the \"{0}\" file ? (normpath : \"{1}\")".format(_src, _srcfile_name))
        size = os.stat(_srcfile_name).st_size
        msg("    = size : {0}".format(size_as_str(size)))

        sourcedate = datetime.utcfromtimestamp(os.path.getmtime(_srcfile_name))
        sourcedate = sourcedate.replace(second=0, microsecond=0)
        sourcedate2 = sourcedate
        sourcedate2 -= datetime(1970, 1, 1)
        sourcedate2 = sourcedate2.total_seconds()
        msg("    = mtime : {0} (epoch value : {1})".format(sourcedate, sourcedate2))

        srchash = hashfile64(_srcfile_name)
        msg("    = hash : {0}".format(srchash))

        # is the hash in the database ?
        already_present_in_db = False
        for hashid in TARGET_DB:
            if hashid == srchash:
                already_present_in_db = True
                break
        if already_present_in_db:
            msg("    = the file's content is equal to a file ALREADY present in the database.")
        else:
            msg("    = the file isn't present in the database.")

    # (1) does _src exist ?
    normsrc = normpath(_src)
    if not os.path.exists(normsrc):
        msg("  ! error : can't find source file \"{0}\" .".format(normsrc))
        return False

    # (2) is _src a file or a directory ?
    if os.path.isdir(normsrc):
        # informations about the source directory :
        if normpath(TARGET_PATH) in normsrc:
            msg("  ! error : the given directory in inside the target directory.")
            return False

        for dirpath, _, filenames in os.walk(normpath(_src)):
            for filename in filenames:
                fullname = os.path.join(normpath(dirpath), filename)
                show_infos_about_a_srcfile(fullname)

    else:
        # informations about the source file :
        if normpath(TARGET_PATH) in normpath(_src):
            # special case : the file is inside the target directory :
            msg("  = what about the \"{0}\" file ? (normpath : \"{1}\")".format(_src, normsrc))
            msg("    This file is inside the target directory.")
            srchash = hashfile64(normsrc)
            msg("    = hash : {0}".format(srchash))
            msg("    Informations extracted from the database :")
            # informations from the database :
            db_connection = sqlite3.connect(DATABASE_FULLNAME)
            db_connection.row_factory = sqlite3.Row
            db_cursor = db_connection.cursor()
            for db_record in db_cursor.execute("SELECT * FROM dbfiles WHERE hashid=?", (srchash,)):
                msg("    = partial hashid : {0}".format(db_record["partialhashid"]))
                msg("    = name : {0}".format(db_record["name"]))
                msg("    = size : {0}".format(db_record["size"]))
                msg("    = source name : {0}".format(db_record["sourcename"]))
                msg("    = source date : {0}".format(db_record["sourcedate"]))
                msg("    = tags' string : {0}".format(db_record["tagsstr"]))
            db_connection.close()

        else:
            # normal case : the file is outside the target directory :
            show_infos_about_a_srcfile(normpath(_src))

    return True

#///////////////////////////////////////////////////////////////////////////////
def add_keywords_in_targetstr(_srcstring,
                              _hashid,
                              _filename_no_extens,
                              _path,
                              _extension,
                              _size,
                              _date,
                              _database_index):
    """
        create_target_name()
        ________________________________________________________________________

        The function replaces some keywords in the string by the parameters given
        to this function.
        The function returned a string which may be used to create target files.

        see the available keywords in the documentation.
            (see documentation:configuration file)

        caveat : in the .ini files, '%' have to be written twice (as in
                 '%%p', e.g.) but Python reads it as if only one % was
                 written.
        ________________________________________________________________________

        PARAMETERS
                o _parameters                   : an object returned by
                                                  read_parameters_from_cfgfile(),
                                                  like PARAMETERS
                o _hashid                       : (str)
                o _filename_no_extens           : (str)
                o _path                         : (str
                o _extension                    : (str)
                o _size                         : (int)
                o _date                         : (str) see DTIME_FORMAT
                o _database_index               : (int)

        RETURNED VALUE
                (str)the expected string
    """
    res = _srcstring

    # beware : order matters !
    res = res.replace("%ht",
                      hex(int(datetime.strptime(_date,
                                                DTIME_FORMAT).timestamp()))[2:])

    res = res.replace("%h", _hashid)

    res = res.replace("%ff", remove_illegal_characters(_filename_no_extens))
    res = res.replace("%f", _filename_no_extens)

    res = res.replace("%pp", remove_illegal_characters(_path))
    res = res.replace("%p", _path)

    res = res.replace("%ee", remove_illegal_characters(_extension))
    res = res.replace("%e", _extension)

    res = res.replace("%s", str(_size))

    res = res.replace("%dd", remove_illegal_characters(_date))

    res = res.replace("%t",
                      str(int(datetime.strptime(_date,
                                                DTIME_FORMAT).timestamp())))

    res = res.replace("%i",
                      remove_illegal_characters(str(_database_index)))

    return res

#///////////////////////////////////////////////////////////////////////////////
def check_args():
    """
        check_args()
        ________________________________________________________________________

        check the arguments of the command line. Raise an exception if something
        is wrong.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    # --select and --add can't be used simultaneously.
    if ARGS.add is True and ARGS.select is True:
        raise KatalError("--select and --add can't be used simultaneously")

    # --settagsstr must be used with --to :
    if ARGS.settagsstr and not ARGS.to:
        raise KatalError("please use --to in combination with --settagsstr")

    # --addtag must be used with --to :
    if ARGS.addtag and not ARGS.to:
        raise KatalError("please use --to in combination with --addtag")

    # --rmtags must be used with --to :
    if ARGS.rmtags and not ARGS.to:
        raise KatalError("please use --to in combination with --rmtags")

    # --move can only be used with --select or with --add :
    if ARGS.move and not (ARGS.add or ARGS.select):
        raise KatalError("--move can only be used in combination with --select or with --add")

    # --strictcmp can only be used with --select or with --add :
    if ARGS.strictcmp and not (ARGS.add or ARGS.select):
        raise KatalError("--strictcmp can only be used in combination with --select or with --add")

    # --copyto can only be used with --findtag :
    if ARGS.copyto and not ARGS.findtag:
        raise KatalError("--copyto can only be used in combination with --findtag .")

#///////////////////////////////////////////////////////////////////////////////
def create_empty_db(_db_name):
    """
        create_empty_db()
        ________________________________________________________________________

        Create an empty database named _db_name .
        ________________________________________________________________________

        PARAMETER :
            o _db_name : name of the file to be created .
                         Please use a normpath'd parameter : the normpath function
                         will not be called by create_empty_db() !

        no RETURNED VALUE
    """
    msg("  ... creating an empty database named \"{0}\"...".format(_db_name))

    if not ARGS.off:

        db_connection = sqlite3.connect(_db_name)
        db_cursor = db_connection.cursor()

        db_cursor.execute(SQL__CREATE_DB)

        db_connection.commit()
        db_connection.close()

    msg("   ... database created")

#///////////////////////////////////////////////////////////////////////////////
def create_subdirs_in_target_path():
    """
        create_subdirs_in_target_path()
        ________________________________________________________________________

        Create the expected subdirectories in TARGET_PATH .
        ________________________________________________________________________

        no PARAMETERS, no RETURNED VALUE
    """
    # (str)name for the message, (str)full path :
    for name, \
        fullpath in (("target", TARGET_PATH),
                     ("system", os.path.join(normpath(TARGET_PATH),
                                             KATALSYS_SUBDIR)),
                     ("trash", os.path.join(normpath(TARGET_PATH),
                                            KATALSYS_SUBDIR, TRASH_SUBSUBDIR)),
                     ("log", os.path.join(normpath(TARGET_PATH),
                                          KATALSYS_SUBDIR, LOG_SUBSUBDIR)),
                     ("tasks", os.path.join(normpath(TARGET_PATH),
                                            KATALSYS_SUBDIR, TASKS_SUBSUBDIR))):
        if not os.path.exists(normpath(fullpath)):
            msg("  * Since the {0} path \"{1}\" (path : \"{2}\") " \
                "doesn't exist, let's create it.".format(name,
                                                         fullpath,
                                                         normpath(fullpath)))
            if not ARGS.off:
                os.mkdir(normpath(fullpath))

#/////////////////////////////////////////////////////////////////////////////////////////
def create_target_name(_parameters,
                       _hashid,
                       _filename_no_extens,
                       _path,
                       _extension,
                       _size,
                       _date,
                       _database_index):
    """
        create_target_name()
        ________________________________________________________________________

        Create the name of a file (a target file) from various informations
        given by the parameters. The function reads the string stored in
        _parameters["target"]["name of the target files"] and replaces some
        keywords in the string by the parameters given to this function.

        see the available keywords in the documentation.
            (see documentation:configuration file)

        caveat : in the .ini files, '%' have to be written twice (as in
                 '%%p', e.g.) but Python reads it as if only one % was
                 written.
        ________________________________________________________________________

        PARAMETERS
                o _parameters                   : an object returned by
                                                  read_parameters_from_cfgfile(),
                                                  like PARAMETERS
                o _hashid                       : (str)
                o _filename_no_extens           : (str)
                o _path                         : (str
                o _extension                    : (str)
                o _size                         : (int)
                o _date                         : (str) see DTIME_FORMAT
                o _database_index               : (int)

        RETURNED VALUE
                (str)name
    """
    return(add_keywords_in_targetstr(_srcstring=_parameters["target"]["name of the target files"],
                                     _hashid=_hashid,
                                     _filename_no_extens=_filename_no_extens,
                                     _path=_path,
                                     _extension=_extension,
                                     _size=_size,
                                     _date=_date,
                                     _database_index=_database_index))

#/////////////////////////////////////////////////////////////////////////////////////////
def create_target_name_and_tags(_parameters,
                                _hashid,
                                _filename_no_extens,
                                _path,
                                _extension,
                                _size,
                                _date,
                                _database_index):
    """
        create_target_name_and_tags()
        ________________________________________________________________________

        Create the name of a file (a target file) from various informations
        given by the parameters. The function reads the string stored in
        _parameters["target"]["name of the target files"] and in
        _parameters["target"]["tags"] and replaces some
        keywords in the string by the parameters given to this function.

        see the available keywords in the documentation.
            (see documentation:configuration file)

        caveat : in the .ini files, '%' have to be written twice (as in
                 '%%p', e.g.) but Python reads it as if only one % was
                 written.
        ________________________________________________________________________

        PARAMETERS
                o _parameters                   : an object returned by
                                                  read_parameters_from_cfgfile(),
                                                  like PARAMETERS
                o _hashid                       : (str)
                o _filename_no_extens           : (str)
                o _path                         : (str
                o _extension                    : (str)
                o _size                         : (int)
                o _date                         : (str) see DTIME_FORMAT
                o _database_index               : (int)

        RETURNED VALUE
                ( (str)name, (str)tags )
    """
    name = create_target_name(_parameters,
                              _hashid,
                              _filename_no_extens,
                              _path,
                              _extension,
                              _size,
                              _date,
                              _database_index)

    tags = create_target_name(_parameters,
                              _hashid,
                              _filename_no_extens,
                              _path,
                              _extension,
                              _size,
                              _date,
                              _database_index)
    return (name, tags)

#/////////////////////////////////////////////////////////////////////////////////////////
def create_target_tags(_parameters,
                       _hashid,
                       _filename_no_extens,
                       _path,
                       _extension,
                       _size,
                       _date,
                       _database_index):
    """
        create_target_tags()
        ________________________________________________________________________

        Create the tags of a file (a target file) from various informations
        given by the parameters. The function reads the string stored in
        _parameters["target"]["tags"] and replaces some
        keywords in the string by the parameters given to this function.

        see the available keywords in the documentation.
            (see documentation:configuration file)

        caveat : in the .ini files, '%' have to be written twice (as in
                 '%%p', e.g.) but Python reads it as if only one % was
                 written.
        ________________________________________________________________________

        PARAMETERS
                o _parameters                   : an object returned by
                                                  read_parameters_from_cfgfile(),
                                                  like PARAMETERS
                o _hashid                       : (str)
                o _filename_no_extens           : (str)
                o _path                         : (str
                o _extension                    : (str)
                o _size                         : (int)
                o _date                         : (str) see DTIME_FORMAT
                o _database_index               : (int)

        RETURNED VALUE
                (str)name
    """
    return(add_keywords_in_targetstr(_srcstring=_parameters["target"]["tags"],
                                     _hashid=_hashid,
                                     _filename_no_extens=_filename_no_extens,
                                     _path=_path,
                                     _extension=_extension,
                                     _size=_size,
                                     _date=_date,
                                     _database_index=_database_index))

#///////////////////////////////////////////////////////////////////////////////
def eval_filter_for_a_file(_filter, _filename, _size, _date):
    """
        eval_filter_for_a_file()
        ________________________________________________________________________

        Eval a file according to a filter and answers the following question :
        does the file matches what is described in the filter ?
        ________________________________________________________________________

        PARAMETERS
                o _filter        : a dict, see documentation:select
                o _filename     : (str) file's name
                o _size         : (int) file's size, in bytes.
                o _date         : (str)file's date

        RETURNED VALUE
                a boolean, giving the expected answer
    """
    res = True

    if res and "name" in _filter:
        res = thefilehastobeadded__filt_name(_filter, _filename)
    if res and "size" in _filter:
        res = thefilehastobeadded__filt_size(_filter, _size)
    if res and "date" in _filter:
        res = thefilehastobeadded__filt_date(_filter, _date)

    return res

#///////////////////////////////////////////////////////////////////////////////
def fill_select(_debug_datatime=None):
    """
        fill_select()
        ________________________________________________________________________

        Fill SELECT and SELECT_SIZE_IN_BYTES from the files stored in
        SOURCE_PATH. This function is used by action__select() .
        ________________________________________________________________________

        PARAMETERS
                o  _debug_datatime : None (normal value) or a dict of DTIME_FORMAT
                                     strings if in debug/test mode.

        RETURNED VALUE
                (int) the number of discarded files
    """
    global SELECT, SELECT_SIZE_IN_BYTES

    SELECT = {}  # see the SELECT format in the documentation:selection
    SELECT_SIZE_IN_BYTES = 0
    number_of_discarded_files = 0

    # these variables will be used by fill_select__checks() too.
    prefix = ""
    fullname = ""

    file_index = 0  # number of the current file in the source directory.
    for dirpath, _, filenames in os.walk(normpath(SOURCE_PATH)):
        for filename in filenames:
            file_index += 1
            fullname = os.path.join(normpath(dirpath), filename)
            size = os.stat(normpath(fullname)).st_size
            if _debug_datatime is None:
                time = datetime.utcfromtimestamp(os.path.getmtime(normpath(fullname)))
                time = time.replace(second=0, microsecond=0)
            else:
                time = datetime.strptime(_debug_datatime[fullname], DTIME_FORMAT)

            fname_no_extens, extension = get_filename_and_extension(normpath(filename))

	        # if we know the total amount of files to be selected (see the --infos option),
	        # we can add the percentage done :
            prefix = ""
            if INFOS_ABOUT_SRC_PATH[1] is not None and INFOS_ABOUT_SRC_PATH[1] != 0:
                prefix = "[{0:.4f}%]".format(file_index/INFOS_ABOUT_SRC_PATH[1]*100.0)

            if not thefilehastobeadded__filters(filename, size, time):
                number_of_discarded_files += 1

                msg("    - {0} discarded \"{1}\" " \
                    ": incompatibility with the filter(s)".format(prefix, fullname))
            else:
                tobeadded, partialhashid, hashid = thefilehastobeadded__db(fullname, size)

                if tobeadded and hashid in SELECT:
                    # tobeadded is True but hashid is already in SELECT; let's discard <filename> :
                    number_of_discarded_files += 1

                    msg("    - {0} (similar hashid among the files to be copied, " \
                        "in the source directory) " \
                        " discarded \"{1}\"".format(prefix, fullname))

                elif tobeadded:
                    # ok, let's add <filename> to SELECT...
                    SELECT[hashid] = \
                     SELECTELEMENT(fullname=fullname,
                                   partialhashid=partialhashid,
                                   path=dirpath,
                                   filename_no_extens=fname_no_extens,
                                   extension=extension,
                                   size=size,
                                   date=time.strftime(DTIME_FORMAT),
                                   targetname= \
                                        create_target_name(_parameters=PARAMETERS,
                                                           _hashid=hashid,
                                                           _filename_no_extens=fname_no_extens,
                                                           _path=dirpath,
                                                           _extension=extension,
                                                           _size=size,
                                                           _date=time.strftime(DTIME_FORMAT),
                                                           _database_index=len(TARGET_DB) + \
                                                                           len(SELECT)),
                                   targettags= \
                                        create_target_tags(_parameters=PARAMETERS,
                                                           _hashid=hashid,
                                                           _filename_no_extens=fname_no_extens,
                                                           _path=dirpath,
                                                           _extension=extension,
                                                           _size=size,
                                                           _date=time.strftime(DTIME_FORMAT),
                                                           _database_index=len(TARGET_DB) + \
                                                                           len(SELECT)))

                    msg("    + {0} selected \"{1}\" (file selected #{2})".format(prefix,
                                                                                 fullname,
                                                                                 len(SELECT)))
                    msg("       size={0}; date={1}".format(size, time.strftime(DTIME_FORMAT)))

                    SELECT_SIZE_IN_BYTES += size

                else:
                    # tobeadded is False : let's discard <filename> :
                    number_of_discarded_files += 1

                    msg("    - {0} (similar hashid in the database) " \
                        " discarded \"{1}\"".format(prefix, fullname))

    return fill_select__checks(_number_of_discarded_files=number_of_discarded_files,
                               _prefix=prefix,
                               _fullname=fullname)

#///////////////////////////////////////////////////////////////////////////////
def fill_select__checks(_number_of_discarded_files, _prefix, _fullname):
    """
        fill_select__checks()
        ________________________________________________________________________

        To be called at the end of fill_select() : remove some files from SELECT
        if they don't pass the checks :
                (1) future filename's can't be in conflict with another file in SELECT
                (2) future filename's can't be in conflict with another file already
                    stored in the target path :
        ________________________________________________________________________

        no PARAMETER
                o _number_of_discarded_files    : (int) see fill_select()
                o _prefix                       : (str) see fill_select()
                o _fullname                     : (str) see fill_select()

        RETURNED VALUE
                (int) the number of discarded files
    """
    msg("    o checking that there's no anomaly with the selected files...")

    # (1) future filename's can't be in conflict with another file in SELECT
    msg("    ... future filename's can't be in conflict with another file in SELECT...")
    to_be_discarded = []        # a list of hash.
    for (selectedfile_hash1, selectedfile_hash2) in itertools.combinations(SELECT, 2):

        if SELECT[selectedfile_hash1].targetname == SELECT[selectedfile_hash2].targetname:
            msg("    ! {0} discarded \"{1}\" : target filename \"{2}\" would be used " \
                "two times for two different files !".format(_prefix,
                                                             _fullname,
                                                             SELECT[selectedfile_hash2].targetname))

            to_be_discarded.append(selectedfile_hash2)

    # (2) future filename's can't be in conflict with another file already
    # stored in the target path :
    msg("    ... future filename's can't be in conflict with another file already")
    msg("        stored in the target path...")
    for selectedfile_hash in SELECT:
        if os.path.exists(os.path.join(normpath(TARGET_PATH),
                                       SELECT[selectedfile_hash].targetname)):
            msg("    ! {0} discarded \"{1}\" : target filename \"{2}\" already " \
                "exists in the target path !".format(_prefix,
                                                     _fullname,
                                                     SELECT[selectedfile_hash].targetname))

            to_be_discarded.append(selectedfile_hash)

    # final message and deletion :
    if len(to_be_discarded) == 0:
        msg("    o  everything ok : no anomaly detected. See details above.")
    else:
        if len(to_be_discarded) == 1:
            ending = "y"
        else:
            ending = "ies"
        msg("    !  beware : {0} anomal{1} detected. " \
            "See details above.".format(len(to_be_discarded),
                                        ending))

        for _hash in to_be_discarded:
            # e.g. , _hash may have discarded two times (same target name + file
            # already present on disk), hence the following condition :
            if _hash in SELECT:
                del SELECT[_hash]
                _number_of_discarded_files += 1

    return _number_of_discarded_files

#///////////////////////////////////////////////////////////////////////////////
def get_disk_free_space(_path):
    """
        get_disk_free_space()
        ________________________________________________________________________

        return the available space on disk() in bytes. Code for Windows system
        from http://stackoverflow.com/questions/51658/ .
        ________________________________________________________________________

        PARAMETER
                o _path : (str) the source path belonging to the disk to be
                          analysed.

        RETURNED VALUE
                the expected int(eger)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(_path),
                                                   None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        stat = os.statvfs(normpath(_path))
        return stat.f_bavail * stat.f_frsize

#///////////////////////////////////////////////////////////////////////////////
def get_filename_and_extension(_path):
    """
        get_filename_and_extension()
        ________________________________________________________________________

        Return
        ________________________________________________________________________

        PARAMETERS
                o  _path        : (str) the source path

        RETURNED VALUE
                (str)filename without extension, (str)the extension without the
                initial dot.
    """
    fname_no_extens, extension = os.path.splitext(_path)

    # the extension can't begin with a dot.
    if extension.startswith("."):
        extension = extension[1:]

    return fname_no_extens, extension

#///////////////////////////////////////////////////////////////////////////////
def goodbye():
    """
        goodbye()
        ________________________________________________________________________

        display a goodbye message.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    msg("=== exit (stopped at {0}; " \
        "total duration time : {1}) ===".format(datetime.now().strftime(DTIME_FORMAT),
                                                datetime.now() - TIMESTAMP_BEGIN))

#///////////////////////////////////////////////////////////////////////////////
def hashfile64(_filename, _stop_after=None):
    """
        hashfile64()
        ________________________________________________________________________

        return the footprint of a file, encoded with the base 64. If _stop_after
        is set to an integer, only the beginning of the file will be used to
        compute the hash (see PARTIALHASHID_BYTESNBR constant).
        ________________________________________________________________________

        PARAMETER
                o _filename : (str) file's name
                o _stop_after:(None/int) if None, the file will be entirely read,
                              otherwise, only the first _stop_after bytes will
                              be read.
        RETURNED VALUE
                the expected string. If you use sha256 as a hasher, the
                resulting string will be 44 bytes long. E.g. :
                        "YLkkC5KqwYvb3F54kU7eEeX1i1Tj8TY1JNvqXy1A91A"
    """
    # hasher used by the hashfile64() function.
    hasher = hashlib.sha256()

    nbr_of_bytes_read = 0
    with open(_filename, "rb") as afile:
        # a buffer of 65536 bytes is an optimized buffer.
        buf = afile.read(65536)
        while len(buf) > 0:
            nbr_of_bytes_read += 65536
            if _stop_after is not None and nbr_of_bytes_read >= _stop_after:
                break

            hasher.update(buf)
            buf = afile.read(65536)

    return b64encode(hasher.digest()).decode()

#///////////////////////////////////////////////////////////////////////////////
def is_ntfs_prefix_mandatory(_path):
    """
        is_ntfs_prefix_mandatory()
        ________________________________________________________________________

        Return True if the _path is a path in a systemfile requiring the NTFS
        prefix for long filenames.
        ________________________________________________________________________

        PARAMETER
            _path : (str)the path to be tested

        RETURNED VALUE
            a boolean
    """
    longpath = os.path.join(_path, "a"*250, "b"*250)
    longpath = os.path.normpath(os.path.abspath(os.path.expanduser(longpath)))
    res = False
    try:
        os.makedirs(longpath)
    except IOError:
        res = True

    if res is False:
        os.rmdir(longpath)

    return res

#///////////////////////////////////////////////////////////////////////////////
def logfile_opening():
    """
        logfile_opening()
        ________________________________________________________________________

        Open the log file and return the result of the called to open().
        If the ancient logfile exists, it is renamed to avoid its overwriting.
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                the _io.BufferedReader object returned by the call to open()
    """
    fullname = os.path.join(KATALSYS_SUBDIR, LOG_SUBSUBDIR, PARAMETERS["log file"]["name"])

    if PARAMETERS["log file"]["overwrite"] == "True":
        # overwrite :
        log_mode = "w"

        if os.path.exists(normpath(fullname)):
            shutil.copyfile(fullname,
                            os.path.join(KATALSYS_SUBDIR, LOG_SUBSUBDIR,
                                         "oldlogfile_" + \
                                         PARAMETERS["log file"]["name"] + \
                                         datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")))
    else:
        # let's append :
        log_mode = "a"

    return open(fullname, log_mode)

#///////////////////////////////////////////////////////////////////////////////
def main():
    """
        main()
        ________________________________________________________________________

        Main entry point.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE

        o  sys.exit(-1) is called if the config file is ill-formed.
        o  sys.exit(-2) is called if a KatalError exception is raised
        o  sys.exit(-3) is called if another exception is raised
    """
    global ARGS

    try:
        ARGS = read_command_line_arguments()
        check_args()

        welcome()
        main_warmup()
        main_actions_tags()
        main_actions()

        goodbye()

        if USE_LOGFILE:
            LOGFILE.close()

    except KatalError as exception:
        print("({0}) ! a critical error occured.\nError message : {1}".format(__projectname__,
                                                                              exception))
        sys.exit(-2)
    else:
        sys.exit(-3)

    sys.exit(0)

#///////////////////////////////////////////////////////////////////////////////
def main_actions():
    """
        main_actions()
        ________________________________________________________________________

        Call the different actions required by the arguments of the command line.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    if ARGS.cleandbrm:
        action__cleandbrm()

    if ARGS.reset:
        action__reset()

    if ARGS.targetkill:
        action__target_kill(ARGS.targetkill)

    if ARGS.whatabout:
        read_target_db()
        action__whatabout(ARGS.whatabout)

    if ARGS.select:
        read_target_db()
        read_filters()
        action__select()

        if not ARGS.mute and len(SELECT) > 0:
            answer = \
                input("\nDo you want to add the selected " \
                      "files to the target directory (\"{0}\") ? (y/N) ".format(TARGET_PATH))

            if answer in ("y", "yes"):
                action__add()
                show_infos_about_target_path()

    if ARGS.add:
        read_target_db()
        read_filters()
        action__select()
        action__add()
        show_infos_about_target_path()

    if ARGS.new:
        action__new(ARGS.new)

    if ARGS.rebase:
        action__rebase(ARGS.rebase)

    if ARGS.findtag:
        action__findtag(ARGS.findtag)

    if ARGS.downloaddefaultcfg is True:
        action__downloadefaultcfg()

#///////////////////////////////////////////////////////////////////////////////
def main_actions_tags():
    """
        main_actions_tags()
        ________________________________________________________________________

        Call the different actions required by the arguments of the command line.
        Function dedicated to the operations on tags.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    if ARGS.rmnotags:
        action__rmnotags()

    if ARGS.settagsstr:
        action__settagsstr(ARGS.settagsstr, ARGS.to)

    if ARGS.addtag:
        action__addtag(ARGS.addtag, ARGS.to)

    if ARGS.rmtags:
        action__rmtags(ARGS.to)

#///////////////////////////////////////////////////////////////////////////////
def main_warmup():
    """
        main_warmup()
        ________________________________________________________________________

        Initializations :

            o initialize DATABASE_FULLNAME
            o -si / --sourceinfos
            o -ti / --targetinfos
            o reading of the configuration file
            o --infos
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE

        o  sys.exit(-1) is called if the config file is ill-formed or missing.
    """
    global PARAMETERS, LOGFILE, DATABASE_FULLNAME

    #...........................................................................
    DATABASE_FULLNAME = os.path.join(normpath(TARGET_PATH), KATALSYS_SUBDIR, DATABASE_NAME)

    #...........................................................................
    if ARGS.targetinfos:
        show_infos_about_target_path()

    #...........................................................................
    # a special case : if the options --new//--downloaddefaultcfg have been used, let's quit :
    if ARGS.new is not None or ARGS.downloaddefaultcfg is True:
        return

    # let's find a config file to be read :
    msg_useddcfg = \
     "    ! error : can't find any config file !\n" \
     "    Use the -ddcfg/--downloaddefaultcfg option to download a default config file \n" \
     "    and move this downloaded file (a) either into the main Katal's config directory \n" \
     "    (choose between {0}) \n" \
     "    (b) either into the target/.katal/ directory .".format(possible_paths_to_cfg())

    configfile_name = ARGS.configfile
    if ARGS.configfile is None:

        for path in possible_paths_to_cfg():

            msg("  * trying to read \"{0}\" as a config file...".format(path))

            if os.path.exists(path):
                msg("   ... ok, let's try to read this config file...")
                configfile_name = path
                break

        if configfile_name is not None:
            msg("  * config file name : \"{0}\" (path : \"{1}\")".format(configfile_name,
                                                                         normpath(configfile_name)))
        else:
            msg(msg_useddcfg)
            sys.exit(-1)

    else:
        msg("  * config file given as a parameter : \"{0}\" " \
            "(path : \"{1}\"".format(configfile_name,
                                     normpath(configfile_name)))

        if not os.path.exists(normpath(configfile_name)) and ARGS.new is None:
            msg("  ! The config file \"{0}\" (path : \"{1}\") " \
                "doesn't exist. ".format(configfile_name,
                                         normpath(configfile_name)))

            if ARGS.downloaddefaultcfg is False:
                msg(msg_useddcfg)
            sys.exit(-1)

    # let's read the config file :
    PARAMETERS = read_parameters_from_cfgfile(configfile_name)
    if PARAMETERS is None:
        sys.exit(-1)
    else:
        msg("    ... config file found and read (ok)")

    # list of the expected directories : if one directory is missing, let's create it.
    create_subdirs_in_target_path()

    if USE_LOGFILE:
        LOGFILE = logfile_opening()
        welcome_in_logfile()

    if TARGET_PATH == SOURCE_PATH:
        msg("  ! warning : " \
            "source path and target path have the same value ! (\"{0}\")".format(TARGET_PATH))

    # we show the following informations :
    msg("  = so, let's use \"{0}\" as config file".format(configfile_name))
    msg("  = source directory : \"{0}\" (path : \"{1}\")".format(SOURCE_PATH,
                                                                 normpath(SOURCE_PATH)))

    #...........................................................................
    if ARGS.infos:
        action__infos()

    #...........................................................................
    if ARGS.sourceinfos:
        show_infos_about_source_path()

#///////////////////////////////////////////////////////////////////////////////
def modify_the_tag_of_some_files(_tag, _to, _mode):
    """
        modify_the_tag_of_some_files()
        ________________________________________________________________________

        Modify the tag(s) of some files.
        ________________________________________________________________________

        PARAMETERS
                o _tag          : (str) new tag(s)
                o _to           : (str) a string (wildcards accepted) describing
                                   what files are concerned
                o _mode         : (str) "append" to add _tag to the other tags
                                        "set" to replace old tag(s) by a new one
    """
    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        msg("    ! no database found.")
    else:
        db_connection = sqlite3.connect(DATABASE_FULLNAME)
        db_connection.row_factory = sqlite3.Row
        db_cursor = db_connection.cursor()

        files_to_be_modified = []       # a list of (hashids, name)
        for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
            if fnmatch.fnmatch(db_record["name"], _to):
                files_to_be_modified.append((db_record["hashid"], db_record["name"]))

        if len(files_to_be_modified) == 0:
            msg("    * no files match the given name(s) given as a parameter.")
        else:
            # let's apply the tag(s) to the <files_to_be_modified> :
            for hashid, filename in files_to_be_modified:

                msg("    o applying the tag string \"{0}\" to {1}.".format(_tag, filename))

                if ARGS.off:
                    pass

                elif _mode == "set":
                    sqlorder = 'UPDATE dbfiles SET tagsstr=? WHERE hashid=?'
                    db_connection.execute(sqlorder, (_tag, hashid))

                elif _mode == "append":
                    sqlorder = 'UPDATE dbfiles SET tagsstr = tagsstr || \"{0}{1}\" ' \
                               'WHERE hashid=\"{2}\"'.format(TAG_SEPARATOR, _tag, hashid)
                    db_connection.executescript(sqlorder)

                else:
                    raise KatalError("_mode argument \"{0}\" isn't known".format(_mode))

            db_connection.commit()

        db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def msg(_msg, _for_console=True, _for_logfile=True):
    """
        msg()
        ________________________________________________________________________

        Display a message on console, write the same message in the log file
        The messagfe isn't displayed on console if ARGS.mute has been set to
        True (see --mute argument)
        ________________________________________________________________________

        PARAMETERS
                o _msg          : (str) the message to be written
                o _for_console  : (bool) authorization to write on console
                o _for_logfile  : (bool) authorization to write in the log file

        no RETURNED VALUE
    """
    # first to the console : otherwise, if an error occurs by writing to the log
    # file, it would'nt possible to read the message.
    if not ARGS.mute and _for_console:
        print(_msg)

    if USE_LOGFILE and _for_logfile and LOGFILE is not None:
        LOGFILE.write(_msg+"\n")

#///////////////////////////////////////////////////////////////////////////////
def normpath(_path):
    """
        normpath()
        ________________________________________________________________________

        Return a human-readable (e.g. "~" -> "/home/myhome/" on Linux systems),
        normalized version of a path.

        The returned string may be used as a parameter given to by
        os.path.exists() .

        about the "\\\\?\\" prefix, see e.g. this thread on StackOverflow :
        http://stackjava-script.com/questions/1365797/
        the prefix allows Windows to deal with path whose length is greater than
        260 characters.
        ________________________________________________________________________

        PARAMETER : (str)_path

        RETURNED VALUE : the expected string
    """
    res = os.path.normpath(os.path.abspath(os.path.expanduser(_path)))

    if ARGS.usentfsprefix:
        res = res.replace("\\\\?\\", "")

    if res == ".":
        res = os.getcwd()

    if ARGS.usentfsprefix:
        res = "\\\\?\\"+res

    return res

#///////////////////////////////////////////////////////////////////////////////
def read_command_line_arguments():
    """
        read_command_line_arguments()
        ________________________________________________________________________

        Read the command line arguments.
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                return the argparse object.
    """
    parser = argparse.ArgumentParser(description="{0} v. {1}".format(__projectname__, __version__),
                                     epilog="by suizokukan AT orange DOT fr",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--add',
                        action="store_true",
                        help="select files according to what is described " \
                             "in the configuration file " \
                             "then add them to the target directory. " \
                             "This option can't be used with the --select one." \
                             "If you want more informations about the process, please " \
                             "use this option in combination with --infos .")

    parser.add_argument('--addtag',
                        type=str,
                        help="Add a tag to some file(s) in combination " \
                             "with the --to option. ")

    parser.add_argument('-cfg', '--configfile',
                        type=str,
                        help="set the name of the config file, e.g. config.ini")

    parser.add_argument('--cleandbrm',
                        action="store_true",
                        help="Remove from the database the missing files in the target path.")

    parser.add_argument('--copyto',
                        type=str,
                        help="To be used with the --findtag parameter. Copy the found files " \
                              "into an export directory.")

    parser.add_argument('-ddcfg', '--downloaddefaultcfg',
                        action="store_true",
                        help="Download the default config file and overwrite the file having " \
                             "the same name. This is done before the script reads the parameters " \
                             "in the config file")

    parser.add_argument('--findtag',
                        type=str,
                        help="find the files in the target directory with the given tag. " \
                              "The tag is a simple string, not a regex.")

    parser.add_argument('--infos',
                        action="store_true",
                        help="display informations about the source directory " \
                             "given in the configuration file. Help the --select/--add " \
                             "options to display more informations about the process : in " \
			     "this case, the --infos will be executed before --select/--add")

    parser.add_argument('-m', '--mute',
                        action="store_true",
                        help="no output to the console; no question asked on the console")

    parser.add_argument('--move',
                        action="store_true",
                        help="to be used with --select and --add : move the files, don't copy them")

    parser.add_argument('-n', '--new',
                        type=str,
                        help="create a new target directory")

    parser.add_argument('--off',
                        action="store_true",
                        help="don't write anything into the target directory or into " \
                             "the database, except into the current log file. " \
                             "Use this option to simulate an operation : you get the messages " \
                             "but no file is modified on disk, no directory is created.")

    parser.add_argument('--rebase',
                        type=str,
                        help="copy the current target directory into a new one : you " \
                             "rename the files in the target directory and in the database. " \
                             "First, use the --new option to create a new target directory, " \
                             "modify the .ini file of the new target directory " \
                             "(modify [target]name of the target files), " \
                             "then use --rebase with the name of the new target directory")

    parser.add_argument('--reset',
                        action="store_true",
                        help="Delete the database and the files in the target directory")

    parser.add_argument('--rmnotags',
                        action="store_true",
                        help="remove all files without a tag")

    parser.add_argument('--rmtags',
                        action="store_true",
                        help="remove all the tags of some file(s) in combination " \
                             "with the --to option. ")

    parser.add_argument('-s', '--select',
                        action="store_true",
                        help="select files according to what is described " \
                             "in the configuration file " \
                             "without adding them to the target directory. " \
                             "This option can't be used with the --add one." \
                     "If you want more informations about the process, please " \
                 "use this option in combination with --infos .")

    parser.add_argument('--settagsstr',
                        type=str,
                        help="give the tag to some file(s) in combination " \
                             "with the --to option. " \
                             "Overwrite the ancient tag string. " \
                             "If you want to empty the tags' string, please use a space, " \
                             "not an empty string : otherwise the parameter given " \
                             "to the script wouldn't be taken in account by the shell")

    parser.add_argument('-si', '--sourceinfos',
                        action="store_true",
                        help="display informations about the source directory")

    parser.add_argument('--strictcmp',
                        action="store_true",
                        help="to be used with --add or --select. Force a bit-to-bit comparision" \
                             "between files whose hashid-s is equal.")

    parser.add_argument('--targetpath',
                        type=str,
                        default=".",
                        help="target path, usually '.' . If you set path to . (=dot character)" \
                             ", it means that the source path is the current directory" \
                             " (=the directory where the script katal.py has been launched)")

    parser.add_argument('-ti', '--targetinfos',
                        action="store_true",
                        help="display informations about the target directory")

    parser.add_argument('-tk', '--targetkill',
                        type=str,
                        help="kill (=move to the trash directory) one file from " \
                             "the target directory." \
                             "DO NOT GIVE A PATH, just the file's name, " \
                             "without the path to the target directory")

    parser.add_argument('--to',
                        type=str,
                        help="give the name of the file(s) concerned by --settagsstr. " \
                        "wildcards accepted; e.g. to select all .py files, use '*.py' . " \
                        "Please DON'T ADD the path to the target directory, only the filenames")

    parser.add_argument('--usentfsprefix',
                        action="store_true",
                        help="Force the script to prefix filenames by a special string " \
                             "required by the NTFS for long filenames, namely \\\\?\\")

    parser.add_argument('--version',
                        action='version',
                        version="{0} v. {1}".format(__projectname__, __version__),
                        help="show the version and exit")

    parser.add_argument('--whatabout',
                        type=str,
                        help="Say if the file[the files in a directory] already in the " \
                             "given as a parameter is in the target directory " \
                             "notwithstanding its name.")

    return parser.parse_args()

#///////////////////////////////////////////////////////////////////////////////
def possible_paths_to_cfg():
    """
        possible_paths_to_cfg()
        ________________________________________________________________________

        return a list of the (str)paths to the config file.
        ________________________________________________________________________

        NO PARAMETER.

        RETURNED VALUE : the expected list of strings.
    """
    res = []

    res.append(os.path.join(os.path.expanduser("~"),
                            ".katal",
                            DEFAULT_CONFIGFILE_NAME))

    if platform.system() == 'Windows':
        res.append(os.path.join(os.path.expanduser("~"),
                                "Local Settings",
                                "Application Data",
                                "katal",
                                DEFAULT_CONFIGFILE_NAME))

    res.append(os.path.os.path.join(normpath("."),
                                    normpath(ARGS.targetpath),
                                    KATALSYS_SUBDIR,
                                    DEFAULT_CONFIGFILE_NAME))

    return res

#///////////////////////////////////////////////////////////////////////////////
def read_parameters_from_cfgfile(_configfile_name):
    """
        read_parameters_from_cfgfile()
        ________________________________________________________________________

        Read the configfile and return the parser or None if an error occured.
        ________________________________________________________________________

        PARAMETER
                o _configfile_name       : (str) config file name (e.g. katal.ini)

        RETURNED VALUE
                None if an error occured while reading the configuration file
                or the expected configparser.ConfigParser object=.
    """
    global USE_LOGFILE
    global TARGET_PATH, TARGETNAME_MAXLENGTH
    global SOURCE_PATH, SOURCENAME_MAXLENGTH
    global HASHID_MAXLENGTH, TAGSSTR_MAXLENGTH

    parser = configparser.ConfigParser()

    try:
        parser.read(_configfile_name)
        USE_LOGFILE = parser["log file"]["use log file"] == "True"
        TARGET_PATH = ARGS.targetpath
        TARGETNAME_MAXLENGTH = int(parser["display"]["target filename.max length on console"])
        SOURCE_PATH = parser["source"]["path"]
        SOURCENAME_MAXLENGTH = int(parser["display"]["source filename.max length on console"])
        HASHID_MAXLENGTH = int(parser["display"]["hashid.max length on console"])
        TAGSSTR_MAXLENGTH = int(parser["display"]["tag.max length on console"])
    except BaseException as exception:
        msg("  ! An error occured while reading " \
            "the config file \"{0}\".".format(_configfile_name))
        msg("  ! Python message : \"{0}\"".format(exception))
        return None

    return parser

#///////////////////////////////////////////////////////////////////////////////
def read_filters():
    """
        read_filters()
        ________________________________________________________________________

        Initialize FILTERS from the configuration file.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    FILTERS.clear()

    stop = False
    filter_index = 1

    while not stop:
        if not PARAMETERS.has_section("source.filter"+str(filter_index)):
            stop = True
        else:
            FILTERS[filter_index] = dict()

            if PARAMETERS.has_option("source.filter"+str(filter_index), "name"):
                FILTERS[filter_index]["name"] = \
                               re.compile(PARAMETERS["source.filter"+str(filter_index)]["name"])

            if PARAMETERS.has_option("source.filter"+str(filter_index), "iname"):
                FILTERS[filter_index]["name"] = \
                               re.compile(PARAMETERS["source.filter"+str(filter_index)]["iname"],
                                          re.IGNORECASE)

            if PARAMETERS.has_option("source.filter"+str(filter_index), "size"):
                FILTERS[filter_index]["size"] = \
                                PARAMETERS["source.filter"+str(filter_index)]["size"]

            if PARAMETERS.has_option("source.filter"+str(filter_index), "date"):
                FILTERS[filter_index]["date"] = \
                                PARAMETERS["source.filter"+str(filter_index)]["date"]

        filter_index += 1

#///////////////////////////////////////////////////////////////////////////////
def read_target_db():
    """
        read_target_db()
        ________________________________________________________________________

        Read the database stored in the target directory and initialize
        TARGET_DB.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    if not os.path.exists(normpath(DATABASE_FULLNAME)):
        create_empty_db(normpath(DATABASE_FULLNAME))

    db_connection = sqlite3.connect(DATABASE_FULLNAME)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        TARGET_DB[db_record["hashid"]] = (db_record["partialhashid"],
                                          db_record["size"],
                                          db_record["sourcename"])

    db_connection.close()

#/////////////////////////////////////////////////////////////////////////////////////////
def remove_illegal_characters(_src):
    """
        remove_illegal_characters()
        ________________________________________________________________________

        Replace some illegal characters by the underscore character. Use this function
        to create files on various plateforms.
        ________________________________________________________________________

        PARAMETER
                o _src   : (str) the source string

        RETURNED VALUE
                the expected string, i.e. <_src> without illegal characters.
    """
    res = _src
    for char in ("*", "/", "\\", ".", "[", "]", ":", ";", "|", "=", ",", "?", "<", ">", "-", " "):
        res = res.replace(char, "_")
    return res

#///////////////////////////////////////////////////////////////////////////////
def shortstr(_str, _max_length):
    """
        shortstr()
        ________________________________________________________________________

        The function returns a shortened version of a string.
        ________________________________________________________________________

        PARAMETER
                o _str          : (src) the source string
                o _max_length   : (int) the maximal length of the string

        RETURNED VALUE
                the expected string
    """
    if len(_str) > _max_length:
        return "[...]"+_str[-(_max_length-5):]
    return _str

#///////////////////////////////////////////////////////////////////////////////
def show_infos_about_source_path():
    """
        show_infos_about_source_path()
        ________________________________________________________________________

        Display informations about the source directory.
		Initialize INFOS_ABOUT_SRC_PATH.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    global INFOS_ABOUT_SRC_PATH

    msg("  = informations about the \"{0}\" " \
        "(path: \"{1}\") source directory =".format(SOURCE_PATH,
                                                    normpath(SOURCE_PATH)))

    if not os.path.exists(normpath(SOURCE_PATH)):
        msg("    ! can't find source path \"{0}\" .".format(SOURCE_PATH))
        return
    if not os.path.isdir(normpath(SOURCE_PATH)):
        msg("    ! source path \"{0}\" isn't a directory .".format(SOURCE_PATH))
        return

    if is_ntfs_prefix_mandatory(SOURCE_PATH):
        msg("    ! the source path should be used with the NTFS prefix for long filenames.")

        if not ARGS.usentfsprefix:
            msg("    ! ... but the --usentfsprefix argument wasn't given !")
            msg("    ! You may encounter an IOError, or a FileNotFound error.")
            msg("    ! If so, please use the --usentfsprefix argument.")
            msg("")

    total_size = 0
    files_number = 0
    extensions = dict()  # (str)extension : [number of files, total size]
    for dirpath, _, fnames in os.walk(normpath(SOURCE_PATH)):
        for filename in fnames:
            fullname = os.path.join(normpath(dirpath), filename)
            size = os.stat(normpath(fullname)).st_size
            extension = os.path.splitext(normpath(filename))[1]

            if extension in extensions:
                extensions[extension][0] += 1
                extensions[extension][1] += size
            else:
                extensions[extension] = [1, size]

            total_size += size
            files_number += 1

    msg("    o files number : {0} file(s)".format(files_number))
    msg("    o total size : {0}".format(size_as_str(total_size)))
    msg("    o list of all extensions ({0} extension(s) found): ".format(len(extensions)))
    for extension in sorted(extensions):
        msg("      - {0:15} : {1} files, {2}".format(extension,
                                                     extensions[extension][0],
                                                     size_as_str(extensions[extension][1])))

    INFOS_ABOUT_SRC_PATH = (total_size, files_number, extensions)

#///////////////////////////////////////////////////////////////////////////////
def show_infos_about_target_path():
    """
        show_infos_about_target_path
        ________________________________________________________________________

        Display informations about the the target directory
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                (int) 0 if ok, -1 if an error occured
    """
    msg("  = informations about the \"{0}\" " \
        "(path: \"{1}\") target directory =".format(TARGET_PATH,
                                                    normpath(TARGET_PATH)))

    if is_ntfs_prefix_mandatory(TARGET_PATH):
        msg("    ! the target path should be used with the NTFS prefix for long filenames.")

        if not ARGS.usentfsprefix:
            msg("    ! ... but the --usentfsprefix argument wasn't given !")
            msg("    ! You may encounter an IOError, or a FileNotFound error.")
            msg("    ! If so, please use the --usentfsprefix argument.")
            msg("")

    def draw_table(_rows, _data):
        """
                Draw a table with some <_rows> and fill it with _data.
        rows= ( ((str)row_name, (int)max length for this row), (str)separator)
        e.g. :
        rows= ( ("hashid", HASHID_MAXLENGTH, "|"), )

        _data : ( (str)row_content1, (str)row_content2, ...)
        """

        def draw_line():
            " draw a simple line made of + and -"
            string = " "*6 + "+"
            for _, row_maxlength, _ in rows:
                string += "-"*(row_maxlength+2) + "+"
            msg(string)

        # real rows' widths : it may happen that a row's width is greater than
        # the maximal value given in _rows since the row name is longer than
        # this maximal value.
        rows = []
        for row_name, row_maxlength, row_separator in _rows:
            rows.append((row_name, max(len(row_name), row_maxlength), row_separator))

        # header :
        draw_line()

        string = " "*6 + "|"
        for row_name, row_maxlength, row_separator in rows:
            string += " " + row_name + " "*(row_maxlength-len(row_name)+1) + row_separator
        msg(string)

        draw_line()

        # data :
        for linedata in _data:
            string = "      |"
            for row_index, row_content in enumerate(linedata):
                text = shortstr(row_content, _rows[row_index][1])
                string += " " + \
                          text + \
                          " "*(rows[row_index][1]-len(text)) + \
                          " " + rows[row_index][2]
            msg(string)  # let's write the computed line

        draw_line()

    if not os.path.exists(normpath(TARGET_PATH)):
        msg("Can't find target path \"{0}\".".format(TARGET_PATH))
        return -1
    if not os.path.isdir(normpath(TARGET_PATH)):
        msg("target path \"{0}\" isn't a directory.".format(TARGET_PATH))
        return -1

    if not os.path.exists(os.path.join(normpath(TARGET_PATH),
                                       KATALSYS_SUBDIR, DATABASE_NAME)):
        msg("    o no database in the target directory o")
    else:
        db_connection = sqlite3.connect(DATABASE_FULLNAME)
        db_connection.row_factory = sqlite3.Row
        db_cursor = db_connection.cursor()

        # there's no easy way to know the size of a table in a database,
        # so we can't display the "empty database" warning before the following
        # code which reads the table.
        rows_data = []
        row_index = 0
        for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
            sourcedate = \
                datetime.utcfromtimestamp(db_record["sourcedate"]).strftime(DTIME_FORMAT)

            rows_data.append((db_record["hashid"],
                              db_record["name"],
                              tagsstr_repr(db_record["tagsstr"]),
                              db_record["sourcename"],
                              sourcedate))

            row_index += 1

        if row_index == 0:
            msg("    ! (empty database)")
        else:
            msg("    o {0} file(s) in the database :".format(row_index))
            # beware : characters like "║" are forbidden (think to the cp1252 encoding
            # required by Windows terminal)
            draw_table(_rows=(("hashid/base64", HASHID_MAXLENGTH, "|"),
                              ("name", TARGETNAME_MAXLENGTH, "|"),
                              ("tags", TAGSSTR_MAXLENGTH, "|"),
                              ("source name", SOURCENAME_MAXLENGTH, "|"),
                              ("source date", DTIME_FORMAT_LENGTH, "|")),
                       _data=rows_data)

        db_connection.close()

    return 0

#///////////////////////////////////////////////////////////////////////////////
def size_as_str(_size):
    """
        size_as_str()
        ________________________________________________________________________

        Return a size in bytes as a human-readable string.
        ________________________________________________________________________

        PARAMETER
                o _size         : (int) size in bytes

        RETURNED VALUE
                a str(ing)
    """
    if _size == 0:
        res = "0 byte"
    elif _size < 1000:
        res = "{0} bytes".format(_size)
    elif _size < 9000:
        res = "{0} kB ({1} bytes)".format(_size/1000.0, _size)
    elif _size < 9000000:
        res = "~{0:.2f} MB ({1} bytes)".format(_size/1000000.0, _size)
    elif _size < 9000000000:
        res = "~{0:.2f} GB ({1} bytes)".format(_size/1000000000.0, _size)
    elif _size < 9000000000000:
        res = "~{0:.2f} TB ({1} bytes)".format(_size/1000000000000.0, _size)
    elif _size < 9000000000000000:
        res = "~{0:.2f} PB ({1} bytes)".format(_size/1000000000000000.0, _size)
    elif _size < 9000000000000000000:
        res = "~{0:.2f} EB ({1} bytes)".format(_size/1000000000000000000.0, _size)
    else:
        res = "~{0:.2f} ZB ({1} bytes)".format(_size/1000000000000000000000.0, _size)

    return res

#//////////////////////////////////////////////////////////////////////////////
def tagsstr_repr(_tagsstr):
    """
        tagsstr_repr()
        ________________________________________________________________________

        Improve the way a tags' string can be displayed.
        ________________________________________________________________________

        PARAMETER
            _tagsstr : the raw tags' string

        RETURNED VALUE
            the expected (str)string
    """
    # let's remove the first tag separator :
    tagsstr = _tagsstr
    if tagsstr.startswith(TAG_SEPARATOR):
        tagsstr = tagsstr[1:]

    return tagsstr

#///////////////////////////////////////////////////////////////////////////////
def thefilehastobeadded__db(_filename, _size):
    """
        thefilehastobeadded__db()
        ________________________________________________________________________

        Return True if the file isn't already known in the database.
        ________________________________________________________________________

        PARAMETERS
                o _filename     : (str) file's name
                o _size         : (int) file's size, in bytes.

        RETURNED VALUE
                either (False, None, None)
                either (True, partial hashid, hashid)
    """
    # a list of hashid(s) :
    res = []

    # (1) how many file(s) in the database have a size equal to _size ?
    for hashid in TARGET_DB:
        _, target_size, _ = TARGET_DB[hashid]
        if target_size == _size:
            res.append(hashid)

    if len(res) == 0:
        return (True,
                hashfile64(_filename=_filename,
                           _stop_after=PARTIALHASHID_BYTESNBR),
                hashfile64(_filename=_filename))

    # (2) how many file(s) among those in <res> have a partial hashid equal
    # to the partial hashid of _filename ?
    new_res = []
    src_partialhashid = hashfile64(_filename=_filename,
                                   _stop_after=PARTIALHASHID_BYTESNBR)
    for hashid in res:
        target_partialhashid, _, _ = TARGET_DB[hashid]
        if target_partialhashid == src_partialhashid:
            new_res.append(hashid)

    res = new_res
    if len(res) == 0:
        return (True,
                src_partialhashid,
                hashfile64(_filename=_filename))

    # (3) how many file(s) among those in <res> have an hashid equal to the
    # hashid of _filename ?
    new_res = []
    src_hashid = hashfile64(_filename=_filename)
    for hashid in res:
        target_hashid, _, _ = TARGET_DB[hashid]
        if target_hashid == src_hashid:
            new_res.append(hashid)

    res = new_res
    if len(res) == 0:
        return (True,
                src_partialhashid,
                src_hashid)

    if not ARGS.strictcmp:
        return (False, None, None)

    # (4) bit-to-bit comparision :
    for hashid in res:
        if not filecmp.cmp(_filename, TARGET_DB[hashid][2], shallow=False):
            return (True,
                    src_partialhashid,
                    src_hashid)

    return (False, None, None)

#///////////////////////////////////////////////////////////////////////////////
def thefilehastobeadded__filters(_filename, _size, _date):
    """
        thefilehastobeadded__filters()
        ________________________________________________________________________

        Return True if a file (_filename, _size) can be choosed and added to
        the target directory, according to the filters (stored in FILTERS).
        ________________________________________________________________________

        PARAMETERS
                o _filename     : (str) file's name
                o _size         : (int) file's size, in bytes.
                o _date         : (str) file's date

        RETURNED VALUE
                a boolean, giving the expected answer
    """
    evalstr = PARAMETERS["source"]["eval"]

    for filter_index in FILTERS:
        _filter = FILTERS[filter_index]

        evalstr = evalstr.replace("filter"+str(filter_index),
                                  str(eval_filter_for_a_file(_filter, _filename, _size, _date)))

    try:
        # eval() IS a dangerous function : see the note about AUTHORIZED_EVALCHARS.
        for char in evalstr:
            if char not in AUTHORIZED_EVALCHARS:
                raise KatalError("Error in configuration file : " \
                                   "trying to compute the \"{0}\" string; " \
                                   "wrong character '{1}'({2}) " \
                                   "used in the string to be evaluated. " \
                                   "Authorized " \
                                   "characters are {3}".format(evalstr,
                                                               char,
                                                               unicodedata.name(char),
                                                               "|"+"|".join(AUTHORIZED_EVALCHARS)))
        return eval(evalstr)

    except BaseException as exception:
        raise KatalError("The eval formula in the config file (\"{0}\")" \
                           "contains an error. Python message : \"{1}\"".format(evalstr,
                                                                                exception))

#///////////////////////////////////////////////////////////////////////////////
def thefilehastobeadded__filt_date(_filter, _date):
    """
        thefilehastobeadded__filt_date()
        ________________________________________________________________________

        Function used by thefilehastobeadded__filters() : check if the date of a
        file matches the filter given as a parameter.
        ________________________________________________________________________

        PARAMETERS
                o _filter        : a dict object; see documentation:selection
                o _date         : (str) file's datestamp (object datetime.datetime)

        RETURNED VALUE
                the expected boolean
    """
    # beware ! the order matters (<= before <, >= before >)
    if _filter["date"].startswith("="):
        return _date == datetime.strptime(_filter["date"][1:], DTIME_FORMAT)
    elif _filter["date"].startswith(">="):
        return _date >= datetime.strptime(_filter["date"][2:], DTIME_FORMAT)
    elif _filter["date"].startswith(">"):
        return _date > datetime.strptime(_filter["date"][1:], DTIME_FORMAT)
    elif _filter["date"].startswith("<="):
        return _date < datetime.strptime(_filter["date"][2:], DTIME_FORMAT)
    elif _filter["date"].startswith("<"):
        return _date < datetime.strptime(_filter["date"][1:], DTIME_FORMAT)
    else:
        raise KatalError("Can't analyse a 'date' field : "+_filter["date"])

#///////////////////////////////////////////////////////////////////////////////
def thefilehastobeadded__filt_name(_filter, _filename):
    """
        thefilehastobeadded__filt_name()
        ________________________________________________________________________

        Function used by thefilehastobeadded__filters() : check if the name of a
        file matches the filter given as a parameter.
        ________________________________________________________________________

        PARAMETERS
                o _filter           : a dict object; see documentation:selection
                o _filename         : (str) file's name

        RETURNED VALUE
                the expected boolean
    """
    # nb : _filter["name"] can either be a case sensitive regex, either
    #      a case insensitive regex. See the read_filters() function.
    return re.match(_filter["name"], _filename) is not None

#///////////////////////////////////////////////////////////////////////////////
def thefilehastobeadded__filt_size(_filter, _size):
    """
        thefilehastobeadded__filt_size()
        ________________________________________________________________________

        Function used by thefilehastobeadded__filters() : check if the size of a
        file matches the filter given as a parameter.
        ________________________________________________________________________

        PARAMETERS
                o _filter        : a dict object; see documentation:selection
                o _size         : (int) file's size

        RETURNED VALUE
                the expected boolean
    """
    res = False

    filter_size = _filter["size"] # a string like ">999" : see documentation:selection

    multiple = 1
    for suffix, _multiple in MULTIPLES:
        if filter_size.endswith(suffix):
            multiple = _multiple
            filter_size = filter_size[:-len(suffix)]
            break

    if multiple == 1 and not filter_size[-1].isdigit():
        raise KatalError("Can't analyse {0} in the filter. " \
                         "Available multiples are : {1}".format(filter_size,
                                                                MULTIPLES))

    # beware !  the order matters (<= before <, >= before >)
    if filter_size.startswith(">="):
        if _size >= float(filter_size[2:])*multiple:
            res = True
    elif filter_size.startswith(">"):
        if _size > float(filter_size[1:])*multiple:
            res = True
    elif filter_size.startswith("<="):
        if _size <= float(filter_size[2:])*multiple:
            res = True
    elif filter_size.startswith("<"):
        if _size < float(filter_size[1:])*multiple:
            res = True
    elif filter_size.startswith("="):
        if _size == float(filter_size[1:])*multiple:
            res = True
    else:
        raise KatalError("Can't analyse {0} in the filter.".format(filter_size))

    return res

#///////////////////////////////////////////////////////////////////////////////
def welcome():
    """
        welcome()
        ________________________________________________________________________

        Display a welcome message with some very broad informations about the
        program. This function may be called before reading the configuration
        file (confer the variable PARAMETERS).

        This function is called before the opening of the log file; hence, all
        the messages are only displayed on console (see welcome_in_logfile
        function)
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE

        sys.exit(-1) if the config file doesn't exist.
    """
    strmsg = "=== {0} v.{1} " \
             "(launched at {2}) ===".format(__projectname__,
                                            __version__,
                                            TIMESTAMP_BEGIN.strftime("%Y-%m-%d %H:%M:%S"))
    msg("="*len(strmsg))
    msg(strmsg)
    msg("="*len(strmsg))

    # if the target file doesn't exist, it will be created later by main_warmup() :
    if ARGS.new is None and ARGS.downloaddefaultcfg is False:
        msg("  = target directory given as parameter : \"{0}\" " \
            "(path : \"{1}\")".format(ARGS.targetpath,
                                      normpath(ARGS.targetpath)))

        if ARGS.configfile is not None:
            msg("  = expected config file : \"{0}\" " \
                "(path : \"{1}\")".format(ARGS.configfile,
                                          normpath(ARGS.configfile)))
        else:
            msg("  = no config file specified on the command line : " \
                "let's search a config file...")

    if ARGS.off:
        msg("  = WARNING                                                               =")
        msg("  = --off option detected :                                               =")
        msg("  =                no file will be modified, no directory will be created =")
        msg("  =                but the corresponding messages will be written in the  =")
        msg("  =                log file.                                              =")

    if ARGS.move:
        msg("  = WARNING                                                               =")
        msg("  = --move option detected :                                              =")
        msg("  =                 the files will be moved (NOT copied) in the target    =")
        msg("  =                 directory.                                            =")

#///////////////////////////////////////////////////////////////////////////////
def welcome_in_logfile():
    """
        welcome_in_logfile()
        ________________________________________________________________________

        The function writes in the log file a welcome message with some very
        broad informations about the program.

        This function has to be called after the opening of the log file.
        This function doesn't write anything on the console.
        See welcome() function for more informations since welcome() and
        welcome_in_logfile() do the same job, the first on console, the
        second in the log file.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    msg(_msg="=== {0} v.{1} " \
        "(launched at {2}) ===".format(__projectname__,
                                       __version__,
                                       TIMESTAMP_BEGIN.strftime("%Y-%m-%d %H:%M:%S")),
        _for_logfile=True,
        _for_console=False)

#///////////////////////////////////////////////////////////////////////////////
#/////////////////////////////// STARTING POINT ////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    main()
