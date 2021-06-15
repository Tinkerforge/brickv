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

from PyQt5.QtWidgets import QDialog

from brickv.ui_developer import Ui_Developer
from brickv.utils import get_modeless_dialog_flags

class DeveloperWindow(QDialog, Ui_Developer):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.ipcon_available = False

        self.button_force_gc.clicked.connect(self.force_gc)

        self.button_close.clicked.connect(self.hide)

    def force_gc(self):
        gc.collect()

        count = gc.get_count()
        stats = gc.get_stats()

        self.label_gc_count0.setText(str(count[0]))
        self.label_gc_count1.setText(str(count[1]))
        self.label_gc_count2.setText(str(count[2]))

        self.label_gc_collections0.setText(str(stats[0]['collections']))
        self.label_gc_collections1.setText(str(stats[1]['collections']))
        self.label_gc_collections2.setText(str(stats[1]['collections']))

        self.label_gc_collected0.setText(str(stats[0]['collected']))
        self.label_gc_collected1.setText(str(stats[1]['collected']))
        self.label_gc_collected2.setText(str(stats[1]['collected']))

        self.label_gc_uncollectable0.setText(str(stats[0]['uncollectable']))
        self.label_gc_uncollectable1.setText(str(stats[1]['uncollectable']))
        self.label_gc_uncollectable2.setText(str(stats[1]['uncollectable']))

    def update_ui_state(self):
        pass

    def set_ipcon_available(self, ipcon_available):
        self.ipcon_available = ipcon_available

        self.update_ui_state()
