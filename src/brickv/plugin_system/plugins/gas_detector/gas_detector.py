# -*- coding: utf-8 -*-  
"""
Gas Detector Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

gas_detector.py: Gas Detector Plugin Implementation

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
from brickv.bindings.bricklet_gas_detector import BrickletGasDetector
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class GasDetectorLabel(QLabel):
    def setText(self, text):
        text = "Value: " + text
        super(GasDetectorLabel, self).setText(text)
    
class GasDetector(PluginBase):
    qtcb_value = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, 'Gas Detector Bricklet', BrickletGasDetector, *args)

        self.gas_detector = self.device
        
        self.qtcb_value.connect(self.cb_value)
        self.gas_detector.register_callback(self.gas_detector.CALLBACK_VALUE,
                                            self.qtcb_value.emit) 
        
        self.gas_detector_label = GasDetectorLabel()
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Value', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.gas_detector_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        
        
    def get_current_value(self):
        return self.current_value

    def cb_value(self, value):
        print value
        self.current_value = value
        self.gas_detector_label.setText(str(value))

    def start(self):
        async_call(self.gas_detector.get_value, None, self.cb_value, self.increase_error_count)
        async_call(self.gas_detector.set_value_callback_period, 100, None, self.increase_error_count)
        
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.gas_detector.set_value_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'gas_detector'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletGasDetector.DEVICE_IDENTIFIER
