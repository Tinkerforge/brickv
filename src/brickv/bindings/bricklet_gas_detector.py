# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-11-27.      #
#                                                           #
# Python Bindings Version 2.1.24                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetValueCallbackThreshold = namedtuple('ValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletGasDetector(Device):
    """
    Measures concentration of different gases
    """

    DEVICE_IDENTIFIER = 252
    DEVICE_DISPLAY_NAME = 'Gas Detector Bricklet'
    DEVICE_URL_PART = 'gas_detector' # internal

    CALLBACK_VALUE = 15
    CALLBACK_VALUE_REACHED = 16


    FUNCTION_GET_VALUE = 1
    FUNCTION_SET_VALUE_CALLBACK_PERIOD = 2
    FUNCTION_GET_VALUE_CALLBACK_PERIOD = 3
    FUNCTION_SET_VALUE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_VALUE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_MOVING_AVERAGE = 8
    FUNCTION_GET_MOVING_AVERAGE = 9
    FUNCTION_SET_DETECTOR_TYPE = 10
    FUNCTION_GET_DETECTOR_TYPE = 11
    FUNCTION_HEATER_ON = 12
    FUNCTION_HEATER_OFF = 13
    FUNCTION_IS_HEATER_ON = 14
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    DETECTOR_TYPE_0 = 0
    DETECTOR_TYPE_1 = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletGasDetector.FUNCTION_GET_VALUE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_THRESHOLD] = BrickletGasDetector.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_THRESHOLD] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_MOVING_AVERAGE] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_MOVING_AVERAGE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_DETECTOR_TYPE] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_DETECTOR_TYPE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_HEATER_ON] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_HEATER_OFF] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_IS_HEATER_ON] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_IDENTITY] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletGasDetector.CALLBACK_VALUE] = 'H'
        self.callback_formats[BrickletGasDetector.CALLBACK_VALUE_REACHED] = 'H'


    def get_value(self):
        """
        Returns a value between 0 and 4095.

        See `here <TODO>`__ for more information about the measurements.

        If you want to get the value periodically, it is recommended
        to use the :cb:`Value` callback and set the period with
        :func:`Set Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_VALUE, (), '', 'H')

    def set_value_callback_period(self, period):
        """
        Sets the period with which the :cb:`Value` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Value` callback is only triggered if the value value has changed
        since the last triggering.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_value_callback_period(self):
        """
        Returns the period as set by :func:`Set Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_value_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Value Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the value value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the value value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the value value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the value value is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Value Callback Threshold`.
        """
        return GetValueCallbackThreshold(*self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period with which the threshold callback

        * :cb:`Value Reached`

        is triggered, if the threshold

        * :func:`Set Value Callback Threshold`

        keeps being reached.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the measured value.

        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.

        The range for the averaging is 1-100.

        The default value is 100.
        """
        average = int(average)

        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length moving average as set by :func:`Set Moving Average`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def set_detector_type(self, detector_type):
        """
        Sets the detector type.

        The following types are currently supported.

        * Type 0: MQ2 and MQ5
        * Type 1: MQ3

        The detector type is written to the EEPROM of the Bricklet, so it only has
        to be set once.

        You can use the Brick Viewer to set the detector type, so you likely
        don't need to use this function in your source code.

        The default detector type is 0.
        """
        detector_type = int(detector_type)

        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_DETECTOR_TYPE, (detector_type,), 'B', '')

    def get_detector_type(self):
        """
        Returns the detector type as set by :func:`Set Detector Type`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_DETECTOR_TYPE, (), '', 'B')

    def heater_on(self):
        """
        Turns the internal heater on.
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_HEATER_ON, (), '', '')

    def heater_off(self):
        """
        Turns the internal heater off.
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_HEATER_OFF, (), '', '')

    def is_heater_on(self):
        """
        Returns *true* if the heater is on, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_IS_HEATER_ON, (), '', '!')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

GasDetector = BrickletGasDetector # for backward compatibility
