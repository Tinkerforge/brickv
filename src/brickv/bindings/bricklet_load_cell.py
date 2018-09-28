# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-09-28.      #
#                                                           #
# Python Bindings Version 2.1.18                            #
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

GetWeightCallbackThreshold = namedtuple('WeightCallbackThreshold', ['option', 'min', 'max'])
GetConfiguration = namedtuple('Configuration', ['rate', 'gain'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLoadCell(Device):
    """
    Measures weight with a load cell
    """

    DEVICE_IDENTIFIER = 253
    DEVICE_DISPLAY_NAME = 'Load Cell Bricklet'
    DEVICE_URL_PART = 'load_cell' # internal

    CALLBACK_WEIGHT = 17
    CALLBACK_WEIGHT_REACHED = 18


    FUNCTION_GET_WEIGHT = 1
    FUNCTION_SET_WEIGHT_CALLBACK_PERIOD = 2
    FUNCTION_GET_WEIGHT_CALLBACK_PERIOD = 3
    FUNCTION_SET_WEIGHT_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_WEIGHT_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_MOVING_AVERAGE = 8
    FUNCTION_GET_MOVING_AVERAGE = 9
    FUNCTION_LED_ON = 10
    FUNCTION_LED_OFF = 11
    FUNCTION_IS_LED_ON = 12
    FUNCTION_CALIBRATE = 13
    FUNCTION_TARE = 14
    FUNCTION_SET_CONFIGURATION = 15
    FUNCTION_GET_CONFIGURATION = 16
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    RATE_10HZ = 0
    RATE_80HZ = 1
    GAIN_128X = 0
    GAIN_64X = 1
    GAIN_32X = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletLoadCell.FUNCTION_GET_WEIGHT] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_THRESHOLD] = BrickletLoadCell.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_THRESHOLD] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_MOVING_AVERAGE] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_MOVING_AVERAGE] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_LED_ON] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_LED_OFF] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_IS_LED_ON] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_CALIBRATE] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_TARE] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_SET_CONFIGURATION] = BrickletLoadCell.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_CONFIGURATION] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLoadCell.FUNCTION_GET_IDENTITY] = BrickletLoadCell.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLoadCell.CALLBACK_WEIGHT] = 'i'
        self.callback_formats[BrickletLoadCell.CALLBACK_WEIGHT_REACHED] = 'i'


    def get_weight(self):
        """
        Returns the currently measured weight in grams.

        If you want to get the weight periodically, it is recommended
        to use the :cb:`Weight` callback and set the period with
        :func:`Set Weight Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_WEIGHT, (), '', 'i')

    def set_weight_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Weight` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Weight` callback is only triggered if the weight has changed since the
        last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_weight_callback_period(self):
        """
        Returns the period as set by :func:`Set Weight Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_PERIOD, (), '', 'I')

    def set_weight_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Weight Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the weight is *outside* the min and max values"
         "'i'",    "Callback is triggered when the weight is *inside* the min and max values"
         "'<'",    "Callback is triggered when the weight is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the weight is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_WEIGHT_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_weight_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Weight Callback Threshold`.
        """
        return GetWeightCallbackThreshold(*self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_WEIGHT_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback

        * :cb:`Weight Reached`

        is triggered, if the threshold

        * :func:`Set Weight Callback Threshold`

        keeps being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the weight value.

        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.

        The range for the averaging is 1-40.

        The default value is 4.
        """
        average = int(average)

        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length moving average as set by :func:`Set Moving Average`.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def led_on(self):
        """
        Turns the LED on.
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_LED_ON, (), '', '')

    def led_off(self):
        """
        Turns the LED off.
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_LED_OFF, (), '', '')

    def is_led_on(self):
        """
        Returns *true* if the led is on, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_IS_LED_ON, (), '', '!')

    def calibrate(self, weight):
        """
        To calibrate your Load Cell Bricklet you have to

        * empty the scale and call this function with 0 and
        * add a known weight to the scale and call this function with the weight in
          grams.

        The calibration is saved in the EEPROM of the Bricklet and only
        needs to be done once.

        We recommend to use the Brick Viewer for calibration, you don't need
        to call this function in your source code.
        """
        weight = int(weight)

        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_CALIBRATE, (weight,), 'I', '')

    def tare(self):
        """
        Sets the currently measured weight as tare weight.
        """
        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_TARE, (), '', '')

    def set_configuration(self, rate, gain):
        """
        The measurement rate and gain are configurable.

        The rate can be either 10Hz or 80Hz. A faster rate will produce more noise.
        It is additionally possible to add a moving average
        (see :func:`Set Moving Average`) to the measurements.

        The gain can be 128x, 64x or 32x. It represents a measurement range of
        ±20mV, ±40mV and ±80mV respectively. The Load Cell Bricklet uses an
        excitation voltage of 5V and most load cells use an output of 2mV/V. That
        means the voltage range is ±15mV for most load cells (i.e. gain of 128x
        is best). If you don't know what all of this means you should keep it at
        128x, it will most likely be correct.

        The configuration is saved in the EEPROM of the Bricklet and only
        needs to be done once.

        We recommend to use the Brick Viewer for configuration, you don't need
        to call this function in your source code.

        The default rate is 10Hz and the default gain is 128x.
        """
        rate = int(rate)
        gain = int(gain)

        self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_SET_CONFIGURATION, (rate, gain), 'B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`Set Configuration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLoadCell.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

LoadCell = BrickletLoadCell # for backward compatibility
