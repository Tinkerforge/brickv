# -*- coding: utf-8 -*-
"""
Sound Pressure Level Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

sound_pressure_level.py: Sound Pressure Level Plugin Implementation

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

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QVBoxLayout, QWidget, QLinearGradient, \
                        QPainter, QSizePolicy, QColor
                        
from PyQt4.QtGui import QSpinBox, QSlider, QWidget, QImage, QPainter, QPen, QAction
from PyQt4.QtCore import pyqtSignal, Qt, QPoint, QSize

from brickv.bindings.bricklet_sound_pressure_level import BrickletSoundPressureLevel
from brickv.plugin_system.plugins.sound_pressure_level.ui_sound_pressure_level import Ui_SoundPressureLevel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plot_widget import PlotWidget

import math

class TuningThermo(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.bar_width = 200 # px
        self.bar_height = 10 # px
        self.border = 3 # px
        self.value = 0
        self.max_value = 1000
        self.min_value = 300

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
        value = value - self.min_value
        self.value = min(max(value, 0), self.max_value-self.min_value)

        self.update()

class SoundPressureLevel(COMCUPluginBase, Ui_SoundPressureLevel):
    qtcb_spectrum = pyqtSignal(object)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletSoundPressureLevel, *args)

        self.setupUi(self)

        self.sound_pressure_level = self.device
        self.cbe_get_decibel = CallbackEmulator(self.sound_pressure_level.get_decibel,
                                                self.cb_get_decibel,
                                                self.increase_error_count)
        
        self.qtcb_spectrum.connect(self.cb_spectrum)
        
        self.thermo = TuningThermo()
        
        plots_spectrum = [(u'Spectrum', Qt.red, None, u'{} °C'.format)]
        self.plot_widget_spectrum = PlotWidget(u'Value [dB]', plots_spectrum, clear_button=None, x_diff=20480, x_scale_title_text='Frequency [Hz]', x_scale_skip_last_tick=False, key=None)
        self.plot_widget_spectrum.set_x_scale(512*40/5, 1)
        
        self.combo_fft_size.currentIndexChanged.connect(self.config_changed)
        self.combo_weighting.currentIndexChanged.connect(self.config_changed)
        
        self.layout_graph.addWidget(self.plot_widget_spectrum)
        self.layout_decibel.insertWidget(3, self.thermo)
        
        self.last_spectrum_length = 512
        
    def config_changed(self, _):
        self.sound_pressure_level.set_configuration(self.combo_fft_size.currentIndex(), self.combo_weighting.currentIndex())

    def cb_get_decibel(self, db):
        self.label_decibel.setText("{:.1f}".format(db/10.0))
        self.thermo.set_value(db)
        
    def cb_spectrum(self, spectrum):
        length = len(spectrum)
        num    = 20480/length
        
        x_data = list(range(0, num*length, num))
        y_data = list(map(lambda x: 20*math.log10(max(1, x/math.sqrt(2))), spectrum))
        
        self.plot_widget_spectrum.set_data(0, x_data, y_data)

    def get_configuration_async(self, config):
        self.combo_fft_size.blockSignals(True)
        self.combo_fft_size.setCurrentIndex(config.fft_size)
        self.combo_fft_size.blockSignals(False)
        
        self.combo_weighting.blockSignals(True)
        self.combo_weighting.setCurrentIndex(config.weighting)
        self.combo_weighting.blockSignals(False)

    def start(self):
        async_call(self.sound_pressure_level.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        self.cbe_get_decibel.set_period(50)
        
        self.sound_pressure_level.set_spectrum_callback_configuration(1)
        self.sound_pressure_level.register_callback(self.sound_pressure_level.CALLBACK_SPECTRUM, self.qtcb_spectrum.emit)

    def stop(self):
        self.cbe_get_decibel.set_period(0)
        self.sound_pressure_level.set_spectrum_callback_configuration(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSoundPressureLevel.DEVICE_IDENTIFIER
