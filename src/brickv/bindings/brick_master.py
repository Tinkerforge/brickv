# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-12-20.      #
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

GetChibiErrorLog = namedtuple('ChibiErrorLog', ['underrun', 'crc_error', 'no_ack', 'overflow'])
GetRS485Configuration = namedtuple('RS485Configuration', ['speed', 'parity', 'stopbits'])
GetWifiConfiguration = namedtuple('WifiConfiguration', ['ssid', 'connection', 'ip', 'subnet_mask', 'gateway', 'port'])
GetWifiEncryption = namedtuple('WifiEncryption', ['encryption', 'key', 'key_index', 'eap_options', 'ca_certificate_length', 'client_certificate_length', 'private_key_length'])
GetWifiStatus = namedtuple('WifiStatus', ['mac_address', 'bssid', 'channel', 'rssi', 'ip', 'subnet_mask', 'gateway', 'rx_count', 'tx_count', 'state'])
GetWifiCertificate = namedtuple('WifiCertificate', ['data', 'data_length'])
GetWifiBufferInfo = namedtuple('WifiBufferInfo', ['overflow', 'low_watermark', 'used'])

class Master(Device):
    """
    Device for controlling Stacks and four Bricklets
    """


    FUNCTION_GET_STACK_VOLTAGE = 1
    FUNCTION_GET_STACK_CURRENT = 2
    FUNCTION_SET_EXTENSION_TYPE = 3
    FUNCTION_GET_EXTENSION_TYPE = 4
    FUNCTION_IS_CHIBI_PRESENT = 5
    FUNCTION_SET_CHIBI_ADDRESS = 6
    FUNCTION_GET_CHIBI_ADDRESS = 7
    FUNCTION_SET_CHIBI_MASTER_ADDRESS = 8
    FUNCTION_GET_CHIBI_MASTER_ADDRESS = 9
    FUNCTION_SET_CHIBI_SLAVE_ADDRESS = 10
    FUNCTION_GET_CHIBI_SLAVE_ADDRESS = 11
    FUNCTION_GET_CHIBI_SIGNAL_STRENGTH = 12
    FUNCTION_GET_CHIBI_ERROR_LOG = 13
    FUNCTION_SET_CHIBI_FREQUENCY = 14
    FUNCTION_GET_CHIBI_FREQUENCY = 15
    FUNCTION_SET_CHIBI_CHANNEL = 16
    FUNCTION_GET_CHIBI_CHANNEL = 17
    FUNCTION_IS_RS485_PRESENT = 18
    FUNCTION_SET_RS485_ADDRESS = 19
    FUNCTION_GET_RS485_ADDRESS = 20
    FUNCTION_SET_RS485_SLAVE_ADDRESS = 21
    FUNCTION_GET_RS485_SLAVE_ADDRESS = 22
    FUNCTION_GET_RS485_ERROR_LOG = 23
    FUNCTION_SET_RS485_CONFIGURATION = 24
    FUNCTION_GET_RS485_CONFIGURATION = 25
    FUNCTION_IS_WIFI_PRESENT = 26
    FUNCTION_SET_WIFI_CONFIGURATION = 27
    FUNCTION_GET_WIFI_CONFIGURATION = 28
    FUNCTION_SET_WIFI_ENCRYPTION = 29
    FUNCTION_GET_WIFI_ENCRYPTION = 30
    FUNCTION_GET_WIFI_STATUS = 31
    FUNCTION_REFRESH_WIFI_STATUS = 32
    FUNCTION_SET_WIFI_CERTIFICATE = 33
    FUNCTION_GET_WIFI_CERTIFICATE = 34
    FUNCTION_SET_WIFI_POWER_MODE = 35
    FUNCTION_GET_WIFI_POWER_MODE = 36
    FUNCTION_GET_WIFI_BUFFER_INFO = 37
    FUNCTION_SET_WIFI_REGULATORY_DOMAIN = 38
    FUNCTION_GET_WIFI_REGULATORY_DOMAIN = 39
    FUNCTION_GET_USB_VOLTAGE = 40
    FUNCTION_RESET = 243
    FUNCTION_GET_CHIP_TEMPERATURE = 242

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Master Brick'

        self.binding_version = [1, 3, 2]


    def get_stack_voltage(self):
        """
        Returns the stack voltage in mV. The stack voltage is the
        voltage that is supplied via the stack, i.e. it is given by a 
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_STACK_VOLTAGE, (), '', 'H')

    def get_stack_current(self):
        """
        Returns the stack current in mA. The stack current is the
        current that is drawn via the stack, i.e. it is given by a
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_STACK_CURRENT, (), '', 'H')

    def set_extension_type(self, extension, exttype):
        """
        Writes the extension type to the EEPROM of a specified extension. 
        The extension is either 0 or 1 (0 is the on the bottom, 1 is the on on top, 
        if only one extension is present use 0).
        
        Possible extension types:
        
        .. csv-table::
         :header: "Type", "Description"
         :widths: 10, 100
        
         "1",    "Chibi"
         "2",    "RS485"
         "3",    "WIFI"
         "4",    "Ethernet"
        
        The extension type is already set when bought and it can be set with the 
        Brick Viewer, it is unlikely that you need this function.
        
        The value will be saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_EXTENSION_TYPE, (extension, exttype), 'B I', '')

    def get_extension_type(self, extension):
        """
        Returns the extension type for a given extension as set by 
        :func:`SetExtensionType`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_EXTENSION_TYPE, (extension,), 'B', 'I')

    def is_chibi_present(self):
        """
        Returns *true* if a Chibi Extension is available to be used by the Master.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_IS_CHIBI_PRESENT, (), '', '?')

    def set_chibi_address(self, address):
        """
        Sets the address (1-255) belonging to the Chibi Extension.
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_ADDRESS, (address,), 'B', '')

    def get_chibi_address(self):
        """
        Returns the address as set by :func:`SetChibiAddress`.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_ADDRESS, (), '', 'B')

    def set_chibi_master_address(self, address):
        """
        Sets the address (1-255) of the Chibi Master. This address is used if the
        Chibi Extension is used as slave (i.e. it does not have a USB connection).
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_MASTER_ADDRESS, (address,), 'B', '')

    def get_chibi_master_address(self):
        """
        Returns the address as set by :func:`SetChibiMasterAddress`.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_MASTER_ADDRESS, (), '', 'B')

    def set_chibi_slave_address(self, num, address):
        """
        Sets up to 254 slave addresses. Valid addresses are in range 1-255.
        The address numeration (via num parameter) has to be used
        ascending from 0. For example: If you use the Chibi Extension in Master mode
        (i.e. the stack has an USB connection) and you want to talk to three other
        Chibi stacks with the slave addresses 17, 23, and 42, you should call with "(0, 17),
        (1, 23) and (2, 42)".
        
        It is possible to set the addresses with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, they don't
        have to be set on every startup.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_chibi_slave_address(self, num):
        """
        Returns the slave address for a given num as set by 
        :func:`SetChibiSlaveAddress`.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_chibi_signal_strength(self):
        """
        Returns the signal strength in dBm. The signal strength updates every time a
        packet is received.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_SIGNAL_STRENGTH, (), '', 'B')

    def get_chibi_error_log(self):
        """
        Returns underrun, CRC error, no ACK and overflow error counts of the Chibi
        communication. If these errors start rising, it is likely that either the
        distance between two Chibi stacks is becoming too big or there are
        interferences.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return GetChibiErrorLog(*self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_ERROR_LOG, (), '', 'H H H H'))

    def set_chibi_frequency(self, frequency):
        """
        Sets the Chibi frequency range for the Chibi Extension. Possible values are:
        
        .. csv-table::
         :header: "Type", "Description"
         :widths: 10, 100
        
         "0",    "OQPSK 868Mhz (Europe)"
         "1",    "OQPSK 915Mhz (US)"
         "2",    "OQPSK 780Mhz (China)"
         "3",    "BPSK40 915Mhz"
        
        It is possible to set the frequency with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_FREQUENCY, (frequency,), 'B', '')

    def get_chibi_frequency(self):
        """
        Returns the frequency value as set by :func:`SetChibiFrequency`.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_FREQUENCY, (), '', 'B')

    def set_chibi_channel(self, channel):
        """
        Sets the channel used by the Chibi Extension. Possible channels are
        different for different frequencies:
        
        .. csv-table::
         :header: "Frequency",             "Possible Channels"
         :widths: 40, 60
        
         "OQPSK 868Mhz (Europe)", "0"
         "OQPSK 915Mhz (US)",     "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
         "OQPSK 780Mhz (China)",  "0, 1, 2, 3"
         "BPSK40 915Mhz",         "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
        
        It is possible to set the channel with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_CHANNEL, (channel,), 'B', '')

    def get_chibi_channel(self):
        """
        Returns the channel as set by :func:`SetChibiChannel`.
        
        .. versionadded:: 1.1.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_CHANNEL, (), '', 'B')

    def is_rs485_present(self):
        """
        Returns *true* if a RS485 Extension is available to be used by the Master.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_IS_RS485_PRESENT, (), '', '?')

    def set_rs485_address(self, address):
        """
        Sets the address (1-255) belonging to the RS485 Extension.
        
        Set to 0 if the RS485 Extension should be the RS485 Master (i.e.
        connected to a PC via USB).
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the RS485 Extension, it does not
        have to be set on every startup.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_RS485_ADDRESS, (address,), 'B', '')

    def get_rs485_address(self):
        """
        Returns the address as set by :func:`SetRS485Address`.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_ADDRESS, (), '', 'B')

    def set_rs485_slave_address(self, num, address):
        """
        Sets up to 255 slave addresses. Valid addresses are in range 1-255.
        The address numeration (via num parameter) has to be used
        ascending from 0. For example: If you use the RS485 Extension in Master mode
        (i.e. the stack has an USB connection) and you want to talk to three other
        RS485 stacks with the IDs 17, 23, and 42, you should call with "(0, 17),
        (1, 23) and (2, 42)".
        
        It is possible to set the addresses with the Brick Viewer and it will be 
        saved in the EEPROM of the RS485 Extension, they don't
        have to be set on every startup.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_RS485_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_rs485_slave_address(self, num):
        """
        Returns the slave address for a given num as set by 
        :func:`SetRS485SlaveAddress`.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_rs485_error_log(self):
        """
        Returns CRC error counts of the RS485 communication.
        If this counter starts rising, it is likely that the distance
        between the RS485 nodes is too big or there is some kind of
        interference.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_ERROR_LOG, (), '', 'H')

    def set_rs485_configuration(self, speed, parity, stopbits):
        """
        Sets the configuration of the RS485 Extension. Speed is given in baud. The
        Master Brick will try to match the given baud rate as exactly as possible.
        The maximum recommended baud rate is 2000000 (2Mbit/s).
        Possible values for parity are 'n' (none), 'e' (even) and 'o' (odd).
        Possible values for stop bits are 1 and 2.
        
        If your RS485 is unstable (lost messages etc.), the first thing you should
        try is to decrease the speed. On very large bus (e.g. 1km), you probably
        should use a value in the range of 100000 (100kbit/s).
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_RS485_CONFIGURATION, (speed, parity, stopbits), 'I c B', '')

    def get_rs485_configuration(self):
        """
        Returns the configuration as set by :func:`SetRS485Configuration`.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        return GetRS485Configuration(*self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_CONFIGURATION, (), '', 'I c B'))

    def is_wifi_present(self):
        """
        Returns *true* if a WIFI Extension is available to be used by the Master.
        
        .. versionadded:: 1.2.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_IS_WIFI_PRESENT, (), '', '?')

    def set_wifi_configuration(self, ssid, connection, ip, subnet_mask, gateway, port):
        """
        Sets the configuration of the WIFI Extension. The *ssid* can have a max length
        of 32 characters. Possible values for *connection* are:
        
        .. csv-table::
         :header: "Value", "Description"
         :widths: 10, 90
        
         "0", "DHCP"
         "1", "Static IP"
         "2", "Access Point: DHCP"
         "3", "Access Point: Static IP"
         "4", "Ad Hoc: DHCP"
         "5", "Ad Hoc: Static IP"
        
        If you set *connection* to one of the static IP options then you have to supply
        *ip*, *subnet_mask* and *gateway* as an array of size 4 (first element of the
        array is the least significant byte of the address). If *connection* is set to
        one of the DHCP options then *ip*, *subnet_mask* and *gateway* are ignored, you
        can set them to 0.
        
        The last parameter is the port that your program will connect to. The
        default port, that is used by brickd, is 4223.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the WIFI configuration.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_WIFI_CONFIGURATION, (ssid, connection, ip, subnet_mask, gateway, port), '32s B 4B 4B 4B H', '')

    def get_wifi_configuration(self):
        """
        Returns the configuration as set by :func:`SetWifiConfiguration`.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        return GetWifiConfiguration(*self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_CONFIGURATION, (), '', '32s B 4B 4B 4B H'))

    def set_wifi_encryption(self, encryption, key, key_index, eap_options, ca_certificate_length, client_certificate_length, private_key_length):
        """
        Sets the encryption of the WIFI Extension. The first parameter is the
        type of the encryption. Possible values are:
        
        .. csv-table::
         :header: "Value", "Description"
         :widths: 10, 90
        
         "0", "WPA/WPA2"
         "1", "WPA Enterprise (EAP-FAST, EAP-TLS, EAP-TTLS, PEAP)"
         "2", "WEP"
         "3", "No Encryption"
        
        The key has a max length of 50 characters and is used if encryption
        is set to 0 or 2 (WPA or WEP). Otherwise the value is ignored.
        For WEP it is possible to set the key index (1-4). If you don't know your
        key index, it is likely 1.
        
        If you choose WPA Enterprise as encryption, you have to set eap options and
        the length of the certificates (for other encryption types these paramters
        are ignored). The certificate length are given in byte and the certificates
        themself can be set with  :func:`SetWifiCertificate`. Eap options consist of 
        the outer authentication (bits 1-2), inner authentication (bit 3) and 
        certificate type (bits 4-5):
        
        .. csv-table::
         :header: "Option", "Bits", "Description"
         :widths: 10, 10, 80
        
         "outer auth", "1-2", "0=EAP-FAST, 1=EAP-TLS, 2=EAP-TTLS, 3=EAP-PEAP"
         "inner auth", "3", "0=EAP-MSCHAP, 1=EAP-GTC"
         "cert type", "4-5", "0=CA Certificate, 1=Client Certificate, 2=Private Key"
        
        Example for EAP-TTLS + EAP-GTC + Private Key: option = 2 | (1 << 2) | (2 << 3).
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the WIFI encryption.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_WIFI_ENCRYPTION, (encryption, key, key_index, eap_options, ca_certificate_length, client_certificate_length, private_key_length), 'B 50s B B H H H', '')

    def get_wifi_encryption(self):
        """
        Returns the encryption as set by :func:`SetWifiEncryption`.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        return GetWifiEncryption(*self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_ENCRYPTION, (), '', 'B 50s B B H H H'))

    def get_wifi_status(self):
        """
        Returns the status of the WIFI Extension. The state is updated automatically,
        all of the other parameters are updated on startup and every time
        :func:`RefreshWifiStatus` is called.
        
        Possible states are:
        
        .. csv-table::
         :header: "State", "Description"
         :widths: 10, 90
        
         "0", "Disassociated"
         "1", "Associated"
         "2", "Associating"
         "3", "Error"
         "255", "Not initialized yet"
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        return GetWifiStatus(*self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_STATUS, (), '', '6B 6B B h 4B 4B 4B I I B'))

    def refresh_wifi_status(self):
        """
        Refreshes the WIFI status (see :func:`GetWifiStatus`). To read the status
        of the WIFI module, the Master Brick has to change from data mode to
        command mode and back. This transaction and the readout itself is
        unfortunately time consuming. This means, that it might take some ms
        until the stack with attached WIFI Extensions reacts again after this
        function is called.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_REFRESH_WIFI_STATUS, (), '', '')

    def set_wifi_certificate(self, index, data, data_length):
        """
        This function is used to set the certificate as well as password and username
        for WPA Enterprise. To set the username use index 0xFFFF,
        to set the password use index 0xFFFE. The max length of username and 
        password is 32.
        
        The certificate is written in chunks of size 32 and the index is used as
        the index of the chunk. The data length should nearly always be 32. Only
        the last chunk can have a length that is not equal to 32.
        
        The starting index of the CA Certificate is 0, of the Client Certificate
        10000 and for the Private Key 20000. Maximum sizes are 1312, 1312 and
        4320 byte respectively.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after uploading the certificate.
        
        It is recommended to use the Brick Viewer to set the certificate, username
        and password.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_WIFI_CERTIFICATE, (index, data, data_length), 'H 32B B', '')

    def get_wifi_certificate(self, index):
        """
        Returns the certificate for a given index as set by :func:`SetWifiCertificate`.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        return GetWifiCertificate(*self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_CERTIFICATE, (index,), 'H', '32B B'))

    def set_wifi_power_mode(self, mode):
        """
        Sets the power mode of the WIFI Extension. Possible modes are:
        
        .. csv-table::
         :header: "Mode", "Description"
         :widths: 10, 90
        
         "0", "Full Speed (high power consumption, high throughput)"
         "1", "Low Power (low power consumption, low throughput)"
        
        The default value is 0 (Full Speed).
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_WIFI_POWER_MODE, (mode,), 'B', '')

    def get_wifi_power_mode(self):
        """
        Returns the power mode as set by :func:`SetWifiPowerMode`.
        
        .. versionadded:: 1.3.0~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_POWER_MODE, (), '', 'B')

    def get_wifi_buffer_info(self):
        """
        Returns informations about the WIFI receive buffer. The WIFI
        receive buffer has a max size of 1500 byte and if data is transfered
        too fast, it might overflow.
        
        The return values are the number of overflows, the low watermark 
        (i.e. the smallest number of bytes that were free in the buffer) and
        the bytes that are currently used.
        
        You should always try to keep the buffer empty, otherwise you will
        have a permanent latency. A good rule of thumb is, that you can transfer
        1000 messages per second without problems.
        
        Try to not send more then 50 messages at a time without any kind of
        break between them.
        
        .. versionadded:: 1.3.2~(Firmware)
        """
        return GetWifiBufferInfo(*self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_BUFFER_INFO, (), '', 'I H H'))

    def set_wifi_regulatory_domain(self, domain):
        """
        Sets the regulatory domain of the WIFI Extension. Possible domains are:
        
        .. csv-table::
         :header: "Domain", "Description"
         :widths: 10, 90
        
         "0", "FCC: Channel 1-11 (N/S America, Australia, New Zealand)"
         "1", "ETSI: Channel 1-13 (Europe, Middle East, Africa)"
         "2", "TELEC: Channel 1-14 (Japan)"
        
        The default value is 1 (ETSI).
        
        .. versionadded:: 1.3.4~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_WIFI_REGULATORY_DOMAIN, (domain,), 'B', '')

    def get_wifi_regulatory_domain(self):
        """
        Returns the regulatory domain as set by :func:`SetWifiRegulatoryDomain`.
        
        .. versionadded:: 1.3.4~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_WIFI_REGULATORY_DOMAIN, (), '', 'B')

    def get_usb_voltage(self):
        """
        Returns the USB voltage in mV.
        
        .. versionadded:: 1.3.5~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_USB_VOLTAGE, (), '', 'H')

    def reset(self):
        """
        Calling this function will reset the Brick. Calling this function
        on a Brick inside of a stack will reset the whole stack.
        
        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        
        .. versionadded:: 1.2.1~(Firmware)
        """
        self.ipcon.send_request(self, Master.FUNCTION_RESET, (), '', '')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C/10 as measured inside the microcontroller. The
        value returned is not the ambient temperature!
        
        The temperature is only proportional to the real temperature and it has an
        accuracy of +-15%. Practically it is only useful as an indicator for
        temperature changes.
        
        .. versionadded:: 1.2.1~(Firmware)
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')
