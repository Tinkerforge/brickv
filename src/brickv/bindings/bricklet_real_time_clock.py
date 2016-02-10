# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-10.      #
#                                                           #
# Python Bindings Version 2.1.8                             #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

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

GetDateTime = namedtuple('DateTime', ['year', 'month', 'day', 'hour', 'minute', 'second', 'centisecond', 'weekday'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRealTimeClock(Device):
    """
    Battery-backed real-time clock
    """

    DEVICE_IDENTIFIER = 268
    DEVICE_DISPLAY_NAME = 'Real-Time Clock Bricklet'


    FUNCTION_SET_DATE_TIME = 1
    FUNCTION_GET_DATE_TIME = 2
    FUNCTION_GET_TIMESTAMP = 3
    FUNCTION_SET_OFFSET = 4
    FUNCTION_GET_OFFSET = 5
    FUNCTION_GET_IDENTITY = 255

    WEEKDAY_MONDAY = 1
    WEEKDAY_TUESDAY = 2
    WEEKDAY_WEDNESDAY = 3
    WEEKDAY_THURSDAY = 4
    WEEKDAY_FRIDAY = 5
    WEEKDAY_SATURDAY = 6
    WEEKDAY_SUNDAY = 7

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRealTimeClock.FUNCTION_SET_DATE_TIME] = BrickletRealTimeClock.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRealTimeClock.FUNCTION_GET_DATE_TIME] = BrickletRealTimeClock.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRealTimeClock.FUNCTION_GET_TIMESTAMP] = BrickletRealTimeClock.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRealTimeClock.FUNCTION_SET_OFFSET] = BrickletRealTimeClock.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRealTimeClock.FUNCTION_GET_OFFSET] = BrickletRealTimeClock.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRealTimeClock.FUNCTION_GET_IDENTITY] = BrickletRealTimeClock.RESPONSE_EXPECTED_ALWAYS_TRUE


    def set_date_time(self, year, month, day, hour, minute, second, centisecond, weekday):
        """
        Sets the current date (including weekday) and the current time with hundredths
        of a second resolution.
        
        Possible value ranges:
        
        * Year: 2000 to 2099
        * Month: 1 to 12 (January to December)
        * Day: 1 to 31
        * Hour: 0 to 23
        * Minute: 0 to 59
        * Second: 0 to 59
        * Centisecond: 0 to 99
        * Weekday: 1 to 7 (Monday to Sunday)
        
        If the backup battery is installed then the real-time clock keeps date and
        time even if the Bricklet is not powered by a Brick.
        
        The real-time clock handles leap year and inserts the 29th of February
        accordingly. But leap seconds, time zones and daylight saving time are not
        handled.
        """
        self.ipcon.send_request(self, BrickletRealTimeClock.FUNCTION_SET_DATE_TIME, (year, month, day, hour, minute, second, centisecond, weekday), 'H B B B B B B B', '')

    def get_date_time(self):
        """
        Returns the current date (including weekday) and the current time of the
        real-time clock with hundredths of a second resolution.
        """
        return GetDateTime(*self.ipcon.send_request(self, BrickletRealTimeClock.FUNCTION_GET_DATE_TIME, (), '', 'H B B B B B B B'))

    def get_timestamp(self):
        """
        Returns the current date and the time of the real-time clock converted to
        milliseconds. The timestamp has an effective resolution of hundredths of a
        second.
        """
        return self.ipcon.send_request(self, BrickletRealTimeClock.FUNCTION_GET_TIMESTAMP, (), '', 'q')

    def set_offset(self, offset):
        """
        Sets the offset the real-time clock should compensate for in 2.17 ppm steps
        between -277.76 ppm (-128) and +275.59 ppm (127).
        
        The real-time clock time can deviate from the actual time due to the frequency
        deviation of its 32.768 kHz crystal. Even without compensation (factory
        default) the resulting time deviation should be at most ±20 ppm (±52.6
        seconds per month).
        
        This deviation can be calculated by comparing the same duration measured by the
        real-time clock (``rtc_duration``) an accurate reference clock
        (``ref_duration``).
        
        For best results the configured offset should be set to 0 ppm first and then a
        duration of at least 6 hours should be measured.
        
        The new offset (``new_offset``) can be calculated from the currently configured
        offset (``current_offset``) and the measured durations as follow::
        
          new_offset = current_offset - round(1000000 * (rtc_duration - ref_duration) / rtc_duration / 2.17)
        
        If you want to calculate the offset, then we recommend using the calibration
        dialog in Brick Viewer, instead of doing it manually.
        
        The offset is saved in the EEPROM of the Bricklet and only needs to be
        configured once.
        """
        self.ipcon.send_request(self, BrickletRealTimeClock.FUNCTION_SET_OFFSET, (offset,), 'b', '')

    def get_offset(self):
        """
        Returns the offset as set by :func:`SetOffset`.
        """
        return self.ipcon.send_request(self, BrickletRealTimeClock.FUNCTION_GET_OFFSET, (), '', 'b')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRealTimeClock.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

RealTimeClock = BrickletRealTimeClock # for backward compatibility
