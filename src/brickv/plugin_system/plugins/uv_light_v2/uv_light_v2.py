# -*- coding: utf-8 -*-
"""
UV Light 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

uv_light_v2.py: UV Light 2.0 Bricklet Plugin Implementation

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

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QVBoxLayout

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_uv_light_v2 import BrickletUVLightV2
from brickv.plot_widget import PlotWidget, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class IndexLabel(FixedSizeLabel):
    def setText(self, text):
        super(IndexLabel, self).setText('UV Index: ' + text)

class UVLightV2(COMCUPluginBase):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletUVLightV2, *args)

        self.uv_light = self.device

        self.cbe_get_uv_type_a = CallbackEmulator(self.uv_light.get_uv_type_a,
                                                  self.cb_get_uv_type_a,
                                                  self.increase_error_count)

        self.cbe_get_uv_type_b = CallbackEmulator(self.uv_light.get_uv_type_b,
                                                  self.cb_get_uv_type_b,
                                                  self.increase_error_count)

        self.index_label = IndexLabel('UV Index:')
        self.index_label.setText('0.0')

        self.current_uv_type_a = 0
        self.current_uv_type_b = 0

        self.timer_uv_index = QTimer()
        self.timer_uv_index.timeout.connect(self.timer_uv_index_timeout)
        self.timer_uv_index.setInterval(200)

        plots = [('UV Light Type A', Qt.red, lambda: self.current_uv_type_a, u'{} µW/cm²'.format),
                 ('UV Light Type B', Qt.green, lambda: self.current_uv_type_b, u'{} µW/cm²'.format)]

        self.plot_widget = PlotWidget(u'UV Light [µW/cm²]', plots, extra_key_widgets=[self.index_label])

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.uv_light.get_uv_type_a, None, self.cb_get_uv_type_a, self.increase_error_count)
        self.cbe_get_uv_type_a.set_period(100)
        async_call(self.uv_light.get_uv_type_b, None, self.cb_get_uv_type_b, self.increase_error_count)
        self.cbe_get_uv_type_b.set_period(100)

        self.timer_uv_index.start()

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_get_uv_type_a.set_period(0)
        self.cbe_get_uv_type_b.set_period(0)

        self.timer_uv_index.stop()

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletUVLightV2.DEVICE_IDENTIFIER

    def timer_uv_index_timeout(self):
        index = ((((self.current_uv_type_a * 2) / 9) + ((self.current_uv_type_b * 4) / 8)) * 0.01) / 2

        self.index_label.setText(unicode(index))

        if index < 2.5:
            color = 'green'
        elif index < 5.5:
            color = 'yellow'
        elif index < 7.5:
            color = 'orange'
        elif index < 10.5:
            color = 'red'
        else:
            color = 'magenta'

        self.index_label.setStyleSheet('QLabel {{ color : {0} }}'.format(color))

    def cb_get_uv_type_a(self, uv_type_a):
        self.current_uv_type_a = uv_type_a

    def cb_get_uv_type_b(self, uv_type_b):
        self.current_uv_type_b = uv_type_b
