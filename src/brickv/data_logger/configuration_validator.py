# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

configuration_validator.py: Data logger configuration validator

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

"""
/*---------------------------------------------------------------------------
                                ConfigurationReader
 ---------------------------------------------------------------------------*/
 """
import codecs  # ConfigurationReader to read the file in correct encoding
import json

from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.utils import DataLoggerException, Utilities
from brickv.data_logger.loggable_devices import Identifier as Idf


class ConfigurationReader(object):
    """
    This class provides the read-in functionality for the Data Logger configuration file
    """
    GENERAL_SECTION = "GENERAL"
    GENERAL_LOG_TO_FILE = "log_to_file"
    GENERAL_PATH_TO_FILE = "path_to_file"
    GENERAL_LOG_COUNT = "log_count"
    GENERAL_LOG_FILE_SIZE = "max_logged_file_size"
    GENERAL_HOST = "host"
    GENERAL_PORT = "port"
    GENERAL_EVENTLOG_PATH = "event_path_to_eventfile"
    GENERAL_EVENTLOG_TO_CONSOLE = "event_log_to_console"
    GENERAL_EVENTLOG_TO_FILE = "event_log_to_file"
    GENERAL_EVENTLOG_LEVEL = "event_log_level"

    DEVICES_SECTION = Idf.DEVICES

    def __init__(self, path_to_config=None, configuration=None):
        """
        pathToConfig -- path to the json configuration file
        OR
        configuration -- the configuration itself
        """
        self._configuration = Configuration()
        self._readConfigErr = 0  # Errors which occure during readin

        if path_to_config is None and configuration is None:
            EventLogger.critical(
                "ConfigurationReader needs a path to the configuration file or an actual configuration")
            return

        if path_to_config is not None:
            self.fileName = path_to_config
            self._read_json_config_file()

        if configuration is not None:
            if isinstance(configuration, Configuration):
                self._configuration = configuration
            else:
                self.map_dict_to_config(configuration)

        validator = ConfigurationValidator(self._configuration)
        validator._error_count += self._readConfigErr
        validator.validate()

    def _read_json_config_file(self):
        with codecs.open(self.fileName, 'r', 'UTF-8') as content_file:
            try:
                json_structure = json.load(content_file)
            except ValueError as e:
                EventLogger.critical("Cant parse the configuration file: " + str(e))
                return

        # Load sections out of the json structure
        try:
            self._configuration._general = json_structure[ConfigurationReader.GENERAL_SECTION]
        except KeyError:
            EventLogger.critical("json configuration file has no [" + ConfigurationReader.GENERAL_SECTION + "] section")
            self._readConfigErr += 1

        self._configuration._devices = prevent_key_error(json_structure, ConfigurationReader.DEVICES_SECTION)

    def map_dict_to_config(self, json_dict):
        self._configuration._general = prevent_key_error(json_dict, ConfigurationReader.GENERAL_SECTION)
        self._configuration._devices = prevent_key_error(json_dict, ConfigurationReader.DEVICES_SECTION)


""""
/*---------------------------------------------------------------------------
                                ConfigurationValidator
 ---------------------------------------------------------------------------*/
"""


class ConfigurationValidator(object):
    """
    This class validates the (json) configuration file
    """
    MIN_INTERVAL = 0

    def __init__(self, config_file):
        self.CR = ConfigurationReader  # alias for the ConfigurationReader

        self.json_config = config_file

        self._error_count = 0
        file_count = self.json_config._general[self.CR.GENERAL_LOG_COUNT]
        file_size = self.json_config._general[self.CR.GENERAL_LOG_FILE_SIZE]

        self._log_space_counter = LogSpaceCounter(file_count, file_size)

    def validate(self):
        """
        This function performs the validation of the various sections of the json
        configuration file
        """
        EventLogger.info("Started configuration file validation")
        self.validate_general_section()
        self.validate_devices_section()
        EventLogger.info("Validation ends with [" + str(self._error_count) + "] errors")

        logging_time = self._log_space_counter.calculate_time()
        if self._log_space_counter.file_size != 0:
            EventLogger.info("Logging time until old data will be overwritten.")
            EventLogger.info("Days: " + str(logging_time[0]) +
                             " Hours: " + str(logging_time[1]) +
                             " Minutes: " + str(logging_time[2]) +
                             " Seconds: " + str(logging_time[3]))
        EventLogger.info("Will write about " + str(
            int(self._log_space_counter.lines_per_second + 0.5)) + " lines per second into the log-file.")

        if self._error_count != 0:
            raise DataLoggerException(DataLoggerException.DL_FAILED_VALIDATION, "Validation process found some errors")

    def validate_general_section(self):
        """
        This function validates the general section out of the configuration
        """
        global_section = self.json_config._general

        # self.CR.GENERAL_HOST ip address
        host = global_section[self.CR.GENERAL_HOST]
        if host is None or len(host) == 0:
            EventLogger.critical(
                self._generate_device_error_message(uid="", tier_array=[self.CR.GENERAL_SECTION, self.CR.GENERAL_HOST],
                                                    msg="invalid host"))

        # self.CR.GENERAL_PORT port number
        port = global_section[self.CR.GENERAL_PORT]
        if not Utilities.is_valid_string(port, 1) and not (0 < port <= 65535):
            EventLogger.critical(
                self._generate_device_error_message(uid="", tier_array=[self.CR.GENERAL_SECTION, self.CR.GENERAL_PORT],
                                                    msg="port should be an integer 0-65535"))

        # --- Datalog file ---------------------------------------------  
        # self.CR.GENERAL_LOG_TO_FILE should be a bool and if its True then
        # self.CR.GENERAL_LOG_TO_FILE should be a string and a valid path
        if not type(global_section[self.CR.GENERAL_LOG_TO_FILE]) == bool:
            EventLogger.critical(
                self._generate_device_error_message(uid="",
                                                    tier_array=[self.CR.GENERAL_SECTION, self.CR.GENERAL_LOG_TO_FILE],
                                                    msg="should be a boolean"))
        else:
            if global_section[self.CR.GENERAL_LOG_TO_FILE]:
                if not Utilities.check_file_path_exists(global_section[self.CR.GENERAL_PATH_TO_FILE]):
                    EventLogger.critical(
                        self._generate_device_error_message(uid="", tier_array=[self.CR.GENERAL_SECTION,
                                                                                self.CR.GENERAL_PATH_TO_FILE],
                                                            msg="path is not reachable"))

        # self.CR.GENERAL_PATH_TO_FILE
        if not Utilities.is_valid_string(global_section[self.CR.GENERAL_PATH_TO_FILE], 1):
            EventLogger.critical(
                self._generate_device_error_message(uid="",
                                                    tier_array=[self.CR.GENERAL_SECTION, self.CR.GENERAL_PATH_TO_FILE],
                                                    msg="should be a path to the file where the data will be saved"))

        # self.CR.GENERAL_LOG_COUNT and GENERAL_LOG_FILE_SIZE
        count = global_section[self.CR.GENERAL_LOG_COUNT]
        if not isinstance(count, int) and (not isinstance(count, float)):
            EventLogger.critical(
                self._generate_device_error_message(uid="",
                                                    tier_array=[self.CR.GENERAL_SECTION, self.CR.GENERAL_LOG_COUNT],
                                                    msg="should be a int or float"))
        size = global_section[self.CR.GENERAL_LOG_FILE_SIZE]
        if not isinstance(size, int) and (not isinstance(size, float)):
            EventLogger.critical(
                self._generate_device_error_message(uid="",
                                                    tier_array=[self.CR.GENERAL_SECTION, self.CR.GENERAL_LOG_FILE_SIZE],
                                                    msg="should be a int or float"))

        # --- Eventlog file ---------------------------------------------    
        # self.CR.GENERAL_EVENTLOG_TO_FILE should be a bool and if its True then
        # self.CR.GENERAL_EVENTLOG_PATH should be a string and a valid path
        if not type(global_section[self.CR.GENERAL_EVENTLOG_TO_FILE]) == bool:
            EventLogger.critical(
                self._generate_device_error_message(uid="", tier_array=[self.CR.GENERAL_SECTION,
                                                                        self.CR.GENERAL_EVENTLOG_TO_FILE],
                                                    msg="should be a boolean"))
        else:
            if global_section[self.CR.GENERAL_EVENTLOG_TO_FILE]:
                if not Utilities.is_valid_string(global_section[self.CR.GENERAL_EVENTLOG_PATH], 1):
                    EventLogger.critical(self._generate_device_error_message(uid="",
                                                                             tier_array=[self.CR.GENERAL_SECTION,
                                                                                         self.CR.GENERAL_EVENTLOG_PATH],
                                                                             msg="should be a path to the event file"))
                else:
                    if not Utilities.check_file_path_exists(global_section[self.CR.GENERAL_EVENTLOG_PATH]):
                        EventLogger.critical(self._generate_device_error_message(uid="",
                                                                                 tier_array=[self.CR.GENERAL_SECTION,
                                                                                             self.CR.GENERAL_EVENTLOG_PATH],
                                                                                 msg="path is not reachable"))

        if not type(global_section[self.CR.GENERAL_EVENTLOG_TO_CONSOLE]) == bool:
            EventLogger.critical(
                self._generate_device_error_message(uid="", tier_array=[self.CR.GENERAL_SECTION,
                                                                        self.CR.GENERAL_EVENTLOG_TO_CONSOLE],
                                                    msg="should be a boolean"))

    def validate_devices_section(self):
        """
            This function validates the devices out of the configuration file
        :return:
        """
        device_definitions = Idf.DEVICE_DEFINITIONS

        for device in self.json_config._devices:
            # name
            blueprint = device_definitions[device[Idf.DD_NAME]]
            if blueprint is None:
                EventLogger.critical(
                    self._generate_device_error_message(uid=device[Idf.DD_UID],
                                                        tier_array=["general"], msg="no such device available"))
                continue  # next device

            # uid
            if not Utilities.is_valid_string(device[Idf.DD_UID], 1) or device[Idf.DD_UID] == Idf.DD_UID_DEFAULT:
                EventLogger.critical(
                    self._generate_device_error_message(uid=device[Idf.DD_UID],
                                                        tier_array=["general"], msg="the UID from '"+device[Idf.DD_NAME]+"' is invalid"))

            device_values = device[Idf.DD_VALUES]
            blueprint_values = blueprint[Idf.DD_VALUES]
            # values
            for device_value in device_values:
                logged_values = 0
                if device_value not in blueprint_values:
                    EventLogger.critical(
                        self._generate_device_error_message(uid=device[Idf.DD_UID],
                                                            tier_array=["values"],
                                                            msg="invalid value " + str(device_value)))
                else:
                    # interval
                    interval = device_values[device_value][Idf.DD_VALUES_INTERVAL]
                    if not self._is_valid_interval(interval):
                        EventLogger.critical(
                            self._generate_device_error_message(uid=device[Idf.DD_UID],
                                                                tier_array=["values"],
                                                                msg="invalid interval " + str(interval)))
                    # subvalue
                    try:
                        subvalues = device_values[device_value][Idf.DD_SUBVALUES]
                        for value in subvalues:
                            if not type(subvalues[value]) == bool:  # type check for validation
                                EventLogger.critical(
                                    self._generate_device_error_message(
                                        uid=device[Idf.DD_UID],
                                        tier_array=["values"],
                                        msg="invalid type " + str(value)))
                            else:
                                if subvalues[value]:  # value check for "lines per second" calculation
                                    logged_values += 1

                    except KeyError:
                        if interval > 0:  # just one value to log
                            logged_values += 1

                    if interval > 0:
                        self._log_space_counter.add_lines_per_second(interval / 1000 * logged_values)

    def _is_valid_interval(self, integer_value, min_value=0):
        """
        Returns True if the 'integer_value' is of type integer and is not negative
        """
        if not isinstance(integer_value, int) or integer_value < min_value and integer_value != 0:
            return False
        return True

    def _generate_device_error_message(self, uid, tier_array, msg):
        err_msg = "[UID=" + uid + "]"
        for tier in tier_array:
            err_msg += "[" + tier + "]"

        self._error_count += 1
        return err_msg + " - " + msg


""""
/*---------------------------------------------------------------------------
                                LogSpaceCounter
 ---------------------------------------------------------------------------*/
"""


class LogSpaceCounter(object):
    """
    This class provides functions to count the average lines per second
    which will be written into the log file
    """

    def __init__(self, file_count, file_size):
        """
        file_count -- the amount of logfiles
        file_size -- the size of each file
        """
        self.file_count = file_count
        self.file_size = file_size

        self.lines_per_second = 0.0

    def add_lines_per_second(self, lines):
        self.lines_per_second += lines

    def calculate_time(self):
        """
        This function calculates the time where the logger can
        save data without overwriting old ones.

        18k lines -> 1MB
        """
        if self.lines_per_second <= 0 or self.file_size == 0:
            return 0, 0, 0, 0

        max_available_space = (self.file_count + 1) * ((self.file_size / 1024.0) / 1024.0)
        seconds_for_one_MB = 18000.0 / self.lines_per_second

        sec = seconds_for_one_MB * max_available_space * 1.0

        days = int(sec / 86400.0)
        sec -= 86400.0 * days

        hrs = int(sec / 3600.0)
        sec -= 3600.0 * hrs

        mins = int(sec / 60.0)
        sec -= 60.0 * mins

        return days, hrs, mins, int(sec)


""""
/*---------------------------------------------------------------------------
                                Configuration
 ---------------------------------------------------------------------------*/
"""


class Configuration:
    """
    This class contains the information out of the json configuration file split by the
    different categories/sections.
    """

    def __init__(self):
        self._general = {}

        self._devices = []

    def is_empty(self):
        return True if len(self._general) == 0 else False


def prevent_key_error(dict_src, key):
    """
    This function returns an empty array if there is no such
    section in the configuration file
    key -- section key
    """
    result = []
    try:
        result = dict_src[key]
    except KeyError:
        EventLogger.warning("json configuration file has no [" + key + "] section")
    return result
