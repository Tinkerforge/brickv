# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-08-23.      #
#                                                           #
# Python Bindings Version 2.1.23                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetTemperatureCallbackThreshold = namedtuple('TemperatureCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletTemperature(Device):
    """
    Measures ambient temperature with 0.5°C accuracy
    """

    DEVICE_IDENTIFIER = 216
    DEVICE_DISPLAY_NAME = 'Temperature Bricklet'
    DEVICE_URL_PART = 'temperature' # internal

    CALLBACK_TEMPERATURE = 8
    CALLBACK_TEMPERATURE_REACHED = 9


    FUNCTION_GET_TEMPERATURE = 1
    FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD = 2
    FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD = 3
    FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_I2C_MODE = 10
    FUNCTION_GET_I2C_MODE = 11
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    I2C_MODE_FAST = 0
    I2C_MODE_SLOW = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 1)

        self.response_expected[BrickletTemperature.FUNCTION_GET_TEMPERATURE] = BrickletTemperature.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD] = BrickletTemperature.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD] = BrickletTemperature.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletTemperature.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletTemperature.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletTemperature.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletTemperature.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_SET_I2C_MODE] = BrickletTemperature.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletTemperature.FUNCTION_GET_I2C_MODE] = BrickletTemperature.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperature.FUNCTION_GET_IDENTITY] = BrickletTemperature.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletTemperature.CALLBACK_TEMPERATURE] = 'h'
        self.callback_formats[BrickletTemperature.CALLBACK_TEMPERATURE_REACHED] = 'h'


    def get_temperature(self):
        """
        Returns the temperature of the sensor. The value
        has a range of -2500 to 8500 and is given in °C/100,
        e.g. a value of 4223 means that a temperature of 42.23 °C is measured.

        If you want to get the temperature periodically, it is recommended
        to use the :cb:`Temperature` callback and set the period with
        :func:`Set Temperature Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletTemperature.FUNCTION_GET_TEMPERATURE, (), '', 'h')

    def set_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Temperature` callback is only triggered if the temperature has changed
        since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletTemperature.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_temperature_callback_period(self):
        """
        Returns the period as set by :func:`Set Temperature Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletTemperature.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Temperature Reached` callback.

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
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletTemperature.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Temperature Callback Threshold`.
        """
        return GetTemperatureCallbackThreshold(*self.ipcon.send_request(self, BrickletTemperature.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback

        * :cb:`Temperature Reached`

        is triggered, if the threshold

        * :func:`Set Temperature Callback Threshold`

        keeps being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletTemperature.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletTemperature.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_i2c_mode(self, mode):
        """
        Sets the I2C mode. Possible modes are:

        * 0: Fast (400kHz, default)
        * 1: Slow (100kHz)

        If you have problems with obvious outliers in the
        Temperature Bricklet measurements, they may be caused by EMI issues.
        In this case it may be helpful to lower the I2C speed.

        It is however not recommended to lower the I2C speed in applications where
        a high throughput needs to be achieved.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        mode = int(mode)

        self.ipcon.send_request(self, BrickletTemperature.FUNCTION_SET_I2C_MODE, (mode,), 'B', '')

    def get_i2c_mode(self):
        """
        Returns the I2C mode as set by :func:`Set I2C Mode`.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        return self.ipcon.send_request(self, BrickletTemperature.FUNCTION_GET_I2C_MODE, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletTemperature.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

Temperature = BrickletTemperature # for backward compatibility
