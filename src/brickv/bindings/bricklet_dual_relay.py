# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-05-31.      #
#                                                           #
# Python Bindings Version 2.1.9                             #
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

GetState = namedtuple('State', ['relay1', 'relay2'])
GetMonoflop = namedtuple('Monoflop', ['state', 'time', 'time_remaining'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletDualRelay(Device):
    """
    Two relays to switch AC/DC devices
    """

    DEVICE_IDENTIFIER = 26
    DEVICE_DISPLAY_NAME = 'Dual Relay Bricklet'

    CALLBACK_MONOFLOP_DONE = 5

    FUNCTION_SET_STATE = 1
    FUNCTION_GET_STATE = 2
    FUNCTION_SET_MONOFLOP = 3
    FUNCTION_GET_MONOFLOP = 4
    FUNCTION_SET_SELECTED_STATE = 6
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletDualRelay.FUNCTION_SET_STATE] = BrickletDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelay.FUNCTION_GET_STATE] = BrickletDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelay.FUNCTION_SET_MONOFLOP] = BrickletDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelay.FUNCTION_GET_MONOFLOP] = BrickletDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelay.CALLBACK_MONOFLOP_DONE] = BrickletDualRelay.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletDualRelay.FUNCTION_SET_SELECTED_STATE] = BrickletDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelay.FUNCTION_GET_IDENTITY] = BrickletDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletDualRelay.CALLBACK_MONOFLOP_DONE] = 'B ?'

    def set_state(self, relay1, relay2):
        """
        Sets the state of the relays, *true* means on and *false* means off. 
        For example: (true, false) turns relay 1 on and relay 2 off.
        
        If you just want to set one of the relays and don't know the current state
        of the other relay, you can get the state with :func:`GetState` or you
        can use :func:`SetSelectedState`.
        
        Running monoflop timers will be overwritten if this function is called.
        
        The default value is (*false*, *false*).
        """
        self.ipcon.send_request(self, BrickletDualRelay.FUNCTION_SET_STATE, (relay1, relay2), '? ?', '')

    def get_state(self):
        """
        Returns the state of the relays, *true* means on and *false* means off.
        """
        return GetState(*self.ipcon.send_request(self, BrickletDualRelay.FUNCTION_GET_STATE, (), '', '? ?'))

    def set_monoflop(self, relay, state, time):
        """
        The first parameter can be 1 or 2 (relay 1 or relay 2). The second parameter 
        is the desired state of the relay (*true* means on and *false* means off).
        The third parameter indicates the time (in ms) that the relay should hold 
        the state.
        
        If this function is called with the parameters (1, true, 1500):
        Relay 1 will turn on and in 1.5s it will turn off again.
        
        A monoflop can be used as a failsafe mechanism. For example: Lets assume you 
        have a RS485 bus and a Dual Relay Bricklet connected to one of the slave 
        stacks. You can now call this function every second, with a time parameter
        of two seconds. The relay will be on all the time. If now the RS485 
        connection is lost, the relay will turn off in at most two seconds.
        """
        self.ipcon.send_request(self, BrickletDualRelay.FUNCTION_SET_MONOFLOP, (relay, state, time), 'B ? I', '')

    def get_monoflop(self, relay):
        """
        Returns (for the given relay) the current state and the time as set by 
        :func:`SetMonoflop` as well as the remaining time until the state flips.
        
        If the timer is not running currently, the remaining time will be returned
        as 0.
        """
        return GetMonoflop(*self.ipcon.send_request(self, BrickletDualRelay.FUNCTION_GET_MONOFLOP, (relay,), 'B', '? I I'))

    def set_selected_state(self, relay, state):
        """
        Sets the state of the selected relay (1 or 2), *true* means on and *false* means off. 
        
        The other relay remains untouched.
        """
        self.ipcon.send_request(self, BrickletDualRelay.FUNCTION_SET_SELECTED_STATE, (relay, state), 'B ?', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletDualRelay.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

DualRelay = BrickletDualRelay # for backward compatibility
