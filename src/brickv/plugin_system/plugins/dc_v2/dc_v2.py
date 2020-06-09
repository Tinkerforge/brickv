# -*- coding: utf-8 -*-
"""
DC 2.0 Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

dc_v2.py: DC 2.0 Plugin implementation

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

from PyQt5.QtWidgets import QErrorMessage, QInputDialog, QAction
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.dc_v2.ui_dc_v2 import Ui_DCV2
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_dc_v2 import BrickletDCV2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.slider_spin_syncer import SliderSpinSyncer

class DCV2(COMCUPluginBase, Ui_DCV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletDCV2, *args)

        self.setupUi(self)

        self.dc = self.device

        self.full_brake_button.clicked.connect(self.full_brake_clicked)
        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        self.radio_mode_brake.toggled.connect(self.brake_value_changed)
        self.radio_mode_coast.toggled.connect(self.coast_value_changed)

        self.gpio0_stop_rising_check.stateChanged.connect(lambda: self.gpio_action_changed(0))
        self.gpio0_stop_falling_check.stateChanged.connect(lambda: self.gpio_action_changed(0))
        self.gpio0_brake_rising_check.stateChanged.connect(lambda: self.gpio_action_changed(0))
        self.gpio0_brake_falling_check.stateChanged.connect(lambda: self.gpio_action_changed(0))
        self.gpio1_stop_rising_check.stateChanged.connect(lambda: self.gpio_action_changed(1))
        self.gpio1_stop_falling_check.stateChanged.connect(lambda: self.gpio_action_changed(1))
        self.gpio1_brake_rising_check.stateChanged.connect(lambda: self.gpio_action_changed(1))
        self.gpio1_brake_falling_check.stateChanged.connect(lambda: self.gpio_action_changed(1))
        self.gpio0_debounce_spin.valueChanged.connect(lambda: self.gpio_configuration_changed(0))
        self.gpio0_stop_deceleration_spin.valueChanged.connect(lambda: self.gpio_configuration_changed(0))
        self.gpio1_debounce_spin.valueChanged.connect(lambda: self.gpio_configuration_changed(1))
        self.gpio1_stop_deceleration_spin.valueChanged.connect(lambda: self.gpio_configuration_changed(1))

        self.velocity_syncer      = SliderSpinSyncer(self.velocity_slider,     self.velocity_spin,     self.velocity_changed)
        self.acceleration_syncer  = SliderSpinSyncer(self.acceleration_slider, self.acceleration_spin, self.motion_changed)
        self.deceleration_syncer  = SliderSpinSyncer(self.deceleration_slider, self.deceleration_spin, self.motion_changed)
        self.frequency_syncer     = SliderSpinSyncer(self.frequency_slider,    self.frequency_spin,    self.frequency_changed)

        self.cbe_power_statistics = CallbackEmulator(self.dc.get_power_statistics, None, self.get_power_statistics_async, self.increase_error_count)
        self.cbe_current_velocity = CallbackEmulator(self.dc.get_current_velocity, None, self.get_current_velocity_async, self.increase_error_count)
        self.cbe_gpio_state       = CallbackEmulator(self.dc.get_gpio_state,       None, self.get_gpio_state_async,       self.increase_error_count)

    def start(self):
        async_call(self.dc.get_drive_mode,    None, self.get_drive_mode_async,    self.increase_error_count)
        async_call(self.dc.get_velocity,      None, self.get_velocity_async,      self.increase_error_count)
        async_call(self.dc.get_motion,        None, self.get_motion_async,        self.increase_error_count)
        async_call(self.dc.get_pwm_frequency, None, self.get_pwm_frequency_async, self.increase_error_count)
        async_call(self.dc.get_enabled,       None, self.get_enabled_async,       self.increase_error_count)

        async_call(self.dc.get_gpio_configuration, 0, lambda x: self.get_gpio_configuration_async(0, x), self.increase_error_count)
        async_call(self.dc.get_gpio_configuration, 1, lambda x: self.get_gpio_configuration_async(1, x), self.increase_error_count)
        async_call(self.dc.get_gpio_action,        0, lambda x: self.get_gpio_action_async(0, x),        self.increase_error_count)
        async_call(self.dc.get_gpio_action,        1, lambda x: self.get_gpio_action_async(1, x),        self.increase_error_count)

        self.cbe_gpio_state.set_period(200)
        self.cbe_power_statistics.set_period(100)
        self.cbe_current_velocity.set_period(50)

    def stop(self):
        self.cbe_gpio_state.set_period(0)
        self.cbe_power_statistics.set_period(0)
        self.cbe_current_velocity.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDCV2.DEVICE_IDENTIFIER

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

    def full_brake_clicked(self):
        try:
            self.dc.full_brake()
            self.velocity_syncer.set_value(0)
        except ip_connection.Error:
            return

    def get_drive_mode_async(self, dm):
        if dm == 0:
            self.radio_mode_brake.setChecked(True)
            self.radio_mode_coast.setChecked(False)
        else:
            self.radio_mode_brake.setChecked(False)
            self.radio_mode_coast.setChecked(True)

    def get_power_statistics_async(self, ps):
        if ps.current >= 1000:
            current_str = "{0}A".format(round(ps.current / 1000.0, 1))
        else:
            current_str = "{0}mA".format(ps.current)

        if ps.voltage >= 1000:
            voltage_str = "{0}V".format(round(ps.voltage / 1000.0, 1))
        else:
            voltage_str = "{0}mV".format(ps.voltage)

        self.current_label.setText(current_str)
        self.input_voltage_label.setText(voltage_str)

    def get_current_velocity_async(self, velocity):
        self.speedometer.set_velocity(velocity)
        self.current_velocity_label.setText('{0} ({1}%)'.format(velocity, round(abs(velocity) * 100 / 32768.0, 1)))

    def get_velocity_async(self, velocity):
        self.velocity_syncer.set_value(velocity)

    def get_motion_async(self, motion):
        self.acceleration_syncer.set_value(motion.acceleration)
        self.deceleration_syncer.set_value(motion.deceleration)

    def get_pwm_frequency_async(self, frequency):
        self.frequency_syncer.set_value(frequency)

    def get_enabled_async(self, enabled):
        self.enable_checkbox.setChecked(enabled)

    def get_gpio_configuration_async(self, channel, conf):
        if channel == 0:
            self.gpio0_debounce_spin.setValue(conf.debounce)
            self.gpio0_stop_deceleration_spin.setValue(conf.stop_deceleration)
        elif channel == 1:
            self.gpio1_debounce_spin.setValue(conf.debounce)
            self.gpio1_stop_deceleration_spin.setValue(conf.stop_deceleration)

    def get_gpio_action_async(self, channel, action):
        if channel == 0:
            self.gpio0_stop_rising_check.setChecked((action & self.dc.GPIO_ACTION_NORMAL_STOP_RISING_EDGE) != 0)
            self.gpio0_stop_falling_check.setChecked((action & self.dc.GPIO_ACTION_NORMAL_STOP_FALLING_EDGE) != 0)
            self.gpio0_brake_rising_check.setChecked((action & self.dc.GPIO_ACTION_FULL_BRAKE_RISING_EDGE) != 0)
            self.gpio0_brake_falling_check.setChecked((action & self.dc.GPIO_ACTION_FULL_BRAKE_FALLING_EDGE) != 0)
        elif channel == 1:
            self.gpio1_stop_rising_check.setChecked((action & self.dc.GPIO_ACTION_NORMAL_STOP_RISING_EDGE) != 0)
            self.gpio1_stop_falling_check.setChecked((action & self.dc.GPIO_ACTION_NORMAL_STOP_FALLING_EDGE) != 0)
            self.gpio1_brake_rising_check.setChecked((action & self.dc.GPIO_ACTION_FULL_BRAKE_RISING_EDGE) != 0)
            self.gpio1_brake_falling_check.setChecked((action & self.dc.GPIO_ACTION_FULL_BRAKE_FALLING_EDGE) != 0)

    def get_gpio_state_async(self, state):
        if state[0]:
            self.gpio0_state_label.setText('High')
        else:
            self.gpio0_state_label.setText('Low')

        if state[1]:
            self.gpio1_state_label.setText('High')
        else:
            self.gpio1_state_label.setText('Low')

    def enable_state_changed(self, state):
        try:
            self.dc.set_enabled(state == Qt.Checked)
        except ip_connection.Error:
            return

    def motion_changed(self, _):
        acceleration = self.acceleration_spin.value()
        deceleration = self.deceleration_spin.value()
        try:
            self.dc.set_motion(acceleration, deceleration)
        except ip_connection.Error:
            return

    def velocity_changed(self, value):
        try:
            self.dc.set_velocity(value)
        except ip_connection.Error:
            return

    def frequency_changed(self, value):
        try:
            self.dc.set_pwm_frequency(value)
        except ip_connection.Error:
            return

    def gpio_action_changed(self, channel):
        action = 0
        if channel == 0:
            if self.gpio0_stop_rising_check.isChecked():   action = action | self.dc.GPIO_ACTION_NORMAL_STOP_RISING_EDGE
            if self.gpio0_stop_falling_check.isChecked():  action = action | self.dc.GPIO_ACTION_NORMAL_STOP_FALLING_EDGE
            if self.gpio0_brake_rising_check.isChecked():  action = action | self.dc.GPIO_ACTION_FULL_BRAKE_RISING_EDGE
            if self.gpio0_brake_falling_check.isChecked(): action = action | self.dc.GPIO_ACTION_FULL_BRAKE_FALLING_EDGE
        elif channel == 1:
            if self.gpio1_stop_rising_check.isChecked():   action = action | self.dc.GPIO_ACTION_NORMAL_STOP_RISING_EDGE
            if self.gpio1_stop_falling_check.isChecked():  action = action | self.dc.GPIO_ACTION_NORMAL_STOP_FALLING_EDGE
            if self.gpio1_brake_rising_check.isChecked():  action = action | self.dc.GPIO_ACTION_FULL_BRAKE_RISING_EDGE
            if self.gpio1_brake_falling_check.isChecked(): action = action | self.dc.GPIO_ACTION_FULL_BRAKE_FALLING_EDGE
        
        # TODO: Retain callback configuration
        self.dc.set_gpio_action(channel, action)

    def gpio_configuration_changed(self, channel):
        if channel == 0:
            debounce          = self.gpio0_debounce_spin.value()
            stop_deceleration = self.gpio0_stop_deceleration_spin.value()
        elif channel == 1:
            debounce          = self.gpio1_debounce_spin.value()
            stop_deceleration = self.gpio1_stop_deceleration_spin.value()

        self.dc.set_gpio_configuration(channel, debounce, stop_deceleration)