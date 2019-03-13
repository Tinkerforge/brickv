#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

pyuic5-fixed.py: Workaround pyuic5 problems

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

# The pyuic5 tool drops the contents margins of layout widgets, but some versions
# of pyuic5 have a bug that makes it identify normal widgets as layout widgets
# resulting in broken layouts. The brickv .ui files were created based on PyQt4.
# To avoid having to chase down all the places where the broken pyuic5 erroneously
# drops contents margins of normal widgets just monkey patch pyuic5 to pretend
# that there are no layout widgets at all to get back to the old pyuic4 behavior.

import PyQt5.uic.uiparser as uiparser

class FixedWidgetStack(uiparser.WidgetStack):
    def topIsLayoutWidget(self):
        return False

uiparser.WidgetStack = FixedWidgetStack

import PyQt5.uic.pyuic as pyuic

if __name__ == '__main__':
    pyuic.main()
