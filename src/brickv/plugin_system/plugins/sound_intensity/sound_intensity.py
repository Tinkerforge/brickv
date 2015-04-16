# -*- coding: utf-8 -*-
"""
Sound Intensity Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QWidget, \
                        QLinearGradient, QPainter, QSizePolicy, QColor

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_sound_intensity import BrickletSoundIntensity
from brickv.async_call import async_call
#from brickv.plot_widget import PlotWidget
from brickv.callback_emulator import CallbackEmulator

class TuningThermo(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.bar_width = 300 # px
        self.bar_height = 10 # px
        self.border = 4 # px
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

class IntensityLabel(QLabel):
    def setText(self, text):
        text = "Intensity Value: " + text
        super(IntensityLabel, self).setText(text)

class SoundIntensity(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletSoundIntensity, *args)

        self.si = self.device

        self.cbe_intensity = CallbackEmulator(self.si.get_intensity,
                                              self.cb_intensity,
                                              self.increase_error_count)

        self.intensity_label = IntensityLabel()
        self.current_value = None
        self.thermo = TuningThermo()

        #plot_list = [['', Qt.red, self.get_current_value]]
        #self.plot_widget = PlotWidget('Intensity Value', plot_list)

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.intensity_label)
        layout_h.addStretch()

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.thermo)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addLayout(layout_h2)
        layout.addStretch()
        #layout.addWidget(QLabel('')) # abuse a label as a fixed-size spacer
        #layout.addWidget(self.plot_widget)

    def get_current_value(self):
        return self.current_value

    def cb_intensity(self, intensity):
        self.thermo.set_value(intensity)
        self.current_value = intensity
        self.intensity_label.setText(str(intensity))

    def start(self):
        async_call(self.si.get_intensity, None, self.cb_intensity, self.increase_error_count)
        self.cbe_intensity.set_period(25)

        #self.plot_widget.stop = False

    def stop(self):
        self.cbe_intensity.set_period(0)

        #self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'sound_intensity'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSoundIntensity.DEVICE_IDENTIFIER
