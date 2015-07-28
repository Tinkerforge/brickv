# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-07-28.      #
#                                                           #
# Bindings Version 2.1.5                                    #
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

GetIlluminanceCallbackThreshold = namedtuple('IlluminanceCallbackThreshold', ['option', 'min', 'max'])
GetConfiguration = namedtuple('Configuration', ['illuminance_range', 'integration_time'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletAmbientLightV2(Device):
    """
    Measures ambient light up to 64000lux
    """

    DEVICE_IDENTIFIER = 259
    DEVICE_DISPLAY_NAME = 'Ambient Light Bricklet 2.0'

    CALLBACK_ILLUMINANCE = 10
    CALLBACK_ILLUMINANCE_REACHED = 11

    FUNCTION_GET_ILLUMINANCE = 1
    FUNCTION_SET_ILLUMINANCE_CALLBACK_PERIOD = 2
    FUNCTION_GET_ILLUMINANCE_CALLBACK_PERIOD = 3
    FUNCTION_SET_ILLUMINANCE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_ILLUMINANCE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_CONFIGURATION = 8
    FUNCTION_GET_CONFIGURATION = 9
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    ILLUMINANCE_RANGE_64000LUX = 0
    ILLUMINANCE_RANGE_32000LUX = 1
    ILLUMINANCE_RANGE_16000LUX = 2
    ILLUMINANCE_RANGE_8000LUX = 3
    ILLUMINANCE_RANGE_1300LUX = 4
    ILLUMINANCE_RANGE_600LUX = 5
    INTEGRATION_TIME_50MS = 0
    INTEGRATION_TIME_100MS = 1
    INTEGRATION_TIME_150MS = 2
    INTEGRATION_TIME_200MS = 3
    INTEGRATION_TIME_250MS = 4
    INTEGRATION_TIME_300MS = 5
    INTEGRATION_TIME_350MS = 6
    INTEGRATION_TIME_400MS = 7

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletAmbientLightV2.FUNCTION_GET_ILLUMINANCE] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_SET_ILLUMINANCE_CALLBACK_PERIOD] = BrickletAmbientLightV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_GET_ILLUMINANCE_CALLBACK_PERIOD] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_SET_ILLUMINANCE_CALLBACK_THRESHOLD] = BrickletAmbientLightV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_GET_ILLUMINANCE_CALLBACK_THRESHOLD] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletAmbientLightV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_SET_CONFIGURATION] = BrickletAmbientLightV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_GET_CONFIGURATION] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAmbientLightV2.CALLBACK_ILLUMINANCE] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletAmbientLightV2.CALLBACK_ILLUMINANCE_REACHED] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletAmbientLightV2.FUNCTION_GET_IDENTITY] = BrickletAmbientLightV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletAmbientLightV2.CALLBACK_ILLUMINANCE] = 'I'
        self.callback_formats[BrickletAmbientLightV2.CALLBACK_ILLUMINANCE_REACHED] = 'I'

    def get_illuminance(self):
        """
        Returns the illuminance of the ambient light sensor. The value
        has a range of 0 to 6400000 and is given in 1/100 Lux, i.e. a value
        of 45000 means that an illuminance of 450 Lux is measured.
        
        If you want to get the illuminance periodically, it is recommended to use the
        callback :func:`Illuminance` and set the period with 
        :func:`SetIlluminanceCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_GET_ILLUMINANCE, (), '', 'I')

    def set_illuminance_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Illuminance` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Illuminance` is only triggered if the illuminance has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_SET_ILLUMINANCE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_illuminance_callback_period(self):
        """
        Returns the period as set by :func:`SetIlluminanceCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_GET_ILLUMINANCE_CALLBACK_PERIOD, (), '', 'I')

    def set_illuminance_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`IlluminanceReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the illuminance is *outside* the min and max values"
         "'i'",    "Callback is triggered when the illuminance is *inside* the min and max values"
         "'<'",    "Callback is triggered when the illuminance is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the illuminance is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_SET_ILLUMINANCE_CALLBACK_THRESHOLD, (option, min, max), 'c I I', '')

    def get_illuminance_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetIlluminanceCallbackThreshold`.
        """
        return GetIlluminanceCallbackThreshold(*self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_GET_ILLUMINANCE_CALLBACK_THRESHOLD, (), '', 'c I I'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`IlluminanceReached`,
        
        are triggered, if the thresholds
        
        * :func:`SetIlluminanceCallbackThreshold`,
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_configuration(self, illuminance_range, integration_time):
        """
        Sets the configuration. It is possible to configure an illuminance range
        between 0-600lux and 0-64000lux and an integration time between 50ms and 400ms.
        
        A smaller illuminance range increases the resolution of the data. An
        increase in integration time will result in less noise on the data.
        
        The default values are 0-8000lux illuminance range and 200ms integration time.
        """
        self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_SET_CONFIGURATION, (illuminance_range, integration_time), 'B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`SetConfiguration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletAmbientLightV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

AmbientLightV2 = BrickletAmbientLightV2 # for backward compatibility
