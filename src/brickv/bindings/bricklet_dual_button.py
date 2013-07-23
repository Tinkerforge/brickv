# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-07-23.      #
#                                                           #
# Bindings Version 2.0.8                                    #
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

GetLEDState = namedtuple('LEDState', ['led1', 'led2'])
GetButtonState = namedtuple('ButtonState', ['button1', 'button2'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletDualButton(Device):
    """
    Device with two buttons and two LEDs
    """

    DEVICE_IDENTIFIER = 230

    CALLBACK_STATE_CHANGED = 4

    FUNCTION_SET_LED_STATE = 1
    FUNCTION_GET_LED_STATE = 2
    FUNCTION_GET_BUTTON_STATE = 3
    FUNCTION_GET_IDENTITY = 255

    LED_STATE_AUTO_TOGGLE_ON = 0
    LED_STATE_AUTO_TOGGLE_OFF = 1
    LED_STATE_ON = 3
    LED_STATE_OFF = 4
    BUTTON_STATE_PRESSED = 0
    BUTTON_STATE_RELEASED = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletDualButton.FUNCTION_SET_LED_STATE] = BrickletDualButton.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualButton.FUNCTION_GET_LED_STATE] = BrickletDualButton.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualButton.FUNCTION_GET_BUTTON_STATE] = BrickletDualButton.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualButton.CALLBACK_STATE_CHANGED] = BrickletDualButton.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletDualButton.FUNCTION_GET_IDENTITY] = BrickletDualButton.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletDualButton.CALLBACK_STATE_CHANGED] = 'B B B B'

    def set_led_state(self, led1, led2):
        """
        
        """
        self.ipcon.send_request(self, BrickletDualButton.FUNCTION_SET_LED_STATE, (led1, led2), 'B B', '')

    def get_led_state(self):
        """
        
        """
        return GetLEDState(*self.ipcon.send_request(self, BrickletDualButton.FUNCTION_GET_LED_STATE, (), '', 'B B'))

    def get_button_state(self):
        """
        
        """
        return GetButtonState(*self.ipcon.send_request(self, BrickletDualButton.FUNCTION_GET_BUTTON_STATE, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletDualButton.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

DualButton = BrickletDualButton # for backward compatibility
