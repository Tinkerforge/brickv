# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2020-07-30.      #
#                                                           #
# Python Bindings Version 2.1.26                            #
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

DebugGetDiscretes = namedtuple('DebugGetDiscretes', ['rx_discretes', 'tx_discretes'])
DebugReadRegisterLowLevel = namedtuple('DebugReadRegisterLowLevel', ['value_length', 'value_data', 'rw_error'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])
DebugReadRegister = namedtuple('DebugReadRegister', ['value', 'rw_error'])

class BrickletARINC429(Device):
    """
    TBD
    """

    DEVICE_IDENTIFIER = 2160
    DEVICE_DISPLAY_NAME = 'ARINC429 Bricklet'
    DEVICE_URL_PART = 'arinc429' # internal



    FUNCTION_DEBUG_GET_DISCRETES = 1
    FUNCTION_DEBUG_READ_REGISTER_LOW_LEVEL = 2
    FUNCTION_DEBUG_WRITE_REGISTER_LOW_LEVEL = 3
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

    RW_ERROR_OK = 0
    RW_ERROR_NO_WRITE = 1
    RW_ERROR_NO_READ = 2
    RW_ERROR_INVALID_OP_CODE = 3
    RW_ERROR_INVALID_LENGTH = 4
    RW_ERROR_SPI = 5
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
        Device.__init__(self, uid, ipcon, BrickletARINC429.DEVICE_IDENTIFIER, BrickletARINC429.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletARINC429.FUNCTION_DEBUG_GET_DISCRETES] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_DEBUG_READ_REGISTER_LOW_LEVEL] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_DEBUG_WRITE_REGISTER_LOW_LEVEL] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_SET_BOOTLOADER_MODE] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_GET_BOOTLOADER_MODE] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletARINC429.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletARINC429.FUNCTION_WRITE_FIRMWARE] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletARINC429.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletARINC429.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_RESET] = BrickletARINC429.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletARINC429.FUNCTION_WRITE_UID] = BrickletARINC429.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletARINC429.FUNCTION_READ_UID] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletARINC429.FUNCTION_GET_IDENTITY] = BrickletARINC429.RESPONSE_EXPECTED_ALWAYS_TRUE


        ipcon.add_device(self)

    def debug_get_discretes(self):
        """
        Debug function to read the discrete signals from the A429 chip.

        RX Discretes Bit   9: MB2-1   - pending frame in RX2, PRIO 1
                           8: MB2-2   -                            2
                           7: MB2-3   -                            3
                           6: R2FLAG  -                       FIFO
                           5: R2INT   -                       FIFO
                           4: MB1-1   - pending frame in RX1, PRIO 1
                           3: MB1-2   -                            2
                           2: MB1-3   -                            3
                           1: R1FLAG  -                       FIFO
                           0: R1INT   -                       FIFO

        TX Discretes Bit 2-7: unused
                           1: TFULL   - TX buffer full
                           0: TEMPTY  - TX buffer empty
        """
        self.check_validity()

        return DebugGetDiscretes(*self.ipcon.send_request(self, BrickletARINC429.FUNCTION_DEBUG_GET_DISCRETES, (), '', 12, 'H H'))

    def debug_read_register_low_level(self, op_code):
        """
        Debug function to read from a SPI register of the A429 chip.
        """
        self.check_validity()

        op_code = int(op_code)

        return DebugReadRegisterLowLevel(*self.ipcon.send_request(self, BrickletARINC429.FUNCTION_DEBUG_READ_REGISTER_LOW_LEVEL, (op_code,), 'B', 42, 'B 32B B'))

    def debug_write_register_low_level(self, op_code, value_length, value_data):
        """
        Debug function to write to a SPI register of the A429 chip.
        """
        self.check_validity()

        op_code = int(op_code)
        value_length = int(value_length)
        value_data = list(map(int, value_data))

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_DEBUG_WRITE_REGISTER_LOW_LEVEL, (op_code, value_length, value_data), 'B B 32B', 9, 'B')

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

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletARINC429.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 24, 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 9, 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_GET_BOOTLOADER_MODE, (), '', 9, 'B')

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

        self.ipcon.send_request(self, BrickletARINC429.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

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

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

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

        self.ipcon.send_request(self, BrickletARINC429.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', 0, '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 9, 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 10, 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletARINC429.FUNCTION_RESET, (), '', 0, '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletARINC429.FUNCTION_WRITE_UID, (uid,), 'I', 0, '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletARINC429.FUNCTION_READ_UID, (), '', 12, 'I')

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
        return GetIdentity(*self.ipcon.send_request(self, BrickletARINC429.FUNCTION_GET_IDENTITY, (), '', 33, '8s 8s c 3B 3B H'))

    def debug_read_register(self, op_code):
        """
        Debug function to read from a SPI register of the A429 chip.
        """
        op_code = int(op_code)

        ret = self.debug_read_register_low_level(op_code)

        return DebugReadRegister(ret.value_data[:ret.value_length], ret.rw_error)

    def debug_write_register(self, op_code, value):
        """
        Debug function to write to a SPI register of the A429 chip.
        """
        op_code = int(op_code)
        value = list(map(int, value))

        value_length = len(value)
        value_data = list(value) # make a copy so we can potentially extend it

        if value_length > 32:
            raise Error(Error.INVALID_PARAMETER, 'Value can be at most 32 items long')

        if value_length < 32:
            value_data += [0] * (32 - value_length)

        return self.debug_write_register_low_level(op_code, value_length, value_data)

ARINC429 = BrickletARINC429 # for backward compatibility
