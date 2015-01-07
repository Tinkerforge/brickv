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
from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_datetime import Ui_REDTabSettingsDateTime
from brickv.plugin_system.plugins.red.api import *
from brickv.utils import get_main_window

class REDTabSettingsDateTime(QtGui.QWidget, Ui_REDTabSettingsDateTime):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings

        self.time_refresh_timer = QtCore.QTimer()
        self.time_refresh_timer.setInterval(1000)
        self.time_refresh_timer.timeout.connect(self.time_refresh)
        self.time_local_old = 0
        self.time_red_old = 0

        # Signals/slots
        self.time_sync_button.clicked.connect(self.time_sync_clicked)

    def tab_on_focus(self):
        self.time_start()

    def tab_off_focus(self):
        self.time_stop()

    def tab_destroy(self):
        pass

    def time_utc_offset(self):
        if time.localtime(time.time()).tm_isdst and time.daylight:
            return -time.altzone/(60*60)

        return -time.timezone/(60*60)

    def time_start(self):
        self.time_sync_button.setEnabled(False)

        def cb_red_brick_time(result):
            if not result or result.stderr:
                err_msg = 'Error getting time from red-brick:\n\n'+unicode(result.stderr)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Date/Time',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)
                return

            try:
                self.time_red_old, tz = map(int, result.stdout.split('\n')[:2])
                if tz < 0:
                    tz_str_red = 'UTC' + str(tz)
                else:
                    tz_str_red = 'UTC+' + str(tz)
                self.time_timezone_red.setText(tz_str_red)

                self.time_local_old = int(time.time())
                tz = self.time_utc_offset()
                if tz < 0:
                    tz_str_local = 'UTC' + str(tz)
                else:
                    tz_str_local = 'UTC+' + str(tz)

                self.time_timezone_local.setText(tz_str_local)
                self.time_update_gui()

                self.time_refresh_timer.start()

                if (self.time_red_old == self.time_local_old) and (tz_str_local == tz_str_red):
                    self.time_sync_button.setEnabled(False)
                else:
                    self.time_sync_button.setEnabled(True)
            except Exception as e:
                err_msg = 'Error parsing time from red-brick:\n\n'+unicode(e)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Date/Time',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)

            self.time_sync_button.setEnabled(True)

        self.script_manager.execute_script('settings_time_get',
                                           cb_red_brick_time)

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
        t = QtCore.QDateTime.fromTime_t(self.time_local_old)
        self.time_date_local.setDateTime(t)
        self.time_time_local.setDateTime(t)

        t = QtCore.QDateTime.fromTime_t(self.time_red_old)
        self.time_date_red.setDateTime(t)
        self.time_time_red.setDateTime(t)

    def time_sync_clicked(self):
        def state_changed(process, t, p):
            if p.state == REDProcess.STATE_ERROR:
                process.release()
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Date/Time',
                                           'Error syncing time.',
                                           QtGui.QMessageBox.Ok)
            elif p.state == REDProcess.STATE_EXITED:
                if t == 0: #timezone
                    self.time_timezone_red.setText(self.time_timezone_local.text())
                elif t == 1: #time
                    self.time_red_old = self.time_local_old

                process.release()

            if self.time_red_old == self.time_local_old and \
               self.time_timezone_red.text() == self.time_timezone_local.text():
                self.time_sync_button.setEnabled(False)
            else:
                self.time_sync_button.setEnabled(True)

        tz = -self.time_utc_offset() # Use posix timezone definition
        if tz < 0:
            tz_str = str(tz)
        else:
            tz_str = '+' + str(tz)

        set_tz_str = ('/bin/ln -sf /usr/share/zoneinfo/Etc/GMT' + tz_str + ' /etc/localtime').split(' ')
        red_process_tz = REDProcess(self.session)
        red_process_tz.state_changed_callback = lambda x: state_changed(red_process_tz, 0, x)
        red_process_tz.spawn(set_tz_str[0], set_tz_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

        set_t_str = ('/bin/date +%s -u -s @' + str(int(time.time()))).split(' ')
        red_process_t = REDProcess(self.session)
        red_process_t.state_changed_callback = lambda x: state_changed(red_process_t, 1, x)
        red_process_t.spawn(set_t_str[0], set_t_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)
