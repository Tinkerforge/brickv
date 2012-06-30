# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-06-30.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from .ip_connection import namedtuple
from .ip_connection import Device, IPConnection, Error

GetState = namedtuple('State', ['relay1', 'relay2'])
GetMonoflop = namedtuple('Monoflop', ['state', 'time', 'time_remaining'])

class DualRelay(Device):
    """
    Device for controlling two relays
    """

    CALLBACK_MONOFLOP_DONE = 5

    FUNCTION_SET_STATE = 1
    FUNCTION_GET_STATE = 2
    FUNCTION_SET_MONOFLOP = 3
    FUNCTION_GET_MONOFLOP = 4

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Dual Relay Bricklet'

        self.binding_version = [1, 0, 0]

        self.callback_formats[DualRelay.CALLBACK_MONOFLOP_DONE] = 'B ?'

    def set_state(self, relay1, relay2):
        """
        Sets the state of the relays, *true* means on and *false* means off. 
        For example: (true, false) turns relay 1 on and relay 2 off.
        
        If you just want to set one of the relays and don't know the current state
        of the other relay, you can get the state with :func:`GetState`.
        
        Running monoflop timers will be overwritten if this function is called.
        
        The default value is (false, false).
        """
        self.ipcon.send_request(self, DualRelay.FUNCTION_SET_STATE, (relay1, relay2), '? ?', '')

    def get_state(self):
        """
        Returns the state of the relays, *true* means on and *false* means off.
        """
        return GetState(*self.ipcon.send_request(self, DualRelay.FUNCTION_GET_STATE, (), '', '? ?'))

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
        self.ipcon.send_request(self, DualRelay.FUNCTION_SET_MONOFLOP, (relay, state, time), 'B ? I', '')

    def get_monoflop(self, relay):
        """
        Returns (for the given relay) the current state and the time as set by 
        func:`SetMonoflop` as well as the remaining time until the state flips. 
        
        If the timer is not running currently, the remaining time will be returned
        as 0.
        """
        return GetMonoflop(*self.ipcon.send_request(self, DualRelay.FUNCTION_GET_MONOFLOP, (relay,), 'B', '? I I'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
