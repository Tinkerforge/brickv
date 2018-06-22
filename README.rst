Brick Viewer
============

This repository contains the source code of the Brick Viewer.

Usage
-----

The following libraries are required:

* python
* python-qt4
* python-qt4-gl
* python-opengl
* python-serial
* python-setuptools
* pyqt4-dev-tools

On Windows you will also need:

* Python for Windows extensions

On Debian based Linux distributions try::

 sudo apt-get install python python-qt4 python-qt4-gl python-opengl python-serial python-setuptools pyqt4-dev-tools

First you have to build the Qt .ui files (you'll need ``pyuic4`` for that), you
can do this with ``python build_all_ui.py`` in ``src/``. After that you should
be able to start brickv from source with ``python main.py`` in the
``src/brickv/`` directory.

Building Packages
-----------------

The Python script ``src/build_pkg.py`` can build a Debian package for
Linux, a ``setup.exe`` for Windows and a Disk Image for macOS. Run::

 python build_pkg.py
