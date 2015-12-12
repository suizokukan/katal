#(1) Katal
A (Python3/GPLv3/OSX-Linux-Windows/CLI) project, using no additional modules than the ones installed with Python3.

Create a catalogue from various source directories, without any duplicate. Add some tags to the files.

#(2) purpose
Read a directory, select some files according to a configuration file (leaving aside the duplicates), copy the selected files in a target directory.
Once the target directory is filled with some files, a database is added to the directory to avoid future duplicates. You can add new files to the target directory by using Katal one more time, with a different source directory.

#(3) installation and tests

    Don't forget : Katal is Python3 project, not a Python2 project !

    $ pip3 install katal

    or

    $ wget https://raw.githubusercontent.com/suizokukan/katal/master/katal/katal.py
    Since katal.py is a stand-alone file, you may place this file in the target directory.

    tests :
    
    $ python -m unittest tests/tests.py

    or
    
    $ nosetests
    
#(4) workflow
    
    $ katal -h
    ... will display all known parameters.
    $ katal --version
    ... wil display the version of the current script.
    
    note : using the --off option allows the user to use Katal without modifying the target 
    directory; with --off, no file will be written and the database will not change.

    note : Katal NEVER simply deletes a file : the script move ALWAYS the file to be deleted in its
    trash directory.

####Create the target directory :
    $ katal --new myworkingdirectory
    
    It may be convenient to go inside the target directory, e.g. :
    $ cd myworkingdirectory
    
    If katal wasn't installed on the computer (pip3 install katal), it may be convenient to copy the 
    script katal.py inside the target directory, e.g. :
    $ cp katal.py myworkingdirectory
    
####Then, modify the .ini file (myworkingdirectory/.katal/katal.ini) and choose a source :

    Inside the .ini file, modify the following line :
    
    [source]
    path : ~/src/
    
####Take a look at the files stored in the source directory :
    $ katal --infos
    Some informations are displayed : how many files lie in the source directory, what are
    the extensions, and so on.
    
####Choose which files have to be selected; modify the .ini file :
    
    (example 1 : all .jpg (any size) and all .bmp greater then 5MB.)

    eval : filter1 or filter2

    [source.filter1]
    iname : .*\.jpg$
    
    [source.filter2]
    iname : .*\.bmp$
    size : >= 5MB
    
    (example 2 : all jpg,tif,bmp,png greater then 1MB.)
    eval : filter1 and (filter2 or filter3 or filter4 or filter5)
    [source.filter1]
    size : >1MB
    [source.filter2]
    iname : .*\.jpg$
    [source.filter3]
    iname : .*\.tif$
    [source.filter4]
    iname : .*\.bmp$
    [source.filter5]
    iname : .*\.png$
    
    Choose a name for the files in the target directory, e.g. :
    name of the target files : birthday__%%dd__%%i.%%e
    (%%dd : date (e.g. 2015_09_25_06_50)
    (%%i : database index, like "0", "1", "2"...)
    (%%e : extension, like "jpg")

####Check if everything's is alright :
    $ katal --infos
    
####Let's see what would happen if the script select the files :
    $ katal --select  ... and answer 'yes' to the final question if all the details are ok to you.    
    The files will be copied in the target directory.
    
    If you want to move the files from source directory to target directory, use the --move option.
    If you want a bit-to-bit check if two files have the same hashes, use the --strictcmp option.
    
####See the result (ti : target informations)
    $ katal -ti
    
    If want to start from scratch just keeping the configuration file, you may delete all target 
    files and flush the database with :
    $ katal --reset
    ...and modify the configuration file and use again --select
    
####Let's tag some files :
    $ katal --addtag=tree --to=*.jpg
    $ katal --addtag=birthday --to=myfile.bmp
    
####Let's search some tags :
    $ katal --findtag=tree
    
####Let's search some files and copy the selected files in new directory :
    $ katal --findtag=birthday --copyto=backup_birthday
    
####Let's remove all the files without any tag :
    $ katal --rmnotags
    ... the files will be copied in the trash directory (myworkingdirectory/.katal/trash)
    
####Let's remove a file :
    $ katal --targetkill=myfile.jpg

####Let's remove some files :
    $ katal --targetkill=file*.jpg
    
####Let's copy a target directory into another one, which didn't exist :
    $ katal --new=../target2
    
    modify the configuration file in target2 : e.g. you may change the name of the files.
    
    Then :
    $ katal --rebase=../target2

####Check if a file external to the target directory is already stored in it ?
    $ katal --whatabout=myfile

#(5) author
suizokukan (suizokukan AT orange DOT fr)

94.23.197.37

#(6) name
The name Katal is derived from the Ancient Greek κατάλογος ("enrolment, register, catalogue").

#(7) arguments

    usage: katal.py [-h] [--add] [--addtag ADDTAG] [-cfg CONFIGFILE] [--cleandbrm]
                    [--copyto COPYTO] [-ddcfg] [--findtag FINDTAG] [--infos] [-m]
                    [--move] [-n NEW] [--off] [--rebase REBASE] [--reset]
                    [--rmnotags] [--rmtags] [-s] [--settagsstr SETTAGSSTR]
                    [--strictcmp] [--targetpath TARGETPATH] [-ti] [-tk TARGETKILL]
                    [--to TO] [--usentfsprefix] [--version]
                    [--whatabout WHATABOUT]

    optional arguments:

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
                            set the name of the config file, e.g. config.ini
                            (default: None)
      --cleandbrm           Remove from the database the missing files in the
                            target path. (default: False)
      --copyto COPYTO       To be used with the --findtag parameter. Copy the
                            found files into an export directory. (default: None)
      -ddcfg, --downloaddefaultcfg
                            Download the default config file and overwrite the
                            file having the same name. This is done before the
                            script reads the parameters in the config file
                            (default: False)
      --findtag FINDTAG     find the files in the target directory with the given
                            tag. The tag is a simple string, not a regex.
                            (default: None)
      --infos               display informations about the source directory given
                            in the configuration file. Help the --select/--add
                            options to display more informations about the process
                            : in this case, the --infos will be executed before
                            --select/--add (default: False)
      -m, --mute            no output to the console; no question asked on the
                            console (default: False)
      --move                to be used with --select and --add : move the files,
                            don't copy them (default: False)
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
      --reset               Delete the database and the files in the target
                            directory (default: False)
      --rmnotags            remove all files without a tag (default: False)
      --rmtags              remove all the tags of some file(s) in combination
                            with the --to option. (default: False)
      -s, --select          select files according to what is described in the
                            configuration file without adding them to the target
                            directory. This option can't be used with the --add
                            one.If you want more informations about the process,
                            please use this option in combination with --infos .
                            (default: False)
      --settagsstr SETTAGSSTR
                            give the tag to some file(s) in combination with the
                            --to option. Overwrite the ancient tag string. If you
                            want to empty the tags' string, please use a space,
                            not an empty string : otherwise the parameter given to
                            the script wouldn't be taken in account by the shell
                            (default: None)
      --strictcmp           to be used with --add or --select. Force a bit-to-bit
                            comparisionbetween files whose hashid-s is equal.
                            (default: False)
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
                            --settagsstr. wildcards accepted; e.g. to select all
                            .py files, use '*.py' . Please DON'T ADD the path to
                            the target directory, only the filenames (default:
                            None)
      --usentfsprefix       Force the script to prefix filenames by a special
                            string required by the NTFS for long filenames, namely
                            \\?\ (default: False)
      --version             show the version and exit
      --whatabout WHATABOUT
                            Say if the file given as a parameter is in the target
                            directory notwithstanding its name. (default: None)

#(8) history

    v 0.2.2 (2015_12_07) : improved documentation and messages

        o improved message in main_warmup()
          If the options -ddcfg/--downloaddefaultcfg are used, don't display
          the advice to use them.
        o improved message in action__downloadefaultcfg()
        o improved the documentation in README.md

        o updated pylintrc, along with pylint 1.5.0 modifications
        o pylinted and fixed setup.py

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v 0.2.1 (2015_11_08)

        o added option --usentfsprefix
          A special prefix is required by the NTFS for long filenames. The --usentfsprefix
          argument allow/disallow to use such a prefix.

        o improved warning messages in show_infos_about_source_path() and in
          show_infos_about_target_path().
        o improved the documentation in README.md

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.2.0 (2015_11_04)

        o fixed an important bug : hashfile64() can't compute the hash with
          the filename, the size or the date !

        o improved the messages in fill_select()

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.9 (2015_11_04)

        o fixed an important bug : filenames whose length is greater than 260
          characters are correctly taken in account.

        o improved the documentation

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.8 (2015_11_01)

        o added the possibility to create tags automatically during a --select/--add .

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.7 (2015_11_01)

        o added --copyto parameter

        o filled the faked/src directory
        o updated create_faked_target.sh in order to test the --copyto parameter

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.6 (2015_11_01)

        o improved the string returned by size_as_str() : no more 'Go' (>'GB'), ...

        o removed the _import_msg argument from msg()
        o removed the 'verbosity' keyword from the cfg files and from the script
        o improved a message in fill_select()

        o 6 tests, pylint=10.0 for the three Python scripts
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.5 (2015_10_30)

        o fixed a bug in create_target_name() : the order of the if's mattered.

        o set __statuspypi__ to 'Development Status :: 5 - Production/Stable'
        o functions are now all described in README.md, in alphabetical order
        o improved messages and documentation

        o 6 tests, pylint=10.0
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

    v.0.1.4 (2015_10_30)

        o ancient keywords like SOURCENAME_WITHOUT_EXTENSION have been renamed :
            HASHID -> %%h
            SOURCENAME_WITHOUT_EXTENSION -> %%f
            SOURCENAME_WITHOUT_EXTENSION2 -> %%ff
            SOURCE_PATH -> %%p
            SOURCE_PATH2 -> %%pp
            SOURCE_EXTENSION -> %%e
            SOURCE_EXTENSION2 -> %%ee
            SIZE -> %%s
            DATE2 -> %%dd
            DATABASE_INDEX -> %%i
            INTTIMESTAMP -> %%t
            HEXTIMESTAMP -> %%ht
        o in filter, 'size' may have a suffix like 'kB', 'MB', ..., 'KiB', 'MiB' .
        o added 'ci_name' to filters (=case insensitive regex)
        o in configuration file, 'sieve' is now called 'filter'
        o new option : --reset (delete database and target files, not the configuration file)
        o new option : --strictcmp option (bit to bit comparision if two hashes are identical)
        o new option : --move (move the files if --select or --add instead of copy them)
        o new option : --findtag

        o added a pylintrc file
        o fixed main_warmup() : sys.exit(-1) is raised if no configuration file
        o removed the --hashid option
        o added constant PARTIALHASHID_BYTESNBR = 1000000
        o 'ProjectError' > 'KatalError'
        o added the thefilehastobeadded__db() function
        o added 'partialhashid' and 'size' to the database
        o hashfile64() now accepts a _stop_after argument, allowing to read only
          the _stop_after first bytes of the file
        o the function hashfile64() uses from now the file content, its name,
          its size and its timestamp
        o improved messages and documentation

        o 6 tests, pylint=10.0
        o version packaged and sent to Pypi (https://pypi.python.org/pypi/Katal)

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
                -2      : a KatalError exception has been raised
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

    [source.filterN]   : N is an integer greater or equal to  1; [source.filter1], [source.filter2], ...
    name/iname         : a regex; e.g. for all files with an .jpg extension : .*\.jpg$
                         (iname : case insensitive)
    size              : a symbol plus an integer
                        e.g., either >999, either <999, either =999, either <=999 either >=999

                        use the following suffixes :

                           "kB" : 1000
                           "KB" : 1000
                           "MB" : 1000**2
                           "GB" : 1000**3
                           "TB" : 1000**4
                           "PB" : 1000**5
                           "EB" : 1000**6
                           "ZB" : 1000**7
                           "YB" : 1000**8
                           "KiB": 1024
                           "MiB": 1024**2
                           "GiB": 1024**3
                           "TiB": 1024**4
                           "PiB": 1024**5
                           "EiB": 1024**6
                           "ZiB": 1024**7
                           "YiB": 1024**8

    [target]                  : parameters about target directory 
    path                      : a string without any quotation mark.

    name of the target files  : a string using keywords which will be replaced by their value
                                see the create_target_name() function.

                known keywords :

                %%h  : hashid (e.g. GwM5NKzoZ76oPAbWwX7od0pI66xZrOHI7TWIggx+xFk=)

                %%f  : source name (with the path), without the extension

                %%ff : source name (with the path), without the extension
                       [see below, no forbidden characters]

                %%p  : source path

                %%pp : source path
                       [see below, no forbidden characters]

                %%e  : source extension, without the dot character (e.g. jpg / no dot character !)

                %%ee : source extension, without the dot character (e.g. jpg / no dot character !)
                       [see below, no forbidden characters]

                %%s  : size (e.g. 123)

                %%dd : date (e.g. 2015_09_25_06_50)
                       [see below, no forbidden characters]

                %%i  : database index (e.g. 123)

                %%t  : timestamp of the file (integer, e.g. 1445584562)

                %%ht : timestamp of the file (hexadecimal, e.g. 5629DED0)

                n.b. : keywords with a reduplicated letter (%%pp, %%ff, ...) are builded against
                       a set of illegal characters, replaced by "_". 

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

    FILTERS is a dictionary with a (int)filter_index as a key and a dict as values.
    This dict may be empty or contain the following keys/values : 
      FILTERS["name"] = re.compile(...)
      FILTERS["size"] = a string like ">999", initial symbol in ('=', '<', '>', '<=', '>=')
      FILTERS["date"] = a string like '>2015-09-17 20:01', initial symbol in ('=', '<', '>', '<=', '>=')
    FILTERS is filled by read_filters().

##(9.5) database
In every target directory a database is created and filled. Its name is set by the
global variable DATABASE_NAME.
TARGET_DB is initialized by read_target_db(); hashid:(partialhashid, size, fullname)
    
    o hashid varchar(44) PRIMARY KEY UNIQUE : hashid (of all the file)
    o partialhashid varchar(44)             : hashid (of the beginning of the file)
    o size integer                          : size
    o name text UNIQUE                      : (target) name
    o sourcename text                       : complete path + name + extension
    o sourcedate integer                    : epoch time
    o tagsstr text                          : a list of tags separated by the TAG_SEPARATOR
                                              symbol.

##(9.6) trash directory
the deleted files are placed in a trashed directory placed inside the target directory. The
trash name is defined in the configuration file.


##(9.7) the database

        hashid (primary key): varchar(44)
        name                : text
        sourcename          : text
        tagsstr             : text

##(9.8) the functions

    o  action__add()                        : add the source files to the target
                                              path.
    o  action__addtag()                     : add one tag to the tags' string of the given files
    o  action__cleandbrm()                  : remove from the database the missing files
    o  action__downloadefaultcfg()          : download the default configuration file
    o  action__findtag()                    : display the files tagged with the _tag parameter
                                              which is a simple string, not a regex.
    o  action__infos()                      : display informations about the source
                                              and the target directory
    o  action__new()                        : create a new target directory
    o  action__rebase()                     : copy a target directory into a new one
    o  action__rebase__files()              : --rebase : select the files to be copied.
    o  action__rebase__write()              : --rebase : write the files into the new target direc.
    o  action__reset()                      : --reset : remove the database and the files in the
                                              target directory
    o  action__rmnotags()                   : Remove all files if they have no tags.
    o  action__rmtags()                     : remove the entire tags' string of some files
    o  action__select()                     : fill SELECT and SELECT_SIZE_IN_BYTES and
                                              display what's going on.
    o  action__settagsstr()                 : Modify the tags string in the target directory,
                                              overwriting ancient tags.
    o  action__target_kill()                : delete a filename from the target directory
                                              and from the database
    o  action__whatabout()                  : is a file already in the target directory ?
    o  add_keywords_in_targetstr()          : replace some keywords by the value given as parameters
                                              in order to make strings used to create the target files
    o  check_args()                         : check the arguments of the command line.
    o  create_empty_db()                    : create an empty database.
    o  create_subdirs_in_target_path()      : create the expected subdirectories in TARGET_PATH .
    o  create_target_name()                 : create the name of a file (a target file)
                                              from various information (filename, ...)
    o  create_target_name_and_tags()        : create the name and the tags of a file (a target file)
                                              from various information (filename, ...)
    o  create_target_tags()                 : create the tags of a file (a target file)
                                              from various information (filename, ...)
    o  eval_filter_for_a_file()             : evaluate a file according to a filter
    o  fill_select()                        : fill SELECT and SELECT_SIZE_IN_BYTES from
                                              the files stored in SOURCE_PATH.
    o  fill_select__checks()                : final checks at the end of fill_select()
    o  get_disk_free_space()                : return the available space on disk
    o  get_filename_and_extension()         : return (filename_no_extension, extension)
    o  goodbye()                            : display the goodbye message
    o  hashfile64()                         : return the footprint of a file, encoded
                                              with the base 64.
    o  logfile_opening()                    : open the log file
    o  main()                               : main entry point
    o  main__actions()                      : call the different actions required by the arguments
    o  main__actions_tags()                 : call the different actions required by the arguments
    o  main__warmup()                       : initializations
    o  modify_the_tag_of_some_files()       : modify the tag(s) of some files
    o  msg()                                : display a message on console, write the
                                              same message in the log file.

    o  normpath()                           : return a human-readable, normalized version of a path
    o  possible_paths_to_cfg()              : return a list of the (str)paths to the config file
    o  read_command_line_arguments()        : read the command line arguments
    o  read_parameters_from_cfgfile()       : read the configuration file
    o  read_filters()                       : initialize FILTERS from the configuration file
    o  read_target_db()                     : read the database stored in the target
                                              directory and initialize TARGET_DB.
    o  remove_illegal_characters()          : replace some illegal characters by the
                                              underscore character.
    o  shortstr()                           : shorten a string
    o  show_infos_about_source_path()       : display informations about source path
    o  show_infos_about_target_path()       : display informations about target path
    o  size_as_str()                        : return a size in bytes as a human-readable
                                              string
    o  tagsstr_repr()                       : return an improved representation of a tags string
    o  is_ntfs_prefix_mandatory()           : return True if the _path is a path in a systemfile
                                              requiring the NTFS prefix for long filenames.
    o  thefilehastobeadded__db()            : return True if the file isn't already known in the
                                              database
    o  thefilehastobeadded__filters()       : return True if a file can be choosed and added to
                                            : the target directory
    o  thefilehastobeadded__filt_date()     : a part of thefilehastobeadded__filters()
    o  thefilehastobeadded__filt_name()     : a part of thefilehastobeadded__filters()
    o  thefilehastobeadded__filt_size()     : a part of thefilehastobeadded__filters()
    o  welcome()                            : display a welcome message on screen
    o  welcome_in_logfile()                 : display a welcome message in the log file
