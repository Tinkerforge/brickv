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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_motorized_poti import BrickletMotorizedPoti
from brickv.plot_widget import PlotWidget, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MotorPositionLabel(FixedSizeLabel):
    def setText(self, text):
        text = "Motor Position: " + text
        super(MotorPositionLabel, self).setText(text)

class MotorizedPoti(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletMotorizedPoti, *args)
        
        self.mp = self.device

        self.cbe_position = CallbackEmulator(self.mp.get_position,
                                             self.cb_position,
                                             self.increase_error_count)

        self.current_position = None

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setMinimumWidth(200)

        plots = [('Position', Qt.red, lambda: self.current_position, str)]
        self.plot_widget = PlotWidget('Position', plots, extra_key_widgets=[self.slider],
                                      curve_motion_granularity=40, update_interval=0.025)

        self.motor_slider = QSlider(Qt.Horizontal)
        self.motor_slider.setRange(0, 100)
        self.motor_slider.sliderReleased.connect(self.motor_slider_released)
        self.motor_slider.sliderMoved.connect(self.motor_slider_moved)
        self.motor_enable = QCheckBox("Enable Motor")
        self.motor_enable.stateChanged.connect(self.motor_enable_changed)

        self.motor_position_label = MotorPositionLabel('Motor Position: ')

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.motor_position_label)
        hlayout.addWidget(self.motor_slider)
        hlayout.addWidget(self.motor_enable)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

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

    def cb_position(self, position):
        self.current_position = position
        self.slider.setValue(position)
        
    def cb_motor_position(self, motor_position):
        self.motor_slider.setValue(motor_position.position)
        self.motor_slider_moved(motor_position.position)
        
    def cb_is_motor_enabled(self, enabled):
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
        