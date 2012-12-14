# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-12-14.      #
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

GetConfig = namedtuple('Config', ['cursor', 'blinking'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLCD20x4(Device):
    """
    Device for controlling a LCD with 4 lines a 20 characters
    """

    DEVICE_IDENTIFIER = 212

    CALLBACK_BUTTON_PRESSED = 9
    CALLBACK_BUTTON_RELEASED = 10

    FUNCTION_WRITE_LINE = 1
    FUNCTION_CLEAR_DISPLAY = 2
    FUNCTION_BACKLIGHT_ON = 3
    FUNCTION_BACKLIGHT_OFF = 4
    FUNCTION_IS_BACKLIGHT_ON = 5
    FUNCTION_SET_CONFIG = 6
    FUNCTION_GET_CONFIG = 7
    FUNCTION_IS_BUTTON_PRESSED = 8
    FUNCTION_GET_IDENTITY = 255

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (1, 0, 0)

        self.response_expected[BrickletLCD20x4.FUNCTION_WRITE_LINE] = BrickletLCD20x4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD20x4.FUNCTION_CLEAR_DISPLAY] = BrickletLCD20x4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD20x4.FUNCTION_BACKLIGHT_ON] = BrickletLCD20x4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD20x4.FUNCTION_BACKLIGHT_OFF] = BrickletLCD20x4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD20x4.FUNCTION_IS_BACKLIGHT_ON] = BrickletLCD20x4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD20x4.FUNCTION_SET_CONFIG] = BrickletLCD20x4.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD20x4.FUNCTION_GET_CONFIG] = BrickletLCD20x4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD20x4.FUNCTION_IS_BUTTON_PRESSED] = BrickletLCD20x4.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD20x4.CALLBACK_BUTTON_PRESSED] = BrickletLCD20x4.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLCD20x4.CALLBACK_BUTTON_RELEASED] = BrickletLCD20x4.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLCD20x4.FUNCTION_GET_IDENTITY] = BrickletLCD20x4.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLCD20x4.CALLBACK_BUTTON_PRESSED] = 'B'
        self.callback_formats[BrickletLCD20x4.CALLBACK_BUTTON_RELEASED] = 'B'

    def write_line(self, line, position, text):
        """
        Writes text to a specific line (0 to 3) with a specific position 
        (0 to 19). The text can have a maximum of 20 characters.
        
        For example: (0, 7, "Hello") will write *Hello* in the middle of the
        first line of the display.
        
        The display uses a special charset that includes all ASCII characters except
        backslash and tilde. The LCD charset also includes several other non-ASCII characters, see
        the `charset specification <https://github.com/Tinkerforge/lcd-20x4-bricklet/raw/master/datasheets/standard_charset.pdf>`__
        for details. The Unicode example above shows how to specify non-ASCII characters
        and how to translate from Unicode to the LCD charset.
        """
        self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_WRITE_LINE, (line, position, text), 'B B 20s', '')

    def clear_display(self):
        """
        Deletes all characters from the display.
        """
        self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_CLEAR_DISPLAY, (), '', '')

    def backlight_on(self):
        """
        Turns the backlight on.
        """
        self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_BACKLIGHT_ON, (), '', '')

    def backlight_off(self):
        """
        Turns the backlight off.
        """
        self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_BACKLIGHT_OFF, (), '', '')

    def is_backlight_on(self):
        """
        Returns *true* if the backlight is on and *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_IS_BACKLIGHT_ON, (), '', '?')

    def set_config(self, cursor, blinking):
        """
        Configures if the cursor (shown as "_") should be visible and if it
        should be blinking (shown as a blinking block). The cursor position
        is one character behind the the last text written with 
        :func:`WriteLine`.
        
        The default is (false, false).
        """
        self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_SET_CONFIG, (cursor, blinking), '? ?', '')

    def get_config(self):
        """
        Returns the configuration as set by :func:`SetConfig`.
        """
        return GetConfig(*self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_GET_CONFIG, (), '', '? ?'))

    def is_button_pressed(self, button):
        """
        Returns *true* if the button (0 to 2) is pressed. If you want to react
        on button presses and releases it is recommended to use the
        :func:`ButtonPressed` and :func:`ButtonReleased` callbacks.
        """
        return self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_IS_BUTTON_PRESSED, (button,), 'B', '?')

    def get_identity(self):
        """
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLCD20x4.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

LCD20x4 = BrickletLCD20x4 # for backward compatibility
