# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

data_logger.py: Main data logger class

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

import logging
import threading

from brickv.bindings.ip_connection import IPConnection
from brickv.data_logger.configuration_validator import ConfigurationReader
from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.job import CSVWriterJob, XivelyJob#, GuiDataJob
import brickv.data_logger.loggable_devices as loggable_devices
from brickv.data_logger.utils import DataLoggerException
import brickv.data_logger.utils as utils
from brickv.data_logger.loggable_devices import Identifier as Idf


class DataLogger(threading.Thread):
    """
    This class represents the data logger and an object of this class is
    the actual instance of a logging process
    """

    # constructor and other functions
    def __init__(self, config, gui_job=None):
        """
            config -- brickv.data_logger.configuration_validator.Configuration
        """
        super(DataLogger, self).__init__()

        self.jobs = []  # thread hashmap for all running threads/jobs
        self.job_exit_flag = False  # flag for stopping the thread
        self.job_sleep = 1  # TODO: Enahncement -> use condition objects
        self.timers = []
        self._gui_job = gui_job
        self.max_file_size = None
        self.max_file_count = None
        self.data_queue = {}  # universal data_queue hash map
        self.host = config._general[ConfigurationReader.GENERAL_HOST]
        self.port = utils.Utilities.parse_to_int(config._general[ConfigurationReader.GENERAL_PORT])
        self.ipcon = IPConnection()
        try:
            self.ipcon.connect(self.host, self.port)  # Connect to brickd
        except Exception as e:
            EventLogger.critical("A critical error occur: " + str(e))
            self.ipcon = None
            raise DataLoggerException(DataLoggerException.DL_CRITICAL_ERROR, "A critical error occur: " + str(e))

        EventLogger.info("Connection to " + self.host + ":" + str(self.port) + " established.")
        self.ipcon.set_timeout(1)  # TODO: Timeout number
        EventLogger.debug("Set ipcon.time_out to 1.")
        self._configuration = config
        self.default_file_path = "logged_data.csv"
        self.log_to_file = True
        self.log_to_xively = False
        self.stopped = False


    def process_general_section(self):
        """
        Information out of the general section will be consumed here
        """
        data = self._configuration._general

        self.log_to_file = data[ConfigurationReader.GENERAL_LOG_TO_FILE]
        self.default_file_path = data[ConfigurationReader.GENERAL_PATH_TO_FILE]
        self.max_file_size = data[ConfigurationReader.GENERAL_LOG_FILE_SIZE]
        self.max_file_count = data[ConfigurationReader.GENERAL_LOG_COUNT]

        EventLogger.debug("Logging output to file: " + str(self.log_to_file))
        EventLogger.debug("Output file path: " + str(self.default_file_path))

    def process_xively_section(self):
        """
        Information out of the xively section will be consumed here
        """
        data = self._configuration._xively
        # TODO: write code for xively handling
        if len(data) == 0:
            return

        self.log_to_xively = data.get(ConfigurationReader.XIVELY_ACTIVE)
        logging.debug("Logging output to Xively: " + str(self.log_to_xively))
        # = data.get(XIVELY_AGENT_DESCRIPTION)
        # = data.get(XIVELY_FEED)
        # = data.get(XIVELY_API_KEY)
        # = DataLogger.parse_to_int(data.get(XIVELY_UPDATE_RATE))

    def initialize_loggable_devices(self):
        """
        This function creates the actual objects for each device out of the configuration
        """
        device_list = self._configuration._devices

        wrong_uid_msg = "The following Devices got an invalid UID: "
        got_wrong_uid_exception = False

        # start the timers
        try:
            for i in range(0, len(device_list)):
                try:
                    loggable_devices.DeviceImpl(device_list[i], self).start_timer()

                except Exception as e:
                    if str(e) == "substring not found":
                        got_wrong_uid_exception = True
                        wrong_uid_msg += str(device_list[i][Idf.DD_NAME])+"("+str(device_list[i][Idf.DD_UID])+"), "
                    else:
                        # other important exception -> raise
                        raise e

            if got_wrong_uid_exception:
                raise Exception(wrong_uid_msg)

        except Exception as exc:
            msg = "A critical error occur: " + str(exc)
            self.stop()
            raise DataLoggerException(DataLoggerException.DL_CRITICAL_ERROR, msg)

    def run(self):
        """
        This function starts the actual logging process in a new thread
        """
        self.stopped = False
        self.process_general_section()
        self.process_xively_section()

        self.initialize_loggable_devices()

        """START-WRITE-THREAD"""
        # create jobs
        # look which thread should be working
        if self.log_to_file:
            self.jobs.append(CSVWriterJob(name="CSV-Writer", datalogger=self))
        if self.log_to_xively:
            self.jobs.append(XivelyJob(name="Xively-Writer", datalogger=self))
        if self._gui_job is not None:
            self._gui_job.set_datalogger(self)
            self.jobs.append(self._gui_job)

        for t in self.jobs:
            t.start()
        EventLogger.debug("Jobs started.")

        """START-TIMERS"""
        for t in self.timers:
            t.start()
        EventLogger.debug("Get-Timers started.")

        """END_CONDITIONS"""
        EventLogger.info("DataLogger is runninng...")
        # TODO Exit condition ?

    def stop(self):
        """
        This function ends the logging process. self.stopped will be set to True if
        the data logger stops
        """
        EventLogger.info("Closing Timers and Threads...")

        """CLEANUP_AFTER_STOP """
        # check if all timers stopped
        for t in self.timers:
            t.stop()
        for t in self.timers:
            t.join()
        EventLogger.debug("Get-Timers[" + str(len(self.timers)) + "] stopped.")

        # set THREAD_EXIT_FLAG for all work threads
        for job in self.jobs:
            job.stop()
        # wait for all threads to stop
        for job in self.jobs:
            job.join()
        EventLogger.debug("Jobs[" + str(len(self.jobs)) + "] stopped.")

        if self.ipcon is not None and self.ipcon.get_connection_state() == IPConnection.CONNECTION_STATE_CONNECTED:
            self.ipcon.disconnect()
        EventLogger.info("Connection closed successfully.")

        self.stopped = True

    def add_to_queue(self, csv):
        """
        Adds logged data to all queues which are registered in 'self.data_queue'

        csv --
        """
        for q in self.data_queue.values():
            q.put(csv)
