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
        (leaving aside the doubloons), copy the selected files in a target
        directory.
        Once the target directory is filled with some files, a database is added
        to the directory to avoid future doubloons. You can add new files to
        the target directory by using Katal one more time, with a different
        source directory.
        ________________________________________________________________________

        see README.md for more documentation.
"""
# Pylint : disabling the "Using the global statement (global-statement)" warning
# pylint: disable=W0603

# Pylint : disabling the "Too many lines in module" error
# pylint: disable=C0302

# Pylint : disabling the "Use of eval" warning
# -> eval() is used in the the_file_has_to_be_added() function
# -> see below how this function is protected against malicious code execution.
# -> see AUTHORIZED_EVALCHARS
# pylint: disable=W0123

import argparse
from base64 import b64encode
from collections import namedtuple
import configparser
import ctypes
import hashlib
from datetime import datetime
import fnmatch
import os
import platform
import re
import shutil
import sqlite3
import urllib.request
import sys
import unicodedata

PROGRAM_NAME = "Katal"
PROGRAM_VERSION = "0.0.7"

# when the program verifies that there's enough free space on disk, it multiplies
# the required amount of space by these coefficient
FREESPACE_MARGIN = 1.1

DEFAULT_CONFIGFILE_NAME = "katal.ini"
DATABASE_NAME = "katal.db"
TAG_SEPARATOR = ";"  # symbol used in the database between two tags.

TIMESTAMP_BEGIN = datetime.now()  # timestamp used to compute the total time of execution.

PARAMETERS = None # see documentation:configuration file

SOURCE_PATH = ""  # initialized from the configuration file.
SOURCENAME_MAXLENGTH = 0  # initialized from the configuration file : this value
                          # fixed the way source filenames are displayed.
INFOS_ABOUT_SRC_PATH = (None, None, None)  # initialized by show_infos_about_source_path()
                                           # ((int)total_size, (int)files_number, (dict)extensions)

TARGET_PATH = ""  # initialized from the configuration file.
TARGETNAME_MAXLENGTH = 0  # initialized from the configuration file : this value
                          # fixed the way source filenames are displayed.
TARGET_DB = []  # see documentation:database; initializd by read_target_db()

# maximal length of the hashids displayed. Can't be greater than 44.
HASHID_MAXLENGTH = 20

# maximal length of the strtags displayed.
STRTAGS_MAXLENGTH = 20

LOGFILE = None  # the file descriptor, initialized by logfile_opening()
USE_LOG_FILE = False  # (bool) initialized from the configuration file
LOG_VERBOSITY = "high"  # initialized from the configuration file (see documentation:logfile)

# SELECT is made of SELECTELEMENT objects, where data about the original files
# are stored.
SELECTELEMENT = namedtuple('SELECTELEMENT', ["complete_name",
                                             "path",
                                             "filename_no_extens",
                                             "extension",
                                             "size",
                                             "date"])

SELECT = {} # see documentation:selection; initialized by action__select()
SELECT_SIZE_IN_BYTES = 0  # initialized by action__select()
SIEVES = {}  # see documentation:selection; initialized by read_sieves()

# date's string format, e.g. "2015-09-17 20:01"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DATETIME_FORMAT_LENGTH = 16

# this minimal subset of characters are the only characters to be used in the
# eval() function. Other characters are forbidden to avoid malicious code execution.
# keywords an symbols : sieve, parentheses, and, or, not, xor, True, False
#                       space, &, |, ^, (, ), 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
AUTHORIZED_EVALCHARS = (' ',
                        'T', 'F',
                        'a', 'd', 'l', 's', 'i', 'e', 'v', 'r', 'u', 'x',
                        'n', 'o', 't',
                        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        '&', '|', '^', '(', ')')

################################################################################
class ProjectError(BaseException):
    """
        ProjectError class

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

        Add the source files to the target path.
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                (int) 0 if success, -1 if an error occured.
    """
    msg("  = copying data =")

    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()

    if get_disk_free_space(TARGET_PATH) < SELECT_SIZE_IN_BYTES*FREESPACE_MARGIN:
        msg("    ! Not enough space on disk. Stopping the program.")
        # returned value : -1 = error
        return -1

    files_to_be_added = []
    len_select = len(SELECT)
    for index, hashid in enumerate(SELECT):

        short_target_name = create_target_name(_hashid=hashid,
                                               _database_index=len(TARGET_DB) + index)

        complete_source_filename = SELECT[hashid].complete_name
        target_name = os.path.join(TARGET_PATH, short_target_name)

        sourcedate = \
         datetime.fromtimestamp(os.path.getmtime(complete_source_filename)).replace(second=0,
                                                                                    microsecond=0)
        # converting the datetime object in epoch value (=the number of seconds from 1970-01-01 :
        sourcedate -= datetime(1970, 1, 1)
        sourcedate = sourcedate.total_seconds()

        msg("    ... ({0}/{1}) copying \"{2}\" to \"{3}\" .".format(index+1,
                                                                    len_select,
                                                                    complete_source_filename,
                                                                    target_name))
        shutil.copyfile(complete_source_filename,
                        target_name)

        files_to_be_added.append((hashid,
                                  short_target_name,
                                  complete_source_filename,
                                  sourcedate,
                                  ""))

    msg("    = all files have been copied, updating the database... =")

    try:
        db_cursor.executemany('INSERT INTO dbfiles VALUES (?,?,?,?,?)', files_to_be_added)
    except sqlite3.IntegrityError as exception:
        msg("!!! An error occured while writing the database : "+str(exception))
        msg("!!! files_to_be_added : ")
        for file_to_be_added in files_to_be_added:
            msg("     ! hashid={0}; name={1}; sourcename={2}; " \
                "sourcedate={3}; strtags={4}".format(*file_to_be_added))
        raise ProjectError("An error occured while writing the database : "+str(exception))
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
    msg("  = let's add the string tag \"{0}\" to {1}".format(_tag, _to))
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
    msg("    = clean the database : remove missing files from the target directory =")

    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
    if not os.path.exists(db_filename):
        msg("    ! Found no database.")
        return

    db_connection = sqlite3.connect(db_filename)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    files_to_be_rmved_from_the_db = []  # hashid of the files
    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        if not os.path.exists(os.path.join(TARGET_PATH, db_record["name"])):
            files_to_be_rmved_from_the_db.append(db_record["hashid"])
            msg("    o about to remove \"{0}\"".format(os.path.join(TARGET_PATH,
                                                                    db_record["filename"])))

    if len(files_to_be_rmved_from_the_db) == 0:
        msg("    ! no file to be removed : the database is ok.")
    else:
        for hashid in files_to_be_rmved_from_the_db:
            db_cursor.execute("DELETE FROM dbfiles WHERE hashid=?", (hashid,))

            db_connection.commit()
            msg("    o ... done")

    db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def action__downloadefaultcfg():
    """
        action__downloadefaultcfg()
        ________________________________________________________________________

        Download the default configuration file and (over)writes it in the current
        directory.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    url = "https://raw.githubusercontent.com/suizokukan/katal/master/katal.ini"

    msg("  = downloading the configuration file =")
    msg("  ... downloading {0} from {1}".format(DEFAULT_CONFIGFILE_NAME, url))

    with urllib.request.urlopen(url) as response, open(DEFAULT_CONFIGFILE_NAME, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

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
                "in the config file. Please wait... =")
    msg("  o sieves :")
    for sieve_index in SIEVES:
        msg("    o sieve #{0} : {1}".format(sieve_index,
                                            SIEVES[sieve_index]))
    msg("  o file list :")

    # let's initialize SELECT and SELECT_SIZE_IN_BYTES :
    number_of_discarded_files = fill_select()

    msg("    o size of the selected files : {0}".format(size_as_str(SELECT_SIZE_IN_BYTES)))

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
        for index, hashid in enumerate(SELECT):

            complete_source_filename = SELECT[hashid].complete_name
            short_target_name = create_target_name(_hashid=hashid,
                                                   _database_index=len(TARGET_DB) + index)

            target_name = os.path.join(TARGET_PATH, short_target_name)

            msg("    o e.g. ... \"{0}\" " \
                "would be copied as \"{1}\" .".format(complete_source_filename,
                                                      target_name))

            example_index += 1

            if example_index > 5:
                break

#///////////////////////////////////////////////////////////////////////////////
def action__rmtags(_to):
    """
        action__rmtags()
        ________________________________________________________________________

        Remove the string tag(s) in the target directory, overwriting ancient tags.
        ________________________________________________________________________

        PARAMETERS
                o _to           : (str) a regex string describing what files are
                                  concerned
    """
    msg("  = let's remove the string tags in {0}".format(_to))
    action__setstrtags(_strtags="", _to=_to)

#///////////////////////////////////////////////////////////////////////////////
def action__setstrtags(_strtags, _to):
    """
        action__setstrtags()
        ________________________________________________________________________

        Set the string tag(s) in the target directory, overwriting ancient tags.
        ________________________________________________________________________

        PARAMETERS
                o _strtags      : (str) the new string tags
                o _to           : (str) a regex string describing what files are
                                  concerned
    """
    msg("  = let's apply the string tag \"{0}\" to {1}".format(_strtags, _to))
    modify_the_tag_of_some_files(_tag=_strtags, _to=_to, _mode="set")

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
                        directory, -2 if the file doesn't exist in the database.
    """
    msg("  = about to kill \"{0}\" from the target directory " \
        "and from its database =".format(_filename))
    if not os.path.exists(os.path.join(TARGET_PATH, _filename)):
        msg("    ! Can't find \"{0}\" file on disk.".format(_filename))
        return -1

    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
    db_connection = sqlite3.connect(db_filename)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    filename_hashid = None
    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        if db_record["name"] == _filename:
            filename_hashid = db_record["hashid"]

    if filename_hashid is None:
        msg("    ! Can't find \"{0}\" file in the database.".format(_filename))
        res = -2
    else:
        # let's remove _filename from the target directory :
        os.remove(os.path.join(TARGET_PATH, _filename))

        # let's remove _filename from the database :
        db_cursor.execute("DELETE FROM dbfiles WHERE hashid=?", (filename_hashid,))

        res = 0  # success.

    db_connection.commit()
    db_connection.close()

    msg("    ... done")
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
    if ARGS.add == True and ARGS.select == True:
        raise ProjectError("--select and --add can't be used simultaneously")

    # --setstrtags must be used with --to :
    if ARGS.setstrtags and not ARGS.to:
        raise ProjectError("please use --to in combination with --setstrtags")

    # --addtag must be used with --to :
    if ARGS.addtag and not ARGS.to:
        raise ProjectError("please use --to in combination with --addtag")

    # --rmtags must be used with --to :
    if ARGS.rmtags and not ARGS.to:
        raise ProjectError("please use --to in combination with --rmtags")

#/////////////////////////////////////////////////////////////////////////////////////////
def create_target_name(_hashid, _database_index):
    """
        create_target_name()
        ________________________________________________________________________

        Create the name of a file (a target file) from various informations
        stored in SELECT. The function reads the string stored in
        PARAMETERS["target"]["name of the target files"] and replaces some
        keywords in the string by the parameters given to this function.

        see the available keywords in the documentation.
            (see documentation:configuration file)
        ________________________________________________________________________

        PARAMETERS
                o _hashid                       : (str)
                o _database_index               : (int)

        RETURNED VALUE
                the expected string
    """
    target_name = PARAMETERS["target"]["name of the target files"]

    target_name = target_name.replace("HASHID",
                                      _hashid)

    target_name = target_name.replace("SOURCENAME_WITHOUT_EXTENSION2",
                                      remove_illegal_characters(SELECT[_hashid].filename_no_extens))
    target_name = target_name.replace("SOURCENAME_WITHOUT_EXTENSION",
                                      SELECT[_hashid].filename_no_extens)

    target_name = target_name.replace("SOURCE_PATH2",
                                      remove_illegal_characters(SELECT[_hashid].path))
    target_name = target_name.replace("SOURCE_PATH",
                                      SELECT[_hashid].path)

    target_name = target_name.replace("SOURCE_EXTENSION2",
                                      remove_illegal_characters(SELECT[_hashid].extension))
    target_name = target_name.replace("SOURCE_EXTENSION",
                                      SELECT[_hashid].extension)

    target_name = target_name.replace("SIZE",
                                      str(SELECT[_hashid].size))

    target_name = target_name.replace("DATE2",
                                      remove_illegal_characters(SELECT[_hashid].date))

    target_name = target_name.replace("DATABASE_INDEX",
                                      remove_illegal_characters(str(_database_index)))

    return target_name

#///////////////////////////////////////////////////////////////////////////////
def eval_sieve_for_a_file(_sieve, _filename, _size, _date):
    """
        eval_sieve_for_a_file()
        ________________________________________________________________________

        Eval a file according to a sieve and answers the following question :
        does the file matches what is described in the sieve ?
        ________________________________________________________________________

        PARAMETERS
                o _sieve        : a dict, see documentation:select
                o _filename     : (str) file's name
                o _size         : (int) file's size, in bytes.
                o _date         : (str)file's date

        RETURNED VALUE
                a boolean, giving the expected answer
    """
    res = True

    if res and "name" in _sieve:
        res = the_file_has_to_be_added__name(_sieve, _filename)
    if res and "size" in _sieve:
        res = the_file_has_to_be_added__size(_sieve, _size)
    if res and "date" in _sieve:
        res = the_file_has_to_be_added__date(_sieve, _date)

    return res

#///////////////////////////////////////////////////////////////////////////////
def fill_select(_debug_datatime=None):
    """
        fill_select()
        ________________________________________________________________________

        Fill SELECT and SELECT_SIZE_IN_BYTES from the files stored in
        SOURCE_PATH. This function is used by action__select() .
        ________________________________________________________________________

        no PARAMETER
                o  _debug_datatime : None (normal value) or a dict of DATETIME_FORMAT
                                     strings if in debug/test mode.

        RETURNED VALUE
                (int) the number of discard files
    """
    global SELECT, SELECT_SIZE_IN_BYTES

    SELECT = {}  # see the SELECT format in the documentation:selection
    SELECT_SIZE_IN_BYTES = 0
    number_of_discarded_files = 0

    file_index = 0  # number of the current file in the source directory.
    for dirpath, _, filenames in os.walk(SOURCE_PATH):
        for filename in filenames:
            file_index += 1
            complete_name = os.path.join(dirpath, filename)
            size = os.stat(complete_name).st_size
            if _debug_datatime is None:
                time = \
                    datetime.fromtimestamp(os.path.getmtime(complete_name)).replace(second=0,
                                                                                    microsecond=0)
            else:
                time = datetime.strptime(_debug_datatime[complete_name], DATETIME_FORMAT)

            filename_no_extens, extension = os.path.splitext(filename)

	    # if we know the total amount of files to be selected (see the --infos option),
	    # we can add the percentage done :
            prefix = ""
            if INFOS_ABOUT_SRC_PATH[1] is not None and INFOS_ABOUT_SRC_PATH[1] != 0:
                prefix = "[{0:.4f}%]".format(file_index/INFOS_ABOUT_SRC_PATH[1]*100.0)

            # the extension stored in SELECT does not begin with a dot.
            if extension.startswith("."):
                extension = extension[1:]

            res = the_file_has_to_be_added(filename, size, time)
            if not res:
                number_of_discarded_files += 1

                msg("    - {0} (sieves described in the config file)" \
                    " discarded \"{1}\"".format(prefix, complete_name),
                    _important_msg=False)
            else:
                # is filename already stored in <TARGET_DB> ?
                _hash = hashfile64(complete_name)

                if _hash not in TARGET_DB and _hash not in SELECT:
                    res = True
                    SELECT[_hash] = SELECTELEMENT(complete_name=complete_name,
                                                  path=dirpath,
                                                  filename_no_extens=filename_no_extens,
                                                  extension=extension,
                                                  size=size,
                                                  date=time.strftime(DATETIME_FORMAT))

                    msg("    + {0} selected {1} ({2} file(s) selected)".format(prefix,
                                                                               complete_name,
                                                                               len(SELECT)),
                        _important_msg=False)

                    SELECT_SIZE_IN_BYTES += os.stat(complete_name).st_size
                else:
                    res = False
                    number_of_discarded_files += 1

                    msg("    - {0} (similar hashid) " \
                        " discarded \"{1}\"".format(prefix, complete_name),
                        _important_msg=False)

    return number_of_discarded_files

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
        stat = os.statvfs(_path)
        return stat.f_bavail * stat.f_frsize

#///////////////////////////////////////////////////////////////////////////////
def goodbye():
    """
        goodbye()
        ________________________________________________________________________

        If not in quiet mode (see --quiet option), display a goodbye message.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    if ARGS.quiet:
        return

    msg("=== exit (stopped at {0}; " \
        "total duration time : {1}) ===".format(datetime.now().strftime(DATETIME_FORMAT),
                                                datetime.now() - TIMESTAMP_BEGIN))

#///////////////////////////////////////////////////////////////////////////////
def hashfile64(_filename):
    """
        hashfile64()
        ________________________________________________________________________

        return the footprint of a file, encoded with the base 64.
        ________________________________________________________________________

        PARAMETER
                o _filename : (str) file's name

        RETURNED VALUE
                the expected string. If you use sha256 as a hasher, the
                resulting string will be 44 bytes long. E.g. :
                        "YLkkC5KqwYvb3F54kU7eEeX1i1Tj8TY1JNvqXy1A91A"
    """
    # hasher used by the hashfile64() function. The SHA256 is a good choice;
    # if you change the hasher, please modify the way the hashids are displayed
    # (see the action__informations() function)
    hasher = hashlib.sha256()

    with open(_filename, "rb") as afile:
        buf = afile.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(65536)
    return b64encode(hasher.digest()).decode()

#///////////////////////////////////////////////////////////////////////////////
def logfile_opening():
    """
        logfile_opening()
        ________________________________________________________________________

        Open the log file and return the result of the called to open().
        ________________________________________________________________________

        no PARAMETER

        RETURNED VALUE
                the _io.BufferedReader object returned by the call to open()
    """
    if PARAMETERS["log file"]["overwrite"] == "True":
        # overwrite :
        log_mode = "w"
    else:
        # let's append :
        log_mode = "a"

    return open(PARAMETERS["log file"]["name"], log_mode)

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
    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
    if not os.path.exists(db_filename):
        msg("    ! Found no database.")
    else:
        db_connection = sqlite3.connect(db_filename)
        db_connection.row_factory = sqlite3.Row
        db_cursor = db_connection.cursor()

        files_to_be_modified = []       # a list of (hashids, name)
        for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
            if fnmatch.fnmatch(db_record["name"], _to) is not None:
                files_to_be_modified.append((db_record["hashid"], db_record["name"]))

        if len(files_to_be_modified) == 0:
            msg("    ! no files match the given regex.")
        else:
            # let's apply the tag(s) to the <files_to_be_modified> :
            for hashid, filename in files_to_be_modified:

                if _mode == "set":
                    msg("    o applying the string tag \"{0}\" to {1}.".format(_tag, filename))
                    sqlorder = 'UPDATE dbfiles SET strtags=? WHERE hashid=?'
                    db_connection.execute(sqlorder, (_tag, hashid))

                elif _mode == "append":
                    msg("    o adding the string tag \"{0}\" to {1}.".format(_tag, filename))
                    sqlorder = 'UPDATE dbfiles SET strtags = strtags || \"{0}{1}\" ' \
                               'WHERE hashid=\"{2}\"'.format(TAG_SEPARATOR, _tag, hashid)
                    db_connection.executescript(sqlorder)

                else:
                    raise ProjectError("_mode argument {0} isn't know".format(_mode))
            db_connection.commit()

        db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def msg(_msg, _for_console=True, _for_logfile=True, _important_msg=True):
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
                o _important_msg: (bool) if False, will be printed only if
                                  LOG_VERBOSITY is set to "high" .

        no RETURNED VALUE
    """
    if _important_msg == False and LOG_VERBOSITY == "low":
        return

    # first to the console : otherwise, if an error occurs by writing to the log
    # file, it would'nt possible to read the message.
    if not ARGS.mute and _for_console:
        print(_msg)

    if USE_LOG_FILE and _for_logfile:
        LOGFILE.write(_msg+"\n")

#///////////////////////////////////////////////////////////////////////////////
def parameters_infos():
    """
        parameters_infos()
        ________________________________________________________________________

        Display some informations about the content of the configuration file
        (confer the PARAMETERS variable). This function must be called after
        the opening of the configuration file.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    if ARGS.quiet:
        return

    msg("  = source directory : \"{0}\" =".format(SOURCE_PATH))
    msg("  = target directory : \"{0}\" =".format(TARGET_PATH))

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
    parser = argparse.ArgumentParser(description="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
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

    parser.add_argument('-c', '--configfile',
                        type=str,
                        default=DEFAULT_CONFIGFILE_NAME,
                        help="config file, e.g. config.ini")

    parser.add_argument('--cleandbrm',
                        action="store_true",
                        help="Remove from the database the missing files in the target path.")

    parser.add_argument('-ddcfg', '--downloaddefaultcfg',
                        action="store_true",
                        help="Download the default config file and overwrite the file having " \
                             "the same name. This is done before the script reads the parameters " \
                             "in the config file")

    parser.add_argument('--hashid',
                        type=str,
                        help="return the hash id of the given file")

    parser.add_argument('--infos',
                        action="store_true",
                        help="display informations about the source directory " \
                             "given in the configuration file. Help the --select/--add " \
							 "options to display more informations about the process : in " \
							 "this case, the --infos will be executed before --select/--add")

    parser.add_argument('-s', '--select',
                        action="store_true",
                        help="select files according to what is described " \
                             "in the configuration file " \
                             "without adding them to the target directory. " \
                             "This option can't be used with the --add one." \
							 "If you want more informations about the process, please " \
							 "use this option in combination with --infos .")

    parser.add_argument('-ti', '--targetinfos',
                        action="store_true",
                        help="display informations about the target directory in --quiet mode")

    parser.add_argument('-tk', '--targetkill',
                        type=str,
                        help="kill one file from the target directory." \
                             "DO NOT GIVE A PATH, just the file's name, " \
                             "without the path to the target directory ")

    parser.add_argument('-m', '--mute',
                        action="store_true",
                        help="no output to the console; no question asked on the console")

    parser.add_argument('-q', '--quiet',
                        action="store_true",
                        help="no welcome/goodbye/informations about the parameters/ messages " \
                             "on console")

    parser.add_argument('--rmtags',
                        action="store_true",
                        help="remove all the tags of some file(s) in combination " \
                             "with the --to option. ")

    parser.add_argument('--setstrtags',
                        type=str,
                        help="give the string tag to some file(s) in combination " \
                             "with the --to option. " \
                             "Overwrite the ancient string tag.")

    parser.add_argument('--to',
                        type=str,
                        help="give the name of the file(s) concerned by --setstrtags. " \
                        "wildcards accepted; e.g. to select all .py files, use '*.py' . " \
                        "Please DON'T ADD the path to the target directory, only the filenames")

    parser.add_argument('--version',
                        action='version',
                        version="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
                        help="show the version and exit")

    return parser.parse_args()

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
    global USE_LOG_FILE, LOG_VERBOSITY
    global TARGET_PATH, TARGETNAME_MAXLENGTH
    global SOURCE_PATH, SOURCENAME_MAXLENGTH
    global HASHID_MAXLENGTH, STRTAGS_MAXLENGTH

    if not os.path.exists(_configfile_name):
        msg("    ! The config file \"{0}\" doesn't exist.".format(_configfile_name))
        return None

    parser = configparser.ConfigParser()

    try:
        parser.read(_configfile_name)
        USE_LOG_FILE = parser["log file"]["use log file"] == "True"
        LOG_VERBOSITY = parser["log file"]["verbosity"]
        TARGET_PATH = parser["target"]["path"]
        TARGETNAME_MAXLENGTH = int(parser["display"]["target filename.max length on console"])
        SOURCE_PATH = parser["source"]["path"]
        SOURCENAME_MAXLENGTH = int(parser["display"]["source filename.max length on console"])
        HASHID_MAXLENGTH = int(parser["display"]["hashid.max length on console"])
        STRTAGS_MAXLENGTH = int(parser["display"]["tag.max length on console"])
    except BaseException as exception:
        msg("    ! An error occured while reading " \
            "the config file \"{0}\".".format(_configfile_name))
        msg("    ! Python message : \"{0}\"".format(exception))
        return None

    return parser

#///////////////////////////////////////////////////////////////////////////////
def read_sieves():
    """
        read_sieves()
        ________________________________________________________________________

        Initialize SIEVES from the configuration file.
        ________________________________________________________________________

        no PARAMETER, no RETURNED VALUE
    """
    SIEVES.clear()

    stop = False
    sieve_index = 1

    while not stop:
        if not PARAMETERS.has_section("source.sieve"+str(sieve_index)):
            stop = True
        else:
            SIEVES[sieve_index] = dict()

            if PARAMETERS.has_option("source.sieve"+str(sieve_index), "name"):
                SIEVES[sieve_index]["name"] = \
                                    re.compile(PARAMETERS["source.sieve"+str(sieve_index)]["name"])
            if PARAMETERS.has_option("source.sieve"+str(sieve_index), "size"):
                SIEVES[sieve_index]["size"] = PARAMETERS["source.sieve"+str(sieve_index)]["size"]
            if PARAMETERS.has_option("source.sieve"+str(sieve_index), "date"):
                SIEVES[sieve_index]["date"] = PARAMETERS["source.sieve"+str(sieve_index)]["date"]

        sieve_index += 1

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
    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)

    if not os.path.exists(db_filename):
        msg("  = creating the database in the target path...")

        # let's create a new database in the target directory :
        db_connection = sqlite3.connect(db_filename)
        db_cursor = db_connection.cursor()

        db_cursor.execute('CREATE TABLE dbfiles ' \
                          '(hashid varchar(44) PRIMARY KEY UNIQUE, name TEXT UNIQUE, ' \
                          'sourcename TEXT, sourcedate INTEGER, strtags TEXT)')

        db_connection.commit()

        db_connection.close()

        msg("  = ... database created.")

    db_connection = sqlite3.connect(db_filename)
    db_connection.row_factory = sqlite3.Row
    db_cursor = db_connection.cursor()

    for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
        TARGET_DB.append(db_record["hashid"])

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
    for char in ("*", "/", "\\", ".", "[", "]", ":", ";", "|", "=", ",", "?", "<", ">"):
        res = res.replace(char, "_")
    return res

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

    if not os.path.exists(SOURCE_PATH):
        msg("Can't read source path {0}.".format(SOURCE_PATH))
        return -1
    if not os.path.isdir(SOURCE_PATH):
        msg("(source path) {0} isn't a directory.".format(SOURCE_PATH))
        return -1

    msg("  = searching informations about the \"{0}\" (source) directory ... =".format(SOURCE_PATH))

    total_size = 0
    files_number = 0
    extensions = dict()  # (str)extension : [number of files, total size]
    for dirpath, _, fnames in os.walk(SOURCE_PATH):
        for filename in fnames:
            complete_name = os.path.join(dirpath, filename)
            size = os.stat(complete_name).st_size
            extension = os.path.splitext(filename)[1]

            if extension in extensions:
                extensions[extension][0] += 1
                extensions[extension][1] += size
            else:
                extensions[extension] = [1, size]

            total_size += size
            files_number += 1

    msg("    o files number : {0} file(s)".format(files_number))
    msg("    o total size : {0}".format(size_as_str(total_size)))
    msg("    o list of all extensions (found {0} extension(s)): ".format(len(extensions)))
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

    if not os.path.exists(TARGET_PATH):
        msg("Can't read target path {0}.".format(TARGET_PATH))
        return -1
    if not os.path.isdir(TARGET_PATH):
        msg("(target path) {0} isn't a directory.".format(TARGET_PATH))
        return -1

    msg("  = informations about the \"{0}\" (target) directory =".format(TARGET_PATH))

    if not os.path.exists(os.path.join(TARGET_PATH, DATABASE_NAME)):
        msg("    o no database in the target directory o")
    else:
        db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
        db_connection = sqlite3.connect(db_filename)
        db_connection.row_factory = sqlite3.Row
        db_cursor = db_connection.cursor()

        # there's no easy way to know the size of a table in a database,
        # so we can't display the "empty database" warning before the following
        # code which reads the table.
        rows_data = []
        row_index = 0
        for db_record in db_cursor.execute('SELECT * FROM dbfiles'):
            sourcedate = datetime.fromtimestamp(db_record["sourcedate"]).strftime(DATETIME_FORMAT)

            rows_data.append((db_record["hashid"],
                              db_record["name"],
                              db_record["strtags"],
                              db_record["sourcename"],
                              sourcedate))

            row_index += 1

        if row_index == 0:
            msg("    ! (empty database)")
        else:
            # beware : characters like "║" are forbidden (think to the cp1252 encoding
            # required by Windows terminal)
            draw_table(_rows=(("hashid/base64", HASHID_MAXLENGTH, "|"),
                              ("name", TARGETNAME_MAXLENGTH, "|"),
                              ("tags", STRTAGS_MAXLENGTH, "|"),
                              ("(source) name", SOURCENAME_MAXLENGTH, "|"),
                              ("(source) date", DATETIME_FORMAT_LENGTH, "|")),
                       _data=rows_data)

        db_connection.close()

    return 0

#///////////////////////////////////////////////////////////////////////////////
def shortstr(_str, _max_length):
    """
        shortstr()
        ________________________________________________________________________

        The function the shortened version of a string.
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
def show_hashid_of_a_file(filename):
    """
        show_hashid_of_a_file()
        ________________________________________________________________________

        The function gives the hashid of a file.
        ________________________________________________________________________

        PARAMETER
                o filename : (str) source filename

        no RETURNED VALUE
    """
    msg("  = hashid of \"{0}\" : \"{1}\"".format(filename,
                                                 hashfile64(filename)))

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
        return "0 byte"
    elif _size < 100000:
        return "{0} bytes".format(_size)
    elif _size < 1000000:
        return "~{0:.2f} Mo ({1} bytes)".format(_size/1000000.0,
                                                _size)
    else:
        return "~{0:.2f} Go ({1} bytes)".format(_size/1000000000.0,
                                                _size)

#///////////////////////////////////////////////////////////////////////////////
def the_file_has_to_be_added(_filename, _size, _date):
    """
        the_file_has_to_be_added()
        ________________________________________________________________________

        Return True if a file (_filename, _size) can be choosed and added to
        the target directory, according to the sieves (stored in SIEVES).
        ________________________________________________________________________

        PARAMETERS
                o _filename     : (str) file's name
                o _size         : (int) file's size, in bytes.
                o _date         : (str) file's date

        RETURNED VALUE
                a boolean, giving the expected answer
    """
    evalstr = PARAMETERS["source"]["eval"]

    for sieve_index in SIEVES:
        sieve = SIEVES[sieve_index]

        evalstr = evalstr.replace("sieve"+str(sieve_index),
                                  str(eval_sieve_for_a_file(sieve, _filename, _size, _date)))

    try:
        # eval() IS a dangerous function : see the note about AUTHORIZED_EVALCHARS.
        for char in evalstr:
            if char not in AUTHORIZED_EVALCHARS:
                raise ProjectError("Error in configuration file : " \
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
        raise ProjectError("The eval formula in the config file " \
                           "contains an error. Python message : "+str(exception))

#///////////////////////////////////////////////////////////////////////////////
def the_file_has_to_be_added__date(_sieve, _date):
    """
        the_file_has_to_be_added__date()
        ________________________________________________________________________

        Function used by the_file_has_to_be_added() : check if the date of a
        file matches the sieve given as a parameter.
        ________________________________________________________________________

        PARAMETERS
                o _sieve        : a dict object; see documentation:selection
                o _date         : (str) file's datestamp (object datetime.datetime)

        RETURNED VALUE
                the expected boolean
    """
    # beware ! the order matters (<= before <, >= before >)
    if _sieve["date"].startswith("="):
        return _date == datetime.strptime(_sieve["date"][1:], DATETIME_FORMAT)
    elif _sieve["date"].startswith(">="):
        return _date >= datetime.strptime(_sieve["date"][2:], DATETIME_FORMAT)
    elif _sieve["date"].startswith(">"):
        return _date > datetime.strptime(_sieve["date"][1:], DATETIME_FORMAT)
    elif _sieve["date"].startswith("<="):
        return _date < datetime.strptime(_sieve["date"][2:], DATETIME_FORMAT)
    elif _sieve["date"].startswith("<"):
        return _date < datetime.strptime(_sieve["date"][1:], DATETIME_FORMAT)
    else:
        raise ProjectError("Can't analyse a 'date' field : "+_sieve["date"])

#///////////////////////////////////////////////////////////////////////////////
def the_file_has_to_be_added__name(_sieve, _filename):
    """
        the_file_has_to_be_added__name()
        ________________________________________________________________________

        Function used by the_file_has_to_be_added() : check if the name of a
        file matches the sieve given as a parameter.
        ________________________________________________________________________

        PARAMETERS
                o _sieve        : a dict object; see documentation:selection
                o _filename     : (str) file's name

        RETURNED VALUE
                the expected boolean
    """
    return re.match(_sieve["name"], _filename) is not None

#///////////////////////////////////////////////////////////////////////////////
def the_file_has_to_be_added__size(_sieve, _size):
    """
        the_file_has_to_be_added__size()
        ________________________________________________________________________

        Function used by the_file_has_to_be_added() : check if the size of a
        file matches the sieve given as a parameter.
        ________________________________________________________________________

        PARAMETERS
                o _sieve        : a dict object; see documentation:selection
                o _size         : (str) file's size

        RETURNED VALUE
                the expected boolean
    """
    res = False

    sieve_size = _sieve["size"] # a string like ">999" : see documentation:selection

    # beware !  the order matters (<= before <, >= before >)
    if sieve_size.startswith(">="):
        if _size >= int(sieve_size[2:]):
            res = True
    elif sieve_size.startswith(">"):
        if _size > int(sieve_size[1:]):
            res = True
    elif sieve_size.startswith("<="):
        if _size <= int(sieve_size[2:]):
            res = True
    elif sieve_size.startswith("<"):
        if _size < int(sieve_size[1:]):
            res = True
    elif sieve_size.startswith("="):
        if _size == int(sieve_size[1:]):
            res = True
    else:
        raise ProjectError("Can't analyse {0} in the sieve.".format(sieve_size))
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
    """
    if ARGS.quiet:
        return

    msg("=== {0} v.{1} (launched at {2}) ===".format(PROGRAM_NAME,
                                                     PROGRAM_VERSION,
                                                     TIMESTAMP_BEGIN.strftime("%Y-%m-%d %H:%M:%S")))
    msg("  = using \"{0}\" as config file".format(ARGS.configfile))

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
        "(launched at {2}) ===".format(PROGRAM_NAME,
                                       PROGRAM_VERSION,
                                       TIMESTAMP_BEGIN.strftime("%Y-%m-%d %H:%M:%S")),
        _for_logfile=True,
        _for_console=False)

    msg("  = using \"{0}\" as config file".format(ARGS.configfile),
        _for_logfile=True,
        _for_console=False)

#///////////////////////////////////////////////////////////////////////////////
#/////////////////////////////// STARTING POINT ////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    try:
        ARGS = read_command_line_arguments()
        check_args()

        if ARGS.targetinfos:
            ARGS.quiet = True

        welcome()

        if ARGS.downloaddefaultcfg:
            action__downloadefaultcfg()

        PARAMETERS = read_parameters_from_cfgfile(ARGS.configfile)
        if PARAMETERS is None:
            sys.exit(-1)

        if USE_LOG_FILE:
            LOGFILE = logfile_opening()
            welcome_in_logfile()

        parameters_infos()

        if not os.path.exists(TARGET_PATH):
            msg("  ! Since the target path \"{0}\" " \
                      "doesn't exist, let's create it.".format(TARGET_PATH))
            os.mkdir(TARGET_PATH)

        if ARGS.infos:
            action__infos()
        if ARGS.targetinfos:
            show_infos_about_target_path()

        if ARGS.cleandbrm:
            action__cleandbrm()

        if ARGS.hashid:
            show_hashid_of_a_file(ARGS.hashid)

        if ARGS.setstrtags:
            action__setstrtags(ARGS.setstrtags, ARGS.to)

        if ARGS.addtag:
            action__addtag(ARGS.addtag, ARGS.to)

        if ARGS.rmtags:
            action__rmtags(ARGS.to)

        if ARGS.targetkill:
            action__target_kill(ARGS.targetkill)

        if ARGS.select:
            read_target_db()
            read_sieves()
            action__select()

            if not ARGS.mute:
                ANSWER = \
                    input("\nDo you want to add the selected " \
                          "files to the target dictionary (\"{0}\") ? (y/N) ".format(TARGET_PATH))

                if ANSWER in ("y", "yes"):
                    action__add()
                    action__infos()

        if ARGS.add:
            read_target_db()
            read_sieves()
            action__select()
            action__add()
            action__infos()

        goodbye()

        if USE_LOG_FILE:
            LOGFILE.close()

    except ProjectError as exception:
        print("({0}) ! a critical error occured.\nError message : {1}".format(PROGRAM_NAME,
                                                                              exception))
        sys.exit(-2)
    else:
        sys.exit(-3)

    sys.exit(0)
