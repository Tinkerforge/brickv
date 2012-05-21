# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-18.      #
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

class DualRelay(Device):
    """
    Device for controlling two relays
    """


    FUNCTION_SET_STATE = 1
    FUNCTION_GET_STATE = 2

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Dual Relay Bricklet';

        self.binding_version = [1, 0, 0]


    def set_state(self, relay1, relay2):
        """
        Sets the state of the relays, *true* means on and *false* means off. 
        For example: (true, false) turns relay 1 on and relay 2 off.
        
        If you just want to set one of the relays and don't know the current state
        of the other relay, you can get the state with :func:`GetState`.
        
        The default value is (false, false).
        """
        self.ipcon.write(self, DualRelay.FUNCTION_SET_STATE, (relay1, relay2), '? ?', '')

    def get_state(self):
        """
        Returns the state of the relays, *true* means on and *false* means off.
        """
        return GetState(*self.ipcon.write(self, DualRelay.FUNCTION_GET_STATE, (), '', '? ?'))
