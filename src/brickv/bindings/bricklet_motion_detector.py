# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-09-11.      #
#                                                           #
# Bindings Version 2.0.11                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
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

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletMotionDetector(Device):
    """
    Device that reads out PIR motion detector
    """

    DEVICE_IDENTIFIER = 233

    CALLBACK_MOTION_DETECTED = 2
    CALLBACK_DETECTION_CYCLE_ENDED = 3

    FUNCTION_GET_MOTION_DETECTED = 1
    FUNCTION_GET_IDENTITY = 255

    MOTION_DETECTED = 0
    MOTION_NOT_DETECTED = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletMotionDetector.FUNCTION_GET_MOTION_DETECTED] = BrickletMotionDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotionDetector.CALLBACK_MOTION_DETECTED] = BrickletMotionDetector.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMotionDetector.CALLBACK_DETECTION_CYCLE_ENDED] = BrickletMotionDetector.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMotionDetector.FUNCTION_GET_IDENTITY] = BrickletMotionDetector.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletMotionDetector.CALLBACK_MOTION_DETECTED] = ''
        self.callback_formats[BrickletMotionDetector.CALLBACK_DETECTION_CYCLE_ENDED] = ''

    def get_motion_detected(self):
        """
        Returns 0 if a motion was detected. How long this returns 0 after a motion
        was detected can be adjusted with one of the small potentiometers on the
        Motion Detector Bricklet, see here. TODO: ADD LINK
        """
        return self.ipcon.send_request(self, BrickletMotionDetector.FUNCTION_GET_MOTION_DETECTED, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletMotionDetector.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

MotionDetector = BrickletMotionDetector # for backward compatibility
