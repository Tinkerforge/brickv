# -*- coding: utf-8 -*-
"""
Ambient Light 2.0 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

ambient_light_v2.py: Ambient Light 2.0 Bricklet Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPainter, \
                        QColor, QBrush, QFrame, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_ambient_light_v2 import BrickletAmbientLightV2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class AmbientLightFrame(QFrame):
    def __init__(self, parent = None):
        QFrame.__init__(self, parent)
        self.color = QColor(128, 128, 128)
        self.setMinimumSize(25, 25)
        self.setMaximumSize(25, 25)

    def set_color(self, r, g, b):
        self.color = QColor(r, g, b)
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self.color))
        qp.setPen(self.color)
        qp.drawRect(0, 0, 25, 25)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.black)
        qp.drawRect(1, 1, 24, 24)
        qp.end()

class IlluminanceLabel(QLabel):
    def setText(self, illuminance):
        text = "Illuminance: {0:.2f} lx (Lux)".format(round(illuminance/100.0, 2))
        super(IlluminanceLabel, self).setText(text)

class AmbientLightV2(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletAmbientLightV2, *args)

        self.al = self.device

        self.has_clamped_output = self.firmware_version >= (2, 0, 2)

        self.cbe_illuminance = CallbackEmulator(self.al.get_illuminance,
                                                self.cb_illuminance,
                                                self.increase_error_count)

        self.illuminance_label = IlluminanceLabel('Illuminance: ')
        self.alf = AmbientLightFrame()
        self.out_of_range_label = QLabel('out-of-range')
        self.saturated_label = QLabel('sensor saturated')

        self.out_of_range_label.hide()
        self.out_of_range_label.setStyleSheet('QLabel { color: red }')
        self.saturated_label.hide()
        self.saturated_label.setStyleSheet('QLabel { color: magenta }')

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Illuminance [lx]', plot_list)

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.illuminance_label)
        layout_h.addWidget(self.out_of_range_label)
        layout_h.addWidget(self.saturated_label)
        layout_h.addWidget(self.alf)
        layout_h.addStretch()
        
        self.range_label = QLabel('Illuminance Range: ')
        self.range_combo = QComboBox()
        if self.has_clamped_output: # Also means that the unlimited range is available
            self.range_combo.addItem("Unlimited", BrickletAmbientLightV2.ILLUMINANCE_RANGE_UNLIMITED)
        self.range_combo.addItem("0 - 64000 Lux", BrickletAmbientLightV2.ILLUMINANCE_RANGE_64000LUX)
        self.range_combo.addItem("0 - 32000 Lux", BrickletAmbientLightV2.ILLUMINANCE_RANGE_32000LUX)
        self.range_combo.addItem("0 - 16000 Lux", BrickletAmbientLightV2.ILLUMINANCE_RANGE_16000LUX)
        self.range_combo.addItem("0 - 8000 Lux", BrickletAmbientLightV2.ILLUMINANCE_RANGE_8000LUX)
        self.range_combo.addItem("0 - 1300 Lux", BrickletAmbientLightV2.ILLUMINANCE_RANGE_1300LUX)
        self.range_combo.addItem("0 - 600 Lux", BrickletAmbientLightV2.ILLUMINANCE_RANGE_600LUX)
        self.range_combo.currentIndexChanged.connect(self.new_config)
        
        self.time_label = QLabel('Integration Time: ')
        self.time_combo = QComboBox()
        self.time_combo.addItem("50ms", BrickletAmbientLightV2.INTEGRATION_TIME_50MS)
        self.time_combo.addItem("100ms", BrickletAmbientLightV2.INTEGRATION_TIME_100MS)
        self.time_combo.addItem("150ms", BrickletAmbientLightV2.INTEGRATION_TIME_150MS)
        self.time_combo.addItem("200ms", BrickletAmbientLightV2.INTEGRATION_TIME_200MS)
        self.time_combo.addItem("250ms", BrickletAmbientLightV2.INTEGRATION_TIME_250MS)
        self.time_combo.addItem("300ms", BrickletAmbientLightV2.INTEGRATION_TIME_300MS)
        self.time_combo.addItem("350ms", BrickletAmbientLightV2.INTEGRATION_TIME_350MS)
        self.time_combo.addItem("400ms", BrickletAmbientLightV2.INTEGRATION_TIME_400MS)
        self.time_combo.currentIndexChanged.connect(self.new_config)
        
        layout_hc = QHBoxLayout()
        layout_hc.addStretch()
        layout_hc.addWidget(self.range_label)
        layout_hc.addWidget(self.range_combo)
        layout_hc.addStretch()
        layout_hc.addWidget(self.time_label)
        layout_hc.addWidget(self.time_combo)
        layout_hc.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_hc)

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

    def get_url_part(self):
        return 'ambient_light_v2'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAmbientLightV2.DEVICE_IDENTIFIER
    
    def get_configucation_async(self, conf):
        self.range_combo.setCurrentIndex(self.range_combo.findData(conf.illuminance_range))
        self.time_combo.setCurrentIndex(self.time_combo.findData(conf.integration_time))
        
    def new_config(self, value):
        try:
            self.al.set_configuration(self.range_combo.itemData(self.range_combo.currentIndex()),
                                      self.time_combo.itemData(self.time_combo.currentIndex()))
        except:
            pass

    def get_current_value(self):
        return self.current_value

    def cb_illuminance(self, illuminance):
        self.current_value = illuminance/100.0
        self.illuminance_label.setText(illuminance)

        max_illuminance = 12000000 # Approximation for unlimited range
        current_range = self.range_combo.itemData(self.range_combo.currentIndex())
        if current_range == BrickletAmbientLightV2.ILLUMINANCE_RANGE_64000LUX:
            max_illuminance = 6400001
        elif current_range == BrickletAmbientLightV2.ILLUMINANCE_RANGE_32000LUX:
            max_illuminance = 3200001
        elif current_range == BrickletAmbientLightV2.ILLUMINANCE_RANGE_16000LUX:
            max_illuminance = 1600001
        elif current_range == BrickletAmbientLightV2.ILLUMINANCE_RANGE_8000LUX:
            max_illuminance = 800001
        elif current_range == BrickletAmbientLightV2.ILLUMINANCE_RANGE_1300LUX:
            max_illuminance = 130001
        elif current_range == BrickletAmbientLightV2.ILLUMINANCE_RANGE_600LUX:
            max_illuminance = 60001

        if self.has_clamped_output: # Also means that the unlimited range is available
            if illuminance == 0:
                self.illuminance_label.setStyleSheet('QLabel { color: magenta }')
                self.out_of_range_label.hide()
                self.saturated_label.show()
            elif illuminance >= max_illuminance:
                self.illuminance_label.setStyleSheet('QLabel { color: red }')
                self.out_of_range_label.show()
                self.saturated_label.hide()
            else:
                self.illuminance_label.setStyleSheet('')
                self.out_of_range_label.hide()
                self.saturated_label.hide()

        value = min(max(illuminance*255/max_illuminance, 0), 255)
        self.alf.set_color(value, value, value)
