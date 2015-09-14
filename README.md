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

        arguments
    
          -h, --help            show this help message and exit
          --add                 select files according to what is described in the
                                configuration file then add them to the target
                                directoryThis option can't be used the --select one.
                                (default: False)
          --configfile CONFIGFILE
                                config file, e.g. config.ini (default: katal.ini)
          --infos               display informations about the source directory given
                                in the configuration file (default: False)
          --select              select files according to what is described in the
                                configuration file without adding them to the target
                                directory. This option can't be used the --add one.
                                (default: False)
          --quiet               no output to the console; no question asked on the
                                console (default: False)
          --version             show the version and exit
        ________________________________________________________________________

        The name Katal comes from the Ancient Greek κατάλογος ("enrolment, 
        register, catalogue").
        ________________________________________________________________________

        history :

        v.0.0.2 (2015_09_14) :
            - added SELECTELEMENT type
            - the call to sys.exit(0) is now at the very end of the file
            - no tests, pylint=10.0, some todos remain.

        v.0.0.1 (2015_09_13) : first try, no tests, pylint=10.0, some todos
                               remain.
        ________________________________________________________________________

        exit codes :

                 0      : success
                -1      : can't read the parameters from the configuration file
                -2      : a ProjectError exception has been raised
                -3      : an unexpected BaseException exception has been raised
                -4      : something happens that halted the program without
                          raising a ProjectError or a BaseException exception.
        ________________________________________________________________________

        SELECT format
                todo
        ________________________________________________________________________

        functions :

        o  action__add()                        : add the source files to the destination
                                                  path.
        o  action__infos()                      : display informations about the source
                                                  and the target directory
        o  action__select()                     : fill SELECT and SELECT_SIZE_IN_BYTES and
                                                  display what's going on.
        o  check_args()                         : check the arguments of the command line.
        o  create_target_name()                 : create the name of a file (a target file)
                                                  from various informations read from a
                                                  source file
        o  fill_select                          : fill SELECT and SELECT_SIZE_IN_BYTES from
                                                  the files stored in SOURCE_PATH.
        o  get_command_line_arguments()         : read the command line arguments
        o  get_parameters_from_cfgfile()        : read the configuration file
        o  get_disk_free_space()                : return the available space on disk
        o  logfile_opening()                    : open the log file
        o  hashfile64()                         : return the footprint of a file, encoded
                                                  with the base 64.
        o  msg()                                : display a message on console, write the
                                                  same message in the log file.
        o  parameters_infos()                   : display some informations about the
                                                  content of the configuration file
        o  read_sieves()                        : initialize SIEVES from the configuration file.
        o  read_target_db()                     : Read the database stored in the target
                                                  directory and initialize TARGET_DB.
        o  remove_illegal_characters()          : replace some illegal characters by the
                                                  underscore character.
        o  show_hashid_of_a_file()              : The function gives the hashid of a file.
        o  size_as_str()                        : return a size in bytes as a human-readable
                                                  string
        o  the_file_has_to_be_added()           : return True if a file can be choosed and added to
                                                : the target directory
        o  the_file_has_to_be_added__name()     : a part of the_file_has_to_be_added()
        o  the_file_has_to_be_added__size()     : a part of the_file_has_to_be_added()
        o  welcome()                            : display a welcome message on screen
        o  welcome_in_logfile()                 : display a welcome message in the log file
