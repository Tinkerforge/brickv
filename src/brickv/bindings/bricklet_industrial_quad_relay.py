# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-11-22.      #
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

GetMonoflop = namedtuple('Monoflop', ['value', 'time', 'time_remaining'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialQuadRelay(Device):
    """
    Device for controlling up to 4 Solid State Relays
    """

    DEVICE_IDENTIFIER = 225

    CALLBACK_MONOFLOP_DONE = 8

    FUNCTION_SET_VALUE = 1
    FUNCTION_GET_VALUE = 2
    FUNCTION_SET_MONOFLOP = 3
    FUNCTION_GET_MONOFLOP = 4
    FUNCTION_SET_GROUP = 5
    FUNCTION_GET_GROUP = 6
    FUNCTION_GET_AVAILABLE_FOR_GROUP = 7
    FUNCTION_GET_IDENTITY = 255

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (1, 0, 0)

        self.callback_formats[IndustrialQuadRelay.CALLBACK_MONOFLOP_DONE] = 'H H'

    def set_value(self, value_mask):
        """
        Sets the output value with a bitmask. The bitmask
        is 16 bit long, *true* refers to a closed relay and *false* refers to 
        an open relay.
        
        For example: The value 0b0000000000000011 will close the relay 
        of pins 0-1 and open the other pins.
        
        If no groups are used (see :func:`SetGroup`), the pins correspond to the
        markings on the Quad Relay Bricklet.
        
        If groups are used, the pins correspond to the element in the group.
        Element 1 in the group will get pins 0-3, element 2 pins 4-7, element 3
        pins 8-11 and element 4 pins 12-15.
        """
        self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_SET_VALUE, (value_mask,), 'H', '')

    def get_value(self):
        """
        Returns the bitmask as set by :func:`SetValue`.
        """
        return self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_GET_VALUE, (), '', 'H')

    def set_monoflop(self, pin_mask, value_mask, time):
        """
        Configures a monoflop of the pins specified by the first parameter
        bitmask.
        
        The second parameter is a bitmask with the desired value of the specified
        pins (*true* means relay closed and *false* means relay open).
        
        The third parameter indicates the time (in ms) that the pins should hold
        the value.
        
        If this function is called with the parameters 
        ((1 << 0) | (1 << 3), (1 << 0), 1500):
        Pin 0 will close and pin 3 will open. In 1.5s pin 0 will open and pin
        3 will close again.
        
        A monoflop can be used as a fail-safe mechanism. For example: Lets assume you
        have a RS485 bus and a Quad Relay Bricklet connected to one of the slave
        stacks. You can now call this function every second, with a time parameter
        of two seconds and pin 0 closed. Pin 0 will be closed all the time. If now
        the RS485 connection is lost, then pin 0 will be opened in at most two seconds.
        """
        self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_SET_MONOFLOP, (pin_mask, value_mask, time), 'H H I', '')

    def get_monoflop(self, pin):
        """
        Returns (for the given pin) the current value and the time as set by
        :func:`SetMonoflop` as well as the remaining time until the value flips.
        
        If the timer is not running currently, the remaining time will be returned
        as 0.
        """
        return GetMonoflop(*self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_GET_MONOFLOP, (pin,), 'B', 'H I I'))

    def set_group(self, group):
        """
        Sets a group of Quad Relay Bricklets that should work together. You can
        find Bricklets that can be grouped together with :func:`GetAvailableForGroup`.
        
        The group consists of 4 elements. Element 1 in the group will get pins 0-3,
        element 2 pins 4-7, element 3 pins 8-11 and element 4 pins 12-15.
        
        Each element can either be one of the ports ('a' to 'd') or 'n' if it should
        not be used.
        
        For example: If you have two Quad Relay Bricklets connected to port A and
        port B respectively, you could call with "['a', 'b', 'n', 'n']".
        
        Now the pins on the Quad Relay on port A are assigned to 0-3 and the
        pins on the Quad Relay on port B are assigned to 4-7. It is now possible
        to call :func:`SetValue` and control two Bricklets at the same time.
        """
        self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_SET_GROUP, (group,), '4c', '')

    def get_group(self):
        """
        Returns the group as set by :func:`SetGroup`
        """
        return self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_GET_GROUP, (), '', '4c')

    def get_available_for_group(self):
        """
        Returns a bitmask of ports that are available for grouping. For example the
        value 0b0101 means: Port *A* and Port *C* are connected to Bricklets that
        can be grouped together.
        """
        return self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_GET_AVAILABLE_FOR_GROUP, (), '', 'B')

    def get_identity(self):
        """
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, IndustrialQuadRelay.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

IndustrialQuadRelay = BrickletIndustrialQuadRelay # for backward compatibility
