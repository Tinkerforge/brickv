# -*- coding: utf-8 -*-
"""
Rotary Poti Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

poti.py: Rotary Poti Plugin implementation

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
from brickv.knob_widget import KnobWidget
from brickv.bindings.bricklet_rotary_poti import BrickletRotaryPoti
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class PositionLabel(QLabel):
    def setText(self, text):
        text = "Position: " + text + " degree"
        super(PositionLabel, self).setText(text)

class RotaryPoti(PluginBase):
    qtcb_position = pyqtSignal(int)

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRotaryPoti, *args)

        self.rp = self.device

        self.qtcb_position.connect(self.cb_position)
        self.rp.register_callback(self.rp.CALLBACK_POSITION,
                                  self.qtcb_position.emit)

        self.position_knob = KnobWidget(self)
        self.position_knob.setFocusPolicy(Qt.NoFocus)
        self.position_knob.set_total_angle(300)
        self.position_knob.set_range(-150, 150)
        self.position_knob.set_scale(30, 3)
        self.position_knob.set_knob_radius(25)

        self.position_label = PositionLabel('Position: ')

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Position', plot_list)

        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.position_label)
        layout_h1.addStretch()

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.position_knob)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.rp.get_position, None, self.cb_position, self.increase_error_count)
        async_call(self.rp.set_position_callback_period, 20, None, self.increase_error_count)

        self.plot_widget.stop = False

    def stop(self):
        async_call(self.rp.set_position_callback_period, 0, None, self.increase_error_count)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'rotary_poti'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRotaryPoti.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_position(self, position):
        self.current_value = position
        self.position_knob.set_value(position)
        self.position_label.setText(str(position))
