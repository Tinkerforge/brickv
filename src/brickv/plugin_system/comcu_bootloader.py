# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QApplication

from brickv.utils import get_main_window

class COMCUBootloader(QWidget):
    def __init__(self, ipcon, info):
        super(COMCUBootloader, self).__init__()

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
        main_window = get_main_window()
        main_window.flashing_clicked()
        QApplication.processEvents()
        main_window.flashing_window.tab_widget.setCurrentPage(2)
        QApplication.processEvents()
        combo_brick = main_window.flashing_window.combo_brick
        combo_port  = main_window.flashing_window.combo_port

        for i in range(combo_brick.count()):
            if '[' + self.info.connected_uid + ']' in combo_brick.itemText(i):
                combo_brick.setCurrentIndex(i)
                QApplication.processEvents()
                break

        try:
            port_index = ord(self.info.position) - ord('a')
        except:
            port_index = 0

        combo_port.setCurrentIndex(port_index)
        QApplication.processEvents()
