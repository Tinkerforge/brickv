#!/usr/bin/env python
# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2009-2010 Olaf Lüke <olaf@tinkerforge.com>

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

import sys
from program_path import ProgramPath

# Append path to sys.path (such that plugins can import ip_connection)
__path = ProgramPath.program_path()
if not __path in sys.path:
    sys.path.insert(0, __path)

import logging
import config

#import PyQt4
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QEvent

from mainwindow import MainWindow
from async_call import ASYNC_EVENT, async_event_handler

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

if __name__ == "__main__":
    brickv = BrickViewer(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(brickv.exec_())
