# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2017-03-27.      #
#                                                           #
# Python Bindings Version 2.1.11                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetImageLowLevel = namedtuple('ImageLowLevel', ['stream_chunk_offset', 'stream_chunk_data'])
GetRawImageLowLevel = namedtuple('RawImageLowLevel', ['stream_chunk_offset', 'stream_chunk_data'])
GetStatistics = namedtuple('Statistics', ['video_scene_statistics', 'spotmeter_statistics', 'temperatures', 'status'])
GetAutomaticGainControlConfig = namedtuple('AutomaticGainControlConfig', ['region_of_interest', 'dampening_factor', 'clip_limit', 'empty_counts'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletThermalImaging(Device):
    """
    60x80 pixel thermal imaging camera
    """

    DEVICE_IDENTIFIER = 278
    DEVICE_DISPLAY_NAME = 'Thermal Imaging Bricklet'

    CALLBACK_IMAGE_LOW_LEVEL = 12
    CALLBACK_RAW_IMAGE_LOW_LEVEL = 13

    CALLBACK_IMAGE = -12
    CALLBACK_RAW_IMAGE = -13

    FUNCTION_GET_IMAGE_LOW_LEVEL = 1
    FUNCTION_GET_RAW_IMAGE_LOW_LEVEL = 2
    FUNCTION_GET_STATISTICS = 3
    FUNCTION_SET_RESOLUTION = 4
    FUNCTION_GET_RESOLUTION = 5
    FUNCTION_SET_SPOTMETER_CONFIG = 6
    FUNCTION_GET_SPOTMETER_CONFIG = 7
    FUNCTION_SET_AUTOMATIC_GAIN_CONTROL_CONFIG = 8
    FUNCTION_GET_AUTOMATIC_GAIN_CONTROL_CONFIG = 9
    FUNCTION_SET_CALLBACK_CONFIG = 10
    FUNCTION_GET_CALLBACK_CONFIG = 11
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

    RESOLUTION_0_TO_6553_KELVIN = 0
    RESOLUTION_0_TO_655_KELVIN = 1
    CALLBACK_CONFIG_CALLBACK_OFF = 0
    CALLBACK_CONFIG_CALLBACK_IMAGE = 1
    CALLBACK_CONFIG_CALLBACK_RAW_IMAGE = 2
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

        self.response_expected[BrickletThermalImaging.FUNCTION_GET_IMAGE_LOW_LEVEL] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_RAW_IMAGE_LOW_LEVEL] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_STATISTICS] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_RESOLUTION] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_RESOLUTION] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_SPOTMETER_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_SPOTMETER_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_AUTOMATIC_GAIN_CONTROL_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_AUTOMATIC_GAIN_CONTROL_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_CALLBACK_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_CALLBACK_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.CALLBACK_IMAGE_LOW_LEVEL] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletThermalImaging.CALLBACK_RAW_IMAGE_LOW_LEVEL] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_BOOTLOADER_MODE] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_BOOTLOADER_MODE] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_WRITE_FIRMWARE] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_RESET] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_WRITE_UID] = BrickletThermalImaging.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletThermalImaging.FUNCTION_READ_UID] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletThermalImaging.FUNCTION_GET_IDENTITY] = BrickletThermalImaging.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletThermalImaging.CALLBACK_IMAGE_LOW_LEVEL] = 'H 62B'
        self.callback_formats[BrickletThermalImaging.CALLBACK_RAW_IMAGE_LOW_LEVEL] = 'H 31H'

        self.low_level_callbacks[BrickletThermalImaging.CALLBACK_IMAGE_LOW_LEVEL] = [BrickletThermalImaging.CALLBACK_IMAGE, {'stream': {'fixed_total_length': 4800}}, None]
        self.low_level_callbacks[BrickletThermalImaging.CALLBACK_RAW_IMAGE_LOW_LEVEL] = [BrickletThermalImaging.CALLBACK_RAW_IMAGE, {'stream': {'fixed_total_length': 4800}}, None]

    def get_image_low_level(self):
        """

        """
        return GetImageLowLevel(*self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_IMAGE_LOW_LEVEL, (), '', 'H 62B'))

    def get_raw_image_low_level(self):
        """

        """
        return GetRawImageLowLevel(*self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_RAW_IMAGE_LOW_LEVEL, (), '', 'H 31H'))

    def get_statistics(self):
        """

        """
        return GetStatistics(*self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_STATISTICS, (), '', '4H 4H 8H H'))

    def set_resolution(self, resolution):
        """

        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_RESOLUTION, (resolution,), 'B', '')

    def get_resolution(self):
        """

        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_RESOLUTION, (), '', 'B')

    def set_spotmeter_config(self, region_of_interest):
        """

        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_SPOTMETER_CONFIG, (region_of_interest,), '4B', '')

    def get_spotmeter_config(self):
        """

        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_SPOTMETER_CONFIG, (), '', '4B')

    def set_automatic_gain_control_config(self, region_of_interest, dampening_factor, clip_limit, empty_counts):
        """

        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_AUTOMATIC_GAIN_CONTROL_CONFIG, (region_of_interest, dampening_factor, clip_limit, empty_counts), '4B H 2H H', '')

    def get_automatic_gain_control_config(self):
        """

        """
        return GetAutomaticGainControlConfig(*self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_AUTOMATIC_GAIN_CONTROL_CONFIG, (), '', '4B H 2H H'))

    def set_callback_config(self, callback_config):
        """

        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_CALLBACK_CONFIG, (callback_config,), 'B', '')

    def get_callback_config(self):
        """

        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_CALLBACK_CONFIG, (), '', 'B')

    def get_spitfp_error_count(self):
        """
        Returns the error count for the communication between Brick and Bricklet.

        The errors are divided into

        * ack checksum errors,
        * message checksum errors,
        * frameing errors and
        * overflow errors.

        The errors counts are for errors that occur on the Bricklet side. All
        Bricks have a similar function that returns the errors on the Brick side.
        """
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        Sets the bootloader mode and returns the status after the requested
        mode change was instigated.

        You can change from bootloader mode to firmware mode and vice versa. A change
        from bootloader mode to firmware mode will only take place if the entry function,
        device identifier und crc are present and correct.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for func:`WriteFirmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletThermalImaging.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def get_image(self):
        stream_extra = (,)
        stream_total_length = 4800
        stream_chunk_offset = 0
        stream_result = None
        stream_data = (,)
        stream_out_of_sync = False

        STREAM_CHUNK_OFFSET_NO_DATA = (1 << 16) - 1 # FIXME: make this depend on the stream_chunk_offset type

        with self.stream_lock:
            if stream_total_length == None: # no fixed-stream-length
                stream_result = self.get_image_low_level()
                stream_extra = stream_result[:-2] # FIXME: validate that extra parameters are identical for all low-level getters of a stream
                stream_total_length = stream_result.stream_total_length
                stream_chunk_offset = stream_result.stream_chunk_offset
                stream_data = stream_result.stream_chunk_data

            if stream_chunk_offset == STREAM_CHUNK_OFFSET_NO_DATA:
                raise Error(Error.STREAM_NO_DATA, 'Stream has no data')
            elif stream_chunk_offset != 0: # stream out-of-sync
                # discard remaining stream to bring it back in-sync
                while stream_chunk_offset + 62 < stream_total_length:
                    # FIXME: validate that total length is identical for all low-level getters of a stream
                    stream_chunk_offset = self.get_image_low_level().stream_chunk_offset

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Stream is out-of-sync')

            # FIXME: validate chunk offset < total length

            while len(stream_data) < stream_total_length:
                stream_result = self.get_image_low_level()
                stream_extra = stream_result[:-2] # FIXME: validate that extra parameters are identical for all low-level getters of a stream
                stream_chunk_offset = stream_result.stream_chunk_offset

                # FIXME: validate that total length is identical for all low-level getters of a stream

                if stream_chunk_offset != len(stream_data): # stream out-of-sync
                    # discard remaining stream to bring it back in-sync
                    while stream_chunk_offset + 62 < stream_total_length:
                        # FIXME: validate that total length is identical for all low-level getters of a stream
                        stream_chunk_offset = self.get_image_low_level().stream_chunk_offset

                    raise Error(Error.STREAM_OUT_OF_SYNC, 'Stream is out-of-sync')

        if len(stream_extra) > 0:
            return stream_extra + (stream_data[:stream_total_length],)
        else:
            return stream_data[:stream_total_length]

    def get_raw_image(self):
        stream_extra = (,)
        stream_total_length = 4800
        stream_chunk_offset = 0
        stream_result = None
        stream_data = (,)
        stream_out_of_sync = False

        STREAM_CHUNK_OFFSET_NO_DATA = (1 << 16) - 1 # FIXME: make this depend on the stream_chunk_offset type

        with self.stream_lock:
            if stream_total_length == None: # no fixed-stream-length
                stream_result = self.get_raw_image_low_level()
                stream_extra = stream_result[:-2] # FIXME: validate that extra parameters are identical for all low-level getters of a stream
                stream_total_length = stream_result.stream_total_length
                stream_chunk_offset = stream_result.stream_chunk_offset
                stream_data = stream_result.stream_chunk_data

            if stream_chunk_offset == STREAM_CHUNK_OFFSET_NO_DATA:
                raise Error(Error.STREAM_NO_DATA, 'Stream has no data')
            elif stream_chunk_offset != 0: # stream out-of-sync
                # discard remaining stream to bring it back in-sync
                while stream_chunk_offset + 31 < stream_total_length:
                    # FIXME: validate that total length is identical for all low-level getters of a stream
                    stream_chunk_offset = self.get_raw_image_low_level().stream_chunk_offset

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Stream is out-of-sync')

            # FIXME: validate chunk offset < total length

            while len(stream_data) < stream_total_length:
                stream_result = self.get_raw_image_low_level()
                stream_extra = stream_result[:-2] # FIXME: validate that extra parameters are identical for all low-level getters of a stream
                stream_chunk_offset = stream_result.stream_chunk_offset

                # FIXME: validate that total length is identical for all low-level getters of a stream

                if stream_chunk_offset != len(stream_data): # stream out-of-sync
                    # discard remaining stream to bring it back in-sync
                    while stream_chunk_offset + 31 < stream_total_length:
                        # FIXME: validate that total length is identical for all low-level getters of a stream
                        stream_chunk_offset = self.get_raw_image_low_level().stream_chunk_offset

                    raise Error(Error.STREAM_OUT_OF_SYNC, 'Stream is out-of-sync')

        if len(stream_extra) > 0:
            return stream_extra + (stream_data[:stream_total_length],)
        else:
            return stream_data[:stream_total_length]

    def register_callback(self, id_, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        if callback is None:
            self.registered_callbacks.pop(id_, None)
        else:
            self.registered_callbacks[id_] = callback

ThermalImaging = BrickletThermalImaging # for backward compatibility
