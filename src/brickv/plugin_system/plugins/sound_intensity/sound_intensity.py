# -*- coding: utf-8 -*-  
"""
Sound Intensity Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

sound_intensity.py: Sound Intensity Plugin Implementation

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
from brickv.bindings.bricklet_sound_intensity import BrickletSoundIntensity
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QWidget, QLinearGradient, QBrush
from PyQt4.QtCore import pyqtSignal, Qt

import PyQt4.Qwt5 as Qwt

class TuningThermo(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.thermo = Qwt.QwtThermo(self)
        self.thermo.setOrientation(Qt.Horizontal, Qwt.QwtThermo.NoScale)
        self.thermo.setRange(0, 3200)
        
        gradient = QLinearGradient(0, 0, 300, 0)
        gradient.setColorAt(0, Qt.green)
        gradient.setColorAt(1, Qt.red)
        
        self.thermo.setFillBrush(QBrush(gradient))
        
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.thermo)

    def setValue(self, value):
        self.thermo.setValue(value)

class IntensityLabel(QLabel):
    def setText(self, text):
        text = "Intensity Value: " + text
        super(IntensityLabel, self).setText(text)
    
class SoundIntensity(PluginBase):
    qtcb_intensity = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, 'Sound Intensity Bricklet', BrickletSoundIntensity, *args)

        self.si = self.device
        
        self.qtcb_intensity.connect(self.cb_intensity)
        self.si.register_callback(self.si.CALLBACK_INTENSITY,
                                  self.qtcb_intensity.emit) 
        
        self.intensity_label = IntensityLabel()
        self.current_value = None
        self.thermo = TuningThermo()
        
#        plot_list = [['', Qt.red, self.get_current_value]]
#        self.plot_widget = PlotWidget('Intensity', plot_list)

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.intensity_label)
        layout_h.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.thermo)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addLayout(layout_h2)
        layout.addStretch()
#        layout.addWidget(self.plot_widget)
        
#    def get_current_value(self):
#        return self.current_value

    def cb_intensity(self, intensity):
        self.thermo.setValue(intensity)
#        self.current_value = intensity
        self.intensity_label.setText(str(intensity))

    def start(self):
        async_call(self.si.get_intensity, None, self.cb_intensity, self.increase_error_count)
        async_call(self.si.set_intensity_callback_period, 10, None, self.increase_error_count)
        
#        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.si.set_intensity_callback_period, 0, None, self.increase_error_count)
        
#        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'sound_intensity'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSoundIntensity.DEVICE_IDENTIFIER
