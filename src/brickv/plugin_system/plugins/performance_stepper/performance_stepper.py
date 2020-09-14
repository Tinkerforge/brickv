# -*- coding: utf-8 -*-
"""
Performance Stepper Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

performance_stepper.py: Performance Stepper Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.performance_stepper.ui_performance_stepper import Ui_PerformanceStepper
from brickv.bindings.bricklet_performance_stepper import BrickletPerformanceStepper
from brickv.bindings import ip_connection
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap
from brickv.monoflop import Monoflop
from brickv.plugin_system.plugins.stepper.speedometer import SpeedoMeter
from brickv.slider_spin_syncer import SliderSpinSyncer

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget
from PyQt5.QtGui import QLinearGradient, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

registers = {
    'General': [
        ('GCONF',         0x00, 'RW'),
        ('GSTAT',         0x01, 'R+C'),
        ('IFCNT',         0x02, 'R'),
        ('SLAVECONF',     0x03, ' W'),
        ('IOIN',          0x04, 'R'),
        ('X_COMPARE',     0x05, ' W'),
        ('OTP_PROG',      0x06, ' W'),
        ('OTP_READ',      0x07, 'R'),
        ('FACTORY_CONF',  0x08, 'RW'),
        ('SHORT_CONF',    0x09, ' W'),
        ('DRV_CONF',      0x0A, ' W'),
        ('GLOBAL_SCALER', 0x0B, ' W'),
        ('OFFSET_READ',   0x0C, 'R'),
    ],
    'Velocity': [
        ('IHOLD_IRUN',    0x10, ' W'),
        ('TPOWERDOWN',    0x11, ' W'),
        ('TSTEP',         0x12, 'R'),
        ('TPWMTHRS',      0x13, ' W'),
        ('TCOOLTHRS',     0x14, ' W'),
        ('THIGH',         0x15, ' W'),
    ],
    'Ramp Generator Motion': [
        ('RAMPMODE',      0x20, 'RW'),
        ('XACTUAL',       0x21, 'RW'),
        ('VACTUAL',       0x22, 'R'),
        ('VSTART',        0x23, ' W'),
        ('A1',            0x24, ' W'),
        ('V1',            0x25, ' W'),
        ('AMAX',          0x26, ' W'),
        ('VMAX',          0x27, ' W'),
        ('DMAX',          0x28, ' W'),
        ('D1',            0x2A, ' W'),
        ('VSTOP',         0x2B, ' W'),
        ('TZEROWAIT',     0x2C, ' W'),
        ('XTARGET',       0x2D, 'RW'),
    ],
    'Ramp Generator Driver': [
        ('VDCMIN',        0x33, ' W'),
        ('SW_MODE',       0x34, 'RW'),
        ('RAMP_STAT',     0x35, 'R+WC'),
        ('XLATCH',        0x36, 'R'),
    ],
    'Encoder': [
        ('ENCMODE',       0x38, 'RW'),
        ('X_ENC',         0x39, 'RW'),
        ('ENC_CONST',     0x3A, ' W'),
        ('ENC_STATUS',    0x3B, 'R+WC'),
        ('ENC_LATCH',     0x3C, 'R'),
        ('ENC_DEVIATION', 0x3D, ' W'),
    ],
    'Micro Stepping': [
        ('MSLUT0',        0x60, ' W'),
        ('MSLUT1',        0x61, ' W'),
        ('MSLUT2',        0x62, ' W'),
        ('MSLUT3',        0x63, ' W'),
        ('MSLUT4',        0x64, ' W'),
        ('MSLUT5',        0x65, ' W'),
        ('MSLUT6',        0x66, ' W'),
        ('MSLUT7',        0x67, ' W'),
        ('MSLUTSEL',      0x68, ' W'),
        ('MSLUTSTART',    0x69, ' W'),
        ('MSCNT',         0x6A, 'R'),
        ('MSCURACT',      0x6B, 'R'),
    ],
    'Driver': [
        ('CHOPCONF',      0x6C, 'RW'),
        ('COOLCONF',      0x6D, ' W'),
        ('DCCTRL',        0x6E, ' W'),
        ('DRV_STATUS',    0x6F, 'R'),
        ('PWMCONF',       0x70, ' W'),
        ('PWM_SCALE',     0x71, 'R'),
        ('PWM_AUTO',      0x72, 'R'),
        ('LOST_STEPS',    0x73, 'R'),
    ],
}

class PerformanceStepper(COMCUPluginBase, Ui_PerformanceStepper):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletPerformanceStepper, *args)

        self.setupUi(self)

        self.ps = self.device

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_counter = 0

        # Init register access elements
        self.parent_items = {}
        for register_name in registers.keys():
            self.parent_items[register_name] = QTreeWidgetItem([register_name])

        for pi in self.parent_items.values():
            self.tree_widget.addTopLevelItem(pi)
        
        self.child_items = []
        for name, rows in registers.items():
            for row in rows:
                child = QTreeWidgetItem([row[0], hex(row[1]), row[2], '0', ''])
                self.child_items.append(child)
                self.parent_items[name].addChild(child)

        for pi in self.parent_items.values():
            pi.setExpanded(True)

        self.tree_widget.itemClicked.connect(self.register_item_clicked)
        self.button_read_registers.clicked.connect(self.read_registers_clicked)
        self.button_write_register.clicked.connect(self.write_register_clicked)

        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        self.maximum_motor_current_spinbox.valueChanged.connect(self.maximum_motor_current_changed)
        self.to_button.clicked.connect(self.to_button_clicked)
        self.steps_button.clicked.connect(self.steps_button_clicked)

        # Motion Configuration
        self.velocity_start_syncer   = SliderSpinSyncer(self.velocity_start_slider,   self.velocity_start_spinbox,   self.motion_changed)
        self.velocity_stop_syncer    = SliderSpinSyncer(self.velocity_stop_slider,    self.velocity_stop_spinbox,    self.motion_changed)
        self.velocity_1_syncer       = SliderSpinSyncer(self.velocity_1_slider,       self.velocity_1_spinbox,       self.motion_changed)
        self.velocity_max_syncer     = SliderSpinSyncer(self.velocity_max_slider,     self.velocity_max_spinbox,     self.motion_changed)
        self.acceleration_1_syncer   = SliderSpinSyncer(self.acceleration_1_slider,   self.acceleration_1_spinbox,   self.motion_changed)
        self.acceleration_max_syncer = SliderSpinSyncer(self.acceleration_max_slider, self.acceleration_max_spinbox, self.motion_changed)
        self.deceleration_max_syncer = SliderSpinSyncer(self.deceleration_max_slider, self.deceleration_max_spinbox, self.motion_changed)
        self.deceleration_1_syncer   = SliderSpinSyncer(self.deceleration_1_slider,   self.deceleration_1_spinbox,   self.motion_changed)
        self.ramp_zero_wait_syncer   = SliderSpinSyncer(self.ramp_zero_wait_slider,   self.ramp_zero_wait_spinbox,   self.motion_changed)


        # Step Configuration
        self.step_resolution_dropbox.currentIndexChanged.connect(self.step_configuration_changed)
        self.interpolate_checkbox.stateChanged.connect(self.step_configuration_changed)

        # Basic Configuration
        self.standstill_current_spin.valueChanged.connect(self.basic_configuration_changed)
        self.motor_run_current_spin.valueChanged.connect(self.basic_configuration_changed)
        self.standstill_delay_time_spin.valueChanged.connect(self.basic_configuration_changed)
        self.power_down_time_spin.valueChanged.connect(self.basic_configuration_changed)
        self.stealth_threshold_spin.valueChanged.connect(self.basic_configuration_changed)
        self.coolstep_threashold_spin.valueChanged.connect(self.basic_configuration_changed)
        self.classic_threshold_spin.valueChanged.connect(self.basic_configuration_changed)
        self.high_velocity_chopper_mode_checkbox.stateChanged.connect(self.basic_configuration_changed)

        # Spreadcycle Configuration
        self.slow_decay_duration_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.fast_decay_duration_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.hysteresis_start_value_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.hysteresis_end_value_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.sine_wave_offset_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.chopper_mode_combo.currentIndexChanged.connect(self.spreadcycle_configuration_changed)
        self.comparator_blank_time_combo.currentIndexChanged.connect(self.spreadcycle_configuration_changed)
        self.high_velocity_fullstep_checkbox.stateChanged.connect(self.spreadcycle_configuration_changed)
        self.fast_decay_without_comparator_checkbox.stateChanged.connect(self.spreadcycle_configuration_changed)

        # Stealth Configuration
        self.enable_stealth_checkbox.stateChanged.connect(self.stealth_configuration_changed)
        self.offset_spin.valueChanged.connect(self.stealth_configuration_changed)
        self.gradient_spin.valueChanged.connect(self.stealth_configuration_changed)
        self.enable_autoscale_checkbox.stateChanged.connect(self.stealth_configuration_changed)
        self.enable_autogradient_checkbox.stateChanged.connect(self.stealth_configuration_changed)
        self.freewheel_mode_combo.currentIndexChanged.connect(self.stealth_configuration_changed)
        self.regulation_loop_gradient_spin.valueChanged.connect(self.stealth_configuration_changed)
        self.amplitude_limit_spin.valueChanged.connect(self.stealth_configuration_changed)

        # Coolstep Configuration
        self.minimum_stallguard_value_spin.valueChanged.connect(self.coolstep_configuration_changed)
        self.maximum_stallguard_value_spin.valueChanged.connect(self.coolstep_configuration_changed)
        self.current_up_step_width_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)
        self.current_down_step_width_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)
        self.minimum_current_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)
        self.stallguard_threshold_value_spin.valueChanged.connect(self.coolstep_configuration_changed)
        self.stallguard_mode_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)

        # Short Configuration
        self.disable_short_to_voltage_protection_checkbox.stateChanged.connect(self.short_configuration_changed)
        self.disable_short_to_ground_protection_checkbox.stateChanged.connect(self.short_configuration_changed)
        self.short_to_voltage_level_spin.valueChanged.connect(self.short_configuration_changed)
        self.short_to_ground_level_spin.valueChanged.connect(self.short_configuration_changed)
        self.spike_filter_bandwidth_combo.currentIndexChanged.connect(self.short_configuration_changed)
        self.short_detection_delay_checkbox.stateChanged.connect(self.short_configuration_changed)
        self.filter_time_combo.currentIndexChanged.connect(self.short_configuration_changed)

    def motion_changed(self, _):
        ramping_mode     = self.ramping_mode_combobox.currentIndex()
        velocity_start   = self.velocity_start_slider.value()
        acceleration_1   = self.acceleration_1_slider.value()
        velocity_1       = self.velocity_1_slider.value()
        acceleration_max = self.acceleration_max_slider.value()
        velocity_max     = self.velocity_max_slider.value()
        deceleration_max = self.deceleration_max_slider.value()
        deceleration_1   = self.deceleration_1_slider.value()
        velocity_stop    = self.velocity_stop_slider.value()
        ramp_zero_wait   = self.ramp_zero_wait_slider.value()

        motion_configuration = (ramping_mode, velocity_start, acceleration_1, velocity_1, acceleration_max, velocity_max, deceleration_max, deceleration_1, velocity_stop, ramp_zero_wait)
        self.ps.set_motion_configuration(*motion_configuration)

    def register_item_clicked(self, item, column):
        try:
            reg   = int(item.text(1), 16)
            value = int(item.text(3))

            self.spinbox_write_register.setValue(reg)
            self.spinbox_write_value.setValue(value)
        except:
            pass

    def read_registers_clicked(self):
        for child in self.child_items:
            reg = int(child.text(1), 0)
            ret = self.ps.read_register(reg)
            child.setText(3, str(ret.value))

    def write_register_clicked(self):
        reg   = self.spinbox_write_register.value()
        value = self.spinbox_write_value.value()
        ret   = self.ps.write_register(reg, value)

    def start(self):
        async_call(self.ps.get_motion_configuration, None, self.get_motion_configuration_async, self.increase_error_count)
        async_call(self.ps.get_step_configuration, None, self.get_step_configuration_async, self.increase_error_count)
        async_call(self.ps.get_motor_current, None, self.get_motor_current_async, self.increase_error_count)
        async_call(self.ps.get_enabled, None, self.get_enabled_async, self.increase_error_count)

        async_call(self.ps.get_step_configuration, None, self.get_step_configuration_async, self.increase_error_count)
        async_call(self.ps.get_basic_configuration, None, self.get_basic_configuration_async, self.increase_error_count)
        async_call(self.ps.get_spreadcycle_configuration, None, self.get_spreadcycle_configuration_async, self.increase_error_count)
        async_call(self.ps.get_stealth_configuration, None, self.get_stealth_configuration_async, self.increase_error_count)
        async_call(self.ps.get_coolstep_configuration, None, self.get_coolstep_configuration_async, self.increase_error_count)
        async_call(self.ps.get_short_configuration, None, self.get_short_configuration_async, self.increase_error_count)

        self.update_timer.start(100)

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPerformanceStepper.DEVICE_IDENTIFIER

    def update_data(self):
        async_call(self.ps.get_remaining_steps,  None, self.get_remaining_steps_async,  self.increase_error_count)
        async_call(self.ps.get_current_position, None, self.get_current_position_async, self.increase_error_count)
        async_call(self.ps.get_current_velocity, None, self.get_current_velocity_async, self.increase_error_count)

        self.update_counter += 1
        if self.update_counter % 10 == 0:
            async_call(self.ps.get_input_voltage, None, self.get_input_voltage_async, self.increase_error_count)
            async_call(self.ps.get_driver_status, None, self.get_driver_status_async, self.increase_error_count)
            async_call(self.ps.get_temperature,   None, self.get_temperature_async,   self.increase_error_count)


    def to_button_clicked(self):
        drive_to = self.to_spin.value()
        try:
            self.ps.set_target_position(drive_to)
        except ip_connection.Error:
            return

    def steps_button_clicked(self):
        drive_steps = self.steps_spin.value()
        try:
            self.ps.set_steps(drive_steps)
        except ip_connection.Error:
            return
    
    def enable_state_changed(self, state):
        self.ps.set_enabled(state == Qt.Checked)

    def maximum_motor_current_changed(self, value):
        try:
            self.ps.set_motor_current(value)
        except ip_connection.Error:
            return

    def step_configuration_changed(self, _):
        step_resolution = self.step_resolution_dropbox.currentIndex()
        interpolation   = self.interpolate_checkbox.isChecked()
        try:
            self.ps.set_step_configuration(step_resolution, interpolation)
        except ip_connection.Error:
            return

    def basic_configuration_changed(self, _):
        standstill_current         = self.standstill_current_spin.value()
        motor_run_current          = self.motor_run_current_spin.value()
        standstill_delay_time      = self.standstill_delay_time_spin.value()
        power_down_time            = self.power_down_time_spin.value()
        stealth_threshold          = self.stealth_threshold_spin.value()
        coolstep_threshold         = self.coolstep_threashold_spin.value()
        classic_threshold          = self.classic_threshold_spin.value()
        high_velocity_chopper_mode = self.high_velocity_chopper_mode_checkbox.isChecked()

        try:
            self.ps.set_basic_configuration(standstill_current, motor_run_current, standstill_delay_time, power_down_time, stealth_threshold, coolstep_threshold, classic_threshold, high_velocity_chopper_mode)
        except ip_connection.Error:
            return

    def spreadcycle_configuration_changed(self, _):
        slow_decay_duration           = self.slow_decay_duration_spin.value()
        fast_decay_duration           = self.fast_decay_duration_spin.value()
        hysteresis_start_value        = self.hysteresis_start_value_spin.value()
        hysteresis_end_value          = self.hysteresis_end_value_spin.value()
        sine_wave_offset              = self.sine_wave_offset_spin.value()
        chopper_mode                  = self.chopper_mode_combo.currentIndex()
        comparator_blank_time         = self.comparator_blank_time_combo.currentIndex()
        high_velocity_fullstep        = self.high_velocity_fullstep_checkbox.isChecked()
        fast_decay_without_comparator = self.fast_decay_without_comparator_checkbox.isChecked()

        try:
            self.ps.set_spreadcycle_configuration(slow_decay_duration, high_velocity_fullstep, fast_decay_duration, hysteresis_start_value, hysteresis_end_value, sine_wave_offset, chopper_mode, comparator_blank_time, fast_decay_without_comparator)
        except ip_connection.Error:
            return

    def stealth_configuration_changed(self, _):
        enable_stealth           = self.enable_stealth_checkbox.isChecked()
        offset                   = self.offset_spin.value()
        gradient                 = self.gradient_spin.value()
        enable_autoscale         = self.enable_autoscale_checkbox.isChecked()
        enable_autogradient      = self.enable_autogradient_checkbox.isChecked()
        freewheel_mode           = self.freewheel_mode_combo.currentIndex()
        regulation_loop_gradient = self.regulation_loop_gradient_spin.value()
        amplitude_limit          = self.amplitude_limit_spin.value()

        try:
            self.ps.set_stealth_configuration(enable_stealth, offset, gradient, enable_autoscale, enable_autogradient, freewheel_mode, regulation_loop_gradient, amplitude_limit)
        except ip_connection.Error:
            return

    def coolstep_configuration_changed(self, _):
        minimum_stallguard_value   = self.minimum_stallguard_value_spin.value()
        maximum_stallguard_value   = self.maximum_stallguard_value_spin.value()
        current_up_step_width      = self.current_up_step_width_combo.currentIndex()
        current_down_step_width    = self.current_down_step_width_combo.currentIndex()
        minimum_current            = self.minimum_current_combo.currentIndex()
        stallguard_threshold_value = self.stallguard_threshold_value_spin.value()
        stallguard_mode            = self.stallguard_mode_combo.currentIndex()

        try:
            self.ps.set_coolstep_configuration(minimum_stallguard_value, maximum_stallguard_value, current_up_step_width, current_down_step_width, minimum_current, stallguard_threshold_value, stallguard_mode)
        except ip_connection.Error:
            return

    def short_configuration_changed(self, _):
        disable_short_to_voltage_protection = self.disable_short_to_voltage_protection_checkbox.isChecked()
        disable_short_to_ground_protection  = self.disable_short_to_ground_protection_checkbox.isChecked()
        short_to_voltage_level              = self.short_to_voltage_level_spin.value()
        short_to_ground_level               = self.short_to_ground_level_spin.value()
        spike_filter_bandwidth              = self.spike_filter_bandwidth_combo.currentIndex()
        short_detection_delay               = self.short_detection_delay_checkbox.isChecked()
        filter_time                         = self.filter_time_combo.currentIndex()

        try:
            self.ps.set_short_configuration(disable_short_to_voltage_protection, disable_short_to_ground_protection, short_to_voltage_level, short_to_ground_level, spike_filter_bandwidth, short_detection_delay, filter_time)
        except ip_connection.Error:
            return

    def get_remaining_steps_async(self, remaining_steps):
        self.remaining_steps_label.setText(str(remaining_steps))

    def get_current_position_async(self, current_position):
        self.position_label.setText(str(current_position))

    def get_current_velocity_async(self, current_velocity):
        self.velocity_label.setText(str(current_velocity))

    def get_input_voltage_async(self, input_voltage):
        self.input_voltage_label.setText('{0:.1f}V'.format(input_voltage/1000))

    def get_temperature_async(self, temperature):
        self.status_temperature.setText('{0:.1f}°C'.format(temperature/10))

    def get_driver_status_async(self, driver_status):
        if driver_status.open_load == 0:
            self.status_open_load.setText('No')
        elif driver_status.open_load == 1:
            self.status_open_load.setText('Phase A')
        elif driver_status.open_load == 2:
            self.status_open_load.setText('Phase B')
        elif driver_status.open_load == 3:
            self.status_open_load.setText('Phase A and B')
        else:
            self.status_open_load.setText('Unknown')

        if driver_status.short_to_ground == 0:
            self.status_short_to_ground.setText('No')
        elif driver_status.short_to_ground == 1:
            self.status_short_to_ground.setText('Phase A')
        elif driver_status.short_to_ground == 2:
            self.status_short_to_ground.setText('Phase B')
        elif driver_status.short_to_ground == 3:
            self.status_short_to_ground.setText('Phase A and B')
        else:
            self.status_short_to_ground.setText('Unknown')

        if driver_status.over_temperature == 0:
            self.status_over_temperature.setText('No')
        elif driver_status.over_temperature == 1:
            self.status_over_temperature.setText('<font color=yellow>Warning</font>')
        elif driver_status.over_temperature == 2:
            self.status_over_temperature.setText('<font color=red>Limit</font>')

        if driver_status.motor_stalled:
            self.status_motor_stalled.setText('Yes')
        else:
            self.status_motor_stalled.setText('No')

        self.status_actual_motor_current.setText(str(driver_status.actual_motor_current))

        if driver_status.full_step_active:
            self.status_full_step_active.setText('Yes')
        else:
            self.status_full_step_active.setText('No')

        self.status_stallguard_result.setText(str(driver_status.stallguard_result))
        self.status_stealth_voltage_amplitude.setText(str(driver_status.stealth_voltage_amplitude))

    def get_enabled_async(self, enabled):
        old_state = self.enable_checkbox.blockSignals(True)
        self.enable_checkbox.setChecked(enabled)
        self.enable_checkbox.blockSignals(old_state)

    def get_motor_current_async(self, value):
        old_state = self.maximum_motor_current_spinbox.blockSignals(True)
        self.maximum_motor_current_spinbox.setValue(value)
        self.maximum_motor_current_spinbox.blockSignals(old_state)

    def get_step_configuration_async(self, conf):
        old_state = self.step_resolution_dropbox.blockSignals(True)
        self.step_resolution_dropbox.setCurrentIndex(conf.step_resolution)
        self.step_resolution_dropbox.blockSignals(old_state)

        old_state = self.interpolate_checkbox.blockSignals(True)
        self.interpolate_checkbox.setChecked(conf.interpolation)
        self.interpolate_checkbox.blockSignals(old_state)

    def get_motion_configuration_async(self, conf):
        self.velocity_start_syncer.set_value(conf.velocity_start)
        self.acceleration_1_syncer.set_value(conf.acceleration_1)
        self.velocity_1_syncer.set_value(conf.velocity_1)
        self.acceleration_max_syncer.set_value(conf.acceleration_max)
        self.velocity_max_syncer.set_value(conf.velocity_max)
        self.deceleration_max_syncer.set_value(conf.deceleration_max)
        self.deceleration_1_syncer.set_value(conf.deceleration_1)
        self.velocity_stop_syncer.set_value(conf.velocity_stop)
        self.ramp_zero_wait_syncer.set_value(conf.ramp_zero_wait)

        self.ramping_mode_combobox.setCurrentIndex(conf.ramping_mode)

    def get_basic_configuration_async(self, conf):
        old_state = self.standstill_current_spin.blockSignals(True)
        self.standstill_current_spin.setValue(conf.standstill_current)
        self.standstill_current_spin.blockSignals(old_state)

        old_state = self.motor_run_current_spin.blockSignals(True)
        self.motor_run_current_spin.setValue(conf.motor_run_current)
        self.motor_run_current_spin.blockSignals(old_state)

        old_state = self.standstill_delay_time_spin.blockSignals(True)
        self.standstill_delay_time_spin.setValue(conf.standstill_delay_time)
        self.standstill_delay_time_spin.blockSignals(old_state)

        old_state = self.power_down_time_spin.blockSignals(True)
        self.power_down_time_spin.setValue(conf.power_down_time)
        self.power_down_time_spin.blockSignals(old_state)

        old_state = self.stealth_threshold_spin.blockSignals(True)
        self.stealth_threshold_spin.setValue(conf.stealth_threshold)
        self.stealth_threshold_spin.blockSignals(old_state)

        old_state = self.coolstep_threashold_spin.blockSignals(True)
        self.coolstep_threashold_spin.setValue(conf.coolstep_threshold)
        self.coolstep_threashold_spin.blockSignals(old_state)

        old_state = self.classic_threshold_spin.blockSignals(True)
        self.classic_threshold_spin.setValue(conf.classic_threshold)
        self.classic_threshold_spin.blockSignals(old_state)

        old_state = self.high_velocity_chopper_mode_checkbox.blockSignals(True)
        self.high_velocity_chopper_mode_checkbox.setChecked(conf.high_velocity_chopper_mode)
        self.high_velocity_chopper_mode_checkbox.blockSignals(old_state)

    def get_spreadcycle_configuration_async(self, conf):
        old_state = self.slow_decay_duration_spin.blockSignals(True)
        self.slow_decay_duration_spin.setValue(conf.slow_decay_duration)
        self.slow_decay_duration_spin.blockSignals(old_state)

        old_state = self.fast_decay_duration_spin.blockSignals(True)
        self.fast_decay_duration_spin.setValue(conf.fast_decay_duration)
        self.fast_decay_duration_spin.blockSignals(old_state)

        old_state = self.hysteresis_start_value_spin.blockSignals(True)
        self.hysteresis_start_value_spin.setValue(conf.hysteresis_start_value)
        self.hysteresis_start_value_spin.blockSignals(old_state)

        old_state = self.hysteresis_end_value_spin.blockSignals(True)
        self.hysteresis_end_value_spin.setValue(conf.hysteresis_end_value)
        self.hysteresis_end_value_spin.blockSignals(old_state)

        old_state = self.sine_wave_offset_spin.blockSignals(True)
        self.sine_wave_offset_spin.setValue(conf.sine_wave_offset)
        self.sine_wave_offset_spin.blockSignals(old_state)

        old_state = self.chopper_mode_combo.blockSignals(True)
        self.chopper_mode_combo.setCurrentIndex(conf.chopper_mode)
        self.chopper_mode_combo.blockSignals(old_state)

        old_state = self.standstill_current_spin.blockSignals(True)
        self.comparator_blank_time_combo.setCurrentIndex(conf.comparator_blank_time)
        self.standstill_current_spin.blockSignals(old_state)

        old_state = self.high_velocity_fullstep_checkbox.blockSignals(True)
        self.high_velocity_fullstep_checkbox.setChecked(conf.high_velocity_fullstep)
        self.high_velocity_fullstep_checkbox.blockSignals(old_state)

        old_state = self.fast_decay_without_comparator_checkbox.blockSignals(True)
        self.fast_decay_without_comparator_checkbox.setChecked(conf.fast_decay_without_comparator)
        self.fast_decay_without_comparator_checkbox.blockSignals(old_state)


    def get_stealth_configuration_async(self, conf):
        old_state = self.enable_stealth_checkbox.blockSignals(True)
        self.enable_stealth_checkbox.setChecked(conf.enable_stealth)
        self.enable_stealth_checkbox.blockSignals(old_state)

        old_state = self.offset_spin.blockSignals(True)
        self.offset_spin.setValue(conf.offset)
        self.offset_spin.blockSignals(old_state)

        old_state = self.gradient_spin.blockSignals(True)
        self.gradient_spin.setValue(conf.gradient)
        self.gradient_spin.blockSignals(old_state)

        old_state = self.enable_autoscale_checkbox.blockSignals(True)
        self.enable_autoscale_checkbox.setChecked(conf.enable_autoscale)
        self.enable_autoscale_checkbox.blockSignals(old_state)

        old_state = self.enable_autogradient_checkbox.blockSignals(True)
        self.enable_autogradient_checkbox.setChecked(conf.enable_autogradient)
        self.enable_autogradient_checkbox.blockSignals(old_state)

        old_state = self.freewheel_mode_combo.blockSignals(True)
        self.freewheel_mode_combo.setCurrentIndex(conf.freewheel_mode)
        self.freewheel_mode_combo.blockSignals(old_state)

        old_state = self.regulation_loop_gradient_spin.blockSignals(True)
        self.regulation_loop_gradient_spin.setValue(conf.regulation_loop_gradient)
        self.regulation_loop_gradient_spin.blockSignals(old_state)

        old_state = self.amplitude_limit_spin.blockSignals(True)
        self.amplitude_limit_spin.setValue(conf.amplitude_limit)
        self.amplitude_limit_spin.blockSignals(old_state)

    def get_coolstep_configuration_async(self, conf):
        old_state = self.minimum_stallguard_value_spin.blockSignals(True)
        self.minimum_stallguard_value_spin.setValue(conf.minimum_stallguard_value)
        self.minimum_stallguard_value_spin.blockSignals(old_state)

        old_state = self.maximum_stallguard_value_spin.blockSignals(True)
        self.maximum_stallguard_value_spin.setValue(conf.maximum_stallguard_value)
        self.maximum_stallguard_value_spin.blockSignals(old_state)

        old_state = self.current_up_step_width_combo.blockSignals(True)
        self.current_up_step_width_combo.setCurrentIndex(conf.current_up_step_width)
        self.current_up_step_width_combo.blockSignals(old_state)

        old_state = self.current_down_step_width_combo.blockSignals(True)
        self.current_down_step_width_combo.setCurrentIndex(conf.current_down_step_width)
        self.current_down_step_width_combo.blockSignals(old_state)

        old_state = self.minimum_current_combo.blockSignals(True)
        self.minimum_current_combo.setCurrentIndex(conf.minimum_current)
        self.minimum_current_combo.blockSignals(old_state)

        old_state = self.stallguard_threshold_value_spin.blockSignals(True)
        self.stallguard_threshold_value_spin.setValue(conf.stallguard_threshold_value)
        self.stallguard_threshold_value_spin.blockSignals(old_state)

        old_state = self.stallguard_mode_combo.blockSignals(True)
        self.stallguard_mode_combo.setCurrentIndex(conf.stallguard_mode)
        self.stallguard_mode_combo.blockSignals(old_state)

    def get_short_configuration_async(self, conf):
        old_state = self.disable_short_to_voltage_protection_checkbox.blockSignals(True)
        self.disable_short_to_voltage_protection_checkbox.setChecked(conf.disable_short_to_voltage_protection)
        self.disable_short_to_voltage_protection_checkbox.blockSignals(old_state)

        old_state = self.disable_short_to_ground_protection_checkbox.blockSignals(True)
        self.disable_short_to_ground_protection_checkbox.setChecked(conf.disable_short_to_ground_protection)
        self.disable_short_to_ground_protection_checkbox.blockSignals(old_state)

        old_state = self.short_to_voltage_level_spin.blockSignals(True)
        self.short_to_voltage_level_spin.setValue(conf.short_to_voltage_level)
        self.short_to_voltage_level_spin.blockSignals(old_state)

        old_state = self.short_to_ground_level_spin.blockSignals(True)
        self.short_to_ground_level_spin.setValue(conf.short_to_ground_level)
        self.short_to_ground_level_spin.blockSignals(old_state)

        old_state = self.spike_filter_bandwidth_combo.blockSignals(True)
        self.spike_filter_bandwidth_combo.setCurrentIndex(conf.spike_filter_bandwidth)
        self.spike_filter_bandwidth_combo.blockSignals(old_state)

        old_state = self.short_detection_delay_checkbox.blockSignals(True)
        self.short_detection_delay_checkbox.setChecked(conf.short_detection_delay)
        self.short_detection_delay_checkbox.blockSignals(old_state)

        old_state = self.filter_time_combo.blockSignals(True)
        self.filter_time_combo.setCurrentIndex(conf.filter_time)
        self.filter_time_combo.blockSignals(old_state)