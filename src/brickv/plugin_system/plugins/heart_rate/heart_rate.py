# -*- coding: utf-8 -*-
"""
Heart Rate Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

heart_rate.py: Heart Rate Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_heart_rate import BrickletHeartRate
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.load_pixmap import load_masked_pixmap

class HeartRate(PluginBase):
    qtcb_beat_state_changed = pyqtSignal(int)

    def __init__(self, *args):
        super().__init__(BrickletHeartRate, *args)

        self.hr = self.device

        self.cbe_heart_rate = CallbackEmulator(self.hr.get_heart_rate,
                                               None,
                                               self.cb_heart_rate,
                                               self.increase_error_count)

        # FIXME: add beat state getter to Heart Rate Bricklet API
        self.qtcb_beat_state_changed.connect(self.cb_beat_state_changed)
        self.hr.register_callback(self.hr.CALLBACK_BEAT_STATE_CHANGED,
                                  self.qtcb_beat_state_changed.emit)

        self.heart_white_bitmap = load_masked_pixmap('plugin_system/plugins/heart_rate/heart_white_small.bmp')
        self.heart_red_bitmap = load_masked_pixmap('plugin_system/plugins/heart_rate/heart_red_small.bmp')
        self.heart_icon = QLabel()
        self.heart_icon.setPixmap(self.heart_white_bitmap)

        self.current_heart_rate = CurveValueWrapper()

        plots = [('Heart Rate', Qt.red, self.current_heart_rate, '{} BPM'.format)]
        self.plot_widget = PlotWidget('Heart Rate [BPM]', plots, extra_key_widgets=[self.heart_icon], y_resolution=1.0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.hr.enable_beat_state_changed_callback, None, None, self.increase_error_count)

        self.cbe_heart_rate.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_heart_rate.set_period(0)
        async_call(self.hr.disable_beat_state_changed_callback, None, None, self.increase_error_count)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHeartRate.DEVICE_IDENTIFIER

    def cb_heart_rate(self, heart_rate):
        self.current_heart_rate.value = heart_rate

    def cb_beat_state_changed(self, state):
        if state == self.hr.BEAT_STATE_RISING:
            self.heart_icon.setPixmap(self.heart_red_bitmap)
        else:
            self.heart_icon.setPixmap(self.heart_white_bitmap)
