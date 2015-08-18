""""
/*---------------------------------------------------------------------------
                                Jobs
 ---------------------------------------------------------------------------*/
"""
from PyQt4 import QtCore
import Queue
import threading
import time

from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.utils import CSVWriter


class AbstractJob(threading.Thread):
    def __init__(self, datalogger=None, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs,
                                  verbose=verbose)
        self._exit_flag = False
        self._datalogger = datalogger
        self._job_name = "[Job:" + self.name + "]"

        if self._datalogger is not None:
            self._datalogger.data_queue[self.name] = Queue.Queue()

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
            EventLogger.warning("Job:" + self.name + " was not ine the DataQueue! -> " + str(key_err))


class CSVWriterJob(AbstractJob):
    """
    This class enables the data logger to write logged data to an CSV formatted file
    """

    def __init__(self, datalogger=None, group=None, name="CSVWriterJob", args=(), kwargs=None, verbose=None):
        target = self._job
        AbstractJob.__init__(self, datalogger=datalogger, group=group, target=target, name=name, args=args,
                             kwargs=kwargs, verbose=verbose)

    def _job(self):
        try:
            # check for datalogger object
            if AbstractJob._job(self):
                return

            EventLogger.debug(self._job_name + " Started")
            csv_writer = CSVWriter(self._datalogger.default_file_path, self._datalogger.max_file_size,
                                   self._datalogger.max_file_count)

            while True:
                if not self._datalogger.data_queue[self.name].empty():
                    csv_data = self._get_data_from_queue()
                    EventLogger.debug(self._job_name + " -> " + str(csv_data))
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


class GuiDataJob(AbstractJob, QtCore.QObject):
    """
    This class enables the data logger to upload logged data to the Xively platform
    """

    SIGNAL_NEW_DATA = "signalNewData"

    def __init__(self, datalogger=None, group=None, name="GuiDataJob", args=(), kwargs=None, verbose=None):
        target = self._job
        AbstractJob.__init__(self, datalogger=datalogger, group=group, target=target, name=name, args=args,
                             kwargs=kwargs, verbose=verbose)
        QtCore.QObject.__init__(self)

    def set_datalogger(self, datalogger):
        self._datalogger = datalogger
        self._datalogger.data_queue[self.name] = Queue.Queue()

    def _job(self):
        try:
            # check for datalogger object
            if AbstractJob._job(self):
                return

            EventLogger.debug(self._job_name + " Started")

            while True:
                if not self._datalogger.data_queue[self.name].empty():
                    csv_data = self._get_data_from_queue()
                    EventLogger.debug(self._job_name + " -> " + str(csv_data))
                    self.emit(QtCore.SIGNAL(GuiDataJob.SIGNAL_NEW_DATA), csv_data)

                if not self._exit_flag and self._datalogger.data_queue[self.name].empty():
                    time.sleep(self._datalogger.job_sleep)

                if self._exit_flag and self._datalogger.data_queue[self.name].empty():
                    self._remove_from_data_queue()
                    break

        except Exception as e:
            EventLogger.critical(self._job_name + " -.- " + str(e))
            self.stop()


class XivelyJob(AbstractJob):
    """
    This class enables the data logger to upload logged data to the Xively platform
    """

    def __init__(self, datalogger=None, group=None, name="XivelyJob", args=(), kwargs=None, verbose=None):
        super(XivelyJob, self).__init__()
        EventLogger.warning(self._job_name + " Is not supported!")
        raise Exception("XivelyJob not yet implemented!")


    def _job(self):
        EventLogger.warning(self._job_name + " Is not supported!")
        raise Exception("XivelyJob._job not yet implemented!")

        # TODO: implement xively logger
        # try:
        # # check for datalogger object
        # if AbstractJob._job(self):
        # return
        #
        # EventLogger.debug(self._job_name + " Started")
        #
        # while (True):
        #         if not self._datalogger.data_queue[self.name].empty():
        #             # write
        #             csv_data = self._get_data_from_queue()
        #             EventLogger.debug(self._job_name + " -> " + str(csv_data))
        #
        #         if not self._exit_flag and self._datalogger.data_queue[self.name].empty():
        #             time.sleep(self._datalogger.job_sleep)
        #
        #         if self._exit_flag and self._datalogger.data_queue[self.name].empty():
        #             # close job
        #             EventLogger.debug(self._job_name + " Finished")
        #
        #             self._remove_from_data_queue()
        #             break
        #
        # except Exception as e:
        #     EventLogger.critical(self._job_name + " " + str(e))
        #     self.stop()
