# -*- coding: utf-8 -*-

# brickv config

import logging

LOGGING_LEVEL = logging.ERROR
LOGGING_FORMAT = "%(asctime)s <%(levelname)s> <%(filename)s:%(lineno)s> %(message)s"
LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"

BRICKV_VERSION = "2.2.4"

HOST_INFO_COUNT = 10

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 4223

DEFAULT_USE_AUTHENTICATION = False
DEFAULT_SECRET = ''
DEFAULT_REMEMBER_SECRET = False

# host|port|use_authentication|remember_secret|secret
DEFAULT_HOST_INFO = 'localhost|4223|0|0|'
