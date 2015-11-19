=======================================
Katal : let's create a files' catalogue
=======================================
Katal by suizokukan (suizokukan AT orange DOT fr)

A (Python3/GPLv3/OSX-Linux-Windows/CLI) project, using no additional modules than the ones installed with Python3.

Note : this Python3 project can't be used with python2.

project's purpose
=================

Read a directory, select some files according to a configuration file (leaving aside the duplicates), copy the selected files in a target directory.
Once the target directory is filled with some files, a database is added to the directory to avoid future duplicates. You can add new files to the target directory by using Katal one more time, with a different source directory.

The name Katal comes from the Ancient Greek κατάλογος ("enrolment, register, catalogue").

installation
============
$pip3 install katal

Since katal.py is a stand-alone file, you can download katal.py in the target directory and use it directly :
$wget https://raw.githubusercontent.com/suizokukan/katal/master/katal.py

name
====
The name Katal is derived from the Ancient Greek word κατάλογος ("enrolment, register, catalogue").

more
====
see README.md file ("workflow" section)
see https://github.com/suizokukan/katal
