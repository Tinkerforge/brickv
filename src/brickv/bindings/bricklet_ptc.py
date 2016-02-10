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

GetTemperatureCallbackThreshold = namedtuple('TemperatureCallbackThreshold', ['option', 'min', 'max'])
GetResistanceCallbackThreshold = namedtuple('ResistanceCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletPTC(Device):
    """
    Reads temperatures from Pt100 und Pt1000 sensors
    """

    DEVICE_IDENTIFIER = 226
    DEVICE_DISPLAY_NAME = 'PTC Bricklet'

    CALLBACK_TEMPERATURE = 13
    CALLBACK_TEMPERATURE_REACHED = 14
    CALLBACK_RESISTANCE = 15
    CALLBACK_RESISTANCE_REACHED = 16

    FUNCTION_GET_TEMPERATURE = 1
    FUNCTION_GET_RESISTANCE = 2
    FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD = 3
    FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD = 4
    FUNCTION_SET_RESISTANCE_CALLBACK_PERIOD = 5
    FUNCTION_GET_RESISTANCE_CALLBACK_PERIOD = 6
    FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_RESISTANCE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_RESISTANCE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12
    FUNCTION_SET_NOISE_REJECTION_FILTER = 17
    FUNCTION_GET_NOISE_REJECTION_FILTER = 18
    FUNCTION_IS_SENSOR_CONNECTED = 19
    FUNCTION_SET_WIRE_MODE = 20
    FUNCTION_GET_WIRE_MODE = 21
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    FILTER_OPTION_50HZ = 0
    FILTER_OPTION_60HZ = 1
    WIRE_MODE_2 = 2
    WIRE_MODE_3 = 3
    WIRE_MODE_4 = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletPTC.FUNCTION_GET_TEMPERATURE] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_RESISTANCE] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD] = BrickletPTC.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_SET_RESISTANCE_CALLBACK_PERIOD] = BrickletPTC.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_RESISTANCE_CALLBACK_PERIOD] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletPTC.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_SET_RESISTANCE_CALLBACK_THRESHOLD] = BrickletPTC.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_RESISTANCE_CALLBACK_THRESHOLD] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletPTC.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.CALLBACK_TEMPERATURE] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPTC.CALLBACK_TEMPERATURE_REACHED] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPTC.CALLBACK_RESISTANCE] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPTC.CALLBACK_RESISTANCE_REACHED] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPTC.FUNCTION_SET_NOISE_REJECTION_FILTER] = BrickletPTC.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTC.FUNCTION_GET_NOISE_REJECTION_FILTER] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_IS_SENSOR_CONNECTED] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_SET_WIRE_MODE] = BrickletPTC.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTC.FUNCTION_GET_WIRE_MODE] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTC.FUNCTION_GET_IDENTITY] = BrickletPTC.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletPTC.CALLBACK_TEMPERATURE] = 'i'
        self.callback_formats[BrickletPTC.CALLBACK_TEMPERATURE_REACHED] = 'i'
        self.callback_formats[BrickletPTC.CALLBACK_RESISTANCE] = 'H'
        self.callback_formats[BrickletPTC.CALLBACK_RESISTANCE_REACHED] = 'H'

    def get_temperature(self):
        """
        Returns the temperature of connected sensor. The value
        has a range of -246 to 849 °C and is given in °C/100,
        e.g. a value of 4223 means that a temperature of 42.23 °C is measured.
        
        If you want to get the temperature periodically, it is recommended 
        to use the callback :func:`Temperature` and set the period with 
        :func:`SetTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_TEMPERATURE, (), '', 'i')

    def get_resistance(self):
        """
        Returns the value as measured by the MAX31865 precision delta-sigma ADC.
        
        The value can be converted with the following formulas:
        
        * Pt100:  resistance = (value * 390) / 32768
        * Pt1000: resistance = (value * 3900) / 32768
        
        If you want to get the resistance periodically, it is recommended 
        to use the callback :func:`Resistance` and set the period with 
        :func:`SetResistanceCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_RESISTANCE, (), '', 'H')

    def set_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Temperature` is only triggered if the temperature has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_resistance_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Resistance` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Resistance` is only triggered if the resistance has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_RESISTANCE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_resistance_callback_period(self):
        """
        Returns the period as set by :func:`SetResistanceCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_RESISTANCE_CALLBACK_PERIOD, (), '', 'I')

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
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetTemperatureCallbackThreshold`.
        """
        return GetTemperatureCallbackThreshold(*self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_resistance_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`ResistanceReached` callback. 
        
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
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_RESISTANCE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_resistance_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetResistanceCallbackThreshold`.
        """
        return GetResistanceCallbackThreshold(*self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_RESISTANCE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`TemperatureReached`,
        * :func:`ResistanceReached`
        
        is triggered, if the threshold
        
        * :func:`SetTemperatureCallbackThreshold`,
        * :func:`SetResistanceCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_noise_rejection_filter(self, filter):
        """
        Sets the noise rejection filter to either 50Hz (0) or 60Hz (1).
        Noise from 50Hz or 60Hz power sources (including
        harmonics of the AC power's fundamental frequency) is
        attenuated by 82dB.
        
        Default value is 0 = 50Hz.
        """
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_NOISE_REJECTION_FILTER, (filter,), 'B', '')

    def get_noise_rejection_filter(self):
        """
        Returns the noise rejection filter option as set by 
        :func:`SetNoiseRejectionFilter`
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_NOISE_REJECTION_FILTER, (), '', 'B')

    def is_sensor_connected(self):
        """
        Returns *true* if the sensor is connected correctly. 
        
        If this function
        returns *false*, there is either no Pt100 or Pt1000 sensor connected,
        the sensor is connected incorrectly or the sensor itself is faulty.
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_IS_SENSOR_CONNECTED, (), '', '?')

    def set_wire_mode(self, mode):
        """
        Sets the wire mode of the sensor. Possible values are 2, 3 and 4 which
        correspond to 2-, 3- and 4-wire sensors. The value has to match the jumper
        configuration on the Bricklet.
        
        The default value is 2 = 2-wire.
        """
        self.ipcon.send_request(self, BrickletPTC.FUNCTION_SET_WIRE_MODE, (mode,), 'B', '')

    def get_wire_mode(self):
        """
        Returns the wire mode as set by :func:`SetWireMode`
        """
        return self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_WIRE_MODE, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletPTC.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

PTC = BrickletPTC # for backward compatibility
