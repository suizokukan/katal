#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#    Katalogoi Copyright (C) 2012 Suizokukan
#    Contact: suizokukan _A.T._ orange dot fr
#
#    This file is part of Katalogoi.
#    Katalogoi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Katalogoi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Katalogoi.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
        Katalogoi project

        from the Ancient Greek κατάλογος "enrolment, register, catalogue"
"""
import argparse
import base64
import configparser
import hashlib
from datetime import datetime
import os
import re

PROGRAM_NAME = "Katalogoi"
PROGRAM_VERSION = "0.0.1"

SELECTIONS = {}
DEFAULT_CONFIGFILE_NAME = "katalogoi.ini"
TIMESTAMP_BEGIN = datetime.now()

#///////////////////////////////////////////////////////////////////////////////
def console_first_message():
    """
        console_first_message()

        $$todo$$
    """
    console_msg("=== {0} v.{1} ({2}) ===".format(PROGRAM_NAME,
                                                 PROGRAM_VERSION,
                                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

#///////////////////////////////////////////////////////////////////////////////
def console_msg(msg):
    """
            console_msg()

            Send a message to the console if not in quiet mode.
    """
    if not ARGS.quiet:
        print(msg)

#///////////////////////////////////////////////////////////////////////////////
def display_informations_about(path):
    """
        display (on the console) some informations about path.
    """
    if not os.path.exists(path):
        # todo : error
        console_msg("Can't read path {0}.".format(path))
        return
    if not os.path.isdir(path):
        console_msg("{0} isn't a directory.".format(path))
        return

    console_msg("  = informations about the \"{0}\" directory =".format(path))

    total_size = 0
    files_number = 0
    extensions = set()
    for dirpath, _, fnames in os.walk(path):
        for filename in fnames:
            complete_name = os.path.join(dirpath, filename)

            extensions.add(os.path.splitext(filename)[1])

            total_size += os.stat(complete_name).st_size
            files_number += 1

    console_msg("  o files number : {0}".format(files_number))
    console_msg("  o total size : ~{0:.2f} Mo; " \
                "~{1:.2f} Go; ({2} bytes)".format(total_size/1000000.0,
                                                  total_size/1000000000.0,
                                                  total_size))
    console_msg("  o list of all extensions : {0}".format(tuple(extensions)))

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
def read_selections():
    """
        initialize SELECTIONS
    """
    stop = False
    selection_index = 1
    while not stop:
        if not PARAMETERS.has_section("selection"+str(selection_index)):
            stop = True
        else:
            SELECTIONS[selection_index] = dict()

            if PARAMETERS.has_option("selection"+str(selection_index), "name"):
                SELECTIONS[selection_index]["name"] = \
                                    re.compile(PARAMETERS["selection"+str(selection_index)]["name"])
            if PARAMETERS.has_option("selection"+str(selection_index), "size"):
                SELECTIONS[selection_index]["size"] = \
                                    re.compile(PARAMETERS["selection"+str(selection_index)]["size"])
        selection_index += 1

#///////////////////////////////////////////////////////////////////////////////
def select():
    """
        $$$todo
    """

    console_msg("  = selecting files according to the instructions " \
                "in the config file. Please wait... =")
    logfile_w("selections : \n{0}\n\n".format(SELECTIONS))
    logfile_w("file list :\n")

    # big loop :
    files = {}      # hash : complete_name
    total_size_of_the_selec_files = 0
    number_of_discarded_files = 0

    for dirpath, _, filenames in os.walk(PARAMETERS["main.source"]["sourcepath"]):
        for filename in filenames:
            complete_name = os.path.join(dirpath, filename)
            size = os.stat(complete_name).st_size

            res = the_file_can_be_selected(filename, size)
            if not res:
                if LOG_VERBOSITY == "high":
                    logfile_w("(selections described in the config file)" \
                              " discarded \"{0}\"\n".format(complete_name))
                    number_of_discarded_files += 1
            else:
                # is filename already stored in <files> ?
                _hash = hashfile(open(complete_name, 'rb'), hashlib.sha256())

                if _hash not in files:
                    res = True
                    files[_hash] = complete_name

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

    if len(files) == 0:
        logfile_w("! no file selected !")
    else:
        logfile_w("number of selected files : {0} " \
                  "(after discarding {1} file(s), " \
                  "{2:.2f}% of all the files)\n".format(len(files),
                                                        number_of_discarded_files,
                                                        number_of_discarded_files/len(files)*100.0))

    if USE_LOG_FILE:
        logfile_closing()

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_selected(filename, size):
    """
                return (bool)res
    """
    # to be True, one of the selections must match the file given as a parameter :
    res = False

    for selection_index in SELECTIONS:
        selection = SELECTIONS[selection_index]

        selection_res = True

        if selection_res and "name" in selection:
            selection_res = the_file_can_be_selected__name(selection, filename)

        if selection_res and "size" in selection:
            selection_res = the_file_can_be_selected__size(selection_index, size)

        # at least, one selection is ok with this file :
        if selection_res:
            res = True
            break

    return res

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_selected__name(selection, filename):
    """
        the_file_can_be_selected__name()

        apply a selection based on the name to <filename>.
    """
    return re.match(selection["name"], filename)

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_selected__size(selection_index, size):
    """
        the_file_can_be_selected__size()

        apply a selection based on the size on <size>.
    """
    res = False

    selection_size = PARAMETERS["selection"+str(selection_index)]["size"]

    if selection_size.startswith(">"):
        if size > int(selection_size[1:]):
            res = True
    if selection_size.startswith(">="):
        if size >= int(selection_size[2:]):
            res = True
    if selection_size.startswith("<"):
        if size < int(selection_size[1:]):
            res = True
    if selection_size.startswith("<="):
        if size <= int(selection_size[2:]):
            res = True
    if selection_size.startswith("="):
        if size == int(selection_size[1:]):
            res = True

    return res

#///////////////////////////////////////////////////////////////////////////////
#/////////////////////////////// STARTING POINT ////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
ARGS = get_args()
PARAMETERS = get_parameters(ARGS.configfile)
USE_LOG_FILE = PARAMETERS["main.log_file"]["use log file"] == "True"
LOG_VERBOSITY = PARAMETERS["main.log_file"]["verbosity"]

LOGFILE = None
if USE_LOG_FILE:
    LOGFILE = logfile_opening()
    logfile_first_message()

console_first_message()

if ARGS.infos:
    display_informations_about(PARAMETERS["main.source"]["sourcepath"])
if ARGS.select:
    read_selections()
    select()

console_msg("=== exit === ({0}) ===".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
console_msg("duration time : {0}".format(datetime.now() - TIMESTAMP_BEGIN))
