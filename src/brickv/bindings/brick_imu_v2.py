# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-04-09.      #
#                                                           #
# Bindings Version 2.1.4                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

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
GetOrientation = namedtuple('Orientation', ['roll', 'pitch', 'heading'])
GetLinearAcceleration = namedtuple('LinearAcceleration', ['x', 'y', 'z'])
GetGravityVector = namedtuple('GravityVector', ['x', 'y', 'z'])
GetQuaternion = namedtuple('Quaternion', ['w', 'x', 'y', 'z'])
GetAllData = namedtuple('AllData', ['acceleration', 'magnetic_field', 'angular_velocity', 'euler_angle', 'quaternion', 'linear_acceleration', 'gravity_vector', 'temperature', 'calibration_status'])
GetProtocol1BrickletName = namedtuple('Protocol1BrickletName', ['protocol_version', 'firmware_version', 'name'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickIMUV2(Device):
    """
    Device for sensing acceleration, magnetic field and angular velocity
    """

    DEVICE_IDENTIFIER = 18
    DEVICE_DISPLAY_NAME = 'IMU 2.0 Brick'

    CALLBACK_ACCELERATION = 33
    CALLBACK_MAGNETIC_FIELD = 34
    CALLBACK_ANGULAR_VELOCITY = 35
    CALLBACK_TEMPERATURE = 36
    CALLBACK_LINEAR_ACCELERATION = 37
    CALLBACK_GRAVITY_VECTOR = 38
    CALLBACK_ORIENTATION = 39
    CALLBACK_QUATERNION = 40
    CALLBACK_ALL_DATA = 41

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
    FUNCTION_SET_CONFIGURATION = 13
    FUNCTION_GET_CONFIGURATION = 14
    FUNCTION_SET_ACCELERATION_PERIOD = 15
    FUNCTION_GET_ACCELERATION_PERIOD = 16
    FUNCTION_SET_MAGNETIC_FIELD_PERIOD = 17
    FUNCTION_GET_MAGNETIC_FIELD_PERIOD = 18
    FUNCTION_SET_ANGULAR_VELOCITY_PERIOD = 19
    FUNCTION_GET_ANGULAR_VELOCITY_PERIOD = 20
    FUNCTION_SET_TEMPERATURE_PERIOD = 21
    FUNCTION_GET_TEMPERATURE_PERIOD = 22
    FUNCTION_SET_ORIENTATION_PERIOD = 23
    FUNCTION_GET_ORIENTATION_PERIOD = 24
    FUNCTION_SET_LINEAR_ACCELERATION_PERIOD = 25
    FUNCTION_GET_LINEAR_ACCELERATION_PERIOD = 26
    FUNCTION_SET_GRAVITY_VECTOR_PERIOD = 27
    FUNCTION_GET_GRAVITY_VECTOR_PERIOD = 28
    FUNCTION_SET_QUATERNION_PERIOD = 29
    FUNCTION_GET_QUATERNION_PERIOD = 30
    FUNCTION_SET_ALL_DATA_PERIOD = 31
    FUNCTION_GET_ALL_DATA_PERIOD = 32
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
        self.response_expected[BrickIMUV2.FUNCTION_SET_CONFIGURATION] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickIMUV2.FUNCTION_GET_CONFIGURATION] = BrickIMUV2.RESPONSE_EXPECTED_FALSE
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
        self.callback_formats[BrickIMUV2.CALLBACK_QUATERNION] = 'H H H H'
        self.callback_formats[BrickIMUV2.CALLBACK_ALL_DATA] = 'h h h h h h h h h h'

    def get_acceleration(self):
        """
        Returns the calibrated acceleration from the accelerometer for the 
        x, y and z axis in mG (G/1000, 1G = 9.80605m/s²).
        
        If you want to get the acceleration periodically, it is recommended 
        to use the callback :func:`Acceleration` and set the period with 
        :func:`SetAccelerationPeriod`.
        """
        return GetAcceleration(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ACCELERATION, (), '', 'h h h'))

    def get_magnetic_field(self):
        """
        Returns the calibrated magnetic field from the magnetometer for the 
        x, y and z axis in mG (Milligauss or Nanotesla).
        
        If you want to get the magnetic field periodically, it is recommended 
        to use the callback :func:`MagneticField` and set the period with 
        :func:`SetMagneticFieldPeriod`.
        """
        return GetMagneticField(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_MAGNETIC_FIELD, (), '', 'h h h'))

    def get_angular_velocity(self):
        """
        Returns the calibrated angular velocity from the gyroscope for the 
        x, y and z axis in °/14.375s (you have to divide by 14.375 to
        get the value in °/s).
        
        If you want to get the angular velocity periodically, it is recommended 
        to use the callback :func:`AngularVelocity` and set the period with 
        :func:`SetAngularVelocityPeriod`.
        """
        return GetAngularVelocity(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ANGULAR_VELOCITY, (), '', 'h h h'))

    def get_temperature(self):
        """
        Returns the temperature of the IMU Brick. The temperature is given in 
        °C/100.
        """
        return self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_TEMPERATURE, (), '', 'b')

    def get_orientation(self):
        """
        Returns the current orientation (roll, pitch, heading) of the IMU Brick as Euler
        angles in one-hundredth degree. Note that Euler angles always experience a
        `gimbal lock <http://en.wikipedia.org/wiki/Gimbal_lock>`__.
        
        We recommend that you use quaternions instead.
        
        The order to sequence in which the orientation values should be applied is 
        roll, yaw, pitch. 
        
        If you want to get the orientation periodically, it is recommended 
        to use the callback :func:`Orientation` and set the period with 
        :func:`SetOrientationPeriod`.
        """
        return GetOrientation(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ORIENTATION, (), '', 'h h h'))

    def get_linear_acceleration(self):
        """
        TODO
        """
        return GetLinearAcceleration(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_LINEAR_ACCELERATION, (), '', 'h h h'))

    def get_gravity_vector(self):
        """
        TODO
        """
        return GetGravityVector(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_GRAVITY_VECTOR, (), '', 'h h h'))

    def get_quaternion(self):
        """
        Returns the current orientation (x, y, z, w) of the IMU as 
        `quaternions <http://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation>`__.
        
        You can go from quaternions to Euler angles with the following formula::
        
         xAngle = atan2(2*y*w - 2*x*z, 1 - 2*y*y - 2*z*z)
         yAngle = atan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)
         zAngle =  asin(2*x*y + 2*z*w)
        
        This process is not reversible, because of the 
        `gimbal lock <http://en.wikipedia.org/wiki/Gimbal_lock>`__.
        
        It is also possible to calculate independent angles. You can calculate 
        yaw, pitch and roll in a right-handed vehicle coordinate system according to DIN70000
        with::
        
         yaw   =  atan2(2*x*y + 2*w*z, w*w + x*x - y*y - z*z)
         pitch = -asin(2*w*y - 2*x*z)
         roll  = -atan2(2*y*z + 2*w*x, -w*w + x*x + y*y - z*z))
        
        Converting the quaternions to an OpenGL transformation matrix is
        possible with the following formula::
        
         matrix = [[1 - 2*(y*y + z*z),     2*(x*y - w*z),     2*(x*z + w*y), 0],
                   [    2*(x*y + w*z), 1 - 2*(x*x + z*z),     2*(y*z - w*x), 0],
                   [    2*(x*z - w*y),     2*(y*z + w*x), 1 - 2*(x*x + y*y), 0],
                   [                0,                 0,                 0, 1]]
        
        If you want to get the quaternions periodically, it is recommended 
        to use the callback :func:`Quaternion` and set the period with 
        :func:`SetQuaternionPeriod`.
        """
        return GetQuaternion(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_QUATERNION, (), '', 'H H H H'))

    def get_all_data(self):
        """
        TODO
        
        If you want to get the data periodically, it is recommended 
        to use the callback :func:`AllData` and set the period with 
        :func:`SetAllDataPeriod`.
        """
        return GetAllData(*self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_ALL_DATA, (), '', '3h 3h 3h 3h 4H 3h 3h b B'))

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

    def set_configuration(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_SET_CONFIGURATION, (), '', '')

    def get_configuration(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickIMUV2.FUNCTION_GET_CONFIGURATION, (), '', '')

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
