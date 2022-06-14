# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2022-06-14.      #
#                                                           #
# Python Bindings Version 2.1.30                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except (ValueError, ImportError):
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetRGBValue = namedtuple('RGBValue', ['r', 'g', 'b'])
GetEnergyMeterValues = namedtuple('EnergyMeterValues', ['power', 'energy_relative', 'energy_absolute', 'phases_active', 'phases_connected'])
GetEnergyMeterDetailedValuesLowLevel = namedtuple('EnergyMeterDetailedValuesLowLevel', ['values_chunk_offset', 'values_chunk_data'])
GetEnergyMeterState = namedtuple('EnergyMeterState', ['energy_meter_type', 'error_count'])
GetAllData1 = namedtuple('AllData1', ['value', 'r', 'g', 'b', 'power', 'energy_relative', 'energy_absolute', 'phases_active', 'phases_connected', 'energy_meter_type', 'error_count', 'input', 'output', 'input_configuration', 'voltage', 'contactor_check_state'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletWARPEnergyManager(Device):
    r"""
    TBD
    """

    DEVICE_IDENTIFIER = 2169
    DEVICE_DISPLAY_NAME = 'WARP Energy Manager Bricklet'
    DEVICE_URL_PART = 'warp_energy_manager' # internal



    FUNCTION_SET_CONTACTOR = 1
    FUNCTION_GET_CONTACTOR = 2
    FUNCTION_SET_RGB_VALUE = 3
    FUNCTION_GET_RGB_VALUE = 4
    FUNCTION_GET_ENERGY_METER_VALUES = 5
    FUNCTION_GET_ENERGY_METER_DETAILED_VALUES_LOW_LEVEL = 6
    FUNCTION_GET_ENERGY_METER_STATE = 7
    FUNCTION_RESET_ENERGY_METER_RELATIVE_ENERGY = 8
    FUNCTION_GET_INPUT = 9
    FUNCTION_SET_OUTPUT = 10
    FUNCTION_GET_OUTPUT = 11
    FUNCTION_SET_INPUT_CONFIGURATION = 12
    FUNCTION_GET_INPUT_CONFIGURATION = 13
    FUNCTION_GET_INPUT_VOLTAGE = 14
    FUNCTION_GET_STATE = 15
    FUNCTION_GET_ALL_DATA_1 = 16
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

    ENERGY_METER_TYPE_NOT_AVAILABLE = 0
    ENERGY_METER_TYPE_SDM72 = 1
    ENERGY_METER_TYPE_SDM630 = 2
    ENERGY_METER_TYPE_SDM72V2 = 3
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
        r"""
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon, BrickletWARPEnergyManager.DEVICE_IDENTIFIER, BrickletWARPEnergyManager.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_CONTACTOR] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_CONTACTOR] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_RGB_VALUE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_RGB_VALUE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_ENERGY_METER_VALUES] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_ENERGY_METER_DETAILED_VALUES_LOW_LEVEL] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_ENERGY_METER_STATE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_RESET_ENERGY_METER_RELATIVE_ENERGY] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_INPUT] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_OUTPUT] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_OUTPUT] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_INPUT_CONFIGURATION] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_INPUT_CONFIGURATION] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_INPUT_VOLTAGE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_STATE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_ALL_DATA_1] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_BOOTLOADER_MODE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_BOOTLOADER_MODE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_WRITE_FIRMWARE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_RESET] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_WRITE_UID] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_READ_UID] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWARPEnergyManager.FUNCTION_GET_IDENTITY] = BrickletWARPEnergyManager.RESPONSE_EXPECTED_ALWAYS_TRUE


        ipcon.add_device(self)

    def set_contactor(self, value):
        r"""
        TBD
        """
        self.check_validity()

        value = bool(value)

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_CONTACTOR, (value,), '!', 0, '')

    def get_contactor(self):
        r"""
        TBD
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_CONTACTOR, (), '', 9, '!')

    def set_rgb_value(self, r, g, b):
        r"""
        Sets the *r*, *g* and *b* values for the LED.
        """
        self.check_validity()

        r = int(r)
        g = int(g)
        b = int(b)

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_RGB_VALUE, (r, g, b), 'B B B', 0, '')

    def get_rgb_value(self):
        r"""
        Returns the *r*, *g* and *b* values of the LED as set by :func:`Set RGB Value`.
        """
        self.check_validity()

        return GetRGBValue(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_RGB_VALUE, (), '', 11, 'B B B'))

    def get_energy_meter_values(self):
        r"""
        TODO
        """
        self.check_validity()

        return GetEnergyMeterValues(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_ENERGY_METER_VALUES, (), '', 22, 'f f f 3! 3!'))

    def get_energy_meter_detailed_values_low_level(self):
        r"""
        TBD
        """
        self.check_validity()

        return GetEnergyMeterDetailedValuesLowLevel(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_ENERGY_METER_DETAILED_VALUES_LOW_LEVEL, (), '', 70, 'H 15f'))

    def get_energy_meter_state(self):
        r"""
        TODO
        """
        self.check_validity()

        return GetEnergyMeterState(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_ENERGY_METER_STATE, (), '', 33, 'B 6I'))

    def reset_energy_meter_relative_energy(self):
        r"""
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_RESET_ENERGY_METER_RELATIVE_ENERGY, (), '', 0, '')

    def get_input(self):
        r"""
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_INPUT, (), '', 9, '2!')

    def set_output(self, output):
        r"""
        TODO
        """
        self.check_validity()

        output = bool(output)

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_OUTPUT, (output,), '!', 0, '')

    def get_output(self):
        r"""
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_OUTPUT, (), '', 9, '!')

    def set_input_configuration(self, input_configuration):
        r"""
        TODO
        """
        self.check_validity()

        input_configuration = list(map(int, input_configuration))

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_INPUT_CONFIGURATION, (input_configuration,), '2B', 0, '')

    def get_input_configuration(self):
        r"""
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_INPUT_CONFIGURATION, (), '', 10, '2B')

    def get_input_voltage(self):
        r"""
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_INPUT_VOLTAGE, (), '', 10, 'H')

    def get_state(self):
        r"""
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_STATE, (), '', 9, 'B')

    def get_all_data_1(self):
        r"""
        TODO
        """
        self.check_validity()

        return GetAllData1(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_ALL_DATA_1, (), '', 58, '! B B B f f f 3! 3! B 6I 2! ! 2B H B'))

    def get_spitfp_error_count(self):
        r"""
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

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 24, 'I I I I'))

    def set_bootloader_mode(self, mode):
        r"""
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

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 9, 'B')

    def get_bootloader_mode(self):
        r"""
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_BOOTLOADER_MODE, (), '', 9, 'B')

    def set_write_firmware_pointer(self, pointer):
        r"""
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

    def write_firmware(self, data):
        r"""
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

    def set_status_led_config(self, config):
        r"""
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', 0, '')

    def get_status_led_config(self):
        r"""
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 9, 'B')

    def get_chip_temperature(self):
        r"""
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 10, 'h')

    def reset(self):
        r"""
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_RESET, (), '', 0, '')

    def write_uid(self, uid):
        r"""
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_WRITE_UID, (uid,), 'I', 0, '')

    def read_uid(self):
        r"""
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_READ_UID, (), '', 12, 'I')

    def get_identity(self):
        r"""
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        A Bricklet connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always at
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletWARPEnergyManager.FUNCTION_GET_IDENTITY, (), '', 33, '8s 8s c 3B 3B H'))

    def get_energy_meter_detailed_values(self):
        r"""
        TBD
        """
        values_length = 85

        with self.stream_lock:
            ret = self.get_energy_meter_detailed_values_low_level()

            if ret.values_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                values_length = 0
                values_out_of_sync = False
                values_data = ()
            else:
                values_out_of_sync = ret.values_chunk_offset != 0
                values_data = ret.values_chunk_data

            while not values_out_of_sync and len(values_data) < values_length:
                ret = self.get_energy_meter_detailed_values_low_level()
                values_out_of_sync = ret.values_chunk_offset != len(values_data)
                values_data += ret.values_chunk_data

            if values_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.values_chunk_offset + 15 < values_length:
                    ret = self.get_energy_meter_detailed_values_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Values stream is out-of-sync')

        return values_data[:values_length]

WARPEnergyManager = BrickletWARPEnergyManager # for backward compatibility
