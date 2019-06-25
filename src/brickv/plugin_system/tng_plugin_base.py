# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

tng_plugin_base.py: TNG modules plugin base implementation

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

from PyQt5.QtWidgets import QAction

from brickv.plugin_system.plugin_base import PluginBase
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call
from brickv.utils import get_main_window

class TNGPluginBase(PluginBase):
    def __init__(self, device_class, ipcon, device_info, override_base_name=None):
        super().__init__(device_class, ipcon, device_info, override_base_name)

        self.start_called = False
        self.is_tng = True

        self.extra_configs = []

        self.reset_action = QAction('Reset', self)
        self.reset_action.triggered.connect(self.remove_and_reset)

        self.extra_actions = [(0, None, [self.reset_action])]

    def remove_and_reset(self):
        get_main_window().remove_device_tab(self.uid)
        self.device.reset()

    # overrides PluginBase.get_configs
    def get_configs(self):
        return PluginBase.get_configs(self) + self.extra_configs

    # overrides PluginBase.get_actions
    def get_actions(self):
        return PluginBase.get_actions(self) + self.extra_actions

    def start_comcu(self):
        self.start()

    def stop_comcu(self):
        self.stop()
