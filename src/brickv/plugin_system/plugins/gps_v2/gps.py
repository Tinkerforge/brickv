# -*- coding: utf-8 -*-
"""
GPS 2.0 Plugin
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>

gps.py: GPS 2.0 Plugin Implementation

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

from PyQt4.QtCore import QUrl, pyqtSignal, QTimer
from PyQt4.QtGui import QDesktopServices, QStandardItemModel, QStandardItem, QHeaderView

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.gps_v2.ui_gps import Ui_GPS
from brickv.bindings.bricklet_gps_v2 import BrickletGPSV2
from brickv.callback_emulator import CallbackEmulator

class GPS(PluginBase, Ui_GPS):
    qtcb_pps = pyqtSignal()
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletGPSV2, *args)

        self.setupUi(self)

        self.gps = self.device

        self.cbe_universal = CallbackEmulator(self.get_universal,
                                              self.cb_universal,
                                              self.increase_error_count)
        
        self.cbe_universal_gps = CallbackEmulator(self.get_universal_gps,
                                                  self.cb_universal_gps,
                                                  self.increase_error_count)

        self.cbe_universal_glo = CallbackEmulator(self.get_universal_glo,
                                                  self.cb_universal_glo,
                                                  self.increase_error_count)
        
        self.qtcb_pps.connect(self.cb_pps)
        self.gps.register_callback(self.gps.CALLBACK_PULSE_PER_SECOND, self.qtcb_pps.emit)
        
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
        
        self.gps_counter = 0
        self.glo_counter = 0
        
        self.gps_model = QStandardItemModel(32, 3, self)
        self.gps_table.setModel(self.gps_model)
        self.gps_model.setHorizontalHeaderItem(0, QStandardItem(u'Elevation (°)'))
        self.gps_model.setHorizontalHeaderItem(1, QStandardItem(u'Azimuth (°)'))
        self.gps_model.setHorizontalHeaderItem(2, QStandardItem(u'SNR (dB)'))
        for i in range(32):
            self.gps_model.setVerticalHeaderItem(i, QStandardItem(u'Sat ' + str(i+1)))
        self.gps_table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        
        self.glo_model = QStandardItemModel(32, 3, self)
        self.glo_table.setModel(self.glo_model)
        self.glo_model.setHorizontalHeaderItem(0, QStandardItem(u'Elevation (°)'))
        self.glo_model.setHorizontalHeaderItem(1, QStandardItem(u'Azimuth (°)'))
        self.glo_model.setHorizontalHeaderItem(2, QStandardItem(u'SNR (dB)'))
        for i in range(32):
            self.glo_model.setVerticalHeaderItem(i, QStandardItem(u'Sat ' + str(i+1+64)))
        self.glo_table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        
    def cb_pps(self):
        self.fix.setStyleSheet("QLabel { color : green; }");
        QTimer.singleShot(200, self.cb_pps_off)
        
    def cb_pps_off(self):
        self.fix.setStyleSheet("QLabel { color : black; }");

    def get_universal(self):
        return self.gps.get_coordinates(), self.gps.get_status(), self.gps.get_altitude(), self.gps.get_motion(), self.gps.get_date_time()
    
    def get_universal_gps(self):
        counter = self.gps_counter
        self.gps_counter = (self.gps_counter + 1) % 33
        
        if counter == 0:
            return counter, self.gps.get_satellite_system_status(self.gps.SATELLITE_SYSTEM_GPS)
        else:
            return counter, self.gps.get_satellite_status(self.gps.SATELLITE_SYSTEM_GPS, counter)
        
    def get_universal_glo(self):
        counter = self.glo_counter
        self.glo_counter = (self.glo_counter + 1) % 33
        
        if counter == 0:
            return counter, self.gps.get_satellite_system_status(self.gps.SATELLITE_SYSTEM_GLONASS)
        else:
            return counter, self.gps.get_satellite_status(self.gps.SATELLITE_SYSTEM_GLONASS, counter)
        
    def cb_universal_gps(self, data):
        try:
            counter, x = data
            if counter == 0:
                self.update_dop(self.gps_fix, self.gps_dop, self.gps_satallites_used, x)
            else:
                self.update_table(self.gps_model, counter, x)
        except:
            pass
    
    def cb_universal_glo(self, data):
        try:
            counter, x = data
            if counter == 0:
                self.update_dop(self.glo_fix, self.glo_dop, self.glo_satallites_used, x)
            else:
                self.update_table(self.glo_model, counter, x)
        except:
            pass
        
    def update_dop(self, fix, dop, used, data):
        if data.fix == 1:
            fix.setText("No Fix")
        elif data.fix == 2:
            fix.setText("2D Fix")
        elif data.fix == 3:
            fix.setText("3D Fix")
        else:
            fix.setText("Error")
            
        str_pdop = '%.2f' % (data.pdop/100.0,)
        str_hdop = '%.2f' % (data.hdop/100.0,)
        str_vdop = '%.2f' % (data.vdop/100.0,)
        dop.setText(str(str_pdop) + ' / ' + str(str_hdop) + ' / ' + str(str_vdop))
        
        sats = []
        for sat in data.satellites:
            if sat != 0:
                sats.append(sat)
        
        if(len(sats) == 0):
            used.setText('None')
        else:
            used.setText(', '.join(map(str, sats)))
    
    def update_table(self, table_model, num, data):
        table_model.setItem(num-1, 0, QStandardItem(str(data.elevation)))
        table_model.setItem(num-1, 1, QStandardItem(str(data.azimuth)))
        table_model.setItem(num-1, 2, QStandardItem(str(data.snr)))

    def cb_universal(self, data):
        try:
            coordinates, status, altitude, motion, date_time = data

            self.cb_coordinates(*coordinates)
            self.cb_status(*status)
            self.cb_altitude(*altitude)
            self.cb_motion(*motion)
            self.cb_date_time(*date_time)
        except:
            pass

    def show_pos_clicked(self):
        if self.had_fix:
            google_str = self.last_ns + self.make_dd_dddddd(self.last_lat, True) + '+' + self.last_ew + self.make_dd_dddddd(self.last_long, True)
            QDesktopServices.openUrl(QUrl('https://maps.google.com/maps?q=' + google_str))
        else:
            QDesktopServices.openUrl(QUrl('http://www.google.com/moon/')) # :-)

    def format_changed(self, index):
        self.cb_coordinates(self.last_lat, self.last_ns, self.last_long, self.last_ew)

    def restart_clicked(self, restart_type):
        if restart_type > 0:
            self.had_fix = False # don't show cached data

            self.last_lat = 0
            self.last_ns = 'U'
            self.last_long = 0
            self.last_ew = 'U'
            
            self.satellites_view.setText('0')

            self.latitude.setText("Unknown")
            self.ns.setText('U')

            self.longitude.setText("Unknown")
            self.ew.setText('U')

            self.gps_dop.setText("Unknown")
            self.glo_dop.setText("Unknown")
            
            self.gps_satallites_used.setText("None")
            self.glo_satallites_used.setText("None")
            
            self.gps_fix.setText("No Fix")
            self.glo_fix.setText("No Fix")
            self.fix.setText("No")
            
            for i in range(32):
                self.gps_model.setItem(i, 0, QStandardItem('0'))
                self.gps_model.setItem(i, 1, QStandardItem('0'))
                self.gps_model.setItem(i, 2, QStandardItem('0'))
                self.glo_model.setItem(i, 0, QStandardItem('0'))
                self.glo_model.setItem(i, 1, QStandardItem('0'))
                self.glo_model.setItem(i, 2, QStandardItem('0'))

            self.altitude.setText("Unknown")

            self.course.setText("(Unknown)")
            self.speed.setText("Unknown")

            if restart_type > 1:
                self.time.setText("Unknown")

        self.gps.restart(restart_type)

    def start(self):
        self.cbe_universal.set_period(250)
        self.cbe_universal_gps.set_period(100)
        self.cbe_universal_glo.set_period(100)

    def stop(self):
        self.cbe_universal.set_period(0)
        self.cbe_universal_gps.set_period(0)
        self.cbe_universal_glo.set_period(0)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'gps'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletGPSV2.DEVICE_IDENTIFIER

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

    def make_dd_dddddd(self, degree, url=False):
        if url:
            return '%2.6f' % (degree / 1000000.0)
        else:
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

    def cb_coordinates(self, lat, ns, long_, ew):
        if not self.had_fix:
            return

        self.last_lat = lat
        self.last_ns = ns
        self.last_long = long_
        self.last_ew = ew

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

    def cb_status(self, has_fix, satellites_view):
        if has_fix:
            self.fix.setText("Yes")
            self.had_fix = True
        else:
            self.fix.setText("No")

        self.satellites_view.setText(str(satellites_view))

    def cb_altitude(self, altitude, geoidal_separation):
        if not self.had_fix:
            return

        self.altitude.setText('%.2f m (Geoidal Separation: %.2f m)' % (altitude/100.0, geoidal_separation/100.0))

    def cb_motion(self, course, speed):
        if not self.had_fix:
            return

        self.course.setText(u'(%.2f°)' % (course/100.0,))
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
