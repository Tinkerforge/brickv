# -*- coding: utf-8 -*-
"""
GPS Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

gps.py: GPS Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDesktopServices
from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QUrl

from ui_gps import Ui_GPS

from bindings import bricklet_gps

import datetime

class GPS(PluginBase, Ui_GPS):
    qtcb_coordinates = pyqtSignal(int, 'char', int, 'char', int, int, int, int)
    qtcb_status = pyqtSignal(int, int, int)
    qtcb_altitude = pyqtSignal(int, int)
    qtcb_motion = pyqtSignal(int, int)
    qtcb_date_time = pyqtSignal(int, int)

    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)

        self.setupUi(self)

        self.gps = bricklet_gps.GPS(self.uid)
        self.ipcon.add_device(self.gps)
        version = self.gps.get_version()[1]
        self.version = '.'.join(map(str, version))

        self.qtcb_coordinates.connect(self.cb_coordinates)
        self.gps.register_callback(self.gps.CALLBACK_COORDINATES,
                                   self.qtcb_coordinates.emit)

        self.qtcb_status.connect(self.cb_status)
        self.gps.register_callback(self.gps.CALLBACK_STATUS,
                                   self.qtcb_status.emit)

        self.qtcb_altitude.connect(self.cb_altitude)
        self.gps.register_callback(self.gps.CALLBACK_ALTITUDE,
                                   self.qtcb_altitude.emit)

        self.qtcb_motion.connect(self.cb_motion)
        self.gps.register_callback(self.gps.CALLBACK_MOTION,
                                   self.qtcb_motion.emit)

        self.qtcb_date_time.connect(self.cb_date_time)
        self.gps.register_callback(self.gps.CALLBACK_DATE_TIME,
                                   self.qtcb_date_time.emit)

        self.format_combobox.currentIndexChanged.connect(self.format_changed)
        self.show_pos.pressed.connect(self.show_pos_pressed)

        self.had_fix = False

        self.last_lat = 0
        self.last_ns = 'U'
        self.last_long = 0
        self.last_ew = 'U'
        self.last_pdop = 0
        self.last_hdop = 0
        self.last_vdop = 0
        self.last_epe = 0

        self.voltage_timer = QTimer()
        self.voltage_timer.timeout.connect(self.update_voltage)
        self.voltage_timer.setInterval(10)

    def show_pos_pressed(self):
        if self.had_fix:
            google_str = self.last_ns + self.make_dd_dddddd(self.last_lat) + ' ' + self.last_ew + self.make_dd_dddddd(self.last_long)
            QDesktopServices.openUrl(QUrl('https://maps.google.com/maps?q=' + google_str))
        else:
            # :-)
            QDesktopServices.openUrl(QUrl('http://www.google.com/moon/'))

    def format_changed(self, index):
        self.cb_coordinates(self.last_lat, self.last_ns, self.last_long, self.last_ew, self.last_pdop, self.last_hdop, self.last_vdop, self.last_epe)

    def start(self):
        self.gps.set_coordinates_callback_period(250)
        self.gps.set_status_callback_period(250)
        self.gps.set_altitude_callback_period(250)
        self.gps.set_motion_callback_period(250)
        self.gps.set_date_time_callback_period(250)

        self.update_voltage()
        self.voltage_timer.start()

    def stop(self):
        self.gps.set_coordinates_callback_period(0)
        self.gps.set_status_callback_period(0)
        self.gps.set_altitude_callback_period(0)
        self.gps.set_motion_callback_period(0)
        self.gps.set_date_time_callback_period(0)

        self.voltage_timer.stop()

    @staticmethod
    def has_name(name):
        return 'GPS Bricklet' in name

    def make_ddmm_mmmmm(self, degree):
        dd = degree / 1000000
        mm = (degree % 1000000) * 60 / 1000000.0
        mmmmm = (mm - int(mm)) * 100000

        dd_str = str(dd)
        mm_str = str(int(mm))
        mmmmm_str = str(int(mmmmm + 0.5))

        while len(mm_str) < 2:
            mm_str = '0' + mm_str

        while len(mmmmm_str) < 5:
            mmmmm_str = '0' + mmmmm_str

        return u'{0}° {1}.{2}’'.format(dd_str, mm_str, mmmmm_str)

    def make_dd_dddddd(self, degree):
        return u'%2.6f°' % (degree / 1000000.0)

    def make_ddmmss_sss(self, degree):
        dd = degree / 1000000
        mm = (degree % 1000000) * 60 / 1000000.0
        ss = (mm - int(mm)) * 60
        sss = (ss - int(ss)) * 1000

        dd_str = str(dd)
        mm_str = str(int(mm))
        ss_str = str(int(ss))
        sss_str = str(int(sss + 0.5))

        while len(mm_str) < 2:
            mm_str = '0' + mm_str

        while len(ss_str) < 2:
            ss_str = '0' + ss_str

        while len(sss_str) < 3:
            sss_str = '0' + sss_str

        return u'{0}° {1}’ {2}.{3}’’'.format(dd_str, mm_str, ss_str, sss_str)

    def cb_coordinates(self, lat, ns, long, ew, pdop, hdop, vdop, epe):
        if not self.had_fix:
            return

        self.last_lat = lat
        self.last_ns = ns
        self.last_long = long
        self.last_ew = ew
        self.last_pdop = pdop
        self.last_hdop = hdop
        self.last_vdop = vdop
        self.last_epe = epe

        if not ns in ('N', 'S'):
            self.latitude.setText("Unknown")
            self.ns.setText('U')
        else:
            self.ns.setText(ns)
            if self.format_combobox.currentIndex() == 0:
                self.latitude.setText(self.make_ddmmss_sss(lat))
            elif self.format_combobox.currentIndex() == 1:
                self.latitude.setText(self.make_dd_dddddd(lat))
            elif self.format_combobox.currentIndex() == 2:
                self.latitude.setText(self.make_ddmm_mmmmm(lat))

        if not ew in ('E', 'W'):
            self.longitude.setText("Unknown")
            self.ew.setText('U')
        else:
            self.ew.setText(ew)
            if self.format_combobox.currentIndex() == 0:
                self.longitude.setText(self.make_ddmmss_sss(long))
            elif self.format_combobox.currentIndex() == 1:
                self.longitude.setText(self.make_dd_dddddd(long))
            elif self.format_combobox.currentIndex() == 2:
                self.longitude.setText(self.make_ddmm_mmmmm(long))

        str_pdop = '%.2f' % (pdop/100.0,)
        str_hdop = '%.2f' % (hdop/100.0,)
        str_vdop = '%.2f' % (vdop/100.0,)
        str_epe = '%.2f m' % (epe/100.0,)

        self.dop.setText(str(str_pdop) + ' / ' + str(str_hdop) + ' / ' + str(str_vdop))
        self.epe.setText(str(str_epe))

    def cb_status(self, fix, satellites_view, satellites_used):
        if fix == 1:
            self.fix.setText("No Fix")
        elif fix == 2:
            self.fix.setText("2D Fix")
            self.had_fix = True
        elif fix == 3:
            self.fix.setText("3D Fix")
            self.had_fix = True
        else:
            self.fix.setText("Error")

        self.satellites_view.setText(str(satellites_view))
        self.satellites_used.setText(str(satellites_used))

    def cb_altitude(self, altitude, geoidal_separation):
        if not self.had_fix:
            return

        self.altitude.setText('%.2f m (Geoidal Separation: %.2f m)' % (altitude/100.0, geoidal_separation/100.0))

    def cb_motion(self, course, speed):
        if not self.had_fix:
            return

        self.course.setText(u'%.2f°' % (course/100.0,))
        self.speed.setText('%.2f km/h' % (speed/100.0,))

    def cb_date_time(self, date, time):
        yy = date % 100
        yy += 2000
        date /= 100
        mm = date % 100
        date /= 100
        dd = date

        time /= 1000
        ss = time % 100
        time /= 100
        mins = time % 100
        time /= 100
        hh = time

        try:
            date_str = str(datetime.datetime(yy, mm, dd, hh, mins, ss)) + " UTC"
        except:
            date_str = "Unknown"

        self.time.setText(date_str)

    def update_voltage(self):
        try:
            bv = self.gps.get_battery_voltage()
            self.voltage.setText('%.2f V' % (bv/1000.0))
        except ip_connection.Error:
            pass
