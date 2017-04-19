# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

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

        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        self.forward_button.clicked.connect(self.forward_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)
        self.full_brake_button.clicked.connect(self.full_brake_clicked)
        self.backward_button.clicked.connect(self.backward_clicked)
        self.to_button.clicked.connect(self.to_button_clicked)
        self.steps_button.clicked.connect(self.steps_button_clicked)
        self.motor_current_button.clicked.connect(self.motor_current_button_clicked)
        self.minimum_motor_voltage_button.clicked.connect(self.minimum_motor_voltage_button_clicked)

        self.qtcb_position_reached.connect(self.cb_position_reached)
        self.silent_stepper.register_callback(self.silent_stepper.CALLBACK_POSITION_REACHED,
                                              self.qtcb_position_reached.emit)

        self.qtcb_under_voltage.connect(self.cb_under_voltage)
        self.silent_stepper.register_callback(self.silent_stepper.CALLBACK_UNDER_VOLTAGE,
                                              self.qtcb_under_voltage.emit)

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
        self.enable_random_slow_decay_checkbox.stateChanged.connect(self.spreadcycle_configuration_changed)
        self.fast_decay_duration_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.hysteresis_start_value_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.hysteresis_end_value_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.sine_wave_offset_spin.valueChanged.connect(self.spreadcycle_configuration_changed)
        self.chopper_mode_combo.currentIndexChanged.connect(self.spreadcycle_configuration_changed)
        self.comparator_blank_time_combo.currentIndexChanged.connect(self.spreadcycle_configuration_changed)
        self.fast_decay_without_comparator_checkbox.stateChanged.connect(self.spreadcycle_configuration_changed)

        # Stealth Configuration
        self.enable_stealth_checkbox.stateChanged.connect(self.stealth_configuration_changed)
        self.amplitude_spin.valueChanged.connect(self.stealth_configuration_changed)
        self.gradient_spin.valueChanged.connect(self.stealth_configuration_changed)
        self.enable_autoscale_checkbox.stateChanged.connect(self.stealth_configuration_changed)
        self.force_symmetric_checkbox.stateChanged.connect(self.stealth_configuration_changed)
        self.freewheel_mode_combo.currentIndexChanged.connect(self.stealth_configuration_changed)

        # Coolstep Configuration
        self.minimum_stallguard_value_spin.valueChanged.connect(self.coolstep_configuration_changed)
        self.maximum_stallguard_value_spin.valueChanged.connect(self.coolstep_configuration_changed)
        self.current_up_step_width_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)
        self.current_down_step_width_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)
        self.minimum_current_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)
        self.stallguard_threshold_value_spin.valueChanged.connect(self.coolstep_configuration_changed)
        self.stallguard_mode_combo.currentIndexChanged.connect(self.coolstep_configuration_changed)

        # Misc Configuration
        self.disable_short_to_ground_protection_checkbox.stateChanged.connect(self.misc_configuration_changed)
        self.synchronize_phase_frequency_spin.valueChanged.connect(self.misc_configuration_changed)

        self.ste = 0
        self.pos = 0
        self.current_velocity = 0
        self.cur = 0
        self.sv  = 0
        self.ev  = 0
        self.mv  = 0
        self.mod = 0

        self.status_led_action = QAction('Status LED', self)
        self.status_led_action.setCheckable(True)
        self.status_led_action.toggled.connect(lambda checked: self.silent_stepper.enable_status_led() if checked else self.silent_stepper.disable_status_led())
        self.set_configs([(0, None, [self.status_led_action])])

        reset = QAction('Reset', self)
        reset.triggered.connect(lambda: self.silent_stepper.reset())
        self.set_actions([(0, None, [reset])])

    def start(self):
        async_call(self.silent_stepper.is_status_led_enabled, None, self.status_led_action.setChecked, self.increase_error_count)

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

    def step_configuration_changed(self, _):
        step_resolution = self.step_resolution_dropbox.currentIndex()
        interpolation = self.interpolate_checkbox.isChecked()
        try:
            self.silent_stepper.set_step_configuration(step_resolution, interpolation)
        except ip_connection.Error:
            return

    def basic_configuration_changed(self, _):
        standstill_current = self.standstill_current_spin.value()
        motor_run_current = self.motor_run_current_spin.value()
        standstill_delay_time = self.standstill_delay_time_spin.value()
        power_down_time = self.power_down_time_spin.value()
        stealth_threshold = self.stealth_threshold_spin.value()
        coolstep_threshold = self.coolstep_threashold_spin.value()
        classic_threshold = self.classic_threshold_spin.value()
        high_velocity_chopper_mode = self.high_velocity_chopper_mode_checkbox.isChecked()

        try:
            self.silent_stepper.set_basic_configuration(standstill_current, motor_run_current, standstill_delay_time, power_down_time, stealth_threshold, coolstep_threshold, classic_threshold, high_velocity_chopper_mode)
        except ip_connection.Error:
            return

    def spreadcycle_configuration_changed(self, _):
        slow_decay_duration = self.slow_decay_duration_spin.value()
        enable_random_slow_decay = self.enable_random_slow_decay_checkbox.isChecked()
        fast_decay_duration = self.fast_decay_duration_spin.value()
        hysteresis_start_value = self.hysteresis_start_value_spin.value()
        hysteresis_end_value = self.hysteresis_end_value_spin.value()
        sine_wave_offset = self.sine_wave_offset_spin.value()
        chopper_mode = self.chopper_mode_combo.currentIndex()
        comparator_blank_time = self.comparator_blank_time_combo.currentIndex()
        fast_decay_without_comparator = self.fast_decay_without_comparator_checkbox.isChecked()

        try:
            self.silent_stepper.set_spreadcycle_configuration(slow_decay_duration, enable_random_slow_decay, fast_decay_duration, hysteresis_start_value, hysteresis_end_value, sine_wave_offset, chopper_mode, comparator_blank_time, fast_decay_without_comparator)
        except ip_connection.Error:
            return

    def stealth_configuration_changed(self, _):
        enable_stealth = self.enable_stealth_checkbox.isChecked()
        amplitude = self.amplitude_spin.value()
        gradient = self.gradient_spin.value()
        enable_autoscale = self.enable_autoscale_checkbox.isChecked()
        force_symmetric = self.force_symmetric_checkbox.isChecked()
        freewheel_mode = self.freewheel_mode_combo.currentIndex()

        try:
            self.silent_stepper.set_stealth_configuration(enable_stealth, amplitude, gradient, enable_autoscale, force_symmetric, freewheel_mode)
        except ip_connection.Error:
            return

    def coolstep_configuration_changed(self, _):
        minimum_stallguard_value = self.minimum_stallguard_value_spin.value()
        maximum_stallguard_value = self.maximum_stallguard_value_spin.value()
        current_up_step_width = self.current_up_step_width_combo.currentIndex()
        current_down_step_width = self.current_down_step_width_combo.currentIndex()
        minimum_current = self.minimum_current_combo.currentIndex()
        stallguard_threshold_value = self.stallguard_threshold_value_spin.value()
        stallguard_mode = self.stallguard_mode_combo.currentIndex()

        try:
            self.silent_stepper.set_coolstep_configuration(minimum_stallguard_value, maximum_stallguard_value, current_up_step_width, current_down_step_width, minimum_current, stallguard_threshold_value, stallguard_mode)
        except ip_connection.Error:
            return

    def misc_configuration_changed(self, _):
        disable_short_to_ground_protection = self.disable_short_to_ground_protection_checkbox.isChecked()
        synchronize_phase_frequency = self.synchronize_phase_frequency_spin.value()

        try:
            self.silent_stepper.set_misc_configuration(disable_short_to_ground_protection, synchronize_phase_frequency)
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
        qid.setIntMinimum(360)
        qid.setIntMaximum(1640)
        qid.setIntStep(100)
        async_call(self.silent_stepper.get_motor_current, None, qid.setIntValue, self.increase_error_count)
        qid.intValueSelected.connect(self.motor_current_selected)
        qid.setLabelText("Choose motor current in mA.")
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

    def driver_status_update(self, update):
        if update.open_load == 0:
            self.status_open_load.setText('No')
        elif update.open_load == 1:
            self.status_open_load.setText('Phase A')
        elif update.open_load == 2:
            self.status_open_load.setText('Phase B')
        elif update.open_load == 3:
            self.status_open_load.setText('Phase A and B')
        else:
            self.status_open_load.setText('Unkown')

        if update.short_to_ground == 0:
            self.status_short_to_ground.setText('No')
        elif update.short_to_ground == 1:
            self.status_short_to_ground.setText('Phase A')
        elif update.short_to_ground == 2:
            self.status_short_to_ground.setText('Phase B')
        elif update.short_to_ground == 3:
            self.status_short_to_ground.setText('Phase A and B')
        else:
            self.status_short_to_ground.setText('Unkown')

        if update.over_temperature == 0:
            self.status_over_temperature.setText('No')
        elif update.over_temperature == 1:
            self.status_over_temperature.setText('<font color=yellow>Warning</font>')
        elif update.over_temperature == 2:
            self.status_over_temperature.setText('<font color=red>Limit</font>')

        if update.motor_stalled:
            self.status_motor_stalled.setText('Yes')
        else:
            self.status_motor_stalled.setText('No')

        self.status_actual_motor_current.setText(str(update.actual_motor_current))

        if update.full_step_active:
            self.status_full_step_active.setText('Yes')
        else:
            self.status_full_step_active.setText('No')

        self.status_stallguard_result.setText(str(update.stallguard_result))
        self.status_stealth_voltage_amplitude.setText(str(update.stealth_voltage_amplitude))

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
                self.enable_checkbox.blockSignals(True)
                self.enable_checkbox.setChecked(True)
                self.enable_checkbox.blockSignals(False)
        else:
            if self.enable_checkbox.isChecked():
                self.endis_all(False)
                self.enable_checkbox.blockSignals(True)
                self.enable_checkbox.setChecked(False)
                self.enable_checkbox.blockSignals(False)

    def get_step_configuration_async(self, conf):
        self.step_resolution_dropbox.blockSignals(True)
        self.step_resolution_dropbox.setCurrentIndex(conf.step_resolution)
        self.step_resolution_dropbox.blockSignals(False)

        self.interpolate_checkbox.blockSignals(True)
        self.interpolate_checkbox.setChecked(conf.interpolation)
        self.interpolate_checkbox.blockSignals(False)

    def get_basic_configuration_async(self, conf):
        self.standstill_current_spin.blockSignals(True)
        self.standstill_current_spin.setValue(conf.standstill_current)
        self.standstill_current_spin.blockSignals(False)

        self.motor_run_current_spin.blockSignals(True)
        self.motor_run_current_spin.setValue(conf.motor_run_current)
        self.motor_run_current_spin.blockSignals(False)

        self.standstill_delay_time_spin.blockSignals(True)
        self.standstill_delay_time_spin.setValue(conf.standstill_delay_time)
        self.standstill_delay_time_spin.blockSignals(False)

        self.power_down_time_spin.blockSignals(True)
        self.power_down_time_spin.setValue(conf.power_down_time)
        self.power_down_time_spin.blockSignals(False)

        self.stealth_threshold_spin.blockSignals(True)
        self.stealth_threshold_spin.setValue(conf.stealth_threshold)
        self.stealth_threshold_spin.blockSignals(False)

        self.coolstep_threashold_spin.blockSignals(True)
        self.coolstep_threashold_spin.setValue(conf.coolstep_threshold)
        self.coolstep_threashold_spin.blockSignals(False)

        self.classic_threshold_spin.blockSignals(True)
        self.classic_threshold_spin.setValue(conf.classic_threshold)
        self.classic_threshold_spin.blockSignals(False)

        self.high_velocity_chopper_mode_checkbox.blockSignals(True)
        self.high_velocity_chopper_mode_checkbox.setChecked(conf.high_velocity_chopper_mode)
        self.high_velocity_chopper_mode_checkbox.blockSignals(False)

    def get_spreadcycle_configuration_async(self, conf):
        self.slow_decay_duration_spin.blockSignals(True)
        self.slow_decay_duration_spin.setValue(conf.slow_decay_duration)
        self.slow_decay_duration_spin.blockSignals(False)

        self.enable_random_slow_decay_checkbox.blockSignals(True)
        self.enable_random_slow_decay_checkbox.setChecked(conf.enable_random_slow_decay)
        self.enable_random_slow_decay_checkbox.blockSignals(False)

        self.fast_decay_duration_spin.blockSignals(True)
        self.fast_decay_duration_spin.setValue(conf.fast_decay_duration)
        self.fast_decay_duration_spin.blockSignals(False)

        self.hysteresis_start_value_spin.blockSignals(True)
        self.hysteresis_start_value_spin.setValue(conf.hysteresis_start_value)
        self.hysteresis_start_value_spin.blockSignals(False)

        self.hysteresis_end_value_spin.blockSignals(True)
        self.hysteresis_end_value_spin.setValue(conf.hysteresis_end_value)
        self.hysteresis_end_value_spin.blockSignals(False)

        self.sine_wave_offset_spin.blockSignals(True)
        self.sine_wave_offset_spin.setValue(conf.sine_wave_offset)
        self.sine_wave_offset_spin.blockSignals(False)

        self.chopper_mode_combo.blockSignals(True)
        self.chopper_mode_combo.setCurrentIndex(conf.chopper_mode)
        self.chopper_mode_combo.blockSignals(False)

        self.standstill_current_spin.blockSignals(True)
        self.comparator_blank_time_combo.setCurrentIndex(conf.comparator_blank_time)
        self.standstill_current_spin.blockSignals(False)

        self.fast_decay_without_comparator_checkbox.blockSignals(True)
        self.fast_decay_without_comparator_checkbox.setChecked(conf.fast_decay_without_comparator)
        self.fast_decay_without_comparator_checkbox.blockSignals(False)


    def get_stealth_configuration_async(self, conf):
        self.enable_stealth_checkbox.blockSignals(True)
        self.enable_stealth_checkbox.setChecked(conf.enable_stealth)
        self.enable_stealth_checkbox.blockSignals(False)

        self.amplitude_spin.blockSignals(True)
        self.amplitude_spin.setValue(conf.amplitude)
        self.amplitude_spin.blockSignals(False)

        self.gradient_spin.blockSignals(True)
        self.gradient_spin.setValue(conf.gradient)
        self.gradient_spin.blockSignals(False)

        self.enable_autoscale_checkbox.blockSignals(True)
        self.enable_autoscale_checkbox.setChecked(conf.enable_autoscale)
        self.enable_autoscale_checkbox.blockSignals(False)

        self.force_symmetric_checkbox.blockSignals(True)
        self.force_symmetric_checkbox.setChecked(conf.force_symmetric)
        self.force_symmetric_checkbox.blockSignals(False)

        self.freewheel_mode_combo.blockSignals(True)
        self.freewheel_mode_combo.setCurrentIndex(conf.freewheel_mode)
        self.freewheel_mode_combo.blockSignals(False)

    def get_coolstep_configuration_async(self, conf):
        self.minimum_stallguard_value_spin.blockSignals(True)
        self.minimum_stallguard_value_spin.setValue(conf.minimum_stallguard_value)
        self.minimum_stallguard_value_spin.blockSignals(False)

        self.maximum_stallguard_value_spin.blockSignals(True)
        self.maximum_stallguard_value_spin.setValue(conf.maximum_stallguard_value)
        self.maximum_stallguard_value_spin.blockSignals(False)

        self.current_up_step_width_combo.blockSignals(True)
        self.current_up_step_width_combo.setCurrentIndex(conf.current_up_step_width)
        self.current_up_step_width_combo.blockSignals(False)

        self.current_down_step_width_combo.blockSignals(True)
        self.current_down_step_width_combo.setCurrentIndex(conf.current_down_step_width)
        self.current_down_step_width_combo.blockSignals(False)

        self.minimum_current_combo.blockSignals(True)
        self.minimum_current_combo.setCurrentIndex(conf.minimum_current)
        self.minimum_current_combo.blockSignals(False)

        self.stallguard_threshold_value_spin.blockSignals(True)
        self.stallguard_threshold_value_spin.setValue(conf.stallguard_threshold_value)
        self.stallguard_threshold_value_spin.blockSignals(False)

        self.stallguard_mode_combo.blockSignals(True)
        self.stallguard_mode_combo.setCurrentIndex(conf.stallguard_mode)
        self.stallguard_mode_combo.blockSignals(False)

    def get_misc_configuration_async(self, conf):
        self.disable_short_to_ground_protection_checkbox.blockSignals(True)
        self.disable_short_to_ground_protection_checkbox.setChecked(conf.disable_short_to_ground_protection)
        self.disable_short_to_ground_protection_checkbox.blockSignals(False)

        self.synchronize_phase_frequency_spin.blockSignals(True)
        self.synchronize_phase_frequency_spin.setValue(conf.synchronize_phase_frequency)
        self.synchronize_phase_frequency_spin.blockSignals(False)

    def update_start(self):
        async_call(self.silent_stepper.get_max_velocity, None, self.get_max_velocity_async, self.increase_error_count)
        async_call(self.silent_stepper.get_speed_ramping, None, self.get_speed_ramping_async, self.increase_error_count)
        async_call(self.silent_stepper.is_enabled, None, self.is_enabled_async, self.increase_error_count)
        async_call(self.silent_stepper.get_step_configuration, None, self.get_step_configuration_async, self.increase_error_count)
        async_call(self.silent_stepper.get_basic_configuration, None, self.get_basic_configuration_async, self.increase_error_count)
        async_call(self.silent_stepper.get_spreadcycle_configuration, None, self.get_spreadcycle_configuration_async, self.increase_error_count)
        async_call(self.silent_stepper.get_stealth_configuration, None, self.get_stealth_configuration_async, self.increase_error_count)
        async_call(self.silent_stepper.get_coolstep_configuration, None, self.get_coolstep_configuration_async, self.increase_error_count)
        async_call(self.silent_stepper.get_misc_configuration, None, self.get_misc_configuration_async, self.increase_error_count)

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
            async_call(self.silent_stepper.get_driver_status, None, self.driver_status_update, self.increase_error_count)

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
