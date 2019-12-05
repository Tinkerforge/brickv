# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-12-05.      #
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

GetPosition = namedtuple('Position', ['x', 'y'])
GetPositionCallbackConfiguration = namedtuple('PositionCallbackConfiguration', ['period', 'value_has_to_change'])
GetPressedCallbackConfiguration = namedtuple('PressedCallbackConfiguration', ['period', 'value_has_to_change'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletJoystickV2(Device):
    """
    2-axis joystick with push-button
    """

    DEVICE_IDENTIFIER = 2138
    DEVICE_DISPLAY_NAME = 'Joystick Bricklet 2.0'
    DEVICE_URL_PART = 'joystick_v2' # internal

    CALLBACK_POSITION = 6
    CALLBACK_PRESSED = 9


    FUNCTION_GET_POSITION = 1
    FUNCTION_IS_PRESSED = 2
    FUNCTION_CALIBRATE = 3
    FUNCTION_SET_POSITION_CALLBACK_CONFIGURATION = 4
    FUNCTION_GET_POSITION_CALLBACK_CONFIGURATION = 5
    FUNCTION_SET_PRESSED_CALLBACK_CONFIGURATION = 7
    FUNCTION_GET_PRESSED_CALLBACK_CONFIGURATION = 8
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

        self.response_expected[BrickletJoystickV2.FUNCTION_GET_POSITION] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_IS_PRESSED] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_CALIBRATE] = BrickletJoystickV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletJoystickV2.FUNCTION_SET_POSITION_CALLBACK_CONFIGURATION] = BrickletJoystickV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_POSITION_CALLBACK_CONFIGURATION] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_SET_PRESSED_CALLBACK_CONFIGURATION] = BrickletJoystickV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_PRESSED_CALLBACK_CONFIGURATION] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletJoystickV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletJoystickV2.FUNCTION_WRITE_FIRMWARE] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletJoystickV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_RESET] = BrickletJoystickV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletJoystickV2.FUNCTION_WRITE_UID] = BrickletJoystickV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletJoystickV2.FUNCTION_READ_UID] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystickV2.FUNCTION_GET_IDENTITY] = BrickletJoystickV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletJoystickV2.CALLBACK_POSITION] = 'h h'
        self.callback_formats[BrickletJoystickV2.CALLBACK_PRESSED] = '!'


    def get_position(self):
        """
        Returns the position of the joystick. The middle position of the joystick is x=0, y=0.
        The returned values are averaged and calibrated (see :func:`Calibrate`).

        If you want to get the position periodically, it is recommended to use the
        :cb:`Position` callback and set the period with
        :func:`Set Position Callback Configuration`.
        """
        return GetPosition(*self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_POSITION, (), '', 'h h'))

    def is_pressed(self):
        """
        Returns *true* if the button is pressed and *false* otherwise.

        If you want to get the press-state periodically, it is recommended to use the
        :cb:`Pressed` callback and set the period with
        :func:`Set Pressed Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_IS_PRESSED, (), '', '!')

    def calibrate(self):
        """
        Calibrates the middle position of the joystick. If your Joystick Bricklet 2.0
        does not return x=0 and y=0 in the middle position, call this function
        while the joystick is standing still in the middle position.

        The resulting calibration will be saved in non-volatile memory,
        thus you only have to calibrate it once.
        """
        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_CALIBRATE, (), '', '')

    def set_position_callback_configuration(self, period, value_has_to_change):
        """
        The period is the period with which the :cb:`Position`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after at least one of the values has changed. If the values didn't
        change within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_SET_POSITION_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_position_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set Position Callback Configuration`.
        """
        return GetPositionCallbackConfiguration(*self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_POSITION_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def set_pressed_callback_configuration(self, period, value_has_to_change):
        """
        The period is the period with which the :cb:`Pressed`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after at least one of the values has changed. If the values didn't
        change within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_SET_PRESSED_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_pressed_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set Pressed Callback Configuration`.
        """
        return GetPressedCallbackConfiguration(*self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_PRESSED_CALLBACK_CONFIGURATION, (), '', 'I !'))

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_READ_UID, (), '', 'I')

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
        return GetIdentity(*self.ipcon.send_request(self, BrickletJoystickV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

JoystickV2 = BrickletJoystickV2 # for backward compatibility
