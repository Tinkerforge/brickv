# -*- coding: utf-8 -*-
"""
Real-Time Clock Plugin
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

real_time_clock.py: Real-Time Clock Plugin Implementation

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
import random

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

WEEKDAY_BY_NUMBER = {
    BrickletRealTimeClock.WEEKDAY_MONDAY : 'Monday',
    BrickletRealTimeClock.WEEKDAY_TUESDAY : 'Tuesday',
    BrickletRealTimeClock.WEEKDAY_WEDNESDAY : 'Wednesday',
    BrickletRealTimeClock.WEEKDAY_THURSDAY : 'Thursday',
    BrickletRealTimeClock.WEEKDAY_FRIDAY : 'Friday',
    BrickletRealTimeClock.WEEKDAY_SATURDAY : 'Saturday',
    BrickletRealTimeClock.WEEKDAY_SUNDAY : 'Sunday',
}

class MeasurmentThread(Thread):
    def __init__(self, calibration):
        Thread.__init__(self, target=self.loop)

        self.daemon = True
        self.calibration = calibration
        self.running = True

    def get_rtc_timestamp(self):
        rtc_now = 0
        getter_start = time.time()

        while self.running:
            try:
                rtc_now = self.calibration.rtc.get_timestamp() / 1000.0
                break
            except Exception as e:
                if self.running:
                    self.calibration.qtcb_timeout.emit()

                time.sleep(0.1)

        getter_end = time.time()
        getter_diff = getter_end - getter_start

        return rtc_now, getter_diff

    def loop(self):
        local_start = time.time()

        rtc_start, getter_diff = self.get_rtc_timestamp()

        local_now = local_start
        rtc_now = rtc_start

        while self.running:
            last_getter_diff = getter_diff
            last_local = local_now
            last_rtc = rtc_now

            sleep_target = random.uniform(0.95, 1.45)

            sleep_start = time.time()
            time.sleep(sleep_target)
            sleep_end = time.time()
            sleep_diff = sleep_end - sleep_start

            if self.running and (sleep_diff < sleep_target - 0.1 or sleep_diff > sleep_target + 0.5):
                self.calibration.qtcb_warning.emit('Measurement might be tainted by abnormal sleep: {:.03f} seconds'.format(sleep_diff))

            local_now = time.time()

            rtc_now, getter_diff = self.get_rtc_timestamp()

            local_diff = local_now - last_local

            # the current local-diff is mostly affected by the last-getter-diff
            # and the current sleep-diff. the current getter-diff has no effect
            # as it didn't happen between the last and the current local measurement
            if self.running and (local_diff < sleep_target - 0.1 or local_diff > last_getter_diff + sleep_diff + 0.25):
                self.calibration.qtcb_warning.emit('Measurement might be tainted by Local Clock jump: {:.03f} seconds'.format(local_diff))

            rtc_diff = rtc_now - last_rtc

            # the current rtc-diff is mostly affected by the last-getter-diff,
            # the current getter-diff and current sleep-diff. in contrast to the
            # local-diff, the rtc-diff is affected by both getter-diffs. on average
            # one should assume that the RTC is sampled in the middle of the
            # getter-diff. but in the worst case the RTC might be sampled at the
            # beginning of the last-getter-diff and at the end of the current
            # getter-diff. therefore, both getter-diffs have to be added for an
            # upper bound on the rtc-diff
            if self.running and (rtc_diff < sleep_target - 0.1 or rtc_diff > last_getter_diff + sleep_diff + getter_diff + 0.25):
                self.calibration.qtcb_warning.emit('Measurement might be tainted by Real-Time Clock jump: {:.03f} seconds'.format(rtc_diff))

            if self.running:
                self.calibration.qtcb_measured_duration.emit(local_now - local_start, rtc_now - rtc_start)

class Calibration(QDialog, Ui_Calibration):
    qtcb_measured_duration = pyqtSignal(float, float)
    qtcb_warning = pyqtSignal(str)
    qtcb_timeout = pyqtSignal()

    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.parent = parent
        self.rtc = parent.rtc
        self.measured_ppm = 0
        self.measured_ppm_avg = 0
        self.measured_ppm_history = []
        self.measured_ppm_index = 0
        self.timeout_count = 0

        self.label_warning_title.hide()
        self.label_warning_message.hide()
        self.label_timeout_title.hide()
        self.label_timeout_count.hide()

        self.qtcb_measured_duration.connect(self.cb_measured_duration)
        self.qtcb_warning.connect(self.cb_warning)
        self.qtcb_timeout.connect(self.cb_timeout)

        self.button_restart.clicked.connect(self.restart)
        self.button_close.clicked.connect(self.close)
        self.spin_new_offset.valueChanged.connect(self.update_new_offset_label)
        self.button_optimize.clicked.connect(self.optimize)
        self.button_save.clicked.connect(self.save)

        if abs(self.parent.offset * 2.17) <= 20.0:
            color = '<font>'
        else:
            color = '<font color="#FF0000">'

        self.label_current_offset.setText('%s%.02f ppm</font> (%d)' % (color, self.parent.offset * 2.17, self.parent.offset))
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

        self.label_warning_title.hide()
        self.label_warning_message.hide()
        self.label_timeout_title.hide()
        self.label_timeout_count.hide()

        self.measured_ppm = 0
        self.measured_ppm_avg = 0
        self.measured_ppm_history = []
        self.measured_ppm_index = 0
        self.timeout_count = 0

        self.cb_measured_duration(0, 0)

        self.measurment_thread = MeasurmentThread(self)
        self.measurment_thread.start()

    def update_new_offset_label(self, new_offset):
        if abs(new_offset * 2.17) <= 20.0:
            color = '<font>'
        else:
            color = '<font color="#FF0000">'

        self.label_new_offset.setText('%s%.02f ppm</font>' % (color, new_offset * 2.17))

    def optimize(self):
        self.spin_new_offset.setValue(self.parent.offset + round(self.measured_ppm_avg / 2.17))

    def save(self):
        self.parent.offset = self.spin_new_offset.value()

        self.rtc.set_offset(self.parent.offset)

        if abs(self.parent.offset * 2.17) <= 20.0:
            color = '<font>'
        else:
            color = '<font color="#FF0000">'

        self.label_current_offset.setText('%s%.02f ppm</font> (%d)' % (color, self.parent.offset * 2.17, self.parent.offset))

    def cb_measured_duration(self, local_duration, rtc_duration):
        rtc_hour = int(rtc_duration) / 3600
        rtc_minute = int(rtc_duration) / 60 % 60
        rtc_second = int(rtc_duration) % 60
        rtc_centisecond = int((rtc_duration % 1) * 100)

        self.label_measured_rtc_duration.setText('%d:%02d:%02d.%02d' % (rtc_hour, rtc_minute, rtc_second, rtc_centisecond))

        local_hour = int(local_duration) / 3600
        local_minute = int(local_duration) / 60 % 60
        local_second = int(local_duration) % 60
        local_microsecond = int((local_duration % 1) * 1000000)

        self.label_measured_local_duration.setText('%d:%02d:%02d.%06d' % (local_hour, local_minute, local_second, local_microsecond))

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

            if abs(self.measured_ppm_avg) <= 20.0:
                measured_ppm_avg_color = '<font>'
            else:
                measured_ppm_avg_color = '<font color="#FF0000">'

            stddev_sum = 0

            for h in self.measured_ppm_history:
                stddev_sum += (h - self.measured_ppm_avg)**2

            stddev = math.sqrt(stddev_sum / len(self.measured_ppm_history))

            if stddev <= 0.25 and local_duration > 60:
                stddev_color = '008000'
            else:
                stddev_color = 'FF0000'

            self.label_measured_offset.setText(u'%.03f ppm (%s%.03f ppm</font> <font color="#%s">± %.03f ppm</font>)' %
                                               (self.measured_ppm, measured_ppm_avg_color, self.measured_ppm_avg, stddev_color, stddev))
        else:
            self.label_measured_offset.setText('undefined')

    def cb_warning(self, message):
        self.label_warning_message.setText(message)

        self.label_warning_title.show()
        self.label_warning_message.show()

    def cb_timeout(self):
        self.timeout_count += 1

        self.label_timeout_count.setText(str(self.timeout_count))

        self.label_timeout_title.show()
        self.label_timeout_count.show()

class RealTimeClock(PluginBase, Ui_RealTimeClock):
    qtcb_alarm = pyqtSignal(int, int, int, int, int, int, int, int, int)

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

        self.combo_alarm_weekday.addItem('Disabled', BrickletRealTimeClock.ALARM_MATCH_DISABLED)
        self.combo_alarm_weekday.addItem('Monday', BrickletRealTimeClock.WEEKDAY_MONDAY)
        self.combo_alarm_weekday.addItem('Tuesday', BrickletRealTimeClock.WEEKDAY_TUESDAY)
        self.combo_alarm_weekday.addItem('Wednesday', BrickletRealTimeClock.WEEKDAY_WEDNESDAY)
        self.combo_alarm_weekday.addItem('Thursday', BrickletRealTimeClock.WEEKDAY_THURSDAY)
        self.combo_alarm_weekday.addItem('Friday', BrickletRealTimeClock.WEEKDAY_FRIDAY)
        self.combo_alarm_weekday.addItem('Saturday', BrickletRealTimeClock.WEEKDAY_SATURDAY)
        self.combo_alarm_weekday.addItem('Sunday', BrickletRealTimeClock.WEEKDAY_SUNDAY)

        if self.firmware_version < (2, 0, 1):
            self.group_alarm.setTitle('Alarm (FW Version >= 2.0.1 required)')
            self.group_alarm.setEnabled(False)
        else:
            self.button_set_alarm.clicked.connect(self.set_alarm)
            self.button_disable_alarm.clicked.connect(self.disable_alarm)
            self.button_clear_alarms.clicked.connect(self.clear_alarms)

            self.spin_alarm_month.valueChanged.connect(self.check_alarm)
            self.spin_alarm_day.valueChanged.connect(self.check_alarm)
            self.spin_alarm_interval.valueChanged.connect(self.check_alarm)

            self.qtcb_alarm.connect(self.cb_alarm)
            self.rtc.register_callback(self.rtc.CALLBACK_ALARM,
                                       self.qtcb_alarm.emit)

    def start(self):
        async_call(self.rtc.get_offset, None, self.get_offset_async, self.increase_error_count)

        if self.firmware_version >= (2, 0, 1):
            async_call(self.rtc.get_alarm, None, self.get_alarm_async, self.increase_error_count)

        self.cbe_date_time.set_period(50)

    def stop(self):
        self.cbe_date_time.set_period(0)

    def destroy(self):
        if self.calibration != None:
            self.calibration.close()

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

    def check_alarm(self):
        month = self.spin_alarm_month.value()
        day = self.spin_alarm_day.value()
        interval = self.spin_alarm_interval.value()

        self.button_set_alarm.setEnabled(month != 0 and day != 0 and interval != 0)

    def set_alarm(self):
        month = self.spin_alarm_month.value()
        day = self.spin_alarm_day.value()
        hour = self.spin_alarm_hour.value()
        minute = self.spin_alarm_minute.value()
        second = self.spin_alarm_second.value()
        weekday = self.combo_alarm_weekday.itemData(self.combo_alarm_weekday.currentIndex())
        interval = self.spin_alarm_interval.value()

        if month == 0 or day == 0 or interval == 0:
            return

        self.rtc.set_alarm(month, day, hour, minute, second, weekday, interval)

    def disable_alarm(self):
        self.spin_alarm_month.setValue(-1)
        self.spin_alarm_day.setValue(-1)
        self.spin_alarm_hour.setValue(-1)
        self.spin_alarm_minute.setValue(-1)
        self.spin_alarm_second.setValue(-1)
        self.combo_alarm_weekday.setCurrentIndex(0)
        self.spin_alarm_interval.setValue(-1)

        self.set_alarm()

    def clear_alarms(self):
        self.list_alarms.clear()

    def get_alarm_async(self, alarm):
        month, day, hour, minute, second, weekday, interval = alarm

        self.spin_alarm_month.setValue(month)
        self.spin_alarm_day.setValue(day)
        self.spin_alarm_hour.setValue(hour)
        self.spin_alarm_minute.setValue(minute)
        self.spin_alarm_second.setValue(second)

        if weekday < 0:
            self.combo_alarm_weekday.setCurrentIndex(0)
        else:
            self.combo_alarm_weekday.setCurrentIndex(weekday)

        self.spin_alarm_interval.setValue(interval)

    def cb_alarm(self, year, month, day, hour, minute, second, centisecond, weekday, interval):
        async_call(self.rtc.get_alarm, None, self.get_alarm_async, self.increase_error_count)

        self.list_alarms.addItem('{0}-{1}-{2} T {3:02}:{4:02}:{5:02}.{6:02} {7}'
                                 .format(year, month, day, hour, minute, second, centisecond, WEEKDAY_BY_NUMBER[weekday]))
