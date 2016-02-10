# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-10.      #
#                                                           #
# Python Bindings Version 2.1.8                             #
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

GetDistanceCallbackThreshold = namedtuple('DistanceCallbackThreshold', ['option', 'min', 'max'])
GetVelocityCallbackThreshold = namedtuple('VelocityCallbackThreshold', ['option', 'min', 'max'])
GetMovingAverage = namedtuple('MovingAverage', ['distance_average_length', 'velocity_average_length'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLaserRangeFinder(Device):
    """
    Measures distance up to 40m with laser light
    """

    DEVICE_IDENTIFIER = 255
    DEVICE_DISPLAY_NAME = 'Laser Range Finder Bricklet'

    CALLBACK_DISTANCE = 20
    CALLBACK_VELOCITY = 21
    CALLBACK_DISTANCE_REACHED = 22
    CALLBACK_VELOCITY_REACHED = 23

    FUNCTION_GET_DISTANCE = 1
    FUNCTION_GET_VELOCITY = 2
    FUNCTION_SET_DISTANCE_CALLBACK_PERIOD = 3
    FUNCTION_GET_DISTANCE_CALLBACK_PERIOD = 4
    FUNCTION_SET_VELOCITY_CALLBACK_PERIOD = 5
    FUNCTION_GET_VELOCITY_CALLBACK_PERIOD = 6
    FUNCTION_SET_DISTANCE_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_DISTANCE_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_VELOCITY_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_VELOCITY_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12
    FUNCTION_SET_MOVING_AVERAGE = 13
    FUNCTION_GET_MOVING_AVERAGE = 14
    FUNCTION_SET_MODE = 15
    FUNCTION_GET_MODE = 16
    FUNCTION_ENABLE_LASER = 17
    FUNCTION_DISABLE_LASER = 18
    FUNCTION_IS_LASER_ENABLED = 19
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    MODE_DISTANCE = 0
    MODE_VELOCITY_MAX_13MS = 1
    MODE_VELOCITY_MAX_32MS = 2
    MODE_VELOCITY_MAX_64MS = 3
    MODE_VELOCITY_MAX_127MS = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_DISTANCE] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_VELOCITY] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_DISTANCE_CALLBACK_PERIOD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_DISTANCE_CALLBACK_PERIOD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_VELOCITY_CALLBACK_PERIOD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_VELOCITY_CALLBACK_PERIOD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_DISTANCE_CALLBACK_THRESHOLD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_DISTANCE_CALLBACK_THRESHOLD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_VELOCITY_CALLBACK_THRESHOLD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_VELOCITY_CALLBACK_THRESHOLD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_MOVING_AVERAGE] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_MOVING_AVERAGE] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_SET_MODE] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_MODE] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_ENABLE_LASER] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_DISABLE_LASER] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_IS_LASER_ENABLED] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLaserRangeFinder.CALLBACK_DISTANCE] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLaserRangeFinder.CALLBACK_VELOCITY] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLaserRangeFinder.CALLBACK_DISTANCE_REACHED] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLaserRangeFinder.CALLBACK_VELOCITY_REACHED] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLaserRangeFinder.FUNCTION_GET_IDENTITY] = BrickletLaserRangeFinder.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLaserRangeFinder.CALLBACK_DISTANCE] = 'H'
        self.callback_formats[BrickletLaserRangeFinder.CALLBACK_VELOCITY] = 'h'
        self.callback_formats[BrickletLaserRangeFinder.CALLBACK_DISTANCE_REACHED] = 'H'
        self.callback_formats[BrickletLaserRangeFinder.CALLBACK_VELOCITY_REACHED] = 'h'

    def get_distance(self):
        """
        Returns the measured distance. The value has a range of 0 to 4000
        and is given in cm.
        
        The Laser Range Finder Bricklet knows different modes. Distances
        are only measured in the distance measurement mode,
        see :func:`SetMode`. Also the laser has to be enabled, see
        :func:`EnableLaser`.
        
        If you want to get the distance periodically, it is recommended to
        use the callback :func:`Distance` and set the period with 
        :func:`SetDistanceCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_DISTANCE, (), '', 'H')

    def get_velocity(self):
        """
        Returns the measured velocity. The value has a range of 0 to 12700
        and is given in 1/100 m/s.
        
        The Laser Range Finder Bricklet knows different modes. Velocity 
        is only measured in the velocity measurement modes, 
        see :func:`SetMode`. Also the laser has to be enabled, see
        :func:`EnableLaser`.
        
        If you want to get the velocity periodically, it is recommended to
        use the callback :func:`Velocity` and set the period with 
        :func:`SetVelocityCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_VELOCITY, (), '', 'h')

    def set_distance_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Distance` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Distance` is only triggered if the distance value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_DISTANCE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_distance_callback_period(self):
        """
        Returns the period as set by :func:`SetDistanceCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_DISTANCE_CALLBACK_PERIOD, (), '', 'I')

    def set_velocity_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Velocity` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Velocity` is only triggered if the velocity value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_VELOCITY_CALLBACK_PERIOD, (period,), 'I', '')

    def get_velocity_callback_period(self):
        """
        Returns the period as set by :func:`SetVelocityCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_VELOCITY_CALLBACK_PERIOD, (), '', 'I')

    def set_distance_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`DistanceReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the distance value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the distance value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the distance value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the distance value is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_DISTANCE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_distance_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetDistanceCallbackThreshold`.
        """
        return GetDistanceCallbackThreshold(*self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_DISTANCE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_velocity_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`VelocityReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the velocity is *outside* the min and max values"
         "'i'",    "Callback is triggered when the velocity is *inside* the min and max values"
         "'<'",    "Callback is triggered when the velocity is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the velocity is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_VELOCITY_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_velocity_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetVelocityCallbackThreshold`.
        """
        return GetVelocityCallbackThreshold(*self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_VELOCITY_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`DistanceReached`,
        * :func:`VelocityReached`,
        
        are triggered, if the thresholds
        
        * :func:`SetDistanceCallbackThreshold`,
        * :func:`SetVelocityCallbackThreshold`,
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, distance_average_length, velocity_average_length):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the distance and velocity.
        
        Setting the length to 0 will turn the averaging completely off. With less
        averaging, there is more noise on the data.
        
        The range for the averaging is 0-30.
        
        The default value is 10.
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_MOVING_AVERAGE, (distance_average_length, velocity_average_length), 'B B', '')

    def get_moving_average(self):
        """
        Returns the length moving average as set by :func:`SetMovingAverage`.
        """
        return GetMovingAverage(*self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B B'))

    def set_mode(self, mode):
        """
        The LIDAR has five different modes. One mode is for distance
        measurements and four modes are for velocity measurements with
        different ranges.
        
        The following modes are available:
        
        * 0: Distance is measured with resolution 1.0 cm and range 0-400 cm
        * 1: Velocity is measured with resolution 0.1 m/s and range is 0-12.7 m/s
        * 2: Velocity is measured with resolution 0.25 m/s and range is 0-31.75 m/s
        * 3: Velocity is measured with resolution 0.5 m/s and range is 0-63.5 m/s
        * 4: Velocity is measured with resolution 1.0 m/s and range is 0-127 m/s
        
        The default mode is 0 (distance is measured).
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_SET_MODE, (mode,), 'B', '')

    def get_mode(self):
        """
        Returns the mode as set by :func:`SetMode`.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_MODE, (), '', 'B')

    def enable_laser(self):
        """
        Activates the laser of the LIDAR.
        
        We recommend that you wait 250ms after enabling the laser before
        the first call of :func:`GetDistance` to ensure stable measurements.
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_ENABLE_LASER, (), '', '')

    def disable_laser(self):
        """
        Deactivates the laser of the LIDAR.
        """
        self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_DISABLE_LASER, (), '', '')

    def is_laser_enabled(self):
        """
        Returns *true* if the laser is enabled, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_IS_LASER_ENABLED, (), '', '?')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLaserRangeFinder.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

LaserRangeFinder = BrickletLaserRangeFinder # for backward compatibility
