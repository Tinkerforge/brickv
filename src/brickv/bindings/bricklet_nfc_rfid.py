# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-05-23.      #
#                                                           #
# Bindings Version 2.1.0                                    #
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

GetTagID = namedtuple('TagID', ['target_type', 'tid_length', 'tid'])
GetState = namedtuple('State', ['state', 'idle'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletNFCRFID(Device):
    """
    Device that can read and write NFC and RFID tags
    """

    DEVICE_IDENTIFIER = 246

    CALLBACK_STATE_CHANGED = 8

    FUNCTION_REQUEST_TAG_ID = 1
    FUNCTION_GET_TAG_ID = 2
    FUNCTION_GET_STATE = 3
    FUNCTION_AUTHENTICATE_MIFARE_CLASSIC_PAGE = 4
    FUNCTION_WRITE_PAGE = 5
    FUNCTION_REQUEST_PAGE = 6
    FUNCTION_GET_PAGE = 7
    FUNCTION_GET_IDENTITY = 255

    TARGET_TYPE_MIFARE_CLASSIC = 0
    TARGET_TYPE_TYPE1 = 1
    TARGET_TYPE_TYPE2 = 2
    STATE_INITIALIZATION = 0
    STATE_IDLE = 128
    STATE_ERROR = 192
    STATE_REQUEST_TAG_ID = 2
    STATE_REQUEST_TAG_ID_READY = 130
    STATE_REQUEST_TAG_ID_ERROR = 194
    STATE_AUTHENTICATING_MIFARE_CLASSIC_PAGE = 3
    STATE_AUTHENTICATING_MIFARE_CLASSIC_PAGE_READY = 131
    STATE_AUTHENTICATING_MIFARE_CLASSIC_PAGE_ERROR = 195
    STATE_WRITE_PAGE = 4
    STATE_WRITE_PAGE_READY = 132
    STATE_WRITE_PAGE_ERROR = 196
    STATE_REQUEST_PAGE = 5
    STATE_REQUEST_PAGE_READY = 133
    STATE_REQUEST_PAGE_ERROR = 197
    KEY_A = 0
    KEY_B = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletNFCRFID.FUNCTION_REQUEST_TAG_ID] = BrickletNFCRFID.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletNFCRFID.FUNCTION_GET_TAG_ID] = BrickletNFCRFID.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletNFCRFID.FUNCTION_GET_STATE] = BrickletNFCRFID.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletNFCRFID.FUNCTION_AUTHENTICATE_MIFARE_CLASSIC_PAGE] = BrickletNFCRFID.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletNFCRFID.FUNCTION_WRITE_PAGE] = BrickletNFCRFID.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletNFCRFID.FUNCTION_REQUEST_PAGE] = BrickletNFCRFID.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletNFCRFID.FUNCTION_GET_PAGE] = BrickletNFCRFID.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletNFCRFID.CALLBACK_STATE_CHANGED] = BrickletNFCRFID.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletNFCRFID.FUNCTION_GET_IDENTITY] = BrickletNFCRFID.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletNFCRFID.CALLBACK_STATE_CHANGED] = 'B ?'

    def request_tag_id(self, target_type):
        """
        
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_REQUEST_TAG_ID, (target_type,), 'B', '')

    def get_tag_id(self):
        """
        
        """
        return GetTagID(*self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_GET_TAG_ID, (), '', 'B H 7B'))

    def get_state(self):
        """
        
        """
        return GetState(*self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_GET_STATE, (), '', 'B ?'))

    def authenticate_mifare_classic_page(self, page, key_number, key):
        """
        
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_AUTHENTICATE_MIFARE_CLASSIC_PAGE, (page, key_number, key), 'H B 6B', '')

    def write_page(self, page, data):
        """
        
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_WRITE_PAGE, (page, data), 'H 16B', '')

    def request_page(self, page):
        """
        
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_REQUEST_PAGE, (page,), 'H', '')

    def get_page(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_GET_PAGE, (), '', '16B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

NFCRFID = BrickletNFCRFID # for backward compatibility
