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

data_logger_version = 'invalid'

#### skip here for brick-logger ####

# MAIN DATA_LOGGER PROGRAM
import argparse  # command line argument parser
import os
import signal
import sys
import traceback
import logging
import functools
import time
import locale

if 'merged_data_logger_modules' not in globals():
    from brickv.data_logger.data_logger import DataLogger
    from brickv.data_logger.event_logger import ConsoleLogger, FileLogger, EventLogger
    from brickv.data_logger.utils import DataLoggerException
    from brickv.data_logger.configuration import load_and_validate_config

def signal_handler(interrupted_ref, signum, frame):
    """
    This function handles the ctrl + c exit condition
    if it's raised through the console
    """
    EventLogger.info('Received SIGINT/SIGTERM')
    interrupted_ref[0] = True

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

def main(config_filename, gui_config, gui_job, override_csv_file_name,
         override_log_file_name, interrupted_ref):
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

    if override_csv_file_name != None:
        config['data']['csv']['file_name'] = override_csv_file_name

    if override_log_file_name != None:
        config['debug']['log']['file_name'] = override_log_file_name

    if config['debug']['log']['enabled']:
        EventLogger.add_logger(FileLogger('FileLogger', log_level_name_to_id(config['debug']['log']['level']),
                                          config['debug']['log']['file_name']))

    try:
        data_logger = DataLogger(config, gui_job)

        if data_logger.ipcon is not None:
            data_logger.run()

            if not gui_start:
                while not interrupted_ref[0]:
                    try:
                        time.sleep(0.25)
                    except:
                        pass

                data_logger.stop()
                sys.exit(0)
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
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass # ignore this as it might fail on macOS, we'll fallback to UTF-8 in that case

    parser = argparse.ArgumentParser(description='Tinkerforge Data Logger')

    class VersionAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print(data_logger_version)
            sys.exit(0)

    parser.add_argument('-v', '--version', action=VersionAction, nargs=0, help='show version and exit')
    parser.add_argument('config', help='config file location', metavar='CONFIG')
    parser.add_argument('--console-log-level', choices=['none', 'debug', 'info', 'warning', 'error', 'critical'],
                        default='info', help='change console log level (default: info)')
    parser.add_argument('--override-csv-file-name', type=str, default=None,
                        help='override CSV file name in config')
    parser.add_argument('--override-log-file-name', type=str, default=None,
                        help='override log file name in config')

    args = parser.parse_args(sys.argv[1:])

    if args.console_log_level != 'none':
        EventLogger.add_logger(ConsoleLogger('ConsoleLogger', log_level_name_to_id(args.console_log_level)))

    interrupted_ref = [False]

    signal.signal(signal.SIGINT, functools.partial(signal_handler, interrupted_ref))
    signal.signal(signal.SIGTERM, functools.partial(signal_handler, interrupted_ref))

    main(args.config, None, None, args.override_csv_file_name, args.override_log_file_name, interrupted_ref)
