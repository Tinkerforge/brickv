# -*- coding: utf-8 -*-
"""
Industrial Dual Relay Plugin
Copyright (C) 2017-2018 Olaf Lüke <olaf@tinkerforge.com>

industrial_dual_relay.py: Industrial Dual Relay Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.industrial_dual_relay.ui_industrial_dual_relay import Ui_IndustrialDualRelay
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_industrial_dual_relay import BrickletIndustrialDualRelay
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap

class IndustrialDualRelay(COMCUPluginBase, Ui_IndustrialDualRelay):
    qtcb_monoflop_done = pyqtSignal(int, bool)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialDualRelay, *args)

        self.setupUi(self)

        self.idr = self.device

        self.qtcb_monoflop_done.connect(self.cb_monoflop_done)
        self.idr.register_callback(self.idr.CALLBACK_MONOFLOP_DONE,
                                   self.qtcb_monoflop_done.emit)

        self.ch0_button.clicked.connect(self.ch0_clicked)
        self.ch1_button.clicked.connect(self.ch1_clicked)

        self.go0_button.clicked.connect(self.go0_clicked)
        self.go1_button.clicked.connect(self.go1_clicked)

        self.ch0_monoflop = False
        self.ch1_monoflop = False

        self.ch0_timebefore = 500
        self.ch1_timebefore = 500

        self.a0_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel0_a.bmp')
        self.a1_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel1_a.bmp')
        self.b0_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel0_b.bmp')
        self.b1_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel1_b.bmp')

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

    def get_value_async(self, value):
        width = self.ch0_button.width()

        if self.ch0_button.minimumWidth() < width:
            self.ch0_button.setMinimumWidth(width)

        width = self.ch1_button.width()

        if self.ch1_button.minimumWidth() < width:
            self.ch1_button.setMinimumWidth(width)

        ch0, ch1 = value

        if ch0:
            self.ch0_button.setText('Switch Off')
            self.ch0_image.setPixmap(self.a0_pixmap)
        else:
            self.ch0_button.setText('Switch On')
            self.ch0_image.setPixmap(self.b0_pixmap)

        if ch1:
            self.ch1_button.setText('Switch Off')
            self.ch1_image.setPixmap(self.a1_pixmap)
        else:
            self.ch1_button.setText('Switch On')
            self.ch1_image.setPixmap(self.b1_pixmap)

    def get_monoflop_async_foobar(self, channel, value, time, time_remaining):
        if channel == 0:
            if time > 0:
                self.ch0_timebefore = time
                self.time0_spinbox.setValue(self.ch0_timebefore)

            if time_remaining > 0:
                if not value:
                    self.value0_combobox.setCurrentIndex(0)

                self.ch0_monoflop = True
                self.time0_spinbox.setEnabled(False)
                self.value0_combobox.setEnabled(False)
        elif channel == 1:
            if time > 0:
                self.ch1_timebefore = time
                self.time1_spinbox.setValue(self.ch1_timebefore)

            if time_remaining > 0:
                if not value:
                    self.value1_combobox.setCurrentIndex(1)

                self.ch1_monoflop = True
                self.time1_spinbox.setEnabled(False)
                self.value1_combobox.setEnabled(False)

    def start(self):
        async_call(self.idr.get_value, None, self.get_value_async, self.increase_error_count)

        for channel in [0, 1]:
            async_call(self.idr.get_monoflop, channel, self.get_monoflop_async_foobar, self.increase_error_count,
                       pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)

        self.update_timer.start()

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDualRelay.DEVICE_IDENTIFIER

    def get_value_ch0_async(self, value):
        ch0, ch1 = value

        try:
            self.idr.set_value(not ch0, ch1)
        except ip_connection.Error:
            return

        self.ch0_monoflop = False
        self.time0_spinbox.setValue(self.ch0_timebefore)
        self.time0_spinbox.setEnabled(True)
        self.value0_combobox.setEnabled(True)

    def ch0_clicked(self):
        width = self.ch0_button.width()

        if self.ch0_button.minimumWidth() < width:
            self.ch0_button.setMinimumWidth(width)

        if 'On' in self.ch0_button.text().replace('&', ''):
            self.ch0_button.setText('Switch Off')
            self.ch0_image.setPixmap(self.a0_pixmap)
        else:
            self.ch0_button.setText('Switch On')
            self.ch0_image.setPixmap(self.b0_pixmap)

        async_call(self.idr.get_value, None, self.get_value_ch0_async, self.increase_error_count)

    def get_value_ch1_async(self, value):
        ch0, ch1 = value

        try:
            self.idr.set_value(ch0, not ch1)
        except ip_connection.Error:
            return

        self.ch1_monoflop = False
        self.time1_spinbox.setValue(self.ch1_timebefore)
        self.time1_spinbox.setEnabled(True)
        self.value1_combobox.setEnabled(True)

    def ch1_clicked(self):
        width = self.ch1_button.width()

        if self.ch1_button.minimumWidth() < width:
            self.ch1_button.setMinimumWidth(width)

        if 'On' in self.ch1_button.text().replace('&', ''):
            self.ch1_button.setText('Switch Off')
            self.ch1_image.setPixmap(self.a1_pixmap)
        else:
            self.ch1_button.setText('Switch On')
            self.ch1_image.setPixmap(self.b1_pixmap)

        async_call(self.idr.get_value, None, self.get_value_ch1_async, self.increase_error_count)

    def go0_clicked(self):
        time = self.time0_spinbox.value()
        value = self.value0_combobox.currentIndex() == 0

        try:
            if self.ch0_monoflop:
                time = self.ch0_timebefore
            else:
                self.ch0_timebefore = self.time0_spinbox.value()

            self.idr.set_monoflop(0, value, time)

            self.ch0_monoflop = True
            self.time0_spinbox.setEnabled(False)
            self.value0_combobox.setEnabled(False)

            if value:
                self.ch0_button.setText('Switch Off')
                self.ch0_image.setPixmap(self.a0_pixmap)
            else:
                self.ch0_button.setText('Switch On')
                self.ch0_image.setPixmap(self.b0_pixmap)
        except ip_connection.Error:
            return

    def go1_clicked(self):
        time = self.time1_spinbox.value()
        value = self.value1_combobox.currentIndex() == 0

        try:
            if self.ch1_monoflop:
                time = self.ch1_timebefore
            else:
                self.ch1_timebefore = self.time1_spinbox.value()

            self.idr.set_monoflop(1, value, time)

            self.ch1_monoflop = True
            self.time1_spinbox.setEnabled(False)
            self.value1_combobox.setEnabled(False)

            if value:
                self.ch1_button.setText('Switch Off')
                self.ch1_image.setPixmap(self.a1_pixmap)
            else:
                self.ch1_button.setText('Switch On')
                self.ch1_image.setPixmap(self.b1_pixmap)
        except ip_connection.Error:
            return

    def cb_monoflop_done(self, channel, value):
        if channel == 0:
            self.ch0_monoflop = False
            self.time0_spinbox.setValue(self.ch0_timebefore)
            self.time0_spinbox.setEnabled(True)
            self.value0_combobox.setEnabled(True)

            if value:
                self.ch0_button.setText('Switch Off')
                self.ch0_image.setPixmap(self.a0_pixmap)
            else:
                self.ch0_button.setText('Switch On')
                self.ch0_image.setPixmap(self.b0_pixmap)
        elif channel == 1:
            self.ch1_monoflop = False
            self.time1_spinbox.setValue(self.ch1_timebefore)
            self.time1_spinbox.setEnabled(True)
            self.value1_combobox.setEnabled(True)

            if value:
                self.ch1_button.setText('Switch Off')
                self.ch1_image.setPixmap(self.a1_pixmap)
            else:
                self.ch1_button.setText('Switch On')
                self.ch1_image.setPixmap(self.b1_pixmap)

    def get_monoflop_async(self, channel, _state, _time, time_remaining):
        if channel == 0:
            if self.ch0_monoflop:
                self.time0_spinbox.setValue(time_remaining)
        elif channel == 1:
            if self.ch1_monoflop:
                self.time1_spinbox.setValue(time_remaining)

    def update(self):
        if self.ch0_monoflop:
            async_call(self.idr.get_monoflop, 0, self.get_monoflop_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)

        if self.ch1_monoflop:
            async_call(self.idr.get_monoflop, 1, self.get_monoflop_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)
