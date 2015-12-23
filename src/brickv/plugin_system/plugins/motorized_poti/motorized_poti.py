# -*- coding: utf-8 -*-  
"""
Motorized Poti Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

motorized_poti.py: Motorized Poti Plugin implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_motorized_poti import BrickletMotorizedPoti
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MotorPositionLabel(QLabel):
    def setText(self, text):
        text = "Motor Position: " + text
        super(MotorPositionLabel, self).setText(text)

class PositionLabel(QLabel):
    def setText(self, text):
        text = "Current Position: " + text
        super(PositionLabel, self).setText(text)

class MotorizedPoti(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletMotorizedPoti, *args)
        
        self.mp = self.device

        self.cbe_position = CallbackEmulator(self.mp.get_position,
                                             self.cb_position,
                                             self.increase_error_count)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        
        self.motor_slider = QSlider(Qt.Horizontal)
        self.motor_slider.setRange(0, 100)
        self.motor_slider.sliderReleased.connect(self.motor_slider_released)
        self.motor_slider.sliderMoved.connect(self.motor_slider_moved)
        self.motor_enable = QCheckBox("enable")
        self.motor_enable.stateChanged.connect(self.motor_enable_changed)
        
        self.position_label = PositionLabel('Current Position: ')
        self.motor_position_label = MotorPositionLabel('Motor Position: ')
        
        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Position', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.position_label)
        layout_h.addWidget(self.slider)
        layout_h.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.motor_position_label)
        layout_h2.addWidget(self.motor_slider)
        layout_h2.addWidget(self.motor_enable)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)
        
    def start(self):
        async_call(self.mp.get_position, None, self.cb_position, self.increase_error_count)
        async_call(self.mp.get_motor_position, None, self.cb_motor_position, self.increase_error_count)
        async_call(self.mp.is_motor_enabled, None, self.cb_is_motor_enabled, self.increase_error_count)

        self.cbe_position.set_period(25)
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_position.set_period(0)
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'motorized_poti'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMotorizedPoti.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_position(self, position):
        self.current_value = position
        self.slider.setValue(position)
        self.position_label.setText(str(position))
        
    def cb_motor_position(self, motor_position):
        print motor_position
        self.motor_slider.setValue(motor_position.position)
        self.motor_slider_moved(motor_position.position)
        
    def cb_is_motor_enabled(self, enabled):
        print enabled
        self.motor_enable.setChecked(enabled)
        
    def motor_slider_moved(self, position):
        self.motor_position_label.setText(str(position))

    def motor_slider_released(self):
        self.mp.set_motor_position(self.motor_slider.value(), False)
        
    def motor_enable_changed(self, state):
        if self.motor_enable.isChecked():
            self.mp.enable_motor()
        else:
            self.mp.disable_motor()
        