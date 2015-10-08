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
import logging

from brickv.data_logger.data_logger import DataLogger
from brickv.data_logger.event_logger import ConsoleLogger, FileLogger, EventLogger
from brickv.data_logger.utils import DataLoggerException
from brickv.data_logger.configuration import load_and_validate_config

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
    global CLOSE
    CLOSE = True

def log_level_name_to_id(log_level):
    if log_level == 'debug':
        return logging.DEBUG
    elif log_level == 'info':
        return logging.INFO
    elif log_level == 'warning':
        return logging.WARNING
    elif log_level == 'error':
        return logging.ERROR
    elif log_level == 'critical':
        return logging.CRITICAL
    else:
        return logging.INFO

def main(config_filename, gui_config, gui_job):
    """
    This function initialize the data logger and starts the logging process
    """
    config = None
    gui_start = False

    if config_filename != None: # started via console
        config = load_and_validate_config(config_filename)

        if config == None:
            return None
    else: # started via GUI
        config = gui_config
        gui_start = True

    if config['debug']['log']['enabled']:
        EventLogger.add_logger(FileLogger('FileLogger', log_level_name_to_id(config['debug']['log']['level']),
                                          config['debug']['log']['file_name']))

    data_logger = None
    try:
        data_logger = DataLogger(config, gui_job)

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tinkerforge Data Logger')

    parser.add_argument('config', help='config file location')
    parser.add_argument('--log-level', choices=['none', 'debug', 'info', 'warning', 'error', 'critical'],
                        default='info', help='console logger log level')

    args = parser.parse_args(sys.argv[1:])

    if args.log_level != 'none':
        EventLogger.add_logger(ConsoleLogger('ConsoleLogger', log_level_name_to_id(args.log_level)))

    signal.signal(signal.SIGINT, signal_handler)

    main(args.config, None, None)
