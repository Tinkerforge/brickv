# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>

helper.py:  helper class with tools

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


# from http://www.py2exe.org/index.cgi/WhereAmI to replace

import os
import sys

class ProgramPath:
    @staticmethod
    def we_are_frozen():
        return hasattr(sys, "frozen")

    @staticmethod
    def program_path():
        if ProgramPath.we_are_frozen():
            return str(os.path.dirname(unicode(sys.executable, 
                                               sys.getfilesystemencoding())))

        return str(os.path.dirname(unicode(__file__, 
                                   sys.getfilesystemencoding())))
