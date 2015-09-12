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
import base64
import configparser
import hashlib
from datetime import datetime
import os
import re
import shutil
import sqlite3

PROGRAM_NAME = "katal"
PROGRAM_VERSION = "0.0.1"

SIEVES = {}
DEFAULT_CONFIGFILE_NAME = "katal.ini"
DATABASE_NAME = "katal.db"
TIMESTAMP_BEGIN = datetime.now()

#///////////////////////////////////////////////////////////////////////////////
def console_first_message():
    """
        console_first_message()

        $$todo$$
    """
    console_w("=== {0} v.{1} (launched at {2}) ===".format(PROGRAM_NAME,
                                                 PROGRAM_VERSION,
                                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    console_w("  = source directory : \"{0}\" =".format(SOURCE_PATH))

#///////////////////////////////////////////////////////////////////////////////
def console_w(msg):
    """
            console_w()

            Send a message to the console if not in quiet mode.
    """
    if not ARGS.quiet:
        print(msg)

#///////////////////////////////////////////////////////////////////////////////
def infos():
    """
        display (on the console) some informations about source and dest directories.
    """
    console_w("  = informations =")

    #...........................................................................
    # source path
    #...........................................................................
    if not os.path.exists(SOURCE_PATH):
        # todo : error
        console_w("Can't read source path {0}.".format(SOURCE_PATH))
        return
    if not os.path.isdir(SOURCE_PATH):
        # error (todo)
        console_w("(source path) {0} isn't a directory.".format(SOURCE_PATH))
        return

    console_w("  = informations about the \"{0}\" (source) directory =".format(SOURCE_PATH))

    total_size = 0
    files_number = 0
    extensions = set()
    for dirpath, _, fnames in os.walk(SOURCE_PATH):
        for filename in fnames:
            complete_name = os.path.join(dirpath, filename)

            extensions.add(os.path.splitext(filename)[1])

            total_size += os.stat(complete_name).st_size
            files_number += 1

    console_w("    o files number : {0}".format(files_number))
    console_w("    o total size : ~{0:.2f} Mo; " \
              "~{1:.2f} Go; ({2} bytes)".format(total_size/1000000.0,
                                                total_size/1000000000.0,
                                                total_size))
    console_w("    o list of all extensions : {0}".format(tuple(extensions)))

   #...........................................................................
    # target path
    #...........................................................................
    if not os.path.exists(TARGET_PATH):
        console_w("Can't read target path {0}.".format(TARGET_PATH))
        return
    if not os.path.isdir(TARGET_PATH):
        # error (todo)
        console_w("(target path) {0} isn't a directory.".format(TARGET_PATH))
        return

    console_w("  = informations about the \"{0}\" (target) directory =".format(TARGET_PATH))

    if not os.path.exists(os.path.join(TARGET_PATH, DATABASE_NAME)):
        console_w("    o no database in the target directory o")
    else:
        db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
        db_connection = sqlite3.connect(db_filename)
        db_cursor = db_connection.cursor()

        console_w("    : hashid                                       : (target) file name : (source) original name")
        row_index=0
        for hashid, filename, originalname in db_cursor.execute('SELECT * FROM files'):
            if len(originalname)>INFO_ORIGINALNAME_MAXLENGTH_ON_SCREEN:
                originalname = "[...]"+originalname[-(INFO_ORIGINALNAME_MAXLENGTH_ON_SCREEN-5):]
            console_w("    o {0} : {1:18} : {2}".format(hashid,
                                                        filename,
                                                        originalname))
            row_index += 1
        if row_index == 0:
            console_w("    ! (empty database)")

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
                        help="no output to the console")

    parser.add_argument('--version',
                        action='version',
                        version="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
                        help="show the version and exit")

    return parser.parse_args()

#///////////////////////////////////////////////////////////////////////////////
def get_parameters(configfile_name):
    """
        read the configfile and return the parser.
    """
    if not os.path.exists(configfile_name):
        #todo
        raise

    parser = configparser.ConfigParser()
    parser.read(configfile_name)

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
    return base64.b64encode(hasher.digest()).decode()

#///////////////////////////////////////////////////////////////////////////////
def logfile_closing():
    """
        logfile_closing()

        close the log file
    """
    LOGFILE.close()

#///////////////////////////////////////////////////////////////////////////////
def logfile_first_message():
    """
        logfile_first_message()

        write $$todo$$$
    """
    logfile_w("*** {0} v.{1} ({2}) ***" \
              "\n\n".format(PROGRAM_NAME,
                            PROGRAM_VERSION,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

#///////////////////////////////////////////////////////////////////////////////
def logfile_opening():
    """
        logfile_opening()

        open the log file and return the result of the called to open().
    """
    if PARAMETERS["main.log_file"]["overwrite"] == "True":
        # overwrite :
        log_mode = "w"
    else:
        # let's append :
        log_mode = "a"

    logfile = open(PARAMETERS["main.log_file"]["name"], log_mode)

    return logfile

#///////////////////////////////////////////////////////////////////////////////
def logfile_w(msg):
    """
        logfile_w()

        Write <msg> into the logfile
    """
    LOGFILE.write(msg)

#///////////////////////////////////////////////////////////////////////////////
def read_sieves():
    """
        initialize SIEVES
    """
    stop = False
    sieve_index = 1
    while not stop:
        if not PARAMETERS.has_section("sieve"+str(sieve_index)):
            stop = True
        else:
            SIEVES[sieve_index] = dict()

            if PARAMETERS.has_option("sieve"+str(sieve_index), "name"):
                SIEVES[sieve_index]["name"] = \
                                    re.compile(PARAMETERS["sieve"+str(sieve_index)]["name"])
            if PARAMETERS.has_option("sieve"+str(sieve_index), "size"):
                SIEVES[sieve_index]["size"] = \
                                    re.compile(PARAMETERS["sieve"+str(sieve_index)]["size"])
        sieve_index += 1

#///////////////////////////////////////////////////////////////////////////////
def select():
    """
        $$$todo
        fill SELECT
    """
    console_w("  = selecting files according to the instructions " \
                "in the config file. Please wait... =")
    logfile_w("sieves : \n{0}\n\n".format(SIEVES))
    logfile_w("file list :\n")

    # big loop :
    total_size_of_the_selec_files = 0
    number_of_discarded_files = 0

    for dirpath, _, filenames in os.walk(SOURCE_PATH):
        for filename in filenames:
            complete_name = os.path.join(dirpath, filename)
            size = os.stat(complete_name).st_size

            res = the_file_can_be_added(filename, size)
            if not res:
                if LOG_VERBOSITY == "high":
                    logfile_w("(sieves described in the config file)" \
                              " discarded \"{0}\"\n".format(complete_name))
                    number_of_discarded_files += 1
            else:
                # is filename already stored in <TARGET_DB> ?
                _hash = hashfile(open(complete_name, 'rb'), hashlib.sha256())

                if _hash not in TARGET_DB:
                    res = True
                    SELECT[_hash] = complete_name

                    if LOG_VERBOSITY == "high":
                        logfile_w("+ {0}\n".format(complete_name))

                    total_size_of_the_selec_files += os.stat(complete_name).st_size
                else:
                    res = False

                    if LOG_VERBOSITY == "high":
                        logfile_w("(file's content already read) " \
                                  " discarded \"{0}\"\n".format(complete_name))
                        number_of_discarded_files += 1

    logfile_w("size of the selected files : ~{0:.2f} Mo; ~{1:.2f} Go; " \
              "({2} bytes)\n".format(total_size_of_the_selec_files/1000000.0,
                                     total_size_of_the_selec_files/1000000000.0,
                                     total_size_of_the_selec_files))

    if len(SELECT) == 0:
        logfile_w("! no file selected !")
    else:
        ratio = number_of_discarded_files/len(SELECT)*100.0
        logfile_w("number of selected files : {0} " \
                  "(after discarding {1} file(s), " \
                  "{2:.2f}% of all the files)\n".format(len(SELECT),
                                                        number_of_discarded_files,
                                                        ratio))

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

    sieve_size = PARAMETERS["sieve"+str(sieve_index)]["size"]

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
        console_w("  = creating the database in the target path...")
        logfile_w("creating the database in target path...")
        
        # let's create a new database in the target directory :
        db_connection = sqlite3.connect(db_filename)
        db_cursor = db_connection.cursor()

        db_cursor.execute('''CREATE TABLE files
        (hashid text, name text, originalname text)''')

        db_connection.commit()
        
        db_connection.close()

        console_w("  = ... database created.")
        logfile_w("... database created.")

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
    if ARGS.add==True and ARGS.select==True:
        # $$$ todo $$$
        raise

#///////////////////////////////////////////////////////////////////////////////
def add():
    """
        Add the source files to the destination path.

        todo : d'abord appeler select()
    """
    db_filename = os.path.join(TARGET_PATH, DATABASE_NAME)
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()

    files_to_be_added = []
    for index, hashid in enumerate(SELECT):
        original_name = SELECT[hashid]

        short_final_name = str(len(TARGET_DB) + index)
        final_name = os.path.join(TARGET_PATH, short_final_name)

        console_w("... copying \"{0}\" to \"{1}\" .".format(original_name, final_name))
        logfile_w("... copying \"{0}\" to \"{1}\" .".format(original_name, final_name))
        shutil.copyfile(original_name, final_name)

        files_to_be_added.append( (hashid, short_final_name, original_name) )

    db_cursor.executemany('INSERT INTO files VALUES (?,?,?)', files_to_be_added)
    db_connection.commit()

    db_connection.close()

#///////////////////////////////////////////////////////////////////////////////
#/////////////////////////////// STARTING POINT ////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
ARGS = get_args()
check_args()

PARAMETERS = get_parameters(ARGS.configfile)
USE_LOG_FILE = PARAMETERS["main.log_file"]["use log file"] == "True"
LOG_VERBOSITY = PARAMETERS["main.log_file"]["verbosity"]
TARGET_DB = []  # a list of hashid
TARGET_PATH = PARAMETERS["target"]["path"]
INFO_ORIGINALNAME_MAXLENGTH_ON_SCREEN = int(PARAMETERS["infos"]["original name.max length on console"])

SOURCE_PATH = PARAMETERS["main.source"]["sourcepath"]

LOGFILE = None
if USE_LOG_FILE:
    LOGFILE = logfile_opening()
    logfile_first_message()

console_first_message()

if not os.path.exists(TARGET_PATH):
    console_w("  ! Since the destination path \"{0}\" " \
              "doesn't exist, let's create it.".format(TARGET_PATH))
    logfile_w("Since the destination path \"{0}\"" \
              "doesn't exist, let's create it.".format(TARGET_PATH))
    os.mkdir(TARGET_PATH)

SELECT = {} # hashid : filename
    
if ARGS.infos:
    infos()
if ARGS.select:
    read_target_db()
    read_sieves()
    select()
if ARGS.add:
    read_target_db()
    read_sieves()
    select()
    add()

if USE_LOG_FILE:
    logfile_closing()

console_w("=== exit (stopped at {0}; " \
          "duration time : {1}) ===".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            datetime.now() - TIMESTAMP_BEGIN))

