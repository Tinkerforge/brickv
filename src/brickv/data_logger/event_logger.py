# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

event_logger.py: Main event logger class

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

#---------------------------------------------------------------------------
#                               Event Logger
#---------------------------------------------------------------------------

if 'merged_data_logger_modules' not in globals():
    from PyQt5 import QtCore
    from PyQt5.QtCore import pyqtSignal

import logging
from datetime import datetime

class EventLogger():
    """
        Basic EventLogger class.
    """

    format = "%(asctime)s - %(levelname)8s - %(message)s"
    __loggers = {}

    def __init__(self):
        pass

    def add_logger(logger):
        if logger.name is None or logger.name == "":
            raise Exception("Logger has no Attribute called 'name'!")

        EventLogger.__loggers[logger.name] = logger

    def remove_logger(logger_name):
        if logger_name in EventLogger.__loggers:
            EventLogger.__loggers.pop(logger_name)
            return True

        return False

    # Does not really work as expected >_>
    # def get_logger(logger_name):
    #     if logger_name in EventLogger.__loggers:
    #         return EventLogger.__loggers.get(logger_name)
    #     return None

    def debug(msg, logger_name=None):
        level = logging.DEBUG
        EventLogger._send_message(level, msg, logger_name)

    def info(msg, logger_name=None):
        level = logging.INFO
        EventLogger._send_message(level, msg, logger_name)

    def warn(msg, logger_name=None):
        level = logging.WARN
        EventLogger._send_message(level, msg, logger_name)

    def warning(msg, logger_name=None):
        level = logging.WARNING
        EventLogger._send_message(level, msg, logger_name)

    def error(msg, logger_name=None):
        level = logging.ERROR
        EventLogger._send_message(level, msg, logger_name)

    def critical(msg, logger_name=None):
        level = logging.CRITICAL
        EventLogger._send_message(level, msg, logger_name)

    def log(level, msg, logger_name=None):
        EventLogger._send_message(level, msg, logger_name)

    def _send_message(level, msg, logger_name):
        if logger_name is not None:
            if logger_name in EventLogger.__loggers:
                EventLogger.__loggers[logger_name].log(level, msg)
        else:
            for logger in EventLogger.__loggers.values():
                logger.log(level, msg)

    # static methods
    add_logger = staticmethod(add_logger)
    remove_logger = staticmethod(remove_logger)
    # get_logger = staticmethod(get_logger)
    debug = staticmethod(debug)
    info = staticmethod(info)
    warn = staticmethod(warn)
    warning = staticmethod(warning)
    error = staticmethod(error)
    critical = staticmethod(critical)
    log = staticmethod(log)
    _send_message = staticmethod(_send_message)


class ConsoleLogger(logging.Logger):
    """
    This class outputs the logged debug messages to the console
    """

    def __init__(self, name, log_level):
        logging.Logger.__init__(self, name, log_level)

        # create console handler and set level
        ch = logging.StreamHandler()

        ch.setLevel(log_level)

        # create formatter
        formatter = logging.Formatter(EventLogger.format)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.addHandler(ch)

class FileLogger(logging.Logger):
    """
    This class writes the logged debug messages to a log file
    """

    def __init__(self, name, log_level, filename):
        logging.Logger.__init__(self, name, log_level)

        ch = logging.FileHandler(filename, mode="a")

        ch.setLevel(log_level)

        # create formatter
        formatter = logging.Formatter(EventLogger.format)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.addHandler(ch)

        self.info("###### NEW LOGGING SESSION STARTED ######")

if 'merged_data_logger_modules' not in globals():
    class GUILogger(logging.Logger, QtCore.QObject):
        """
        This class outputs the logged data to the brickv gui
        """

        _output_format = "{asctime} - <b>{levelname:8}</b> - {message}"
        _output_format_warning = "<font color=\"orange\">{asctime} - <b>{levelname:8}</b> - {message}</font>"
        _output_format_critical = "<font color=\"red\">{asctime} - <b>{levelname:8}</b> - {message}</font>"

        #SIGNAL_NEW_MESSAGE = "newEventMessage"
        #SIGNAL_NEW_MESSAGE_TAB_HIGHLIGHT = "newEventTabHighlight"

        newEventMessage = pyqtSignal(str)
        newEventTabHighlight = pyqtSignal()

        def __init__(self, name, log_level):
            logging.Logger.__init__(self, name, log_level)
            QtCore.QObject.__init__(self)

        def debug(self, msg):
            self.log(logging.DEBUG, msg)

        def info(self, msg):
            self.log(logging.INFO, msg)

        def warn(self, msg):
            self.log(logging.WARN, msg)

        def warning(self, msg):
            self.log(logging.WARNING, msg)

        def critical(self, msg):
            self.log(logging.CRITICAL, msg)

        def error(self, msg):
            self.log(logging.ERROR, msg)

        def log(self, level, msg):
            if level >= self.level:
                asctime = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
                levelname = logging.getLevelName(level)

                if level == logging.WARN or level == logging.WARNING:
                    self.newEventMessage.emit(GUILogger._output_format_warning.format(asctime=asctime, levelname=levelname, message=msg))
                    self.newEventTabHighlight.emit()
                elif level == logging.CRITICAL or level == logging.ERROR:
                    self.newEventMessage.emit(GUILogger._output_format_critical.format(asctime=asctime, levelname=levelname, message=msg))
                    self.newEventTabHighlight.emit()
                else:
                    self.newEventMessage.emit(GUILogger._output_format.format(asctime=asctime, levelname=levelname, message=msg))
