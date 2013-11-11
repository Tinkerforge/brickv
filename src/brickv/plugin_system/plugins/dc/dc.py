# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2009-2012 Olaf Lüke <olaf@tinkerforge.com>

dc.py: DC Plugin implementation

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
from brickv.bindings import ip_connection
from brickv.bindings.brick_dc import BrickDC
from brickv.async_call import async_call

from PyQt4.QtGui import QErrorMessage, QInputDialog
from PyQt4.QtCore import QTimer, Qt, pyqtSignal

from brickv.plugin_system.plugins.dc.speedometer import SpeedoMeter
from brickv.plugin_system.plugins.dc.ui_dc import Ui_DC

class DC(PluginBase, Ui_DC):
    qtcb_position_reached = pyqtSignal(int)
    qtcb_under_voltage = pyqtSignal(int)
    qtcb_emergency_shutdown = pyqtSignal()
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'DC Brick', version)
        
        self.setupUi(self)
        self.encoder_hide_all()
        
        self.dc = BrickDC(uid, ipcon)
        self.device = self.dc
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        
        self.speedometer = SpeedoMeter()
        self.vertical_layout_right.insertWidget(4, self.speedometer)
        
        self.new_value = 0
        self.update_counter = 0
        
        self.full_brake_time = 0
        
        self.velocity_slider.sliderReleased.connect(self.velocity_slider_released)
        self.velocity_slider.valueChanged.connect(self.velocity_spin.setValue)
        self.velocity_spin.editingFinished.connect(self.velocity_spin_finished)
        
        self.acceleration_slider.sliderReleased.connect(self.acceleration_slider_released)
        self.acceleration_slider.valueChanged.connect(self.acceleration_spin.setValue)
        self.acceleration_spin.editingFinished.connect(self.acceleration_spin_finished)
        
        self.frequency_slider.sliderReleased.connect(self.frequency_slider_released)
        self.frequency_slider.valueChanged.connect(self.frequency_spin.setValue)
        self.frequency_spin.editingFinished.connect(self.frequency_spin_finished)
        
        self.radio_mode_brake.toggled.connect(self.brake_value_changed)
        self.radio_mode_coast.toggled.connect(self.coast_value_changed)
        
        self.minimum_voltage_button.pressed.connect(self.minimum_voltage_button_pressed)
        self.full_brake_button.pressed.connect(self.full_brake_pressed)
        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        
        self.emergency_signal = None
        self.under_signal = None
        self.current_velocity_signal = None
        self.velocity_reached_signal = None
        
        self.qem = QErrorMessage(self)
        
        self.qtcb_under_voltage.connect(self.cb_under_voltage)
        self.dc.register_callback(self.dc.CALLBACK_UNDER_VOLTAGE,
                                  self.qtcb_under_voltage.emit) 
        
        self.qtcb_emergency_shutdown.connect(self.cb_emergency_shutdown)
        self.dc.register_callback(self.dc.CALLBACK_EMERGENCY_SHUTDOWN,
                                  self.qtcb_emergency_shutdown.emit) 
        
        self.qtcb_position_reached.connect(self.update_velocity)
        self.dc.register_callback(self.dc.CALLBACK_VELOCITY_REACHED,
                                  self.qtcb_position_reached.emit) 
        self.dc.register_callback(self.dc.CALLBACK_CURRENT_VELOCITY,
                                  self.qtcb_position_reached.emit)
        
#        if self.version >= (2, 0, 1):
#            self.enable_encoder_checkbox.stateChanged.connect(self.enable_encoder_state_changed)
#            self.encoder_show()
#        else:
#            self.enable_encoder_checkbox.setText('Enable Encoder (Firmware >= 2.01 required)')
#            self.enable_encoder_checkbox.setEnabled(False)
    
    def start(self):
        self.update_timer.start(1000)
        async_call(self.dc.set_current_velocity_period, 100, None, self.increase_error_count)
        self.update_start()
        self.update_data()
        
    def stop(self):
        self.update_timer.stop()
        async_call(self.dc.set_current_velocity_period, 0, None, self.increase_error_count)

    def has_reset_device(self):
        return self.version >= (1, 1, 3)

    def reset_device(self):
        if self.has_reset_device():
            self.dc.reset()

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'dc'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickDC.DEVICE_IDENTIFIER
        
    def cb_emergency_shutdown(self):
        if not self.qem.isVisible():
            self.qem.setWindowTitle("Emergency Shutdown")
            self.qem.showMessage("Emergency Shutdown: Short-Circuit or Over-Temperature")
        
    def cb_under_voltage(self, ov):
        mv_str = self.minimum_voltage_label.text()
        ov_str = "%gV"  % round(ov/1000.0, 1)
        if not self.qem.isVisible():
            self.qem.setWindowTitle("Under Voltage")
            self.qem.showMessage("Under Voltage: Output Voltage of " + ov_str +
                                 " is below minimum voltage of " + mv_str,
                                 "DC_UnderVoltage")
            
    def encoder_hide_all(self):
        self.enable_encoder_checkbox.hide()
        self.encoder_hide()
            
    def encoder_hide(self):
        self.p_label.hide()
        self.p_spinbox.hide()
        self.i_label.hide()
        self.i_spinbox.hide()
        self.d_label.hide()
        self.d_spinbox.hide()
        self.st_label.hide()
        self.st_spinbox.hide()
        self.cpr_label.hide()
        self.cpr_spinbox.hide()
        self.encoder_spacer.hide()
        
    def encoder_show(self):
        self.p_label.show()
        self.p_spinbox.show()
        self.i_label.show()
        self.i_spinbox.show()
        self.d_label.show()
        self.d_spinbox.show()
        self.st_label.show()
        self.st_spinbox.show()
        self.cpr_label.show()
        self.cpr_spinbox.show()
        self.encoder_spacer.show()          
         
    def enable_encoder_state_changed(self, state):
        try:
            if state == Qt.Checked:
                self.dc.enable_encoder()
                self.update_encoder()
            elif state == Qt.Unchecked:
                self.dc.disable_encoder()

        except ip_connection.Error:
            return
        
    def enable_state_changed(self, state):
        try:
            if state == Qt.Checked:
                self.dc.enable()
            elif state == Qt.Unchecked:
                self.dc.disable()
        except ip_connection.Error:
            return
            
    def brake_value_changed(self, checked):
        if checked:
            try:
                self.dc.set_drive_mode(0)
            except ip_connection.Error:
                return
        
    def coast_value_changed(self, checked):
        if checked:
            try:
                self.dc.set_drive_mode(1)
            except ip_connection.Error:
                return
        
    def full_brake_pressed(self):
        try:
            self.dc.full_brake()
        except ip_connection.Error:
            return
        
    def minimum_voltage_selected(self, value):
        try:
            self.dc.set_minimum_voltage(value)
        except ip_connection.Error:
            return
        
    def minimum_voltage_button_pressed(self):
        qid = QInputDialog(self)
        qid.setInputMode(QInputDialog.IntInput)
        qid.setIntMinimum(5000)
        qid.setIntMaximum(0xFFFF)
        qid.setIntStep(100)
        async_call(self.dc.get_minimum_voltage, None, qid.setIntValue, self.increase_error_count)
        qid.intValueSelected.connect(self.minimum_voltage_selected)
        qid.setLabelText("Choose minimum motor voltage in mV.")
        qid.open()
        
    def stack_input_voltage_update(self, sv):
        sv_str = "%gV"  % round(sv/1000.0, 1)
        self.stack_voltage_label.setText(sv_str)
        
    def external_input_voltage_update(self, ev):
        ev_str = "%gV"  % round(ev/1000.0, 1)
        self.external_voltage_label.setText(ev_str)
        
    def minimum_voltage_update(self, mv):
        mv_str = "%gV"  % round(mv/1000.0, 1)
        self.minimum_voltage_label.setText(mv_str)
        
    def drive_mode_update(self, dm):
        if dm == 0:
            self.radio_mode_brake.setChecked(True)
            self.radio_mode_coast.setChecked(False)
        else:
            self.radio_mode_brake.setChecked(False)
            self.radio_mode_coast.setChecked(True)
            
    def current_consumption_update(self, cc):
        if cc >= 1000:
            cc_str = "%gA"  % round(cc/1000.0, 1)
        else:
            cc_str = "%gmA" % cc
            
        self.current_label.setText(cc_str)

    
    def update_velocity(self, value):
        if value != self.speedometer.value():
            self.speedometer.set_velocity(value)
        
    def get_velocity_async(self, velocity):
        if not self.velocity_slider.isSliderDown():
            if velocity != self.velocity_slider.sliderPosition():
                self.velocity_slider.setSliderPosition(velocity)
                self.velocity_spin.setValue(velocity)
        
    def get_acceleration_async(self, acceleration):
        if not self.acceleration_slider.isSliderDown():
            if acceleration != self.acceleration_slider.sliderPosition():
                self.acceleration_slider.setSliderPosition(acceleration)
                self.acceleration_spin.setValue(acceleration)
        
    def get_pwm_frequency_async(self, frequency):
        if not self.frequency_slider.isSliderDown():
            if frequency != self.frequency_slider.sliderPosition():
                self.frequency_slider.setSliderPosition(frequency)
                self.frequency_spin.setValue(frequency)
        
    def is_enabled_async(self, enabled):
        if enabled:
            self.enable_checkbox.setCheckState(Qt.Checked)
        else:
            self.enable_checkbox.setCheckState(Qt.Unchecked)
            
    def is_encoder_enabled_async(self, enabled):
        if enabled:
            self.enable_encoder_checkbox.setCheckState(Qt.Checked)
        else:
            self.enable_encoder_checkbox.setCheckState(Qt.Unchecked)
            
    def get_encoder_config_async(self, cpr):
        self.cpr_spinbox.setValue(cpr)
    
    def get_encoder_pid_config_async(self, pid_config):
        self.p_spinbox.setValue(pid_config.p)
        self.i_spinbox.setValue(pid_config.i)
        self.d_spinbox.setValue(pid_config.d)
        self.st_spinbox.setValue(pid_config.sample_time)
        
    def update_encoder(self):
        async_call(self.dc.get_encoder_config, None, self.get_encoder_config_async, self.increase_error_count)
        async_call(self.dc.get_encoder_pid_config, None, self.get_encoder_pid_config_async, self.increase_error_count)
        async_call(self.dc.is_encoder_enabled, None, self.is_encoder_enabled_async, self.increase_error_count)
        
        
    def update_start(self):
        async_call(self.dc.get_drive_mode, None, self.drive_mode_update, self.increase_error_count)
        async_call(self.dc.get_velocity, None, self.get_velocity_async, self.increase_error_count)
        async_call(self.dc.get_acceleration, None, self.get_acceleration_async, self.increase_error_count)
        async_call(self.dc.get_pwm_frequency, None, self.get_pwm_frequency_async, self.increase_error_count)
        async_call(self.dc.is_enabled, None, self.is_enabled_async, self.increase_error_count)
#        if self.version >= (2, 0, 1):
#            self.update_encoder()
            

    def update_data(self):
        async_call(self.dc.get_stack_input_voltage, None, self.stack_input_voltage_update, self.increase_error_count)
        async_call(self.dc.get_external_input_voltage, None, self.external_input_voltage_update, self.increase_error_count)
        async_call(self.dc.get_minimum_voltage, None, self.minimum_voltage_update, self.increase_error_count)
        async_call(self.dc.get_current_consumption, None, self.current_consumption_update, self.increase_error_count)
        
    def acceleration_slider_released(self):
        value = self.acceleration_slider.value()
        self.acceleration_spin.setValue(value)
        try:
            self.dc.set_acceleration(value)
        except ip_connection.Error:
            return
        
    def acceleration_spin_finished(self):
        value = self.acceleration_spin.value()
        self.acceleration_slider.setValue(value)
        try:
            self.dc.set_acceleration(value)
        except ip_connection.Error:
            return
        
    def velocity_slider_released(self):
        value = self.velocity_slider.value()
        self.velocity_spin.setValue(value)
        try:
            self.dc.set_velocity(value)
        except ip_connection.Error:
            return
        
    def velocity_spin_finished(self):
        value = self.velocity_spin.value()
        self.velocity_slider.setValue(value)
        try:
            self.dc.set_velocity(value)
        except ip_connection.Error:
            return
        
    def frequency_slider_released(self):
        value = self.frequency_slider.value()
        self.frequency_spin.setValue(value)
        try:
            self.dc.set_pwm_frequency(value)
        except ip_connection.Error:
            return
        
    def frequency_spin_finished(self):
        value = self.frequency_spin.value()
        self.frequency_slider.setValue(value)
        try:
            self.dc.set_pwm_frequency(value)
        except ip_connection.Error:
            return
