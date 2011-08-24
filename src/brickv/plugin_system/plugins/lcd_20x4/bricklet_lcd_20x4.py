# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2011-08-23.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from ip_connection import namedtuple
from ip_connection import Device, IPConnection, Error

GetConfig = namedtuple('Config', ['cursor', 'blinking'])

class LCD20x4(Device):
    CALLBACK_BUTTON_PRESSED = 9
    CALLBACK_BUTTON_RELEASED = 10

    TYPE_WRITE_LINE = 1
    TYPE_CLEAR_DISPLAY = 2
    TYPE_BACKLIGHT_ON = 3
    TYPE_BACKLIGHT_OFF = 4
    TYPE_IS_BACKLIGHT_ON = 5
    TYPE_SET_CONFIG = 6
    TYPE_GET_CONFIG = 7
    TYPE_IS_BUTTON_PRESSED = 8
    TYPE_BUTTON_PRESSED = 9
    TYPE_BUTTON_RELEASED = 10

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[LCD20x4.CALLBACK_BUTTON_PRESSED] = 'B'
        self.callbacks_format[LCD20x4.CALLBACK_BUTTON_RELEASED] = 'B'

    def write_line(self, line, position, text):
        self.ipcon.write(self, LCD20x4.TYPE_WRITE_LINE, (line, position, text), 'B B 20s', '')

    def clear_display(self):
        self.ipcon.write(self, LCD20x4.TYPE_CLEAR_DISPLAY, (), '', '')

    def backlight_on(self):
        self.ipcon.write(self, LCD20x4.TYPE_BACKLIGHT_ON, (), '', '')

    def backlight_off(self):
        self.ipcon.write(self, LCD20x4.TYPE_BACKLIGHT_OFF, (), '', '')

    def is_backlight_on(self):
        return self.ipcon.write(self, LCD20x4.TYPE_IS_BACKLIGHT_ON, (), '', '?')

    def set_config(self, cursor, blinking):
        self.ipcon.write(self, LCD20x4.TYPE_SET_CONFIG, (cursor, blinking), '? ?', '')

    def get_config(self):
        return GetConfig(*self.ipcon.write(self, LCD20x4.TYPE_GET_CONFIG, (), '', '? ?'))

    def is_button_pressed(self, button):
        return self.ipcon.write(self, LCD20x4.TYPE_IS_BUTTON_PRESSED, (button,), 'B', '?')
