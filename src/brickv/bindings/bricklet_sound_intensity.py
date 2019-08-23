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

GetIntensityCallbackThreshold = namedtuple('IntensityCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletSoundIntensity(Device):
    """
    Measures sound intensity
    """

    DEVICE_IDENTIFIER = 238
    DEVICE_DISPLAY_NAME = 'Sound Intensity Bricklet'
    DEVICE_URL_PART = 'sound_intensity' # internal

    CALLBACK_INTENSITY = 8
    CALLBACK_INTENSITY_REACHED = 9


    FUNCTION_GET_INTENSITY = 1
    FUNCTION_SET_INTENSITY_CALLBACK_PERIOD = 2
    FUNCTION_GET_INTENSITY_CALLBACK_PERIOD = 3
    FUNCTION_SET_INTENSITY_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_INTENSITY_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletSoundIntensity.FUNCTION_GET_INTENSITY] = BrickletSoundIntensity.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_SET_INTENSITY_CALLBACK_PERIOD] = BrickletSoundIntensity.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_GET_INTENSITY_CALLBACK_PERIOD] = BrickletSoundIntensity.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_SET_INTENSITY_CALLBACK_THRESHOLD] = BrickletSoundIntensity.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_GET_INTENSITY_CALLBACK_THRESHOLD] = BrickletSoundIntensity.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletSoundIntensity.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletSoundIntensity.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSoundIntensity.FUNCTION_GET_IDENTITY] = BrickletSoundIntensity.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletSoundIntensity.CALLBACK_INTENSITY] = 'H'
        self.callback_formats[BrickletSoundIntensity.CALLBACK_INTENSITY_REACHED] = 'H'


    def get_intensity(self):
        """
        Returns the current sound intensity. The value has a range of
        0 to 4095.

        The value corresponds to the
        `upper envelop <https://en.wikipedia.org/wiki/Envelope_(waves)>`__
        of the signal of the microphone capsule.

        If you want to get the intensity periodically, it is recommended to use the
        :cb:`Intensity` callback and set the period with
        :func:`Set Intensity Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_GET_INTENSITY, (), '', 'H')

    def set_intensity_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Intensity` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Intensity` callback is only triggered if the intensity has changed
        since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_SET_INTENSITY_CALLBACK_PERIOD, (period,), 'I', '')

    def get_intensity_callback_period(self):
        """
        Returns the period as set by :func:`Set Intensity Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_GET_INTENSITY_CALLBACK_PERIOD, (), '', 'I')

    def set_intensity_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Intensity Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the intensity is *outside* the min and max values"
         "'i'",    "Callback is triggered when the intensity is *inside* the min and max values"
         "'<'",    "Callback is triggered when the intensity is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the intensity is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_SET_INTENSITY_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_intensity_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Intensity Callback Threshold`.
        """
        return GetIntensityCallbackThreshold(*self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_GET_INTENSITY_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback

        * :cb:`Intensity Reached`

        is triggered, if the thresholds

        * :func:`Set Intensity Callback Threshold`

        keeps being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletSoundIntensity.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

SoundIntensity = BrickletSoundIntensity # for backward compatibility
