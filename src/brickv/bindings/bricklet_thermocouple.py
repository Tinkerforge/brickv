# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-11-30.      #
#                                                           #
# Python Bindings Version 2.1.6                             #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
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

GetTemperatureCallbackThreshold = namedtuple('TemperatureCallbackThreshold', ['option', 'min', 'max'])
GetConfiguration = namedtuple('Configuration', ['averaging', 'thermocouple_type', 'filter'])
GetErrorState = namedtuple('ErrorState', ['over_under', 'open_circuit'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletThermocouple(Device):
    """
    Measures temperature with thermocouples
    """

    DEVICE_IDENTIFIER = 266
    DEVICE_DISPLAY_NAME = 'Thermocouple Bricklet'

    CALLBACK_TEMPERATURE = 8
    CALLBACK_TEMPERATURE_REACHED = 9
    CALLBACK_ERROR_STATE = 13

    FUNCTION_GET_TEMPERATURE = 1
    FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD = 2
    FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD = 3
    FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_CONFIGURATION = 10
    FUNCTION_GET_CONFIGURATION = 11
    FUNCTION_GET_ERROR_STATE = 12
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    AVERAGING_1 = 1
    AVERAGING_2 = 2
    AVERAGING_4 = 4
    AVERAGING_8 = 8
    AVERAGING_16 = 16
    TYPE_B = 0
    TYPE_E = 1
    TYPE_J = 2
    TYPE_K = 3
    TYPE_N = 4
    TYPE_R = 5
    TYPE_S = 6
    TYPE_T = 7
    TYPE_G8 = 8
    TYPE_G32 = 9
    FILTER_OPTION_50HZ = 0
    FILTER_OPTION_60HZ = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletThermocouple.FUNCTION_GET_TEMPERATURE] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD] = BrickletThermocouple.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletThermocouple.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletThermocouple.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermocouple.CALLBACK_TEMPERATURE] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletThermocouple.CALLBACK_TEMPERATURE_REACHED] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletThermocouple.FUNCTION_SET_CONFIGURATION] = BrickletThermocouple.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermocouple.FUNCTION_GET_CONFIGURATION] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermocouple.FUNCTION_GET_ERROR_STATE] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermocouple.CALLBACK_ERROR_STATE] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletThermocouple.FUNCTION_GET_IDENTITY] = BrickletThermocouple.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletThermocouple.CALLBACK_TEMPERATURE] = 'i'
        self.callback_formats[BrickletThermocouple.CALLBACK_TEMPERATURE_REACHED] = 'i'
        self.callback_formats[BrickletThermocouple.CALLBACK_ERROR_STATE] = '? ?'

    def get_temperature(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_TEMPERATURE, (), '', 'i')

    def set_temperature_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`TemperatureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the temperature is *outside* the min and max values"
         "'i'",    "Callback is triggered when the temperature is *inside* the min and max values"
         "'<'",    "Callback is triggered when the temperature is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the temperature is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetTemperatureCallbackThreshold`.
        """
        return GetTemperatureCallbackThreshold(*self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`TemperatureReached`
        
        is triggered, if the threshold
        
        * :func:`SetTemperatureCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_configuration(self, averaging, thermocouple_type, filter):
        """
        Conversion time in ms 60Hz: 82 + (samples-1)*16.67
                              50Hz: 98 + (samples-1)*20
        
        G8:  Gain = 8,  value = 8  x 1.6 x 2^17 x V_in
        G32: Gain = 32, value = 32 x 1.6 x 2^17 x V_in
        
        where V_in = thermocouple input voltage
        
        Default: 16, K, 50Hz
        """
        self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_SET_CONFIGURATION, (averaging, thermocouple_type, filter), 'B B B', '')

    def get_configuration(self):
        """
        
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_CONFIGURATION, (), '', 'B B B'))

    def get_error_state(self):
        """
        * Returns current error state
        """
        return GetErrorState(*self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_ERROR_STATE, (), '', '? ?'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletThermocouple.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Thermocouple = BrickletThermocouple # for backward compatibility
