PROGRAM_NAME = "Katalogoi"
PROGRAM_VERSION = "0.0.1"
import argparse
import base64
import configparser
import hashlib
from datetime import datetime
import os
import re

SELECTIONS = {}
DEFAULT_CONFIGFILE_NAME = "katalogoi.ini"
TIMESTAMP_BEGIN = datetime.now()

#///////////////////////////////////////////////////////////////////////////////
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    #return hasher.digest()
    #return hasher.hexdigest()
    return base64.b64encode(hasher.digest()).decode()

#///////////////////////////////////////////////////////////////////////////////
def display_informations_about(path):
    """
        display (on the console) some informations about path.
    """
    if not os.path.exists(path):
        # todo : error
        print("Can't read path {0}.".format(path))
        return
    if not os.path.isdir(path):
        print("{0} isn't a directory.".format(path))
        return

    print("=== {0} v.{1} ({2}) ===".format(PROGRAM_NAME,
                                           PROGRAM_VERSION,
                                           datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("  = informations about the \"{0}\" directory =".format(path))

    total_size = 0
    files_number = 0
    extensions = set()
    for dirpath, dnames, fnames in os.walk(path):
        for f in fnames:
            complete_name = os.path.join(dirpath, f)

            extensions.add( os.path.splitext(f)[1] )
            
            total_size += os.stat(complete_name).st_size
            files_number += 1

    print("  o files number : {0}".format(files_number))
    print("  o total size : ~{0:.2f} Mo; ~{1:.2f} Go; ({2} bytes)".format(total_size/1000000.0,
                                                                          total_size/1000000000.0,
                                                                          total_size))
    print("  o list of all extensions : {0}".format(tuple(extensions)))

#///////////////////////////////////////////////////////////////////////////////
def get_args():
    """
        Read the command line arguments.

        Return the argparse object.
    """
    parser = argparse.ArgumentParser(description="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
                                     epilog="by suizokukan AT orange DOT fr",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--version',
                        action='version',
                        version="{0} v. {1}".format(PROGRAM_NAME, PROGRAM_VERSION),
                        help="show the version and exit")

    parser.add_argument('--configfile',
                        type=str,
                        default=DEFAULT_CONFIGFILE_NAME,
                        help="config file, e.g. config.ini")

    parser.add_argument('--infos',
                        action="store_true",
                        help="display informations about the source directory " \
                             "given in the configuration file")

    parser.add_argument('--proceed',
                        action="store_true",
                        help="proceed to what is described in the configuration file")

    return parser.parse_args()

#///////////////////////////////////////////////////////////////////////////////
def get_parameters(configfile_name):
    if not os.path.exists(configfile_name):
        #todo
        raise
    
    parser = configparser.ConfigParser()
    parser.read(configfile_name)
    return parser

#///////////////////////////////////////////////////////////////////////////////
def the_file_can_be_selected(complete_name, filename, size, files):
    """
                return (bool)res
    """
    # to be True, one of the selections must match the file given as a parameter :
    res = False

    for selection_index in SELECTIONS:
        selection = SELECTIONS[selection_index]

        selection_res = True

        if selection_res and "name" in selection:
            selection_res = False

            if re.match(selection["name"], filename):
                selection_res = True

        if selection_res and "size" in selection:
            selection_res = False

            selection_size = PARAMETERS["selection"+str(selection_index)]["size"]

            if selection_size.startswith(">"):
                if size>int(selection_size[1:]):
                    selection_res = True
            if selection_size.startswith(">="):
                if size>=int(selection_size[2:]):
                    selection_res = True
            if selection_size.startswith("<"):
                if size<int(selection_size[1:]):
                    selection_res = True
            if selection_size.startswith("<="):
                if size<=int(selection_size[2:]):
                    selection_res = True
            if selection_size.startswith("="):
                if size==int(selection_size[1:]):
                    selection_res = True

        # at least, one selection is ok with this file :
        if selection_res:
            res = True
            break

    return res

#///////////////////////////////////////////////////////////////////////////////
def proceed():

    print("  = proceeding according to the instructions in the config file. Please wait... =")

    # log file mode :
    if PARAMETERS["main.log_file"]["overwrite"]=="True":
        # overwrite :
        log_mode="w"
    else:
        # let's append :
        log_mode="a"

    # big loop :
    with open(PARAMETERS["main.log_file"]["name"], log_mode) as logfile:
        logfile.write("*** {0} v.{1} ({2}) ***\n".format(PROGRAM_NAME,
                                                         PROGRAM_VERSION,
                                                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        logfile.write("selections : \n{0}\n".format(SELECTIONS))

        files = {}      # hash : complete_name
        total_size_of_the_selected_files = 0
        
        for dirpath, _, filenames in os.walk(PARAMETERS["main.source"]["sourcepath"]):
            for filename in filenames:
                complete_name = os.path.join(dirpath, filename)
                size = os.stat(complete_name).st_size
                
                res = the_file_can_be_selected(complete_name, filename, size, files)
                if not res:
                    logfile.write("(selections described in the config file)" \
                                  " discarded \"{0}\"\n".format(complete_name))
                else:
                    # is filename already stored in <files> ?
                    _hash = hashfile(open(complete_name, 'rb'), hashlib.sha256())

                    if _hash not in files:
                        res = True
                        files[_hash] = complete_name
                        logfile.write("+ {0}".complete_name)
                        total_size_of_the_selected_files += os.stat(complete_name).st_size
                    else:
                        res = False
                        logfile.write("(file's content already read) " \
                                      " discarded \"{0}\"\n".format(complete_name))

        logfile.write("size of the selected files : ~{0:.2f} Mo; ~{1:.2f} Go; " \
                      "({2} bytes)\n".format(total_size_of_the_selected_files/1000000.0,
                                             total_size_of_the_selected_files/1000000000.0,
                                             total_size_of_the_selected_files))

#///////////////////////////////////////////////////////////////////////////////
def read_selections():
    """
        initialize SELECTIONS
    """
    stop = False
    selection_index=1
    while not stop:
        if not PARAMETERS.has_section("selection"+str(selection_index)):
            stop=True
        else:
            SELECTIONS[selection_index]=dict()
            if PARAMETERS.has_option("selection"+str(selection_index), "name"):
                SELECTIONS[selection_index]["name"]=\
                                    re.compile(PARAMETERS["selection"+str(selection_index)]["name"])
            if PARAMETERS.has_option("selection"+str(selection_index), "size"):
                SELECTIONS[selection_index]["size"]=\
                                    re.compile(PARAMETERS["selection"+str(selection_index)]["size"])
        selection_index+=1

#///////////////////////////////////////////////////////////////////////////////
#/////////////////////////////// STARTING POINT ////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////
ARGS = get_args()
PARAMETERS = get_parameters(ARGS.configfile)

if ARGS.infos:
    display_informations_about(PARAMETERS["main.source"]["sourcepath"])
if ARGS.proceed:
    read_selections()
    proceed()

print("=== exit === ({0}) ===".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))    
print("duration time : {0}".format(datetime.now() - TIMESTAMP_BEGIN))


