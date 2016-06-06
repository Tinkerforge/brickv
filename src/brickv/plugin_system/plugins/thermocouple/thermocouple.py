# -*- coding: utf-8 -*-  
"""
Thermocouple Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

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

class Thermocouple(PluginBase):
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

        self.current_temperature = None # float, °C

        self.error_label = QLabel('Current Errors: None')
        self.error_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        plots = [('Temperature', Qt.red, lambda: self.current_temperature, u'{:.2f} °C'.format)]
        self.plot_widget = PlotWidget(u'Temperature [°C]', plots, extra_key_widgets=[self.error_label])

        self.averaging_label = QLabel('Averaging:')
        self.averaging_combo = QComboBox()
        self.averaging_combo.addItem('1', BrickletThermocouple.AVERAGING_1)
        self.averaging_combo.addItem('2', BrickletThermocouple.AVERAGING_2)
        self.averaging_combo.addItem('4', BrickletThermocouple.AVERAGING_4)
        self.averaging_combo.addItem('8', BrickletThermocouple.AVERAGING_8)
        self.averaging_combo.addItem('16', BrickletThermocouple.AVERAGING_16)
        
        self.type_label = QLabel('Thermocouple Type:')
        self.type_combo = QComboBox()
        self.type_combo.addItem('B', BrickletThermocouple.TYPE_B)
        self.type_combo.addItem('E', BrickletThermocouple.TYPE_E)
        self.type_combo.addItem('J', BrickletThermocouple.TYPE_J)
        self.type_combo.addItem('K', BrickletThermocouple.TYPE_K)
        self.type_combo.addItem('N', BrickletThermocouple.TYPE_N)
        self.type_combo.addItem('R', BrickletThermocouple.TYPE_R)
        self.type_combo.addItem('S', BrickletThermocouple.TYPE_S)
        self.type_combo.addItem('T', BrickletThermocouple.TYPE_T)
        self.type_combo.addItem('Gain 8', BrickletThermocouple.TYPE_G8)
        self.type_combo.addItem('Gain 32', BrickletThermocouple.TYPE_G32)

        self.filter_label = QLabel('Noise Rejection Filter:')
        self.filter_combo = QComboBox()
        self.filter_combo.addItem('50 Hz', BrickletThermocouple.FILTER_OPTION_50HZ)
        self.filter_combo.addItem('60 Hz', BrickletThermocouple.FILTER_OPTION_60HZ)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.averaging_label)
        hlayout.addWidget(self.averaging_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.type_label)
        hlayout.addWidget(self.type_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.filter_label)
        hlayout.addWidget(self.filter_combo)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)
        
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
        return 'thermocouple'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletThermocouple.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value
    
    def configuration_changed(self, _):
        conf_averaging = self.averaging_combo.itemData(self.averaging_combo.currentIndex())
        conf_type = self.type_combo.itemData(self.type_combo.currentIndex())
        conf_filter = self.filter_combo.itemData(self.filter_combo.currentIndex())
        
        self.thermo.set_configuration(conf_averaging, conf_type, conf_filter)

    def cb_temperature(self, temperature):
        self.current_temperature = temperature / 100.0

    def cb_configuration(self, conf):
        self.averaging_combo.blockSignals(True)
        self.averaging_combo.setCurrentIndex(self.averaging_combo.findData(conf.averaging))
        self.averaging_combo.blockSignals(False)
            
        self.type_combo.blockSignals(True)
        self.type_combo.setCurrentIndex(self.type_combo.findData(conf.thermocouple_type))
        self.type_combo.blockSignals(False)

        self.filter_combo.blockSignals(True)
        self.filter_combo.setCurrentIndex(self.filter_combo.findData(conf.filter))
        self.filter_combo.blockSignals(False)
        
    def cb_error_state(self, over_under, open_circuit):
        if over_under or open_circuit:
            text = 'Current Errors: '
            if over_under:
                text += 'Over/Under Voltage'
            if over_under and open_circuit:
                text += ' and '
            if open_circuit:
                text += 'Open Circuit\n(defective thermocouple or nothing connected)'
                
            self.error_label.setStyleSheet('QLabel { color : red }')
            self.error_label.setText(text)
        else:
            self.error_label.setStyleSheet('')
            self.error_label.setText('Current Errors: None')
