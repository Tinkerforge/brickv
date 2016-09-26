# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-09-08.      #
#                                                           #
# Python Bindings Version 2.1.10                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetAcceleration = namedtuple('Acceleration', ['x', 'y', 'z'])
GetMagneticField = namedtuple('MagneticField', ['x', 'y', 'z'])
GetAngularVelocity = namedtuple('AngularVelocity', ['x', 'y', 'z'])
GetOrientation = namedtuple('Orientation', ['heading', 'roll', 'pitch'])
GetLinearAcceleration = namedtuple('LinearAcceleration', ['x', 'y', 'z'])
GetGravityVector = namedtuple('GravityVector', ['x', 'y', 'z'])
GetQuaternion = namedtuple('Quaternion', ['w', 'x', 'y', 'z'])
GetAllData = namedtuple('AllData', ['acceleration', 'magnetic_field', 'angular_velocity', 'euler_angle', 'quaternion', 'linear_acceleration', 'gravity_vector', 'temperature', 'calibration_status'])
GetProtocol1BrickletName = namedtuple('Protocol1BrickletName', ['protocol_version', 'firmware_version', 'name'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickIMUV2(Device):
    """
    Full fledged AHRS with 9 degrees of freedom
    """

    DEVICE_IDENTIFIER = 18
    DEVICE_DISPLAY_NAME = 'IMU Brick 2.0'

    CALLBACK_ACCELERATION = 32
    CALLBACK_MAGNETIC_FIELD = 33
    CALLBACK_ANGULAR_VELOCITY = 34
    CALLBACK_TEMPERATURE = 35
    CALLBACK_LINEAR_ACCELERATION = 36
    CALLBACK_GRAVITY_VECTOR = 37
    CALLBACK_ORIENTATION = 38
    CALLBACK_QUATERNION = 39
    CALLBACK_ALL_DATA = 40

    FUNCTION_GET_ACCELERATION = 1
    FUNCTION_GET_MAGNETIC_FIELD = 2
    FUNCTION_GET_ANGULAR_VELOCITY = 3
    FUNCTION_GET_TEMPERATURE = 4
    FUNCTION_GET_ORIENTATION = 5
    FUNCTION_GET_LINEAR_ACCELERATION = 6
    FUNCTION_GET_GRAVITY_VECTOR = 7
    FUNCTION_GET_QUATERNION = 8
    FUNCTION_GET_ALL_DATA = 9
    FUNCTION_LEDS_ON = 10
    FUNCTION_LEDS_OFF = 11
    FUNCTION_ARE_LEDS_ON = 12
    FUNCTION_SAVE_CALIBRATION = 13
    FUNCTION_SET_ACCELERATION_PERIOD = 14
    FUNCTION_GET_ACCELERATION_PERIOD = 15
    FUNCTION_SET_MAGNETIC_FIELD_PERIOD = 16
    FUNCTION_GET_MAGNETIC_FIELD_PERIOD = 17
    FUNCTION_SET_ANGULAR_VELOCITY_PERIOD = 18
    FUNCTION_GET_ANGULAR_VELOCITY_PERIOD = 19
    FUNCTION_SET_TEMPERATURE_PERIOD = 20
    FUNCTION_GET_TEMPERATURE_PERIOD = 21
    FUNCTION_SET_ORIENTATION_PERIOD = 22
    FUNCTION_GET_ORIENTATION_PERIOD = 23
    FUNCTION_SET_LINEAR_ACCELERATION_PERIOD = 24
    FUNCTION_GET_LINEAR_ACCELERATION_PERIOD = 25
    FUNCTION_SET_GRAVITY_VECTOR_PERIOD = 26
    FUNCTION_GET_GRAVITY_VECTOR_PERIOD = 27
    FUNCTION_SET_QUATERNION_PERIOD = 28
    FUNCTION_GET_QUATERNION_PERIOD = 29
    FUNCTION_SET_ALL_DATA_PERIOD = 30
    FUNCTION_GET_ALL_DATA_PERIOD = 31
    FUNCTION_ENABLE_STATUS_LED = 238
    FUNCTION_DISABLE_STATUS_LED = 239
    FUNCTION_IS_STATUS_LED_ENABLED = 240
    FUNCTION_GET_PROTOCOL1_BRICKLET_NAME = 241
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickIMUV2.FUNCTION_GET_ACCELERATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_MAGNETIC_FIELD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ANGULAR_VELOCITY] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_TEMPERATURE] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ORIENTATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_LINEAR_ACCELERATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_GRAVITY_VECTOR] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_QUATERNION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ALL_DATA] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_LEDS_ON] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_LEDS_OFF] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_ARE_LEDS_ON] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SAVE_CALIBRATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_ACCELERATION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ACCELERATION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_MAGNETIC_FIELD_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_MAGNETIC_FIELD_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_ANGULAR_VELOCITY_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ANGULAR_VELOCITY_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_TEMPERATURE_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_TEMPERATURE_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_ORIENTATION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ORIENTATION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_LINEAR_ACCELERATION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_LINEAR_ACCELERATION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_GRAVITY_VECTOR_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_GRAVITY_VECTOR_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_QUATERNION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_QUATERNION_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_SET_ALL_DATA_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_ALL_DATA_PERIOD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.CALLBACK_ACCELERATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_MAGNETIC_FIELD] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_ANGULAR_VELOCITY] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_TEMPERATURE] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_LINEAR_ACCELERATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_GRAVITY_VECTOR] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_ORIENTATION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_QUATERNION] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.CALLBACK_ALL_DATA] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_ENABLE_STATUS_LED] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_DISABLE_STATUS_LED] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_IS_STATUS_LED_ENABLED] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_PROTOCOL1_BRICKLET_NAME] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickIMUV2.FUNCTION_RESET] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_GET_IDENTITY] = BrickIMUV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickIMUV2.CALLBACK_ACCELERATION] = 'h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_MAGNETIC_FIELD] = 'h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_ANGULAR_VELOCITY] = 'h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_TEMPERATURE] = 'b'
        self.callback_formats[BrickIMUV2.CALLBACK_LINEAR_ACCELERATION] = 'h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_GRAVITY_VECTOR] = 'h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_ORIENTATION] = 'h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_QUATERNION] = 'h h h h'
        self.callback_formats[BrickIMUV2.CALLBACK_ALL_DATA] = '3h 3h 3h 3h 4h 3h 3h b B'

    def get_acceleration(self):
        """
        Returns the calibrated acceleration from the accelerometer for the 
        x, y and z axis in 1/100 m/s².
        
        If you want to get the acceleration periodically, it is recommended 
        to use the callback :func:`Acceleration` and set the period with 
        :func:`SetAccelerationPeriod`.
        """
        return GetAcceleration(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ACCELERATION, (), '', 'h h h'))

    def get_magnetic_field(self):
        """
        Returns the calibrated magnetic field from the magnetometer for the 
        x, y and z axis in 1/16 µT (Microtesla).
        
        If you want to get the magnetic field periodically, it is recommended 
        to use the callback :func:`MagneticField` and set the period with 
        :func:`SetMagneticFieldPeriod`.
        """
        return GetMagneticField(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_MAGNETIC_FIELD, (), '', 'h h h'))

    def get_angular_velocity(self):
        """
        Returns the calibrated angular velocity from the gyroscope for the 
        x, y and z axis in 1/16 °/s.
        
        If you want to get the angular velocity periodically, it is recommended 
        to use the callback :func:`AngularVelocity` and set the period with 
        :func:`SetAngularVelocityPeriod`.
        """
        return GetAngularVelocity(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ANGULAR_VELOCITY, (), '', 'h h h'))

    def get_temperature(self):
        """
        Returns the temperature of the IMU Brick. The temperature is given in 
        °C. The temperature is measured in the core of the BNO055 IC, it is not the
        ambient temperature
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_TEMPERATURE, (), '', 'b')

    def get_orientation(self):
        """
        Returns the current orientation (heading, roll, pitch) of the IMU Brick as
        independent Euler angles in 1/16 degree. Note that Euler angles always
        experience a `gimbal lock <https://en.wikipedia.org/wiki/Gimbal_lock>`__. We
        recommend that you use quaternions instead, if you need the absolute orientation.
        
        The rotation angle has the following ranges:
        
        * heading: 0° to 360°
        * roll: -90° to +90°
        * pitch: -180° to +180°
        
        If you want to get the orientation periodically, it is recommended 
        to use the callback :func:`Orientation` and set the period with 
        :func:`SetOrientationPeriod`.
        """
        return GetOrientation(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ORIENTATION, (), '', 'h h h'))

    def get_linear_acceleration(self):
        """
        Returns the linear acceleration of the IMU Brick for the
        x, y and z axis in 1/100 m/s².
        
        The linear acceleration is the acceleration in each of the three
        axis of the IMU Brick with the influences of gravity removed.
        
        It is also possible to get the gravity vector with the influence of linear
        acceleration removed, see :func:`GetGravityVector`.
        
        If you want to get the linear acceleration periodically, it is recommended 
        to use the callback :func:`LinearAcceleration` and set the period with 
        :func:`SetLinearAccelerationPeriod`.
        """
        return GetLinearAcceleration(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_LINEAR_ACCELERATION, (), '', 'h h h'))

    def get_gravity_vector(self):
        """
        Returns the current gravity vector of the IMU Brick for the
        x, y and z axis in 1/100 m/s².
        
        The gravity vector is the acceleration that occurs due to gravity.
        Influences of additional linear acceleration are removed.
        
        It is also possible to get the linear acceleration with the influence 
        of gravity removed, see :func:`GetLinearAcceleration`.
        
        If you want to get the gravity vector periodically, it is recommended 
        to use the callback :func:`GravityVector` and set the period with 
        :func:`SetGravityVectorPeriod`.
        """
        return GetGravityVector(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_GRAVITY_VECTOR, (), '', 'h h h'))

    def get_quaternion(self):
        """
        Returns the current orientation (w, x, y, z) of the IMU Brick as
        `quaternions <https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation>`__.
        
        You have to divide the returns values by 16383 (14 bit) to get
        the usual range of -1.0 to +1.0 for quaternions.
        
        If you want to get the quaternions periodically, it is recommended 
        to use the callback :func:`Quaternion` and set the period with 
        :func:`SetQuaternionPeriod`.
        """
        return GetQuaternion(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_QUATERNION, (), '', 'h h h h'))

    def get_all_data(self):
        """
        Return all of the available data of the IMU Brick.
        
        * acceleration in 1/100 m/s² (see :func:`GetAcceleration`)
        * magnetic field in 1/16 µT (see :func:`GetMagneticField`)
        * angular velocity in 1/16 °/s (see :func:`GetAngularVelocity`)
        * Euler angles in 1/16 ° (see :func:`GetOrientation`)
        * quaternion 1/16383 (see :func:`GetQuaternion`)
        * linear acceleration 1/100 m/s² (see :func:`GetLinearAcceleration`)
        * gravity vector 1/100 m/s² (see :func:`GetGravityVector`)
        * temperature in 1 °C (see :func:`GetTemperature`)
        * calibration status (see below)
        
        The calibration status consists of four pairs of two bits. Each pair
        of bits represents the status of the current calibration.
        
        * bit 0-1: Magnetometer
        * bit 2-3: Accelerometer
        * bit 4-5: Gyroscope
        * bit 6-7: System
        
        A value of 0 means for "not calibrated" and a value of 3 means
        "fully calibrated". In your program you should always be able to
        ignore the calibration status, it is used by the calibration
        window of the Brick Viewer and it can be ignored after the first
        calibration. See the documentation in the calibration window for
        more information regarding the calibration of the IMU Brick.
        
        If you want to get the data periodically, it is recommended 
        to use the callback :func:`AllData` and set the period with 
        :func:`SetAllDataPeriod`.
        """
        return GetAllData(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ALL_DATA, (), '', '3h 3h 3h 3h 4h 3h 3h b B'))

    def leds_on(self):
        """
        Turns the orientation and direction LEDs of the IMU Brick on.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_LEDS_ON, (), '', '')

    def leds_off(self):
        """
        Turns the orientation and direction LEDs of the IMU Brick off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_LEDS_OFF, (), '', '')

    def are_leds_on(self):
        """
        Returns *true* if the orientation and direction LEDs of the IMU Brick
        are on, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_ARE_LEDS_ON, (), '', '?')

    def save_calibration(self):
        """
        A call of this function saves the current calibration to be used
        as a starting point for the next restart of continuous calibration
        of the IMU Brick.
        
        A return value of *true* means that the calibration could be used and
        *false* means that it could not be used (this happens if the calibration 
        status is not "fully calibrated").
        
        This function is used by the calibration window of the Brick Viewer, you
        should not need to call it in your program.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SAVE_CALIBRATION, (), '', '?')

    def set_acceleration_period(self, period):
        """
        Sets the period in ms with which the :func:`Acceleration` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_ACCELERATION_PERIOD, (period,), 'I', '')

    def get_acceleration_period(self):
        """
        Returns the period as set by :func:`SetAccelerationPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ACCELERATION_PERIOD, (), '', 'I')

    def set_magnetic_field_period(self, period):
        """
        Sets the period in ms with which the :func:`MagneticField` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_MAGNETIC_FIELD_PERIOD, (period,), 'I', '')

    def get_magnetic_field_period(self):
        """
        Returns the period as set by :func:`SetMagneticFieldPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_MAGNETIC_FIELD_PERIOD, (), '', 'I')

    def set_angular_velocity_period(self, period):
        """
        Sets the period in ms with which the :func:`AngularVelocity` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_ANGULAR_VELOCITY_PERIOD, (period,), 'I', '')

    def get_angular_velocity_period(self):
        """
        Returns the period as set by :func:`SetAngularVelocityPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ANGULAR_VELOCITY_PERIOD, (), '', 'I')

    def set_temperature_period(self, period):
        """
        Sets the period in ms with which the :func:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_TEMPERATURE_PERIOD, (period,), 'I', '')

    def get_temperature_period(self):
        """
        Returns the period as set by :func:`SetTemperaturePeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_TEMPERATURE_PERIOD, (), '', 'I')

    def set_orientation_period(self, period):
        """
        Sets the period in ms with which the :func:`Orientation` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_ORIENTATION_PERIOD, (period,), 'I', '')

    def get_orientation_period(self):
        """
        Returns the period as set by :func:`SetOrientationPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ORIENTATION_PERIOD, (), '', 'I')

    def set_linear_acceleration_period(self, period):
        """
        Sets the period in ms with which the :func:`LinearAcceleration` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_LINEAR_ACCELERATION_PERIOD, (period,), 'I', '')

    def get_linear_acceleration_period(self):
        """
        Returns the period as set by :func:`SetLinearAccelerationPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_LINEAR_ACCELERATION_PERIOD, (), '', 'I')

    def set_gravity_vector_period(self, period):
        """
        Sets the period in ms with which the :func:`GravityVector` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_GRAVITY_VECTOR_PERIOD, (period,), 'I', '')

    def get_gravity_vector_period(self):
        """
        Returns the period as set by :func:`SetGravityVectorPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_GRAVITY_VECTOR_PERIOD, (), '', 'I')

    def set_quaternion_period(self, period):
        """
        Sets the period in ms with which the :func:`Quaternion` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_QUATERNION_PERIOD, (period,), 'I', '')

    def get_quaternion_period(self):
        """
        Returns the period as set by :func:`SetQuaternionPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_QUATERNION_PERIOD, (), '', 'I')

    def set_all_data_period(self, period):
        """
        Sets the period in ms with which the :func:`AllData` callback is triggered
        periodically. A value of 0 turns the callback off.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_ALL_DATA_PERIOD, (period,), 'I', '')

    def get_all_data_period(self):
        """
        Returns the period as set by :func:`SetAllDataPeriod`.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ALL_DATA_PERIOD, (), '', 'I')

    def enable_status_led(self):
        """
        Enables the status LED.
        
        The status LED is the blue LED next to the USB connector. If enabled is is
        on and it flickers if data is transfered. If disabled it is always off.
        
        The default state is enabled.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_ENABLE_STATUS_LED, (), '', '')

    def disable_status_led(self):
        """
        Disables the status LED.
        
        The status LED is the blue LED next to the USB connector. If enabled is is
        on and it flickers if data is transfered. If disabled it is always off.
        
        The default state is enabled.
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_DISABLE_STATUS_LED, (), '', '')

    def is_status_led_enabled(self):
        """
        Returns *true* if the status LED is enabled, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_IS_STATUS_LED_ENABLED, (), '', '?')

    def get_protocol1_bricklet_name(self, port):
        """
        Returns the firmware and protocol version and the name of the Bricklet for a
        given port.
        
        This functions sole purpose is to allow automatic flashing of v1.x.y Bricklet
        plugins.
        """
        return GetProtocol1BrickletName(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_PROTOCOL1_BRICKLET_NAME, (port,), 'c', 'B 3B 40s'))

    def get_chip_temperature(self):
        """
        Returns the temperature in °C/10 as measured inside the microcontroller. The
        value returned is not the ambient temperature!
        
        The temperature is only proportional to the real temperature and it has an
        accuracy of +-15%. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Brick. Calling this function
        on a Brick inside of a stack will reset the whole stack.
        
        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_RESET, (), '', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Brick is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be '0'-'8' (stack position).
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

IMUV2 = BrickIMUV2 # for backward compatibility
