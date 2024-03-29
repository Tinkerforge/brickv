# -*- coding: utf-8 -*-
"""
Ambient Light Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

ambient_light.py: Ambient Light Bricklet Plugin Implementation

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QFrame
from PyQt5.QtGui import QPainter, QColor, QBrush

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_ambient_light import BrickletAmbientLight
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator
from brickv.color_frame import ColorFrame

class AmbientLight(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletAmbientLight, *args)

        self.al = self.device

        self.cbe_illuminance = CallbackEmulator(self,
                                                self.al.get_illuminance,
                                                None,
                                                self.cb_illuminance,
                                                self.increase_error_count)

        self.alf = ColorFrame(25, 25, QColor(128, 128, 128))

        self.current_illuminance = CurveValueWrapper() # float, lx

        plots = [('Illuminance', Qt.red, self.current_illuminance, '{} lx (Lux)'.format)]
        self.plot_widget = PlotWidget('Illuminance [lx]', plots, extra_key_widgets=[self.alf], y_resolution=0.1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        self.cbe_illuminance.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_illuminance.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAmbientLight.DEVICE_IDENTIFIER

    def cb_illuminance(self, illuminance):
        self.current_illuminance.value = illuminance / 10.0

        value = illuminance * 255 // 9000
        self.alf.set_color(QColor(value, value, value))
