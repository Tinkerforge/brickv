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

* Python >= 3.5
* PyQt >= 5.5 with QtOpenGL
* pySerial
* pytz
* tzlocal

On Windows you will also need:

* pypiwin32

On Debian based Linux distributions try::

 sudo apt-get install python3 python3-pyqt5 python3-pyqt5.qtopengl python3-serial python3-tz python3-tzlocal

On other systems you can install the requirements with pip::

 pip install -r src/requirements.txt

If you use pip, a virtual environment is recommended, but not necessary.

First you have to build the Qt .ui files with the fixed version of ``pyuic5``,
you can do this with ``python3 build_src.py`` in ``src/``. After that you
should be able to start brickv from source with ``python3 main.py`` in the
``src/brickv/`` directory.

Building Packages
-----------------

The Python script ``src/build_pkg.py`` can build a Debian package for
Linux, a ``setup.exe`` for Windows or a disk image for macOS.

To build an installer (Windows) or disk image (macOS),
a virtual environment is required.

Linux
~~~~~

To build the Debian package, you need to install setuptools.
To build the package run ``python3 build_pkg.py``
or continue with "Building inside a virtual environment".

macOS
~~~~~

Building the macOS disk image requires python3 installed with homebrew.
Then continue with "Building inside a virtual environment".

Windows
~~~~~~~

Under Windows ensure, that python3 is in the PATH, e.g. by creating
a python3.bat file with the content::

 @echo off
 python.exe %*

To build an installer, NSIS and the Universal CRT (available as a part of the
Windows 10 SDK) is required.
Then continue with "Building inside a virtual environment".

Building inside a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The virtual environment is created with::

 python3 -m venv brickv-venv

and activated with ``source brickv-venv/bin/activate`` under Linux or macOS,
or under Windows with either ``brickv-venv/Scripts/activate.bat``
or ``brickv-venv/Scripts/activate.ps1``
if you use cmd.exe or PowerShell.

The required packages can then be installed with::

 pip install -r src/requirements.txt

Then run ``python3 src/build_pkg.py --no-sign`` to build
the package, disk image or installer.
