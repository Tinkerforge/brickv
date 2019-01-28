# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>

unknown.py: Unknwon Plugin Implementation

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

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout

from brickv.plugin_system.plugin_base import PluginBase

class Unknown(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, None, *args, override_base_name='Unknown')
        
        # All new released Bricklets will have a comcu
        self.has_comcu = True

        info = args[1]

        layout = QVBoxLayout()
        layout.addStretch()
        label = QLabel("""The {6} with

   * Device Identifier: {0}
   * UID: {1}
   * Position: {2}
   * FW Version: {3}.{4}.{5}

is not yet supported.

Please update Brick Viewer!""".format(info.device_identifier,
                                      info.uid,
                                      info.position.upper(),
                                      info.firmware_version_installed[0],
                                      info.firmware_version_installed[1],
                                      info.firmware_version_installed[2],
                                      'Brick' if str(info.device_identifier).startswith('1') else 'Bricklet'))

        #label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(label)
        layout.addStretch()

        hbox = QHBoxLayout(self)
        hbox.addStretch()
        hbox.addLayout(layout)
        hbox.addStretch()

    def start(self):
        pass

    def stop(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return False
