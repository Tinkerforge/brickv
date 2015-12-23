# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2005 Olaf Lüke <olaf@tinkerforge.com>

silent_stepper.py: Silent Stepper Brick Plugin implementation

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

from PyQt4.QtCore import QTimer, Qt, pyqtSignal
from PyQt4.QtGui import QErrorMessage, QInputDialog, QAction

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.stepper.speedometer import SpeedoMeter
from brickv.plugin_system.plugins.silent_stepper.ui_silent_stepper import Ui_SilentStepper
from brickv.bindings import ip_connection
from brickv.bindings.brick_silent_stepper import BrickSilentStepper
from brickv.async_call import async_call
from brickv.slider_spin_syncer import SliderSpinSyncer

class SilentStepper(PluginBase, Ui_SilentStepper):
    qtcb_position_reached = pyqtSignal(int)
    qtcb_under_voltage = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, BrickSilentStepper, *args)

        self.setupUi(self)
     
        self.silent_stepper = self.device
     
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

        self.velocity_syncer = SliderSpinSyncer(self.velocity_slider,
                                                self.velocity_spin,
                                                self.velocity_changed)

        self.acceleration_syncer = SliderSpinSyncer(self.acceleration_slider,
                                                    self.acceleration_spin,
                                                    self.acceleration_changed)

        self.deceleration_syncer = SliderSpinSyncer(self.deceleration_slider,
                                                    self.deceleration_spin,
                                                    self.deceleration_changed)

#        self.decay_syncer = SliderSpinSyncer(self.decay_slider,
#                                             self.decay_spin,
#                                             self.decay_changed)

        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        self.forward_button.clicked.connect(self.forward_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)
        self.full_brake_button.clicked.connect(self.full_brake_clicked)
        self.backward_button.clicked.connect(self.backward_clicked)
        self.to_button.clicked.connect(self.to_button_clicked)
        self.steps_button.clicked.connect(self.steps_button_clicked)
        self.motor_current_button.clicked.connect(self.motor_current_button_clicked)
        self.minimum_motor_voltage_button.clicked.connect(self.minimum_motor_voltage_button_clicked)
        
        self.mode_dropbox.currentIndexChanged.connect(self.mode_changed)
        
        self.qtcb_position_reached.connect(self.cb_position_reached)
        self.silent_stepper.register_callback(self.silent_stepper.CALLBACK_POSITION_REACHED, 
                                              self.qtcb_position_reached.emit)
        
        self.qtcb_under_voltage.connect(self.cb_under_voltage)
        self.silent_stepper.register_callback(self.silent_stepper.CALLBACK_UNDER_VOLTAGE, 
                                              self.qtcb_under_voltage.emit)

        self.ste = 0
        self.pos = 0
        self.current_velocity = 0
        self.cur = 0
        self.sv  = 0
        self.ev  = 0
        self.mv  = 0
        self.mod = 0

        if self.firmware_version >= (1, 1, 4):
            reset = QAction('Reset', self)
            reset.triggered.connect(lambda: self.silent_stepper.reset())
            self.set_actions(reset)
        
    def start(self):
        self.update_timer.start(100)
        self.update_start()
        
    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    def get_url_part(self):
        return 'silent_stepper'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickSilentStepper.DEVICE_IDENTIFIER
    
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
            self.silent_stepper.set_step_mode(1 << index)
            self.mod = 1 << index
        except ip_connection.Error:
            return
        
    def forward_clicked(self):
        try:
            self.silent_stepper.drive_forward()
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, self.steps_button])
        
    def backward_clicked(self):
        try:
            self.silent_stepper.drive_backward()
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, self.steps_button])
        
    def stop_clicked(self):
        try:
            self.silent_stepper.stop()
        except ip_connection.Error:
            return
        self.endis_all(True)
        
    def full_brake_clicked(self):
        try:
            self.silent_stepper.full_brake()
        except ip_connection.Error:
            return
        self.endis_all(True)
        
    def to_button_clicked(self):
        drive_to = self.to_spin.value()
        try:
            self.silent_stepper.set_target_position(drive_to)
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, 
                           self.steps_button, 
                           self.forward_button,
                           self.backward_button])
        
    def steps_button_clicked(self):
        drive_steps = self.steps_spin.value()
        try:
            self.silent_stepper.set_steps(drive_steps)
        except ip_connection.Error:
            return
        self.disable_list([self.to_button, 
                           self.steps_button, 
                           self.forward_button,
                           self.backward_button])
        
    def motor_current_button_clicked(self):
        qid = QInputDialog(self)
        qid.setInputMode(QInputDialog.IntInput)
        qid.setIntMinimum(0)
        qid.setIntMaximum(2500)
        qid.setIntStep(100)
        async_call(self.silent_stepper.get_motor_current, None, qid.setIntValue, self.increase_error_count)
        qid.intValueSelected.connect(self.motor_current_selected)
        qid.setLabelText("Choose motor current in mA.")
#                         "<font color=red>Setting this too high can destroy your Motor.</font>")
        qid.open()
        
    def minimum_motor_voltage_button_clicked(self):
        qid = QInputDialog(self)
        qid.setInputMode(QInputDialog.IntInput)
        qid.setIntMinimum(0)
        qid.setIntMaximum(40000)
        qid.setIntStep(100)
        async_call(self.silent_stepper.get_minimum_voltage, None, qid.setIntValue, self.increase_error_count)
        qid.intValueSelected.connect(self.minimum_motor_voltage_selected)
        qid.setLabelText("Choose minimum motor voltage in mV.")
        qid.open()
        
    def motor_current_selected(self, value):
        try:
            self.silent_stepper.set_motor_current(value)
        except ip_connection.Error:
            return
        
    def minimum_motor_voltage_selected(self, value):
        try:
            self.silent_stepper.set_minimum_voltage(value)
        except ip_connection.Error:
            return
        
    def cb_under_voltage(self, ov):
        mv_str = self.minimum_voltage_label.text()
        ov_str = "%gV"  % round(ov/1000.0, 1)
        if not self.qem.isVisible():
            self.qem.showMessage("Under Voltage: Output Voltage of " + ov_str +
                                 " is below minimum voltage of " + mv_str,
                                 "SilentStepper_UnderVoltage")
        
    def enable_state_changed(self, state):
        try:
            if state == Qt.Checked:
                self.endis_all(True)
                self.silent_stepper.enable()
            elif state == Qt.Unchecked:
                self.endis_all(False)
                self.silent_stepper.disable()
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
            if not self.enable_checkbox.isChecked():
                self.endis_all(True)
                self.enable_checkbox.setChecked(True)
        else:
            if self.enable_checkbox.isChecked():
                self.endis_all(False)
                self.enable_checkbox.setChecked(False)
        
    def update_start(self):
        async_call(self.silent_stepper.get_max_velocity, None, self.get_max_velocity_async, self.increase_error_count)
        async_call(self.silent_stepper.get_speed_ramping, None, self.get_speed_ramping_async, self.increase_error_count)
        async_call(self.silent_stepper.is_enabled, None, self.is_enabled_async, self.increase_error_count)

    def update_data(self):
        async_call(self.silent_stepper.get_remaining_steps, None, self.remaining_steps_update, self.increase_error_count)
        async_call(self.silent_stepper.get_current_position, None, self.position_update, self.increase_error_count)
        async_call(self.silent_stepper.get_current_velocity, None, self.speedometer.set_velocity, self.increase_error_count)

        self.update_counter += 1
        if self.update_counter % 10 == 0:
            async_call(self.silent_stepper.get_motor_current, None, self.maximum_current_update, self.increase_error_count)
            async_call(self.silent_stepper.get_stack_input_voltage, None, self.stack_input_voltage_update, self.increase_error_count)
            async_call(self.silent_stepper.get_external_input_voltage, None, self.external_input_voltage_update, self.increase_error_count)
            async_call(self.silent_stepper.get_minimum_voltage, None, self.minimum_voltage_update, self.increase_error_count)
            async_call(self.silent_stepper.get_step_mode, None, self.mode_update, self.increase_error_count)

    def velocity_changed(self, value):
        try:
            self.silent_stepper.set_max_velocity(value)
        except ip_connection.Error:
            return

    def acceleration_changed(self, value):
        dec = self.deceleration_spin.value()
        try:
            self.silent_stepper.set_speed_ramping(value, dec)
        except ip_connection.Error:
            return
            
    def deceleration_changed(self, value):
        acc = self.acceleration_slider.value()
        try:
            self.silent_stepper.set_speed_ramping(acc, value)
        except ip_connection.Error:
            return

#    def decay_changed(self, value):
#        try:
#            self.silent_stepper.set_decay(value)
#        except ip_connection.Error:
#            return
