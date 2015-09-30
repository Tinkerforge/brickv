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

import codecs
import json

from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.utils import DataLoggerException, Utilities
from brickv.data_logger.loggable_devices import Identifier as Idf

def load_and_validate_config(filename):
    EventLogger.info("Loading config file from '{0}'".format(filename))

    with codecs.open(filename, 'r', 'UTF-8') as f:
        try:
            config = json.load(f)
        except ValueError as e:
            EventLogger.critical("Could not parse config file as JSON: " + str(e))
            return None

    if not ConfigValidator(config).validate():
        return None

    return config

""""
/*---------------------------------------------------------------------------
                                ConfigValidator
 ---------------------------------------------------------------------------*/
"""


class ConfigValidator(object):
    """
    This class validates the (JSON) config file
    """
    MIN_INTERVAL = 0

    def __init__(self, config):
        self._error_count = 0
        self._config = config

        # FIXME: dont access the config before its validated. also this code should not be here
        # but somewhere else. it has nothing to do with validation
        #file_count = self._config['data']['csv']['file_count']
        #file_size = self._config['data']['csv']['file_size']
        #self._log_space_counter = LogSpaceCounter(file_count, file_size)

    def _report_error(self, message):
        self._error_count += 1
        EventLogger.critical(message)

    def validate(self):
        """
        This function performs the validation of the various sections of the JSON
        configuration file
        """
        EventLogger.info("Validating config file")

        self._validate_hosts()
        self._validate_data()
        self._validate_events()
        self._validate_devices_section()

        if self._error_count > 0:
            EventLogger.critical("Validation found {0} errors".format(self._error_count))
        else:
            EventLogger.info("Validation successful")

        #logging_time = self._log_space_counter.calculate_time()
        #if self._log_space_counter.file_size != 0:
        #    EventLogger.info("Logging time until old data will be overwritten.")
        #    EventLogger.info("Days: " + str(logging_time[0]) +
        #                     " Hours: " + str(logging_time[1]) +
        #                     " Minutes: " + str(logging_time[2]) +
        #                     " Seconds: " + str(logging_time[3]))
        #EventLogger.info("Will write about " + str(
        #    int(self._log_space_counter.lines_per_second + 0.5)) + " lines per second into the log-file.")

        return self._error_count == 0

    def _validate_hosts(self):
        """
        This function validates the hosts section of the configuration
        """
        try:
            hosts = self._config['hosts']
        except KeyError:
            self._report_error('Config has no "hosts" section')
            return

        if not isinstance(hosts, dict):
            self._report_error('"hosts" section is not a dictionary')
            return

        try:
            hosts['default']
        except KeyError:
            self._report_error('Config has no default host')

        for host_id, host in hosts.items():
            try:
                name = host['name']
            except KeyError:
                self._report_error('Host with ID "{0}" has no name'.format(host_id))
            else:
                if not isinstance(name, basestring):
                    self._report_error('Name of host with ID "{0}" is not a string'.format(host_id))
                elif len(name) == 0:
                    self._report_error('Name of host with ID "{0}" is empty'.format(host_id))

            try:
                port = host['port']
            except KeyError:
                self._report_error('Host with ID "{0}" has no port'.format(host_id))
            else:
                if not isinstance(port, int):
                    self._report_error('Port of host with ID "{0}" is not an int'.format(host_id))
                elif port < 1 or port > 65535:
                    self._report_error('Port of host with ID "{0}" is out-of-range'.format(host_id))

    def _validate_data(self):
        """
        This function validates the data section out of the configuration
        """
        try:
            data = self._config['data']
        except KeyError:
            self._report_error('Config has no "data" section')
            return

        try:
            time_format = data['time_format']
        except KeyError:
            self._report_error('"data" section has no "time_format" member')
        else:
            if not isinstance(time_format, basestring):
                self._report_error('"data/time_format" is not a string')
            elif time_format not in ['de', 'us', 'iso', 'unix']:
                self._report_error('Invalid "data/time_format" value: {0}'.format(time_format))

        self._validate_data_csv()

    def _validate_data_csv(self):
        """
        This function validates the data/csv section out of the configuration
        """
        try:
            csv = self._config['data']['csv']
        except KeyError:
            self._report_error('Config has no "data/csv" section')
            return

        try:
            enabled = csv['enabled']
        except KeyError:
            self._report_error('"data/csv" section has no "enabled" member')
        else:
            if not isinstance(enabled, bool):
                self._report_error('"data/csv/enabled" is not an bool')

        try:
            file_name = csv['file_name']
        except KeyError:
            self._report_error('"data/csv" section has no "file_name" member')
        else:
            if not isinstance(file_name, basestring):
                self._report_error('"data/csv/file_name" is not an string')
            elif len(file_name) == 0:
                self._report_error('"data/csv/file_name" is empty')

        try:
            file_count = csv['file_count']
        except KeyError:
            self._report_error('"data/csv" section has no "file_count" member')
        else:
            if not isinstance(file_count, int):
                self._report_error('"data/csv/file_count" is not an integer')
            elif file_count < 1 or file_count > 65535:
                self._report_error('"data/csv/file_count" is out-of-range')

        try:
            file_size = csv['file_size']
        except KeyError:
            self._report_error('"data/csv" section has no "file_size" member')
        else:
            if not isinstance(file_size, int):
                self._report_error('"data/csv/file_size" is not an integer')
            elif file_size < 0 or file_size > 2097152:
                self._report_error('"data/csv/file_size" is out-of-range')

    def _validate_events(self):
        """
        This function validates the events section out of the configuration
        """
        try:
            events = self._config['events']
        except KeyError:
            self._report_error('Config has no "events" section')
            return

        try:
            time_format = events['time_format']
        except KeyError:
            self._report_error('"events" section has no "time_format" member')
        else:
            if not isinstance(time_format, basestring):
                self._report_error('"events/time_format" is not a string')
            elif time_format not in ['de', 'us', 'iso', 'unix']:
                self._report_error('Invalid "events/time_format" value: {0}'.format(time_format))

        self._validate_events_log()

    def _validate_events_log(self):
        """
        This function validates the events/log section out of the configuration
        """
        try:
            log = self._config['events']['log']
        except KeyError:
            self._report_error('Config has no "events/log" section')
            return

        try:
            enabled = log['enabled']
        except KeyError:
            self._report_error('"events/log" section has no "enabled" member')
        else:
            if not isinstance(enabled, bool):
                self._report_error('"events/log/enabled" is not an bool')

        try:
            file_name = log['file_name']
        except KeyError:
            self._report_error('"events/log" section has no "file_name" member')
        else:
            if not isinstance(file_name, basestring):
                self._report_error('"events/log/file_name" is not an string')
            elif len(file_name) == 0:
                self._report_error('"events/log/file_name" is empty')

        try:
            level = log['level']
        except KeyError:
            self._report_error('"events/log" section has no "level" member')
        else:
            if not isinstance(level, basestring):
                self._report_error('"events/log/level" is not an integer')
            elif level not in ['debug', 'info', 'warning', 'error', 'critical']:
                self._report_error('Invalid "events/log/level" value: {0}'.format(level))

    def _validate_devices_section(self):
        """
            This function validates the devices out of the configuration file
        :return:
        """
        try:
            devices = self._config['devices']
        except KeyError:
            self._report_error('Config has no devices section')
            return

        device_definitions = Idf.DEVICE_DEFINITIONS

        for device in devices:
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

            # host
            try:
                host = device['host']
            except KeyError:
                self._report_error('Device "{0}" with UID "{1}" has no host'.format(device[Idf.DD_NAME], device[Idf.DD_UID]))
            else:
                if not isinstance(host, basestring):
                    self._report_error('Host for device "{0}" with UID "{1}" is not a string'.format(device[Idf.DD_NAME], device[Idf.DD_UID]))

                if len(host) == 0:
                    self._report_error('Host for device "{0}" with UID "{1}" is empty'.format(device[Idf.DD_NAME], device[Idf.DD_UID]))

                if host != 'default':
                    self._report_error('Host for device "{0}" with UID "{1}" is not set to "default"'.format(device[Idf.DD_NAME], device[Idf.DD_UID]))

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

                    #if interval > 0:
                    #    self._log_space_counter.add_lines_per_second(interval * logged_values)

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
