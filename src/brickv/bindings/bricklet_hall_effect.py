# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-08-23.      #
#                                                           #
# Bindings Version 2.0.9                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
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

GetEdgeCountConfig = namedtuple('EdgeCountConfig', ['edge_type', 'debounce'])
EdgeInterrupt = namedtuple('EdgeInterrupt', ['count', 'value'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletHallEffect(Device):
    """
    Device that detects presence of magnetic field via hall effect
    """

    DEVICE_IDENTIFIER = 240

    CALLBACK_EDGE_COUNT = 10

    FUNCTION_GET_VALUE = 1
    FUNCTION_GET_EDGE_COUNT = 2
    FUNCTION_SET_EDGE_COUNT_CONFIG = 3
    FUNCTION_GET_EDGE_COUNT_CONFIG = 4
    FUNCTION_SET_EDGE_INTERRUPT = 5
    FUNCTION_GET_EDGE_INTERRUPT = 6
    FUNCTION_SET_EDGE_COUNT_CALLBACK_PERIOD = 7
    FUNCTION_GET_EDGE_COUNT_CALLBACK_PERIOD = 8
    FUNCTION_EDGE_INTERRUPT = 9
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletHallEffect.FUNCTION_GET_VALUE] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_GET_EDGE_COUNT] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_SET_EDGE_COUNT_CONFIG] = BrickletHallEffect.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHallEffect.FUNCTION_GET_EDGE_COUNT_CONFIG] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_SET_EDGE_INTERRUPT] = BrickletHallEffect.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_GET_EDGE_INTERRUPT] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_SET_EDGE_COUNT_CALLBACK_PERIOD] = BrickletHallEffect.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_GET_EDGE_COUNT_CALLBACK_PERIOD] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHallEffect.FUNCTION_EDGE_INTERRUPT] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHallEffect.CALLBACK_EDGE_COUNT] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletHallEffect.FUNCTION_GET_IDENTITY] = BrickletHallEffect.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletHallEffect.CALLBACK_EDGE_COUNT] = 'I ?'

    def get_value(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_GET_VALUE, (), '', '?')

    def get_edge_count(self, reset_counter):
        """
        
        """
        return self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_GET_EDGE_COUNT, (reset_counter,), '?', 'I')

    def set_edge_count_config(self, edge_type, debounce):
        """
        
        """
        self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_SET_EDGE_COUNT_CONFIG, (edge_type, debounce), 'B B', '')

    def get_edge_count_config(self):
        """
        
        """
        return GetEdgeCountConfig(*self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_GET_EDGE_COUNT_CONFIG, (), '', 'B B'))

    def set_edge_interrupt(self, count):
        """
        Interrupt every count edges
        """
        self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_SET_EDGE_INTERRUPT, (count,), 'I', '')

    def get_edge_interrupt(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_GET_EDGE_INTERRUPT, (), '', 'I')

    def set_edge_count_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`EdgeCount` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`EdgeCount` is only triggered if the edge count has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_SET_EDGE_COUNT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_edge_count_callback_period(self):
        """
        Returns the period as set by :func:`SetEdgeCountCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_GET_EDGE_COUNT_CALLBACK_PERIOD, (), '', 'I')

    def edge_interrupt(self):
        """
        
        """
        return EdgeInterrupt(*self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_EDGE_INTERRUPT, (), '', 'I ?'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletHallEffect.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

HallEffect = BrickletHallEffect # for backward compatibility
