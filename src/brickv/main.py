#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2013-2015 Matthias Bolte <matthias@tinkerforge.com>

main.py: Entry file for Brick Viewer

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sip
sip.setapi('QString', 2)

import os
import sys
import logging

# from http://www.py2exe.org/index.cgi/WhereAmI
if hasattr(sys, "frozen"):
    program_path = os.path.dirname(os.path.realpath(unicode(sys.executable, sys.getfilesystemencoding())))

    if sys.platform == "darwin":
        resources_path = os.path.join(os.path.split(program_path)[0], 'Resources')
    else:
        resources_path = program_path
else:
    program_path = os.path.dirname(os.path.realpath(unicode(__file__, sys.getfilesystemencoding())))
    resources_path = program_path

# add program_path so OpenGL is properly imported
sys.path.insert(0, program_path)

# Allow brickv to be directly started by calling "main.py"
# without "brickv" being in the path already
if not 'brickv' in sys.modules:
    head, tail = os.path.split(program_path)

    if not head in sys.path:
        sys.path.insert(0, head)

    if not hasattr(sys, "frozen"):
        # load and inject in modules list, this allows to have the source in a
        # directory named differently than 'brickv'
        sys.modules['brickv'] = __import__(tail, globals(), locals(), [], -1)

from PyQt4.QtGui import QApplication, QIcon, QFont
from PyQt4.QtCore import QEvent, pyqtSignal

from brickv import config
from brickv.mainwindow import MainWindow
from brickv.async_call import ASYNC_EVENT, async_event_handler

logging.basicConfig(level=config.LOGGING_LEVEL,
                    format=config.LOGGING_FORMAT,
                    datefmt=config.LOGGING_DATEFMT)

class BrickViewer(QApplication):
    object_creator_signal = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.object_creator_signal.connect(self.object_creator_slot)
        self.setWindowIcon(QIcon(os.path.join(resources_path, 'brickv-icon.png')))

    def object_creator_slot(self, object_creator):
        object_creator.create()

    def notify(self, receiver, event):
        if event.type() > QEvent.User and event.type() == ASYNC_EVENT:
            async_event_handler()

        return QApplication.notify(self, receiver, event)

def main():
    argv = sys.argv

    if sys.platform == 'win32':
        argv += ['-style', 'windowsxp']

    if sys.platform == 'darwin':
        # fix OSX 10.9 font
        # http://successfulsoftware.net/2013/10/23/fixing-qt-4-for-mac-os-x-10-9-mavericks/
        # https://bugreports.qt-project.org/browse/QTBUG-32789
        QFont.insertSubstitution('.Lucida Grande UI', 'Lucida Grande')
        # fix OSX 10.10 font
        # https://bugreports.qt-project.org/browse/QTBUG-40833
        QFont.insertSubstitution('.Helvetica Neue DeskInterface', 'Helvetica Neue')

    brick_viewer = BrickViewer(argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(brick_viewer.exec_())

if __name__ == "__main__":
    main()
