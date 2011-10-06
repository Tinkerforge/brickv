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

GetAcceleration = namedtuple('Acceleration', ['x', 'y', 'z'])
GetMagneticField = namedtuple('MagneticField', ['x', 'y', 'z'])
GetAngularVelocity = namedtuple('AngularVelocity', ['x', 'y', 'z'])
GetAllData = namedtuple('AllData', ['acc_x', 'acc_y', 'acc_z', 'mag_x', 'mag_y', 'mag_z', 'ang_x', 'ang_y', 'ang_z', 'temperature'])
GetOrientation = namedtuple('Orientation', ['roll', 'pitch', 'yaw'])
GetQuaternion = namedtuple('Quaternion', ['w', 'x', 'y', 'z'])
GetAccelerationThreshold = namedtuple('AccelerationThreshold', ['threshold', 'option'])
GetMagneticFieldThreshold = namedtuple('MagneticFieldThreshold', ['threshold', 'option'])
GetAngularVelocityThreshold = namedtuple('AngularVelocityThreshold', ['threshold', 'option'])
GetAllDataThreshold = namedtuple('AllDataThreshold', ['threshold', 'option'])
GetOrientationThreshold = namedtuple('OrientationThreshold', ['threshold', 'option'])
GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class IMU(Device):
    CALLBACK_ACCELERATION = 40
    CALLBACK_MAGNETIC_FIELD = 41
    CALLBACK_ANGULAR_VELOCITY = 42
    CALLBACK_ALL_DATA = 43
    CALLBACK_ORIENTATION = 44
    CALLBACK_QUATERNION = 45
    CALLBACK_ACCELERATION_REACHED = 46
    CALLBACK_MAGNETIC_FIELD_REACHED = 47
    CALLBACK_ANGULAR_VELOCITY_REACHED = 48
    CALLBACK_ALL_DATA_REACHED = 49
    CALLBACK_ORIENTATION_REACHED = 50

    TYPE_GET_ACCELERATION = 1
    TYPE_GET_MAGNETIC_FIELD = 2
    TYPE_GET_ANGULAR_VELOCITY = 3
    TYPE_GET_ALL_DATA = 4
    TYPE_GET_ORIENTATION = 5
    TYPE_GET_QUATERNION = 6
    TYPE_GET_IMU_TEMPERATURE = 7
    TYPE_LEDS_ON = 8
    TYPE_LEDS_OFF = 9
    TYPE_ARE_LEDS_ON = 10
    TYPE_SET_ACCELERATION_RANGE = 11
    TYPE_GET_ACCELERATION_RANGE = 12
    TYPE_SET_MAGNETOMETER_RANGE = 13
    TYPE_GET_MAGNETOMETER_RANGE = 14
    TYPE_SET_ZERO = 15
    TYPE_SET_DEBOUNCE_PERIOD = 16
    TYPE_GET_DEBOUNCE_PERIOD = 17
    TYPE_SET_ACCELERATION_THRESHOLD = 18
    TYPE_GET_ACCELERATION_THRESHOLD = 19
    TYPE_SET_MAGNETIC_FIELD_THRESHOLD = 20
    TYPE_GET_MAGNETIC_FIELD_THRESHOLD = 21
    TYPE_SET_ANGULAR_VELOCITY_THRESHOLD = 22
    TYPE_GET_ANGULAR_VELOCITY_THRESHOLD = 23
    TYPE_SET_ALL_DATA_THRESHOLD = 24
    TYPE_GET_ALL_DATA_THRESHOLD = 25
    TYPE_SET_ORIENTATION_THRESHOLD = 26
    TYPE_GET_ORIENTATION_THRESHOLD = 27
    TYPE_SET_ACCELERATION_PERIOD = 28
    TYPE_GET_ACCELERATION_PERIOD = 29
    TYPE_SET_MAGNETIC_FIELD_PERIOD = 30
    TYPE_GET_MAGNETIC_FIELD_PERIOD = 31
    TYPE_SET_ANGULAR_VELOCITY_PERIOD = 32
    TYPE_GET_ANGULAR_VELOCITY_PERIOD = 33
    TYPE_SET_ALL_DATA_PERIOD = 34
    TYPE_GET_ALL_DATA_PERIOD = 35
    TYPE_SET_ORIENTATION_PERIOD = 36
    TYPE_GET_ORIENTATION_PERIOD = 37
    TYPE_SET_QUATERNION_PERIOD = 38
    TYPE_GET_QUATERNION_PERIOD = 39
    TYPE_ACCELERATION = 40
    TYPE_MAGNETIC_FIELD = 41
    TYPE_ANGULAR_VELOCITY = 42
    TYPE_ALL_DATA = 43
    TYPE_ORIENTATION = 44
    TYPE_QUATERNION = 45
    TYPE_ACCELERATION_REACHED = 46
    TYPE_MAGNETIC_FIELD_REACHED = 47
    TYPE_ANGULAR_VELOCITY_REACHED = 48
    TYPE_ALL_DATA_REACHED = 49
    TYPE_ORIENTATION_REACHED = 50

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[IMU.CALLBACK_ACCELERATION] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_MAGNETIC_FIELD] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_ANGULAR_VELOCITY] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_ALL_DATA] = 'h h h h h h h h h h'
        self.callbacks_format[IMU.CALLBACK_ORIENTATION] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_QUATERNION] = 'f f f f'
        self.callbacks_format[IMU.CALLBACK_ACCELERATION_REACHED] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_MAGNETIC_FIELD_REACHED] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_ANGULAR_VELOCITY_REACHED] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_ALL_DATA_REACHED] = 'h h h h h h h h h h'
        self.callbacks_format[IMU.CALLBACK_ORIENTATION_REACHED] = 'h h h'

    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def get_acceleration(self):
        return GetAcceleration(*self.ipcon.write(self, IMU.TYPE_GET_ACCELERATION, (), '', 'h h h'))

    def get_magnetic_field(self):
        return GetMagneticField(*self.ipcon.write(self, IMU.TYPE_GET_MAGNETIC_FIELD, (), '', 'h h h'))

    def get_angular_velocity(self):
        return GetAngularVelocity(*self.ipcon.write(self, IMU.TYPE_GET_ANGULAR_VELOCITY, (), '', 'h h h'))

    def get_all_data(self):
        return GetAllData(*self.ipcon.write(self, IMU.TYPE_GET_ALL_DATA, (), '', 'h h h h h h h h h h'))

    def get_orientation(self):
        return GetOrientation(*self.ipcon.write(self, IMU.TYPE_GET_ORIENTATION, (), '', 'h h h'))

    def get_quaternion(self):
        return GetQuaternion(*self.ipcon.write(self, IMU.TYPE_GET_QUATERNION, (), '', 'f f f f'))

    def get_imu_temperature(self):
        return self.ipcon.write(self, IMU.TYPE_GET_IMU_TEMPERATURE, (), '', 'h')

    def leds_on(self):
        self.ipcon.write(self, IMU.TYPE_LEDS_ON, (), '', '')

    def leds_off(self):
        self.ipcon.write(self, IMU.TYPE_LEDS_OFF, (), '', '')

    def are_leds_on(self):
        return self.ipcon.write(self, IMU.TYPE_ARE_LEDS_ON, (), '', '?')

    def set_acceleration_range(self, range):
        self.ipcon.write(self, IMU.TYPE_SET_ACCELERATION_RANGE, (range,), 'B', '')

    def get_acceleration_range(self):
        return self.ipcon.write(self, IMU.TYPE_GET_ACCELERATION_RANGE, (), '', 'B')

    def set_magnetometer_range(self, range):
        self.ipcon.write(self, IMU.TYPE_SET_MAGNETOMETER_RANGE, (range,), 'B', '')

    def get_magnetometer_range(self):
        return self.ipcon.write(self, IMU.TYPE_GET_MAGNETOMETER_RANGE, (), '', 'B')

    def set_zero(self):
        self.ipcon.write(self, IMU.TYPE_SET_ZERO, (), '', '')

    def set_debounce_period(self, debounce_period):
        self.ipcon.write(self, IMU.TYPE_SET_DEBOUNCE_PERIOD, (debounce_period,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_acceleration_threshold(self, num, threshold, option):
        self.ipcon.write(self, IMU.TYPE_SET_ACCELERATION_THRESHOLD, (num, threshold, option), 'B 3h 3c', '')

    def get_acceleration_threshold(self, num):
        return GetAccelerationThreshold(*self.ipcon.write(self, IMU.TYPE_GET_ACCELERATION_THRESHOLD, (num,), 'B', '3h 3c'))

    def set_magnetic_field_threshold(self, num, threshold, option):
        self.ipcon.write(self, IMU.TYPE_SET_MAGNETIC_FIELD_THRESHOLD, (num, threshold, option), 'B 3h 3c', '')

    def get_magnetic_field_threshold(self, num):
        return GetMagneticFieldThreshold(*self.ipcon.write(self, IMU.TYPE_GET_MAGNETIC_FIELD_THRESHOLD, (num,), 'B', '3h 3c'))

    def set_angular_velocity_threshold(self, num, threshold, option):
        self.ipcon.write(self, IMU.TYPE_SET_ANGULAR_VELOCITY_THRESHOLD, (num, threshold, option), 'B 3h 3c', '')

    def get_angular_velocity_threshold(self, num):
        return GetAngularVelocityThreshold(*self.ipcon.write(self, IMU.TYPE_GET_ANGULAR_VELOCITY_THRESHOLD, (num,), 'B', '3h 3c'))

    def set_all_data_threshold(self, num, threshold, option):
        self.ipcon.write(self, IMU.TYPE_SET_ALL_DATA_THRESHOLD, (num, threshold, option), 'B 9h 9c', '')

    def get_all_data_threshold(self, num):
        return GetAllDataThreshold(*self.ipcon.write(self, IMU.TYPE_GET_ALL_DATA_THRESHOLD, (num,), 'B', '9h 9c'))

    def set_orientation_threshold(self, num, threshold, option):
        self.ipcon.write(self, IMU.TYPE_SET_ORIENTATION_THRESHOLD, (num, threshold, option), 'B 3h 3c', '')

    def get_orientation_threshold(self, num):
        return GetOrientationThreshold(*self.ipcon.write(self, IMU.TYPE_GET_ORIENTATION_THRESHOLD, (num,), 'B', '3h 3c'))

    def set_acceleration_period(self, period):
        self.ipcon.write(self, IMU.TYPE_SET_ACCELERATION_PERIOD, (period,), 'I', '')

    def get_acceleration_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_ACCELERATION_PERIOD, (), '', 'I')

    def set_magnetic_field_period(self, period):
        self.ipcon.write(self, IMU.TYPE_SET_MAGNETIC_FIELD_PERIOD, (period,), 'I', '')

    def get_magnetic_field_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_MAGNETIC_FIELD_PERIOD, (), '', 'I')

    def set_angular_velocity_period(self, period):
        self.ipcon.write(self, IMU.TYPE_SET_ANGULAR_VELOCITY_PERIOD, (period,), 'I', '')

    def get_angular_velocity_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_ANGULAR_VELOCITY_PERIOD, (), '', 'I')

    def set_all_data_period(self, period):
        self.ipcon.write(self, IMU.TYPE_SET_ALL_DATA_PERIOD, (period,), 'I', '')

    def get_all_data_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_ALL_DATA_PERIOD, (), '', 'I')

    def set_orientation_period(self, period):
        self.ipcon.write(self, IMU.TYPE_SET_ORIENTATION_PERIOD, (period,), 'I', '')

    def get_orientation_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_ORIENTATION_PERIOD, (), '', 'I')

    def set_quaternion_period(self, period):
        self.ipcon.write(self, IMU.TYPE_SET_QUATERNION_PERIOD, (period,), 'I', '')

    def get_quaternion_period(self):
        return self.ipcon.write(self, IMU.TYPE_GET_QUATERNION_PERIOD, (), '', 'I')
