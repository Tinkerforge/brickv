# -*- coding: utf-8 -*-
"""
AC Current Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

ac_current.py: AC Current Plugin Implementation

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_ac_current import BrickletACCurrent
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class CurrentLabel(QLabel):
    def setText(self, text):
        text = "Current: " + text + " A"
        super(CurrentLabel, self).setText(text)

class ACCurrent(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletACCurrent, *args)

        self.acc = self.device

        self.cbe_current = CallbackEmulator(self.acc.get_current,
                                            self.cb_current,
                                            self.increase_error_count)

        self.current_label = CurrentLabel('Current: ')

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Current [A]', plot_list)

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.current_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

        self.label_average = QLabel('Length of moving average:')
        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(1)
        self.spin_average.setMaximum(50)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(50)
        self.spin_average.editingFinished.connect(self.spin_average_finished)
        
        self.label_range = QLabel('Current Range: ')
        self.combo_range = QComboBox()
        self.combo_range.addItem("0") # TODO: Adjust ranges
        self.combo_range.addItem("1")
        self.combo_range.currentIndexChanged.connect(self.new_config)

        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.label_average)
        layout_h1.addWidget(self.spin_average)
        layout_h1.addStretch()
        layout_h1.addWidget(self.label_range)
        layout_h1.addWidget(self.combo_range)
        layout_h1.addStretch()
        layout.addLayout(layout_h1)
        
    def get_configuration_async(self, conf):
        self.combo_range.setCurrentIndex(conf)

    def get_moving_average_async(self, average):
        self.spin_average.setValue(average)
        
    def new_config(self, value):
        try:
            self.acc.set_configuration(value)
        except:
            pass

    def start(self):
        async_call(self.acc.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.acc.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.acc.get_current, None, self.cb_current, self.increase_error_count)
        self.cbe_current.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_current.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'ac_current'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletACCurrent.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_current(self, current):
        c = round(current/1000.0, 2)
        self.current_value = c
        self.current_label.setText('%6.02f' % c)

    def spin_average_finished(self):
        self.acc.set_moving_average(self.spin_average.value())
