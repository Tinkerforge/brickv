# -*- coding: utf-8 -*-  
"""
Current Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

current.py: Current Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from plot_widget import PlotWidget

from PyQt4.QtGui import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpinBox
from PyQt4.QtCore import pyqtSignal, Qt
        
from bindings import bricklet_voltage_current

from ui_voltage_current import Ui_VoltageCurrent
        
class CurrentLabel(QLabel):
    def setText(self, text):
        text = "Current: " + text + " mA"
        super(CurrentLabel, self).setText(text)
        
class VoltageLabel(QLabel):
    def setText(self, text):
        text = "Voltage: " + text + " mV"
        super(VoltageLabel, self).setText(text)

class PowerLabel(QLabel):
    def setText(self, text):
        text = "Power: " + text + " mW"
        super(PowerLabel, self).setText(text)
    
class VoltageCurrent(PluginBase, Ui_VoltageCurrent):
    qtcb_current = pyqtSignal(int)
    qtcb_voltage = pyqtSignal(int)
    qtcb_power = pyqtSignal(int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.vc = bricklet_voltage_current.VoltageCurrent(self.uid)
        self.ipcon.add_device(self.vc)
        self.version = '.'.join(map(str, self.vc.get_version()[1]))
        
        self.qtcb_current.connect(self.cb_current)
        self.vc.register_callback(self.vc.CALLBACK_CURRENT,
                                  self.qtcb_current.emit)
        self.qtcb_voltage.connect(self.cb_voltage)
        self.vc.register_callback(self.vc.CALLBACK_VOLTAGE,
                                  self.qtcb_voltage.emit)
        self.qtcb_power.connect(self.cb_power)
        self.vc.register_callback(self.vc.CALLBACK_POWER,
                                  self.qtcb_power.emit)
        
        self.current_label = CurrentLabel('Current: ')
        self.voltage_label = VoltageLabel('Voltage: ')
        self.power_label = PowerLabel('Power: ')
        
        self.current_value = 0
        self.voltage_value = 0
        self.power_value = 0
        
        plot_list_current = [['', Qt.red, self.get_current_value]]
        plot_list_voltage = [['', Qt.blue, self.get_voltage_value]]
        plot_list_power = [['', Qt.darkGreen, self.get_power_value]]
        self.plot_widget_current = PlotWidget('Current [mA]', plot_list_current)
        self.plot_widget_voltage = PlotWidget('Voltage [mV]', plot_list_voltage)
        self.plot_widget_power = PlotWidget('Power [mW]', plot_list_power)
        
        self.save_cal_button.pressed.connect(self.save_cal_pressed)
        self.save_conf_button.pressed.connect(self.save_conf_pressed)
        
        layout_plots = QHBoxLayout()
        layout_current = QVBoxLayout()
        layout_voltage = QVBoxLayout()
        layout_power = QVBoxLayout()
        
        layout_label_current = QHBoxLayout()
        layout_label_current.addStretch()
        layout_label_current.addWidget(self.current_label)
        layout_label_current.addStretch()
        layout_current.addLayout(layout_label_current)
        layout_current.addWidget(self.plot_widget_current)
        
        layout_label_voltage = QHBoxLayout()
        layout_label_voltage.addStretch()
        layout_label_voltage.addWidget(self.voltage_label)
        layout_label_voltage.addStretch()
        layout_voltage.addLayout(layout_label_voltage)
        layout_voltage.addWidget(self.plot_widget_voltage)
        
        layout_label_power = QHBoxLayout()
        layout_label_power.addStretch()
        layout_label_power.addWidget(self.power_label)
        layout_label_power.addStretch()
        layout_power.addLayout(layout_label_power)
        layout_power.addWidget(self.plot_widget_power)
        
        layout_plots.addLayout(layout_current)
        layout_plots.addLayout(layout_voltage)
        layout_plots.addLayout(layout_power)
        
        self.main_layout.insertLayout(0, layout_plots)
        
    def get_configuration_async(self, conf):
        avg, vol, cur = conf
        self.averaging_box.setCurrentIndex(avg)
        self.voltage_box.setCurrentIndex(vol)
        self.current_box.setCurrentIndex(cur)
        
    def get_calibration_async(self, calibration):
        gainmul, gaindiv = calibration
        self.gainmul_spinbox.setValue(gainmul)
        self.gaindiv_spinbox.setValue(gaindiv)
            
    def start(self):
        current = self.vc.get_current()
        voltage = self.vc.get_voltage()
        power = self.vc.get_power()
        configuration = self.vc.get_configuration()
        calibration = self.vc.get_calibration()

        self.cb_current(current)
        self.cb_voltage(voltage)
        self.cb_power(power)
        self.get_configuration_async(configuration)
        self.get_calibration_async(calibration)

        self.vc.set_current_callback_period(100)
        self.vc.set_voltage_callback_period(100)
        self.vc.set_power_callback_period(100)
        
        self.plot_widget_current.stop = False
        self.plot_widget_voltage.stop = False
        self.plot_widget_power.stop = False
        
    def stop(self):
        self.vc.set_current_callback_period(0)
        self.vc.set_voltage_callback_period(0)
        self.vc.set_power_callback_period(0)
        
        self.plot_widget_current.stop = True
        self.plot_widget_voltage.stop = True
        self.plot_widget_power.stop = True

    @staticmethod
    def has_name(name):
        return 'Voltage/Current Bricklet' in name 

    def get_current_value(self):
        return self.current_value
    
    def get_voltage_value(self):
        return self.voltage_value
    
    def get_power_value(self):
        return self.power_value

    def cb_current(self, current):
        self.current_value = current
        self.current_label.setText(str(current)) 
        
    def cb_voltage(self, voltage):
        self.voltage_value = voltage
        self.voltage_label.setText(str(voltage)) 
        
    def cb_power(self, power):
        self.power_value = power
        self.power_label.setText(str(power)) 
        
    def save_cal_pressed(self):
        gainmul = self.gainmul_spinbox.value()
        gaindiv = self.gaindiv_spinbox.value()
        self.vc.set_calibration(gainmul, gaindiv)
        
    def save_conf_pressed(self):
        avg = self.averaging_box.currentIndex()
        vol = self.voltage_box.currentIndex()
        cur = self.current_box.currentIndex()
        self.vc.set_configuration(avg, vol, cur)
