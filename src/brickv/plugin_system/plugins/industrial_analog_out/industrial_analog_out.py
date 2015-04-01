# -*- coding: utf-8 -*-  
"""
Industrial Analog Out Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

industrial_analog_out.py: Industrial Analog Out Plugin Implementation

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
from brickv.bindings.bricklet_industrial_analog_out import BrickletIndustrialAnalogOut
from brickv.plugin_system.plugins.industrial_analog_out.ui_industrial_analog_out import Ui_IndustrialAnalogOut
from brickv.async_call import async_call
from brickv.utils import CallbackEmulator

class IndustrialAnalogOut(PluginBase, Ui_IndustrialAnalogOut):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletIndustrialAnalogOut, *args)
        
        self.setupUi(self)

        self.ao = self.device
        
        self.spin_voltage.editingFinished.connect(self.voltage_spin_finished)
        self.slider_voltage.sliderReleased.connect(self.voltage_slider_released)
        self.slider_voltage.valueChanged.connect(self.voltage_slider_changed)
        self.spin_current.editingFinished.connect(self.current_spin_finished)
        self.slider_current.sliderReleased.connect(self.current_slider_released)
        self.slider_current.valueChanged.connect(self.current_slider_changed)
        
        self.radio_voltage.released.connect(self.radio_released)
        self.radio_current.released.connect(self.radio_released)
        
        self.box_voltage_range.activated.connect(self.config_changed)
        self.box_current_range.activated.connect(self.config_changed)
        
        self.last_voltage = 0
        self.last_current = 4000
        self.last_voltage_range = 0
        self.last_current_range = 1
        
        self.ui_voltage = [self.label_voltage, self.label_mv, self.label_voltage_range, self.slider_voltage, self.spin_voltage, self.box_voltage_range]
        self.ui_current = [self.label_current, self.label_ua, self.label_current_range, self.slider_current, self.spin_current, self.box_current_range]
        self.new_voltage(self.last_voltage)
        self.new_current(self.last_current)
        self.mode_voltage()
        
    def start(self):
        async_call(self.ao.get_voltage, None, self.new_voltage, self.increase_error_count)
        async_call(self.ao.get_current, None, self.new_current, self.increase_error_count)
        async_call(self.ao.get_configuration, None, self.cb_get_configuration, self.increase_error_count)
        
    def stop(self):
        pass

    def destroy(self):
        pass

    def get_url_part(self):
        return 'industrial_analog_out'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialAnalogOut.DEVICE_IDENTIFIER
    
    def new_voltage(self, voltage):
        try:
            self.last_voltage = voltage
            self.spin_voltage.setValue(voltage)
            self.slider_voltage.setValue(voltage)
            self.label_voltage.setText("Output Voltage: " + "{0:.3f}V".format(round(voltage/1000.0, 3)))
        except:
            pass
    
    def new_current(self, current):
        try:
            self.last_current = current
            self.spin_current.setValue(current)
            self.slider_current.setValue(current)
            self.label_current.setText("Output Current: " + "{0:.3f}mA".format(round(current/1000.0, 3)))
        except:
            pass

    def mode_voltage(self):
        for ui in self.ui_voltage:
            ui.show()
        for ui in self.ui_current:
            ui.hide()
        
    def mode_current(self):
        for ui in self.ui_voltage:
            ui.hide()
        for ui in self.ui_current:
            ui.show()
            
    def radio_released(self):
        if self.radio_voltage.isChecked():
            async_call(self.ao.get_voltage, None, self.new_voltage, self.increase_error_count)
            self.mode_voltage()
        else:
            async_call(self.ao.get_current, None, self.new_current, self.increase_error_count)
            self.mode_current()
    
    def voltage_spin_finished(self):
        value = self.spin_voltage.value()
        self.new_voltage(value)
        self.ao.set_voltage(value)
    
    def voltage_slider_released(self):
        value = self.slider_voltage.value()
        self.new_voltage(value)
        self.ao.set_voltage(value)
    
    def voltage_slider_changed(self, value):
        self.spin_voltage.setValue(value)
    
    def current_spin_finished(self):
        value = self.spin_current.value()
        self.new_current(value)
        self.ao.set_current(value)
    
    def current_slider_released(self):
        value = self.slider_current.value()
        self.new_current(value)
        self.ao.set_current(value)
    
    def current_slider_changed(self, value):
        self.spin_current.setValue(value)
        
    # TODO: use constants from Bindings when available
    def new_configuration(self):
        if self.last_voltage_range == 0:
            self.slider_voltage.setMaximum(5000)
            self.spin_voltage.setMaximum(5000)
        elif self.last_voltage_range == 1:
            self.slider_voltage.setMaximum(10000)
            self.spin_voltage.setMaximum(10000)
            
        if self.last_current_range == 0:
            self.slider_current.setMinimum(4000)
            self.spin_current.setMinimum(4000)
            self.slider_current.setMaximum(20000)
            self.spin_current.setMaximum(20000)
        elif self.last_current_range == 1:
            self.slider_current.setMinimum(0)
            self.spin_current.setMinimum(0)
            self.slider_current.setMaximum(20000)
            self.spin_current.setMaximum(20000)
        elif self.last_current_range == 2:
            self.slider_current.setMinimum(0)
            self.spin_current.setMinimum(0)
            self.slider_current.setMaximum(24000)
            self.spin_current.setMaximum(24000)
    
    def config_changed(self, value):
        voltage_range = self.box_voltage_range.currentIndex()
        current_range = self.box_current_range.currentIndex()
        try:
            self.ao.set_configuration(voltage_range, current_range)
            async_call(self.ao.get_voltage, None, self.new_voltage, self.increase_error_count)
            async_call(self.ao.get_current, None, self.new_current, self.increase_error_count)
            self.last_voltage_range = voltage_range
            self.last_current_range = current_range
            self.new_configuration()
        except:
            pass

    
    def cb_get_configuration(self, conf):
        self.last_voltage_range = conf.voltage_range
        self.last_current_range = conf.current_range
        self.box_voltage_range.setCurrentIndex(conf.voltage_range)
        self.box_current_range.setCurrentIndex(conf.current_range)
        self.new_configuration()