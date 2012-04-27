# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-04-27.      #
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

GetSpeedRamping = namedtuple('SpeedRamping', ['acceleration', 'deacceleration'])
GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class Stepper(Device):
    CALLBACK_UNDER_VOLTAGE = 31
    CALLBACK_POSITION_REACHED = 32

    TYPE_SET_MAX_VELOCITY = 1
    TYPE_GET_MAX_VELOCITY = 2
    TYPE_GET_CURRENT_VELOCITY = 3
    TYPE_SET_SPEED_RAMPING = 4
    TYPE_GET_SPEED_RAMPING = 5
    TYPE_FULL_BRAKE = 6
    TYPE_SET_CURRENT_POSITION = 7
    TYPE_GET_CURRENT_POSITION = 8
    TYPE_SET_TARGET_POSITION = 9
    TYPE_GET_TARGET_POSITION = 10
    TYPE_SET_STEPS = 11
    TYPE_GET_STEPS = 12
    TYPE_GET_REMAINING_STEPS = 13
    TYPE_SET_STEP_MODE = 14
    TYPE_GET_STEP_MODE = 15
    TYPE_DRIVE_FORWARD = 16
    TYPE_DRIVE_BACKWARD = 17
    TYPE_STOP = 18
    TYPE_GET_STACK_INPUT_VOLTAGE = 19
    TYPE_GET_EXTERNAL_INPUT_VOLTAGE = 20
    TYPE_GET_CURRENT_CONSUMPTION = 21
    TYPE_SET_MOTOR_CURRENT = 22
    TYPE_GET_MOTOR_CURRENT = 23
    TYPE_ENABLE = 24
    TYPE_DISABLE = 25
    TYPE_IS_ENABLED = 26
    TYPE_SET_DECAY = 27
    TYPE_GET_DECAY = 28
    TYPE_SET_MINIMUM_VOLTAGE = 29
    TYPE_GET_MINIMUM_VOLTAGE = 30
    TYPE_UNDER_VOLTAGE = 31
    TYPE_POSITION_REACHED = 32
    TYPE_SET_SYNC_RECT = 33
    TYPE_IS_SYNC_RECT = 34

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[Stepper.CALLBACK_UNDER_VOLTAGE] = 'H'
        self.callbacks_format[Stepper.CALLBACK_POSITION_REACHED] = 'i'

    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def set_max_velocity(self, velocity):
        self.ipcon.write(self, Stepper.TYPE_SET_MAX_VELOCITY, (velocity,), 'H', '')

    def get_max_velocity(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_MAX_VELOCITY, (), '', 'H')

    def get_current_velocity(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_CURRENT_VELOCITY, (), '', 'H')

    def set_speed_ramping(self, acceleration, deacceleration):
        self.ipcon.write(self, Stepper.TYPE_SET_SPEED_RAMPING, (acceleration, deacceleration), 'H H', '')

    def get_speed_ramping(self):
        return GetSpeedRamping(*self.ipcon.write(self, Stepper.TYPE_GET_SPEED_RAMPING, (), '', 'H H'))

    def full_brake(self):
        self.ipcon.write(self, Stepper.TYPE_FULL_BRAKE, (), '', '')

    def set_current_position(self, position):
        self.ipcon.write(self, Stepper.TYPE_SET_CURRENT_POSITION, (position,), 'i', '')

    def get_current_position(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_CURRENT_POSITION, (), '', 'i')

    def set_target_position(self, position):
        self.ipcon.write(self, Stepper.TYPE_SET_TARGET_POSITION, (position,), 'i', '')

    def get_target_position(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_TARGET_POSITION, (), '', 'i')

    def set_steps(self, steps):
        self.ipcon.write(self, Stepper.TYPE_SET_STEPS, (steps,), 'i', '')

    def get_steps(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_STEPS, (), '', 'i')

    def get_remaining_steps(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_REMAINING_STEPS, (), '', 'i')

    def set_step_mode(self, mode):
        self.ipcon.write(self, Stepper.TYPE_SET_STEP_MODE, (mode,), 'B', '')

    def get_step_mode(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_STEP_MODE, (), '', 'B')

    def drive_forward(self):
        self.ipcon.write(self, Stepper.TYPE_DRIVE_FORWARD, (), '', '')

    def drive_backward(self):
        self.ipcon.write(self, Stepper.TYPE_DRIVE_BACKWARD, (), '', '')

    def stop(self):
        self.ipcon.write(self, Stepper.TYPE_STOP, (), '', '')

    def get_stack_input_voltage(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_STACK_INPUT_VOLTAGE, (), '', 'H')

    def get_external_input_voltage(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_EXTERNAL_INPUT_VOLTAGE, (), '', 'H')

    def get_current_consumption(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_CURRENT_CONSUMPTION, (), '', 'H')

    def set_motor_current(self, current):
        self.ipcon.write(self, Stepper.TYPE_SET_MOTOR_CURRENT, (current,), 'H', '')

    def get_motor_current(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_MOTOR_CURRENT, (), '', 'H')

    def enable(self):
        self.ipcon.write(self, Stepper.TYPE_ENABLE, (), '', '')

    def disable(self):
        self.ipcon.write(self, Stepper.TYPE_DISABLE, (), '', '')

    def is_enabled(self):
        return self.ipcon.write(self, Stepper.TYPE_IS_ENABLED, (), '', '?')

    def set_decay(self, decay):
        self.ipcon.write(self, Stepper.TYPE_SET_DECAY, (decay,), 'H', '')

    def get_decay(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_DECAY, (), '', 'H')

    def set_minimum_voltage(self, voltage):
        self.ipcon.write(self, Stepper.TYPE_SET_MINIMUM_VOLTAGE, (voltage,), 'H', '')

    def get_minimum_voltage(self):
        return self.ipcon.write(self, Stepper.TYPE_GET_MINIMUM_VOLTAGE, (), '', 'H')

    def set_sync_rect(self, sync_rect):
        self.ipcon.write(self, Stepper.TYPE_SET_SYNC_RECT, (sync_rect,), '?', '')

    def is_sync_rect(self):
        return self.ipcon.write(self, Stepper.TYPE_IS_SYNC_RECT, (), '', '?')
