# -*- coding: utf-8 -*-
"""
Motorized LinearPoti Plugin
Copyright (C) 2015-2017 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

motorized_linear_poti.py: Motorized Linear Poti Plugin implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QCheckBox, QFrame, QComboBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_motorized_linear_poti import BrickletMotorizedLinearPoti
from brickv.plot_widget import PlotWidget, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MotorPositionLabel(FixedSizeLabel):
    def setText(self, text):
        text = "Motor Target Position: " + text
        super(MotorPositionLabel, self).setText(text)

class MotorizedLinearPoti(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(self, BrickletMotorizedLinearPoti, *args)

        self.mp = self.device

        self.cbe_position = CallbackEmulator(self.mp.get_position,
                                             self.cb_position,
                                             self.increase_error_count)

        self.current_position = None

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setMinimumWidth(200)
        self.slider.setEnabled(False)

        plots = [('Potentiometer Position', Qt.red, lambda: self.current_position, str)]
        self.plot_widget = PlotWidget('Position', plots, extra_key_widgets=[self.slider],
                                      curve_motion_granularity=40, update_interval=0.025)

        self.motor_slider = QSlider(Qt.Horizontal)
        self.motor_slider.setRange(0, 100)
        self.motor_slider.valueChanged.connect(self.motor_slider_value_changed)
        self.motor_hold_position = QCheckBox("Hold Position")
        self.motor_drive_mode = QComboBox()
        self.motor_drive_mode.addItem('Fast')
        self.motor_drive_mode.addItem('Smooth')

        def get_motor_slider_value():
            return self.motor_slider.value()

        self.motor_hold_position.stateChanged.connect(lambda x: self.motor_slider_value_changed(get_motor_slider_value()))
        self.motor_drive_mode.currentIndexChanged.connect(lambda x: self.motor_slider_value_changed(get_motor_slider_value()))

        self.motor_position_label = MotorPositionLabel('Motor Target Position:')

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.motor_position_label)
        hlayout.addWidget(self.motor_slider)
        hlayout.addWidget(self.motor_drive_mode)
        hlayout.addWidget(self.motor_hold_position)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.mp.get_position, None, self.cb_position, self.increase_error_count)
        async_call(self.mp.get_motor_position, None, self.cb_motor_position, self.increase_error_count)

        self.cbe_position.set_period(25)
        self.plot_widget.stop = False

    def stop(self):
        self.cbe_position.set_period(0)
        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMotorizedLinearPoti.DEVICE_IDENTIFIER

    def cb_position(self, position):
        self.current_position = position
        self.slider.setValue(position)

    def cb_motor_position(self, motor):
        self.motor_slider.blockSignals(True)
        self.motor_hold_position.blockSignals(True)
        self.motor_drive_mode.blockSignals(True)

        self.motor_hold_position.setChecked(motor.hold_position)
        self.motor_drive_mode.setCurrentIndex(motor.drive_mode)
        self.motor_position_label.setText(str(motor.position))
        self.motor_slider.setValue(motor.position)

        self.motor_slider.blockSignals(False)
        self.motor_hold_position.blockSignals(False)
        self.motor_drive_mode.blockSignals(False)


    def motor_slider_value_changed(self, position):
        self.motor_position_label.setText(str(position))
        self.mp.set_motor_position(self.motor_slider.value(), self.motor_drive_mode.currentIndex(), self.motor_hold_position.isChecked())
