# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-07-28.      #
#                                                           #
# Bindings Version 2.1.5                                    #
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

GetTagID = namedtuple('TagID', ['tag_type', 'tid_length', 'tid'])
GetState = namedtuple('State', ['state', 'idle'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletNFCRFID(Device):
    """
    Reads and writes NFC and RFID tags
    """

    DEVICE_IDENTIFIER = 246
    DEVICE_DISPLAY_NAME = 'NFC/RFID Bricklet'

    CALLBACK_STATE_CHANGED = 8

    FUNCTION_REQUEST_TAG_ID = 1
    FUNCTION_GET_TAG_ID = 2
    FUNCTION_GET_STATE = 3
    FUNCTION_AUTHENTICATE_MIFARE_CLASSIC_PAGE = 4
    FUNCTION_WRITE_PAGE = 5
    FUNCTION_REQUEST_PAGE = 6
    FUNCTION_GET_PAGE = 7
    FUNCTION_GET_IDENTITY = 255

    TAG_TYPE_MIFARE_CLASSIC = 0
    TAG_TYPE_TYPE1 = 1
    TAG_TYPE_TYPE2 = 2
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

    def request_tag_id(self, tag_type):
        """
        To read or write a tag that is in proximity of the NFC/RFID Bricklet you 
        first have to call this function with the expected tag type as parameter.
        It is no problem if you don't know the tag type. You can cycle through 
        the available tag types until the tag gives an answer to the request.
        
        Current the following tag types are supported:
        
        * Mifare Classic (``tag_type`` = 0)
        * NFC Forum Type 1 (``tag_type`` = 1)
        * NFC Forum Type 2 (``tag_type`` = 2)
        
        After you call :func:`RequestTagID` the NFC/RFID Bricklet will try to read 
        the tag ID from the tag. After this process is done the state will change.
        You can either register the :func:`StateChanged` callback or you can poll
        :func:`GetState` to find out about the state change.
        
        If the state changes to *RequestTagIDError* it means that either there was 
        no tag present or that the tag is of an incompatible type. If the state 
        changes to *RequestTagIDReady* it means that a compatible tag was found 
        and that the tag ID could be read out. You can now get the tag ID by
        calling :func:`GetTagID`.
        
        If two tags are in the proximity of the NFC/RFID Bricklet, this
        function will cycle through the tags. To select a specific tag you have
        to call :func:`RequestTagID` until the correct tag id is found.
        
        In case of any *Error* state the selection is lost and you have to
        start again by calling :func:`RequestTagID`.
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_REQUEST_TAG_ID, (tag_type,), 'B', '')

    def get_tag_id(self):
        """
        Returns the tag type, tag ID and the length of the tag ID 
        (4 or 7 bytes are possible length). This function can only be called if the
        NFC/RFID is currently in one of the *Ready* states. The returned ID
        is the ID that was saved through the last call of :func:`RequestTagID`.
        
        To get the tag ID of a tag the approach is as follows:
        
        1. Call :func:`RequestTagID`
        2. Wait for state to change to *RequestTagIDReady* (see :func:`GetState` or
           :func:`StateChanged`)
        3. Call :func:`GetTagID`
        """
        return GetTagID(*self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_GET_TAG_ID, (), '', 'B B 7B'))

    def get_state(self):
        """
        Returns the current state of the NFC/RFID Bricklet.
        
        On startup the Bricklet will be in the *Initialization* state. The
        initialization will only take about 20ms. After that it changes to *Idle*.
        
        The functions of this Bricklet can be called in the *Idle* state and all of
        the *Ready* and *Error* states.
        
        Example: If you call :func:`RequestPage`, the state will change to 
        *RequestPage* until the reading of the page is finished. Then it will change
        to either *RequestPageReady* if it worked or to *RequestPageError* if it
        didn't. If the request worked you can get the page by calling :func:`GetPage`.
        
        The same approach is used analogously for the other API functions.
        
        Possible states are:
        
        * Initialization = 0
        * Idle = 128
        * Error = 192
        * RequestTagID = 2
        * RequestTagIDReady = 130
        * RequestTagIDError = 194
        * AuthenticatingMifareClassicPage = 3
        * AuthenticatingMifareClassicPageReady = 131
        * AuthenticatingMifareClassicPageError = 195
        * WritePage = 4
        * WritePageReady = 132
        * WritePageError = 196
        * RequestPage = 5
        * RequestPageReady = 133
        * RequestPageError = 197
        """
        return GetState(*self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_GET_STATE, (), '', 'B ?'))

    def authenticate_mifare_classic_page(self, page, key_number, key):
        """
        Mifare Classic tags use authentication. If you want to read from or write to
        a Mifare Classic page you have to authenticate it beforehand.
        Each page can be authenticated with two keys: A (``key_number`` = 0) and B
        (``key_number`` = 1). A new Mifare Classic
        tag that has not yet been written to can can be accessed with key A
        and the default key ``[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]``.
        
        The approach to read or write a Mifare Classic page is as follows:
        
        1. Call :func:`RequestTagID`
        2. Wait for state to change to *RequestTagIDReady* (see :func:`GetState`
           or :func:`StateChanged`)
        3. If looking for a specific tag then call :func:`GetTagID` and check if the
           expected tag was found, if it was not found got back to step 1
        4. Call :func:`AuthenticateMifareClassicPage` with page and key for the page
        5. Wait for state to change to *AuthenticatingMifareClassicPageReady* (see
           :func:`GetState` or :func:`StateChanged`)
        6. Call :func:`RequestPage` or :func:`WritePage` to read/write page
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_AUTHENTICATE_MIFARE_CLASSIC_PAGE, (page, key_number, key), 'H B 6B', '')

    def write_page(self, page, data):
        """
        Writes 16 bytes starting from the given page. How many pages are written
        depends on the tag type. The page sizes are as follows:
        
        * Mifare Classic page size: 16 byte (one page is written)
        * NFC Forum Type 1 page size: 8 byte (two pages are written)
        * NFC Forum Type 2 page size: 4 byte (four pages are written)
        
        The general approach for writing to a tag is as follows:
        
        1. Call :func:`RequestTagID`
        2. Wait for state to change to *RequestTagIDReady* (see :func:`GetState` or
           :func:`StateChanged`)
        3. If looking for a specific tag then call :func:`GetTagID` and check if the
           expected tag was found, if it was not found got back to step 1
        4. Call :func:`WritePage` with page number and data
        5. Wait for state to change to *WritePageReady* (see :func:`GetState` or
           :func:`StateChanged`)
        
        If you use a Mifare Classic tag you have to authenticate a page before you
        can write to it. See :func:`AuthenticateMifareClassicPage`.
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_WRITE_PAGE, (page, data), 'H 16B', '')

    def request_page(self, page):
        """
        Reads 16 bytes starting from the given page and stores them into a buffer. 
        The buffer can then be read out with :func:`GetPage`.
        How many pages are read depends on the tag type. The page sizes are 
        as follows:
        
        * Mifare Classic page size: 16 byte (one page is read)
        * NFC Forum Type 1 page size: 8 byte (two pages are read)
        * NFC Forum Type 2 page size: 4 byte (four pages are read)
        
        The general approach for reading a tag is as follows:
        
        1. Call :func:`RequestTagID`
        2. Wait for state to change to *RequestTagIDReady* (see :func:`GetState`
           or :func:`StateChanged`)
        3. If looking for a specific tag then call :func:`GetTagID` and check if the
           expected tag was found, if it was not found got back to step 1
        4. Call :func:`RequestPage` with page number
        5. Wait for state to change to *RequestPageReady* (see :func:`GetState`
           or :func:`StateChanged`)
        6. Call :func:`GetPage` to retrieve the page from the buffer
        
        If you use a Mifare Classic tag you have to authenticate a page before you
        can read it. See :func:`AuthenticateMifareClassicPage`.
        """
        self.ipcon.send_request(self, BrickletNFCRFID.FUNCTION_REQUEST_PAGE, (page,), 'H', '')

    def get_page(self):
        """
        Returns 16 bytes of data from an internal buffer. To fill the buffer
        with specific pages you have to call :func:`RequestPage` beforehand.
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
