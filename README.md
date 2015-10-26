#(1) Katal
A (Python3/GPLv3/OSX-Linux-Windows/CLI) project, using no additional modules than the ones installed with Python3.

Create a catalogue from various source directories, without any duplicate. Add some tags to the files.

#(2) purpose
Read a directory, select some files according to a configuration file (leaving aside the duplicates), copy the selected files in a target directory.
Once the target directory is filled with some files, a database is added to the directory to avoid future duplicates. You can add new files to the target directory by using Katal one more time, with a different source directory.

#(3) installation

    $ pip install katal

    or

    $ wget https://github.com/suizokukan/katal/blob/master/katal/katal.py
    Since katal.py is a stand-alone file, you may place this file in the target directory.
    
#(4) how to use (in brief)

    Create the target directory :
    
    $ katal --new myworkingdirectory

    Check if everything's is alright :

    $ katal --infos

    Modify the .ini file (myworkingdirectory/.katal/katal.ini), choose a source.

    Check if everything's is alright :

    $ katal --select  ... and answer 'yes' to the final question if all the details are ok to you.    

#(5) author
suizokukan (suizokukan AT orange DOT fr)

#(6) name
The name Katal is derived from the Ancient Greek κατάλογος ("enrolment, register, catalogue").

#(7) arguments

      -h, --help            show this help message and exit
      --add                 select files according to what is described in the
                            configuration file then add them to the target
                            directory. This option can't be used with the --select
                            one.If you want more informations about the process,
                            please use this option in combination with --infos .
                            (default: False)
      --addtag ADDTAG       Add a tag to some file(s) in combination with the --to
                            option. (default: None)
      -cfg CONFIGFILE, --configfile CONFIGFILE
                            config file, e.g. config.ini (default: None)
      --cleandbrm           Remove from the database the missing files in the
                            target path. (default: False)
      -ddcfg, --downloaddefaultcfg
                            Download the default config file and overwrite the
                            file having the same name. This is done before the
                            script reads the parameters in the config file
                            (default: False)
      --hashid HASHID       return the hash id of the given file (default: None)
      --infos               display informations about the source directory given
                            in the configuration file. Help the --select/--add
                            options to display more informations about the process
                            : in this case, the --infos will be executed before
                            --select/--add (default: False)
      -m, --mute            no output to the console; no question asked on the
                            console (default: False)
      -n NEW, --new NEW     create a new target directory (default: None)
      --off                 don't write anything into the target directory or into
                            the database, except into the current log file. Use
                            this option to simulate an operation : you get the
                            messages but no file is modified on disk, no directory
                            is created. (default: False)
      --rebase REBASE       copy the current target directory into a new one : you
                            rename the files in the target directory and in the
                            database. First, use the --new option to create a new
                            target directory, modify the .ini file of the new
                            target directory (modify [target]name of the target
                            files), then use --rebase with the name of the new
                            target directory (default: None)
      --rmnotags            remove all files without a tag (default: False)
      --rmtags              remove all the tags of some file(s) in combination
                            with the --to option. (default: False)
      -s, --select          select files according to what is described in the
                            configuration file without adding them to the target
                            directory. This option can't be used with the --add
                            one.If you want more informations about the process,
                            please use this option in combination with --infos .
                            (default: False)
      --setstrtags SETSTRTAGS
                            give the string tag to some file(s) in combination
                            with the --to option. Overwrite the ancient string
                            tag. If you want to empty the tags' string, please use
                            a space, not an empty string : otherwise the parameter
                            given to the script wouldn't be taken in account by
                            the shell (default: None)
      --targetpath TARGETPATH
                            target path, usually '.' . If you set path to . (=dot
                            character), it means that the source path is the
                            current directory (=the directory where the script
                            katal.py has been launched) (default: .)
      -ti, --targetinfos    display informations about the target directory
                            (default: False)
      -tk TARGETKILL, --targetkill TARGETKILL
                            kill (=move to the trash directory) one file from the
                            target directory.DO NOT GIVE A PATH, just the file's
                            name, without the path to the target directory
                            (default: None)
      --to TO               give the name of the file(s) concerned by
                            --setstrtags. wildcards accepted; e.g. to select all
                            .py files, use '*.py' . Please DON'T ADD the path to
                            the target directory, only the filenames (default:
                            None)
      --version             show the version and exit

#(8) history

    v.0.1.3 (2015_10_25)

        o remove HEXDATE from the target file's formats.
        o remove the --quiet option
        o rename option : -c > -cfg

        o after --add or --select the informations about the target path are displayed,
          not about the source directory.
        o fixed a critical bug in action__target_kill()
        o improved various messages
        o improved the documentation

        o 7 tests, pylint=10.0
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.2 (2015_10_23)

        o added the --rebase option : copy a target directory into a new one and change
          the filenames.
        o added two filename's formats : INTTIMESTAMP and HEXTIMESTAMP
        o fixed action__add()
          action__add() modifies the timestamp of the files in the target path so that
          this timestamp is equal to the original file.

        o replace fromtimestamp() by utcfromtimestamp()
        o improved normpath() : special strings like ".." are now developped.
        o improved remove_illegal_characters() : added the ("-", " ") characters to the list
          of the forbidden characters.
        o modified create_target_name()
          create_target_name() takes from now another parameter, the _parameter one,
          allowing to choose which config file is choosed when calling the function.
        o added the SQL__CREATE_DB constant
        o added main_actions_tags() function to relief main_actions().
        o improved messages in action__rebase__write() : added the number of the current
          file to be copied.
        o fixed the message displayed in action__rebase__write()

        o 7 tests, pylint=10.0
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)
    
    v.0.1.1 (2015_10_21)

        o fixed create_target_name() : added HEXDATE as a name format
        o added 2 checks at the end of fill_select()
          The function fill_select__checks() checks that :
          (1) future filename's can't be in conflict with another file in SELECT
          (2) future filename's can't be in conflict with another file already
          stored in the target path

        o fixed a bug in action__cleandbrm()
        o fixed main_warmup() : show informations if the -ti/--targetinfos paramater is given
        o fixed show_infos_about_source_path() : no returned value
        o added the call to actions__infos() if the --infos option is used
        o added normpath() function, used every time a os.path.* function is called

        o 7 tests, pylint=10.0
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.0 (2015_10_14)
    
        o added the --targetpath option
        o added the -n/--new option
        o the configuration file, the trash/log/tasks subsubdirectories are now stored
          inside a "katal system" subdirectory inside the target directory. 

        o check_before_commit_a_new_version.sh > check_and_commit_a_new_version.sh
          the script has 2 new steps : 'pylint tests/tests.py' and 'git commit -a'.
        o added a global constant, DATABASE_FULLNAME
        o added a new global constant, DEFAULTCFGFILE_URL
        o removed the parameters_infos() function
        o added a new function, create_subdirs_in_target_path(), to relieve main_warmup()
        o the function action__downloadefaultcfg() now returns a (bool)success
        o the function action__downloadefaultcfg() now takes an argument, newname.
        o fixed the tests script (targetpath is defined outside the test class/methods)
        o the documentation, the error messages and katal.ini have been improved

        o 7 tests, pylint=10.0
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.0.9 (2015_10_12)
    
        o --off option : don't write anything into the target directory or into
          the database.

        o added some files required by Pypi : setup.py, README.rst, setup.cfg and
          the katal/ subdirectory
        o added a function for the main entry point : main()
        o the documentation, the error messages and katal.ini have been improved
        o added the script check_before_commit_a_new_version.sh

        o 7 tests, pylint=10.0
        o first version to be packaged and send to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.0.8 (2015_10_04)
    
        o --rmnotags option : added the action__rmnotags() function
        o deleted files are moved to a trash subdirectory, inside the target
          directory. (see issue #13)
    
        o in modified action__target_kill() : return an error code if there's no database.
        o fixed an important bug in modify_the_tag_of_some_files() :
          the files are now correctly choosed along with the --to argument's content
        o modified logfile__opening(): rename old log files so that they can be
          easily deleted (issue #15)
        o added a new column in the database : 'sourcedate'
        o in logfile_opening() : if the opening mode is "append", save the last
          log file with a different name to prevent its overwriting.
        o added global constant TAG_SEPARATOR
        o database 'name' and 'hashid' are unique from now;
        o the documentation and the error messages have been improved
    
        o 7 tests, pylint=10.0

    v.0.0.7 (2015_09_28)
        o --cleandbrm option : Remove from the database the missing files in
          the target path; added the action__cleandbrm() function (issue #1)

        o modified msg() function : new parameter "_important_msg"
          If _important_msg is False, the message will be printed only if
          LOG_VERBOSITY is set to "high" .
        o fixed a minor bug in fill_select() : number_of_discarded_files is
          now correctly computed
        o improved code readibility by using sqlite3.Row as a row factory.    
        o fixed show_infos_about_target_path()::draw_table() : characters like "║"
          are forbidden (problem with the cp1252 
        o modified msg() : messages are written to the console first
        o (issue #4) fill_select() adds a percentage of the work done based on
          the informations gathered by the --infos options.
        o modified show_infos_about_source_path() : added the number of the
          extensions found in the source directory (issue #2).
        o modified show_infos_about_source_path() : extensions are now sorted by name
        o the documentation and the error messages have been improved

        o 7 tests, pylint=10.0

    v.0.0.6 (2015_09_23)
        o  added a new sieve (by date)
        o  added option -ddcfg / --downloaddefaultcfg
        o  added --rmtags option
        o  added --addtag option
        o  the --to option takes from now wildcards name, not a regex anymore
    
        o (database) 'tag' > 'strtag'; --settag > --setstrtag
        o  improved security : eval() function is now used in the secured way
        o  welcome_* functions now use the TIMESTAMP_BEGIN global variable
        o various parts of the documentation and error messages have been improved

        o 7 tests, pylint=10.0

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

#(9) technical details

##(9.1) exit codes
                 0      : success
                -1      : can't read the parameters from the configuration file
                -2      : a ProjectError exception has been raised
                -3      : an unexpected exception exception has been raised

##(9.2) configuration file
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
                                       SOURCE_EXTENSION     (no . character)
                                       SOURCE_EXTENSION2    (no . character)
                                       SIZE
                                       DATE2
                                       DATABASE_INDEX
                                       INTTIMESTAMP         (e.g. 1445584562)
                                       HEXTIMESTAMP         (e.g. 5629DED0)

                                       n.b. : keywords ending by "2" are builded 
                                              against a set of illegal characters
                                              replaced by "_".

##(9.3) logfile
Can be filled with many informations (verbosity="high") or less informations (verbosity="low"). See in documentation:configuration file the explanations about the log verbosity.

The logfile is opened by logfile_opening. The program writes in it via msg() if _for_logfile is
set to True.

##(9.4) selection

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

##(9.5) database
In every target directory a database is created and filled. Its name is set by the
global variable DATABASE_NAME.
TARGET_DB is a list of hashids and initialized by read_target_db().
    
    o hashid varchar(44) PRIMARY KEY UNIQUE : hashid
    o name text UNIQUE                      : (target) name
    o sourcename text                       : complete path + name + extension
    o sourcedate integer                    : epoch time
    o strtags text                          : a list of tags separated by the TAG_SEPARATOR
                                              symbol.

##(9.6) trash directory
the deleted files are placed in a trashed directory placed inside the target directory. The
trash name is defined in the configuration file.    


##(9.7) the database

        hashid (primary key): varchar(44)
        name                : text
        sourcename          : text
        strtags             : text

##(9.8) the functions

    o  action__add()                        : add the source files to the target
                                              path.
    o  action__addtag()                     : add one tag to the string tags of some files
    o  action__cleandbrm()                  : remove from the database the missing files
    o  action__downloadefaultcfg()          : download the default configuration file
    o  action__infos()                      : display informations about the source
                                              and the target directory
    o  action__rebase()                     : copy a target directory into a new one
    o  action__rebase__files()              : --rebase : select the files to be copied.
    o  action__rebase__write()              : --rebase : write the files into the new target direc.
    o  action__rmnotags()                   : Remove all files if they have no tags.
    o  action__rmtags()                     : remove the entire string tags of some files
    o  action__select()                     : fill SELECT and SELECT_SIZE_IN_BYTES and
                                              display what's going on.
    o  action__setstrtags()                 : Modify the string tag in the target directory,
                                              overwriting ancient tags.
    o  action__target_kill()                : delete a filename from the target directory
                                              and from the database
    o  check_args()                         : check the arguments of the command line.
    o  create_subdirs_in_target_path()      : create the expected subdirectories in TARGET_PATH .
    o  create_target_name()                 : create the name of a file (a target file)
                                              from various informations read from a
                                              source file
    o  eval_sieve_for_a_file()              : evaluate a file according to a sieve
    o  fill_select()                        : fill SELECT and SELECT_SIZE_IN_BYTES from
                                              the files stored in SOURCE_PATH.
    o  fill_select__checks()                : final checks at the end of fill_select()
    o  get_disk_free_space()                : return the available space on disk
    o  get_filename_and_extension()         : return (filename_no_extension, extension)
    o  goodbye()                            : display the goodbye message
    o  logfile_opening()                    : open the log file
    o  hashfile64()                         : return the footprint of a file, encoded
                                              with the base 64.
    o  main()                               : main entry point
    o  main__actions()                      : call the different actions required by the arguments
    o  main__actions_tags()                 : call the different actions required by the arguments
    o  main__warmup()                       : initializations
    o  modify_the_tag_of_some_files()       : modify the tag(s) of some files
    o  msg()                                : display a message on console, write the
                                              same message in the log file.
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
    o  normpath()                           : return a human-readable, normalized version of a path
    o  the_file_has_to_be_added()           : return True if a file can be choosed and added to
                                            : the target directory
    o  the_file_has_to_be_added__name()     : a part of the_file_has_to_be_added()
    o  the_file_has_to_be_added__size()     : a part of the_file_has_to_be_added()
    o  welcome()                            : display a welcome message on screen
    o  welcome_in_logfile()                 : display a welcome message in the log file
