# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2017-09-29.      #
#                                                           #
# Python Bindings Version 2.1.14                            #
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

GetMoistureCallbackConfiguration = namedtuple('MoistureCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletMoistureV2(Device):
    """
    Measures soil moisture
    """

    DEVICE_IDENTIFIER = 287
    DEVICE_DISPLAY_NAME = 'Moisture Bricklet 2.0'

    CALLBACK_MOISTURE = 4


    FUNCTION_GET_MOISTURE = 1
    FUNCTION_SET_MOISTURE_CALLBACK_CONFIGURATION = 2
    FUNCTION_GET_MOISTURE_CALLBACK_CONFIGURATION = 3
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

        self.response_expected[BrickletMoistureV2.FUNCTION_GET_MOISTURE] = BrickletMoistureV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoistureV2.FUNCTION_SET_MOISTURE_CALLBACK_CONFIGURATION] = BrickletMoistureV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMoistureV2.FUNCTION_GET_MOISTURE_CALLBACK_CONFIGURATION] = BrickletMoistureV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoistureV2.FUNCTION_GET_IDENTITY] = BrickletMoistureV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletMoistureV2.CALLBACK_MOISTURE] = 'H'


    def get_moisture(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletMoistureV2.FUNCTION_GET_MOISTURE, (), '', 'H')

    def set_moisture_callback_configuration(self, period, value_has_to_change, option, min, max):
        """
        TODO
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletMoistureV2.FUNCTION_SET_MOISTURE_CALLBACK_CONFIGURATION, (period, value_has_to_change, option, min, max), 'I ! c H H', '')

    def get_moisture_callback_configuration(self):
        """
        TODO
        """
        return GetMoistureCallbackConfiguration(*self.ipcon.send_request(self, BrickletMoistureV2.FUNCTION_GET_MOISTURE_CALLBACK_CONFIGURATION, (), '', 'I ! c H H'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletMoistureV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

MoistureV2 = BrickletMoistureV2 # for backward compatibility
