# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

main.py: Main standalone data logger

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

# MAIN DATA_LOGGER PROGRAM
import argparse  # command line argument parser
import os
import signal
import sys
import traceback

from brickv.data_logger.data_logger import DataLogger
from brickv.data_logger.event_logger import ConsoleLogger, FileLogger, EventLogger
from brickv.data_logger.utils import DataLoggerException

if hasattr(sys, "frozen"):
    program_path = os.path.dirname(os.path.realpath(unicode(sys.executable, sys.getfilesystemencoding())))

    if sys.platform == "darwin":
        resources_path = os.path.join(os.path.split(program_path)[0], 'Resources')
    else:
        resources_path = program_path
else:
    program_path = os.path.dirname(os.path.realpath(unicode(__file__, sys.getfilesystemencoding())))
    resources_path = program_path

# add program_path so OpenGL is properly imported
sys.path.insert(0, program_path)

# Allow brickv to be directly started by calling "main.py"
# without "brickv" being in the path already
if 'brickv' not in sys.modules:
    head, tail = os.path.split(program_path)

    if head not in sys.path:
        sys.path.insert(0, head)

    if not hasattr(sys, "frozen"):
        # load and inject in modules list, this allows to have the source in a
        # directory named differently than 'brickv'
        sys.modules['brickv'] = __import__(tail, globals(), locals(), [], -1)

# HashMap keywords to store results of the command line arguments
CONSOLE_CONFIG_FILE = "config_file"
GUI_CONFIG = "configuration"
GUI_ELEMENT = "gui_element"
CONSOLE_VALIDATE_ONLY = "validate"
CLOSE = False


def __exit_condition(data_logger):
    """
    Waits for an 'exit' or 'quit' to stop logging and close the program
    """
    try:
        while True:
            raw_input("")  # FIXME: is raw_input the right approach
            if CLOSE:
                raise KeyboardInterrupt()

    except (KeyboardInterrupt, EOFError):
        sys.stdin.close()
        data_logger.stop()


def signal_handler(signum, frame):
    """
    This function handles the ctrl + c exit condition
    if it's raised through the console
    """
    main.CLOSE = True


signal.signal(signal.SIGINT, signal_handler)


def __manage_eventlog(arguments_map):
    """EventLogger.EVENT_CONSOLE_LOGGING = arguments_map[ConfigurationReader.GENERAL_EVENTLOG_TO_CONSOLE]
    EventLogger.EVENT_FILE_LOGGING = arguments_map[ConfigurationReader.GENERAL_EVENTLOG_TO_FILE]
    EventLogger.EVENT_FILE_LOGGING_PATH = arguments_map[ConfigurationReader.GENERAL_EVENTLOG_PATH]
    EventLogger.EVENT_LOG_LEVEL = arguments_map[ConfigurationReader.GENERAL_EVENTLOG_LEVEL]

    if EventLogger.EVENT_FILE_LOGGING:
        EventLogger.add_logger(
            FileLogger("FileLogger", EventLogger.EVENT_LOG_LEVEL, EventLogger.EVENT_FILE_LOGGING_PATH))
    if not EventLogger.EVENT_CONSOLE_LOGGING:
        EventLogger.remove_logger("ConsoleLogger")
    else:
        EventLogger.remove_logger("ConsoleLogger")
        EventLogger.add_logger(ConsoleLogger("ConsoleLogger", EventLogger.EVENT_LOG_LEVEL))
"""

def main(arguments_map):
    """
    This function initialize the data logger and starts the logging process
    """
    config = None
    gui_start = False
    try:
        # was started via console
        if CONSOLE_CONFIG_FILE in arguments_map and arguments_map[CONSOLE_CONFIG_FILE] is not None:
            config = load_and_validate_config(arguments_map[CONSOLE_CONFIG_FILE])

            if config == None:
                return

        # was started via gui
        elif GUI_CONFIG in arguments_map and arguments_map[GUI_CONFIG] is not None:
            gui_start = True
            config = arguments_map[GUI_CONFIG]

        # no configuration file was given
        else:
            raise DataLoggerException(desc="Can not run data logger without a configuration.")

        if CONSOLE_VALIDATE_ONLY in arguments_map and arguments_map[CONSOLE_VALIDATE_ONLY]:
            return

        # activate eventlogger
        __manage_eventlog(config)

    except Exception as exc:
        EventLogger.critical(str(exc))
        if gui_start:
            return None
        else:
            sys.exit(DataLoggerException.DL_CRITICAL_ERROR)

    data_logger = None
    try:
        if gui_start:
            data_logger = DataLogger(config, arguments_map[GUI_ELEMENT])
        else:
            data_logger = DataLogger(config)

        if data_logger.ipcon is not None:
            data_logger.run()
            if not gui_start:
                __exit_condition(data_logger)
        else:
            raise DataLoggerException(DataLoggerException.DL_CRITICAL_ERROR,
                                      "DataLogger did not start logging process! Please check for errors.")

    except Exception as exc:
        EventLogger.critical(str(exc))
        if gui_start:
            return None
        else:
            sys.exit(DataLoggerException.DL_CRITICAL_ERROR)

    return data_logger

def command_line_start(argv, program_name):
    """
    This function processes the command line arguments, if it was started via the console.
    """
    cl_parser = argparse.ArgumentParser(description='Tinkerforge Data Logger')

    cl_parser.add_argument('config_file', help="Path to the configuration file")
    cl_parser.add_argument('-v', action="store_true", dest="validate",
                           help="Just process the validation of the configuration file")

    results = cl_parser.parse_args(argv)

    arguments_map = {}
    arguments_map[CONSOLE_CONFIG_FILE] = results.config_file
    arguments_map[CONSOLE_VALIDATE_ONLY] = results.validate

    return arguments_map

###main###
if __name__ == '__main__':
    arguments_map = command_line_start(sys.argv[1:], sys.argv[0])
    main(arguments_map)
