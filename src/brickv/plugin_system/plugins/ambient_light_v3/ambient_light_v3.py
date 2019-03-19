# -*- coding: utf-8 -*-
"""
Ambient Light 3.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

ambient_light_v3.py: Ambient Light 3.0 Bricklet Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox
from PyQt5.QtGui import QPainter, QColor, QBrush

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_ambient_light_v3 import BrickletAmbientLightV3
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class AmbientLightFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = QColor(128, 128, 128)
        self.setMinimumSize(25, 25)
        self.setMaximumSize(25, 25)

    def set_color(self, r, g, b):
        self.color = QColor(r, g, b)
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setBrush(QBrush(self.color))
        qp.setPen(self.color)
        qp.drawRect(0, 0, 25, 25)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.black)
        qp.drawRect(1, 1, 24, 24)

class AmbientLightV3(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletAmbientLightV3, *args)

        self.al = self.device

        self.cbe_illuminance = CallbackEmulator(self.al.get_illuminance,
                                                self.cb_illuminance,
                                                self.increase_error_count)

        self.alf = AmbientLightFrame()
        self.out_of_range_label = QLabel('Illuminance is out-of-range')
        self.saturated_label = QLabel('Sensor is saturated')

        self.out_of_range_label.hide()
        self.out_of_range_label.setStyleSheet('QLabel { color: red }')
        self.saturated_label.hide()
        self.saturated_label.setStyleSheet('QLabel { color: magenta }')

        self.current_illuminance = None # float, lx

        plots = [('Illuminance', Qt.red, lambda: self.current_illuminance, '{:.2f} lx (Lux)'.format)]
        self.plot_widget = PlotWidget('Illuminance [lx]', plots, extra_key_widgets=[self.out_of_range_label, self.saturated_label, self.alf])

        self.range_label = QLabel('Illuminance Range:')
        self.range_combo = QComboBox()

        self.range_combo.addItem("Unlimited", BrickletAmbientLightV3.ILLUMINANCE_RANGE_UNLIMITED)
        self.range_combo.addItem("0 - 64000 lx", BrickletAmbientLightV3.ILLUMINANCE_RANGE_64000LUX)
        self.range_combo.addItem("0 - 32000 lx", BrickletAmbientLightV3.ILLUMINANCE_RANGE_32000LUX)
        self.range_combo.addItem("0 - 16000 lx", BrickletAmbientLightV3.ILLUMINANCE_RANGE_16000LUX)
        self.range_combo.addItem("0 - 8000 lx", BrickletAmbientLightV3.ILLUMINANCE_RANGE_8000LUX)
        self.range_combo.addItem("0 - 1300 lx", BrickletAmbientLightV3.ILLUMINANCE_RANGE_1300LUX)
        self.range_combo.addItem("0 - 600 lx", BrickletAmbientLightV3.ILLUMINANCE_RANGE_600LUX)
        self.range_combo.currentIndexChanged.connect(self.new_config)

        self.time_label = QLabel('Integration Time:')
        self.time_combo = QComboBox()
        self.time_combo.addItem("50 ms", BrickletAmbientLightV3.INTEGRATION_TIME_50MS)
        self.time_combo.addItem("100 ms", BrickletAmbientLightV3.INTEGRATION_TIME_100MS)
        self.time_combo.addItem("150 ms", BrickletAmbientLightV3.INTEGRATION_TIME_150MS)
        self.time_combo.addItem("200 ms", BrickletAmbientLightV3.INTEGRATION_TIME_200MS)
        self.time_combo.addItem("250 ms", BrickletAmbientLightV3.INTEGRATION_TIME_250MS)
        self.time_combo.addItem("300 ms", BrickletAmbientLightV3.INTEGRATION_TIME_300MS)
        self.time_combo.addItem("350 ms", BrickletAmbientLightV3.INTEGRATION_TIME_350MS)
        self.time_combo.addItem("400 ms", BrickletAmbientLightV3.INTEGRATION_TIME_400MS)
        self.time_combo.currentIndexChanged.connect(self.new_config)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.range_label)
        hlayout.addWidget(self.range_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.time_label)
        hlayout.addWidget(self.time_combo)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.al.get_configuration, None, self.get_configucation_async, self.increase_error_count)
        async_call(self.al.get_illuminance, None, self.cb_illuminance, self.increase_error_count)
        self.cbe_illuminance.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_illuminance.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAmbientLightV3.DEVICE_IDENTIFIER

    def get_configucation_async(self, conf):
        self.range_combo.setCurrentIndex(self.range_combo.findData(conf.illuminance_range))
        self.time_combo.setCurrentIndex(self.time_combo.findData(conf.integration_time))

    def new_config(self, value):
        try:
            self.al.set_configuration(self.range_combo.itemData(self.range_combo.currentIndex()),
                                      self.time_combo.itemData(self.time_combo.currentIndex()))
        except:
            pass

    def cb_illuminance(self, illuminance):
        self.current_illuminance = illuminance / 100.0

        max_illuminance = 12000000 # Approximation for unlimited range
        current_range = self.range_combo.itemData(self.range_combo.currentIndex())
        if current_range == BrickletAmbientLightV3.ILLUMINANCE_RANGE_64000LUX:
            max_illuminance = 6400001
        elif current_range == BrickletAmbientLightV3.ILLUMINANCE_RANGE_32000LUX:
            max_illuminance = 3200001
        elif current_range == BrickletAmbientLightV3.ILLUMINANCE_RANGE_16000LUX:
            max_illuminance = 1600001
        elif current_range == BrickletAmbientLightV3.ILLUMINANCE_RANGE_8000LUX:
            max_illuminance = 800001
        elif current_range == BrickletAmbientLightV3.ILLUMINANCE_RANGE_1300LUX:
            max_illuminance = 130001
        elif current_range == BrickletAmbientLightV3.ILLUMINANCE_RANGE_600LUX:
            max_illuminance = 60001

        if illuminance == 0:
            self.plot_widget.get_key_item(0).setStyleSheet('QLabel { color: magenta }')
            self.out_of_range_label.hide()
            self.saturated_label.show()
        elif illuminance >= max_illuminance:
            self.plot_widget.get_key_item(0).setStyleSheet('QLabel { color: red }')
            self.out_of_range_label.show()
            self.saturated_label.hide()
        else:
            self.plot_widget.get_key_item(0).setStyleSheet('')
            self.out_of_range_label.hide()
            self.saturated_label.hide()

        value = min(max(illuminance * 255 / max_illuminance, 0), 255)
        self.alf.set_color(value, value, value)
