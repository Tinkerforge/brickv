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

#### skip here for brick-logger ####

import logging
import threading
import time

if 'merged_data_logger_modules' not in globals():
    from brickv.bindings.ip_connection import IPConnection, base58decode
    from brickv.data_logger.event_logger import EventLogger
    from brickv.data_logger.job import CSVWriterJob#, GuiDataJob
    from brickv.data_logger.loggable_devices import DeviceImpl
    from brickv.data_logger.utils import DataLoggerException
else:
    from tinkerforge.ip_connection import IPConnection, base58decode

class DataLogger(threading.Thread):
    """
    This class represents the data logger and an object of this class is
    the actual instance of a logging process
    """

    # constructor and other functions
    def __init__(self, config, gui_job):
        super(DataLogger, self).__init__()

        self.daemon = True

        self.jobs = []  # thread hashmap for all running threads/jobs
        self.job_exit_flag = False  # flag for stopping the thread
        self.job_sleep = 1  # TODO: Enahncement -> use condition objects
        self.timers = []
        self._gui_job = gui_job
        self.data_queue = {}  # universal data_queue hash map
        self.host = config['hosts']['default']['name']
        self.port = config['hosts']['default']['port']
        self.loggable_devices = []
        self.ipcon = IPConnection()

        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, self.cb_connected)
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, self.cb_enumerate)

        try:
            self.ipcon.connect(self.host, self.port)  # Connect to brickd
        except Exception as e:
            EventLogger.critical("A critical error occur: " + str(e))
            self.ipcon = None
            raise DataLoggerException(DataLoggerException.DL_CRITICAL_ERROR, "A critical error occur: " + str(e))

        EventLogger.info("Connection to " + self.host + ":" + str(self.port) + " established.")
        self.ipcon.set_timeout(1)  # TODO: Timeout number
        EventLogger.debug("Set ipcon.time_out to 1.")
        self._config = config
        self.csv_file_name = 'logger_data_{0}.csv'.format(int(time.time()))
        self.csv_enabled = True
        self.stopped = False

    def cb_connected(self, connect_reason):
        self.apply_options()

    def cb_enumerate(self, uid, connected_uid, position,
                     hardware_version, firmware_version,
                     device_identifier, enumeration_type):
        if enumeration_type in [IPConnection.ENUMERATION_TYPE_AVAILABLE,
                                IPConnection.ENUMERATION_TYPE_CONNECTED]:
            self.apply_options()

    def apply_options(self):
        for loggable_device in self.loggable_devices:
            loggable_device.apply_options()

    def process_data_csv_section(self):
        """
        Information out of the general section will be consumed here
        """
        csv = self._config['data']['csv']

        self.csv_enabled = csv['enabled']
        self.csv_file_name = csv['file_name']

        EventLogger.debug("Logging output to CSV file: " + str(self.csv_enabled))
        EventLogger.debug("Output file path: " + str(self.csv_file_name))

    def initialize_loggable_devices(self):
        """
        This function creates the actual objects for each device out of the configuration
        """
        # start the timers
        for device in self._config['devices']:
            if len(device['uid']) == 0:
                EventLogger.warning('Ignoring "{0}" with empty UID'.format(device['name']))
                continue

            try:
                decoded_uid = base58decode(device['uid'])
            except:
                EventLogger.warning('Ignoring "{0}" with invalid UID: {1}'.format(device['name'], device['uid']))
                continue

            if decoded_uid < 1 or decoded_uid > 0xFFFFFFFF:
                EventLogger.warning('Ignoring "{0}" with out-of-range UID: {1}'.format(device['name'], device['uid']))
                continue

            try:
                loggable_device = DeviceImpl(device, self)
                loggable_device.start_timer()
            except Exception as e:
                msg = "A critical error occur: " + str(e)
                self.stop()
                raise DataLoggerException(DataLoggerException.DL_CRITICAL_ERROR, msg)

            self.loggable_devices.append(loggable_device)

        self.apply_options()

    def run(self):
        """
        This function starts the actual logging process in a new thread
        """
        self.stopped = False
        self.process_data_csv_section()

        self.initialize_loggable_devices()

        """START-WRITE-THREAD"""
        # create jobs
        # look which thread should be working
        if self.csv_enabled:
            self.jobs.append(CSVWriterJob(name="CSV-Writer", datalogger=self))
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
        EventLogger.info("DataLogger is running...")
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
