# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2020-02-26.      #
#                                                           #
# Python Bindings Version 2.1.24                            #
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

ReadBlackWhiteLowLevel = namedtuple('ReadBlackWhiteLowLevel', ['pixels_length', 'pixels_chunk_offset', 'pixels_chunk_data'])
ReadColorLowLevel = namedtuple('ReadColorLowLevel', ['pixels_length', 'pixels_chunk_offset', 'pixels_chunk_data'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletEPaper296x128(Device):
    """
    Three color 296x128 e-paper display
    """

    DEVICE_IDENTIFIER = 2146
    DEVICE_DISPLAY_NAME = 'E-Paper 296x128 Bricklet'
    DEVICE_URL_PART = 'e_paper_296x128' # internal

    CALLBACK_DRAW_STATUS = 11


    FUNCTION_DRAW = 1
    FUNCTION_GET_DRAW_STATUS = 2
    FUNCTION_WRITE_BLACK_WHITE_LOW_LEVEL = 3
    FUNCTION_READ_BLACK_WHITE_LOW_LEVEL = 4
    FUNCTION_WRITE_COLOR_LOW_LEVEL = 5
    FUNCTION_READ_COLOR_LOW_LEVEL = 6
    FUNCTION_FILL_DISPLAY = 7
    FUNCTION_DRAW_TEXT = 8
    FUNCTION_DRAW_LINE = 9
    FUNCTION_DRAW_BOX = 10
    FUNCTION_SET_UPDATE_MODE = 12
    FUNCTION_GET_UPDATE_MODE = 13
    FUNCTION_SET_DISPLAY_TYPE = 14
    FUNCTION_GET_DISPLAY_TYPE = 15
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

    DRAW_STATUS_IDLE = 0
    DRAW_STATUS_COPYING = 1
    DRAW_STATUS_DRAWING = 2
    COLOR_BLACK = 0
    COLOR_WHITE = 1
    COLOR_RED = 2
    COLOR_GRAY = 2
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
    ORIENTATION_HORIZONTAL = 0
    ORIENTATION_VERTICAL = 1
    UPDATE_MODE_DEFAULT = 0
    UPDATE_MODE_BLACK_WHITE = 1
    UPDATE_MODE_DELTA = 2
    DISPLAY_TYPE_BLACK_WHITE_RED = 0
    DISPLAY_TYPE_BLACK_WHITE_GRAY = 1
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
        Device.__init__(self, uid, ipcon, BrickletEPaper296x128.DEVICE_IDENTIFIER, BrickletEPaper296x128.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletEPaper296x128.FUNCTION_DRAW] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_DRAW_STATUS] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_WRITE_BLACK_WHITE_LOW_LEVEL] = BrickletEPaper296x128.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_READ_BLACK_WHITE_LOW_LEVEL] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_WRITE_COLOR_LOW_LEVEL] = BrickletEPaper296x128.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_READ_COLOR_LOW_LEVEL] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_FILL_DISPLAY] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_DRAW_TEXT] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_DRAW_LINE] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_DRAW_BOX] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_SET_UPDATE_MODE] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_UPDATE_MODE] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_SET_DISPLAY_TYPE] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_DISPLAY_TYPE] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_SET_BOOTLOADER_MODE] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_BOOTLOADER_MODE] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_WRITE_FIRMWARE] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_RESET] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_WRITE_UID] = BrickletEPaper296x128.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEPaper296x128.FUNCTION_READ_UID] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEPaper296x128.FUNCTION_GET_IDENTITY] = BrickletEPaper296x128.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletEPaper296x128.CALLBACK_DRAW_STATUS] = 'B'

        ipcon.add_device(self)

    def draw(self):
        """
        Draws the current black/white and red or gray buffer to the e-paper display.

        The Bricklet does not have any double-buffering. You should not call
        this function while writing to the buffer. See :func:`Get Draw Status`.
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_DRAW, (), '', '')

    def get_draw_status(self):
        """
        Returns one of three draw statuses:

        * Idle
        * Copying: Data is being copied from the buffer of the Bricklet to the buffer of the display.
        * Drawing: The display is updating its content (during this phase the flickering etc happens).

        You can write to the buffer (through one of the write or draw functions) when the status is
        either *idle* or *drawing*. You should not write to the buffer while it is being *copied* to the
        display. There is no double-buffering.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_DRAW_STATUS, (), '', 'B')

    def write_black_white_low_level(self, x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data):
        """
        Writes black/white pixels to the specified window into the buffer.

        The pixels are written into the window line by line top to bottom
        and each line is written from left to right.

        The value 0 (false) corresponds to a black pixel and the value 1 (true) to a
        white pixel.

        This function writes the pixels into the black/white pixel buffer, to draw the
        buffer to the display use :func:`Draw`.

        Use :func:`Write Color` to write red or gray pixels.
        """
        self.check_validity()

        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)
        pixels_length = int(pixels_length)
        pixels_chunk_offset = int(pixels_chunk_offset)
        pixels_chunk_data = list(map(bool, pixels_chunk_data))

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_WRITE_BLACK_WHITE_LOW_LEVEL, (x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data), 'H B H B H H 432!', '')

    def read_black_white_low_level(self, x_start, y_start, x_end, y_end):
        """
        Returns the current content of the black/white pixel buffer for the specified window.

        The pixels are read into the window line by line top to bottom and
        each line is read from left to right.

        The current content of the buffer does not have to be the current content of the display.
        It is possible that the data was not drawn to the display yet and after a restart of
        the Bricklet the buffer will be reset to black, while the display retains its content.
        """
        self.check_validity()

        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        return ReadBlackWhiteLowLevel(*self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_READ_BLACK_WHITE_LOW_LEVEL, (x_start, y_start, x_end, y_end), 'H B H B', 'H H 464!'))

    def write_color_low_level(self, x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data):
        """
        The E-Paper 296x128 Bricklet is available with the colors black/white/red and
        black/white/gray. Depending on the model this function writes either red or
        gray pixels to the specified window into the buffer.

        The pixels are written into the window line by line top to bottom
        and each line is written from left to right.

        The value 0 (false) means that this pixel does not have color. It will be either black
        or white (see :func:`Write Black White`). The value 1 (true) corresponds to a red or gray
        pixel, depending on the Bricklet model.

        This function writes the pixels into the red or gray pixel buffer, to draw the buffer
        to the display use :func:`Draw`.

        Use :func:`Write Black White` to write black/white pixels.
        """
        self.check_validity()

        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)
        pixels_length = int(pixels_length)
        pixels_chunk_offset = int(pixels_chunk_offset)
        pixels_chunk_data = list(map(bool, pixels_chunk_data))

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_WRITE_COLOR_LOW_LEVEL, (x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data), 'H B H B H H 432!', '')

    def read_color_low_level(self, x_start, y_start, x_end, y_end):
        """
        Returns the current content of the red or gray pixel buffer for the specified window.

        The pixels are written into the window line by line top to bottom
        and each line is written from left to right.

        The current content of the buffer does not have to be the current content of the display.
        It is possible that the data was not drawn to the display yet and after a restart of
        the Bricklet the buffer will be reset to black, while the display retains its content.
        """
        self.check_validity()

        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        return ReadColorLowLevel(*self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_READ_COLOR_LOW_LEVEL, (x_start, y_start, x_end, y_end), 'H B H B', 'H H 464!'))

    def fill_display(self, color):
        """
        Fills the complete content of the display with the given color.

        This function writes the pixels into the black/white/red|gray pixel buffer, to draw the buffer
        to the display use :func:`Draw`.
        """
        self.check_validity()

        color = int(color)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_FILL_DISPLAY, (color,), 'B', '')

    def draw_text(self, position_x, position_y, font, color, orientation, text):
        """
        Draws a text with up to 50 characters at the pixel position (x, y).

        You can use one of 9 different font sizes and draw the text in
        black/white/red|gray. The text can be drawn horizontal or vertical.

        This function writes the pixels into the black/white/red|gray pixel buffer, to draw the buffer
        to the display use :func:`Draw`.
        """
        self.check_validity()

        position_x = int(position_x)
        position_y = int(position_y)
        font = int(font)
        color = int(color)
        orientation = int(orientation)
        text = create_string(text)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_DRAW_TEXT, (position_x, position_y, font, color, orientation, text), 'H B B B B 50s', '')

    def draw_line(self, position_x_start, position_y_start, position_x_end, position_y_end, color):
        """
        Draws a line from (x, y)-start to (x, y)-end in the given color.

        This function writes the pixels into the black/white/red|gray pixel buffer, to draw the buffer
        to the display use :func:`Draw`.
        """
        self.check_validity()

        position_x_start = int(position_x_start)
        position_y_start = int(position_y_start)
        position_x_end = int(position_x_end)
        position_y_end = int(position_y_end)
        color = int(color)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_DRAW_LINE, (position_x_start, position_y_start, position_x_end, position_y_end, color), 'H B H B B', '')

    def draw_box(self, position_x_start, position_y_start, position_x_end, position_y_end, fill, color):
        """
        Draws a box from (x, y)-start to (x, y)-end in the given color.

        If you set fill to true, the box will be filled with the
        color. Otherwise only the outline will be drawn.

        This function writes the pixels into the black/white/red|gray pixel buffer, to draw the buffer
        to the display use :func:`Draw`.
        """
        self.check_validity()

        position_x_start = int(position_x_start)
        position_y_start = int(position_y_start)
        position_x_end = int(position_x_end)
        position_y_end = int(position_y_end)
        fill = bool(fill)
        color = int(color)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_DRAW_BOX, (position_x_start, position_y_start, position_x_end, position_y_end, fill, color), 'H B H B ! B', '')

    def set_update_mode(self, update_mode):
        """
        .. note::
         The default update mode corresponds to the default e-paper display
         manufacturer settings. All of the other modes are experimental and
         will result in increased ghosting and possibly other long-term
         side effects.

         If you want to know more about the inner workings of an e-paper display
         take a look at this excellent video from Ben Krasnow:
         `https://www.youtube.com/watch?v=MsbiO8EAsGw <https://www.youtube.com/watch?v=MsbiO8EAsGw>`__.

         If you are not sure about this option, leave the update mode at default.

        Currently there are three update modes available:

        * Default: Settings as given by the manufacturer. An update will take about
          7.5 seconds and during the update the screen will flicker several times.
        * Black/White: This will only update the black/white pixel. It uses the manufacturer
          settings for black/white and ignores the red or gray pixel buffer. With this mode the
          display will flicker once and it takes about 2.5 seconds. Compared to the default settings
          there is more ghosting.
        * Delta: This will only update the black/white pixel. It uses an aggressive method where
          the changes are not applied for a whole buffer but only for the delta between the last
          and the next buffer. With this mode the display will not flicker during an update and
          it takes about 900-950ms. Compared to the other two settings there is more ghosting. This
          mode can be used for something like a flicker-free live update of a text.

        With the black/white/red display if you use either the black/white or the delta mode,
        after a while of going back and forth between black and white the white color will
        start to appear red-ish or pink-ish.

        If you use the aggressive delta mode and rapidly change the content, we recommend that you
        change back to the default mode every few hours and in the default mode cycle between the
        three available colors a few times. This will get rid of the ghosting and after that you can
        go back to the delta mode with flicker-free updates.
        """
        self.check_validity()

        update_mode = int(update_mode)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_SET_UPDATE_MODE, (update_mode,), 'B', '')

    def get_update_mode(self):
        """
        Returns the update mode as set by :func:`Set Update Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_UPDATE_MODE, (), '', 'B')

    def set_display_type(self, display_type):
        """
        Sets the type of the display. The e-paper display is available
        in black/white/red and black/white/gray. This will be factory set
        during the flashing and testing phase. The value is saved in
        non-volatile memory and will stay after a power cycle.
        """
        self.check_validity()

        display_type = int(display_type)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_SET_DISPLAY_TYPE, (display_type,), 'B', '')

    def get_display_type(self):
        """
        Returns the type of the e-paper display. It can either be
        black/white/red or black/white/gray.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_DISPLAY_TYPE, (), '', 'B')

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
        self.check_validity()

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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
        self.check_validity()

        mode = int(mode)

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        The Raspberry Pi HAT (Zero) Brick is always at position 'i' and the Bricklet
        connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always as
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletEPaper296x128.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def write_black_white(self, x_start, y_start, x_end, y_end, pixels):
        """
        Writes black/white pixels to the specified window into the buffer.

        The pixels are written into the window line by line top to bottom
        and each line is written from left to right.

        The value 0 (false) corresponds to a black pixel and the value 1 (true) to a
        white pixel.

        This function writes the pixels into the black/white pixel buffer, to draw the
        buffer to the display use :func:`Draw`.

        Use :func:`Write Color` to write red or gray pixels.
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
            pixels_chunk_data = [False] * 432
            ret = self.write_black_white_low_level(x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data)
        else:
            with self.stream_lock:
                while pixels_chunk_offset < pixels_length:
                    pixels_chunk_data = create_chunk_data(pixels, pixels_chunk_offset, 432, False)
                    ret = self.write_black_white_low_level(x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data)
                    pixels_chunk_offset += 432

        return ret

    def read_black_white(self, x_start, y_start, x_end, y_end):
        """
        Returns the current content of the black/white pixel buffer for the specified window.

        The pixels are read into the window line by line top to bottom and
        each line is read from left to right.

        The current content of the buffer does not have to be the current content of the display.
        It is possible that the data was not drawn to the display yet and after a restart of
        the Bricklet the buffer will be reset to black, while the display retains its content.
        """
        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        with self.stream_lock:
            ret = self.read_black_white_low_level(x_start, y_start, x_end, y_end)
            pixels_length = ret.pixels_length
            pixels_out_of_sync = ret.pixels_chunk_offset != 0
            pixels_data = ret.pixels_chunk_data

            while not pixels_out_of_sync and len(pixels_data) < pixels_length:
                ret = self.read_black_white_low_level(x_start, y_start, x_end, y_end)
                pixels_length = ret.pixels_length
                pixels_out_of_sync = ret.pixels_chunk_offset != len(pixels_data)
                pixels_data += ret.pixels_chunk_data

            if pixels_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.pixels_chunk_offset + 464 < pixels_length:
                    ret = self.read_black_white_low_level(x_start, y_start, x_end, y_end)
                    pixels_length = ret.pixels_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Pixels stream is out-of-sync')

        return pixels_data[:pixels_length]

    def write_color(self, x_start, y_start, x_end, y_end, pixels):
        """
        The E-Paper 296x128 Bricklet is available with the colors black/white/red and
        black/white/gray. Depending on the model this function writes either red or
        gray pixels to the specified window into the buffer.

        The pixels are written into the window line by line top to bottom
        and each line is written from left to right.

        The value 0 (false) means that this pixel does not have color. It will be either black
        or white (see :func:`Write Black White`). The value 1 (true) corresponds to a red or gray
        pixel, depending on the Bricklet model.

        This function writes the pixels into the red or gray pixel buffer, to draw the buffer
        to the display use :func:`Draw`.

        Use :func:`Write Black White` to write black/white pixels.
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
            pixels_chunk_data = [False] * 432
            ret = self.write_color_low_level(x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data)
        else:
            with self.stream_lock:
                while pixels_chunk_offset < pixels_length:
                    pixels_chunk_data = create_chunk_data(pixels, pixels_chunk_offset, 432, False)
                    ret = self.write_color_low_level(x_start, y_start, x_end, y_end, pixels_length, pixels_chunk_offset, pixels_chunk_data)
                    pixels_chunk_offset += 432

        return ret

    def read_color(self, x_start, y_start, x_end, y_end):
        """
        Returns the current content of the red or gray pixel buffer for the specified window.

        The pixels are written into the window line by line top to bottom
        and each line is written from left to right.

        The current content of the buffer does not have to be the current content of the display.
        It is possible that the data was not drawn to the display yet and after a restart of
        the Bricklet the buffer will be reset to black, while the display retains its content.
        """
        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        with self.stream_lock:
            ret = self.read_color_low_level(x_start, y_start, x_end, y_end)
            pixels_length = ret.pixels_length
            pixels_out_of_sync = ret.pixels_chunk_offset != 0
            pixels_data = ret.pixels_chunk_data

            while not pixels_out_of_sync and len(pixels_data) < pixels_length:
                ret = self.read_color_low_level(x_start, y_start, x_end, y_end)
                pixels_length = ret.pixels_length
                pixels_out_of_sync = ret.pixels_chunk_offset != len(pixels_data)
                pixels_data += ret.pixels_chunk_data

            if pixels_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.pixels_chunk_offset + 464 < pixels_length:
                    ret = self.read_color_low_level(x_start, y_start, x_end, y_end)
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

EPaper296x128 = BrickletEPaper296x128 # for backward compatibility
