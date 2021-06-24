# -*- coding: utf-8 -*-
"""
Servo 2.0 Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

servo_v2.py: Servo Bricklet 2.0 Plugin implementation

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

import time
import random
from threading import Event

from PyQt5.QtCore import Qt, QRect, QTimer, pyqtSignal, QThread
from PyQt5.QtWidgets import QLabel, QWidget, QInputDialog, QErrorMessage, QAction
from PyQt5.QtGui import QColor, QPainter

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.servo_v2.ui_servo_v2 import Ui_ServoV2
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_servo_v2 import BrickletServoV2
from brickv.async_call import async_call
from brickv.knob_widget import KnobWidget
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.callback_emulator import CallbackEmulator

class ColorBar(QWidget):
    def __init__(self, orientation, *args):
        super().__init__(*args)
        self.orientation = orientation
        self.light = QColor(Qt.gray)
        self.dark = QColor(Qt.black)
        self.height = 100

    def paintEvent(self, _):
        painter = QPainter(self)
        self.draw_color_bar(painter, self.rect())

    def grey(self):
        self.light = QColor(Qt.gray)
        self.dark = QColor(Qt.black)
        self.update()

    def color(self):
        self.light = QColor(Qt.red)
        self.dark = QColor(Qt.green)
        self.update()

    def set_height(self, height):
        self.height = height
        self.update()

    def draw_color_bar(self, painter, rect):
        h1, s1, v1, _ = self.light.getHsv()
        h2, s2, v2, _ = self.dark.getHsv()

        painter.save()
        painter.setClipRect(rect)
        painter.setClipping(True)

        if self.orientation == Qt.Horizontal:
            num_intervalls = rect.width()
        else:
            num_intervalls = rect.height()

        section = QRect()

        num_intervalls_shown = (num_intervalls*self.height)//100
        l = list(range(num_intervalls-num_intervalls_shown, num_intervalls))
        l.reverse()
        for i in l:
            if self.orientation == Qt.Horizontal:
                section.setRect(rect.x() + i, rect.y(),
                                1, rect.height())
            else:
                section.setRect(rect.x(), rect.y() + i,
                                rect.width(), 1)

            ratio = float(i)/float(num_intervalls)
            color = QColor()
            color.setHsv(h1 + int(ratio*(h2-h1) + 0.5),
                         s1 + int(ratio*(s2-s1) + 0.5),
                         v1 + int(ratio*(v2-v1) + 0.5))

            painter.fillRect(section, color)

        painter.restore()

class PositionKnob(KnobWidget):
    def __init__(self):
        super().__init__()

        self.set_total_angle(180)
        self.set_range(-90, 90)
        self.set_knob_radius(15)
        self.set_scale_visible(False)

class ServoV2(COMCUPluginBase, Ui_ServoV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletServoV2, *args)

        self.setupUi(self)

        self.servo = self.device

        self.cbe_status = CallbackEmulator(self,
                                           self.servo.get_status,
                                           None,
                                           self.cb_status,
                                           self.increase_error_count)

        self.position_list = []
        self.velocity_list = []
        self.current_list = []
        self.enable_list = []

        self.up_cur = 0
        self.up_siv = 0
        self.up_eiv = 0
        self.up_opv = 0
        self.up_mv = 0

        self.up_ena = [0]*10
        self.up_pos = [0]*10
        self.up_vel = [0]*10
        self.up_acc = [0]*10

        self.alive = True

        for i in range(1, 11):
            label = QLabel()
            label.setText('Off')
            self.enable_list.append(label)
            self.status_grid.addWidget(label, i, 1)

        for i in range(1, 11):
            pk = PositionKnob()
            self.position_list.append(pk)
            self.status_grid.addWidget(pk, i, 2)

        for i in range(1, 11):
            cb = ColorBar(Qt.Vertical)
            self.velocity_list.append(cb)
            self.status_grid.addWidget(cb, i, 3)

        for i in range(1, 11):
            cb = ColorBar(Qt.Vertical)
            self.current_list.append(cb)
            self.status_grid.addWidget(cb, i, 4)

        self.servo_dropbox.currentIndexChanged.connect(lambda x: self.update_servo_specific())
        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)

        self.position_syncer = SliderSpinSyncer(self.position_slider,
                                                self.position_spin,
                                                self.position_changed)

        self.velocity_syncer = SliderSpinSyncer(self.velocity_slider,
                                                self.velocity_spin,
                                                self.motion_changed)

        self.acceleration_syncer = SliderSpinSyncer(self.acceleration_slider,
                                                    self.acceleration_spin,
                                                    self.motion_changed)

        self.deceleration_syncer = SliderSpinSyncer(self.deceleration_slider,
                                                    self.deceleration_spin,
                                                    self.motion_changed)

        self.period_syncer = SliderSpinSyncer(self.period_slider,
                                              self.period_spin,
                                              self.period_changed)

        self.pulse_width_min_spin.editingFinished.connect(self.pulse_width_spin_finished)
        self.pulse_width_max_spin.editingFinished.connect(self.pulse_width_spin_finished)
        self.degree_min_spin.editingFinished.connect(self.degree_spin_finished)
        self.degree_max_spin.editingFinished.connect(self.degree_spin_finished)

    def start(self):
        self.cbe_status.set_period(100)
        self.update_servo_specific()

    def stop(self):
        self.cbe_status.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletServoV2.DEVICE_IDENTIFIER

    def get_period_async(self, period):
        self.period_spin.blockSignals(True)
        self.period_spin.setValue(period)
        self.period_spin.blockSignals(False)

        self.period_slider.blockSignals(True)
        self.period_slider.setValue(period)
        self.period_slider.blockSignals(False)

    def get_enabled_async(self, enabled):
        self.enable_checkbox.blockSignals(True)
        self.enable_checkbox.setChecked(enabled)
        self.enable_checkbox.blockSignals(False)

    def get_position_async(self, position):
        self.position_spin.blockSignals(True)
        self.position_spin.setValue(position)
        self.position_spin.blockSignals(False)

        self.position_slider.blockSignals(True)
        self.position_slider.setValue(position)
        self.position_slider.blockSignals(False)

    def get_motion_configuration_async(self, motion):
        self.velocity_spin.blockSignals(True)
        self.velocity_spin.setValue(motion.velocity)
        self.velocity_spin.blockSignals(False)
        self.velocity_slider.blockSignals(True)
        self.velocity_slider.setValue(motion.velocity)
        self.velocity_slider.blockSignals(False)

        self.acceleration_spin.blockSignals(True)
        self.acceleration_spin.setValue(motion.acceleration)
        self.acceleration_spin.blockSignals(False)
        self.acceleration_slider.blockSignals(True)
        self.acceleration_slider.setValue(motion.acceleration)
        self.acceleration_slider.blockSignals(False)

        self.deceleration_spin.blockSignals(True)
        self.deceleration_spin.setValue(motion.deceleration)
        self.deceleration_spin.blockSignals(False)
        self.deceleration_slider.blockSignals(True)
        self.deceleration_slider.setValue(motion.deceleration)
        self.deceleration_slider.blockSignals(False)

    def get_degree_async(self, servo, degree_min, degree_max):
        self.degree_min_spin.blockSignals(True)
        self.degree_min_spin.setValue(degree_min)
        self.degree_min_spin.blockSignals(False)
        self.degree_max_spin.blockSignals(True)
        self.degree_max_spin.setValue(degree_max)
        self.degree_max_spin.blockSignals(False)

        self.position_slider.setMinimum(degree_min)
        self.position_slider.setMaximum(degree_max)
        self.position_spin.setMinimum(degree_min)
        self.position_spin.setMaximum(degree_max)

        self.position_list[servo].set_total_angle((degree_max - degree_min) / 100)
        self.position_list[servo].set_range(degree_min / 100, degree_max / 100)

    def get_pulse_width_async(self, pulse_width_min, pulse_width_max):
        self.pulse_width_min_spin.blockSignals(True)
        self.pulse_width_min_spin.setValue(pulse_width_min)
        self.pulse_width_min_spin.blockSignals(False)
        self.pulse_width_max_spin.blockSignals(True)
        self.pulse_width_max_spin.setValue(pulse_width_max)
        self.pulse_width_max_spin.blockSignals(False)

    def update_servo_specific(self):
        servo = self.selected_servo()

        if servo == 0xFFFF:
            self.enable_checkbox.setChecked(False)
            return

        async_call(self.servo.get_enabled, servo, self.get_enabled_async, self.increase_error_count)
        async_call(self.servo.get_position, servo, self.get_position_async, self.increase_error_count)
        async_call(self.servo.get_motion_configuration, servo, self.get_motion_configuration_async, self.increase_error_count)
        async_call(self.servo.get_period, servo, self.get_period_async, self.increase_error_count)
        async_call(self.servo.get_degree, servo, self.get_degree_async, self.increase_error_count,
                   pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)
        async_call(self.servo.get_pulse_width, servo, self.get_pulse_width_async, self.increase_error_count,
                   expand_result_tuple_for_callback=True)

    def servo_current_update(self, value):
        self.current_label.setText(str(value) + "mA")

    def input_voltage_update(self, sv):
        sv_str = "%gV" % round(sv / 1000.0, 1)
        self.input_voltage_label.setText(sv_str)

    def position_update(self, servo, position):
        self.position_list[servo].set_value(position / 100)

    def velocity_update(self, servo, velocity):
        self.velocity_list[servo].set_height(velocity * 100 // 0xFFFF)

    def current_update(self, servo, current):
        self.current_list[servo].set_height(min(100, current * 100 // 200))

    def enable_update(self, servo, enabled):
        if enabled:
            if self.enable_list[servo].text().replace('&', '') != 'On':
                self.enable_list[servo].setText('On')
                self.velocity_list[servo].color()
                self.current_list[servo].color()
        else:
            if self.enable_list[servo].text().replace('&', '') != 'Off':
                self.enable_list[servo].setText('Off')
                self.velocity_list[servo].grey()
                self.current_list[servo].grey()

    def selected_servo(self):
        try:
            return int(self.servo_dropbox.currentText()[-1:])
        except:
            return 0xFFFF

    def enable_state_changed(self, state):
        try:
            self.servo.set_enable(self.selected_servo(), state == Qt.Checked)
        except ip_connection.Error:
            return

    def position_changed(self, value):
        try: 
            self.servo.set_position(self.selected_servo(), value)
        except ip_connection.Error:
            return

    def motion_changed(self, _):
        try:
            self.servo.set_motion_configuration(self.selected_servo(), self.velocity_spin.value(), self.acceleration_spin.value(), self.deceleration_spin.value())
        except ip_connection.Error:
            return

    def period_changed(self, value):
        try:
            self.servo.set_period(self.selected_servo(), value)
        except ip_connection.Error:
            return

    def pulse_width_spin_finished(self):
        try:
            self.servo.set_pulse_width(self.selected_servo(),
                                       self.pulse_width_min_spin.value(),
                                       self.pulse_width_max_spin.value())
        except ip_connection.Error:
            return

    def degree_spin_finished(self):
        degree_min = self.degree_min_spin.value()
        degree_max = self.degree_max_spin.value()
        servo = self.selected_servo()

        self.position_slider.setMinimum(degree_min)
        self.position_slider.setMaximum(degree_max)
        self.position_spin.setMinimum(degree_min)
        self.position_spin.setMaximum(degree_max)

        if servo == 0xFFFF:
            for i in range(7):
                self.position_list[i].set_total_angle((degree_max - degree_min) / 100)
                self.position_list[i].set_range(degree_min / 100, degree_max / 100)
        else:
            self.position_list[servo].set_total_angle((degree_max - degree_min) / 100)
            self.position_list[servo].set_range(degree_min / 100, degree_max / 100)

        try:
            self.servo.set_degree(servo, degree_min, degree_max)
        except ip_connection.Error:
            return

    def cb_status(self, status):
        servo = self.selected_servo()
        self.input_voltage_update(status.input_voltage)
        if servo == 0xFFFF:
            self.servo_current_update(sum(status.current))
        else:
            self.servo_current_update(status.current[servo])
        for servo in range(10):
            self.enable_update(servo, status.enabled[servo])
            self.position_update(servo, status.current_position[servo])
            self.velocity_update(servo, status.current_velocity[servo])
            self.current_update(servo, status.current[servo])
