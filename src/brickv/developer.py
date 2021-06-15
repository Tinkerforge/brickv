# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2021 Matthias Bolte <matthias@tinkerforge.com>

developer.py: GUI for developer features

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

import gc

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog

from brickv.ui_developer import Ui_Developer
from brickv.utils import get_modeless_dialog_flags

class DeveloperWindow(QDialog, Ui_Developer):
    gc_stats_changed = pyqtSignal(int, int)

    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.ipcon_available = False
        self.gc_runs = 0
        self.gc_collected = 0
        self.gc_uncollectable = 0

        self.gc_stats_changed.connect(self.update_gc_stats)

        self.button_force_gc.clicked.connect(self.force_gc)

        self.button_close.clicked.connect(self.hide)

        gc.callbacks.append(self.gc_callback)

    def force_gc(self):
        gc.collect()

    def gc_callback(self, phase, info):
        try:
            if phase == 'stop':
                self.gc_stats_changed.emit(info['collected'], info['uncollectable'])
        except RuntimeError as e:
            if str(e) != 'wrapped C/C++ object of type DeveloperWindow has been deleted':
                raise

    def update_gc_stats(self, collected, uncollectable):
        self.gc_runs += 1
        objects = len(gc.get_objects())
        self.gc_collected += collected
        self.gc_uncollectable += uncollectable

        self.label_gc_runs.setText(str(self.gc_runs))
        self.label_gc_objects.setText(str(objects))
        self.label_gc_collected.setText(str(self.gc_collected))
        self.label_gc_uncollectable.setText(str(self.gc_uncollectable))

    def update_ui_state(self):
        pass

    def set_ipcon_available(self, ipcon_available):
        self.ipcon_available = ipcon_available

        self.update_ui_state()
