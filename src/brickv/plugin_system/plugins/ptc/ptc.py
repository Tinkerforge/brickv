# -*- coding: utf-8 -*-  
"""
PTC Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

ptc.py: PTC Plugin Implementation

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
from brickv.bindings.bricklet_ptc import BrickletPTC
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox
from PyQt4.QtCore import pyqtSignal, Qt, QTimer

class TemperatureLabel(QLabel):
    def setText(self, text):
        text = "Temperature: " + text + " %cC" % 0xB0
        super(TemperatureLabel, self).setText(text)

#class ResistanceLabel(QLabel):
#    def setText(self, text):
#        text = "Resistance: " + text + " Ohm"
#        super(ResistanceLabel, self).setText(text)
    
class PTC(PluginBase):
    qtcb_temperature = pyqtSignal(int)
#    qtcb_resistance = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'PTC Bricklet', version, BrickletPTC)

        self.ptc = self.device
        
        self.str_connected = 'Sensor is currently <font color="green">connected</font>'
        self.str_not_connected = 'Sensor is currently <font color="red">not connected</font>'
        
        self.qtcb_temperature.connect(self.cb_temperature)
        self.ptc.register_callback(self.ptc.CALLBACK_TEMPERATURE,
                                   self.qtcb_temperature.emit) 
        
#        self.qtcb_resistance.connect(self.cb_resistance)
#        self.ptc.register_callback(self.ptc.CALLBACK_RESISTANCE,
#                                   self.qtcb_resistance.emit) 
        
        self.temperature_label = TemperatureLabel()
#        self.resistance_label = ResistanceLabel()
        
        self.wire_label = QLabel('Wire Type:')
        self.wire_combo = QComboBox()
        self.wire_combo.addItem('2-Wire')
        self.wire_combo.addItem('3-Wire')
        self.wire_combo.addItem('4-Wire')
        
        self.noise_label = QLabel('Noise Rejection Filter:')
        self.noise_combo = QComboBox()
        self.noise_combo.addItem('50Hz')
        self.noise_combo.addItem('60Hz')
        
        self.connected_label = QLabel(self.str_connected)
        
        self.current_value = None
        
        self.wire_combo.currentIndexChanged.connect(self.wire_combo_index_changed)
        self.noise_combo.currentIndexChanged.connect(self.noise_combo_index_changed)
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Temperature [%cC]' % 0xB0, plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.temperature_label)
        layout_h.addStretch()
        layout_h.addWidget(self.connected_label)
        layout_h.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(self.wire_label)
        layout_h2.addWidget(self.wire_combo)
        layout_h2.addStretch()
        layout_h2.addWidget(self.noise_label)
        layout_h2.addWidget(self.noise_combo)

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_h2)
        
        self.connected_timer = QTimer()
        self.connected_timer.timeout.connect(self.update_connected)
        self.connected_timer.setInterval(1000)

    def start(self):
        async_call(self.ptc.get_temperature, None, self.cb_temperature, self.increase_error_count)
#        async_call(self.ptc.get_resistance, None, self.cb_resistance, self.increase_error_count)
        async_call(self.ptc.set_temperature_callback_period, 100, None, self.increase_error_count)
#        async_call(self.ptc.set_resistance_callback_period, 100, None, self.increase_error_count)
        
        async_call(self.ptc.is_sensor_connected, None, self.is_sensor_connected_async, self.increase_error_count)
        async_call(self.ptc.get_noise_rejection_filter, None, self.get_noise_rejection_filter_async, self.increase_error_count)
        async_call(self.ptc.get_wire_mode, None, self.get_wire_mode_async, self.increase_error_count)
        
        self.connected_timer.start()
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.ptc.set_temperature_callback_period, 0, None, self.increase_error_count)
#        async_call(self.ptc.set_resistance_callback_period, 0, None, self.increase_error_count)
        
        self.connected_timer.stop()
        self.plot_widget.stop = True

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'ptc'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPTC.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value
    
    def update_connected(self):
        async_call(self.ptc.is_sensor_connected, None, self.is_sensor_connected_async, self.increase_error_count)
    
    def wire_combo_index_changed(self, index):
        async_call(self.ptc.set_wire_mode, index+2, None, self.increase_error_count)
        
    def noise_combo_index_changed(self, index):
        async_call(self.ptc.set_noise_rejection_filter, index, None, self.increase_error_count)
    
    def is_sensor_connected_async(self, connected):
        if connected:
            self.connected_label.setText(self.str_connected)
        else:
            self.connected_label.setText(self.str_not_connected)
    
    def get_noise_rejection_filter_async(self, filter_option):
        self.noise_combo.setCurrentIndex(filter_option)
        
    def get_wire_mode_async(self, mode):
        self.wire_combo.setCurrentIndex(mode-2)

    def cb_temperature(self, temperature):
        self.current_value = temperature/100.0
        self.temperature_label.setText('%8.02f' % (temperature/100.0))
        
    def cb_resistance(self, resistance):
        resistance_str = str(round(resistance*3900.0/(1 << 15), 1))
        self.resistance_label.setText(resistance_str)
