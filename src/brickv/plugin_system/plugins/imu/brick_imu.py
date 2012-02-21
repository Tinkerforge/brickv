# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-02-17.      #
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
GetQuaternion = namedtuple('Quaternion', ['x', 'y', 'z', 'w'])
GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class IMU(Device):
    CALLBACK_ACCELERATION = 31
    CALLBACK_MAGNETIC_FIELD = 32
    CALLBACK_ANGULAR_VELOCITY = 33
    CALLBACK_ALL_DATA = 34
    CALLBACK_ORIENTATION = 35
    CALLBACK_QUATERNION = 36

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
    TYPE_SET_CONVERGENCE_SPEED = 15
    TYPE_GET_CONVERGENCE_SPEED = 16
    TYPE_SET_CALIBRATION = 17
    TYPE_GET_CALIBRATION = 18
    TYPE_SET_ACCELERATION_PERIOD = 19
    TYPE_GET_ACCELERATION_PERIOD = 20
    TYPE_SET_MAGNETIC_FIELD_PERIOD = 21
    TYPE_GET_MAGNETIC_FIELD_PERIOD = 22
    TYPE_SET_ANGULAR_VELOCITY_PERIOD = 23
    TYPE_GET_ANGULAR_VELOCITY_PERIOD = 24
    TYPE_SET_ALL_DATA_PERIOD = 25
    TYPE_GET_ALL_DATA_PERIOD = 26
    TYPE_SET_ORIENTATION_PERIOD = 27
    TYPE_GET_ORIENTATION_PERIOD = 28
    TYPE_SET_QUATERNION_PERIOD = 29
    TYPE_GET_QUATERNION_PERIOD = 30
    TYPE_ACCELERATION = 31
    TYPE_MAGNETIC_FIELD = 32
    TYPE_ANGULAR_VELOCITY = 33
    TYPE_ALL_DATA = 34
    TYPE_ORIENTATION = 35
    TYPE_QUATERNION = 36

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[IMU.CALLBACK_ACCELERATION] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_MAGNETIC_FIELD] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_ANGULAR_VELOCITY] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_ALL_DATA] = 'h h h h h h h h h h'
        self.callbacks_format[IMU.CALLBACK_ORIENTATION] = 'h h h'
        self.callbacks_format[IMU.CALLBACK_QUATERNION] = 'f f f f'

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

    def set_convergence_speed(self, speed):
        self.ipcon.write(self, IMU.TYPE_SET_CONVERGENCE_SPEED, (speed,), 'H', '')

    def get_convergence_speed(self):
        return self.ipcon.write(self, IMU.TYPE_GET_CONVERGENCE_SPEED, (), '', 'H')

    def set_calibration(self, typ, data):
        self.ipcon.write(self, IMU.TYPE_SET_CALIBRATION, (typ, data), 'B 10h', '')

    def get_calibration(self, typ):
        return self.ipcon.write(self, IMU.TYPE_GET_CALIBRATION, (typ,), 'B', '10h')

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
