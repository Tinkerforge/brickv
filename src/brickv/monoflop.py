# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

monoflop.py: General Monoflop logic

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

from PyQt5.QtCore import pyqtSignal, QTimer, QObject
from PyQt5.QtWidgets import QDoubleSpinBox

from brickv.async_call import async_call
from brickv.bindings.ip_connection import Error

class Monoflop(QObject):
    qtcb_monoflop_done = pyqtSignal(object)
    qtcb_monoflop_channel_done = pyqtSignal(int, object)

    def __init__(self, device, channels, value_comboboxes, value_change_callback, time_spinboxes, time_remaining_labels, parent,
                 setter_uses_bitmasks=False, callback_uses_bitmasks=False, handle_get_monoflop_invalid_parameter_as_abort=False):
        super().__init__(parent)

        if channels == None:
            channels = [None]
            time_spinboxes = [time_spinboxes]
            value_comboboxes = [value_comboboxes]
            time_remaining_labels = [time_remaining_labels]
        elif time_remaining_labels == None:
            time_remaining_labels = [None] * len(channels)

        for time_spinbox in time_spinboxes:
            assert isinstance(time_spinbox, QDoubleSpinBox), time_spinbox

            time_spinbox.setRange(1, (1 << 32) - 1)
            time_spinbox.setDecimals(0)
            time_spinbox.setSingleStep(1)
            time_spinbox.setValue(1000)

        self.device = device
        self.channels = channels
        self.value_comboboxes = value_comboboxes
        self.value_change_callback = value_change_callback
        self.time_spinboxes = time_spinboxes
        self.time_remaining_labels = time_remaining_labels
        self.parent = parent
        self.setter_uses_bitmasks = setter_uses_bitmasks
        self.callback_uses_bitmasks = callback_uses_bitmasks
        self.handle_get_monoflop_invalid_parameter_as_abort = handle_get_monoflop_invalid_parameter_as_abort
        self.times = [int(time_spinbox.value()) for time_spinbox in time_spinboxes]
        self.running = [False] * len(channels)

        self.qtcb_monoflop_done.connect(self.cb_monoflop_done)
        self.qtcb_monoflop_channel_done.connect(self.cb_monoflop_channel_done)

        if channels[0] != None:
            self.device.register_callback(self.device.CALLBACK_MONOFLOP_DONE,
                                          self.qtcb_monoflop_channel_done.emit)
        else:
            self.device.register_callback(self.device.CALLBACK_MONOFLOP_DONE,
                                          self.qtcb_monoflop_done.emit)

        self.last_update_value = None
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

    def get_monoflop_channel_start_async(self, channel, value, time, time_remaining):
        channel_index = self.channels.index(channel)

        if time > 0:
            self.times[channel_index] = time

        self.running[channel_index] = time_remaining > 0

        if self.running[channel_index]:
            self.time_spinboxes[channel_index].setValue(time_remaining)
        elif time > 0:
            self.time_spinboxes[channel_index].setValue(time)

        self.value_comboboxes[channel_index].setDisabled(self.running[channel_index])
        self.time_spinboxes[channel_index].setDisabled(self.running[channel_index])

        if self.time_remaining_labels[channel_index] != None:
            self.time_remaining_labels[channel_index].setText(str(time_remaining))

        if self.running[channel_index]:
            self.update()
            self.update_timer.start()

    def get_monoflop_channel_start_async_error(self, channel, error):
        if self.handle_get_monoflop_invalid_parameter_as_abort and \
           isinstance(error, Error) and error.value == Error.INVALID_PARAMETER:
            self.abort_tracking(channel)
            return

        self.parent.increase_error_count()

    def get_monoflop_start_async(self, value, time, time_remaining):
        self.get_monoflop_channel_start_async(None, value, time, time_remaining)

    def get_monoflop_start_async_error(self, error):
        self.get_monoflop_channel_start_async_error(None, error)

    def start(self):
        for channel in self.channels:
            if channel != None:
                async_call(self.device.get_monoflop, channel, self.get_monoflop_channel_start_async, self.get_monoflop_channel_start_async_error,
                           pass_arguments_to_result_callback=True, pass_arguments_to_error_callback=True, pass_exception_to_error_callback=True,
                           expand_result_tuple_for_callback=True)
            else:
                async_call(self.device.get_monoflop, None, self.get_monoflop_start_async, self.get_monoflop_start_async_error,
                           pass_exception_to_error_callback=True, expand_result_tuple_for_callback=True)

    def stop(self):
        self.update_timer.stop()

    def trigger(self, channel=None):
        channel_index = self.channels.index(channel)

        value_combobox = self.value_comboboxes[channel_index]
        time_spinbox = self.time_spinboxes[channel_index]

        if not self.running[channel_index]:
            self.times[channel_index] = int(time_spinbox.value())

        value = value_combobox.itemData(value_combobox.currentIndex())
        time = self.times[channel_index]

        if channel != None:
            if self.setter_uses_bitmasks:
                arguments = (1 << channel_index, value << channel_index, time)
            else:
                arguments = (channel, value, time)
        else:
            assert not self.setter_uses_bitmasks

            arguments = (value, time)

        self.last_update_value = None

        async_call(self.device.set_monoflop, arguments, None, self.parent.increase_error_count)

        self.running[channel_index] = True

        self.value_comboboxes[channel_index].setDisabled(True)
        self.time_spinboxes[channel_index].setDisabled(True)

        if self.time_remaining_labels[channel_index] != None:
            self.time_remaining_labels[channel_index].setText(str(time))

        self.update()
        self.update_timer.start()

    def get_monoflop_channel_update_async(self, channel, value, time, time_remaining):
        channel_index = self.channels.index(channel)

        if self.value_change_callback != None and value != self.last_update_value:
            if channel != None:
                self.value_change_callback(channel, value)
            else:
                self.value_change_callback(value)

        self.last_update_value = value

        if time_remaining == 0:
            self.abort_tracking(channel)
        elif self.running[channel_index]:
            self.times[channel_index] = time

            self.time_spinboxes[channel_index].setValue(time_remaining)

            if self.time_remaining_labels[channel_index] != None:
                self.time_remaining_labels[channel_index].setText(str(time_remaining))

    def get_monoflop_channel_update_async_error(self, channel, error):
        if self.handle_get_monoflop_invalid_parameter_as_abort and \
           isinstance(error, Error) and error.value == Error.INVALID_PARAMETER:
            self.abort_tracking(channel)
            return

        self.parent.increase_error_count()

    def get_monoflop_update_async(self, value, time, time_remaining):
        self.get_monoflop_channel_update_async(None, value, time, time_remaining)

    def get_monoflop_update_async_error(self, error):
        self.get_monoflop_channel_update_async_error(None, error)

    def update(self):
        for channel_index, channel in enumerate(self.channels):
            if not self.running[channel_index]:
                continue

            if channel != None:
                async_call(self.device.get_monoflop, channel, self.get_monoflop_channel_update_async, self.get_monoflop_channel_update_async_error,
                           pass_arguments_to_result_callback=True, pass_arguments_to_error_callback=True, pass_exception_to_error_callback=True,
                           expand_result_tuple_for_callback=True)
            else:
                async_call(self.device.get_monoflop, None, self.get_monoflop_update_async, self.get_monoflop_update_async_error,
                           pass_exception_to_error_callback=True, expand_result_tuple_for_callback=True)

    def abort_tracking(self, channel=None):
        channel_index = self.channels.index(channel)

        if self.running[channel_index]:
            self.time_spinboxes[channel_index].setValue(self.times[channel_index])

        self.running[channel_index] = False

        self.value_comboboxes[channel_index].setEnabled(True)
        self.time_spinboxes[channel_index].setEnabled(True)

        if self.time_remaining_labels[channel_index] != None:
            self.time_remaining_labels[channel_index].setText('0')

        if not any(self.running):
            self.update_timer.stop()

    def active(self, channel=None):
        channel_index = self.channels.index(channel)

        return self.running[channel_index]

    def cb_monoflop_channel_done(self, channel, value):
        if self.callback_uses_bitmasks:
            assert isinstance(channel, int)
            assert isinstance(value, int)

            channels = []
            values = []

            for channel_index in range(len(self.channels)):
                if channel & (1 << channel_index) != 0:
                    channels.append(channel_index)
                    values.append(int(value & (1 << channel_index) != 0))
        else:
            channels = [channel]
            values = [value]

        for channel, value in zip(channels, values):
            self.abort_tracking(channel)

            if self.value_change_callback != None:
                if channel != None:
                    self.value_change_callback(channel, value)
                else:
                    self.value_change_callback(value)

    def cb_monoflop_done(self, value):
        assert not self.callback_uses_bitmasks

        self.cb_monoflop_channel_done(None, value)
