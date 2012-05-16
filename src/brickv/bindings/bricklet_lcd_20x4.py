# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-16.      #
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

GetConfig = namedtuple('Config', ['cursor', 'blinking'])

class LCD20x4(Device):
    """
    Device for controlling a LCD with 4 lines a 20 characters
    """

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

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[LCD20x4.CALLBACK_BUTTON_PRESSED] = 'B'
        self.callbacks_format[LCD20x4.CALLBACK_BUTTON_RELEASED] = 'B'

    def write_line(self, line, position, text):
        """
        Writes text to a specific line (0 to 3) with a specific position 
        (0 to 19). The text can have a maximum of 20 characters.
        
        For example: (0, 7, "Hello") will write *Hello* in the middle of the
        first line of the display.
        """
        self.ipcon.write(self, LCD20x4.FUNCTION_WRITE_LINE, (line, position, text), 'B B 20s', '')

    def clear_display(self):
        """
        Deletes all characters from the display.
        """
        self.ipcon.write(self, LCD20x4.FUNCTION_CLEAR_DISPLAY, (), '', '')

    def backlight_on(self):
        """
        Turns the backlight on.
        """
        self.ipcon.write(self, LCD20x4.FUNCTION_BACKLIGHT_ON, (), '', '')

    def backlight_off(self):
        """
        Turns the backlight off.
        """
        self.ipcon.write(self, LCD20x4.FUNCTION_BACKLIGHT_OFF, (), '', '')

    def is_backlight_on(self):
        """
        Returns true if the backlight is on and false otherwise.
        """
        return self.ipcon.write(self, LCD20x4.FUNCTION_IS_BACKLIGHT_ON, (), '', '?')

    def set_config(self, cursor, blinking):
        """
        Configures if the cursor (shown as "_") should be visible and if it
        should be blinking (shown as a blinking block). The cursor position
        is one character behind the the last text written with 
        :func:`WriteLine`.
        
        The default is (false, false).
        """
        self.ipcon.write(self, LCD20x4.FUNCTION_SET_CONFIG, (cursor, blinking), '? ?', '')

    def get_config(self):
        """
        Returns the configuration as set by :func:`SetConfig`.
        """
        return GetConfig(*self.ipcon.write(self, LCD20x4.FUNCTION_GET_CONFIG, (), '', '? ?'))

    def is_button_pressed(self, button):
        """
        Returns true if the button (0 to 2) is pressed. If you want to react
        on button presses and releases it is recommended to use the
        :func:`ButtonPressed` and :func:`ButtonReleased` callbacks.
        """
        return self.ipcon.write(self, LCD20x4.FUNCTION_IS_BUTTON_PRESSED, (button,), 'B', '?')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
