# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-08-28.      #
#                                                           #
# Bindings Version 2.0.10                                    #
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

GetSegments = namedtuple('Segments', ['segments', 'brightness', 'colon'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletSegmentDisplay4x7(Device):
    """
    Device for controling four 7-segment displays
    """

    DEVICE_IDENTIFIER = 237


    FUNCTION_SET_SEGMENTS = 1
    FUNCTION_GET_SEGMENTS = 2
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletSegmentDisplay4x7.FUNCTION_SET_SEGMENTS] = BrickletSegmentDisplay4x7.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7.FUNCTION_GET_SEGMENTS] = BrickletSegmentDisplay4x7.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7.FUNCTION_GET_IDENTITY] = BrickletSegmentDisplay4x7.RESPONSE_EXPECTED_ALWAYS_TRUE


    def set_segments(self, segments, brightness, colon):
        """
        The 7-segment display can be set with bitmaps. Every bit controls one
        segment:
        
        .. image:: /Images/Bricklets/bricklet_segment_display_4x7_bit_order.png
           :scale: 100 %
           :alt: Bit order of one segment
           :align: center
        
        For example to set a "5" you would want to activate segments 0, 2, 3, 5 and 6.
        This is represented by the number 0b00110101 = 0x35 = 53.
        
        The brightness can be set between 0 (dark) and 7 (bright). The colon
        parameter turns the colon of the display on or off.
        """
        self.ipcon.send_request(self, BrickletSegmentDisplay4x7.FUNCTION_SET_SEGMENTS, (segments, brightness, colon), '4B B ?', '')

    def get_segments(self):
        """
        Returns the segment, brightness and color data as set by 
        :func:`SetSegments`.
        """
        return GetSegments(*self.ipcon.send_request(self, BrickletSegmentDisplay4x7.FUNCTION_GET_SEGMENTS, (), '', '4B B ?'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletSegmentDisplay4x7.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

SegmentDisplay4x7 = BrickletSegmentDisplay4x7 # for backward compatibility
