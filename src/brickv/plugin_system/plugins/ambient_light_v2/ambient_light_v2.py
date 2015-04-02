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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_ambient_light_v2 import BrickletAmbientLightV2
from brickv.async_call import async_call
from brickv.utils import CallbackEmulator

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPainter, QColor, QBrush, QFrame, QComboBox
from PyQt4.QtCore import Qt

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

        self.cbe_illuminance = CallbackEmulator(self.al.get_illuminance,
                                                self.cb_illuminance,
                                                self.increase_error_count)

        self.illuminance_label = IlluminanceLabel('Illuminance: ')
        self.alf = AmbientLightFrame()

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Illuminance [lx]', plot_list)

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.illuminance_label)
        layout_h.addWidget(self.alf)
        layout_h.addStretch()
        
        self.range_label = QLabel('Illuminance Range: ')
        self.range_combo = QComboBox()
        self.range_combo.addItem("0 - 64000 Lux")
        self.range_combo.addItem("0 - 32000 Lux")
        self.range_combo.addItem("0 - 16000 Lux")
        self.range_combo.addItem("0 - 8000 Lux")
        self.range_combo.addItem("0 - 1300 Lux")
        self.range_combo.addItem("0 - 600 Lux")
        self.range_combo.activated.connect(self.new_config)
        
        self.time_label = QLabel('Integration Time: ')
        self.time_combo = QComboBox()
        self.time_combo.addItem("50ms")
        self.time_combo.addItem("100ms")
        self.time_combo.addItem("150ms")
        self.time_combo.addItem("200ms")
        self.time_combo.addItem("250ms")
        self.time_combo.addItem("300ms")
        self.time_combo.addItem("350ms")
        self.time_combo.addItem("400ms")
        self.time_combo.activated.connect(self.new_config)
        
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
        self.range_combo.setCurrentIndex(conf.illuminance_range)
        self.time_combo.setCurrentIndex(conf.integration_time)
        
    def new_config(self, value):
        try:
            self.al.set_configuration(self.range_combo.currentIndex(), 
                                      self.time_combo.currentIndex())
        except:
            pass

    def get_current_value(self):
        return self.current_value

    def cb_illuminance(self, illuminance):
        self.current_value = illuminance/100.0
        self.illuminance_label.setText(illuminance)

        value = illuminance*255/64000
        self.alf.set_color(value, value, value)
