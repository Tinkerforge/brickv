# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-10-05.      #
#                                                           #
# Python Bindings Version 2.1.19                            #
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

GetMonoflop = namedtuple('Monoflop', ['state', 'time', 'time_remaining'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletSolidStateRelay(Device):
    """
    Controls AC and DC Solid State Relays
    """

    DEVICE_IDENTIFIER = 244
    DEVICE_DISPLAY_NAME = 'Solid State Relay Bricklet'
    DEVICE_URL_PART = 'solid_state_relay' # internal

    CALLBACK_MONOFLOP_DONE = 5


    FUNCTION_SET_STATE = 1
    FUNCTION_GET_STATE = 2
    FUNCTION_SET_MONOFLOP = 3
    FUNCTION_GET_MONOFLOP = 4
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletSolidStateRelay.FUNCTION_SET_STATE] = BrickletSolidStateRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSolidStateRelay.FUNCTION_GET_STATE] = BrickletSolidStateRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSolidStateRelay.FUNCTION_SET_MONOFLOP] = BrickletSolidStateRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSolidStateRelay.FUNCTION_GET_MONOFLOP] = BrickletSolidStateRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSolidStateRelay.FUNCTION_GET_IDENTITY] = BrickletSolidStateRelay.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletSolidStateRelay.CALLBACK_MONOFLOP_DONE] = '!'


    def set_state(self, state):
        """
        Sets the state of the relays *true* means on and *false* means off.

        Running monoflop timers will be overwritten if this function is called.

        The default value is *false*.
        """
        state = bool(state)

        self.ipcon.send_request(self, BrickletSolidStateRelay.FUNCTION_SET_STATE, (state,), '!', '')

    def get_state(self):
        """
        Returns the state of the relay, *true* means on and *false* means off.
        """
        return self.ipcon.send_request(self, BrickletSolidStateRelay.FUNCTION_GET_STATE, (), '', '!')

    def set_monoflop(self, state, time):
        """
        The first parameter  is the desired state of the relay (*true* means on
        and *false* means off). The second parameter indicates the time (in ms) that
        the relay should hold the state.

        If this function is called with the parameters (true, 1500):
        The relay will turn on and in 1.5s it will turn off again.

        A monoflop can be used as a failsafe mechanism. For example: Lets assume you
        have a RS485 bus and a Solid State Relay Bricklet connected to one of the slave
        stacks. You can now call this function every second, with a time parameter
        of two seconds. The relay will be on all the time. If now the RS485
        connection is lost, the relay will turn off in at most two seconds.
        """
        state = bool(state)
        time = int(time)

        self.ipcon.send_request(self, BrickletSolidStateRelay.FUNCTION_SET_MONOFLOP, (state, time), '! I', '')

    def get_monoflop(self):
        """
        Returns the current state and the time as set by
        :func:`Set Monoflop` as well as the remaining time until the state flips.

        If the timer is not running currently, the remaining time will be returned
        as 0.
        """
        return GetMonoflop(*self.ipcon.send_request(self, BrickletSolidStateRelay.FUNCTION_GET_MONOFLOP, (), '', '! I I'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletSolidStateRelay.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

SolidStateRelay = BrickletSolidStateRelay # for backward compatibility
