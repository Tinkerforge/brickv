# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-09-08.      #
#                                                           #
# Python Bindings Version 2.1.10                            #
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

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletMotionDetector(Device):
    """
    Passive infrared (PIR) motion sensor, 7m range
    """

    DEVICE_IDENTIFIER = 233
    DEVICE_DISPLAY_NAME = 'Motion Detector Bricklet'

    CALLBACK_MOTION_DETECTED = 2
    CALLBACK_DETECTION_CYCLE_ENDED = 3

    FUNCTION_GET_MOTION_DETECTED = 1
    FUNCTION_GET_IDENTITY = 255

    MOTION_NOT_DETECTED = 0
    MOTION_DETECTED = 1

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
        Returns 1 if a motion was detected. How long this returns 1 after a motion
        was detected can be adjusted with one of the small potentiometers on the
        Motion Detector Bricklet, see :ref:`here
        <motion_detector_bricklet_sensitivity_delay_block_time>`.
        
        There is also a blue LED on the Bricklet that is on as long as the Bricklet is
        in the "motion detected" state.
        """
        return self.ipcon.send_request(self, BrickletMotionDetector.FUNCTION_GET_MOTION_DETECTED, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletMotionDetector.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

MotionDetector = BrickletMotionDetector # for backward compatibility
