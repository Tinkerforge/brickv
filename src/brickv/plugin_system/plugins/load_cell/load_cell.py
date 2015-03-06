# -*- coding: utf-8 -*-  
"""
Load Cell Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

load_cell.py: Load Cell Plugin Implementation

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
from brickv.bindings.bricklet_load_cell import BrickletLoadCell
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class WeightLabel(QLabel):
    def setText(self, text):
        text = "Weight: " + text + " g"
        super(WeightLabel, self).setText(text)
    
class LoadCell(PluginBase):
    qtcb_weight = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletLoadCell, *args)
        
        self.lc = self.device
        
        self.qtcb_weight.connect(self.cb_weight)
        self.lc.register_callback(self.lc.CALLBACK_WEIGHT,
                                   self.qtcb_weight.emit) 
        
        self.weight_label = WeightLabel()
        
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Weight [g]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.weight_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.lc.get_weight, None, self.cb_weight, self.increase_error_count)
        async_call(self.lc.set_weight_callback_period, 100, None, self.increase_error_count)
        
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.lc.set_weight_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'load_cell'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLoadCell.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_weight(self, weight):
        self.current_value = weight
        self.weight_label.setText(str(weight))
