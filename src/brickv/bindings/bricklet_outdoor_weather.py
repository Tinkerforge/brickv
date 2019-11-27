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

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetStationIdentifiersLowLevel = namedtuple('StationIdentifiersLowLevel', ['identifiers_length', 'identifiers_chunk_offset', 'identifiers_chunk_data'])
GetSensorIdentifiersLowLevel = namedtuple('SensorIdentifiersLowLevel', ['identifiers_length', 'identifiers_chunk_offset', 'identifiers_chunk_data'])
GetStationData = namedtuple('StationData', ['temperature', 'humidity', 'wind_speed', 'gust_speed', 'rain', 'wind_direction', 'battery_low', 'last_change'])
GetSensorData = namedtuple('SensorData', ['temperature', 'humidity', 'last_change'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletOutdoorWeather(Device):
    """
    433MHz receiver for outdoor weather station
    """

    DEVICE_IDENTIFIER = 288
    DEVICE_DISPLAY_NAME = 'Outdoor Weather Bricklet'
    DEVICE_URL_PART = 'outdoor_weather' # internal

    CALLBACK_STATION_DATA = 9
    CALLBACK_SENSOR_DATA = 10


    FUNCTION_GET_STATION_IDENTIFIERS_LOW_LEVEL = 1
    FUNCTION_GET_SENSOR_IDENTIFIERS_LOW_LEVEL = 2
    FUNCTION_GET_STATION_DATA = 3
    FUNCTION_GET_SENSOR_DATA = 4
    FUNCTION_SET_STATION_CALLBACK_CONFIGURATION = 5
    FUNCTION_GET_STATION_CALLBACK_CONFIGURATION = 6
    FUNCTION_SET_SENSOR_CALLBACK_CONFIGURATION = 7
    FUNCTION_GET_SENSOR_CALLBACK_CONFIGURATION = 8
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

    WIND_DIRECTION_N = 0
    WIND_DIRECTION_NNE = 1
    WIND_DIRECTION_NE = 2
    WIND_DIRECTION_ENE = 3
    WIND_DIRECTION_E = 4
    WIND_DIRECTION_ESE = 5
    WIND_DIRECTION_SE = 6
    WIND_DIRECTION_SSE = 7
    WIND_DIRECTION_S = 8
    WIND_DIRECTION_SSW = 9
    WIND_DIRECTION_SW = 10
    WIND_DIRECTION_WSW = 11
    WIND_DIRECTION_W = 12
    WIND_DIRECTION_WNW = 13
    WIND_DIRECTION_NW = 14
    WIND_DIRECTION_NNW = 15
    WIND_DIRECTION_ERROR = 255
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

        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_STATION_IDENTIFIERS_LOW_LEVEL] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_SENSOR_IDENTIFIERS_LOW_LEVEL] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_STATION_DATA] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_SENSOR_DATA] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_SET_STATION_CALLBACK_CONFIGURATION] = BrickletOutdoorWeather.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_STATION_CALLBACK_CONFIGURATION] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_SET_SENSOR_CALLBACK_CONFIGURATION] = BrickletOutdoorWeather.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_SENSOR_CALLBACK_CONFIGURATION] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_SET_BOOTLOADER_MODE] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_BOOTLOADER_MODE] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletOutdoorWeather.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_WRITE_FIRMWARE] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletOutdoorWeather.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_RESET] = BrickletOutdoorWeather.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_WRITE_UID] = BrickletOutdoorWeather.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_READ_UID] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOutdoorWeather.FUNCTION_GET_IDENTITY] = BrickletOutdoorWeather.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletOutdoorWeather.CALLBACK_STATION_DATA] = 'B h B I I I B !'
        self.callback_formats[BrickletOutdoorWeather.CALLBACK_SENSOR_DATA] = 'B h B'


    def get_station_identifiers_low_level(self):
        """
        Returns the identifiers (number between 0 and 255) of all `stations
        <https://www.tinkerforge.com/en/shop/accessories/sensors/outdoor-weather-station-ws-6147.html>`__
        that have been seen since the startup of the Bricklet.

        Each station gives itself a random identifier on first startup.

        Since firmware version 2.0.2 a station is removed from the list if no data was received for
        12 hours.
        """
        return GetStationIdentifiersLowLevel(*self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_STATION_IDENTIFIERS_LOW_LEVEL, (), '', 'H H 60B'))

    def get_sensor_identifiers_low_level(self):
        """
        Returns the identifiers (number between 0 and 255) of all `sensors
        <https://www.tinkerforge.com/en/shop/accessories/sensors/temperature-humidity-sensor-th-6148.html>`__
        that have been seen since the startup of the Bricklet.

        Each sensor gives itself a random identifier on first startup.

        Since firmware version 2.0.2 a sensor is removed from the list if no data was received for
        12 hours.
        """
        return GetSensorIdentifiersLowLevel(*self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_SENSOR_IDENTIFIERS_LOW_LEVEL, (), '', 'H H 60B'))

    def get_station_data(self, identifier):
        """
        Returns the last received data for a station with the given identifier.
        Call :func:`Get Station Identifiers` for a list of all available identifiers.

        The return values are:

        * Temperature,
        * Humidity,
        * Wind Speed,
        * Gust Speed,
        * Rain Fall,
        * Wind Direction,
        * Battery Low (true if battery is low) and
        * Last Change (seconds since the reception of this data).
        """
        identifier = int(identifier)

        return GetStationData(*self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_STATION_DATA, (identifier,), 'B', 'h B I I I B ! H'))

    def get_sensor_data(self, identifier):
        """
        Returns the last measured data for a sensor with the given identifier.
        Call :func:`Get Sensor Identifiers` for a list of all available identifiers.

        The return values are:

        * Temperature,
        * Humidity and
        * Last Change (seconds since the last reception of data).
        """
        identifier = int(identifier)

        return GetSensorData(*self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_SENSOR_DATA, (identifier,), 'B', 'h B H'))

    def set_station_callback_configuration(self, enable_callback):
        """
        Turns callback for station data on or off.
        """
        enable_callback = bool(enable_callback)

        self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_SET_STATION_CALLBACK_CONFIGURATION, (enable_callback,), '!', '')

    def get_station_callback_configuration(self):
        """
        Returns the configuration as set by :func:`Set Station Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_STATION_CALLBACK_CONFIGURATION, (), '', '!')

    def set_sensor_callback_configuration(self, enable_callback):
        """
        Turns callback for sensor data on or off.
        """
        enable_callback = bool(enable_callback)

        self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_SET_SENSOR_CALLBACK_CONFIGURATION, (enable_callback,), '!', '')

    def get_sensor_callback_configuration(self):
        """
        Returns the configuration as set by :func:`Set Sensor Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_SENSOR_CALLBACK_CONFIGURATION, (), '', '!')

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletOutdoorWeather.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def get_station_identifiers(self):
        """
        Returns the identifiers (number between 0 and 255) of all `stations
        <https://www.tinkerforge.com/en/shop/accessories/sensors/outdoor-weather-station-ws-6147.html>`__
        that have been seen since the startup of the Bricklet.

        Each station gives itself a random identifier on first startup.

        Since firmware version 2.0.2 a station is removed from the list if no data was received for
        12 hours.
        """
        with self.stream_lock:
            ret = self.get_station_identifiers_low_level()
            identifiers_length = ret.identifiers_length
            identifiers_out_of_sync = ret.identifiers_chunk_offset != 0
            identifiers_data = ret.identifiers_chunk_data

            while not identifiers_out_of_sync and len(identifiers_data) < identifiers_length:
                ret = self.get_station_identifiers_low_level()
                identifiers_length = ret.identifiers_length
                identifiers_out_of_sync = ret.identifiers_chunk_offset != len(identifiers_data)
                identifiers_data += ret.identifiers_chunk_data

            if identifiers_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.identifiers_chunk_offset + 60 < identifiers_length:
                    ret = self.get_station_identifiers_low_level()
                    identifiers_length = ret.identifiers_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Identifiers stream is out-of-sync')

        return identifiers_data[:identifiers_length]

    def get_sensor_identifiers(self):
        """
        Returns the identifiers (number between 0 and 255) of all `sensors
        <https://www.tinkerforge.com/en/shop/accessories/sensors/temperature-humidity-sensor-th-6148.html>`__
        that have been seen since the startup of the Bricklet.

        Each sensor gives itself a random identifier on first startup.

        Since firmware version 2.0.2 a sensor is removed from the list if no data was received for
        12 hours.
        """
        with self.stream_lock:
            ret = self.get_sensor_identifiers_low_level()
            identifiers_length = ret.identifiers_length
            identifiers_out_of_sync = ret.identifiers_chunk_offset != 0
            identifiers_data = ret.identifiers_chunk_data

            while not identifiers_out_of_sync and len(identifiers_data) < identifiers_length:
                ret = self.get_sensor_identifiers_low_level()
                identifiers_length = ret.identifiers_length
                identifiers_out_of_sync = ret.identifiers_chunk_offset != len(identifiers_data)
                identifiers_data += ret.identifiers_chunk_data

            if identifiers_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.identifiers_chunk_offset + 60 < identifiers_length:
                    ret = self.get_sensor_identifiers_low_level()
                    identifiers_length = ret.identifiers_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Identifiers stream is out-of-sync')

        return identifiers_data[:identifiers_length]

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

OutdoorWeather = BrickletOutdoorWeather # for backward compatibility
