# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2016-2018 Olaf Lüke <olaf@tinkerforge.com>

comcu_bootloader.py: COMCU Bootloader plugin implementation

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

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QApplication

from brickv.utils import get_main_window
from brickv import infos

class COMCUBootloader(QWidget):
    def __init__(self, ipcon, info):
        super().__init__()

        self.ipcon = ipcon
        self.info = info

        layout = QVBoxLayout()
        layout.addStretch()
        label = QLabel("This Bricklet is in bootloader mode.")
        layout.addWidget(label)

        button = QPushButton("Flash Bricklet")
        button.pressed.connect(self.button_pressed)
        layout.addWidget(button)
        layout.addStretch()

        hbox = QHBoxLayout(self)
        hbox.addStretch()
        hbox.addLayout(layout)
        hbox.addStretch()

    def button_pressed(self):
        get_main_window().show_bricklet_update(self.info.connected_uid, self.info.position)
