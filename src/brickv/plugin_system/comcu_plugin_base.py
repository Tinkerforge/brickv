# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>

comcu_plugin_base.py: COMCU plugin base implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

class COMCUPluginBase(PluginBase):
    def __init__(self, device_class, ipcon, device_info, override_base_name=None):
        PluginBase.__init__(self, device_class, ipcon, device_info, override_base_name)

        self.start_called = False
        self.has_comcu = True
        self.cbe_bootloader_mode = CallbackEmulator(self.device.get_bootloader_mode,
                                                    self.cb_bootloader_mode,
                                                    self.increase_error_count)

    def cb_bootloader_mode(self, mode):
        if not self.start_called and mode == self.device.BOOTLOADER_MODE_FIRMWARE and self.isVisible():
            self.start_called = True
            self.start()
        elif mode == self.device.BOOTLOADER_MODE_BOOTLOADER and self.isVisible():
            self.stop()
            self.hide()
            self.widget_bootloader.show()
        elif mode == self.device.BOOTLOADER_MODE_FIRMWARE and not self.isVisible():
            self.widget_bootloader.hide()
            self.show()
            self.start_called = True
            self.start()

    def start_comcu(self):
        self.start_called = False
        async_call(self.device.get_bootloader_mode, None, self.cb_bootloader_mode, self.increase_error_count)
        self.cbe_bootloader_mode.set_period(1000)

    def stop_comcu(self):
        self.cbe_bootloader_mode.set_period(0)
        if self.isVisible():
            self.stop()