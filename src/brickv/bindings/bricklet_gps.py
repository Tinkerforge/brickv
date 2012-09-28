# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-09-27.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from .ip_connection import namedtuple
from .ip_connection import Device, IPConnection, Error

GetCoordinates = namedtuple('Coordinates', ['ns', 'latitude', 'ew', 'longitude', 'pdop', 'hdop', 'vdop'])
GetStatus = namedtuple('Status', ['fix', 'satellites_view', 'satellites_used', 'speed', 'course', 'date', 'time', 'altitude', 'altitude_accuracy'])

class GPS(Device):
    """
    Device for receiving GPS position
    """

    CALLBACK_COORDINATES = 8
    CALLBACK_STATUS = 9

    FUNCTION_GET_COORDINATES = 1
    FUNCTION_GET_STATUS = 2
    FUNCTION_RESTART = 3
    FUNCTION_SET_COORDINATES_CALLBACK_PERIOD = 4
    FUNCTION_GET_COORDINATES_CALLBACK_PERIOD = 5
    FUNCTION_SET_STATUS_CALLBACK_PERIOD = 6
    FUNCTION_GET_STATUS_CALLBACK_PERIOD = 7

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'GPS Bricklet'

        self.binding_version = [1, 0, 0]

        self.callback_formats[GPS.CALLBACK_COORDINATES] = 'c 2H c 2H H H H'
        self.callback_formats[GPS.CALLBACK_STATUS] = 'B B B H H I I h h'

    def get_coordinates(self):
        """
        
        """
        return GetCoordinates(*self.ipcon.send_request(self, GPS.FUNCTION_GET_COORDINATES, (), '', 'c 2H c 2H H H H'))

    def get_status(self):
        """
        
        """
        return GetStatus(*self.ipcon.send_request(self, GPS.FUNCTION_GET_STATUS, (), '', 'B B B H H I I h h'))

    def restart(self, restart_type):
        """
        
        """
        self.ipcon.send_request(self, GPS.FUNCTION_RESTART, (restart_type,), 'B', '')

    def set_coordinates_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, GPS.FUNCTION_SET_COORDINATES_CALLBACK_PERIOD, (period,), 'I', '')

    def get_coordinates_callback_period(self):
        """
        Returns the period as set by :func:`SetCoordinatesCallbackPeriod`.
        """
        return self.ipcon.send_request(self, GPS.FUNCTION_GET_COORDINATES_CALLBACK_PERIOD, (), '', 'I')

    def set_status_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, GPS.FUNCTION_SET_STATUS_CALLBACK_PERIOD, (period,), 'I', '')

    def get_status_callback_period(self):
        """
        Returns the period as set by :func:`GetStatusCallbackPeriod`.
        """
        return self.ipcon.send_request(self, GPS.FUNCTION_GET_STATUS_CALLBACK_PERIOD, (), '', 'I')

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
