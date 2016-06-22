# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-06-22.      #
#                                                           #
# Python Bindings Version 2.1.9                             #
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

GetChibiErrorLog = namedtuple('ChibiErrorLog', ['underrun', 'crc_error', 'no_ack', 'overflow'])
GetRS485Configuration = namedtuple('RS485Configuration', ['speed', 'parity', 'stopbits'])
GetWifiConfiguration = namedtuple('WifiConfiguration', ['ssid', 'connection', 'ip', 'subnet_mask', 'gateway', 'port'])
GetWifiEncryption = namedtuple('WifiEncryption', ['encryption', 'key', 'key_index', 'eap_options', 'ca_certificate_length', 'client_certificate_length', 'private_key_length'])
GetWifiStatus = namedtuple('WifiStatus', ['mac_address', 'bssid', 'channel', 'rssi', 'ip', 'subnet_mask', 'gateway', 'rx_count', 'tx_count', 'state'])
GetWifiCertificate = namedtuple('WifiCertificate', ['data', 'data_length'])
GetWifiBufferInfo = namedtuple('WifiBufferInfo', ['overflow', 'low_watermark', 'used'])
GetStackCurrentCallbackThreshold = namedtuple('StackCurrentCallbackThreshold', ['option', 'min', 'max'])
GetStackVoltageCallbackThreshold = namedtuple('StackVoltageCallbackThreshold', ['option', 'min', 'max'])
GetUSBVoltageCallbackThreshold = namedtuple('USBVoltageCallbackThreshold', ['option', 'min', 'max'])
GetEthernetConfiguration = namedtuple('EthernetConfiguration', ['connection', 'ip', 'subnet_mask', 'gateway', 'port'])
GetEthernetStatus = namedtuple('EthernetStatus', ['mac_address', 'ip', 'subnet_mask', 'gateway', 'rx_count', 'tx_count', 'hostname'])
GetEthernetWebsocketConfiguration = namedtuple('EthernetWebsocketConfiguration', ['sockets', 'port'])
ReadWifi2Flash = namedtuple('ReadWifi2Flash', ['data', 'length_out'])
GetWifi2Configuration = namedtuple('Wifi2Configuration', ['port', 'websocket_port', 'website_port', 'phy_mode', 'sleep_mode', 'website'])
GetWifi2Status = namedtuple('Wifi2Status', ['client_enabled', 'client_status', 'client_ip', 'client_subnet_mask', 'client_gateway', 'client_mac_address', 'client_rx_count', 'client_tx_count', 'client_rssi', 'ap_enabled', 'ap_ip', 'ap_subnet_mask', 'ap_gateway', 'ap_mac_address', 'ap_rx_count', 'ap_tx_count', 'ap_connected_count'])
GetWifi2ClientConfiguration = namedtuple('Wifi2ClientConfiguration', ['enable', 'ssid', 'ip', 'subnet_mask', 'gateway', 'mac_address', 'bssid'])
GetWifi2APConfiguration = namedtuple('Wifi2APConfiguration', ['enable', 'ssid', 'ip', 'subnet_mask', 'gateway', 'encryption', 'hidden', 'channel', 'mac_address'])
GetProtocol1BrickletName = namedtuple('Protocol1BrickletName', ['protocol_version', 'firmware_version', 'name'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickMaster(Device):
    """
    Basis to build stacks and has 4 Bricklet ports
    """

    DEVICE_IDENTIFIER = 13
    DEVICE_DISPLAY_NAME = 'Master Brick'

    CALLBACK_STACK_CURRENT = 59
    CALLBACK_STACK_VOLTAGE = 60
    CALLBACK_USB_VOLTAGE = 61
    CALLBACK_STACK_CURRENT_REACHED = 62
    CALLBACK_STACK_VOLTAGE_REACHED = 63
    CALLBACK_USB_VOLTAGE_REACHED = 64

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
    FUNCTION_SET_LONG_WIFI_KEY = 41
    FUNCTION_GET_LONG_WIFI_KEY = 42
    FUNCTION_SET_WIFI_HOSTNAME = 43
    FUNCTION_GET_WIFI_HOSTNAME = 44
    FUNCTION_SET_STACK_CURRENT_CALLBACK_PERIOD = 45
    FUNCTION_GET_STACK_CURRENT_CALLBACK_PERIOD = 46
    FUNCTION_SET_STACK_VOLTAGE_CALLBACK_PERIOD = 47
    FUNCTION_GET_STACK_VOLTAGE_CALLBACK_PERIOD = 48
    FUNCTION_SET_USB_VOLTAGE_CALLBACK_PERIOD = 49
    FUNCTION_GET_USB_VOLTAGE_CALLBACK_PERIOD = 50
    FUNCTION_SET_STACK_CURRENT_CALLBACK_THRESHOLD = 51
    FUNCTION_GET_STACK_CURRENT_CALLBACK_THRESHOLD = 52
    FUNCTION_SET_STACK_VOLTAGE_CALLBACK_THRESHOLD = 53
    FUNCTION_GET_STACK_VOLTAGE_CALLBACK_THRESHOLD = 54
    FUNCTION_SET_USB_VOLTAGE_CALLBACK_THRESHOLD = 55
    FUNCTION_GET_USB_VOLTAGE_CALLBACK_THRESHOLD = 56
    FUNCTION_SET_DEBOUNCE_PERIOD = 57
    FUNCTION_GET_DEBOUNCE_PERIOD = 58
    FUNCTION_IS_ETHERNET_PRESENT = 65
    FUNCTION_SET_ETHERNET_CONFIGURATION = 66
    FUNCTION_GET_ETHERNET_CONFIGURATION = 67
    FUNCTION_GET_ETHERNET_STATUS = 68
    FUNCTION_SET_ETHERNET_HOSTNAME = 69
    FUNCTION_SET_ETHERNET_MAC_ADDRESS = 70
    FUNCTION_SET_ETHERNET_WEBSOCKET_CONFIGURATION = 71
    FUNCTION_GET_ETHERNET_WEBSOCKET_CONFIGURATION = 72
    FUNCTION_SET_ETHERNET_AUTHENTICATION_SECRET = 73
    FUNCTION_GET_ETHERNET_AUTHENTICATION_SECRET = 74
    FUNCTION_SET_WIFI_AUTHENTICATION_SECRET = 75
    FUNCTION_GET_WIFI_AUTHENTICATION_SECRET = 76
    FUNCTION_GET_CONNECTION_TYPE = 77
    FUNCTION_IS_WIFI2_PRESENT = 78
    FUNCTION_START_WIFI2_BOOTLOADER = 79
    FUNCTION_WRITE_WIFI2_FLASH = 80
    FUNCTION_READ_WIFI2_FLASH = 81
    FUNCTION_SET_WIFI2_AUTHENTICATION_SECRET = 82
    FUNCTION_GET_WIFI2_AUTHENTICATION_SECRET = 83
    FUNCTION_SET_WIFI2_CONFIGURATION = 84
    FUNCTION_GET_WIFI2_CONFIGURATION = 85
    FUNCTION_GET_WIFI2_STATUS = 86
    FUNCTION_SET_WIFI2_CLIENT_CONFIGURATION = 87
    FUNCTION_GET_WIFI2_CLIENT_CONFIGURATION = 88
    FUNCTION_SET_WIFI2_CLIENT_HOSTNAME = 89
    FUNCTION_GET_WIFI2_CLIENT_HOSTNAME = 90
    FUNCTION_SET_WIFI2_CLIENT_PASSWORD = 91
    FUNCTION_GET_WIFI2_CLIENT_PASSWORD = 92
    FUNCTION_SET_WIFI2_AP_CONFIGURATION = 93
    FUNCTION_GET_WIFI2_AP_CONFIGURATION = 94
    FUNCTION_SET_WIFI2_AP_PASSWORD = 95
    FUNCTION_GET_WIFI2_AP_PASSWORD = 96
    FUNCTION_SAVE_WIFI2_CONFIGURATION = 97
    FUNCTION_GET_WIFI2_FIRMWARE_VERSION = 98
    FUNCTION_ENABLE_WIFI2_STATUS_LED = 99
    FUNCTION_DISABLE_WIFI2_STATUS_LED = 100
    FUNCTION_IS_WIFI2_STATUS_LED_ENABLED = 101
    FUNCTION_ENABLE_STATUS_LED = 238
    FUNCTION_DISABLE_STATUS_LED = 239
    FUNCTION_IS_STATUS_LED_ENABLED = 240
    FUNCTION_GET_PROTOCOL1_BRICKLET_NAME = 241
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_GET_IDENTITY = 255

    EXTENSION_TYPE_CHIBI = 1
    EXTENSION_TYPE_RS485 = 2
    EXTENSION_TYPE_WIFI = 3
    EXTENSION_TYPE_ETHERNET = 4
    EXTENSION_TYPE_WIFI2 = 5
    CHIBI_FREQUENCY_OQPSK_868_MHZ = 0
    CHIBI_FREQUENCY_OQPSK_915_MHZ = 1
    CHIBI_FREQUENCY_OQPSK_780_MHZ = 2
    CHIBI_FREQUENCY_BPSK40_915_MHZ = 3
    RS485_PARITY_NONE = 'n'
    RS485_PARITY_EVEN = 'e'
    RS485_PARITY_ODD = 'o'
    WIFI_CONNECTION_DHCP = 0
    WIFI_CONNECTION_STATIC_IP = 1
    WIFI_CONNECTION_ACCESS_POINT_DHCP = 2
    WIFI_CONNECTION_ACCESS_POINT_STATIC_IP = 3
    WIFI_CONNECTION_AD_HOC_DHCP = 4
    WIFI_CONNECTION_AD_HOC_STATIC_IP = 5
    WIFI_ENCRYPTION_WPA_WPA2 = 0
    WIFI_ENCRYPTION_WPA_ENTERPRISE = 1
    WIFI_ENCRYPTION_WEP = 2
    WIFI_ENCRYPTION_NO_ENCRYPTION = 3
    WIFI_EAP_OPTION_OUTER_AUTH_EAP_FAST = 0
    WIFI_EAP_OPTION_OUTER_AUTH_EAP_TLS = 1
    WIFI_EAP_OPTION_OUTER_AUTH_EAP_TTLS = 2
    WIFI_EAP_OPTION_OUTER_AUTH_EAP_PEAP = 3
    WIFI_EAP_OPTION_INNER_AUTH_EAP_MSCHAP = 0
    WIFI_EAP_OPTION_INNER_AUTH_EAP_GTC = 4
    WIFI_EAP_OPTION_CERT_TYPE_CA_CERT = 0
    WIFI_EAP_OPTION_CERT_TYPE_CLIENT_CERT = 8
    WIFI_EAP_OPTION_CERT_TYPE_PRIVATE_KEY = 16
    WIFI_STATE_DISASSOCIATED = 0
    WIFI_STATE_ASSOCIATED = 1
    WIFI_STATE_ASSOCIATING = 2
    WIFI_STATE_ERROR = 3
    WIFI_STATE_NOT_INITIALIZED_YET = 255
    WIFI_POWER_MODE_FULL_SPEED = 0
    WIFI_POWER_MODE_LOW_POWER = 1
    WIFI_DOMAIN_CHANNEL_1TO11 = 0
    WIFI_DOMAIN_CHANNEL_1TO13 = 1
    WIFI_DOMAIN_CHANNEL_1TO14 = 2
    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    ETHERNET_CONNECTION_DHCP = 0
    ETHERNET_CONNECTION_STATIC_IP = 1
    CONNECTION_TYPE_NONE = 0
    CONNECTION_TYPE_USB = 1
    CONNECTION_TYPE_SPI_STACK = 2
    CONNECTION_TYPE_CHIBI = 3
    CONNECTION_TYPE_RS485 = 4
    CONNECTION_TYPE_WIFI = 5
    CONNECTION_TYPE_ETHERNET = 6
    CONNECTION_TYPE_WIFI2 = 7

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 4)

        self.response_expected[BrickMaster.FUNCTION_GET_STACK_VOLTAGE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_STACK_CURRENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_EXTENSION_TYPE] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_EXTENSION_TYPE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_IS_CHIBI_PRESENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_CHIBI_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_CHIBI_MASTER_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_MASTER_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_CHIBI_SLAVE_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_SLAVE_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_SIGNAL_STRENGTH] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_ERROR_LOG] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_CHIBI_FREQUENCY] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_FREQUENCY] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_CHIBI_CHANNEL] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIBI_CHANNEL] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_IS_RS485_PRESENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_RS485_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_RS485_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_RS485_SLAVE_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_RS485_SLAVE_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_RS485_ERROR_LOG] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_RS485_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_RS485_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_IS_WIFI_PRESENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_ENCRYPTION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_ENCRYPTION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_STATUS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_REFRESH_WIFI_STATUS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_CERTIFICATE] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_CERTIFICATE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_POWER_MODE] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_POWER_MODE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_BUFFER_INFO] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_REGULATORY_DOMAIN] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_REGULATORY_DOMAIN] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_USB_VOLTAGE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_LONG_WIFI_KEY] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_LONG_WIFI_KEY] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_HOSTNAME] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_HOSTNAME] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_STACK_CURRENT_CALLBACK_PERIOD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_STACK_CURRENT_CALLBACK_PERIOD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_STACK_VOLTAGE_CALLBACK_PERIOD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_STACK_VOLTAGE_CALLBACK_PERIOD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_USB_VOLTAGE_CALLBACK_PERIOD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_USB_VOLTAGE_CALLBACK_PERIOD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_STACK_CURRENT_CALLBACK_THRESHOLD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_STACK_CURRENT_CALLBACK_THRESHOLD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_STACK_VOLTAGE_CALLBACK_THRESHOLD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_STACK_VOLTAGE_CALLBACK_THRESHOLD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_USB_VOLTAGE_CALLBACK_THRESHOLD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_USB_VOLTAGE_CALLBACK_THRESHOLD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickMaster.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.CALLBACK_STACK_CURRENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickMaster.CALLBACK_STACK_VOLTAGE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickMaster.CALLBACK_USB_VOLTAGE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickMaster.CALLBACK_STACK_CURRENT_REACHED] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickMaster.CALLBACK_STACK_VOLTAGE_REACHED] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickMaster.CALLBACK_USB_VOLTAGE_REACHED] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickMaster.FUNCTION_IS_ETHERNET_PRESENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_ETHERNET_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_ETHERNET_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_ETHERNET_STATUS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_ETHERNET_HOSTNAME] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_SET_ETHERNET_MAC_ADDRESS] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_SET_ETHERNET_WEBSOCKET_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_ETHERNET_WEBSOCKET_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_ETHERNET_AUTHENTICATION_SECRET] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_ETHERNET_AUTHENTICATION_SECRET] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI_AUTHENTICATION_SECRET] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI_AUTHENTICATION_SECRET] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_CONNECTION_TYPE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_IS_WIFI2_PRESENT] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_START_WIFI2_BOOTLOADER] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_WRITE_WIFI2_FLASH] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_READ_WIFI2_FLASH] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_AUTHENTICATION_SECRET] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_AUTHENTICATION_SECRET] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_STATUS] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_CLIENT_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_CLIENT_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_CLIENT_HOSTNAME] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_CLIENT_HOSTNAME] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_CLIENT_PASSWORD] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_CLIENT_PASSWORD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_AP_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_AP_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SET_WIFI2_AP_PASSWORD] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_AP_PASSWORD] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_SAVE_WIFI2_CONFIGURATION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_WIFI2_FIRMWARE_VERSION] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_ENABLE_WIFI2_STATUS_LED] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_DISABLE_WIFI2_STATUS_LED] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_IS_WIFI2_STATUS_LED_ENABLED] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_ENABLE_STATUS_LED] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_DISABLE_STATUS_LED] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_IS_STATUS_LED_ENABLED] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_PROTOCOL1_BRICKLET_NAME] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_GET_CHIP_TEMPERATURE] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickMaster.FUNCTION_RESET] = BrickMaster.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickMaster.FUNCTION_GET_IDENTITY] = BrickMaster.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickMaster.CALLBACK_STACK_CURRENT] = 'H'
        self.callback_formats[BrickMaster.CALLBACK_STACK_VOLTAGE] = 'H'
        self.callback_formats[BrickMaster.CALLBACK_USB_VOLTAGE] = 'H'
        self.callback_formats[BrickMaster.CALLBACK_STACK_CURRENT_REACHED] = 'H'
        self.callback_formats[BrickMaster.CALLBACK_STACK_VOLTAGE_REACHED] = 'H'
        self.callback_formats[BrickMaster.CALLBACK_USB_VOLTAGE_REACHED] = 'H'

    def get_stack_voltage(self):
        """
        Returns the stack voltage in mV. The stack voltage is the
        voltage that is supplied via the stack, i.e. it is given by a 
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_STACK_VOLTAGE, (), '', 'H')

    def get_stack_current(self):
        """
        Returns the stack current in mA. The stack current is the
        current that is drawn via the stack, i.e. it is given by a
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_STACK_CURRENT, (), '', 'H')

    def set_extension_type(self, extension, exttype):
        """
        Writes the extension type to the EEPROM of a specified extension. 
        The extension is either 0 or 1 (0 is the on the bottom, 1 is the one on top,
        if only one extension is present use 0).
        
        Possible extension types:
        
        .. csv-table::
         :header: "Type", "Description"
         :widths: 10, 100
        
         "1",    "Chibi"
         "2",    "RS485"
         "3",    "WIFI"
         "4",    "Ethernet"
         "5",    "WIFI 2.0"
        
        The extension type is already set when bought and it can be set with the 
        Brick Viewer, it is unlikely that you need this function.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_EXTENSION_TYPE, (extension, exttype), 'B I', '')

    def get_extension_type(self, extension):
        """
        Returns the type for a given extension as set by :func:`SetExtensionType`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_EXTENSION_TYPE, (extension,), 'B', 'I')

    def is_chibi_present(self):
        """
        Returns *true* if a Chibi Extension is available to be used by the Master Brick.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_CHIBI_PRESENT, (), '', '?')

    def set_chibi_address(self, address):
        """
        Sets the address (1-255) belonging to the Chibi Extension.
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_CHIBI_ADDRESS, (address,), 'B', '')

    def get_chibi_address(self):
        """
        Returns the address as set by :func:`SetChibiAddress`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_ADDRESS, (), '', 'B')

    def set_chibi_master_address(self, address):
        """
        Sets the address (1-255) of the Chibi Master. This address is used if the
        Chibi Extension is used as slave (i.e. it does not have a USB connection).
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_CHIBI_MASTER_ADDRESS, (address,), 'B', '')

    def get_chibi_master_address(self):
        """
        Returns the address as set by :func:`SetChibiMasterAddress`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_MASTER_ADDRESS, (), '', 'B')

    def set_chibi_slave_address(self, num, address):
        """
        Sets up to 254 slave addresses. Valid addresses are in range 1-255. 0 has a
        special meaning, it is used as list terminator and not allowed as normal slave
        address. The address numeration (via ``num`` parameter) has to be used
        ascending from 0. For example: If you use the Chibi Extension in Master mode
        (i.e. the stack has an USB connection) and you want to talk to three other
        Chibi stacks with the slave addresses 17, 23, and 42, you should call with
        ``(0, 17)``, ``(1, 23)``, ``(2, 42)`` and ``(3, 0)``. The last call with
        ``(3, 0)`` is a list terminator and indicates that the Chibi slave address
        list contains 3 addresses in this case.
        
        It is possible to set the addresses with the Brick Viewer, that will take care
        of correct address numeration and list termination.
        
        The slave addresses will be saved in the EEPROM of the Chibi Extension, they
        don't have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_CHIBI_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_chibi_slave_address(self, num):
        """
        Returns the slave address for a given ``num`` as set by
        :func:`SetChibiSlaveAddress`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_chibi_signal_strength(self):
        """
        Returns the signal strength in dBm. The signal strength updates every time a
        packet is received.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_SIGNAL_STRENGTH, (), '', 'B')

    def get_chibi_error_log(self):
        """
        Returns underrun, CRC error, no ACK and overflow error counts of the Chibi
        communication. If these errors start rising, it is likely that either the
        distance between two Chibi stacks is becoming too big or there are
        interferences.
        """
        return GetChibiErrorLog(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_ERROR_LOG, (), '', 'H H H H'))

    def set_chibi_frequency(self, frequency):
        """
        Sets the Chibi frequency range for the Chibi Extension. Possible values are:
        
        .. csv-table::
         :header: "Type", "Description"
         :widths: 10, 100
        
         "0",    "OQPSK 868MHz (Europe)"
         "1",    "OQPSK 915MHz (US)"
         "2",    "OQPSK 780MHz (China)"
         "3",    "BPSK40 915MHz"
        
        It is possible to set the frequency with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_CHIBI_FREQUENCY, (frequency,), 'B', '')

    def get_chibi_frequency(self):
        """
        Returns the frequency value as set by :func:`SetChibiFrequency`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_FREQUENCY, (), '', 'B')

    def set_chibi_channel(self, channel):
        """
        Sets the channel used by the Chibi Extension. Possible channels are
        different for different frequencies:
        
        .. csv-table::
         :header: "Frequency",             "Possible Channels"
         :widths: 40, 60
        
         "OQPSK 868MHz (Europe)", "0"
         "OQPSK 915MHz (US)",     "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
         "OQPSK 780MHz (China)",  "0, 1, 2, 3"
         "BPSK40 915MHz",         "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
        
        It is possible to set the channel with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_CHIBI_CHANNEL, (channel,), 'B', '')

    def get_chibi_channel(self):
        """
        Returns the channel as set by :func:`SetChibiChannel`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIBI_CHANNEL, (), '', 'B')

    def is_rs485_present(self):
        """
        Returns *true* if a RS485 Extension is available to be used by the Master Brick.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_RS485_PRESENT, (), '', '?')

    def set_rs485_address(self, address):
        """
        Sets the address (0-255) belonging to the RS485 Extension.
        
        Set to 0 if the RS485 Extension should be the RS485 Master (i.e.
        connected to a PC via USB).
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the RS485 Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_RS485_ADDRESS, (address,), 'B', '')

    def get_rs485_address(self):
        """
        Returns the address as set by :func:`SetRS485Address`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_RS485_ADDRESS, (), '', 'B')

    def set_rs485_slave_address(self, num, address):
        """
        Sets up to 255 slave addresses. Valid addresses are in range 1-255. 0 has a
        special meaning, it is used as list terminator and not allowed as normal slave
        address. The address numeration (via ``num`` parameter) has to be used
        ascending from 0. For example: If you use the RS485 Extension in Master mode
        (i.e. the stack has an USB connection) and you want to talk to three other
        RS485 stacks with the addresses 17, 23, and 42, you should call with
        ``(0, 17)``, ``(1, 23)``, ``(2, 42)`` and ``(3, 0)``. The last call with
        ``(3, 0)`` is a list terminator and indicates that the RS485 slave address list
        contains 3 addresses in this case.
        
        It is possible to set the addresses with the Brick Viewer, that will take care
        of correct address numeration and list termination.
        
        The slave addresses will be saved in the EEPROM of the Chibi Extension, they
        don't have to be set on every startup.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_RS485_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_rs485_slave_address(self, num):
        """
        Returns the slave address for a given ``num`` as set by
        :func:`SetRS485SlaveAddress`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_RS485_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_rs485_error_log(self):
        """
        Returns CRC error counts of the RS485 communication.
        If this counter starts rising, it is likely that the distance
        between the RS485 nodes is too big or there is some kind of
        interference.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_RS485_ERROR_LOG, (), '', 'H')

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
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_RS485_CONFIGURATION, (speed, parity, stopbits), 'I c B', '')

    def get_rs485_configuration(self):
        """
        Returns the configuration as set by :func:`SetRS485Configuration`.
        """
        return GetRS485Configuration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_RS485_CONFIGURATION, (), '', 'I c B'))

    def is_wifi_present(self):
        """
        Returns *true* if a WIFI Extension is available to be used by the Master Brick.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_WIFI_PRESENT, (), '', '?')

    def set_wifi_configuration(self, ssid, connection, ip, subnet_mask, gateway, port):
        """
        Sets the configuration of the WIFI Extension. The ``ssid`` can have a max length
        of 32 characters. Possible values for ``connection`` are:
        
        .. csv-table::
         :header: "Value", "Description"
         :widths: 10, 90
        
         "0", "DHCP"
         "1", "Static IP"
         "2", "Access Point: DHCP"
         "3", "Access Point: Static IP"
         "4", "Ad Hoc: DHCP"
         "5", "Ad Hoc: Static IP"
        
        If you set ``connection`` to one of the static IP options then you have to
        supply ``ip``, ``subnet_mask`` and ``gateway`` as an array of size 4 (first
        element of the array is the least significant byte of the address). If
        ``connection`` is set to one of the DHCP options then ``ip``, ``subnet_mask``
        and ``gateway`` are ignored, you can set them to 0.
        
        The last parameter is the port that your program will connect to. The
        default port, that is used by brickd, is 4223.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the WIFI configuration.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_CONFIGURATION, (ssid, connection, ip, subnet_mask, gateway, port), '32s B 4B 4B 4B H', '')

    def get_wifi_configuration(self):
        """
        Returns the configuration as set by :func:`SetWifiConfiguration`.
        """
        return GetWifiConfiguration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_CONFIGURATION, (), '', '32s B 4B 4B 4B H'))

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
        
        The ``key`` has a max length of 50 characters and is used if ``encryption``
        is set to 0 or 2 (WPA/WPA2 or WEP). Otherwise the value is ignored.
        
        For WPA/WPA2 the key has to be at least 8 characters long. If you want to set
        a key with more than 50 characters, see :func:`SetLongWifiKey`.
        
        For WEP the key has to be either 10 or 26 hexadecimal digits long. It is
        possible to set the WEP ``key_index`` (1-4). If you don't know your
        ``key_index``, it is likely 1.
        
        If you choose WPA Enterprise as encryption, you have to set ``eap_options`` and
        the length of the certificates (for other encryption types these parameters
        are ignored). The certificate length are given in byte and the certificates
        themselves can be set with :func:`SetWifiCertificate`. ``eap_options`` consist
        of the outer authentication (bits 1-2), inner authentication (bit 3) and
        certificate type (bits 4-5):
        
        .. csv-table::
         :header: "Option", "Bits", "Description"
         :widths: 20, 10, 70
        
         "outer authentication", "1-2", "0=EAP-FAST, 1=EAP-TLS, 2=EAP-TTLS, 3=EAP-PEAP"
         "inner authentication", "3", "0=EAP-MSCHAP, 1=EAP-GTC"
         "certificate type", "4-5", "0=CA Certificate, 1=Client Certificate, 2=Private Key"
        
        Example for EAP-TTLS + EAP-GTC + Private Key: ``option = 2 | (1 << 2) | (2 << 3)``.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the Wi-Fi encryption.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_ENCRYPTION, (encryption, key, key_index, eap_options, ca_certificate_length, client_certificate_length, private_key_length), 'B 50s B B H H H', '')

    def get_wifi_encryption(self):
        """
        Returns the encryption as set by :func:`SetWifiEncryption`.
        """
        return GetWifiEncryption(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_ENCRYPTION, (), '', 'B 50s B B H H H'))

    def get_wifi_status(self):
        """
        Returns the status of the WIFI Extension. The ``state`` is updated automatically,
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
        """
        return GetWifiStatus(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_STATUS, (), '', '6B 6B B h 4B 4B 4B I I B'))

    def refresh_wifi_status(self):
        """
        Refreshes the Wi-Fi status (see :func:`GetWifiStatus`). To read the status
        of the Wi-Fi module, the Master Brick has to change from data mode to
        command mode and back. This transaction and the readout itself is
        unfortunately time consuming. This means, that it might take some ms
        until the stack with attached WIFI Extension reacts again after this
        function is called.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_REFRESH_WIFI_STATUS, (), '', '')

    def set_wifi_certificate(self, index, data, data_length):
        """
        This function is used to set the certificate as well as password and username
        for WPA Enterprise. To set the username use index 0xFFFF,
        to set the password use index 0xFFFE. The max length of username and 
        password is 32.
        
        The certificate is written in chunks of size 32 and the index is used as
        the index of the chunk. ``data_length`` should nearly always be 32. Only
        the last chunk can have a length that is not equal to 32.
        
        The starting index of the CA Certificate is 0, of the Client Certificate
        10000 and for the Private Key 20000. Maximum sizes are 1312, 1312 and
        4320 byte respectively.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after uploading the certificate.
        
        It is recommended to use the Brick Viewer to set the certificate, username
        and password.
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_CERTIFICATE, (index, data, data_length), 'H 32B B', '')

    def get_wifi_certificate(self, index):
        """
        Returns the certificate for a given index as set by :func:`SetWifiCertificate`.
        """
        return GetWifiCertificate(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_CERTIFICATE, (index,), 'H', '32B B'))

    def set_wifi_power_mode(self, mode):
        """
        Sets the power mode of the WIFI Extension. Possible modes are:
        
        .. csv-table::
         :header: "Mode", "Description"
         :widths: 10, 90
        
         "0", "Full Speed (high power consumption, high throughput)"
         "1", "Low Power (low power consumption, low throughput)"
        
        The default value is 0 (Full Speed).
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_POWER_MODE, (mode,), 'B', '')

    def get_wifi_power_mode(self):
        """
        Returns the power mode as set by :func:`SetWifiPowerMode`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_POWER_MODE, (), '', 'B')

    def get_wifi_buffer_info(self):
        """
        Returns informations about the Wi-Fi receive buffer. The Wi-Fi
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
        """
        return GetWifiBufferInfo(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_BUFFER_INFO, (), '', 'I H H'))

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
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_REGULATORY_DOMAIN, (domain,), 'B', '')

    def get_wifi_regulatory_domain(self):
        """
        Returns the regulatory domain as set by :func:`SetWifiRegulatoryDomain`.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_REGULATORY_DOMAIN, (), '', 'B')

    def get_usb_voltage(self):
        """
        Returns the USB voltage in mV. Does not work with hardware version 2.1.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_USB_VOLTAGE, (), '', 'H')

    def set_long_wifi_key(self, key):
        """
        Sets a long Wi-Fi key (up to 63 chars, at least 8 chars) for WPA encryption.
        This key will be used
        if the key in :func:`SetWifiEncryption` is set to "-". In the old protocol,
        a payload of size 63 was not possible, so the maximum key length was 50 chars.
        
        With the new protocol this is possible, since we didn't want to break API,
        this function was added additionally.
        
        .. versionadded:: 2.0.2$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_LONG_WIFI_KEY, (key,), '64s', '')

    def get_long_wifi_key(self):
        """
        Returns the encryption key as set by :func:`SetLongWifiKey`.
        
        .. versionadded:: 2.0.2$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_LONG_WIFI_KEY, (), '', '64s')

    def set_wifi_hostname(self, hostname):
        """
        Sets the hostname of the WIFI Extension. The hostname will be displayed 
        by access points as the hostname in the DHCP clients table.
        
        Setting an empty String will restore the default hostname.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_HOSTNAME, (hostname,), '16s', '')

    def get_wifi_hostname(self):
        """
        Returns the hostname as set by :func:`GetWifiHostname`.
        
        An empty String means, that the default hostname is used.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_HOSTNAME, (), '', '16s')

    def set_stack_current_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`StackCurrent` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`StackCurrent` is only triggered if the current has changed since the
        last triggering.
        
        The default value is 0.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_STACK_CURRENT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_stack_current_callback_period(self):
        """
        Returns the period as set by :func:`SetCurrentCallbackPeriod`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_STACK_CURRENT_CALLBACK_PERIOD, (), '', 'I')

    def set_stack_voltage_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`StackVoltage` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`StackVoltage` is only triggered if the voltage has changed since the
        last triggering.
        
        The default value is 0.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_STACK_VOLTAGE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_stack_voltage_callback_period(self):
        """
        Returns the period as set by :func:`SetStackVoltageCallbackPeriod`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_STACK_VOLTAGE_CALLBACK_PERIOD, (), '', 'I')

    def set_usb_voltage_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`USBVoltage` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`USBVoltage` is only triggered if the voltage has changed since the
        last triggering.
        
        The default value is 0.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_USB_VOLTAGE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_usb_voltage_callback_period(self):
        """
        Returns the period as set by :func:`SetUSBVoltageCallbackPeriod`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_USB_VOLTAGE_CALLBACK_PERIOD, (), '', 'I')

    def set_stack_current_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`StackCurrentReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the current is *outside* the min and max values"
         "'i'",    "Callback is triggered when the current is *inside* the min and max values"
         "'<'",    "Callback is triggered when the current is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the current is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_STACK_CURRENT_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_stack_current_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetStackCurrentCallbackThreshold`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return GetStackCurrentCallbackThreshold(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_STACK_CURRENT_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_stack_voltage_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`StackStackVoltageReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the voltage is *outside* the min and max values"
         "'i'",    "Callback is triggered when the voltage is *inside* the min and max values"
         "'<'",    "Callback is triggered when the voltage is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the voltage is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_STACK_VOLTAGE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_stack_voltage_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetStackVoltageCallbackThreshold`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return GetStackVoltageCallbackThreshold(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_STACK_VOLTAGE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_usb_voltage_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`USBVoltageReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the voltage is *outside* the min and max values"
         "'i'",    "Callback is triggered when the voltage is *inside* the min and max values"
         "'<'",    "Callback is triggered when the voltage is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the voltage is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_USB_VOLTAGE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_usb_voltage_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetUSBVoltageCallbackThreshold`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return GetUSBVoltageCallbackThreshold(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_USB_VOLTAGE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`StackCurrentReached`,
        * :func:`StackVoltageReached`,
        * :func:`USBVoltageReached`
        
        are triggered, if the thresholds
        
        * :func:`SetStackCurrentCallbackThreshold`,
        * :func:`SetStackVoltageCallbackThreshold`,
        * :func:`SetUSBVoltageCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        
        .. versionadded:: 2.0.5$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def is_ethernet_present(self):
        """
        Returns *true* if a Ethernet Extension is available to be used by the Master
        Brick.
        
        .. versionadded:: 2.1.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_ETHERNET_PRESENT, (), '', '?')

    def set_ethernet_configuration(self, connection, ip, subnet_mask, gateway, port):
        """
        Sets the configuration of the Ethernet Extension. Possible values for
        ``connection`` are:
        
        .. csv-table::
         :header: "Value", "Description"
         :widths: 10, 90
        
         "0", "DHCP"
         "1", "Static IP"
        
        If you set ``connection`` to static IP options then you have to supply ``ip``,
        ``subnet_mask`` and ``gateway`` as an array of size 4 (first element of the
        array is the least significant byte of the address). If ``connection`` is set
        to the DHCP options then ``ip``, ``subnet_mask`` and ``gateway`` are ignored,
        you can set them to 0.
        
        The last parameter is the port that your program will connect to. The
        default port, that is used by brickd, is 4223.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the Ethernet configuration.
        
        .. versionadded:: 2.1.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_ETHERNET_CONFIGURATION, (connection, ip, subnet_mask, gateway, port), 'B 4B 4B 4B H', '')

    def get_ethernet_configuration(self):
        """
        Returns the configuration as set by :func:`SetEthernetConfiguration`.
        
        .. versionadded:: 2.1.0$nbsp;(Firmware)
        """
        return GetEthernetConfiguration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_ETHERNET_CONFIGURATION, (), '', 'B 4B 4B 4B H'))

    def get_ethernet_status(self):
        """
        Returns the status of the Ethernet Extension.
        
        ``mac_address``, ``ip``, ``subnet_mask`` and ``gateway`` are given as an array.
        The first element of the array is the least significant byte of the address.
        
        ``rx_count`` and ``tx_count`` are the number of bytes that have been
        received/send since last restart.
        
        ``hostname`` is the currently used hostname.
        
        .. versionadded:: 2.1.0$nbsp;(Firmware)
        """
        return GetEthernetStatus(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_ETHERNET_STATUS, (), '', '6B 4B 4B 4B I I 32s'))

    def set_ethernet_hostname(self, hostname):
        """
        Sets the hostname of the Ethernet Extension. The hostname will be displayed 
        by access points as the hostname in the DHCP clients table.
        
        Setting an empty String will restore the default hostname.
        
        The current hostname can be discovered with :func:`GetEthernetStatus`.
        
        .. versionadded:: 2.1.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_ETHERNET_HOSTNAME, (hostname,), '32s', '')

    def set_ethernet_mac_address(self, mac_address):
        """
        Sets the MAC address of the Ethernet Extension. The Ethernet Extension should
        come configured with a valid MAC address, that is also written on a
        sticker of the extension itself.
        
        The MAC address can be read out again with :func:`GetEthernetStatus`.
        
        .. versionadded:: 2.1.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_ETHERNET_MAC_ADDRESS, (mac_address,), '6B', '')

    def set_ethernet_websocket_configuration(self, sockets, port):
        """
        Sets the Ethernet WebSocket configuration. The first parameter sets the number of socket
        connections that are reserved for WebSockets. The range is 0-7. The connections
        are shared with the plain sockets. Example: If you set the connections to 3,
        there will be 3 WebSocket and 4 plain socket connections available.
        
        The second parameter is the port for the WebSocket connections. The port can
        not be the same as the port for the plain socket connections.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the Ethernet configuration.
        
        The default values are 3 for the socket connections and 4280 for the port.
        
        .. versionadded:: 2.2.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_ETHERNET_WEBSOCKET_CONFIGURATION, (sockets, port), 'B H', '')

    def get_ethernet_websocket_configuration(self):
        """
        Returns the configuration as set by :func:`SetEthernetConfiguration`.
        
        .. versionadded:: 2.2.0$nbsp;(Firmware)
        """
        return GetEthernetWebsocketConfiguration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_ETHERNET_WEBSOCKET_CONFIGURATION, (), '', 'B H'))

    def set_ethernet_authentication_secret(self, secret):
        """
        Sets the Ethernet authentication secret. The secret can be a string of up to 64
        characters. An empty string disables the authentication.
        
        See the :ref:`authentication tutorial <tutorial_authentication>` for more
        information.
        
        The secret is stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the Ethernet authentication secret.
        
        The default value is an empty string (authentication disabled).
        
        .. versionadded:: 2.2.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_ETHERNET_AUTHENTICATION_SECRET, (secret,), '64s', '')

    def get_ethernet_authentication_secret(self):
        """
        Returns the authentication secret as set by :func:`SetEthernetAuthenticationSecret`.
        
        .. versionadded:: 2.2.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_ETHERNET_AUTHENTICATION_SECRET, (), '', '64s')

    def set_wifi_authentication_secret(self, secret):
        """
        Sets the WIFI authentication secret. The secret can be a string of up to 64
        characters. An empty string disables the authentication.
        
        See the :ref:`authentication tutorial <tutorial_authentication>` for more
        information.
        
        The secret is stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the WIFI authentication secret.
        
        The default value is an empty string (authentication disabled).
        
        .. versionadded:: 2.2.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI_AUTHENTICATION_SECRET, (secret,), '64s', '')

    def get_wifi_authentication_secret(self):
        """
        Returns the authentication secret as set by :func:`SetWifiAuthenticationSecret`.
        
        .. versionadded:: 2.2.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI_AUTHENTICATION_SECRET, (), '', '64s')

    def get_connection_type(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CONNECTION_TYPE, (), '', 'B')

    def is_wifi2_present(self):
        """
        Returns *true* if a WIFI Extension 2.0 is available to be used by the Master
        Brick.
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_WIFI2_PRESENT, (), '', '?')

    def start_wifi2_bootloader(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_START_WIFI2_BOOTLOADER, (), '', 'b')

    def write_wifi2_flash(self, data, length):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_WRITE_WIFI2_FLASH, (data, length), '60B B', 'b')

    def read_wifi2_flash(self, length_in):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return ReadWifi2Flash(*self.ipcon.send_request(self, BrickMaster.FUNCTION_READ_WIFI2_FLASH, (length_in,), 'B', '60B B'))

    def set_wifi2_authentication_secret(self, secret):
        """
        Sets the WIFI authentication secret. The secret can be a string of up to 64
        characters. An empty string disables the authentication.
        
        See the :ref:`authentication tutorial <tutorial_authentication>` for more
        information.
        
        The secret is stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        
        It is recommended to use the Brick Viewer to set the WIFI authentication secret.
        
        The default value is an empty string (authentication disabled).
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_AUTHENTICATION_SECRET, (secret,), '64s', '')

    def get_wifi2_authentication_secret(self):
        """
        Returns the authentication secret as set by :func:`SetWifi2AuthenticationSecret`.
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_AUTHENTICATION_SECRET, (), '', '64s')

    def set_wifi2_configuration(self, port, websocket_port, website_port, phy_mode, sleep_mode, website):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_CONFIGURATION, (port, websocket_port, website_port, phy_mode, sleep_mode, website), 'H H H B B B', '')

    def get_wifi2_configuration(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return GetWifi2Configuration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_CONFIGURATION, (), '', 'H H H B B B'))

    def get_wifi2_status(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return GetWifi2Status(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_STATUS, (), '', '? B 4B 4B 4B 6B I I b ? 4B 4B 4B 6B I I B'))

    def set_wifi2_client_configuration(self, enable, ssid, ip, subnet_mask, gateway, mac_address, bssid):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_CLIENT_CONFIGURATION, (enable, ssid, ip, subnet_mask, gateway, mac_address, bssid), '? 32s 4B 4B 4B 6B 6B', '')

    def get_wifi2_client_configuration(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return GetWifi2ClientConfiguration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_CLIENT_CONFIGURATION, (), '', '? 32s 4B 4B 4B 6B 6B'))

    def set_wifi2_client_hostname(self, hostname):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_CLIENT_HOSTNAME, (hostname,), '32s', '')

    def get_wifi2_client_hostname(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_CLIENT_HOSTNAME, (), '', '32s')

    def set_wifi2_client_password(self, password):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_CLIENT_PASSWORD, (password,), '64s', '')

    def get_wifi2_client_password(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_CLIENT_PASSWORD, (), '', '64s')

    def set_wifi2_ap_configuration(self, enable, ssid, ip, subnet_mask, gateway, auth, hidden, channel, mac_address):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_AP_CONFIGURATION, (enable, ssid, ip, subnet_mask, gateway, auth, hidden, channel, mac_address), '? 32s 4B 4B 4B B ? B 6B', '')

    def get_wifi2_ap_configuration(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return GetWifi2APConfiguration(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_AP_CONFIGURATION, (), '', '? 32s 4B 4B 4B B ? B 6B'))

    def set_wifi2_ap_password(self, password):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_SET_WIFI2_AP_PASSWORD, (password,), '64s', '')

    def get_wifi2_ap_password(self):
        """
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_AP_PASSWORD, (), '', '64s')

    def save_wifi2_configuration(self):
        """
        Call this function to actually save configuration
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_SAVE_WIFI2_CONFIGURATION, (), '', 'B')

    def get_wifi2_firmware_version(self):
        """
        Returns the current version of the WIFI Extension 2.0 firmware (major, minor, revision).
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_WIFI2_FIRMWARE_VERSION, (), '', '3B')

    def enable_wifi2_status_led(self):
        """
        Turns the green status LED of the WIFI Extension 2.0 on.
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_ENABLE_WIFI2_STATUS_LED, (), '', '')

    def disable_wifi2_status_led(self):
        """
        Turns the green status LED of the WIFI Extension 2.0 off.
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_DISABLE_WIFI2_STATUS_LED, (), '', '')

    def is_wifi2_status_led_enabled(self):
        """
        Returns *True* if the green status LED of the WIFI Extension 2.0 is turned on.
        
        .. versionadded:: 2.4.0$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_WIFI2_STATUS_LED_ENABLED, (), '', '?')

    def enable_status_led(self):
        """
        Enables the status LED.
        
        The status LED is the blue LED next to the USB connector. If enabled is is
        on and it flickers if data is transfered. If disabled it is always off.
        
        The default state is enabled.
        
        .. versionadded:: 2.3.2$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_ENABLE_STATUS_LED, (), '', '')

    def disable_status_led(self):
        """
        Disables the status LED.
        
        The status LED is the blue LED next to the USB connector. If enabled is is
        on and it flickers if data is transfered. If disabled it is always off.
        
        The default state is enabled.
        
        .. versionadded:: 2.3.2$nbsp;(Firmware)
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_DISABLE_STATUS_LED, (), '', '')

    def is_status_led_enabled(self):
        """
        Returns *true* if the status LED is enabled, *false* otherwise.
        
        .. versionadded:: 2.3.2$nbsp;(Firmware)
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_IS_STATUS_LED_ENABLED, (), '', '?')

    def get_protocol1_bricklet_name(self, port):
        """
        Returns the firmware and protocol version and the name of the Bricklet for a
        given port.
        
        This functions sole purpose is to allow automatic flashing of v1.x.y Bricklet
        plugins.
        """
        return GetProtocol1BrickletName(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_PROTOCOL1_BRICKLET_NAME, (port,), 'c', 'B 3B 40s'))

    def get_chip_temperature(self):
        """
        Returns the temperature in °C/10 as measured inside the microcontroller. The
        value returned is not the ambient temperature!
        
        The temperature is only proportional to the real temperature and it has an
        accuracy of +-15%. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Brick. Calling this function
        on a Brick inside of a stack will reset the whole stack.
        
        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickMaster.FUNCTION_RESET, (), '', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Brick is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be '0'-'8' (stack position).
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickMaster.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Master = BrickMaster # for backward compatibility
