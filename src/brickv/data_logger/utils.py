# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

utils.py: Util classes for the data logger

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

#### skip here for brick-logger ####

import csv  # CSV_Writer
from datetime import datetime  # CSV_Data
import os  # CSV_Writer
from shutil import copyfile
import sys  # CSV_Writer
from threading import Timer
import time  # Writer Thread
import math
import locale

if 'merged_data_logger_modules' not in globals():
    from brickv.data_logger.event_logger import EventLogger

def utf8_strftime(timestamp, fmt):
    return datetime.fromtimestamp(timestamp).strftime(fmt)

def timestamp_to_de(timestamp):
    return utf8_strftime(timestamp, '%d.%m.%Y %H:%M:%S')

def timestamp_to_de_msec(timestamp):
    return timestamp_to_de(timestamp) + ',' + ('%.3f' % math.modf(timestamp)[0])[2:]

def timestamp_to_us(timestamp):
    return utf8_strftime(timestamp, '%m/%d/%Y %H:%M:%S')

def timestamp_to_us_msec(timestamp):
    return timestamp_to_us(timestamp) + '.' + ('%.3f' % math.modf(timestamp)[0])[2:]

def timestamp_to_iso(timestamp, milli=False):
    """
    Format a timestamp in ISO 8601 standard
    ISO 8601 = YYYY-MM-DDThh:mm:ss.fff+tz:tz
               2014-09-10T14:12:05.563+02:00
    """

    if time.localtime().tm_isdst and time.daylight:
        offset = -time.altzone / 60
    else:
        offset = -time.timezone / 60

    tz = '%02d:%02d' % (abs(offset) / 60, abs(offset) % 60)

    if offset < 0:
        tz = '-' + tz
    else:
        tz = '+' + tz

    if milli:
        ms = '.' + ('%.3f' % math.modf(timestamp)[0])[2:]
    else:
        ms = ''

    return utf8_strftime(timestamp, '%Y-%m-%dT%H:%M:%S') + ms + tz

def timestamp_to_iso_msec(timestamp):
    return timestamp_to_iso(timestamp, True)

def timestamp_to_unix(timestamp):
    return str(int(timestamp))

def timestamp_to_unix_msec(timestamp):
    return '%.3f' % timestamp

def timestamp_to_strftime(timestamp, time_format):
    try:
        return utf8_strftime(timestamp, time_format)
    except Exception as e:
        return 'Error: ' + str(e).replace('\n', ' ')

class DataLoggerException(Exception):
    # Error Codes
    DL_MISSING_ARGUMENT = -1  # Missing Arguments in Config File
    DL_FAILED_VALIDATION = -2  # Validation found errors in the configuration file
    DL_CRITICAL_ERROR = -42  # For all other critical errors

    def __init__(self, err_code=DL_CRITICAL_ERROR, desc="No Description!"):
        self.value = err_code
        self.description = desc

    def __str__(self):
        return str("ERROR[DL" + str(self.value) + "]: " + str(self.description))


'''
/*---------------------------------------------------------------------------
                                CSVData
 ---------------------------------------------------------------------------*/
 '''


class CSVData(object):
    """
    This class is used as a temporary save spot for all csv relevant data.
    """

    def __init__(self, timestamp, name, uid, var_name, raw_data, var_unit):
        """
        timestamp -- time data was
        name      -- display name of Brick(let)
        uid       -- UID of Brick(let)
        var_name  -- name of logged value
        raw_data  -- logged value
        var_unit  -- unit of logged value
        """
        self.timestamp = timestamp # datatime object
        self.name = name
        self.uid = uid
        self.var_name = var_name
        self.raw_data = raw_data
        self.var_unit = var_unit

    def __str__(self):
        """
        Simple Debug function for easier display of the object.
        """
        return "[TIME=" + str(self.timestamp) + \
               ";NAME=" + str(self.name) + \
               ";UID=" + str(self.uid) + \
               ";VAR=" + str(self.var_name) + \
               ";RAW=" + str(self.raw_data) + \
               ";UNIT=" + str(self.var_unit) + "]"

'''
/*---------------------------------------------------------------------------
                                LoggerTimer
 ---------------------------------------------------------------------------*/
 '''


class LoggerTimer(object):
    """This class provides a timer with a repeat functionality based on a interval"""

    def __init__(self, interval, func_name, var_name, device):
        """
        interval -- the repeat interval in seconds
        func -- the function which will be called
        """
        self.exit_flag = False
        if interval < 0:
            interval = 0

        self._interval = interval # in seconds
        self._func_name = func_name
        self._var_name = var_name
        self._device = device
        self._was_started = False
        self._t = Timer(self._interval, self._loop)

    def _loop(self):
        """Runs the <self._func_name> function every <self._interval> seconds"""
        start = time.time() # FIXME: use time.monotonic() in Python 3
        getattr(self._device, self._func_name)(self._var_name)
        elapsed = max(time.time() - start, 0) # FIXME: use time.monotonic() in Python 3
        self.cancel()
        if self.exit_flag:
            return
        self._t = Timer(max(self._interval - elapsed, 0), self._loop)
        self.start()

    def start(self):
        """Starts the timer if <self._interval> is not 0 otherwise the
           timer will be canceled
        """
        if self._interval == 0:
            self.cancel()
            return

        self._t.start()
        self._was_started = True

    def stop(self):
        self.exit_flag = True
        self._was_started = False

    def cancel(self):
        self._t.cancel()

    def join(self):
        if self._interval == 0:  # quick fix for no timer.start()
            return

        if self._was_started:
            self._t.join()


"""
/*---------------------------------------------------------------------------
                                Utilities
 ---------------------------------------------------------------------------*/
"""


class Utilities(object):
    """
    This class provides some utility functions for the data logger project
    """

    def parse_to_int(string):
        """
        Returns an integer out of a string.
        0(Zero) -- if string is negative or an exception raised during the converting process.
        """
        try:
            ret = int(float(string))
            if ret < 0:
                ret = 0
            return ret
        except ValueError:
            # EventLogger.debug("DataLogger.parse_to_int(" + string + ") could not be parsed! Return 0 for the Timer.")
            return 0

    parse_to_int = staticmethod(parse_to_int)

    def parse_to_bool(bool_string):
        """
        Returns a 'True', if the string is equals to 'true' or 'True'.
        Otherwise it'll return a False
        """
        if bool_string == "true" or bool_string == "True" or bool_string == "TRUE":
            return True
        else:
            return False

    parse_to_bool = staticmethod(parse_to_bool)

    def parse_device_name(device_name):
        tmp = device_name.split("[")
        if len(tmp) == 1:
            return tmp[0], None

        device = tmp[0][:len(tmp[0]) - 1]
        uid = tmp[1][:len(tmp[1]) - 1]

        return device, uid

    parse_device_name = staticmethod(parse_device_name)

    def replace_right(source, target, replacement, replacements=None):
        return replacement.join(source.rsplit(target, replacements))

    replace_right = staticmethod(replace_right)

    def check_file_path_exists(file_path):
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path == "" or dir_path is None:
                if file_path == "" or file_path is None:
                    # no filename - dir
                    return False
                else:
                    # filename - but no dir
                    return True
            elif os.path.isdir(dir_path):
                # dir found
                return True
            return False
        except Exception:
            return False

    check_file_path_exists = staticmethod(check_file_path_exists)

    def is_valid_string(string_value, min_length=0):
        """
        Returns True if 'string_value' is of type str and has at least a size of
        'min_length'
        """
        if not isinstance(string_value, str) or len(string_value) < min_length:
            return False
        return True

    is_valid_string = staticmethod(is_valid_string)


'''
/*---------------------------------------------------------------------------
                                CSVWriter
 ---------------------------------------------------------------------------*/
 '''


class CSVWriter(object):
    """
    This class provides the actual open/write functions, which are used by the CSVWriterJob class to write logged data into
    a CSV formatted file.
    """

    def __init__(self, file_path, max_file_count=1, max_file_size=0):
        """
        file_path = Path to the csv file
        """
        self._file_path = file_path
        # check if file path exists
        if not Utilities.check_file_path_exists(self._file_path):
            raise Exception("File Path not found! -> " + str(self._file_path))

        self._raw_file = None
        self._csv_file = None

        if max_file_size < 0:
            max_file_size = 0
        self._file_size = max_file_size

        # HINT: create always at least 1 backup file!
        if max_file_count < 1:
            max_file_count = 1

        self._file_count = max_file_count

        self._open_file_A()

    def _open_file_A(self):
        """Opens a file in append mode."""

        # newline problem solved + import sys
        if sys.version_info >= (3, 0, 0):
            self._raw_file = open(self._file_path, 'a', newline='')  # FIXME append or write?!
        else:
            self._raw_file = open(self._file_path, 'ab')

        self._csv_file = csv.writer(self._raw_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # if the file is empty, create a csv header
        if self._file_is_empty():
            self._write_header()

    def _file_is_empty(self):
        """
        Simple check if the file is empty.
        Return:
            True  - File is empty or missing
            False - File is not empty
        """
        try:
            if os.stat(self._file_path).st_size > 0:
                return False
            else:
                return True
        except OSError:
            return True

    def _write_header(self):
        """Writes a csv header into the file"""
        if not self._file_is_empty():
            EventLogger.debug("File is not empty")
            return

        EventLogger.debug("CSVWriter._write_header() - done")
        self._csv_file.writerow(["TIME"] + ["NAME"] + ["UID"] + ["VAR"] + ["RAW"] + ["UNIT"])
        self._raw_file.flush()

    def write_data_row(self, csv_data):
        """
        Write a row into the csv file.
        Return:
            True  - Row was written into thee file
            False - Row was not written into the File
        """
        if self._raw_file is None or self._csv_file is None:
            return False

        self._csv_file.writerow([csv_data.timestamp] + [csv_data.name] + [csv_data.uid] + [csv_data.var_name] + [str(csv_data.raw_data)] + [csv_data.var_unit])
        self._raw_file.flush()

        if self._file_size > 0:
            self._rolling_file()

        return True

    def set_file_path(self, new_file_path):
        """
        Sets a new file path.
        Return:
            True  - File path was updated and successfully opened
            False - File path could not be updated or opened
        """
        if not self.close_file():
            return False

        self._file_path = new_file_path
        self._open_file_A()
        return True

    def reopen_file(self):
        """
        Tries to reopen a file, if the file was manually closed.
        Return:
            True  - File could be reopened
            False - File could not be reopened
        """
        if self._raw_file is not None and self._csv_file is not None:
            return False

        self._open_file_A()
        return True

    def close_file(self):
        """
        Tries to close the current file.
        Return:
            True  - File was close
            False - File could not be closed
        """
        if self._raw_file is None or self._csv_file is None:
            return False
        try:
            self._raw_file.close()
            self._csv_file = None
            self._raw_file = None
            return True

        except ValueError:
            return False

    def _rolling_file(self):
        f_size = os.path.getsize(self._file_path)
        if f_size > self._file_size:
            # self.set_file_path(self._create_new_file_name(self._file_path))
            EventLogger.info(
                "Max Filesize(" + "%.3f" % (self._file_size / 1024.0 / 1024.0) + " MB) reached! Rolling Files...")
            self._roll_files()

    # FIXME: only files with a . are working!
    def _roll_files(self):
        i = self._file_count

        self.close_file()

        while True:
            if i == 0:
                # first file reached
                break

            tmp_file_name = Utilities.replace_right(self._file_path, ".", "(" + str(i) + ").", 1)

            if os.path.exists(tmp_file_name):
                if i == self._file_count:
                    # max file count -> delete
                    os.remove(tmp_file_name)
                    EventLogger.debug("Rolling Files... removed File(" + str(i) + ")")

                else:
                    # copy file and remove old
                    copyfile(tmp_file_name, Utilities.replace_right(self._file_path, ".", "(" + str(i + 1) + ").", 1))
                    EventLogger.debug("Rolling Files... copied File(" + str(i) + ") into (" + str(i + 1) + ")")
                    os.remove(tmp_file_name)

            i -= 1

        if self._file_count != 0:
            copyfile(self._file_path, Utilities.replace_right(self._file_path, ".", "(" + str(1) + ").", 1))
            EventLogger.debug("Rolling Files... copied original File into File(1)")
        os.remove(self._file_path)
        self._open_file_A()
