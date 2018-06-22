# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-06-22.      #
#                                                           #
# Python Bindings Version 2.1.17                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

ReadPixelsLowLevel = namedtuple('ReadPixelsLowLevel', ['pixels_length', 'pixels_chunk_offset', 'pixels_chunk_data'])
GetDisplayConfiguration = namedtuple('DisplayConfiguration', ['contrast', 'backlight', 'invert', 'automatic_draw'])
GetTouchPosition = namedtuple('TouchPosition', ['pressure', 'x', 'y', 'age'])
GetTouchPositionCallbackConfiguration = namedtuple('TouchPositionCallbackConfiguration', ['period', 'value_has_to_change'])
GetTouchGesture = namedtuple('TouchGesture', ['gesture', 'duration', 'x_start', 'y_start', 'x_end', 'y_end', 'age'])
GetTouchGestureCallbackConfiguration = namedtuple('TouchGestureCallbackConfiguration', ['period', 'value_has_to_change'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLCD128x64(Device):
    """
    LCD with 128x64 pixel
    """

    DEVICE_IDENTIFIER = 298
    DEVICE_DISPLAY_NAME = 'LCD 128x64 Bricklet'
    DEVICE_URL_PART = 'lcd_128x64' # internal

    CALLBACK_TOUCH_POSITION = 11
    CALLBACK_TOUCH_GESTURE = 15


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

        self.api_version = (2, 0, 0)

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
        self.callback_formats[BrickletLCD128x64.CALLBACK_TOUCH_GESTURE] = 'B I H H H H I'


    def write_pixels_low_level(self, x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data):
        """
        Writes pixels to the specified window.

        The x-axis goes from 0-127 and the y-axis from 0-63. The pixels are written
        into the window line by line from left to right.

        If automatic draw is enabled (default) the pixels are directly written to
        the screen and only changes are updated. If you only need to update a few
        pixels, only these pixels are updated on the screen, the rest stays the same.

        If automatic draw is disabled the pixels are written to a buffer and the
        buffer is transferred to the display only after :func:`Draw Buffered Frame`
        is called.

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

        The x-axis goes from 0-127 and the y-axis from 0-63. The pixels are read
        from the window line by line from left to right.

        If automatic draw is enabled the pixels that are read are always the same that are
        shown on the display.

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
        from 0 to 100 and you can invert the color (black/white) of the display.

        If automatic draw is set to *true*, the display is automatically updated with every
        call of :func:`Write Pixels` or :func:`Write Line`. If it is set to false, the
        changes are written into a temporary buffer and only shown on the display after
        a call of :func:`Draw Buffered Frame`.

        The default values are contrast 21, backlight intensity 100, inverting off
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
        """
        line = int(line)
        position = int(position)
        text = create_string(text)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_WRITE_LINE, (line, position, text), 'B B 22s', '')

    def draw_buffered_frame(self, force_complete_redraw):
        """
        Draws the currently buffered frame. Normally each call of :func:`Write Pixels` or
        :func:`Write Line` draws directly onto the display. If you turn automatic draw off
        (:func:`Set Display Configuration`), the data is written in a temporary buffer and
        only transferred to the display by calling this function.

        Set the *force complete redraw* parameter to *true* to redraw the whole display
        instead of only the changed parts. Normally it should not be necessary to set this to
        *true*. It may only become necessary in case of stuck pixels because of errors.
        """
        force_complete_redraw = bool(force_complete_redraw)

        self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_DRAW_BUFFERED_FRAME, (force_complete_redraw,), '!', '')

    def get_touch_position(self):
        """
        Returns the last valid touch position.

        * *X*: Touch position on x-axis (0-127)
        * *Y*: Touch position on y-axis (0-63)
        * *Pressure*: Amount of pressure applied by the user (0-300).
        * *Age*: Age of touch press in ms (how long ago it was).
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

        Additionally to the gestures a vector with a start and end position of the gesture is is
        provided. You can use this vecotr do determine a more exact location of the gesture (e.g.
        the swipe from top to bottom was on the left or right part of the screen).

        The *age*-parameter corresponds to the age of gesture in ms (how long ago it was).
        """
        return GetTouchGesture(*self.ipcon.send_request(self, BrickletLCD128x64.FUNCTION_GET_TOUCH_GESTURE, (), '', 'B I H H H H I'))

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

        The x-axis goes from 0-127 and the y-axis from 0-63. The pixels are written
        into the window line by line from left to right.

        If automatic draw is enabled (default) the pixels are directly written to
        the screen and only changes are updated. If you only need to update a few
        pixels, only these pixels are updated on the screen, the rest stays the same.

        If automatic draw is disabled the pixels are written to a buffer and the
        buffer is transferred to the display only after :func:`Draw Buffered Frame`
        is called.

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

        The x-axis goes from 0-127 and the y-axis from 0-63. The pixels are read
        from the window line by line from left to right.

        If automatic draw is enabled the pixels that are read are always the same that are
        shown on the display.

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

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

LCD128x64 = BrickletLCD128x64 # for backward compatibility
