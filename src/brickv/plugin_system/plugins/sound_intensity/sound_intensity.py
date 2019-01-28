# -*- coding: utf-8 -*-
"""
Sound Intensity Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

sound_intensity.py: Sound Intensity Plugin Implementation

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QLinearGradient, QColor

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_sound_intensity import BrickletSoundIntensity
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget
from brickv.callback_emulator import CallbackEmulator

class TuningThermo(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.bar_width = 200 # px
        self.bar_height = 10 # px
        self.border = 3 # px
        self.value = 0
        self.max_value = 3200

        self.setFixedWidth(self.border + self.bar_width + self.border)
        self.setFixedHeight(self.border + self.bar_height + self.border)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.gradient = QLinearGradient(0, 0, self.bar_width, 0)
        self.gradient.setColorAt(0, Qt.green)
        self.gradient.setColorAt(1, Qt.red)

    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()

        painter.fillRect(0, 0, width, height, QColor(245, 245, 245))

        painter.setPen(QColor(190, 190, 190))
        painter.drawRect(0, 0, width - 1, height - 1)

        filled_bar_width = round(float(width - self.border * 2 - 1) * self.value / self.max_value + 1)

        painter.fillRect(self.border, self.border, filled_bar_width, height - self.border * 2, self.gradient)

    def set_value(self, value):
        self.value = min(max(value, 0), self.max_value)

        self.update()

class SoundIntensity(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletSoundIntensity, *args)

        self.si = self.device

        self.cbe_intensity = CallbackEmulator(self.si.get_intensity,
                                              self.cb_intensity,
                                              self.increase_error_count)

        self.current_intensity = None
        self.thermo = TuningThermo()

        plots = [('Intensity Value', Qt.red, lambda: self.current_intensity, str)]
        self.plot_widget = PlotWidget('Intensity Value', plots, curve_motion_granularity=40,
                                      update_interval=0.025, extra_key_widgets=[self.thermo])

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def cb_intensity(self, intensity):
        self.thermo.set_value(intensity)
        self.current_intensity = intensity

    def start(self):
        async_call(self.si.get_intensity, None, self.cb_intensity, self.increase_error_count)
        self.cbe_intensity.set_period(25)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_intensity.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSoundIntensity.DEVICE_IDENTIFIER
