# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2011-08-23.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from ip_connection import namedtuple
from ip_connection import Device, IPConnection, Error


class DC(Device):
    CALLBACK_UNDER_VOLTAGE = 21
    CALLBACK_EMERGENCY_SHUTDOWN = 22
    CALLBACK_VELOCITY_REACHED = 23
    CALLBACK_CURRENT_VELOCITY = 24

    TYPE_SET_VELOCITY = 1
    TYPE_GET_VELOCITY = 2
    TYPE_GET_CURRENT_VELOCITY = 3
    TYPE_SET_ACCELERATION = 4
    TYPE_GET_ACCELERATION = 5
    TYPE_SET_PWM_FREQUENCY = 6
    TYPE_GET_PWM_FREQUENCY = 7
    TYPE_FULL_BRAKE = 8
    TYPE_GET_STACK_INPUT_VOLTAGE = 9
    TYPE_GET_EXTERNAL_INPUT_VOLTAGE = 10
    TYPE_GET_CURRENT_CONSUMPTION = 11
    TYPE_ENABLE = 12
    TYPE_DISABLE = 13
    TYPE_IS_ENABLED = 14
    TYPE_SET_MINIMUM_VOLTAGE = 15
    TYPE_GET_MINIMUM_VOLTAGE = 16
    TYPE_SET_DRIVE_MODE = 17
    TYPE_GET_DRIVE_MODE = 18
    TYPE_SET_CURRENT_VELOCITY_PERIOD = 19
    TYPE_GET_CURRENT_VELOCITY_PERIOD = 20
    TYPE_UNDER_VOLTAGE = 21
    TYPE_EMERGENCY_SHUTDOWN = 22
    TYPE_VELOCITY_REACHED = 23
    TYPE_CURRENT_VELOCITY = 24

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[DC.CALLBACK_UNDER_VOLTAGE] = 'H'
        self.callbacks_format[DC.CALLBACK_EMERGENCY_SHUTDOWN] = ''
        self.callbacks_format[DC.CALLBACK_VELOCITY_REACHED] = 'h'
        self.callbacks_format[DC.CALLBACK_CURRENT_VELOCITY] = 'h'

    def set_velocity(self, velocity):
        self.ipcon.write(self, DC.TYPE_SET_VELOCITY, (velocity,), 'h', '')

    def get_velocity(self):
        return self.ipcon.write(self, DC.TYPE_GET_VELOCITY, (), '', 'h')

    def get_current_velocity(self):
        return self.ipcon.write(self, DC.TYPE_GET_CURRENT_VELOCITY, (), '', 'h')

    def set_acceleration(self, acceleration):
        self.ipcon.write(self, DC.TYPE_SET_ACCELERATION, (acceleration,), 'H', '')

    def get_acceleration(self):
        return self.ipcon.write(self, DC.TYPE_GET_ACCELERATION, (), '', 'H')

    def set_pwm_frequency(self, frequency):
        self.ipcon.write(self, DC.TYPE_SET_PWM_FREQUENCY, (frequency,), 'H', '')

    def get_pwm_frequency(self):
        return self.ipcon.write(self, DC.TYPE_GET_PWM_FREQUENCY, (), '', 'H')

    def full_brake(self):
        self.ipcon.write(self, DC.TYPE_FULL_BRAKE, (), '', '')

    def get_stack_input_voltage(self):
        return self.ipcon.write(self, DC.TYPE_GET_STACK_INPUT_VOLTAGE, (), '', 'H')

    def get_external_input_voltage(self):
        return self.ipcon.write(self, DC.TYPE_GET_EXTERNAL_INPUT_VOLTAGE, (), '', 'H')

    def get_current_consumption(self):
        return self.ipcon.write(self, DC.TYPE_GET_CURRENT_CONSUMPTION, (), '', 'H')

    def enable(self):
        self.ipcon.write(self, DC.TYPE_ENABLE, (), '', '')

    def disable(self):
        self.ipcon.write(self, DC.TYPE_DISABLE, (), '', '')

    def is_enabled(self):
        return self.ipcon.write(self, DC.TYPE_IS_ENABLED, (), '', '?')

    def set_minimum_voltage(self, voltage):
        self.ipcon.write(self, DC.TYPE_SET_MINIMUM_VOLTAGE, (voltage,), 'H', '')

    def get_minimum_voltage(self):
        return self.ipcon.write(self, DC.TYPE_GET_MINIMUM_VOLTAGE, (), '', 'H')

    def set_drive_mode(self, mode):
        self.ipcon.write(self, DC.TYPE_SET_DRIVE_MODE, (mode,), 'B', '')

    def get_drive_mode(self):
        return self.ipcon.write(self, DC.TYPE_GET_DRIVE_MODE, (), '', 'B')

    def set_current_velocity_period(self, period):
        self.ipcon.write(self, DC.TYPE_SET_CURRENT_VELOCITY_PERIOD, (period,), 'H', '')

    def get_current_velocity_period(self):
        return self.ipcon.write(self, DC.TYPE_GET_CURRENT_VELOCITY_PERIOD, (), '', 'H')
