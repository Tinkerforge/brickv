# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-11-27.      #
#                                                           #
# Python Bindings Version 2.1.24                            #
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

GetValues = namedtuple('Values', ['gas_concentration', 'temperature', 'humidity', 'gas_type'])
GetCalibration = namedtuple('Calibration', ['adc_count_zero', 'temperature_zero', 'humidity_zero', 'compensation_zero_low', 'compensation_zero_high', 'ppm_span', 'adc_count_span', 'temperature_span', 'humidity_span', 'compensation_span_low', 'compensation_span_high', 'temperature_offset', 'humidity_offset', 'sensitivity'])
GetValuesCallbackConfiguration = namedtuple('ValuesCallbackConfiguration', ['period', 'value_has_to_change'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletGas(Device):
    """
    TBD
    """

    DEVICE_IDENTIFIER = 2155
    DEVICE_DISPLAY_NAME = 'Gas Bricklet'
    DEVICE_URL_PART = 'gas' # internal

    CALLBACK_VALUES = 7


    FUNCTION_GET_VALUES = 1
    FUNCTION_GET_ADC_COUNT = 2
    FUNCTION_SET_CALIBRATION = 3
    FUNCTION_GET_CALIBRATION = 4
    FUNCTION_SET_VALUES_CALLBACK_CONFIGURATION = 5
    FUNCTION_GET_VALUES_CALLBACK_CONFIGURATION = 6
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

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    GAS_TYPE_CO = 0
    GAS_TYPE_ETOH = 1
    GAS_TYPE_H2S = 2
    GAS_TYPE_SO2 = 3
    GAS_TYPE_NO2 = 4
    GAS_TYPE_O3 = 5
    GAS_TYPE_IAQ = 6
    GAS_TYPE_RESP = 7
    GAS_TYPE_O3_NO2 = 8
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

        self.response_expected[BrickletGas.FUNCTION_GET_VALUES] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_GET_ADC_COUNT] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_SET_CALIBRATION] = BrickletGas.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGas.FUNCTION_GET_CALIBRATION] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_SET_VALUES_CALLBACK_CONFIGURATION] = BrickletGas.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGas.FUNCTION_GET_VALUES_CALLBACK_CONFIGURATION] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_SET_BOOTLOADER_MODE] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_GET_BOOTLOADER_MODE] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletGas.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGas.FUNCTION_WRITE_FIRMWARE] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletGas.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGas.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_RESET] = BrickletGas.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGas.FUNCTION_WRITE_UID] = BrickletGas.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGas.FUNCTION_READ_UID] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGas.FUNCTION_GET_IDENTITY] = BrickletGas.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletGas.CALLBACK_VALUES] = 'i h H B'


    def get_values(self):
        """
        # MAX 4 SPS
        """
        return GetValues(*self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_VALUES, (), '', 'i h H B'))

    def get_adc_count(self):
        """

        """
        return self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_ADC_COUNT, (), '', 'I')

    def set_calibration(self, adc_count_zero, temperature_zero, humidity_zero, compensation_zero_low, compensation_zero_high, ppm_span, adc_count_span, temperature_span, humidity_span, compensation_span_low, compensation_span_high, temperature_offset, humidity_offset, sensitivity):
        """

        """
        adc_count_zero = int(adc_count_zero)
        temperature_zero = int(temperature_zero)
        humidity_zero = int(humidity_zero)
        compensation_zero_low = int(compensation_zero_low)
        compensation_zero_high = int(compensation_zero_high)
        ppm_span = int(ppm_span)
        adc_count_span = int(adc_count_span)
        temperature_span = int(temperature_span)
        humidity_span = int(humidity_span)
        compensation_span_low = int(compensation_span_low)
        compensation_span_high = int(compensation_span_high)
        temperature_offset = int(temperature_offset)
        humidity_offset = int(humidity_offset)
        sensitivity = int(sensitivity)

        self.ipcon.send_request(self, BrickletGas.FUNCTION_SET_CALIBRATION, (adc_count_zero, temperature_zero, humidity_zero, compensation_zero_low, compensation_zero_high, ppm_span, adc_count_span, temperature_span, humidity_span, compensation_span_low, compensation_span_high, temperature_offset, humidity_offset, sensitivity), 'I h h i i I I h h i i h h i', '')

    def get_calibration(self):
        """

        """
        return GetCalibration(*self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_CALIBRATION, (), '', 'I h h i i I I h h i i h h i'))

    def set_values_callback_configuration(self, period, value_has_to_change):
        """
        The period is the period with which the :cb:`Values`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletGas.FUNCTION_SET_VALUES_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_values_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set Values Callback Configuration`.
        """
        return GetValuesCallbackConfiguration(*self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_VALUES_CALLBACK_CONFIGURATION, (), '', 'I !'))

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletGas.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletGas.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletGas.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletGas.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletGas.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletGas.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletGas.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletGas.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

Gas = BrickletGas # for backward compatibility
