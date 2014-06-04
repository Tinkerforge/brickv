# -*- coding: utf-8 -*-  
"""
Analog In Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

analog_in.py: Analog In Plugin Implementation

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
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_analog_in import BrickletAnalogIn
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QSpinBox
from PyQt4.QtCore import pyqtSignal, Qt
        
class VoltageLabel(QLabel):
    def setText(self, text):
        text = "Voltage: " + text + " V"
        super(VoltageLabel, self).setText(text)
    
class AnalogIn(PluginBase):
    qtcb_voltage = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Analog In Bricklet', version, BrickletAnalogIn)
        
        self.ai = self.device
        
        self.qtcb_voltage.connect(self.cb_voltage)
        self.ai.register_callback(self.ai.CALLBACK_VOLTAGE,
                                  self.qtcb_voltage.emit) 
        
        self.voltage_label = VoltageLabel('Voltage: ')
        
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Voltage [mV]', plot_list)

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.voltage_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

        if self.version >= (2, 0, 1):
            self.combo_range = QComboBox()
            self.combo_range.addItem('Automatic', BrickletAnalogIn.RANGE_AUTOMATIC)
            if self.version >= (2, 0, 3):
                self.combo_range.addItem('0V - 3.30V', BrickletAnalogIn.RANGE_UP_TO_3V)
            self.combo_range.addItem('0V - 6.05V', BrickletAnalogIn.RANGE_UP_TO_6V)
            self.combo_range.addItem('0V - 10.32V', BrickletAnalogIn.RANGE_UP_TO_10V)
            self.combo_range.addItem('0V - 36.30V', BrickletAnalogIn.RANGE_UP_TO_36V)
            self.combo_range.addItem('0V - 45.00V', BrickletAnalogIn.RANGE_UP_TO_45V)
            self.combo_range.currentIndexChanged.connect(self.range_changed)

            layout_h1 = QHBoxLayout()
            layout_h1.addStretch()
            layout_h1.addWidget(QLabel('Range:'))
            layout_h1.addWidget(self.combo_range)

            if self.version >= (2, 0, 3):
                self.spin_average = QSpinBox()
                self.spin_average.setMinimum(0)
                self.spin_average.setMaximum(255)
                self.spin_average.setSingleStep(1)
                self.spin_average.setValue(50)
                self.spin_average.editingFinished.connect(self.spin_average_finished)

                layout_h1.addStretch()
                layout_h1.addWidget(QLabel('Average Length:'))
                layout_h1.addWidget(self.spin_average)

            layout_h1.addStretch()
            layout.addLayout(layout_h1)

    def get_range_async(self, range):
        self.combo_range.setCurrentIndex(self.combo_range.findData(range))

    def get_averaging_async(self, average):
        self.spin_average.setValue(average)

    def start(self):
        if self.version >= (2, 0, 1):
            async_call(self.ai.get_range, None, self.get_range_async, self.increase_error_count)
        if self.version >= (2, 0, 3):
            async_call(self.ai.get_averaging, None, self.get_averaging_async, self.increase_error_count)
        async_call(self.ai.get_voltage, None, self.cb_voltage, self.increase_error_count)
        async_call(self.ai.set_voltage_callback_period, 100, None, self.increase_error_count)
        
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.ai.set_voltage_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'analog_in'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogIn.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_voltage(self, voltage):
        self.current_value = voltage
        self.voltage_label.setText(str(voltage/1000.0))

    def range_changed(self, index):
        if index >= 0 and self.version >= (2, 0, 1):
            range = self.combo_range.itemData(index).toInt()[0]
            async_call(self.ai.set_range, range, None, self.increase_error_count)

    def spin_average_finished(self):
        self.ai.set_averaging(self.spin_average.value())
