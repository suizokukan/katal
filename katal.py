#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#    katal Copyright (C) 2012 Suizokukan
#    Contact: suizokukan _A.T._ orange dot fr
#
#    This file is part of katal.
#    katal is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    katal is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with katal.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
        katal project

        from the Ancient Greek κατάλογος "enrolment, register, catalogue"
"""
import argparse
from base64 import b64encode
from collections import namedtuple
import configparser
import hashlib
from datetime import datetime
import os
import re
import shutil
import sqlite3
import sys

PROGRAM_NAME = "katal"
PROGRAM_VERSION = "0.0.1"

DEFAULT_CONFIGFILE_NAME = "katal.ini"
DATABASE_NAME = "katal.db"

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
    res = _src.replace("*", "_")
    res = res.replace("/", "_")
    res = res.replace("\\", "_")
    res = res.replace(".", "_")
    res = res.replace("\"", "_")
    res = res.replace("[", "_")
    res = res.replace("]", "_")
    res = res.replace(":", "_")
    res = res.replace(";", "_")
    res = res.replace("|", "_")
    res = res.replace("=", "_")
    res = res.replace(",", "_")
    res = res.replace("?", "_")
    res = res.replace("<", "_")
    res = res.replace(">", "_")
    return res

#/////////////////////////////////////////////////////////////////////////////////////////
def create_target_name(_hashid,
                       _sourcename_without_extens,
                       _source_path,
                       _source_extension,
                       _str_size,
                       _str_date,
                       _database_index):
    """
        create_target_name()
        ________________________________________________________________________

        Create the name of a file (a target file) from various informations
        read from an source(source) file. The function reads the string stored 
        in PARAMETERS["target"]["name of the target files"] and replaces some 
        keywords in the string by the parameters given to this function.

           keywords                             example
           ---------------------------------------------------------------------

           HASHID                               |
           SOURCENAME_WITHOUT_EXTENSION       | cat
           SOURCENAME_WITHOUT_EXTENSION2      | cat_
           SOURCE_PATH                        | /home/someone/Pictures
           SOURCE_PATH2                       | _home_someone_Pictures
           SOURCE_EXTENSION                   | jpg
           SOURCE_EXTENSION2                  | jpg
           SIZE                                 | 1234
           DATE2                                | ****todo$$$
           DATABASE_INDEX                       | 123

           n.b. : keywords ending by "2" are builded against a set of illegal 
                  characters replaced by "_".
        ________________________________________________________________________

        PARAMETERS
                o _hashid                       : (str)
                o _sourcename_without_extens  : (str) e.g. "cat"
                o _source_path                : (str) e.g. "/home/" or "c:\"
                o _source_extension           : (str) e.g. "jpg" (no dot !)
                o 
    """

    target_name  = PARAMETERS["target"]["name of the target files"]

    target_name = target_name.replace("HASHID",
                                      _hashid)

    target_name = target_name.replace("SOURCENAME_WITHOUT_EXTENSION2",
                                      remove_illegal_characters(_sourcename_without_extens))
    target_name = target_name.replace("SOURCENAME_WITHOUT_EXTENSION",
                                      _sourcename_without_extens)

    target_name = target_name.replace("SOURCE_PATH2",
                                      remove_illegal_characters(_source_path))
    target_name = target_name.replace("SOURCE_PATH",
                                      _source_path)

    target_name = target_name.replace("SOURCE_EXTENSION2",
                                      remove_illegal_characters(_source_extension))
    target_name = target_name.replace("SOURCE_EXTENSION",
                                      _source_extension)

    target_name = target_name.replace("SIZE",
                                      str(_str_size))
    
    target_name = target_name.replace("DATE2",
                                      remove_illegal_characters(str(_str_date)))
    
    target_name = target_name.replace("DATABASE_INDEX",
                                      remove_illegal_characters(str(_database_index)))
    
    return target_name

    

#///////////////////////////////////////////////////////////////////////////////
def size_as_str(size):
    """
        Return size a human-readable string.
    """
    if size < 100000:
        return "{0} bytes".format(size)
    elif size < 1000000:
        return "~{0:.2f} Mo ({1} bytes)".format(size/1000000.0,
                                                size)
    else:
        return "~{0:.2f} Go ({1} bytes)".format(size/1000000000.0,
                                                size)

#///////////////////////////////////////////////////////////////////////////////
DiskUsageNTuple = namedtuple('usage', 'total used free')
def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.

        confer http://stackoverflow.com/questions/787776

todo:$$$
    """
    stat = os.statvfs(path)
    free = stat.f_bavail * stat.f_frsize
    total = stat.f_blocks * stat.f_frsize
    used = (stat.f_blocks - stat.f_bfree) * stat.f_frsize
    return DiskUsageNTuple(total, used, free)

#///////////////////////////////////////////////////////////////////////////////
def first_message0():
    """
        first_message0()

        before PARAMETERS

        $$todo$$
    """
    msg("=== {0} v.{1} (launched at {2}) ===".format(PROGRAM_NAME,
                                                     PROGRAM_VERSION,
                                                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    msg("  = using \"{0}\" as config file".format(ARGS.configfile))

#///////////////////////////////////////////////////////////////////////////////
def first_message1():
    """
        first_message1()

        after PARAMETERS

        $$todo$$
    """
    msg("  = source directory : \"{0}\" =".format(SOURCE_PATH))
    msg("  = target directory : \"{0}\" =".format(TARGET_PATH))


#///////////////////////////////////////////////////////////////////////////////
def infos():
    """
        display some informations about source and dest directories.
    """
    msg("  = informations =")

    #...........................................................................
    # source path
    #...........................................................................
    if not os.path.exists(SOURCE_PATH):
        # todo : error
        msg("Can't read source path {0}.".format(SOURCE_PATH))
        return
    if not os.path.isdir(SOURCE_PATH):
        # error (todo)
        msg("(source path) {0} isn't a directory.".format(SOURCE_PATH))
        return

    msg("  = informations about the \"{0}\" (source) directory =".format(SOURCE_PATH))

    total_size = 0
    files_number = 0
    extensions = set()
    for dirpath, _, fnames in os.walk(SOURCE_PATH):
        for filename in fnames:
            complete_name = os.path.join(dirpath, filename)

            extensions.add(os.path.splitext(filename)[1])

            total_size += os.stat(complete_name).st_size
            files_number += 1

    msg("    o files number : {0}".format(files_number))
    msg("    o total size : {0}".format(size_as_str(total_size)))
    msg("    o list of all extensions : {0}".format(tuple(extensions)))

   #...........................................................................
    # target path
    #...........................................................................
    if not os.path.exists(TARGET_PATH):
        msg("Can't read target path {0}.".format(TARGET_PATH))
        return
    if not os.path.isdir(TARGET_PATH):
        # error (todo)
        msg("(target path) {0} isn't a directory.".format(TARGET_PATH))
        return

    msg("  = informations about the \"{0}\" (target) directory =".format(TARGET_PATH))

    if not os.path.exists(os.path.join(TARGET_PATH, DATABASE_NAME)):
        msg("    o no database in the target directory o")
    else:
        db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
        db_connection = sqlite3.connect(db_filename)
        db_cursor = db_connection.cursor()

        msg("    : hashid                                       : (target) file name : (source) source name")
        row_index = 0
        for hashid, filename, sourcename in db_cursor.execute('SELECT * FROM files'):

            if len(filename) > TARGETFILENAME_MAXLENGTH:
                filename = "[...]"+filename[-(TARGETFILENAME_MAXLENGTH-5):]
            if len(sourcename) > SOURCENAME_MAXLENGTH:
                sourcename = "[...]"+sourcename[-(SOURCENAME_MAXLENGTH-5):]

            msg("    o {0} : {1:18} : {2}".format(hashid,
                                                  filename,
                                                  sourcename))
            row_index += 1
        if row_index == 0:
            msg("    ! (empty database)")

        db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def get_args():
    """
        Read the command line arguments.

        Return the argparse object.
    """
    parser = argparse.ArgumentParser(description="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
                                     epilog="by suizokukan AT orange DOT fr",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--add',
                        action="store_true",
                        help="select files according to what is described " \
                             "in the configuration file " \
                             "then add them to the target directory" \
                             "This option can't be used the --select one.")

    parser.add_argument('--configfile',
                        type=str,
                        default=DEFAULT_CONFIGFILE_NAME,
                        help="config file, e.g. config.ini")

    parser.add_argument('--infos',
                        action="store_true",
                        help="display informations about the source directory " \
                             "given in the configuration file")

    parser.add_argument('--select',
                        action="store_true",
                        help="select files according to what is described " \
                             "in the configuration file " \
                             "without adding them to the target directory. " \
                             "This option can't be used the --add one.")

    parser.add_argument('--quiet',
                        action="store_true",
                        help="no output to the console; no question asked on the console")

    parser.add_argument('--version',
                        action='version',
                        version="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
                        help="show the version and exit")

    return parser.parse_args()

#///////////////////////////////////////////////////////////////////////////////
def get_parameters(configfile_name):
    """
        read the configfile and return the parser or None if an error occured.
    """
    if not os.path.exists(configfile_name):
        msg("    ! The config file \"{0}\" doesn't exist.".format(configfile_name))
        return None

    parser = configparser.ConfigParser()
    try:
        parser.read(configfile_name)
    except BaseException as exception:
        msg("    ! An error occured while reading the config file \"{0}\".".format(configfile_name))
        msg("    ! Python message : \"{0}\"".format(exception))
        return None

    return parser

#///////////////////////////////////////////////////////////////////////////////
def hashfile(afile, hasher, blocksize=65536):
    """
        return the footprint of a file.

        e.g. :
                _hash = hashfile(open(complete_name, 'rb'), hashlib.sha256())
    """
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    #return hasher.digest()
    #return hasher.hexdigest()
    return b64encode(hasher.digest()).decode()

#///////////////////////////////////////////////////////////////////////////////
def logfile_closing():
    """
        logfile_closing()

        close the log file
    """
    LOGFILE.close()

#///////////////////////////////////////////////////////////////////////////////
def logfile_opening():
    """
        logfile_opening()

        open the log file and return the result of the called to open().
    """
    if PARAMETERS["log file"]["overwrite"] == "True":
        # overwrite :
        log_mode = "w"
    else:
        # let's append :
        log_mode = "a"

    logfile = open(PARAMETERS["log file"]["name"], log_mode)

    return logfile

#///////////////////////////////////////////////////////////////////////////////
def msg(_msg, for_console=True, for_logfile=True):
    """
        msg()

        Write <_msg> into the $$$
    """
    if USE_LOG_FILE and for_console:
        LOGFILE.write(_msg+"\n")

    if not ARGS.quiet and for_logfile:
        print(_msg)

#///////////////////////////////////////////////////////////////////////////////
def read_sieves():
    """
        initialize SIEVES
    """
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
                SIEVES[sieve_index]["size"] = \
                                    re.compile(PARAMETERS["source.sieve"+str(sieve_index)]["size"])
        sieve_index += 1

#///////////////////////////////////////////////////////////////////////////////
def select():
    """
        $$$todo
        fill SELECT and SELECT_SIZE_IN_BYTES
    """
    msg("  = selecting files according to the instructions " \
                "in the config file. Please wait... =")
    msg("  o sieves :")
    for sieve_index in SIEVES:
        msg("    o sieve #{0} : {1}".format(sieve_index,
                                            SIEVES[sieve_index]))
    msg("  o file list :")

    # big loop :
    SELECT_SIZE_IN_BYTES = 0
    number_of_discarded_files = 0

    for dirpath, _, filenames in os.walk(SOURCE_PATH):
        for filename in filenames:
            complete_name = os.path.join(dirpath, filename)
            size = os.stat(complete_name).st_size
            time = datetime.fromtimestamp(os.path.getmtime(complete_name))
            filename_without_extension, extension = os.path.splitext(filename)

            # the extension stored in SELECT does not begin with a dot.
            if extension.startswith("."):
                extension = extension[1:]

            res = the_file_can_be_added(filename, size)
            if not res:
                if VERBOSITY == "high":
                    msg("    - (sieves described in the config file)" \
                              " discarded \"{0}\"".format(complete_name))
                    number_of_discarded_files += 1
            else:
                # is filename already stored in <TARGET_DB> ?
                _hash = hashfile(open(complete_name, 'rb'), hashlib.sha256())

                if _hash not in TARGET_DB:
                    res = True
                    SELECT[_hash] = (complete_name,
                                     dirpath,
                                     filename_without_extension,
                                     extension,
                                     size,
                                     time.strftime("%Y_%m_%d__%H_%M_%S"))

                    if VERBOSITY == "high":
                        msg("    + selected {0} ({1} file(s) selected)".format(complete_name,
                                                                               len(SELECT)))

                    SELECT_SIZE_IN_BYTES += os.stat(complete_name).st_size
                else:
                    res = False

                    if VERBOSITY == "high":
                        msg("    - (similar hashid) " \
                                  " discarded \"{0}\"".format(complete_name))
                        number_of_discarded_files += 1

    msg("    o size of the selected files : {0}".format(size_as_str(SELECT_SIZE_IN_BYTES)))

    if len(SELECT) == 0:
        msg("    ! no file selected !")
    else:
        ratio = number_of_discarded_files/len(SELECT)*100.0
        msg("    o number of selected files : {0} " \
                  "(after discarding {1} file(s), " \
                  "{2:.2f}% of all the files)".format(len(SELECT),
                                                      number_of_discarded_files,
                                                      ratio))

    # let's check that the target path has sufficient free space :
    available_space = disk_usage(TARGET_PATH)
    msg("    o required space : {0}; " \
        "available space on disk : {1}".format(SELECT_SIZE_IN_BYTES,
                                               available_space.free))

    # let's give some examples of the target names :
    example_index = 0
    for index, hashid in enumerate(SELECT):

        (complete_source_filename,
         source_path,
         filename_without_extension,
         extension,
         size,
         date) = SELECT[hashid]

        short_target_name = \
                  create_target_name(_hashid=hashid,
                                     _sourcename_without_extens=filename_without_extension,
                                     _source_path=source_path,
                                     _source_extension=extension,
                                     _str_size=size,
                                     _str_date=date,
                                     _database_index=str(len(TARGET_DB) + index))

        target_name = os.path.join(TARGET_PATH, short_target_name)

        msg("    o e.g. ... \"{0}\" would be copied as \"{1}\" .".format(complete_source_filename,
                                                                         target_name))

        example_index += 1

        if example_index>5:
            break

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_added(filename, size):
    """
                return (bool)res
    """
    # to be True, one of the sieves must match the file given as a parameter :
    res = False

    for sieve_index in SIEVES:
        sieve = SIEVES[sieve_index]

        sieve_res = True

        if sieve_res and "name" in sieve:
            sieve_res = the_file_can_be_added__name(sieve, filename)

        if sieve_res and "size" in sieve:
            sieve_res = the_file_can_be_added__size(sieve_index, size)

        # at least, one sieve is ok with this file :
        if sieve_res:
            res = True
            break

    return res

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_added__name(sieve, filename):
    """
        the_file_can_be_added__name()

        apply a sieve based on the name to <filename>.
    """
    return re.match(sieve["name"], filename)

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_added__size(sieve_index, size):
    """
        the_file_can_be_added__size()

        apply a sieve based on the size on <size>.
    """
    res = False

    sieve_size = PARAMETERS["source.sieve"+str(sieve_index)]["size"]

    if sieve_size.startswith(">"):
        if size > int(sieve_size[1:]):
            res = True
    if sieve_size.startswith(">="):
        if size >= int(sieve_size[2:]):
            res = True
    if sieve_size.startswith("<"):
        if size < int(sieve_size[1:]):
            res = True
    if sieve_size.startswith("<="):
        if size <= int(sieve_size[2:]):
            res = True
    if sieve_size.startswith("="):
        if size == int(sieve_size[1:]):
            res = True

    return res

#///////////////////////////////////////////////////////////////////////////////
def read_target_db():
    """
        read the database stored in the target directory and initialize
        TARGET_DB.
    """
    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)

    if not os.path.exists(db_filename):
        msg("  = creating the database in the target path...")

        # let's create a new database in the target directory :
        db_connection = sqlite3.connect(db_filename)
        db_cursor = db_connection.cursor()

        db_cursor.execute('''CREATE TABLE files
        (hashid text, name text, sourcename text)''')

        db_connection.commit()

        db_connection.close()

        msg("  = ... database created.")

    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()

    for hashid, _, _ in db_cursor.execute('SELECT * FROM files'):
        TARGET_DB.append(hashid)

    db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
def check_args():
    """
        check_args()

        Check $todo
    """

    # --select and --add can't be used simultaneously.
    if ARGS.add == True and ARGS.select == True:
        # $$$ todo $$$
        raise

#///////////////////////////////////////////////////////////////////////////////
def add():
    """
        Add the source files to the destination path.

        todo : d'abord appeler select()
    """
    msg("    = copying data =")

    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()

    # (100000 bytes for the database) :
    available_space = disk_usage(TARGET_PATH).free
    if available_space < SELECT_SIZE_IN_BYTES + 100000:
        msg("    ! Not enough space on disk. Stopping the program.")
        return # todo : return value for add()

    files_to_be_added = []
    len_select = len(SELECT)
    for index, hashid in enumerate(SELECT):

        (complete_source_filename,
         source_path,
         filename_without_extension,
         extension,
         size,
         date) = SELECT[hashid]

        short_target_name = \
                  create_target_name(_hashid=hashid,
                                     _sourcename_without_extens=filename_without_extension,
                                     _source_path=source_path,
                                     _source_extension=extension,
                                     _str_size=size,
                                     _str_date=date,
                                     _database_index=str(len(TARGET_DB) + index))

        target_name = os.path.join(TARGET_PATH, short_target_name)

        msg("    ... ({0}/{1}) copying \"{2}\" to \"{3}\" .".format(index+1,
                                                                    len_select,
                                                                    complete_source_filename,
                                                                    target_name))
        shutil.copyfile(complete_source_filename,
                        target_name)

        files_to_be_added.append((hashid, short_target_name, complete_source_filename))

    db_cursor.executemany('INSERT INTO files VALUES (?,?,?)', files_to_be_added)
    db_connection.commit()

    db_connection.close()

    return # todo : return value for add()

#///////////////////////////////////////////////////////////////////////////////
#/////////////////////////////// STARTING POINT ////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
ARGS = get_args()
check_args()

# a function like msg() may need this variable before its initialization (see further)
USE_LOG_FILE = False

first_message0()

PARAMETERS = get_parameters(ARGS.configfile)
if PARAMETERS is None:
    sys.exit()  # todo: valeur renvoyée par le programme ?

SIEVES = {}
TIMESTAMP_BEGIN = datetime.now()
USE_LOG_FILE = PARAMETERS["log file"]["use log file"] == "True"
VERBOSITY = PARAMETERS["log file"]["verbosity"]
TARGET_DB = []  # a list of hashid
TARGET_PATH = PARAMETERS["target"]["path"]
TARGETFILENAME_MAXLENGTH = int(PARAMETERS["infos"]["target filename.max length on console"])
SOURCENAME_MAXLENGTH = int(PARAMETERS["infos"]["source filename.max length on console"])

SOURCE_PATH = PARAMETERS["source"]["sourcepath"]

LOGFILE = None
if USE_LOG_FILE:
    LOGFILE = logfile_opening()

first_message1()

if not os.path.exists(TARGET_PATH):
    msg("  ! Since the destination path \"{0}\" " \
              "doesn't exist, let's create it.".format(TARGET_PATH))
    os.mkdir(TARGET_PATH)

SELECT = {} # hashid : complete filename, source_path, filename without extension, extension, size, date
SELECT_SIZE_IN_BYTES = 0

if ARGS.infos:
    infos()
if ARGS.select:
    read_target_db()
    read_sieves()
    select()

    if not ARGS.quiet:
        ANSWER = input("\nDo you want to add the selected files to the target dictionary (\"{0}\") ? (y/N) ".format(TARGET_PATH))

        if ANSWER in ("y", "yes"):
            add()
            infos()

if ARGS.add:
    read_target_db()
    read_sieves()
    select()
    add()
    infos()

msg("=== exit (stopped at {0}; " \
          "total duration time : {1}) ===".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                  datetime.now() - TIMESTAMP_BEGIN))

if USE_LOG_FILE:
    logfile_closing()
