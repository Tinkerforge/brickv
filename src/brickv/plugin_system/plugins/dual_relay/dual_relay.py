# -*- coding: utf-8 -*-  
"""
Dual Relay Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.dual_relay.ui_dual_relay import Ui_DualRelay
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_dual_relay import BrickletDualRelay
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap

class DualRelay(PluginBase, Ui_DualRelay):
    qtcb_monoflop = pyqtSignal(int, bool)
    
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletDualRelay, *args)

        self.setupUi(self)
        
        self.dr = self.device

        self.has_monoflop = self.firmware_version >= (1, 1, 1)
        
        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.dr.register_callback(self.dr.CALLBACK_MONOFLOP_DONE,
                                  self.qtcb_monoflop.emit)
        
        self.dr1_button.clicked.connect(self.dr1_clicked)
        self.dr2_button.clicked.connect(self.dr2_clicked)
        
        self.go1_button.clicked.connect(self.go1_clicked)
        self.go2_button.clicked.connect(self.go2_clicked)

        self.r1_monoflop = False
        self.r2_monoflop = False

        self.r1_timebefore = 500
        self.r2_timebefore = 500
        
        self.a1_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_a1.bmp')
        self.a2_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_a2.bmp')
        self.b1_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_b1.bmp')
        self.b2_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_b2.bmp')

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

        if not self.has_monoflop:
            self.go1_button.setText("Go (FW Versiom >= 1.1.1 required)")
            self.go2_button.setText("Go (FW Versiom >= 1.1.1 required)")
            self.go1_button.setEnabled(False)
            self.go2_button.setEnabled(False)
        
    def get_state_async(self, state):
        width = self.dr1_button.width()
        if self.dr1_button.minimumWidth() < width:
            self.dr1_button.setMinimumWidth(width)

        width = self.dr2_button.width()
        if self.dr2_button.minimumWidth() < width:
            self.dr2_button.setMinimumWidth(width)
        
        dr1, dr2 = state
        if dr1:
            self.dr1_button.setText('Switch Off')
            self.dr1_image.setPixmap(self.a1_pixmap)
        else:
            self.dr1_button.setText('Switch On')
            self.dr1_image.setPixmap(self.b1_pixmap)
        if dr2:
            self.dr2_button.setText('Switch Off')
            self.dr2_image.setPixmap(self.a2_pixmap)
        else:
            self.dr2_button.setText('Switch On')
            self.dr2_image.setPixmap(self.b2_pixmap)
            
    def get_monoflop_async(self, monoflop, index):
        state, time, time_remaining = monoflop
        if index == 1:
            if time > 0:
                self.r1_timebefore = time
                self.time1_spinbox.setValue(self.r1_timebefore)
            if time_remaining > 0:
                if not state:
                    self.state1_combobox.setCurrentIndex(0)
                self.r1_monoflop = True
                self.time1_spinbox.setEnabled(False)
                self.state1_combobox.setEnabled(False)
        elif index == 2:
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

    def start(self):
        async_call(self.dr.get_state, None, self.get_state_async, self.increase_error_count)
        if self.has_monoflop:
            async_call(self.dr.get_monoflop, 1, lambda x: self.get_monoflop_async(x, 1), self.increase_error_count)
            async_call(self.dr.get_monoflop, 2, lambda x: self.get_monoflop_async(x, 2), self.increase_error_count)
            self.update_timer.start()

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    def get_url_part(self):
        return 'dual_relay'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDualRelay.DEVICE_IDENTIFIER

    def get_state_dr1_clicked(self, state):
        dr1, dr2 = state
        
        try:
            self.dr.set_state(not dr1, dr2)
        except ip_connection.Error:
            return
        
        self.r1_monoflop = False
        self.time1_spinbox.setValue(self.r1_timebefore)
        self.time1_spinbox.setEnabled(True)
        self.state1_combobox.setEnabled(True)
        
    def dr1_clicked(self):
        width = self.dr1_button.width()
        if self.dr1_button.minimumWidth() < width:
            self.dr1_button.setMinimumWidth(width)

        if 'On' in self.dr1_button.text():
            self.dr1_button.setText('Switch Off')
            self.dr1_image.setPixmap(self.a1_pixmap)
        else:
            self.dr1_button.setText('Switch On')
            self.dr1_image.setPixmap(self.b1_pixmap)

        async_call(self.dr.get_state, None, self.get_state_dr1_clicked, self.increase_error_count)

    def get_state_dr2_clicked(self, state):
        dr1, dr2 = state
        
        try:
            self.dr.set_state(dr1, not dr2)
        except ip_connection.Error:
            return
        
        self.r2_monoflop = False
        self.time2_spinbox.setValue(self.r2_timebefore)
        self.time2_spinbox.setEnabled(True)
        self.state2_combobox.setEnabled(True)
        
    def dr2_clicked(self):
        width = self.dr2_button.width()
        if self.dr2_button.minimumWidth() < width:
            self.dr2_button.setMinimumWidth(width)

        if 'On' in self.dr2_button.text():
            self.dr2_button.setText('Switch Off')
            self.dr2_image.setPixmap(self.a2_pixmap)
        else:
            self.dr2_button.setText('Switch On')
            self.dr2_image.setPixmap(self.b2_pixmap)

        async_call(self.dr.get_state, None, self.get_state_dr2_clicked, self.increase_error_count)

    def go1_clicked(self):
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

    def go2_clicked(self):
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
    
    def update_time_remaining(self, relay, time_remaining):
        if relay == 1:
            if self.r1_monoflop:
                self.time1_spinbox.setValue(time_remaining)
        elif relay == 2:
            if self.r2_monoflop:
                self.time2_spinbox.setValue(time_remaining)

    def update(self):
        if self.r1_monoflop:
            try:
                async_call(self.dr.get_monoflop, 1, lambda a: self.update_time_remaining(1, a[2]), self.increase_error_count)
            except ip_connection.Error:
                pass
        if self.r2_monoflop:
            try:
                async_call(self.dr.get_monoflop, 2, lambda a: self.update_time_remaining(2, a[2]), self.increase_error_count)
            except ip_connection.Error:
                pass
