# -*- coding: utf-8 -*-
"""
Joystick 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

joystick_v2.py: Joystick 2.0 Plugin implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from PyQt5.QtGui import QPainter, QBrush

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_joystick_v2 import BrickletJoystickV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class JoystickFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.x = 0
        self.y = 0
        self.pressed = False

    def set_pressed(self, pressed):
        self.pressed = pressed
        self.repaint()

    def set_position(self, x, y):
        self.x = x + 110
        self.y = 110 - y
        self.repaint()

    def paintEvent(self, _event):
        qp = QPainter(self)
        if self.pressed:
            qp.setBrush(QBrush(Qt.red))
        else:
            qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.red)
        qp.drawLine(110, 10, 110, 210)
        qp.drawLine(10, 110, 210, 110)
        qp.drawEllipse(self.x-5, self.y-5, 10, 10)

class JoystickV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletJoystickV2, *args)

        self.js = self.device

        self.cbe_position = CallbackEmulator(self.js.get_position,
                                             None,
                                             self.cb_position,
                                             self.increase_error_count,
                                             expand_result_tuple_for_callback=True)

        self.cbe_pressed = CallbackEmulator(self.js.is_pressed,
                                            None,
                                            self.cb_pressed,
                                            self.increase_error_count)

        self.joystick_frame = JoystickFrame(self)
        self.joystick_frame.setMinimumSize(220, 220)
        self.joystick_frame.setMaximumSize(220, 220)
        self.joystick_frame.set_position(0, 0)

        self.calibrate_button = QPushButton('Calibrate Zero')
        self.calibrate_button.clicked.connect(self.calibrate_clicked)

        self.current_x = CurveValueWrapper()
        self.current_y = CurveValueWrapper()

        plots = [('X', Qt.darkGreen, self.current_x, str),
                 ('Y', Qt.blue, self.current_y, str)]
        self.plot_widget = PlotWidget('Position', plots, update_interval=0.025, y_resolution=1.0)

        vlayout = QVBoxLayout()
        vlayout.addStretch()
        vlayout.addWidget(self.joystick_frame)
        vlayout.addWidget(self.calibrate_button)
        vlayout.addStretch()

        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addLayout(vlayout)

    def start(self):
        self.cbe_position.set_period(50)
        self.cbe_pressed.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_position.set_period(0)
        self.cbe_pressed.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletJoystickV2.DEVICE_IDENTIFIER

    def calibrate_clicked(self):
        try:
            self.js.calibrate()
        except ip_connection.Error:
            return

    def cb_position(self, x, y):
        self.current_x.value = x
        self.current_y.value = y
        self.joystick_frame.set_position(x, y)

    def cb_pressed(self, pressed):
        self.joystick_frame.set_pressed(pressed)
