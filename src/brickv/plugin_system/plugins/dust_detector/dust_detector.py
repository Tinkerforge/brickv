# -*- coding: utf-8 -*-  
"""
Dust Detector Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

dust_detector.py: Dust Detector Plugin Implementation

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_dust_detector import BrickletDustDetector
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class DustDensityLabel(QLabel):
    def setText(self, text):
        text = u'Dust Density: ' + text + u'µg/m³'
        super(DustDensityLabel, self).setText(text)
    
class DustDetector(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletDustDetector, *args)

        self.dust_detector = self.device

        self.cbe_dust_density = CallbackEmulator(self.dust_detector.get_dust_density,
                                                 self.cb_dust_density,
                                                 self.increase_error_count)

        self.dust_density_label = DustDensityLabel()
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget(u'Dust Density [µg/m³]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.dust_density_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        
    def get_current_value(self):
        return self.current_value

    def cb_dust_density(self, dust_density):
        self.current_value = dust_density
        self.dust_density_label.setText(str(dust_density))

    def start(self):
        async_call(self.dust_detector.get_dust_density, None, self.cb_dust_density, self.increase_error_count)
        self.cbe_dust_density.set_period(100)
        
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_dust_density.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'dust_detector'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDustDetector.DEVICE_IDENTIFIER
