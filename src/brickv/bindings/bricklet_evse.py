# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2020-09-29.      #
#                                                           #
# Python Bindings Version 2.1.26                            #
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

GetState = namedtuple('State', ['iec61851_state', 'contactor_state', 'contactor_error', 'lock_state', 'time_since_state_change', 'uptime'])
GetHardwareConfiguration = namedtuple('HardwareConfiguration', ['jumper_configuration', 'has_lock_switch'])
GetLowLevelState = namedtuple('LowLevelState', ['low_level_mode_enabled', 'led_state', 'cp_pwm_duty_cycle', 'adc_values', 'voltages', 'resistances', 'gpio', 'motor_direction', 'motor_duty_cycle'])
GetADCCalibration = namedtuple('ADCCalibration', ['calibration_ongoing', 'min_value', 'max_value'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletEVSE(Device):
    """
    TBD
    """

    DEVICE_IDENTIFIER = 2159
    DEVICE_DISPLAY_NAME = 'EVSE Bricklet'
    DEVICE_URL_PART = 'evse' # internal



    FUNCTION_GET_STATE = 1
    FUNCTION_GET_HARDWARE_CONFIGURATION = 2
    FUNCTION_GET_LOW_LEVEL_STATE = 3
    FUNCTION_SET_LOW_LEVEL_OUTPUT = 4
    FUNCTION_CALIBRATE_ADC = 5
    FUNCTION_GET_ADC_CALIBRATION = 6
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

    IEC61851_STATE_A = 0
    IEC61851_STATE_B = 1
    IEC61851_STATE_C = 2
    IEC61851_STATE_D = 3
    IEC61851_STATE_EF = 4
    LED_STATE_OFF = 0
    LED_STATE_ON = 1
    LED_STATE_BLINKING = 2
    LED_STATE_BREATHING = 3
    CONTACTOR_STATE_AC1_NLIVE_AC2_NLIVE = 0
    CONTACTOR_STATE_AC1_LIVE_AC2_NLIVE = 1
    CONTACTOR_STATE_AC1_NLIVE_AC2_LIVE = 2
    CONTACTOR_STATE_AC1_LIVE_AC2_LIVE = 3
    LOCK_STATE_INIT = 0
    LOCK_STATE_OPEN = 1
    LOCK_STATE_CLOSING = 2
    LOCK_STATE_CLOSE = 3
    LOCK_STATE_OPENING = 4
    LOCK_STATE_ERROR = 5
    JUMPER_CONFIGURATION_6A = 0
    JUMPER_CONFIGURATION_10A = 1
    JUMPER_CONFIGURATION_13A = 2
    JUMPER_CONFIGURATION_16A = 3
    JUMPER_CONFIGURATION_20A = 4
    JUMPER_CONFIGURATION_25A = 5
    JUMPER_CONFIGURATION_32A = 6
    JUMPER_CONFIGURATION_SOFTWARE = 7
    JUMPER_CONFIGURATION_UNCONFIGURED = 8
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
        Device.__init__(self, uid, ipcon, BrickletEVSE.DEVICE_IDENTIFIER, BrickletEVSE.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletEVSE.FUNCTION_GET_STATE] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_HARDWARE_CONFIGURATION] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_LOW_LEVEL_STATE] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_SET_LOW_LEVEL_OUTPUT] = BrickletEVSE.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSE.FUNCTION_CALIBRATE_ADC] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_ADC_CALIBRATION] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_SET_BOOTLOADER_MODE] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_BOOTLOADER_MODE] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletEVSE.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSE.FUNCTION_WRITE_FIRMWARE] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletEVSE.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSE.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_RESET] = BrickletEVSE.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSE.FUNCTION_WRITE_UID] = BrickletEVSE.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSE.FUNCTION_READ_UID] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSE.FUNCTION_GET_IDENTITY] = BrickletEVSE.RESPONSE_EXPECTED_ALWAYS_TRUE


        ipcon.add_device(self)

    def get_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetState(*self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_STATE, (), '', 20, 'B B B B I I'))

    def get_hardware_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return GetHardwareConfiguration(*self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_HARDWARE_CONFIGURATION, (), '', 10, 'B !'))

    def get_low_level_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetLowLevelState(*self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_LOW_LEVEL_STATE, (), '', 34, '! B H 2H 3h 2I 5! ! H'))

    def set_low_level_output(self, low_level_mode_enabled, cp_duty_cycle, motor_direction, motor_duty_cycle, relay_enabled, password):
        """
        TODO
        """
        self.check_validity()

        low_level_mode_enabled = bool(low_level_mode_enabled)
        cp_duty_cycle = int(cp_duty_cycle)
        motor_direction = bool(motor_direction)
        motor_duty_cycle = int(motor_duty_cycle)
        relay_enabled = int(relay_enabled)
        password = int(password)

        self.ipcon.send_request(self, BrickletEVSE.FUNCTION_SET_LOW_LEVEL_OUTPUT, (low_level_mode_enabled, cp_duty_cycle, motor_direction, motor_duty_cycle, relay_enabled, password), '! H ! H H I', 0, '')

    def calibrate_adc(self, password):
        """
        TODO
        """
        self.check_validity()

        password = int(password)

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_CALIBRATE_ADC, (password,), 'I', 9, '!')

    def get_adc_calibration(self):
        """
        TODO
        """
        self.check_validity()

        return GetADCCalibration(*self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_ADC_CALIBRATION, (), '', 13, '! h h'))

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

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 24, 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 9, 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_BOOTLOADER_MODE, (), '', 9, 'B')

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

        self.ipcon.send_request(self, BrickletEVSE.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

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

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

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

        self.ipcon.send_request(self, BrickletEVSE.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', 0, '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 9, 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 10, 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSE.FUNCTION_RESET, (), '', 0, '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletEVSE.FUNCTION_WRITE_UID, (uid,), 'I', 0, '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSE.FUNCTION_READ_UID, (), '', 12, 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        A Bricklet connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always as
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletEVSE.FUNCTION_GET_IDENTITY, (), '', 33, '8s 8s c 3B 3B H'))

EVSE = BrickletEVSE # for backward compatibility
