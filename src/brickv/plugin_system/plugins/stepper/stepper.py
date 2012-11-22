# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2009-2012 Olaf Lüke <olaf@tinkerforge.com>

stepper.py: Stepper Plugin implementation

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

from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from bindings.brick_stepper import BrickStepper
from async_call import async_call

from PyQt4.QtGui import QErrorMessage, QInputDialog
from PyQt4.QtCore import QTimer, Qt, pyqtSignal

from speedometer import SpeedoMeter
from threading import Thread
import time

from ui_stepper import Ui_Stepper

class Stepper(PluginBase, Ui_Stepper):
    qtcb_position_reached = pyqtSignal(int)
    qtcb_under_voltage = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Stepper Brick', version)
        
        self.setupUi(self)
     
        self.stepper = BrickStepper(uid, ipcon)
        self.device = self.stepper
     
        self.endis_all(False)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)

        self.speedometer = SpeedoMeter()
        self.vertical_layout_right.insertWidget(5, self.speedometer)
        
        self.new_value = 0
        self.update_counter = 0
        
        self.full_brake_time = 0

        self.qem = QErrorMessage(self)
        self.qem.setWindowTitle("Under Voltage")
        
        self.velocity_slider.sliderReleased.connect(self.velocity_slider_released)
        self.velocity_slider.valueChanged.connect(self.velocity_spin.setValue)
        self.velocity_spin.editingFinished.connect(self.velocity_spin_finished)
        
        self.acceleration_slider.sliderReleased.connect(self.acceleration_slider_released)
        self.acceleration_slider.valueChanged.connect(self.acceleration_spin.setValue)
        self.acceleration_spin.editingFinished.connect(self.acceleration_spin_finished)
        
        self.deceleration_slider.sliderReleased.connect(self.deceleration_slider_released)
        self.deceleration_slider.valueChanged.connect(self.deceleration_spin.setValue)
        self.deceleration_spin.editingFinished.connect(self.deceleration_spin_finished)
        
#        self.decay_slider.sliderReleased.connect(self.decay_slider_released)
#        self.decay_slider.valueChanged.connect(self.decay_spin.setValue)
#        self.decay_spin.editingFinished.connect(self.decay_spin_finished)
        
        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        self.forward_button.pressed.connect(self.forward_pressed)
        self.stop_button.pressed.connect(self.stop_pressed)
        self.full_brake_button.pressed.connect(self.full_brake_pressed)
        self.backward_button.pressed.connect(self.backward_pressed)
        self.to_button.pressed.connect(self.to_button_pressed)
        self.steps_button.pressed.connect(self.steps_button_pressed)
        self.motor_current_button.pressed.connect(self.motor_current_button_pressed)
        self.minimum_motor_voltage_button.pressed.connect(self.minimum_motor_voltage_button_pressed)
        
        self.mode_dropbox.currentIndexChanged.connect(self.mode_changed)
        
        self.qtcb_position_reached.connect(self.cb_position_reached)
        self.stepper.register_callback(self.stepper.CALLBACK_POSITION_REACHED, 
                                       self.qtcb_position_reached.emit)
        
        self.qtcb_under_voltage.connect(self.cb_under_voltage)
        self.stepper.register_callback(self.stepper.CALLBACK_UNDER_VOLTAGE, 
                                       self.qtcb_under_voltage.emit)
        
        self.update_data_async_thread = None
        
        self.ste = 0
        self.pos = 0
        self.current_velocity = 0
        self.cur = 0
        self.sv  = 0
        self.ev  = 0
        self.mv  = 0
        self.mod = 0
        
    def start(self):
        self.update_timer.start(100)
        self.update_start()
        
    def stop(self):
        self.update_timer.stop()

    def has_reset_device(self):
        return self.version >= [1, 1, 4]

    def reset_device(self):
        if self.has_reset_device():
            self.stepper.reset()

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'stepper'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickStepper.DEVICE_IDENTIFIER
    
    def cb_position_reached(self, position):
        self.position_update(position)
        self.endis_all(True)
            
    def disable_list(self, button_list):
        for button in button_list:
            button.setEnabled(False)
        
    def endis_all(self, value):
        self.forward_button.setEnabled(value)
        self.stop_button.setEnabled(value)
        self.backward_button.setEnabled(value)
        self.to_button.setEnabled(value)
        self.steps_button.setEnabled(value)
        self.full_brake_button.setEnabled(value)
        
    def mode_changed(self, index):
        try:
            self.stepper.set_step_mode(1 << index)
            self.mod = 1 << index
        except ip_connection.Error:
            return
        
    def forward_pressed(self):
        try:
            self.stepper.drive_forward()
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, self.steps_button])
        
    def backward_pressed(self):
        try:
            self.stepper.drive_backward()
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, self.steps_button])
        
    def stop_pressed(self):
        try:
            self.stepper.stop()
        except ip_connection.Error:
            return
        self.endis_all(True)
        
    def full_brake_pressed(self):
        try:
            self.stepper.full_brake()
        except ip_connection.Error:
            return
        self.endis_all(True)
        
    def to_button_pressed(self):
        drive_to = self.to_spin.value()
        try:
            self.stepper.set_target_position(drive_to)
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, 
                           self.steps_button, 
                           self.forward_button,
                           self.backward_button])
        
    def steps_button_pressed(self):
        drive_steps = self.steps_spin.value()
        try:
            self.stepper.set_steps(drive_steps)
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, 
                           self.steps_button, 
                           self.forward_button,
                           self.backward_button])
        
    def motor_current_button_pressed(self):
        qid = QInputDialog(self)
        qid.setInputMode(QInputDialog.IntInput)
        qid.setIntMinimum(0)
        qid.setIntMaximum(2500)
        qid.setIntStep(100)
        async_call(self.stepper.get_motor_current, None, qid.setIntValue, self.increase_error_count)
        qid.intValueSelected.connect(self.motor_current_selected)
        qid.setLabelText("Choose motor current in mA.")
#                         "<font color=red>Setting this too high can destroy your Motor.</font>")
        qid.open()
        
    def minimum_motor_voltage_button_pressed(self):
        qid = QInputDialog(self)
        qid.setInputMode(QInputDialog.IntInput)
        qid.setIntMinimum(0)
        qid.setIntMaximum(40000)
        qid.setIntStep(100)
        async_call(self.stepper.get_minimum_voltage, None, qid.setIntValue, self.increase_error_count)
        qid.intValueSelected.connect(self.minimum_motor_voltage_selected)
        qid.setLabelText("Choose minimum motor voltage in mV.")
        qid.open()
        
    def motor_current_selected(self, value):
        try:
            self.stepper.set_motor_current(value)
        except ip_connection.Error:
            return
        
    def minimum_motor_voltage_selected(self, value):
        try:
            self.stepper.set_minimum_voltage(value)
        except ip_connection.Error:
            return
        
    def cb_under_voltage(self, ov):
        mv_str = self.minimum_voltage_label.text()
        ov_str = "%gV"  % round(ov/1000.0, 1)
        if not self.qem.isVisible():
            self.qem.showMessage("Under Voltage: Output Voltage of " + ov_str +
                                 " is below minimum voltage of " + mv_str,
                                 "Stepper_UnderVoltage")
        
    def enable_state_changed(self, state):
        try:
            if state == Qt.Checked:
                self.endis_all(True)
                self.stepper.enable()
            elif state == Qt.Unchecked:
                self.endis_all(False)
                self.stepper.disable()
        except ip_connection.Error:
            return
        
    def stack_input_voltage_update(self, sv):
        sv_str = "%gV"  % round(sv/1000.0, 1)
        self.stack_voltage_label.setText(sv_str)
        
    def external_input_voltage_update(self, ev):
        ev_str = "%gV"  % round(ev/1000.0, 1)
        self.external_voltage_label.setText(ev_str)
        
    def minimum_voltage_update(self, mv):
        mv_str = "%gV"  % round(mv/1000.0, 1)
        self.minimum_voltage_label.setText(mv_str)
        
    def maximum_current_update(self, cur):
        cur_str = "%gA"  % round(cur/1000.0, 1)
        self.maximum_current_label.setText(cur_str)
        
    def position_update(self, pos):
        pos_str = "%d" % pos
        self.position_label.setText(pos_str)
        
    def remaining_steps_update(self, ste):
        ste_str = "%d" % ste
        self.remaining_steps_label.setText(ste_str)
        
    def mode_update(self, mod):
        if mod == 8:
            index = 3
        elif mod == 4:
            index = 2
        elif mod == 2:
            index = 1
        else:
            index = 0
            
        self.mode_dropbox.setCurrentIndex(index)
        
    def get_max_velocity_async(self, velocity):
        if not self.velocity_slider.isSliderDown():
            if velocity != self.velocity_slider.sliderPosition():
                self.velocity_slider.setSliderPosition(velocity)
                self.velocity_spin.setValue(velocity)
        
    def get_speed_ramping_async(self, ramp):
        acc, dec = ramp
        if not self.acceleration_slider.isSliderDown() and \
           not self.deceleration_slider.isSliderDown():
            if acc != self.acceleration_slider.sliderPosition():
                self.acceleration_slider.setSliderPosition(acc)
                self.acceleration_spin.setValue(acc)
            if dec != self.deceleration_slider.sliderPosition():
                self.deceleration_slider.setSliderPosition(dec)
                self.deceleration_spin.setValue(dec)
        
    def is_enabled_async(self, enabled):
        if enabled:
            if self.enable_checkbox.checkState() != Qt.Checked:
                self.endis_all(True)
                self.enable_checkbox.setCheckState(Qt.Checked)
        else:
            if self.enable_checkbox.checkState() != Qt.Unchecked:
                self.endis_all(False)
                self.enable_checkbox.setCheckState(Qt.Unchecked)
        
    def update_start(self):
        async_call(self.stepper.get_max_velocity, None, self.get_max_velocity_async, self.increase_error_count)
        async_call(self.stepper.get_speed_ramping, None, self.get_speed_ramping_async, self.increase_error_count)
        async_call(self.stepper.is_enabled, None, self.is_enabled_async, self.increase_error_count)

    def update_data(self):
        async_call(self.stepper.get_remaining_steps, None, self.remaining_steps_update, self.increase_error_count)
        async_call(self.stepper.get_current_position, None, self.position_update, self.increase_error_count)
        async_call(self.stepper.get_current_velocity, None, self.speedometer.set_velocity, self.increase_error_count)

        self.update_counter += 1
        if self.update_counter % 10 == 0:
            async_call(self.stepper.get_motor_current, None, self.maximum_current_update, self.increase_error_count)
            async_call(self.stepper.get_stack_input_voltage, None, self.stack_input_voltage_update, self.increase_error_count)
            async_call(self.stepper.get_external_input_voltage, None, self.external_input_voltage_update, self.increase_error_count)
            async_call(self.stepper.get_minimum_voltage, None, self.minimum_voltage_update, self.increase_error_count)
            async_call(self.stepper.get_step_mode, None, self.mode_update, self.increase_error_count)
        
    def velocity_slider_released(self):
        value = self.velocity_slider.value()
        self.velocity_spin.setValue(value)
        try:
            self.stepper.set_max_velocity(value)
        except ip_connection.Error:
            return
 
    def velocity_spin_finished(self):
        value = self.velocity_spin.value()
        self.velocity_slider.setValue(value)
        try:
            self.stepper.set_max_velocity(value)
        except ip_connection.Error:
            return
    
    def acceleration_slider_released(self):
        acc = self.acceleration_slider.value()
        dec = self.deceleration_slider.value()
        self.acceleration_spin.setValue(acc)
        try:
            self.stepper.set_speed_ramping(acc, dec)
        except ip_connection.Error:
            return
 
    def acceleration_spin_finished(self):
        acc = self.acceleration_spin.value()
        dec = self.deceleration_spin.value()
        self.acceleration_slider.setValue(acc)
        try:
            self.stepper.set_speed_ramping(acc, dec)
        except ip_connection.Error:
            return
            
    def deceleration_slider_released(self):
        acc = self.acceleration_slider.value()
        dec = self.deceleration_slider.value()
        self.deceleration_spin.setValue(dec)
        try:
            self.stepper.set_speed_ramping(acc, dec)
        except ip_connection.Error:
            return
 
    def deceleration_spin_finished(self):
        acc = self.acceleration_spin.value()
        dec = self.deceleration_spin.value()
        self.deceleration_slider.setValue(dec)
        try:
            self.stepper.set_speed_ramping(acc, dec)
        except ip_connection.Error:
            return

#    def decay_slider_released(self):
#        value = self.decay_slider.value()
#        self.decay_spin.setValue(value)
#        try:
#            self.stepper.set_decay(value)
#        except ip_connection.Error:
#            return
 
#    def decay_spin_finished(self):
#        value = self.decay_spin.value()
#        self.decay_slider.setValue(value)
#        try:
#            self.stepper.set_decay(value)
#        except ip_connection.Error:
#            return
