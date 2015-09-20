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

        ________________________________________________________________________

        The name Katal comes from the Ancient Greek κατάλογος ("enrolment, 
        register, catalogue").
        ________________________________________________________________________

        ________________________________________________________________________

        exit codes :

                 0      : success
                -1      : can't read the parameters from the configuration file
                -2      : a ProjectError exception has been raised
                -3      : an unexpected exception exception has been raised
        ________________________________________________________________________
        ________________________________________________________________________


(1) configuration file
The informations stored in the configuration file are written in the PARAMETERS global variable.
PARAMETERS is filled by read_parameters_from_cfgfile() and is a configparser.Configparser object.
The default name of the configuration file is set by the DEFAULT_CONFIGFILE_NAME global variable
and may be set by the commande line (see --configfile option).

[log file]    : parameters about the logfile
use log file  : True/False; if False, all the messages are written only to the console.
name          : no quotation mark here !
overwrite     : True/False; if False, the log file will grow after each execution.
verbosity     : log verbosity="high" or "low"; turn if off (=low) if the log message is too big 
                or too verbose.

[display]         : parameters about the way informations are displayed
target filename.max length on console : (max length of the file names displayed)
source filename.max length on console : (max length of the file names displayed)

[source]          : parameters about source directory 
path              : a string without any quotation mark.

[source.sieveN]   : N is an integer greater or equal to  1; [source.sieve1], [source.sieve2], ...
name              : a regex; e.g. for all files with an .jpg extension : .*\.jpg$
size              : a symbol plus an integer
                    e.g., either >999, either <999, either =999, either <=999 either >=999

[target]                  : parameters about target directory 
path                      : a string without any quotation mark.

name of the target files  : a string using keywords which will be replaced by their value
                            see the create_target_name() function.

                                  known keywords :

                                   HASHID
                                   SOURCENAME_WITHOUT_EXTENSION
                                   SOURCENAME_WITHOUT_EXTENSION2
                                   SOURCE_PATH
                                   SOURCE_PATH2
                                   SOURCE_EXTENSION
                                   SOURCE_EXTENSION2
                                   SIZE
                                   DATE2
                                   DATABASE_INDEX

                                   n.b. : keywords ending by "2" are builded 
                                          against a set of illegal characters
                                          replaced by "_".

(2) logfile
Can be filled with many informations (verbosity="high") or less informations (verbosity="low"). See in documentation:configuration file the explanations about the log verbosity.

The logfile is opened by logfile_opening. The program writes in it via msg() if _for_logfile is
set to True.

(3) selection

SELECT is filled by fill_select(), a function called by action__select(). SELECT is a dictionary with hashid as keys and SELECTELEMENT as values.

Definition of SELECTELEMENT :
  SELECTELEMENT = namedtuple('SELECTELEMENT', ["complete_name",
                                               "path",
                                               "filename_no_extens",
                                               "extension",
                                               "size",
                                               "date"])

  !!! an "extension" stored in SELECTELEMENT does not start with a dot (".") !!!

SIEVES is a dictionary with a (int)sieve_index as a key and a dict as values.
This dict may be empty or contain the following keys/values : 
  SIEVES["name"] = re.compile(...)
  SIEVES["size"] = a string like ">999", initial symbol in ('=', '<', '>', '<=', '>=')
  SIEVES["date"] = a string like '>2015-09-17 20:01', initial symbol in ('=', '<', '>', '<=', '>=')
SIEVES is filled by read_sieves().

(4) database
In every target directory a database is created and filled. Its name is set by the
global variable DATABASE_NAME.
TARGET_DB is a list of hashids and initialized by read_target_db().

(A) history

    v.0.0.5 (2015_09_17) :
        o  added --targetkill/-tk option and the action__targetkill() function
        o  improved show_infos_about_target_path() : each column has its own separator,
           the table is computed by the function : no more magic numbers
        o  added -ti, --targetinfos option (--targetinfos/-ti uses --quiet mode)
        o  added --settag, --to options
        o  fixed get_disk_free_space() for Windows systems
        o  added short options for some options : -c, -s, -ti, -m, -q
        o  'shortened_str' > 'shortstr'
        o  added a 'tag' field in the database

    v.0.0.4 (2015_09_16) :
        o  Tests class (four tests ok)
        o  added eval formula in config file; added function eval_sieve_for_a_file()
        o  fixed a typo in size_as_str() : the '0 byte' case
        o  fixed a bug in hashfile64() : the hasher is now created every time 
           the function is called
        o  modified the SIEVES format for "size"
        o  moved the declaration of global variables at the beginning of the file
        o  added a block : if __name__ == '__main__', allowing to call the script
           from another script.
        o  modified the database data types : hashid=varchar(44); primary key on hashid
        o  improved the way the program catches the exceptions
        o  improved action__infos() display : for each extension the size in bytes is
           displayed
        o  updated .gitignore 
        o  "VERBOSITY" > "LOG_VERBOSITY"; TARGETFILENAME_* > TARGETNAME_*
        o  added FREESPACE_MARGIN constant
        o  renamed some functions (get_* > read_*)

    v.0.0.3 (2015_09_14) :
        o  --quiet and --mute options
        o  --hashid option (and show_hashid_of_a_file() function)
        o  fixed the error in the shebang line
        o  rewrote remove_illegal_character()
        o  improved action__select() : no useless messages are displayed with the
            --add option

    v.0.0.2 (2015_09_14) :
        o  added SELECTELEMENT type
        o  the call to sys.exit(0) is now at the very end of the file
        o  no tests, pylint=10.0, some todos remain.

            no tests, pylint=10.0, some todos remain.

    v.0.0.1 (2015_09_13) : first try, no tests, pylint=10.0, some todos
                           remain.

(B) arguments

  arguments
    
  -h, --help            show this help message and exit
  --add                 select files according to what is described in the
                        configuration file then add them to the target
                        directoryThis option can't be used the --select one.
                        (default: False)
  -c CONFIGFILE, --configfile CONFIGFILE
                        config file, e.g. config.ini (default: katal.ini)
  --hashid HASHID       return the hash id of the given file (default: None)
  --infos               display informations about the source directory given
                        in the configuration file (default: False)
  -s, --select          select files according to what is described in the
                        configuration file without adding them to the target
                        directory. This option can't be used the --add one.
                        (default: False)
  -ti, --targetinfos    display informations about the target directory in
                        --quiet mode (default: False)
  -m, --mute            no output to the console; no question asked on the
                        console (default: False)
  -q, --quiet           no welcome/goodbye/informations about the parameters/
                        messages on console (default: False)
  --settag SETTAG       give the tag to some file(s) in combination with the
                        --to option (default: None)
  --to TO               give the name of the file(s) concerned by --settag.
                        The argument is a regex; e.g. to select all .py files,
                        use --to=".*\.py$ (default: None)
  --version             show the version and exit

(C) the database

        hashid (primary key): varchar(44)
        name                : text
        sourcename          : text
        tag                 : text

(D) the functions

o  action__add()                        : add the source files to the destination
                                          path.
o  action__downloadefaultcfg            : download the default configuration file
o  action__infos()                      : display informations about the source
                                          and the target directory
o  action__select()                     : fill SELECT and SELECT_SIZE_IN_BYTES and
                                          display what's going on.
o  action__settag()                     : Modify the tag(s) in the target directory,
                                          overwriting ancient tags.
o  action__target_kill()                : delete a filename from the target directory
                                          and from the database
o  check_args()                         : check the arguments of the command line.
o  create_target_name()                 : create the name of a file (a target file)
                                          from various informations read from a
                                          source file
o  eval_sieve_for_a_file()              : evaluate a file according to a sieve
o  fill_select                          : fill SELECT and SELECT_SIZE_IN_BYTES from
                                          the files stored in SOURCE_PATH.
o  get_disk_free_space()                : return the available space on disk
o  goodbye()                            : display the goodbye message
o  logfile_opening()                    : open the log file
o  hashfile64()                         : return the footprint of a file, encoded
                                          with the base 64.
o  msg()                                : display a message on console, write the
                                          same message in the log file.
o  parameters_infos()                   : display some informations about the
                                          content of the configuration file
o  read_command_line_arguments()        : read the command line arguments
o  read_parameters_from_cfgfile()       : read the configuration file
o  read_sieves()                        : initialize SIEVES from the configuration file
o  read_target_db()                     : read the database stored in the target
                                          directory and initialize TARGET_DB.
o  remove_illegal_characters()          : replace some illegal characters by the
                                          underscore character.
o  shortstr()                           : shorten a string
o  show_hashid_of_a_file()              : the function gives the hashid of a file.
o  show_infos_about_source_path()       : display informations about source path
o  show_infos_about_target_path()       : display informations about target path
o  size_as_str()                        : return a size in bytes as a human-readable
                                          string
o  the_file_has_to_be_added()           : return True if a file can be choosed and added to
                                        : the target directory
o  the_file_has_to_be_added__name()     : a part of the_file_has_to_be_added()
o  the_file_has_to_be_added__size()     : a part of the_file_has_to_be_added()
o  welcome()                            : display a welcome message on screen
o  welcome_in_logfile()                 : display a welcome message in the log file
