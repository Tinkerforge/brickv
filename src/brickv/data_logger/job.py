# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

job.py: Data logger jobs

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
#                               Jobs
#---------------------------------------------------------------------------

import queue
import threading
import time

if 'merged_data_logger_modules' not in globals():
    from PyQt5 import QtCore
    from brickv.data_logger.event_logger import EventLogger
    from brickv.data_logger.utils import CSVWriter

class AbstractJob(threading.Thread):
    def __init__(self, name, target, datalogger=None):
        threading.Thread.__init__(self, name=name, target=target)

        self.daemon = True
        self._exit_flag = False
        self._datalogger = datalogger
        self._job_name = "[Job:" + self.name + "]"

        if self._datalogger is not None:
            self._datalogger.data_queue[self.name] = queue.Queue()

    def stop(self):
        self._exit_flag = True

    def _job(self):
        # check for datalogger object
        if self._datalogger is None:
            EventLogger.warning(self.name + " started but did not get a DataLogger Object! No work could be done.")
            return True
        return False

    def _get_data_from_queue(self):
        if self._datalogger is not None:
            return self._datalogger.data_queue[self.name].get()
        return None

    # Needs to be called when you end the job!
    def _remove_from_data_queue(self):
        try:
            self._datalogger.data_queue.pop(self.name)
        except KeyError as key_err:
            EventLogger.warning("Job:" + self.name + " was not in the DataQueue! -> " + str(key_err))


class CSVWriterJob(AbstractJob):
    """
    This class enables the data logger to write logged data to an CSV formatted file
    """

    def __init__(self, datalogger=None, name="CSVWriterJob"):
        target = self._job
        AbstractJob.__init__(self, datalogger=datalogger, name=name, target=target)

    def _job(self):
        try:
            # check for datalogger object
            if AbstractJob._job(self):
                return

            EventLogger.debug(self._job_name + " Started")
            csv_writer = CSVWriter(self._datalogger.csv_file_name)

            while True:
                if not self._datalogger.data_queue[self.name].empty():
                    csv_data = self._get_data_from_queue()
                    #EventLogger.debug(self._job_name + " -> " + str(csv_data))
                    if not csv_writer.write_data_row(csv_data):
                        EventLogger.warning(self._job_name + " Could not write csv row!")

                if not self._exit_flag and self._datalogger.data_queue[self.name].empty():
                    time.sleep(self._datalogger.job_sleep)

                if self._exit_flag and self._datalogger.data_queue[self.name].empty():
                    exit_return_value = csv_writer.close_file()
                    if exit_return_value:
                        EventLogger.debug(self._job_name + " Closed his csv_writer")
                    else:
                        EventLogger.debug(
                            self._job_name + " Could NOT close his csv_writer! EXIT_RETURN_VALUE=" + str(exit))
                    EventLogger.debug(self._job_name + " Finished")

                    self._remove_from_data_queue()
                    break

        except Exception as e:
            EventLogger.critical(self._job_name + " " + str(e))
            self.stop()


if 'merged_data_logger_modules' not in globals():
    class GuiDataJob(AbstractJob, QtCore.QObject):
        """
        This class enables the data logger to log to the Gui
        """
        from brickv.data_logger.utils import LoggerTimer, CSVData
        signalNewData = QtCore.pyqtSignal(CSVData)

        def __init__(self, datalogger=None, name="GuiDataJob"):
            target = self._job
            AbstractJob.__init__(self, datalogger=datalogger, target=target, name=name)
            QtCore.QObject.__init__(self)

        def set_datalogger(self, datalogger):
            self._datalogger = datalogger
            self._datalogger.data_queue[self.name] = queue.Queue()

        def _job(self):
            try:
                # check for datalogger object
                if AbstractJob._job(self):
                    return

                EventLogger.debug(self._job_name + " Started")

                while True:
                    if not self._datalogger.data_queue[self.name].empty():
                        csv_data = self._get_data_from_queue()
                        #EventLogger.debug(self._job_name + " -> " + str(csv_data))
                        self.signalNewData.emit(csv_data)

                    if not self._exit_flag and self._datalogger.data_queue[self.name].empty():
                        time.sleep(self._datalogger.job_sleep)

                    if self._exit_flag and self._datalogger.data_queue[self.name].empty():
                        self._remove_from_data_queue()
                        break

            except Exception as e:
                EventLogger.critical(self._job_name + " -.- " + str(e))
                self.stop()