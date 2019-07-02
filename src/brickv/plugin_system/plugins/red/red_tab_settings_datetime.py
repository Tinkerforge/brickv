# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_datetime.py: RED settings datetime tab implementation

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

import time
from datetime import datetime
from tzlocal import get_localzone
import pytz

from PyQt5.QtCore import QDateTime, QTimer, Qt
from PyQt5.QtWidgets import QWidget, QMessageBox

from brickv.plugin_system.plugins.red.ui_red_tab_settings_datetime import Ui_REDTabSettingsDateTime
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.utils import get_main_window

class REDTabSettingsDateTime(QWidget, Ui_REDTabSettingsDateTime):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.time_refresh_timer = QTimer(self)
        self.time_refresh_timer.setInterval(1000)
        self.time_refresh_timer.timeout.connect(self.time_refresh)
        self.time_local_old = 0
        self.time_red_old = 0

        # Signals/slots
        self.time_sync_button.clicked.connect(self.time_sync_clicked)

        self.time_timezone_red.clear()
        self.time_timezone_red.addItems(pytz.common_timezones)
        self.time_timezone_red.setCurrentText('Collecting data...')
        self.time_timezone_red.currentIndexChanged.connect(lambda: self.save_timezone_button.setEnabled(True))
        self.time_timezone_red.lineEdit().setReadOnly(True)

        self.red_reconfigure_label.hide()

        self.save_timezone_button.clicked.connect(lambda: self.set_red_timezone(self.time_timezone_red.currentText()))
        self.save_timezone_button.clicked.connect(self.red_reconfigure_label.hide)

    def tab_on_focus(self):
        self.time_start()

    def tab_off_focus(self):
        self.time_stop()

    def tab_destroy(self):
        pass

    def time_utc_offset(self):
        if time.localtime(time.time()).tm_isdst and time.daylight:
            return -time.altzone

        return -time.timezone

    def format_time_utc_offset(self, tz):
        tz //= 60

        h = abs(tz) // 60
        m = abs(tz) % 60

        if m != 0:
            return 'UTC{}{:02}:{:02}'.format('-' if tz < 0 else '+', h, m)

        return 'UTC{}{}'.format('-' if tz < 0 else '+', h)

    def convert_from_posix(self, tz):
        tz = tz.replace('Etc/', '')
        #.startswith('GMT') breaks the GMT timezone (without offset)
        if tz.startswith('GMT+') or tz.startswith('GMT-'):
            gmt_offset = -int(tz.replace('GMT', '')) # Convert from POSIX offset
            tz = 'UTC' + ('+' if gmt_offset > 0 else '') + str(gmt_offset)
        return tz

    def time_start(self):
        self.time_sync_button.setEnabled(False)

        def cb_red_brick_time(result):
            if not report_script_result(result, 'Settings | Date/Time', 'Error getting time from RED Brick'):
                return

            try:
                self.time_local_old = int(time.time())

                self.time_red_old, self.time_iso8601_red, timezone = result.stdout.split('\n')[:3]
                self.time_red_old = int(self.time_red_old)

                try:
                    self.timezone_red = pytz.timezone(timezone)
                except:
                    self.timezone_red = None

                    timezone = self.convert_from_posix(timezone)

                    timezone = "Unknown ({})".format(timezone) if len(timezone) > 0 else "Unknown"
                    self.red_reconfigure_label.show()
                    self.save_timezone_button.setEnabled(False)

                self.time_timezone_red.setCurrentText(timezone)

                try:
                    tz_str_local = self.convert_from_posix(get_localzone().zone)
                except:
                    tz_str_local = 'Unknown ({})'.format(self.format_time_utc_offset(self.time_utc_offset()))
                self.time_timezone_local.setText(tz_str_local)
                self.time_update_gui()

                self.time_refresh_timer.start()

                self.time_sync_button.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(get_main_window(),
                                     'Settings | Date/Time',
                                     'Error parsing time from RED Brick:\n\n{0}'.format(e))

            self.time_sync_button.setEnabled(True)

        self.script_manager.execute_script('settings_time_get', cb_red_brick_time)

    def time_stop(self):
        try:
            self.time_refresh_timer.stop()
        except:
            pass

    def time_refresh(self):
        self.time_local_old += 1
        self.time_red_old += 1

        self.time_update_gui()

    def time_update_gui(self):
        t = datetime.fromtimestamp(self.time_local_old)
        self.time_date_local.setDateTime(t)
        self.time_time_local.setDateTime(t)

        if self.timezone_red is None:
            t = QDateTime.fromString(self.time_iso8601_red, Qt.ISODate)
        else:
            t = datetime.fromtimestamp(self.time_red_old, tz=pytz.utc).astimezone(self.timezone_red)

        self.time_date_red.setDateTime(t)
        self.time_time_red.setDateTime(t)

    def set_red_timezone(self, timezone):
        def state_changed(process, t, p):
            if p.state == REDProcess.STATE_ERROR:
                process.release()
                QMessageBox.critical(get_main_window(),
                                     'Settings | Date/Time',
                                     'Error setting timezone.')
            elif p.state == REDProcess.STATE_EXITED:
                self.time_start()
                process.release()

        tz_str = '/usr/share/zoneinfo/' + timezone
        set_tz_str = ('/bin/ln -sf ' + tz_str + ' /etc/localtime').split(' ')
        red_process_tz = REDProcess(self.session)
        red_process_tz.state_changed_callback = lambda x: state_changed(red_process_tz, 0, x)
        red_process_tz.spawn(set_tz_str[0], set_tz_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

    def set_red_time(self, t):
        def state_changed(process, t, p):
            if p.state == REDProcess.STATE_ERROR:
                process.release()
                QMessageBox.critical(get_main_window(),
                                     'Settings | Date/Time',
                                     'Error syncing time.')
            elif p.state == REDProcess.STATE_EXITED:
                self.time_start()
                process.release()

        set_t_str = ('/bin/date +%s -u -s @' + str(int(t))).split(' ')
        red_process_t = REDProcess(self.session)
        red_process_t.state_changed_callback = lambda x: state_changed(red_process_t, 1, x)
        red_process_t.spawn(set_t_str[0], set_t_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

    def time_sync_clicked(self):
        try:
            tz_str = get_localzone().zone
            self.red_reconfigure_label.hide()
        except:
            tz = -self.time_utc_offset() # Use posix timezone definition
            if tz % 3600 != 0:
                get_main_window().show_status('Failed to query local timezone.\nFallback without automatic daylight saving time support:\nUTC offset was not a whole amount of hours.')
                self.set_red_time(time.time())
                return

            get_main_window().show_status('Failed to query local timezone.\nUsing fallback without automatic daylight saving time support.')
            tz /= 3600
            if tz < 0:
                tz_str = str(tz)
            else:
                tz_str = '+' + str(tz)
            tz_str = 'Etc/GMT' + tz_str

        self.set_red_timezone(tz_str)
        self.set_red_time(time.time())


