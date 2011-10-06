# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2011-10-06.      #
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

GetPulseWidth = namedtuple('PulseWidth', ['min', 'max'])
GetDegree = namedtuple('Degree', ['min', 'max'])
GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class Servo(Device):
    CALLBACK_UNDER_VOLTAGE = 26
    CALLBACK_POSITION_REACHED = 27
    CALLBACK_VELOCITY_REACHED = 28

    TYPE_ENABLE = 1
    TYPE_DISABLE = 2
    TYPE_IS_ENABLED = 3
    TYPE_SET_POSITION = 4
    TYPE_GET_POSITION = 5
    TYPE_GET_CURRENT_POSITION = 6
    TYPE_SET_VELOCITY = 7
    TYPE_GET_VELOCITY = 8
    TYPE_GET_CURRENT_VELOCITY = 9
    TYPE_SET_ACCELERATION = 10
    TYPE_GET_ACCELERATION = 11
    TYPE_SET_OUTPUT_VOLTAGE = 12
    TYPE_GET_OUTPUT_VOLTAGE = 13
    TYPE_SET_PULSE_WIDTH = 14
    TYPE_GET_PULSE_WIDTH = 15
    TYPE_SET_DEGREE = 16
    TYPE_GET_DEGREE = 17
    TYPE_SET_PERIOD = 18
    TYPE_GET_PERIOD = 19
    TYPE_GET_SERVO_CURRENT = 20
    TYPE_GET_OVERALL_CURRENT = 21
    TYPE_GET_STACK_INPUT_VOLTAGE = 22
    TYPE_GET_EXTERNAL_INPUT_VOLTAGE = 23
    TYPE_SET_MINIMUM_VOLTAGE = 24
    TYPE_GET_MINIMUM_VOLTAGE = 25
    TYPE_UNDER_VOLTAGE = 26
    TYPE_POSITION_REACHED = 27
    TYPE_VELOCITY_REACHED = 28

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[Servo.CALLBACK_UNDER_VOLTAGE] = 'H'
        self.callbacks_format[Servo.CALLBACK_POSITION_REACHED] = 'B h'
        self.callbacks_format[Servo.CALLBACK_VELOCITY_REACHED] = 'B h'

    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def enable(self, servo_num):
        self.ipcon.write(self, Servo.TYPE_ENABLE, (servo_num,), 'B', '')

    def disable(self, servo_num):
        self.ipcon.write(self, Servo.TYPE_DISABLE, (servo_num,), 'B', '')

    def is_enabled(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_IS_ENABLED, (servo_num,), 'B', '?')

    def set_position(self, servo_num, position):
        self.ipcon.write(self, Servo.TYPE_SET_POSITION, (servo_num, position), 'B h', '')

    def get_position(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_POSITION, (servo_num,), 'B', 'h')

    def get_current_position(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_CURRENT_POSITION, (servo_num,), 'B', 'h')

    def set_velocity(self, servo_num, velocity):
        self.ipcon.write(self, Servo.TYPE_SET_VELOCITY, (servo_num, velocity), 'B H', '')

    def get_velocity(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_VELOCITY, (servo_num,), 'B', 'H')

    def get_current_velocity(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_CURRENT_VELOCITY, (servo_num,), 'B', 'H')

    def set_acceleration(self, servo_num, acceleration):
        self.ipcon.write(self, Servo.TYPE_SET_ACCELERATION, (servo_num, acceleration), 'B H', '')

    def get_acceleration(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_ACCELERATION, (servo_num,), 'B', 'H')

    def set_output_voltage(self, voltage):
        self.ipcon.write(self, Servo.TYPE_SET_OUTPUT_VOLTAGE, (voltage,), 'H', '')

    def get_output_voltage(self):
        return self.ipcon.write(self, Servo.TYPE_GET_OUTPUT_VOLTAGE, (), '', 'H')

    def set_pulse_width(self, servo_num, min, max):
        self.ipcon.write(self, Servo.TYPE_SET_PULSE_WIDTH, (servo_num, min, max), 'B H H', '')

    def get_pulse_width(self, servo_num):
        return GetPulseWidth(*self.ipcon.write(self, Servo.TYPE_GET_PULSE_WIDTH, (servo_num,), 'B', 'H H'))

    def set_degree(self, servo_num, min, max):
        self.ipcon.write(self, Servo.TYPE_SET_DEGREE, (servo_num, min, max), 'B h h', '')

    def get_degree(self, servo_num):
        return GetDegree(*self.ipcon.write(self, Servo.TYPE_GET_DEGREE, (servo_num,), 'B', 'h h'))

    def set_period(self, servo_num, period):
        self.ipcon.write(self, Servo.TYPE_SET_PERIOD, (servo_num, period), 'B H', '')

    def get_period(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_PERIOD, (servo_num,), 'B', 'H')

    def get_servo_current(self, servo_num):
        return self.ipcon.write(self, Servo.TYPE_GET_SERVO_CURRENT, (servo_num,), 'B', 'H')

    def get_overall_current(self):
        return self.ipcon.write(self, Servo.TYPE_GET_OVERALL_CURRENT, (), '', 'H')

    def get_stack_input_voltage(self):
        return self.ipcon.write(self, Servo.TYPE_GET_STACK_INPUT_VOLTAGE, (), '', 'H')

    def get_external_input_voltage(self):
        return self.ipcon.write(self, Servo.TYPE_GET_EXTERNAL_INPUT_VOLTAGE, (), '', 'H')

    def set_minimum_voltage(self, voltage):
        self.ipcon.write(self, Servo.TYPE_SET_MINIMUM_VOLTAGE, (voltage,), 'H', '')

    def get_minimum_voltage(self):
        return self.ipcon.write(self, Servo.TYPE_GET_MINIMUM_VOLTAGE, (), '', 'H')
