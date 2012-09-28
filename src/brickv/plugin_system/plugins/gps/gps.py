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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPixmap, QDesktopServices
from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QUrl

from ui_gps import Ui_GPS

from bindings import bricklet_gps

import datetime
        
class GPS(PluginBase, Ui_GPS):
    qtcb_coordinates = pyqtSignal('char', int, int, 'char', int, int, int, int, int)
    qtcb_status = pyqtSignal(int, int, int, int, int, int, int, int, int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.gps = bricklet_gps.GPS(self.uid)
        self.ipcon.add_device(self.gps)
        version = self.gps.get_version()[1]
        self.version = '.'.join(map(str, version))
        
        self.qtcb_coordinates.connect(self.cb_coordinates)
        self.gps.register_callback(self.gps.CALLBACK_COORDINATES,
                                   lambda a, b, c, d, e, f, g: self.qtcb_coordinates.emit(a, b[0], b[1], c, d[0], d[1], e, f, g))
        
        self.qtcb_status.connect(self.cb_status)
        self.gps.register_callback(self.gps.CALLBACK_STATUS,
                                   self.qtcb_status.emit)
        
        self.format_combobox.currentIndexChanged.connect(self.format_changed)
        self.show_pos.pressed.connect(self.show_pos_pressed)
        
        self.last_ns = 'U'
        self.last_lat1 = 0
        self.last_lat2 = 0
        self.last_ew = 'U'
        self.last_long1 = 0
        self.last_long2 = 0
        self.last_pdop = 0
        self.last_hdop = 0
        self.last_vdop = 0
        
    def show_pos_pressed(self):
        if self.last_ns != 'U' and self.last_ew != 'U':
            google_str = self.last_ns + self.make_ddddddd(self.last_lat1, self.last_lat2) + ' ' + self.last_ew + self.make_ddddddd(self.last_long1, self.last_long2)
            QDesktopServices.openUrl(QUrl('https://maps.google.com/maps?q=' + google_str))
        else:
            # :-)
            QDesktopServices.openUrl(QUrl('http://www.google.com/moon/'))
        
    def format_changed(self, index):
        self.cb_coordinates(self.last_ns, self.last_lat1, self.last_lat2, self.last_ew, self.last_long1, self.last_long2, self.last_pdop, self.last_hdop, self.last_vdop)
        
    def start(self):
        self.gps.set_coordinates_callback_period(250)
        self.gps.set_status_callback_period(250)

    def stop(self):
        self.gps.set_coordinates_callback_period(0)
        self.gps.set_status_callback_period(0)
        
    @staticmethod
    def has_name(name):
        return 'GPS Bricklet' in name
    
    def make_ddmmmmmm(self, time1, time2):
        str_time2 = str(time2)
        
        while(len(str_time2) < 4):
            str_time2 = '0' + str_time2
            
        str_time1 = str(time1)
        
        while(len(str_time1) < 4):
            str_time1 = '0' + str_time1
        
        return str_time1[:2] + u'°' + str_time1[2:] + '.' + str_time2 + u'´'
        
    def make_ddddddd(self, time1, time2):
        dd = time1/100
        mm = (time1 % 100) + time2/10000.0
        dd += mm/60.0
        
        dd_str = '%2.5f' % (dd,)
        
        return dd_str + u'°'
    
    def make_ddmmss(self, time1, time2):
        dd_rdy = str(time1/100)
        mm = (time1 % 100) + time2/10000.0
        
        mm_rdy = int(mm)
        ss = (mm - mm_rdy)
        mm_rdy = str(mm_rdy)
        ss_rdy = str(int(ss*60 + 0.5))
        
        while(len(dd_rdy) < 2):
            dd_rdy = '0' + dd_rdy
        while(len(mm_rdy) < 2):
            mm_rdy = '0' + mm_rdy
        while(len(ss_rdy) < 2):
            ss_rdy = '0' + ss_rdy
        
        return dd_rdy + u'° ' + mm_rdy + u"' " + ss_rdy + u"''"
    
    def cb_coordinates(self, ns, lat1, lat2, ew, long1, long2, pdop, hdop, vdop):
        self.last_ns = ns
        self.last_lat1 = lat1
        self.last_lat2 = lat2
        self.last_ew = ew
        self.last_long1 = long1
        self.last_long2 = long2
        self.last_pdop = pdop
        self.last_hdop = hdop
        self.last_vdop = vdop
        
        if not ns in ('N', 'S'):
            self.ns.setText('U')
            self.latitude.setText("Unknown")
        else:
            self.ns.setText(ns)
            if self.format_combobox.currentIndex() == 0:
                self.latitude.setText(self.make_ddmmss(lat1, lat2))
            elif self.format_combobox.currentIndex() == 1:
                self.latitude.setText(self.make_ddddddd(lat1, lat2))
            elif self.format_combobox.currentIndex() == 2:
                self.latitude.setText(self.make_ddmmmmmm(lat1, lat2))
                
        if not ew in ('E', 'W'):
            self.ew.setText('U')
            self.longitude.setText("Unknown")
        else:
            self.ew.setText(ew)
            if self.format_combobox.currentIndex() == 0:
                self.longitude.setText(self.make_ddmmss(long1, long2))
            elif self.format_combobox.currentIndex() == 1:
                self.longitude.setText(self.make_ddddddd(long1, long2))
            elif self.format_combobox.currentIndex() == 2:
                self.longitude.setText(self.make_ddmmmmmm(long1, long2))
            
        str_pdop = '%.2f' % (pdop/100.0,)
        str_hdop = '%.2f' % (hdop/100.0,)
        str_vdop = '%.2f' % (vdop/100.0,)
            
        self.dop.setText(str(str_pdop) + ' / ' + str(str_hdop) + ' / ' + str(str_vdop))
        
    def cb_status(self, fix, satellites_view, satellites_used, speed, course, date, time, altitude, altitude_accuracy):
        if fix == 1:
            self.fix.setText("No Fix")
        elif fix == 2:
            self.fix.setText("2D Fix")
        elif fix == 3:
            self.fix.setText("3D Fix")
        else:
            self.fix.setText("Error")
            
        
        self.satellites_view.setText(str(satellites_view))
        self.satellites_used.setText(str(satellites_used))
        
        self.speed.setText('%.2f km/h' % (speed/100.0,))
        self.course.setText('%.2f %c' %  (course/100.0, 0xB0))
        
        yy = date % 100
        yy += 2000
        date /= 100
        mm = date % 100
        date /= 100
        dd = date
        ss = time % 100
        time /= 100
        mins = time % 100
        time /= 100
        hh = time
        
        try:
            date_str = str(datetime.datetime(yy, mm, dd, hh, mins, ss)) + " UTC"
        except:
            date_str = "No time information yet"
        self.time.setText(date_str)
        
        self.altitude.setText('%.2f m (accuracy: %.2f)' % (altitude/100.0, altitude_accuracy/100))