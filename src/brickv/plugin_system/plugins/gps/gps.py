# -*- coding: utf-8 -*-
"""
GPS Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

import datetime

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.gps.ui_gps import Ui_GPS
from brickv.bindings.bricklet_gps import BrickletGPS
from brickv.callback_emulator import CallbackEmulator

class GPS(PluginBase, Ui_GPS):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletGPS, *args)

        self.setupUi(self)

        self.gps = self.device

        self.cbe_universal = CallbackEmulator(self.get_universal,
                                              None,
                                              self.cb_universal,
                                              self.increase_error_count,
                                              expand_result_tuple_for_callback=True)

        self.format_combobox.currentIndexChanged.connect(self.format_changed)
        self.show_pos.clicked.connect(self.show_pos_clicked)
        self.hot_start.clicked.connect(lambda: self.restart_clicked(0))
        self.warm_start.clicked.connect(lambda: self.restart_clicked(1))
        self.cold_start.clicked.connect(lambda: self.restart_clicked(2))
        self.factory_reset.clicked.connect(lambda: self.restart_clicked(3))

        self.had_fix = False

        self.last_lat = 0
        self.last_ns = 'U'
        self.last_long = 0
        self.last_ew = 'U'
        self.last_pdop = 0
        self.last_hdop = 0
        self.last_vdop = 0
        self.last_epe = 0

    def get_universal(self):
        return self.gps.get_coordinates(), self.gps.get_status(), self.gps.get_altitude(), self.gps.get_motion(), self.gps.get_date_time()

    def cb_universal(self, coordinates, status, altitude, motion, date_time):
        self.cb_coordinates(*coordinates)
        self.cb_status(*status)
        self.cb_altitude(*altitude)
        self.cb_motion(*motion)
        self.cb_date_time(*date_time)

    def show_pos_clicked(self):
        if self.had_fix:
            google_str = self.last_ns + self.make_dd_dddddd(self.last_lat, True) + '+' + self.last_ew + self.make_dd_dddddd(self.last_long, True)
            QDesktopServices.openUrl(QUrl('https://maps.google.com/maps?q=' + google_str))
        else:
            QDesktopServices.openUrl(QUrl('http://www.google.com/moon/')) # :-)

    def format_changed(self, _index):
        self.cb_coordinates(self.last_lat, self.last_ns, self.last_long, self.last_ew, self.last_pdop, self.last_hdop, self.last_vdop, self.last_epe)

    def restart_clicked(self, restart_type):
        if restart_type > 0:
            self.had_fix = False # don't show cached data

            self.last_lat = 0
            self.last_ns = 'U'
            self.last_long = 0
            self.last_ew = 'U'
            self.last_pdop = 0
            self.last_hdop = 0
            self.last_vdop = 0
            self.last_epe = 0

            self.latitude.setText("Unknown")
            self.ns.setText('U')

            self.longitude.setText("Unknown")
            self.ew.setText('U')

            self.dop.setText("Unknown")
            self.epe.setText("Unknown")

            self.altitude.setText("Unknown")

            self.course.setText("Unknown")
            self.speed.setText("Unknown")

            if restart_type > 1:
                self.time.setText("Unknown")

        self.gps.restart(restart_type)

    def start(self):
        self.cbe_universal.set_period(250)

    def stop(self):
        self.cbe_universal.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletGPS.DEVICE_IDENTIFIER

    def make_ddmm_mmmmm(self, degree):
        dd = degree // 1000000
        mm = (degree % 1000000) * 60 / 1000000.0
        mmmmm = (mm - int(mm)) * 100000

        dd_str = str(dd)
        mm_str = str(int(mm))
        mmmmm_str = str(int(mmmmm + 0.5))

        while len(mm_str) < 2:
            mm_str = '0' + mm_str

        while len(mmmmm_str) < 5:
            mmmmm_str = '0' + mmmmm_str

        return '{0}° {1}.{2}’'.format(dd_str, mm_str, mmmmm_str)

    def make_dd_dddddd(self, degree, url=False):
        if url:
            return '%2.6f' % (degree / 1000000.0)
        else:
            return '%2.6f°' % (degree / 1000000.0)

    def make_ddmmss_sss(self, degree):
        dd = degree // 1000000
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

        return '{0}° {1}’ {2}.{3}’’'.format(dd_str, mm_str, ss_str, sss_str)

    def cb_coordinates(self, lat, ns, long_, ew, pdop, hdop, vdop, epe):
        if not self.had_fix:
            return

        self.last_lat = lat
        self.last_ns = ns
        self.last_long = long_
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
                self.longitude.setText(self.make_ddmmss_sss(long_))
            elif self.format_combobox.currentIndex() == 1:
                self.longitude.setText(self.make_dd_dddddd(long_))
            elif self.format_combobox.currentIndex() == 2:
                self.longitude.setText(self.make_ddmm_mmmmm(long_))

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

        self.course.setText('%.2f°' % (course/100.0,))
        self.speed.setText('%.2f km/h' % (speed/100.0,))

    def cb_date_time(self, date, time):
        yy = date % 100
        yy += 2000
        date //= 100
        mm = date % 100
        date //= 100
        dd = date

        time //= 1000
        ss = time % 100
        time //= 100
        mins = time % 100
        time //= 100
        hh = time

        try:
            date_str = str(datetime.datetime(yy, mm, dd, hh, mins, ss)) + " UTC"
        except:
            date_str = "Unknown"

        self.time.setText(date_str)
