# -*- coding: utf-8 -*-  
"""
Industrial Dual 0-20mA Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

industrial_dual_0_20ma.py: PTC Plugin Implementation

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
from brickv.bindings.bricklet_industrial_dual_0_20ma import BrickletIndustrialDual020mA
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox
from PyQt4.QtCore import pyqtSignal, Qt, QTimer

class CurrentLabel(QLabel):
    def setText(self, text):
        text = "Current: " + text + " mA"
        super(CurrentLabel, self).setText(text)

class IndustrialDual020mA(PluginBase):
    qtcb_current = pyqtSignal(int, int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Industrial Dual 0-20mA Bricklet', version)
        
        self.str_connected = 'Sensor {0} is currently <font color="green">connected</font>'
        self.str_not_connected = 'Sensor {0} is currently <font color="red">not connected</font>'
        
        self.dual020 = BrickletIndustrialDual020mA(uid, ipcon)
        
        self.qtcb_current.connect(self.cb_current)
        self.dual020.register_callback(self.dual020.CALLBACK_CURRENT,
                                       self.qtcb_current.emit) 

        self.current_label = [CurrentLabel(), CurrentLabel()]
        
        self.sample_rate_label1 = QLabel('Sample Rate:')
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItem('240')
        self.sample_rate_combo.addItem('60')
        self.sample_rate_combo.addItem('15')
        self.sample_rate_combo.addItem('4')
        self.sample_rate_label2 = QLabel('Samples per second')
        
        self.connected_label = [QLabel(self.str_not_connected.format(0)),
                                QLabel(self.str_not_connected.format(1))]
        
        self.current_value = [None, None]
        
        self.sample_rate_combo.currentIndexChanged.connect(self.sample_rate_combo_index_changed)
        
        plot_list = [['Sensor 0', Qt.red, self.get_current_value0],
                     ['Sensor 1', Qt.blue, self.get_current_value1]]
        self.plot_widget = PlotWidget('Current [mA]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addWidget(QLabel("Sensor 0: "))
        layout_h.addWidget(self.current_label[0])
        layout_h.addStretch()
        layout_h.addWidget(self.connected_label[0])
        
        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(QLabel("Sensor 1: "))
        layout_h2.addWidget(self.current_label[1])
        layout_h2.addStretch()
        layout_h2.addWidget(self.connected_label[1])
        
        layout_h3 = QHBoxLayout()
        layout_h3.addWidget(self.sample_rate_label1)
        layout_h3.addWidget(self.sample_rate_combo)
        layout_h3.addWidget(self.sample_rate_label2)
        layout_h3.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_h3)
        
    def start(self):
        async_call(self.dual020.get_current, 0, lambda x: self.cb_current(0, x), self.increase_error_count)
        async_call(self.dual020.get_current, 1, lambda x: self.cb_current(1, x), self.increase_error_count)
        async_call(self.dual020.set_current_callback_period, (0, 100), None, self.increase_error_count)
        async_call(self.dual020.set_current_callback_period, (1, 100), None, self.increase_error_count)
        
        async_call(self.dual020.get_sample_rate, None, self.get_sample_rate_async, self.increase_error_count)
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.dual020.set_current_callback_period, (0, 0), None, self.increase_error_count)
        async_call(self.dual020.set_current_callback_period, (1, 0), None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'industrial_dual_0_20ma'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDual020mA.DEVICE_IDENTIFIER

    def get_current_value0(self):
        return self.current_value[0]
    
    def get_current_value1(self):
        return self.current_value[1]
    
    def update_connected(self):
        pass
    
    def sample_rate_combo_index_changed(self, index):
        async_call(self.dual020.set_sample_rate, index, None, self.increase_error_count)
    
    def get_sample_rate_async(self, rate):
        self.sample_rate_combo.setCurrentIndex(rate)

    def cb_current(self, sensor, current):
        value = current/(1000*1000.0)
        self.current_label[sensor].setText('%6.02f' % round(value, 2))
        self.current_value[sensor] = value
        if value < 3.9:
            self.connected_label[sensor].setText(self.str_not_connected.format(sensor))
        else:
            self.connected_label[sensor].setText(self.str_connected.format(sensor))
