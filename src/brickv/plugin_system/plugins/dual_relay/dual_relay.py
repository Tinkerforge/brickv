# -*- coding: utf-8 -*-  
"""
Dual Relay Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

dual_relay.py: Dual Relay Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt4.QtCore import Qt, pyqtSignal, QTimer

from ui_dual_relay import Ui_DualRelay
from relay_a1_pixmap import get_relay_a1_pixmap
from relay_a2_pixmap import get_relay_a2_pixmap
from relay_b1_pixmap import get_relay_b1_pixmap
from relay_b2_pixmap import get_relay_b2_pixmap

from bindings import bricklet_dual_relay
        
class DualRelay(PluginBase, Ui_DualRelay):
    qtcb_monoflop = pyqtSignal(int, bool)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.dr = bricklet_dual_relay.DualRelay(self.uid)
        self.ipcon.add_device(self.dr)
        version = self.dr.get_version()[1]
        self.version = '.'.join(map(str, version))
        self.has_monoflop = version[1] > 1 or (version[1] == 1 and version[2] > 0)
        
        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.dr.register_callback(self.dr.CALLBACK_MONOFLOP_DONE,
                                  self.qtcb_monoflop.emit)
        
        self.dr1_button.pressed.connect(self.dr1_pressed)
        self.dr2_button.pressed.connect(self.dr2_pressed)
        
        self.go1_button.pressed.connect(self.go1_pressed)
        self.go2_button.pressed.connect(self.go2_pressed)

        self.r1_monoflop = False
        self.r2_monoflop = False

        self.r1_timebefore = 500
        self.r2_timebefore = 500
        
        self.a1_pixmap = get_relay_a1_pixmap()
        self.a2_pixmap = get_relay_a2_pixmap()
        self.b1_pixmap = get_relay_b1_pixmap()
        self.b2_pixmap = get_relay_b2_pixmap()

        try:
            dr1, dr2 = self.dr.get_state()
            if dr1:
                self.dr1_image.setPixmap(self.a1_pixmap)
                self.dr1_button.setText('Switch Off')
            else:
                self.dr1_image.setPixmap(self.b1_pixmap)
            if dr2:
                self.dr2_image.setPixmap(self.a2_pixmap)
                self.dr2_button.setText('Switch Off')
            else:
                self.dr2_image.setPixmap(self.b2_pixmap)

            if self.has_monoflop:
                state, time, time_remaining = self.dr.get_monoflop(1)
                if time > 0:
                    self.r1_timebefore = time
                    self.time1_spinbox.setValue(self.r1_timebefore)
                if time_remaining > 0:
                    if not state:
                        self.state1_combobox.setCurrentIndex(1)
                    self.r1_monoflop = True
                    self.time1_spinbox.setEnabled(False)
                    self.state1_combobox.setEnabled(False)

                state, time, time_remaining = self.dr.get_monoflop(2)
                if time > 0:
                    self.r2_timebefore = time
                    self.time2_spinbox.setValue(self.r2_timebefore)
                if time_remaining > 0:
                    if not state:
                        self.state2_combobox.setCurrentIndex(1)
                    self.r2_monoflop = True
                    self.time2_spinbox.setEnabled(False)
                    self.state2_combobox.setEnabled(False)
        except ip_connection.Error:
            pass
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

        if not self.has_monoflop:
            self.go1_button.setText("Go (> 1.1.0 needed)")
            self.go2_button.setText("Go (> 1.1.0 needed)")
            self.go1_button.setEnabled(False)
            self.go2_button.setEnabled(False)
        else:
            self.update_timer.start()
        
    def start(self):
        if self.has_monoflop:
            self.update_timer.start()

    def stop(self):
        self.update_timer.stop()

    @staticmethod
    def has_name(name):
        return 'Dual Relay Bricklet' in name 

    def dr1_pressed(self):
        if 'On' in self.dr1_button.text():
            self.dr1_button.setText('Switch Off')
            self.dr1_image.setPixmap(self.a1_pixmap)
        else:
            self.dr1_button.setText('Switch On')
            self.dr1_image.setPixmap(self.b1_pixmap)
        
        dr1, dr2 = ('Off' in self.dr1_button.text(), 'Off' in self.dr2_button.text())
        
        try:
            self.dr.set_state(dr1, dr2)
        except ip_connection.Error:
            return
        
        self.r1_monoflop = False
        self.time1_spinbox.setValue(self.r1_timebefore)
        self.time1_spinbox.setEnabled(True)
        self.state1_combobox.setEnabled(True)
        
    def dr2_pressed(self):
        if 'On' in self.dr2_button.text():
            self.dr2_button.setText('Switch Off')
            self.dr2_image.setPixmap(self.a2_pixmap)
        else:
            self.dr2_button.setText('Switch On')
            self.dr2_image.setPixmap(self.b2_pixmap)

        dr1, dr2 = ('Off' in self.dr1_button.text(), 'Off' in self.dr2_button.text())
        
        try:
            self.dr.set_state(dr1, dr2)
        except ip_connection.Error:
            return
        
        self.r2_monoflop = False
        self.time2_spinbox.setValue(self.r2_timebefore)
        self.time2_spinbox.setEnabled(True)
        self.state2_combobox.setEnabled(True)

    def go1_pressed(self):   
        time = self.time1_spinbox.value()
        state = self.state1_combobox.currentIndex() == 0
        try:
            if self.r1_monoflop:
                time = self.r1_timebefore
            else:
                self.r1_timebefore = self.time1_spinbox.value()
                
            self.dr.set_monoflop(1, state, time)
            
            self.r1_monoflop = True
            self.time1_spinbox.setEnabled(False)
            self.state1_combobox.setEnabled(False)
            
            if state:
                self.dr1_button.setText('Switch Off')
                self.dr1_image.setPixmap(self.a1_pixmap)
            else:
                self.dr1_button.setText('Switch On')
                self.dr1_image.setPixmap(self.b1_pixmap)
        except ip_connection.Error:
            return

    def go2_pressed(self):
        time = self.time2_spinbox.value()
        state = self.state2_combobox.currentIndex() == 0
        try:
            if self.r2_monoflop:
                time = self.r2_timebefore
            else:
                self.r2_timebefore = self.time2_spinbox.value()
                
            self.dr.set_monoflop(2, state, time)
            
            self.r2_monoflop = True
            self.time2_spinbox.setEnabled(False)
            self.state2_combobox.setEnabled(False)
            
            if state:
                self.dr2_button.setText('Switch Off')
                self.dr2_image.setPixmap(self.a2_pixmap)
            else:
                self.dr2_button.setText('Switch On')
                self.dr2_image.setPixmap(self.b2_pixmap)
        except ip_connection.Error:
            return
    
    def cb_monoflop(self, relay, state):
        if relay == 1:
            self.r1_monoflop = False
            self.time1_spinbox.setValue(self.r1_timebefore)
            self.time1_spinbox.setEnabled(True)
            self.state1_combobox.setEnabled(True)
            if state:
                self.dr1_button.setText('Switch Off')
                self.dr1_image.setPixmap(self.a1_pixmap)
            else:
                self.dr1_button.setText('Switch On')
                self.dr1_image.setPixmap(self.b1_pixmap)
        else:
            self.r2_monoflop = False
            self.time2_spinbox.setValue(self.r2_timebefore)
            self.time2_spinbox.setEnabled(True)
            self.state2_combobox.setEnabled(True)
            if state:
                self.dr2_button.setText('Switch Off')
                self.dr2_image.setPixmap(self.a2_pixmap)
            else:
                self.dr2_button.setText('Switch On')
                self.dr2_image.setPixmap(self.b2_pixmap)
    
    def update(self):
        if self.r1_monoflop:
            try:
                state, time, time_remaining = self.dr.get_monoflop(1)
                self.time1_spinbox.setValue(time_remaining)
            except ip_connection.Error:
                pass
        if self.r2_monoflop:
            try:
                state, time, time_remaining = self.dr.get_monoflop(2)
                self.time2_spinbox.setValue(time_remaining)
            except ip_connection.Error:
                pass
