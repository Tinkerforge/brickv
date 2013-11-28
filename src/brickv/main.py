#!/usr/bin/env python
# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2013 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2009-2013 Olaf Lüke <olaf@tinkerforge.com>

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

import os
import sys
import logging

# from http://www.py2exe.org/index.cgi/WhereAmI
if hasattr(sys, "frozen"):
    program_path = str(os.path.dirname(os.path.realpath(unicode(sys.executable, sys.getfilesystemencoding()))))
else:
    program_path = str(os.path.dirname(os.path.realpath(unicode(__file__, sys.getfilesystemencoding()))))

# add program_path so OpenGL is properly imported
sys.path.insert(0, program_path)

# Allow brickv to be directly started by calling "main.py"
# without "brickv" being in the path already
if not 'brickv' in sys.modules:
    head, tail = os.path.split(program_path)
    if not head in sys.path:
        sys.path.insert(0, head)

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QEvent

from brickv import config
from brickv.mainwindow import MainWindow
from brickv.async_call import ASYNC_EVENT, async_event_handler

logging.basicConfig( 
    level = config.LOGGING_LEVEL, 
    format = config.LOGGING_FORMAT,
    datefmt = config.LOGGING_DATEFMT
) 

class BrickViewer(QApplication):
    def notify(self, receiver, event):
        if event.type() > QEvent.User:
            if event.type() == ASYNC_EVENT:
                async_event_handler()
        return super(BrickViewer, self).notify(receiver, event)

def main():
    brick_viewer = BrickViewer(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(brick_viewer.exec_())

if __name__ == "__main__":
    main()
