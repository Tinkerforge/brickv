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

GetEdgeCountConfig = namedtuple('EdgeCountConfig', ['edge_type', 'debounce'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialDigitalIn4(Device):
    """
    4 galvanically isolated digital inputs
    """

    DEVICE_IDENTIFIER = 223
    DEVICE_DISPLAY_NAME = 'Industrial Digital In 4 Bricklet'
    DEVICE_URL_PART = 'industrial_digital_in_4' # internal

    CALLBACK_INTERRUPT = 9


    FUNCTION_GET_VALUE = 1
    FUNCTION_SET_GROUP = 2
    FUNCTION_GET_GROUP = 3
    FUNCTION_GET_AVAILABLE_FOR_GROUP = 4
    FUNCTION_SET_DEBOUNCE_PERIOD = 5
    FUNCTION_GET_DEBOUNCE_PERIOD = 6
    FUNCTION_SET_INTERRUPT = 7
    FUNCTION_GET_INTERRUPT = 8
    FUNCTION_GET_EDGE_COUNT = 10
    FUNCTION_SET_EDGE_COUNT_CONFIG = 11
    FUNCTION_GET_EDGE_COUNT_CONFIG = 12
    FUNCTION_GET_IDENTITY = 255

    EDGE_TYPE_RISING = 0
    EDGE_TYPE_FALLING = 1
    EDGE_TYPE_BOTH = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 1)

        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_VALUE] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_GROUP] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_GROUP] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_AVAILABLE_FOR_GROUP] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_INTERRUPT] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_INTERRUPT] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_EDGE_COUNT] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_EDGE_COUNT_CONFIG] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_EDGE_COUNT_CONFIG] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_IDENTITY] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletIndustrialDigitalIn4.CALLBACK_INTERRUPT] = 'H H'


    def get_value(self):
        """
        Returns the input value with a bitmask. The bitmask is 16bit long, *true*
        refers to high and *false* refers to low.

        For example: The value 3 or 0b0011 means that pins 0-1 are high and the other
        pins are low.

        If no groups are used (see :func:`Set Group`), the pins correspond to the
        markings on the Digital In 4 Bricklet.

        If groups are used, the pins correspond to the element in the group.
        Element 1 in the group will get pins 0-3, element 2 pins 4-7, element 3
        pins 8-11 and element 4 pins 12-15.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_VALUE, (), '', 'H')

    def set_group(self, group):
        """
        Sets a group of Digital In 4 Bricklets that should work together. You can
        find Bricklets that can be grouped together with :func:`Get Available For Group`.

        The group consists of 4 elements. Element 1 in the group will get pins 0-3,
        element 2 pins 4-7, element 3 pins 8-11 and element 4 pins 12-15.

        Each element can either be one of the ports ('a' to 'd') or 'n' if it should
        not be used.

        For example: If you have two Digital In 4 Bricklets connected to port A and
        port B respectively, you could call with ``['a', 'b', 'n', 'n']``.

        Now the pins on the Digital In 4 on port A are assigned to 0-3 and the
        pins on the Digital In 4 on port B are assigned to 4-7. It is now possible
        to call :func:`Get Value` and read out two Bricklets at the same time.

        Changing the group configuration resets all edge counter configurations
        and values.
        """
        group = create_char_list(group)

        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_GROUP, (group,), '4c', '')

    def get_group(self):
        """
        Returns the group as set by :func:`Set Group`
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_GROUP, (), '', '4c')

    def get_available_for_group(self):
        """
        Returns a bitmask of ports that are available for grouping. For example the
        value 5 or 0b0101 means: Port A and port C are connected to Bricklets that
        can be grouped together.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_AVAILABLE_FOR_GROUP, (), '', 'B')

    def set_debounce_period(self, debounce):
        """
        Sets the debounce period of the :cb:`Interrupt` callback in ms.

        For example: If you set this value to 100, you will get the interrupt
        maximal every 100ms. This is necessary if something that bounces is
        connected to the Digital In 4 Bricklet, such as a button.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_interrupt(self, interrupt_mask):
        """
        Sets the pins on which an interrupt is activated with a bitmask.
        Interrupts are triggered on changes of the voltage level of the pin,
        i.e. changes from high to low and low to high.

        For example: An interrupt bitmask of 9 or 0b1001 will enable the interrupt for
        pins 0 and 3.

        The interrupts use the grouping as set by :func:`Set Group`.

        The interrupt is delivered with the :cb:`Interrupt` callback.
        """
        interrupt_mask = int(interrupt_mask)

        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_INTERRUPT, (interrupt_mask,), 'H', '')

    def get_interrupt(self):
        """
        Returns the interrupt bitmask as set by :func:`Set Interrupt`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_INTERRUPT, (), '', 'H')

    def get_edge_count(self, pin, reset_counter):
        """
        Returns the current value of the edge counter for the selected pin. You can
        configure the edges that are counted with :func:`Set Edge Count Config`.

        If you set the reset counter to *true*, the count is set back to 0
        directly after it is read.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        pin = int(pin)
        reset_counter = bool(reset_counter)

        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_EDGE_COUNT, (pin, reset_counter), 'B !', 'I')

    def set_edge_count_config(self, selection_mask, edge_type, debounce):
        """
        Configures the edge counter for the selected pins. A bitmask of 9 or 0b1001 will
        enable the edge counter for pins 0 and 3.

        The edge type parameter configures if rising edges, falling edges or
        both are counted if the pin is configured for input. Possible edge types are:

        * 0 = rising (default)
        * 1 = falling
        * 2 = both

        The debounce time is given in ms.

        Configuring an edge counter resets its value to 0.

        If you don't know what any of this means, just leave it at default. The
        default configuration is very likely OK for you.

        Default values: 0 (edge type) and 100ms (debounce time)

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        selection_mask = int(selection_mask)
        edge_type = int(edge_type)
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_EDGE_COUNT_CONFIG, (selection_mask, edge_type, debounce), 'H B B', '')

    def get_edge_count_config(self, pin):
        """
        Returns the edge type and debounce time for the selected pin as set by
        :func:`Set Edge Count Config`.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        pin = int(pin)

        return GetEdgeCountConfig(*self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_EDGE_COUNT_CONFIG, (pin,), 'B', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

IndustrialDigitalIn4 = BrickletIndustrialDigitalIn4 # for backward compatibility
