Brick Viewer
============

This repository contains the source code of the Brick Viewer.

Usage
-----

First you have to build the Qt .ui files, you can do this with
``python build_all_ui.py`` in ``src/brickv/`` (note: you need ``pyuic4`` for that).
After that you should be able to start brickv from source with
``python main.py`` in the ``src/brickv/`` directory.

The following libraries are required:

* python-qt4
* python-qt4-gl
* python-qwt5-qt4
* python-opengl
* python-serial

On Debian based Linux distributions try::

 sudo apt-get install python python-qt4 python-qt4-gl python-qwt5-qt4 python-opengl python-serial

Building Packages
-----------------

The Python script ``src/brickv/build_pkg.py`` can build a Debian package for
Linux, a ``setup.exe`` for Windows and a Disk Image for Mac OS X. Try::

 python build_pkg.py linux

or::

 python build_pkg.py windows

or::

 python build_pkg.py macosx
