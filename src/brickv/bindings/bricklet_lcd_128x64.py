# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-01-29.      #
#                                                           #
# Python Bindings Version 2.1.21                            #
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

ReadPixelsLowLevel = namedtuple('ReadPixelsLowLevel', ['pixels_length', 'pixels_chunk_offset', 'pixels_chunk_data'])
GetDisplayConfiguration = namedtuple('DisplayConfiguration', ['contrast', 'backlight', 'invert', 'automatic_draw'])
GetTouchPosition = namedtuple('TouchPosition', ['pressure', 'x', 'y', 'age'])
GetTouchPositionCallbackConfiguration = namedtuple('TouchPositionCallbackConfiguration', ['period', 'value_has_to_change'])
GetTouchGesture = namedtuple('TouchGesture', ['gesture', 'duration', 'pressure_max', 'x_start', 'y_start', 'x_end', 'y_end', 'age'])
GetTouchGestureCallbackConfiguration = namedtuple('TouchGestureCallbackConfiguration', ['period', 'value_has_to_change'])
GetGUIButton = namedtuple('GUIButton', ['active', 'position_x', 'position_y', 'width', 'height', 'text'])
GetGUIButtonPressedCallbackConfiguration = namedtuple('GUIButtonPressedCallbackConfiguration', ['period', 'value_has_to_change'])
GetGUISlider = namedtuple('GUISlider', ['active', 'position_x', 'position_y', 'length', 'direction', 'value'])
GetGUISliderValueCallbackConfiguration = namedtuple('GUISliderValueCallbackConfiguration', ['period', 'value_has_to_change'])
GetGUITabConfiguration = namedtuple('GUITabConfiguration', ['change_tab_config', 'clear_gui'])
GetGUITabText = namedtuple('GUITabText', ['active', 'text'])
GetGUITabIcon = namedtuple('GUITabIcon', ['active', 'icon'])
GetGUITabSelectedCallbackConfiguration = namedtuple('GUITabSelectedCallbackConfiguration', ['period', 'value_has_to_change'])
GetGUIGraphConfiguration = namedtuple('GUIGraphConfiguration', ['active', 'graph_type', 'position_x', 'position_y', 'width', 'height', 'text_x', 'text_y'])
GetGUIGraphDataLowLevel = namedtuple('GUIGraphDataLowLevel', ['data_length', 'data_chunk_offset', 'data_chunk_data'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLCD128x64(Device):
    """
    7.1cm (2.8") display with 128x64 pixel and touch screen
    """

    DEVICE_IDENTIFIER = 298
    DEVICE_DISPLAY_NAME = 'LCD 128x64 Bricklet'
    DEVICE_URL_PART = 'lcd_128x64' # internal

    CALLBACK_TOUCH_POSITION = 11
    CALLBACK_TOUCH_GESTURE = 15
    CALLBACK_GUI_BUTTON_PRESSED = 25
    CALLBACK_GUI_SLIDER_VALUE = 32
    CALLBACK_GUI_TAB_SELECTED = 44


    FUNCTION_WRITE_PIXELS_LOW_LEVEL = 1
    FUNCTION_READ_PIXELS_LOW_LEVEL = 2
    FUNCTION_CLEAR_DISPLAY = 3
    FUNCTION_SET_DISPLAY_CONFIGURATION = 4
    FUNCTION_GET_DISPLAY_CONFIGURATION = 5
    FUNCTION_WRITE_LINE = 6
    FUNCTION_DRAW_BUFFERED_FRAME = 7
    FUNCTION_GET_TOUCH_POSITION = 8
    FUNCTION_SET_TOUCH_POSITION_CALLBACK_CONFIGURATION = 9
    FUNCTION_GET_TOUCH_POSITION_CALLBACK_CONFIGURATION = 10
    FUNCTION_GET_TOUCH_GESTURE = 12
    FUNCTION_SET_TOUCH_GESTURE_CALLBACK_CONFIGURATION = 13
    FUNCTION_GET_TOUCH_GESTURE_CALLBACK_CONFIGURATION = 14
    FUNCTION_DRAW_LINE = 16
    FUNCTION_DRAW_BOX = 17
    FUNCTION_DRAW_TEXT = 18
    FUNCTION_SET_GUI_BUTTON = 19
    FUNCTION_GET_GUI_BUTTON = 20
    FUNCTION_REMOVE_GUI_BUTTON = 21
    FUNCTION_SET_GUI_BUTTON_PRESSED_CALLBACK_CONFIGURATION = 22
    FUNCTION_GET_GUI_BUTTON_PRESSED_CALLBACK_CONFIGURATION = 23
    FUNCTION_GET_GUI_BUTTON_PRESSED = 24
    FUNCTION_SET_GUI_SLIDER = 26
    FUNCTION_GET_GUI_SLIDER = 27
    FUNCTION_REMOVE_GUI_SLIDER = 28
    FUNCTION_SET_GUI_SLIDER_VALUE_CALLBACK_CONFIGURATION = 29
    FUNCTION_GET_GUI_SLIDER_VALUE_CALLBACK_CONFIGURATION = 30
    FUNCTION_GET_GUI_SLIDER_VALUE = 31
    FUNCTION_SET_GUI_TAB_CONFIGURATION = 33
    FUNCTION_GET_GUI_TAB_CONFIGURATION = 34
    FUNCTION_SET_GUI_TAB_TEXT = 35
    FUNCTION_GET_GUI_TAB_TEXT = 36
    FUNCTION_SET_GUI_TAB_ICON = 37
    FUNCTION_GET_GUI_TAB_ICON = 38
    FUNCTION_REMOVE_GUI_TAB = 39
    FUNCTION_SET_GUI_TAB_SELECTED = 40
    FUNCTION_SET_GUI_TAB_SELECTED_CALLBACK_CONFIGURATION = 41
    FUNCTION_GET_GUI_TAB_SELECTED_CALLBACK_CONFIGURATION = 42
    FUNCTION_GET_GUI_TAB_SELECTED = 43
    FUNCTION_SET_GUI_GRAPH_CONFIGURATION = 45
    FUNCTION_GET_GUI_GRAPH_CONFIGURATION = 46
    FUNCTION_SET_GUI_GRAPH_DATA_LOW_LEVEL = 47
    FUNCTION_GET_GUI_GRAPH_DATA_LOW_LEVEL = 48
    FUNCTION_REMOVE_GUI_GRAPH = 49
    FUNCTION_REMOVE_ALL_GUI = 50
    FUNCTION_SET_TOUCH_LED_CONFIG = 51
    FUNCTION_GET_TOUCH_LED_CONFIG = 52
    FUNCTION_GET_SPITFP_ERROR_COUNT = 234
    FUNCTION_SET_BOOTLOADER_MODE = 235
    FUNCTION_GET_BOOTLOADER_MODE = 236
    FUNCTION_SET_WRITE_FIRMWARE_POINTER = 237
    FUNCTION_WRITE_FIRMWARE = 238
    FUNCTION_SET_STATUS_LED_CONFIG = 239
    FUNCTION_GET_STATUS_LED_CONFIG = 240
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_WRITE_UID = 248
    FUNCTION_READ_UID = 249
    FUNCTION_GET_IDENTITY = 255

    GESTURE_LEFT_TO_RIGHT = 0
    GESTURE_RIGHT_TO_LEFT = 1
    GESTURE_TOP_TO_BOTTOM = 2
    GESTURE_BOTTOM_TO_TOP = 3
    COLOR_WHITE = False
    COLOR_BLACK = True
    FONT_6X8 = 0
    FONT_6X16 = 1
    FONT_6X24 = 2
    FONT_6X32 = 3
    FONT_12X16 = 4
    FONT_12X24 = 5
    FONT_12X32 = 6
    FONT_18X24 = 7
    FONT_18X32 = 8
    FONT_24X32 = 9
    DIRECTION_HORIZONTAL = 0
    DIRECTION_VERTICAL = 1
    CHANGE_TAB_ON_CLICK = 1
    CHANGE_TAB_ON_SWIPE = 2
    CHANGE_TAB_ON_CLICK_AND_SWIPE = 3
    GRAPH_TYPE_DOT = 0
    GRAPH_TYPE_LINE = 1
    GRAPH_TYPE_BAR = 2
    TOUCH_LED_CONFIG_OFF = 0
    TOUCH_LED_CONFIG_ON = 1
    TOUCH_LED_CONFIG_SHOW_HEARTBEAT = 2
    TOUCH_LED_CONFIG_SHOW_TOUCH = 3
    BOOTLOADER_MODE_BOOTLOADER = 0
    BOOTLOADER_MODE_FIRMWARE = 1
    BOOTLOADER_MODE_BOOTLOADER_WAIT_FOR_REBOOT = 2
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_REBOOT = 3
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_ERASE_AND_REBOOT = 4
    BOOTLOADER_STATUS_OK = 0
    BOOTLOADER_STATUS_INVALID_MODE = 1
    BOOTLOADER_STATUS_NO_CHANGE = 2
    BOOTLOADER_STATUS_ENTRY_FUNCTION_NOT_PRESENT = 3
    BOOTLOADER_STATUS_DEVICE_IDENTIFIER_INCORRECT = 4
    BOOTLOADER_STATUS_CRC_MISMATCH = 5
    STATUS_LED_CONFIG_OFF = 0
    STATUS_LED_CONFIG_ON = 1
    STATUS_LED_CONFIG_SHOW_HEARTBEAT = 2
    STATUS_LED_CONFIG_SHOW_STATUS = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 1)

        self.response_expected[BrickletLCD128x64.FUNCTION_WRITE_PIXELS_LOW_LEVEL] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_READ_PIXELS_LOW_LEVEL] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_CLEAR_DISPLAY] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_DISPLAY_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_DISPLAY_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_WRITE_LINE] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_DRAW_BUFFERED_FRAME] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_TOUCH_POSITION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_TOUCH_POSITION_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_TOUCH_POSITION_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_TOUCH_GESTURE] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_TOUCH_GESTURE_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_TOUCH_GESTURE_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_DRAW_LINE] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_DRAW_BOX] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_DRAW_TEXT] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_BUTTON] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_BUTTON] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_REMOVE_GUI_BUTTON] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_BUTTON_PRESSED_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_BUTTON_PRESSED_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_BUTTON_PRESSED] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_SLIDER] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_SLIDER] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_REMOVE_GUI_SLIDER] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_SLIDER_VALUE_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_SLIDER_VALUE_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_SLIDER_VALUE] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_TAB_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_TAB_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_TAB_TEXT] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_TAB_TEXT] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_TAB_ICON] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_TAB_ICON] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_REMOVE_GUI_TAB] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_TAB_SELECTED] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_TAB_SELECTED_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_TAB_SELECTED_CALLBACK_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_TAB_SELECTED] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_GRAPH_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_GRAPH_CONFIGURATION] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_GUI_GRAPH_DATA_LOW_LEVEL] = BrickletLCD128x64.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_GUI_GRAPH_DATA_LOW_LEVEL] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_REMOVE_GUI_GRAPH] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_REMOVE_ALL_GUI] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_TOUCH_LED_CONFIG] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_TOUCH_LED_CONFIG] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_BOOTLOADER_MODE] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_BOOTLOADER_MODE] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_WRITE_FIRMWARE] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_RESET] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_WRITE_UID] = BrickletLCD128x64.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLCD128x64.FUNCTION_READ_UID] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLCD128x64.FUNCTION_GET_IDENTITY] = BrickletLCD128x64.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLCD128x64.CALLBACK_TOUCH_POSITION] = 'H H H I'
        self.callback_formats[BrickletLCD128x64.CALLBACK_TOUCH_GESTURE] = 'B I H H H H H I'
        self.callback_formats[BrickletLCD128x64.CALLBACK_GUI_BUTTON_PRESSED] = 'B !'
        self.callback_formats[BrickletLCD128x64.CALLBACK_GUI_SLIDER_VALUE] = 'B B'
        self.callback_formats[BrickletLCD128x64.CALLBACK_GUI_TAB_SELECTED] = 'b'


    def write_pixels_low_level(self, x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data):
        """
        Writes pixels to the specified window.

        The x-axis goes from 0 to 127 and the y-axis from 0 to 63. The pixels are written
        into the window line by line top to bottom and each line is written from left to
        right.

        If automatic draw is enabled (default) the pixels are directly written to
        the screen. Only pixels that have actually changed are updated on the screen,
        the rest stays the same.

        If automatic draw is disabled the pixels are written to an internal buffer and
        the buffer is transferred to the display only after :func:`Draw Buffered Frame`
        is called. This can be used to avoid flicker when drawing a complex frame in
        multiple steps.

        Automatic draw can be configured with the :func:`Set Display Configuration`
        function.
        """
        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)
        pixels_length = int(pixels_length)
        pixels_chunk_offset = int(pixels_chunk_offset)
        pixels_chunk_data = list(map(bool, pixels_chunk_data))

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_WRITE_PIXELS_LOW_LEVEL, (x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data), 'B B B B H H 448!', '')

    def read_pixels_low_level(self, x_start, y_start, x_end, y_end):
        """
        Reads pixels from the specified window.

        The x-axis goes from 0 to 127 and the y-axis from 0 to 63. The pixels are read
        from the window line by line top to bottom and each line is read from left to
        right.

        If automatic draw is enabled (default) the pixels that are read are always the
        same that are shown on the display.

        If automatic draw is disabled the pixels are read from the internal buffer
        (see :func:`Draw Buffered Frame`).

        Automatic draw can be configured with the :func:`Set Display Configuration`
        function.
        """
        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        return ReadPixelsLowLevel(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_READ_PIXELS_LOW_LEVEL, (x_start, y_start, x_end, y_end), 'B B B B', 'H H 480!'))

    def clear_display(self):
        """
        Clears the complete content of the display.
        """
        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_CLEAR_DISPLAY, (), '', '')

    def set_display_configuration(self, contrast, backlight, invert, automatic_draw):
        """
        Sets the configuration of the display.

        You can set a contrast value from 0 to 63, a backlight intensity value
        from 0 to 100 and you can invert the color (white/black) of the display.

        If automatic draw is set to *true*, the display is automatically updated with every
        call of :func:`Write Pixels` and :func:`Write Line`. If it is set to false, the
        changes are written into an internal buffer and only shown on the display after
        a call of :func:`Draw Buffered Frame`.

        The default values are contrast 14, backlight intensity 100, inverting off
        and automatic draw on.
        """
        contrast = int(contrast)
        backlight = int(backlight)
        invert = bool(invert)
        automatic_draw = bool(automatic_draw)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_DISPLAY_CONFIGURATION, (contrast, backlight, invert, automatic_draw), 'B B ! !', '')

    def get_display_configuration(self):
        """
        Returns the configuration as set by :func:`Set Display Configuration`.
        """
        return GetDisplayConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_DISPLAY_CONFIGURATION, (), '', 'B B ! !'))

    def write_line(self, line, position, text):
        """
        Writes text to a specific line (0 to 7) with a specific position
        (0 to 21). The text can have a maximum of 22 characters.

        For example: (1, 10, "Hello") will write *Hello* in the middle of the
        second line of the display.

        The display uses a special 5x7 pixel charset. You can view the characters
        of the charset in Brick Viewer.

        This function is a 1:1 replacement for the function with the same name
        in the LCD 20x4 Bricklet. You can draw text at a specific pixel position
        and with different font sizes with the :func:`Draw Text` function.
        """
        line = int(line)
        position = int(position)
        text = create_string(text)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_WRITE_LINE, (line, position, text), 'B B 22s', '')

    def draw_buffered_frame(self, force_complete_redraw):
        """
        Draws the currently buffered frame. Normally each call of :func:`Write Pixels` and
        :func:`Write Line` draws directly onto the display. If you turn automatic draw off
        (:func:`Set Display Configuration`), the data is written in an internal buffer and
        only transferred to the display by calling this function. This can be used to
        avoid flicker when drawing a complex frame in multiple steps.

        Set the `force complete redraw` to *true* to redraw the whole display
        instead of only the changed parts. Normally it should not be necessary to set this to
        *true*. It may only become necessary in case of stuck pixels because of errors.
        """
        force_complete_redraw = bool(force_complete_redraw)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_DRAW_BUFFERED_FRAME, (force_complete_redraw,), '!', '')

    def get_touch_position(self):
        """
        Returns the last valid touch position:

        * Pressure: Amount of pressure applied by the user (0-300)
        * X: Touch position on x-axis (0-127)
        * Y: Touch position on y-axis (0-63)
        * Age: Age of touch press in ms (how long ago it was)
        """
        return GetTouchPosition(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_TOUCH_POSITION, (), '', 'H H H I'))

    def set_touch_position_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`Touch Position` callback
        is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_TOUCH_POSITION_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_touch_position_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set Touch Position Callback Configuration`.
        """
        return GetTouchPositionCallbackConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_TOUCH_POSITION_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def get_touch_gesture(self):
        """
        Returns one of four touch gestures that can be automatically detected by the Bricklet.

        The gestures are swipes from left to right, right to left, top to bottom and bottom to top.

        Additionally to the gestures a vector with a start and end position of the gesture is
        provided. You can use this vector do determine a more exact location of the gesture (e.g.
        the swipe from top to bottom was on the left or right part of the screen).

        The age parameter corresponds to the age of gesture in ms (how long ago it was).
        """
        return GetTouchGesture(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_TOUCH_GESTURE, (), '', 'B I H H H H H I'))

    def set_touch_gesture_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`Touch Gesture` callback
        is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_TOUCH_GESTURE_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_touch_gesture_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set Touch Gesture Callback Configuration`.
        """
        return GetTouchGestureCallbackConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_TOUCH_GESTURE_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def draw_line(self, position_x_start, position_y_start, position_x_end, position_y_end, color):
        """
        Draws a white or black line from (x, y)-start to (x, y)-end.
        The x values have to be within the range of 0 to 127 and the y
        values have t be within the range of 0 to 63.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        position_x_start = int(position_x_start)
        position_y_start = int(position_y_start)
        position_x_end = int(position_x_end)
        position_y_end = int(position_y_end)
        color = bool(color)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_DRAW_LINE, (position_x_start, position_y_start, position_x_end, position_y_end, color), 'B B B B !', '')

    def draw_box(self, position_x_start, position_y_start, position_x_end, position_y_end, fill, color):
        """
        Draws a white or black box from (x, y)-start to (x, y)-end.
        The x values have to be within the range of 0 to 127 and the y
        values have to be within the range of 0 to 63.

        If you set fill to true, the box will be filled with the
        color. Otherwise only the outline will be drawn.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        position_x_start = int(position_x_start)
        position_y_start = int(position_y_start)
        position_x_end = int(position_x_end)
        position_y_end = int(position_y_end)
        fill = bool(fill)
        color = bool(color)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_DRAW_BOX, (position_x_start, position_y_start, position_x_end, position_y_end, fill, color), 'B B B B ! !', '')

    def draw_text(self, position_x, position_y, font, color, text):
        """
        Draws a text with up to 22 characters at the pixel position (x, y).

        The x values have to be within the range of 0 to 127 and the y
        values have to be within the range of 0 to 63.

        You can use one of 9 different font sizes and draw the text in white or black.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        position_x = int(position_x)
        position_y = int(position_y)
        font = int(font)
        color = bool(color)
        text = create_string(text)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_DRAW_TEXT, (position_x, position_y, font, color, text), 'B B B ! 22s', '')

    def set_gui_button(self, index, position_x, position_y, width, height, text):
        """
        Draws a clickable button at position (x, y) with the given text
        of up to 16 characters.

        You can use up to 12 buttons (index 0-11).

        The x position + width has to be within the range of 1 to 128 and the y
        position + height has to be within the range of 1 to 64.

        The minimum useful width/height of a button is 3.

        You can enable a callback for a button press with
        :func:`Set GUI Button Pressed Callback Configuration`. The callback will
        be triggered for press and release-events.

        The button is drawn in a separate GUI buffer and the button-frame will
        always stay on top of the graphics drawn with :func:`Write Pixels`. To
        remove the button use :func:`Remove GUI Button`.

        If you want an icon instead of text, you can draw the icon inside of the
        button with :func:`Write Pixels`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        position_x = int(position_x)
        position_y = int(position_y)
        width = int(width)
        height = int(height)
        text = create_string(text)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_BUTTON, (index, position_x, position_y, width, height, text), 'B B B B B 16s', '')

    def get_gui_button(self, index):
        """
        Returns the button properties for a given `Index` as set by :func:`Set GUI Button`.

        Additionally the `Active` parameter shows if a button is currently active/visible
        or not.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return GetGUIButton(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_BUTTON, (index,), 'B', '! B B B B 16s'))

    def remove_gui_button(self, index):
        """
        Removes the button with the given index.

        You can use index 255 to remove all buttons.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_REMOVE_GUI_BUTTON, (index,), 'B', '')

    def set_gui_button_pressed_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`GUI Button Pressed` callback
        is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_BUTTON_PRESSED_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_gui_button_pressed_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set GUI Button Pressed Callback Configuration`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return GetGUIButtonPressedCallbackConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_BUTTON_PRESSED_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def get_gui_button_pressed(self, index):
        """
        Returns the state of the button for the given index.

        The state can either be pressed (true) or released (false).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_BUTTON_PRESSED, (index,), 'B', '!')

    def set_gui_slider(self, index, position_x, position_y, length, direction, value):
        """
        Draws a slider at position (x, y) with the given length.

        You can use up to 6 sliders (index 0-5).

        If you use the horizontal direction, the x position + length has to be
        within the range of 1 to 128 and the y position has to be within
        the range of 0 to 46.

        If you use the vertical direction, the y position + length has to be
        within the range of 1 to 64 and the x position has to be within
        the range of 0 to 110.

        The minimum length of a slider is 8.

        The parameter value is the start-position of the slider, it can
        be between 0 and length-8.

        You can enable a callback for the slider value with
        :func:`Set GUI Slider Value Callback Configuration`.

        The slider is drawn in a separate GUI buffer and it will
        always stay on top of the graphics drawn with :func:`Write Pixels`. To
        remove the button use :func:`Remove GUI Slider`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        position_x = int(position_x)
        position_y = int(position_y)
        length = int(length)
        direction = int(direction)
        value = int(value)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_SLIDER, (index, position_x, position_y, length, direction, value), 'B B B B B B', '')

    def get_gui_slider(self, index):
        """
        Returns the slider properties for a given `Index` as set by :func:`Set GUI Slider`.

        Additionally the `Active` parameter shows if a button is currently active/visible
        or not.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return GetGUISlider(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_SLIDER, (index,), 'B', '! B B B B B'))

    def remove_gui_slider(self, index):
        """
        Removes the slider with the given index.

        You can use index 255 to remove all slider.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_REMOVE_GUI_SLIDER, (index,), 'B', '')

    def set_gui_slider_value_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`GUI Slider Value` callback
        is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_SLIDER_VALUE_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_gui_slider_value_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set GUI Slider Value Callback Configuration`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return GetGUISliderValueCallbackConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_SLIDER_VALUE_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def get_gui_slider_value(self, index):
        """
        Returns the current slider value for the given index.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_SLIDER_VALUE, (index,), 'B', 'B')

    def set_gui_tab_configuration(self, change_tab_config, clear_gui):
        """
        Sets the general configuration for tabs. You can configure the tabs to only
        accept clicks or only swipes (gesture left/right and right/left) or both.

        Additionally, if you set `Clear GUI` to true, all of the GUI elements (buttons,
        slider, graphs) will automatically be removed on every tab change.

        By default click and swipe as well as automatic GUI clear is enabled.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        change_tab_config = int(change_tab_config)
        clear_gui = bool(clear_gui)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_TAB_CONFIGURATION, (change_tab_config, clear_gui), 'B !', '')

    def get_gui_tab_configuration(self):
        """
        Returns the tab configuration as set by :func:`Set GUI Tab Configuration`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return GetGUITabConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_TAB_CONFIGURATION, (), '', 'B !'))

    def set_gui_tab_text(self, index, text):
        """
        Adds a text-tab with the given index. The text can have a length of up to 5 characters.

        You can use up to 10 tabs (index 0-9).

        A text-tab with the same index as a icon-tab will overwrite the icon-tab.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        text = create_string(text)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_TAB_TEXT, (index, text), 'B 5s', '')

    def get_gui_tab_text(self, index):
        """
        Returns the text for a given index as set by :func:`Set GUI Tab Text`.

        Additionally the `Active` parameter shows if the tab is currently active/visible
        or not.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return GetGUITabText(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_TAB_TEXT, (index,), 'B', '! 5s'))

    def set_gui_tab_icon(self, index, icon):
        """
        Adds a icon-tab with the given index. The icon can have a width of 28 pixels
        with a height of 6 pixels. It is drawn line-by-line from left to right.

        You can use up to 10 tabs (index 0-9).

        A icon-tab with the same index as a text-tab will overwrite the text-tab.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        icon = list(map(bool, icon))

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_TAB_ICON, (index, icon), 'B 168!', '')

    def get_gui_tab_icon(self, index):
        """
        Returns the icon for a given index as set by :func:`Set GUI Tab Icon`.

        Additionally the `Active` parameter shows if the tab is currently active/visible
        or not.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return GetGUITabIcon(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_TAB_ICON, (index,), 'B', '! 168!'))

    def remove_gui_tab(self, index):
        """
        Removes the tab with the given index.

        You can use index 255 to remove all tabs.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_REMOVE_GUI_TAB, (index,), 'B', '')

    def set_gui_tab_selected(self, index):
        """
        Sets the tab with the given index as selected (drawn as selected on the display).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_TAB_SELECTED, (index,), 'B', '')

    def set_gui_tab_selected_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`GUI Tab Selected` callback
        is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_TAB_SELECTED_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_gui_tab_selected_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set GUI Tab Selected Callback Configuration`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return GetGUITabSelectedCallbackConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_TAB_SELECTED_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def get_gui_tab_selected(self):
        """
        Returns the index of the currently selected tab.
        If there are not tabs, the returned index is -1.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_TAB_SELECTED, (), '', 'b')

    def set_gui_graph_configuration(self, index, graph_type, position_x, position_y, width, height, text_x, text_y):
        """
        Sets the configuration for up to four graphs (index 0-3).

        The graph type can be dot-, line- or bar-graph.

        The x and y position are pixel positions. They have to be within
        the range of (0, 0) to (127, 63). The maximum width is 118 and the
        maximum height is 63.

        You can add a text for the x and y axis with at most 4 characters each.
        The text is drawn at the inside of the graph and it can overwrite some
        of the graph data. If you need the text outside of the graph you can
        leave this text here empty and use :func:`Draw Text` to draw the caption
        outside of the graph.

        The data of the graph can be set and updated with :func:`Set GUI Graph Data`.

        The graph is drawn in a separate GUI buffer and the graph-frame and data will
        always stay on top of the graphics drawn with :func:`Write Pixels`. To
        remove the graph use :func:`Remove GUI Graph`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        graph_type = int(graph_type)
        position_x = int(position_x)
        position_y = int(position_y)
        width = int(width)
        height = int(height)
        text_x = create_string(text_x)
        text_y = create_string(text_y)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_GRAPH_CONFIGURATION, (index, graph_type, position_x, position_y, width, height, text_x, text_y), 'B B B B B B 4s 4s', '')

    def get_gui_graph_configuration(self, index):
        """
        Returns the graph properties for a given `Index` as set by :func:`Set GUI Graph Configuration`.

        Additionally the `Active` parameter shows if a graph is currently active/visible
        or not.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return GetGUIGraphConfiguration(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_GRAPH_CONFIGURATION, (index,), 'B', '! B B B B B 4s 4s'))

    def set_gui_graph_data_low_level(self, index, data_length, data_chunk_offset, data_chunk_data):
        """
        Sets the data for a graph with the given index. You have to configure the graph with
        :func:`Set GUI Graph Configuration` before you can set the first data.

        The graph will show the first n values of the data that you set, where
        n is the width set with :func:`Set GUI Graph Configuration`. If you set
        less then n values it will show the rest of the values as zero.

        The maximum number of data-points you can set is 118 (which also corresponds to the
        maximum width of the graph).

        You have to scale your values to be between 0 and 255. 0 will be shown
        at the bottom of the graph and 255 at the top.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        data_length = int(data_length)
        data_chunk_offset = int(data_chunk_offset)
        data_chunk_data = list(map(int, data_chunk_data))

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_GUI_GRAPH_DATA_LOW_LEVEL, (index, data_length, data_chunk_offset, data_chunk_data), 'B H H 59B', '')

    def get_gui_graph_data_low_level(self, index):
        """
        Returns the graph data for a given index as set by :func:`Set GUI Graph Data`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        return GetGUIGraphDataLowLevel(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_GUI_GRAPH_DATA_LOW_LEVEL, (index,), 'B', 'H H 59B'))

    def remove_gui_graph(self, index):
        """
        Removes the graph with the given index.

        You can use index 255 to remove all graphs.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_REMOVE_GUI_GRAPH, (index,), 'B', '')

    def remove_all_gui(self):
        """
        Removes all GUI elements (buttons, slider, graphs, tabs).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_REMOVE_ALL_GUI, (), '', '')

    def set_touch_led_config(self, config):
        """
        Sets the touch LED configuration. By default the LED is on if the
        LCD is touched.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is off.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_TOUCH_LED_CONFIG, (config,), 'B', '')

    def get_touch_led_config(self):
        """
        Returns the configuration as set by :func:`Set Touch LED Config`

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_TOUCH_LED_CONFIG, (), '', 'B')

    def get_spitfp_error_count(self):
        """
        Returns the error count for the communication between Brick and Bricklet.

        The errors are divided into

        * ACK checksum errors,
        * message checksum errors,
        * framing errors and
        * overflow errors.

        The errors counts are for errors that occur on the Bricklet side. All
        Bricks have a similar function that returns the errors on the Brick side.
        """
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        Sets the bootloader mode and returns the status after the requested
        mode change was instigated.

        You can change from bootloader mode to firmware mode and vice versa. A change
        from bootloader mode to firmware mode will only take place if the entry function,
        device identifier and CRC are present and correct.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        mode = int(mode)

        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def write_pixels(self, x_start, y_start, x_end, y_end, pixels):
        """
        Writes pixels to the specified window.

        The x-axis goes from 0 to 127 and the y-axis from 0 to 63. The pixels are written
        into the window line by line top to bottom and each line is written from left to
        right.

        If automatic draw is enabled (default) the pixels are directly written to
        the screen. Only pixels that have actually changed are updated on the screen,
        the rest stays the same.

        If automatic draw is disabled the pixels are written to an internal buffer and
        the buffer is transferred to the display only after :func:`Draw Buffered Frame`
        is called. This can be used to avoid flicker when drawing a complex frame in
        multiple steps.

        Automatic draw can be configured with the :func:`Set Display Configuration`
        function.
        """
        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)
        pixels = list(map(bool, pixels))

        if len(pixels) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Pixels can be at most 65535 items long')

        pixels_length = len(pixels)
        pixels_chunk_offset = 0

        if pixels_length == 0:
            pixels_chunk_data = [False] * 448
            ret = self.write_pixels_low_level(x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data)
        else:
            with self.stream_lock:
                while pixels_chunk_offset < pixels_length:
                    pixels_chunk_data = create_chunk_data(pixels, pixels_chunk_offset, 448, False)
                    ret = self.write_pixels_low_level(x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data)
                    pixels_chunk_offset += 448

        return ret

    def read_pixels(self, x_start, y_start, x_end, y_end):
        """
        Reads pixels from the specified window.

        The x-axis goes from 0 to 127 and the y-axis from 0 to 63. The pixels are read
        from the window line by line top to bottom and each line is read from left to
        right.

        If automatic draw is enabled (default) the pixels that are read are always the
        same that are shown on the display.

        If automatic draw is disabled the pixels are read from the internal buffer
        (see :func:`Draw Buffered Frame`).

        Automatic draw can be configured with the :func:`Set Display Configuration`
        function.
        """
        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        with self.stream_lock:
            ret = self.read_pixels_low_level(x_start, y_start, x_end, y_end)
            pixels_length = ret.pixels_length
            pixels_out_of_sync = ret.pixels_chunk_offset != 0
            pixels_data = ret.pixels_chunk_data

            while not pixels_out_of_sync and len(pixels_data) < pixels_length:
                ret = self.read_pixels_low_level(x_start, y_start, x_end, y_end)
                pixels_length = ret.pixels_length
                pixels_out_of_sync = ret.pixels_chunk_offset != len(pixels_data)
                pixels_data += ret.pixels_chunk_data

            if pixels_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.pixels_chunk_offset + 480 < pixels_length:
                    ret = self.read_pixels_low_level(x_start, y_start, x_end, y_end)
                    pixels_length = ret.pixels_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Pixels stream is out-of-sync')

        return pixels_data[:pixels_length]

    def set_gui_graph_data(self, index, data):
        """
        Sets the data for a graph with the given index. You have to configure the graph with
        :func:`Set GUI Graph Configuration` before you can set the first data.

        The graph will show the first n values of the data that you set, where
        n is the width set with :func:`Set GUI Graph Configuration`. If you set
        less then n values it will show the rest of the values as zero.

        The maximum number of data-points you can set is 118 (which also corresponds to the
        maximum width of the graph).

        You have to scale your values to be between 0 and 255. 0 will be shown
        at the bottom of the graph and 255 at the top.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)
        data = list(map(int, data))

        if len(data) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Data can be at most 65535 items long')

        data_length = len(data)
        data_chunk_offset = 0

        if data_length == 0:
            data_chunk_data = [0] * 59
            ret = self.set_gui_graph_data_low_level(index, data_length, data_chunk_offset, data_chunk_data)
        else:
            with self.stream_lock:
                while data_chunk_offset < data_length:
                    data_chunk_data = create_chunk_data(data, data_chunk_offset, 59, 0)
                    ret = self.set_gui_graph_data_low_level(index, data_length, data_chunk_offset, data_chunk_data)
                    data_chunk_offset += 59

        return ret

    def get_gui_graph_data(self, index):
        """
        Returns the graph data for a given index as set by :func:`Set GUI Graph Data`.

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        index = int(index)

        with self.stream_lock:
            ret = self.get_gui_graph_data_low_level(index)
            data_length = ret.data_length
            data_out_of_sync = ret.data_chunk_offset != 0
            data_data = ret.data_chunk_data

            while not data_out_of_sync and len(data_data) < data_length:
                ret = self.get_gui_graph_data_low_level(index)
                data_length = ret.data_length
                data_out_of_sync = ret.data_chunk_offset != len(data_data)
                data_data += ret.data_chunk_data

            if data_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.data_chunk_offset + 59 < data_length:
                    ret = self.get_gui_graph_data_low_level(index)
                    data_length = ret.data_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Data stream is out-of-sync')

        return data_data[:data_length]

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

LCD128x64 = BrickletLCD128x64 # for backward compatibility
