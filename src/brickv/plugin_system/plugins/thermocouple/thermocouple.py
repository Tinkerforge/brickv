# -*- coding: utf-8 -*-  
"""
Thermocouple Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

thermocouple.py: Thermocouple Plugin Implementation

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

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_thermocouple import BrickletThermocouple
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class TemperatureLabel(QLabel):
    def setText(self, text):
        text = "Temperature: " + text + " %cC" % 0xB0
        super(TemperatureLabel, self).setText(text)
    
class Thermocouple(PluginBase):
    AVERAGING = [BrickletThermocouple.AVERAGING_1, BrickletThermocouple.AVERAGING_2, BrickletThermocouple.AVERAGING_4, BrickletThermocouple.AVERAGING_8, BrickletThermocouple.AVERAGING_16]
    THERMOCOUPLE_TYPE = [BrickletThermocouple.TYPE_B, BrickletThermocouple.TYPE_E, BrickletThermocouple.TYPE_J, BrickletThermocouple.TYPE_K, BrickletThermocouple.TYPE_N, BrickletThermocouple.TYPE_R, BrickletThermocouple.TYPE_S, BrickletThermocouple.TYPE_T, BrickletThermocouple.TYPE_G8, BrickletThermocouple.TYPE_G32]
    FILTER_TYPE = [BrickletThermocouple.FILTER_OPTION_50HZ, BrickletThermocouple.FILTER_OPTION_60HZ]
    
    qtcb_error_state = pyqtSignal(bool, bool)
    
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletThermocouple, *args)
        
        self.thermo = self.device
        
        self.qtcb_error_state.connect(self.cb_error_state)
        self.thermo.register_callback(self.thermo.CALLBACK_ERROR_STATE,
                                      self.qtcb_error_state.emit)

        self.cbe_temperature = CallbackEmulator(self.thermo.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.temperature_label = TemperatureLabel()
        
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Temperature [%cC]' % 0xB0, plot_list)

        self.averaging_label = QLabel('Averaging:')
        self.averaging_combo = QComboBox()
        self.averaging_combo.addItem('1 sample')
        self.averaging_combo.addItem('2 samples')
        self.averaging_combo.addItem('4 samples')
        self.averaging_combo.addItem('8 samples')
        self.averaging_combo.addItem('16 samples')
        
        self.type_label = QLabel('Thermocouple Type:')
        self.type_combo = QComboBox()
        self.type_combo.addItem('B')
        self.type_combo.addItem('E')
        self.type_combo.addItem('J')
        self.type_combo.addItem('K')
        self.type_combo.addItem('N')
        self.type_combo.addItem('R')
        self.type_combo.addItem('S')
        self.type_combo.addItem('T')
        self.type_combo.addItem('Gain 8')
        self.type_combo.addItem('Gain 32')
        
        self.filter_label = QLabel('Noise Rejection Filter:')
        self.filter_combo = QComboBox()
        self.filter_combo.addItem('50Hz')
        self.filter_combo.addItem('60Hz')
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        self.error_label = QLabel('Current errors: None')
        
        layout_conf = QHBoxLayout()
        layout_conf.addWidget(self.averaging_label)
        layout_conf.addWidget(self.averaging_combo)
        layout_conf.addStretch()
        layout_conf.addWidget(self.type_label)
        layout_conf.addWidget(self.type_combo)
        layout_conf.addStretch()
        layout_conf.addWidget(self.filter_label)
        layout_conf.addWidget(self.filter_combo)
        
        layout_error = QHBoxLayout()
        layout_error.addStretch()
        layout_error.addWidget(self.error_label)
        layout_error.addStretch()
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.temperature_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_conf)
        layout.addWidget(line)
        layout.addLayout(layout_error)
        
        self.averaging_combo.currentIndexChanged.connect(self.configuration_changed)
        self.type_combo.currentIndexChanged.connect(self.configuration_changed)
        self.filter_combo.currentIndexChanged.connect(self.configuration_changed)
        
        
    def start(self):
        async_call(self.thermo.get_temperature, None, self.cb_temperature, self.increase_error_count)
        async_call(self.thermo.get_configuration, None, self.cb_configuration, self.increase_error_count)
        async_call(self.thermo.get_error_state, None, lambda e: self.cb_error_state(e.over_under, e.open_circuit))
        self.cbe_temperature.set_period(100)
        
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_temperature.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'temperature'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletThermocouple.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value
    
    def configuration_changed(self, _):
        conf_averaging = Thermocouple.AVERAGING[self.averaging_combo.currentIndex()]
        conf_type = Thermocouple.THERMOCOUPLE_TYPE[self.type_combo.currentIndex()]
        conf_filter = Thermocouple.FILTER_TYPE[self.filter_combo.currentIndex()]
        
        self.thermo.set_configuration(conf_averaging, conf_type, conf_filter)

    def cb_temperature(self, temperature):
        self.current_value = temperature/100.0
        self.temperature_label.setText(str(temperature/100.0))

    def cb_configuration(self, conf):
        self.averaging_combo.blockSignals(True)
        if conf.averaging == self.thermo.AVERAGING_1:
            self.averaging_combo.setCurrentIndex(0)
        elif conf.averaging == self.thermo.AVERAGING_2:
            self.averaging_combo.setCurrentIndex(1)
        elif conf.averaging == self.thermo.AVERAGING_4:
            self.averaging_combo.setCurrentIndex(2)
        elif conf.averaging == self.thermo.AVERAGING_8:
            self.averaging_combo.setCurrentIndex(3)
        elif conf.averaging == self.thermo.AVERAGING_16:
            self.averaging_combo.setCurrentIndex(4)
        self.averaging_combo.blockSignals(False)
            
        self.type_combo.blockSignals(True)
        if conf.thermocouple_type == self.thermo.TYPE_B:
            self.type_combo.setCurrentIndex(0)
        elif conf.thermocouple_type == self.thermo.TYPE_E:
            self.type_combo.setCurrentIndex(1)
        elif conf.thermocouple_type == self.thermo.TYPE_J:
            self.type_combo.setCurrentIndex(2)
        elif conf.thermocouple_type == self.thermo.TYPE_K:
            self.type_combo.setCurrentIndex(3)
        elif conf.thermocouple_type == self.thermo.TYPE_N:
            self.type_combo.setCurrentIndex(4)
        elif conf.thermocouple_type == self.thermo.TYPE_R:
            self.type_combo.setCurrentIndex(5)
        elif conf.thermocouple_type == self.thermo.TYPE_S:
            self.type_combo.setCurrentIndex(6)
        elif conf.thermocouple_type == self.thermo.TYPE_T:
            self.type_combo.setCurrentIndex(7)
        elif conf.thermocouple_type == self.thermo.TYPE_G8:
            self.type_combo.setCurrentIndex(8)
        elif conf.thermocouple_type == self.thermo.TYPE_G32:
            self.type_combo.setCurrentIndex(9)
        self.type_combo.blockSignals(False)

        self.filter_combo.blockSignals(True)
        if conf.filter == self.thermo.FILTER_OPTION_50HZ:
            self.filter_combo.setCurrentIndex(0)
        elif conf.filter == self.thermo.FILTER_OPTION_60HZ:
            self.filter_combo.setCurrentIndex(1)
        self.filter_combo.blockSignals(False)
        
    def cb_error_state(self, over_under, open_circuit):
        if over_under or open_circuit:
            text = 'Current errors: '
            if over_under:
                text += 'Over/Under Voltage'
            if over_under and open_circuit:
                text += ' and '
            if open_circuit:
                text += 'Open Circuit (defective thermocouple or nothing connected)'
                
            self.error_label.setStyleSheet('QLabel { color : red }')
            self.error_label.setText(text)
        else:
            self.error_label.setStyleSheet('')
            self.error_label.setText('Current errors: None')
            