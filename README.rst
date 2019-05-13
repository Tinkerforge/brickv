Brick Viewer
============

This repository contains the source code of Brick Viewer.

Platforms
---------

* Linux
* macOS 10.11 or newer
* Windows 7 or newer

Usage
-----

The following libraries are required:

* python >= 3.5
* pyqt >= 5.5
* pyqt5.qtopengl
* pyserial

On Windows you will also need:

* pypiwin32

On Debian based Linux distributions try::

 sudo apt-get install python3 python3-pyqt5 python3-pyqt5.qtopengl python3-serial

First you have to build the Qt .ui files with the fixed version of ``pyuic5``,
you can do this with ``python3 build_src.py`` in ``src/``. After that you
should be able to start brickv from source with ``python3 main.py`` in the
``src/brickv/`` directory.

Building Packages
-----------------

The Python script ``src/build_pkg.py`` can build a Debian package for
Linux, a ``setup.exe`` for Windows or a disk image for macOS.

To build the Debian package, you need to install setuptools.

To build the Windows installer or macOS disk image, you need a virtual
environment (either virtualenv or pyvenv) with pyinstaller.

Under Windows ensure, that python3 is in the PATH, e.g. by creating
a python3.bat file with the content::

 @echo off
 python.exe %*

To build an installer, NSIS and the Universal CRT (available as a part of the
Windows 10 SDK) is required.

Remember to activate the virtual environment.

To build the package, installer or disk image, run::

 python3 build_pkg.py
