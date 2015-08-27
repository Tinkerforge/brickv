# -*- coding: utf-8 -*-
"""
UV Light Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

uv_light.py: UV Light Bricklet Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPainter, \
                        QColor, QBrush, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_uv_light import BrickletUVLight
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class UVLabel(QLabel):
    def setText(self, text):
        text = u"UV Index: " + text
        super(UVLabel, self).setText(text)
        
class IRLabel(QLabel):
    def setText(self, text):
        text = u"IR Value: " + text + u" W/m²"
        super(IRLabel, self).setText(text)
        
class AmbLabel(QLabel):
    def setText(self, text):
        text = u"Illuminance: " + text + u" lx (Lux)"
        super(AmbLabel, self).setText(text)

class UVLight(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletUVLight, *args)

        self.uv_light = self.device

        self.cbe_uv_index = CallbackEmulator(self.uv_light.get_uv_index,
                                             self.cb_uv_index,
                                             self.increase_error_count)
        self.cbe_ir_value = CallbackEmulator(self.uv_light.get_ir_value,
                                             self.cb_ir_value,
                                             self.increase_error_count)
        self.cbe_illuminance = CallbackEmulator(self.uv_light.get_illuminance,
                                                self.cb_illuminance,
                                                self.increase_error_count)

        self.uv_label = UVLabel('UV Index: ')
        self.ir_label = IRLabel('IR Value: ')
        self.amb_label = AmbLabel('Illuminance: ')

        self.current_uv_index = None
        self.current_ir_value = None
        self.current_illuminance = None
        
        plot_list = [['', Qt.red, self.get_current_uv_index]]
        self.plot_widget_uv = PlotWidget('UV Index', plot_list)

        plot_list = [['', Qt.red, self.get_current_ir_value]]
        self.plot_widget_ir = PlotWidget('IR Value [W/m²]', plot_list)

        plot_list = [['', Qt.red, self.get_current_illuminance]]
        self.plot_widget_amb = PlotWidget('Illuminance [lx]', plot_list)
        
        layout_uv = QVBoxLayout()
        layout_uv.addStretch()
        layout_uv.addWidget(self.uv_label)
        layout_uv.addWidget(self.plot_widget_uv)
        layout_uv.addStretch()
        
        layout_ir = QVBoxLayout()
        layout_ir.addStretch()
        layout_ir.addWidget(self.ir_label)
        layout_ir.addWidget(self.plot_widget_ir)
        layout_ir.addStretch()
        
        layout_amb = QVBoxLayout()
        layout_amb.addStretch()
        layout_amb.addWidget(self.amb_label)
        layout_amb.addWidget(self.plot_widget_amb)
        layout_amb.addStretch()

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addLayout(layout_uv)
        layout_h.addLayout(layout_ir)
        layout_h.addLayout(layout_amb)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)

    def start(self):
        async_call(self.uv_light.get_uv_index, None, self.cb_uv_index, self.increase_error_count)
        async_call(self.uv_light.get_ir_value, None, self.cb_ir_value, self.increase_error_count)
        async_call(self.uv_light.get_illuminance, None, self.cb_illuminance, self.increase_error_count)
        self.cbe_uv_index.set_period(100)
        self.cbe_ir_value.set_period(100)
        self.cbe_illuminance.set_period(100)

        self.plot_widget_uv.stop = False
        self.plot_widget_ir.stop = False
        self.plot_widget_amb.stop = False

    def stop(self):
        self.cbe_uv_index.set_period(0)
        self.cbe_ir_value.set_period(0)
        self.cbe_illuminance.set_period(0)

        self.plot_widget_uv.stop = True
        self.plot_widget_ir.stop = True
        self.plot_widget_amb.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'uv_light'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletUVLight.DEVICE_IDENTIFIER

    def get_current_uv_index(self):
        return self.current_uv_index
    
    def get_current_ir_value(self):
        return self.current_ir_value
    
    def get_current_illuminance(self):
        return self.current_illuminance

    def cb_uv_index(self, uv_index):
        self.current_uv_index = round(uv_index/100.0, 1)        
        self.uv_label.setText(unicode(self.current_uv_index))
        
    def cb_ir_value(self, ir_value):
        self.current_ir_value = round(ir_value/1000.0, 1)        
        self.ir_label.setText(unicode(self.current_ir_value))
        
    def cb_illuminance(self, illuminance):
        self.current_illuminance = illuminance
        self.amb_label.setText(unicode(self.current_illuminance))
