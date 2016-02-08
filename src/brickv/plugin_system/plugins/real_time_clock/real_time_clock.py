# -*- coding: utf-8 -*-
"""
Real-Time Clock Plugin
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

real_time_clock.py: Hall Effect Plugin Implementation

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

from datetime import datetime
from threading import Thread
import time
import math

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QDialog

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.real_time_clock.ui_real_time_clock import Ui_RealTimeClock
from brickv.plugin_system.plugins.real_time_clock.ui_calibration import Ui_Calibration
from brickv.bindings.bricklet_real_time_clock import BrickletRealTimeClock
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_modeless_dialog_flags

WEEKDAY_BY_NAME = {
    'Monday' : BrickletRealTimeClock.WEEKDAY_MONDAY,
    'Tuesday' : BrickletRealTimeClock.WEEKDAY_TUESDAY,
    'Wednesday' : BrickletRealTimeClock.WEEKDAY_WEDNESDAY,
    'Thursday' : BrickletRealTimeClock.WEEKDAY_THURSDAY,
    'Friday' : BrickletRealTimeClock.WEEKDAY_FRIDAY,
    'Saturday' : BrickletRealTimeClock.WEEKDAY_SATURDAY,
    'Sunday' : BrickletRealTimeClock.WEEKDAY_SUNDAY,
}

class MeasurmentThread(Thread):
    def __init__(self, calibration):
        Thread.__init__(self, target=self.loop)

        self.daemon = True
        self.calibration = calibration
        self.running = True

    def loop(self):
        local_start = time.time()

        try:
            rtc_start = self.calibration.rtc.get_timestamp() / 1000.0
        except:
            self.calibration.qtcb_measurement_error.emit('Could not get Real-Time Clock timestamp')
            return

        local_now = local_start
        rtc_now = rtc_start

        time.sleep(1)

        while self.running:
            last_local = local_now
            last_rtc = rtc_now

            local_now = time.time()

            try:
                rtc_now = self.calibration.rtc.get_timestamp() / 1000.0
            except:
                self.calibration.qtcb_measurement_error.emit('Could not get Real-Time Clock timestamp')
                return

            local_diff = local_now - last_local

            if local_diff < 0.9 or local_diff > 1.1:
                self.calibration.qtcb_measurement_error.emit('Measurement interrupted by Local Clock jump')
                return

            rtc_diff = rtc_now - last_rtc

            if rtc_diff < 0.9 or rtc_diff > 1.1:
                self.calibration.qtcb_measurement_error.emit('Measurement interrupted by Real-Time Clock jump')
                return

            self.calibration.qtcb_measured_duration.emit(local_now - local_start, rtc_now - rtc_start)

            time.sleep(1)

class Calibration(QDialog, Ui_Calibration):
    qtcb_measured_duration = pyqtSignal(float, float)
    qtcb_measurement_error = pyqtSignal(str)

    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.parent = parent
        self.rtc = parent.rtc
        self.measured_ppm = 0
        self.measured_ppm_avg = 0
        self.measured_ppm_history = []
        self.measured_ppm_index = 0

        self.label_error_title.hide()
        self.label_error_message.hide()

        self.qtcb_measured_duration.connect(self.cb_measured_duration)
        self.qtcb_measurement_error.connect(self.cb_measurement_error)

        self.button_restart.clicked.connect(self.restart)
        self.button_close.clicked.connect(self.close)
        self.spin_new_offset.valueChanged.connect(self.update_new_offset_label)
        self.button_optimize.clicked.connect(self.optimize)
        self.button_save.clicked.connect(self.save)

        self.label_current_offset.setText('%.02f ppm (%d)' % (self.parent.offset * 2.17,
                                                              self.parent.offset))
        self.spin_new_offset.setValue(self.parent.offset)

        self.measurment_thread = MeasurmentThread(self)
        self.measurment_thread.start()

    def closeEvent(self, event):
        if self.measurment_thread != None:
            self.measurment_thread.running = False

        self.parent.button_calibration.setEnabled(True)
        self.parent.calibration = None

    def restart(self):
        if self.measurment_thread != None:
            self.measurment_thread.running = False

        self.label_error_title.hide()
        self.label_error_message.hide()

        self.measured_ppm = 0
        self.measured_ppm_avg = 0
        self.measured_ppm_history = []
        self.measured_ppm_index = 0

        self.measurment_thread = MeasurmentThread(self)
        self.measurment_thread.start()

    def update_new_offset_label(self, new_offset):
        self.label_new_offset.setText('%.02f ppm' % (new_offset * 2.17))

    def optimize(self):
        self.spin_new_offset.setValue(self.parent.offset + round(self.measured_ppm_avg / 2.17))

    def save(self):
        self.parent.offset = self.spin_new_offset.value()

        self.rtc.set_offset(self.parent.offset)
        self.label_current_offset.setText('%.02f ppm (%d)' % (self.parent.offset * 2.17,
                                                              self.parent.offset))

    def cb_measured_duration(self, local_duration, rtc_duration):
        rtc_hour = int(rtc_duration) / 3600
        rtc_minute = int(rtc_duration) / 60 % 60
        rtc_second = int(rtc_duration) % 60
        rtc_millisecond = int((rtc_duration % 1) * 1000000)

        self.label_measured_rtc_duration.setText('%d:%02d:%02d.%06d' % (rtc_hour, rtc_minute, rtc_second, rtc_millisecond))

        local_hour = int(local_duration) / 3600
        local_minute = int(local_duration) / 60 % 60
        local_second = int(local_duration) % 60
        local_millisecond = int((local_duration % 1) * 1000000)

        self.label_measured_local_duration.setText('%d:%02d:%02d.%06d' % (local_hour, local_minute, local_second, local_millisecond))

        self.label_measured_difference.setText('%.06f seconds' % (rtc_duration - local_duration))

        if rtc_duration > 0:
            self.measured_ppm = 1000000 * (rtc_duration - local_duration) / rtc_duration

            if len(self.measured_ppm_history) < 600:
                self.measured_ppm_history.append(self.measured_ppm)
                self.measured_ppm_index = 0
            else:
                self.measured_ppm_history[self.measured_ppm_index] = self.measured_ppm
                self.measured_ppm_index = (self.measured_ppm_index + 1) % 600

            self.measured_ppm_avg = sum(self.measured_ppm_history) / len(self.measured_ppm_history)
            stddev_sum = 0

            for h in self.measured_ppm_history:
                stddev_sum += (h - self.measured_ppm_avg)**2

            stddev = math.sqrt(stddev_sum / len(self.measured_ppm_history))

            self.label_measured_offset.setText(u'%.03f ppm (%.03f ppm ± %.03f ppm)' % (self.measured_ppm, self.measured_ppm_avg, stddev))
        else:
            self.label_measured_offset.setText('undefined')

    def cb_measurement_error(self, message):
        self.measurment_thread = None

        self.label_error_message.setText(message)

        self.label_error_title.show()
        self.label_error_message.show()

class RealTimeClock(PluginBase, Ui_RealTimeClock):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRealTimeClock, *args)

        self.setupUi(self)

        self.rtc = self.device

        self.cbe_date_time = CallbackEmulator(self.rtc.get_date_time,
                                              self.cb_date_time,
                                              self.increase_error_count)

        self.calibration = None
        self.offset = 0

        self.combo_weekday_manual.addItem('Monday', BrickletRealTimeClock.WEEKDAY_MONDAY)
        self.combo_weekday_manual.addItem('Tuesday', BrickletRealTimeClock.WEEKDAY_TUESDAY)
        self.combo_weekday_manual.addItem('Wednesday', BrickletRealTimeClock.WEEKDAY_WEDNESDAY)
        self.combo_weekday_manual.addItem('Thursday', BrickletRealTimeClock.WEEKDAY_THURSDAY)
        self.combo_weekday_manual.addItem('Friday', BrickletRealTimeClock.WEEKDAY_FRIDAY)
        self.combo_weekday_manual.addItem('Saturday', BrickletRealTimeClock.WEEKDAY_SATURDAY)
        self.combo_weekday_manual.addItem('Sunday', BrickletRealTimeClock.WEEKDAY_SUNDAY)

        index = self.combo_weekday_manual.findData(self.rtc.WEEKDAY_SATURDAY)
        self.combo_weekday_manual.setCurrentIndex(index)

        self.button_save_local.clicked.connect(self.save_local)
        self.button_save_manual.clicked.connect(self.save_manual)
        self.button_load_manual.clicked.connect(self.load_manual)

        self.button_calibration.clicked.connect(self.calibrate)

    def start(self):
        async_call(self.rtc.get_offset, None, self.get_offset_async, self.increase_error_count)
        self.cbe_date_time.set_period(50)

    def stop(self):
        self.cbe_date_time.set_period(0)

    def destroy(self):
        if self.calibration != None:
            self.calibration.close()

    def get_url_part(self):
        return 'real_time_clock'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRealTimeClock.DEVICE_IDENTIFIER

    def save_local(self):
        year = int(self.label_year_local.text())
        month = int(self.label_month_local.text())
        day = int(self.label_day_local.text())
        hour = int(self.label_hour_local.text())
        minute = int(self.label_minute_local.text())
        second = int(self.label_second_local.text())
        centisecond = int(self.label_centisecond_local.text())
        weekday = WEEKDAY_BY_NAME[self.label_weekday_local.text()]

        self.rtc.set_date_time(year, month, day, hour, minute, second, centisecond, weekday)

    def save_manual(self):
        year = self.spin_year_manual.value()
        month = self.spin_month_manual.value()
        day = self.spin_day_manual.value()
        hour = self.spin_hour_manual.value()
        minute = self.spin_minute_manual.value()
        second = self.spin_second_manual.value()
        centisecond = self.spin_centisecond_manual.value()
        weekday = self.combo_weekday_manual.itemData(self.combo_weekday_manual.currentIndex())

        self.rtc.set_date_time(year, month, day, hour, minute, second, centisecond, weekday)

    def load_manual(self):
        year = int(self.label_year_bricklet.text())
        month = int(self.label_month_bricklet.text())
        day = int(self.label_day_bricklet.text())
        hour = int(self.label_hour_bricklet.text())
        minute = int(self.label_minute_bricklet.text())
        second = int(self.label_second_bricklet.text())
        centisecond = int(self.label_centisecond_bricklet.text())
        weekday = WEEKDAY_BY_NAME[self.label_weekday_bricklet.text()]

        self.spin_year_manual.setValue(year)
        self.spin_month_manual.setValue(month)
        self.spin_day_manual.setValue(day)
        self.spin_hour_manual.setValue(hour)
        self.spin_minute_manual.setValue(minute)
        self.spin_second_manual.setValue(second)
        self.spin_centisecond_manual.setValue(centisecond)

        index = self.combo_weekday_manual.findData(weekday)
        self.combo_weekday_manual.setCurrentIndex(index)

    def cb_date_time(self, date_time):
        year, month, day, hour, minute, second, centisecond, weekday = date_time

        self.label_year_bricklet.setText(str(year))
        self.label_month_bricklet.setText('%02d' % month)
        self.label_day_bricklet.setText('%02d' % day)
        self.label_hour_bricklet.setText('%02d' % hour)
        self.label_minute_bricklet.setText('%02d' % minute)
        self.label_second_bricklet.setText('%02d' % second)
        self.label_centisecond_bricklet.setText('%02d' % centisecond)

        index = self.combo_weekday_manual.findData(weekday)
        self.label_weekday_bricklet.setText(self.combo_weekday_manual.itemText(index))

        local = datetime.now()

        self.label_year_local.setText(str(local.year))
        self.label_month_local.setText('%02d' % local.month)
        self.label_day_local.setText('%02d' % local.day)
        self.label_hour_local.setText('%02d' % local.hour)
        self.label_minute_local.setText('%02d' % local.minute)
        self.label_second_local.setText('%02d' % local.second)
        self.label_centisecond_local.setText('%02d' % (local.microsecond // 10000))

        index = self.combo_weekday_manual.findData(local.isoweekday())
        self.label_weekday_local.setText(self.combo_weekday_manual.itemText(index))

    def calibrate(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.button_calibration.setEnabled(False)
        self.calibration.show()

    def get_offset_async(self, offset):
        self.offset = offset
