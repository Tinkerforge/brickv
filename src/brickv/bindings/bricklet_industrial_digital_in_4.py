# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-01-09.      #
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

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialDigitalIn4(Device):
    """
    Device for controlling up to 4 optically coupled digital inputs
    """

    DEVICE_IDENTIFIER = 223

    CALLBACK_INTERRUPT = 9

    FUNCTION_GET_VALUE = 1
    FUNCTION_SET_GROUP = 2
    FUNCTION_GET_GROUP = 3
    FUNCTION_GET_AVAILABLE_FOR_GROUP = 4
    FUNCTION_SET_DEBOUNCE_PERIOD = 5
    FUNCTION_GET_DEBOUNCE_PERIOD = 6
    FUNCTION_SET_INTERRUPT = 7
    FUNCTION_GET_INTERRUPT = 8
    FUNCTION_GET_IDENTITY = 255

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (1, 0, 0)

        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_VALUE] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_GROUP] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_GROUP] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_AVAILABLE_FOR_GROUP] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_SET_INTERRUPT] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_INTERRUPT] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDigitalIn4.CALLBACK_INTERRUPT] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletIndustrialDigitalIn4.FUNCTION_GET_IDENTITY] = BrickletIndustrialDigitalIn4.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletIndustrialDigitalIn4.CALLBACK_INTERRUPT] = 'H H'

    def get_value(self):
        """
        Returns the input value with a bitmask. The bitmask
        is 16 bit long, *true* refers to high and *false* refers to 
        low.
        
        For example: The value 0b0000000000000011 means that pins 0-1 
        are high and the other pins are low.
        
        If no groups are used (see :func:`SetGroup`), the pins correspond to the
        markings on the Digital In 4 Bricklet.
        
        If groups are used, the pins correspond to the element in the group.
        Element 1 in the group will get pins 0-3, element 2 pins 4-7, element 3
        pins 8-11 and element 4 pins 12-15.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_VALUE, (), '', 'H')

    def set_group(self, group):
        """
        Sets a group of Digital In 4 Bricklets that should work together. You can
        find Bricklets that can be grouped together with :func:`GetAvailableForGroup`.
        
        The group consists of 4 elements. Element 1 in the group will get pins 0-3,
        element 2 pins 4-7, element 3 pins 8-11 and element 4 pins 12-15.
        
        Each element can either be one of the ports ('a' to 'd') or 'n' if it should
        not be used.
        
        For example: If you have two Digital In 4 Bricklets connected to port A and
        port B respectively, you could call with "['a', 'b', 'n', 'n']".
        
        Now the pins on the Digital In 4 on port A are assigned to 0-3 and the
        pins on the Digital In 4 on port B are assigned to 4-7. It is now possible
        to call :func:`GetValue` and read out two Bricklets at the same time.
        """
        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_GROUP, (group,), '4c', '')

    def get_group(self):
        """
        Returns the group as set by :func:`SetGroup`
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_GROUP, (), '', '4c')

    def get_available_for_group(self):
        """
        Returns a bitmask of ports that are available for grouping. For example the
        value 0b0101 means: Port *A* and Port *C* are connected to Bricklets that
        can be grouped together.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_AVAILABLE_FOR_GROUP, (), '', 'B')

    def set_debounce_period(self, debounce):
        """
        Sets the debounce period of the :func:`Interrupt` callback in ms.
        
        For example: If you set this value to 100, you will get the interrupt
        maximal every 100ms. This is necessary if something that bounces is
        connected to the Digital In 4 Bricklet, such as a button.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_interrupt(self, interrupt_mask):
        """
        Sets the pins on which an interrupt is activated with a bitmask.
        Interrupts are triggered on changes of the voltage level of the pin,
        i.e. changes from high to low and low to high.
        
        For example: An interrupt bitmask of 9 (0b0000000000001001) will 
        enable the interrupt for pins 0 and 3.
        
        The interrupts use the grouping as set by :func:`SetGroup`.
        
        The interrupt is delivered with the callback :func:`Interrupt`.
        """
        self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_SET_INTERRUPT, (interrupt_mask,), 'H', '')

    def get_interrupt(self):
        """
        Returns the interrupt bitmask as set by :func:`SetInterrupt`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_INTERRUPT, (), '', 'H')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers are:
        
        .. csv-table::
         :header: "Device Identifier", "Device Name"
         :widths: 30, 100
        
         "11", "Brick DC"
         "12", "Brick Debug"
         "13", "Brick Master"
         "14", "Brick Servo"
         "15", "Brick Stepper"
         "16", "Brick IMU"
         "", ""
         "21", "Bricklet Ambient Light"
         "22", "Bricklet Breakout"
         "23", "Bricklet Current12"
         "24", "Bricklet Current25"
         "25", "Bricklet Distance IR"
         "26", "Bricklet Dual Relay"
         "27", "Bricklet Humidity"
         "28", "Bricklet IO-16"
         "29", "Bricklet IO-4"
         "210", "Bricklet Joystick"
         "211", "Bricklet LCD 16x2"
         "212", "Bricklet LCD 20x4"
         "213", "Bricklet Linear Poti"
         "214", "Bricklet Piezo Buzzer"
         "215", "Bricklet Rotary Poti"
         "216", "Bricklet Temperature"
         "217", "Bricklet Temperature IR"
         "218", "Bricklet Voltage"
         "219", "Bricklet Analog In"
         "220", "Bricklet Analog Out"
         "221", "Bricklet Barometer"
         "222", "Bricklet GPS"
         "223", "Bricklet Industrial Digital In 4"
         "224", "Bricklet Industrial Digital Out 4"
         "225", "Bricklet Industrial Quad Relay"
         "226", "Bricklet PTC"
         "227", "Bricklet Voltage/Current"
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletIndustrialDigitalIn4.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

IndustrialDigitalIn4 = BrickletIndustrialDigitalIn4 # for backward compatibility
