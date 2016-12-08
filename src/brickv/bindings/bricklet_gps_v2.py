# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-12-07.      #
#                                                           #
# Python Bindings Version 2.1.10                            #
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

GetCoordinates = namedtuple('Coordinates', ['latitude', 'ns', 'longitude', 'ew'])
GetStatus = namedtuple('Status', ['has_fix', 'satellites_view'])
GetAltitude = namedtuple('Altitude', ['altitude', 'geoidal_separation'])
GetMotion = namedtuple('Motion', ['course', 'speed'])
GetDateTime = namedtuple('DateTime', ['date', 'time'])
GetSatelliteSystemStatus = namedtuple('SatelliteSystemStatus', ['satellites', 'fix', 'pdop', 'hdop', 'vdop'])
GetSatelliteStatus = namedtuple('SatelliteStatus', ['elevation', 'azimuth', 'snr'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletGPSV2(Device):
    """
    Determine position, velocity and altitude using GPS
    """

    DEVICE_IDENTIFIER = 276
    DEVICE_DISPLAY_NAME = 'GPS Bricklet 2.0'

    CALLBACK_PULSE_PER_SECOND = 19
    CALLBACK_COORDINATES = 20
    CALLBACK_STATUS = 21
    CALLBACK_ALTITUDE = 22
    CALLBACK_MOTION = 23
    CALLBACK_DATE_TIME = 24

    FUNCTION_GET_COORDINATES = 1
    FUNCTION_GET_STATUS = 2
    FUNCTION_GET_ALTITUDE = 3
    FUNCTION_GET_MOTION = 4
    FUNCTION_GET_DATE_TIME = 5
    FUNCTION_RESTART = 6
    FUNCTION_GET_SATELLITE_SYSTEM_STATUS = 7
    FUNCTION_GET_SATELLITE_STATUS = 8
    FUNCTION_SET_COORDINATES_CALLBACK_PERIOD = 9
    FUNCTION_GET_COORDINATES_CALLBACK_PERIOD = 10
    FUNCTION_SET_STATUS_CALLBACK_PERIOD = 11
    FUNCTION_GET_STATUS_CALLBACK_PERIOD = 12
    FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD = 13
    FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD = 14
    FUNCTION_SET_MOTION_CALLBACK_PERIOD = 15
    FUNCTION_GET_MOTION_CALLBACK_PERIOD = 16
    FUNCTION_SET_DATE_TIME_CALLBACK_PERIOD = 17
    FUNCTION_GET_DATE_TIME_CALLBACK_PERIOD = 18
    FUNCTION_GET_SPITFP_ERROR_COUNT = 234
    FUNCTION_SET_BOOTLOADER_MODE = 235
    FUNCTION_GET_BOOTLOADER_MODE = 236
    FUNCTION_SET_WRITE_FIRMWARE_POINTER = 237
    FUNCTION_WRITE_FIRMWARE = 238
    FUNCTION_SET_STATUS_LED_CONFIG = 239
    FUNCTION_GET_STATUS_LED_CONFIG = 240
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_GET_IDENTITY = 255

    RESTART_TYPE_HOT_START = 0
    RESTART_TYPE_WARM_START = 1
    RESTART_TYPE_COLD_START = 2
    RESTART_TYPE_FACTORY_RESET = 3
    SATELLITE_SYSTEM_GPS = 0
    SATELLITE_SYSTEM_GLONASS = 1
    SATELLITE_SYSTEM_GALILEO = 2
    FIX_NO_FIX = 1
    FIX_2D_FIX = 2
    FIX_3D_FIX = 3
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
    STATUS_LED_CONFIG_SHOW_STATUS = 2
    STATUS_LED_CONFIG_SHOW_HEARTBEAT = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletGPSV2.FUNCTION_GET_COORDINATES] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_STATUS] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_ALTITUDE] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_MOTION] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_DATE_TIME] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_RESTART] = BrickletGPSV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_SATELLITE_SYSTEM_STATUS] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_SATELLITE_STATUS] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_COORDINATES_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_COORDINATES_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_STATUS_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_STATUS_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_MOTION_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_MOTION_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_DATE_TIME_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_DATE_TIME_CALLBACK_PERIOD] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.CALLBACK_PULSE_PER_SECOND] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPSV2.CALLBACK_COORDINATES] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPSV2.CALLBACK_STATUS] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPSV2.CALLBACK_ALTITUDE] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPSV2.CALLBACK_MOTION] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPSV2.CALLBACK_DATE_TIME] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletGPSV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPSV2.FUNCTION_WRITE_FIRMWARE] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletGPSV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPSV2.FUNCTION_RESET] = BrickletGPSV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPSV2.FUNCTION_GET_IDENTITY] = BrickletGPSV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletGPSV2.CALLBACK_PULSE_PER_SECOND] = ''
        self.callback_formats[BrickletGPSV2.CALLBACK_COORDINATES] = 'I c I c'
        self.callback_formats[BrickletGPSV2.CALLBACK_STATUS] = '? B'
        self.callback_formats[BrickletGPSV2.CALLBACK_ALTITUDE] = 'i i'
        self.callback_formats[BrickletGPSV2.CALLBACK_MOTION] = 'I I'
        self.callback_formats[BrickletGPSV2.CALLBACK_DATE_TIME] = 'I I'

    def get_coordinates(self):
        """
        Returns the GPS coordinates. Latitude and longitude are given in the
        ``DD.dddddd°`` format, the value 57123468 means 57.123468°.
        The parameter ``ns`` and ``ew`` are the cardinal directions for
        latitude and longitude. Possible values for ``ns`` and ``ew`` are 'N', 'S', 'E'
        and 'W' (north, south, east and west).
        
        This data is only valid if there is currently a fix as indicated by
        :func:`GetStatus`.
        """
        return GetCoordinates(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_COORDINATES, (), '', 'I c I c'))

    def get_status(self):
        """
        Returns if a fix is currently available as well as the, the number of 
        satellites that are in view.
        
        TODO: LED color?
        There is also a :ref:`blue LED <gps_bricklet_fix_led>` on the Bricklet that
        indicates the fix status.
        """
        return GetStatus(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_STATUS, (), '', '? B'))

    def get_altitude(self):
        """
        Returns the current altitude and corresponding geoidal separation.
        
        Both values are given in cm.
        
        This data is only valid if there is currently a fix as indicated by
        :func:`GetStatus`.
        """
        return GetAltitude(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_ALTITUDE, (), '', 'i i'))

    def get_motion(self):
        """
        Returns the current course and speed. Course is given in hundredths degree
        and speed is given in hundredths km/h. A course of 0° means the Bricklet is
        traveling north bound and 90° means it is traveling east bound.
        
        Please note that this only returns useful values if an actual movement
        is present.
        
        This data is only valid if there is currently a fix as indicated by
        :func:`GetStatus`.
        """
        return GetMotion(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_MOTION, (), '', 'I I'))

    def get_date_time(self):
        """
        Returns the current date and time. The date is
        given in the format ``ddmmyy`` and the time is given
        in the format ``hhmmss.sss``. For example, 140713 means
        14.05.13 as date and 195923568 means 19:59:23.568 as time.
        """
        return GetDateTime(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_DATE_TIME, (), '', 'I I'))

    def restart(self, restart_type):
        """
        Restarts the GPS Bricklet, the following restart types are available:
        
        .. csv-table::
         :header: "Value", "Description"
         :widths: 10, 100
        
         "0", "Hot start (use all available data in the NV store)"
         "1", "Warm start (don't use ephemeris at restart)"
         "2", "Cold start (don't use time, position, almanacs and ephemeris at restart)"
         "3", "Factory reset (clear all system/user configurations at restart)"
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_RESTART, (restart_type,), 'B', '')

    def get_satellite_system_status(self, satellite_system):
        """
        TODO (galileo not supported yet)
        """
        return GetSatelliteSystemStatus(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_SATELLITE_SYSTEM_STATUS, (satellite_system,), 'B', '12b B H H H'))

    def get_satellite_status(self, satellite_system, satellite_number):
        """
        TODO (galileo not supported yet)
        """
        return GetSatelliteStatus(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_SATELLITE_STATUS, (satellite_system, satellite_number), 'B B', 'h h h'))

    def set_coordinates_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Coordinates` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Coordinates` is only triggered if the coordinates changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_COORDINATES_CALLBACK_PERIOD, (period,), 'I', '')

    def get_coordinates_callback_period(self):
        """
        Returns the period as set by :func:`SetCoordinatesCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_COORDINATES_CALLBACK_PERIOD, (), '', 'I')

    def set_status_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Status` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Status` is only triggered if the status changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_STATUS_CALLBACK_PERIOD, (period,), 'I', '')

    def get_status_callback_period(self):
        """
        Returns the period as set by :func:`SetStatusCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_STATUS_CALLBACK_PERIOD, (), '', 'I')

    def set_altitude_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Altitude` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Altitude` is only triggered if the altitude changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_altitude_callback_period(self):
        """
        Returns the period as set by :func:`SetAltitudeCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD, (), '', 'I')

    def set_motion_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Motion` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Motion` is only triggered if the motion changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_MOTION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_motion_callback_period(self):
        """
        Returns the period as set by :func:`SetMotionCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_MOTION_CALLBACK_PERIOD, (), '', 'I')

    def set_date_time_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`DateTime` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`DateTime` is only triggered if the date or time changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_DATE_TIME_CALLBACK_PERIOD, (period,), 'I', '')

    def get_date_time_callback_period(self):
        """
        Returns the period as set by :func:`SetDateTimeCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_DATE_TIME_CALLBACK_PERIOD, (), '', 'I')

    def get_spitfp_error_count(self):
        """
        TODO
        """
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once 
        for every 10 received data packets.
        
        You can also turn the LED permanently on/off or show a heartbeat.
        
        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`SetStatusLEDConfig`
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!
        
        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.
        
        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_RESET, (), '', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletGPSV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

GPSV2 = BrickletGPSV2 # for backward compatibility
