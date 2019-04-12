# -*- coding: utf-8 -*-
"""
Solid State Relay Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

solid_state_relay.py: Solid State Relay Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.solid_state_relay.ui_solid_state_relay import Ui_SolidStateRelay
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_solid_state_relay import BrickletSolidStateRelay
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap

class SolidStateRelay(PluginBase, Ui_SolidStateRelay):
    qtcb_monoflop_done = pyqtSignal(bool)

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletSolidStateRelay, *args)

        self.setupUi(self)

        self.ssr = self.device

        self.qtcb_monoflop_done.connect(self.cb_monoflop_done)
        self.ssr.register_callback(self.ssr.CALLBACK_MONOFLOP_DONE,
                                   self.qtcb_monoflop_done.emit)

        self.ssr_button.clicked.connect(self.ssr_clicked)
        self.go_button.clicked.connect(self.go_clicked)

        self.monoflop = False
        self.timebefore = 500

        self.a_pixmap = load_masked_pixmap('plugin_system/plugins/solid_state_relay/relay_a.bmp')
        self.b_pixmap = load_masked_pixmap('plugin_system/plugins/solid_state_relay/relay_b.bmp')

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

    def get_state_async(self, state):
        width = self.ssr_button.width()
        if self.ssr_button.minimumWidth() < width:
            self.ssr_button.setMinimumWidth(width)

        s = state
        if s:
            self.ssr_button.setText('Switch Off')
            self.ssr_image.setPixmap(self.a_pixmap)
        else:
            self.ssr_button.setText('Switch On')
            self.ssr_image.setPixmap(self.b_pixmap)

    def get_monoflop_async_foobar(self, state, time, time_remaining):
        if time > 0:
            self.timebefore = time
            self.time_spinbox.setValue(self.timebefore)
        if time_remaining > 0:
            if not state:
                self.state_combobox.setCurrentIndex(0)
            self.monoflop = True
            self.time_spinbox.setEnabled(False)
            self.state_combobox.setEnabled(False)

    def start(self):
        async_call(self.ssr.get_state, None, self.get_state_async, self.increase_error_count)
        async_call(self.ssr.get_monoflop, None, self.get_monoflop_async_foobar, self.increase_error_count,
                   expand_result_tuple_for_callback=True)

        self.update_timer.start()

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSolidStateRelay.DEVICE_IDENTIFIER

    def ssr_clicked(self):
        width = self.ssr_button.width()
        if self.ssr_button.minimumWidth() < width:
            self.ssr_button.setMinimumWidth(width)

        if 'On' in self.ssr_button.text().replace('&', ''):
            self.ssr_button.setText('Switch Off')
            self.ssr_image.setPixmap(self.a_pixmap)
        else:
            self.ssr_button.setText('Switch On')
            self.ssr_image.setPixmap(self.b_pixmap)

        state = not 'On' in self.ssr_button.text().replace('&', '')
        try:
            self.ssr.set_state(state)
        except ip_connection.Error:
            return

        self.monoflop = False
        self.time_spinbox.setValue(self.timebefore)
        self.time_spinbox.setEnabled(True)
        self.state_combobox.setEnabled(True)

    def go_clicked(self):
        time = self.time_spinbox.value()
        state = self.state_combobox.currentIndex() == 0
        try:
            if self.monoflop:
                time = self.timebefore
            else:
                self.timebefore = self.time_spinbox.value()

            self.ssr.set_monoflop(state, time)

            self.monoflop = True
            self.time_spinbox.setEnabled(False)
            self.state_combobox.setEnabled(False)

            if state:
                self.ssr_button.setText('Switch Off')
                self.ssr_image.setPixmap(self.a_pixmap)
            else:
                self.ssr_button.setText('Switch On')
                self.ssr_image.setPixmap(self.b_pixmap)
        except ip_connection.Error:
            return

    def cb_monoflop_done(self, state):
        self.monoflop = False
        self.time_spinbox.setValue(self.timebefore)
        self.time_spinbox.setEnabled(True)
        self.state_combobox.setEnabled(True)
        if state:
            self.ssr_button.setText('Switch Off')
            self.ssr_image.setPixmap(self.a_pixmap)
        else:
            self.ssr_button.setText('Switch On')
            self.ssr_image.setPixmap(self.b_pixmap)

    def get_monoflop_async(self, _state, _time, time_remaining):
        if self.monoflop:
            self.time_spinbox.setValue(time_remaining)

    def update(self):
        if self.monoflop:
            async_call(self.ssr.get_monoflop, None, self.get_monoflop_async, self.increase_error_count,
                       expand_result_tuple_for_callback=True)
