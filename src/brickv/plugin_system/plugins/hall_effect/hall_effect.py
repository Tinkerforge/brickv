# -*- coding: utf-8 -*-
"""
Hall Effect Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

hall_effect.py: Hall Effect Plugin Implementation

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, \
                        QComboBox, QPushButton

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_hall_effect import BrickletHallEffect
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget, CurveValueWrapper, FixedSizeLabel
from brickv.callback_emulator import CallbackEmulator

class CountLabel(FixedSizeLabel):
    def setText(self, text):
        text = 'Count: ' + str(text)
        super().setText(text)

class HallEffect(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletHallEffect, *args)

        self.hf = self.device

        self.cbe_edge_count = CallbackEmulator(self.get_edge_count,
                                               self.cb_edge_count,
                                               self.increase_error_count)

        self.current_value = CurveValueWrapper()

        self.label_count = CountLabel('Count')

        plots = [('Value', Qt.red, self.current_value, str)]
        self.plot_widget = PlotWidget('Value', plots, extra_key_widgets=[self.label_count],
                                      curve_motion_granularity=20, update_interval=0.05)
        self.plot_widget.set_fixed_y_scale(0, 1, 1, 1)

        self.combo_edge_type = QComboBox()
        self.combo_edge_type.addItem('Rising')
        self.combo_edge_type.addItem('Falling')
        self.combo_edge_type.addItem('Both')
        self.combo_edge_type.currentIndexChanged.connect(self.edge_changed)

        self.spin_debounce = QSpinBox()
        self.spin_debounce.setMinimum(0)
        self.spin_debounce.setMaximum(255)
        self.spin_debounce.setValue(100)
        self.spin_debounce.editingFinished.connect(self.debounce_changed)

        self.button_reset = QPushButton('Reset Count')
        self.button_reset.clicked.connect(self.reset_count)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('Edge Type:'))
        hlayout.addWidget(self.combo_edge_type)
        hlayout.addStretch()
        hlayout.addWidget(QLabel('Debounce Period [ms]:'))
        hlayout.addWidget(self.spin_debounce)
        hlayout.addStretch()
        hlayout.addWidget(self.button_reset)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def debounce_changed(self):
        self.hf.set_edge_count_config(self.combo_edge_type.currentIndex(), self.spin_debounce.value())

    def edge_changed(self, _value):
        self.hf.set_edge_count_config(self.combo_edge_type.currentIndex(), self.spin_debounce.value())

    def get_edge_count(self):
        return self.hf.get_edge_count(False), self.hf.get_value()

    def cb_edge_count(self, data):
        count, value = data

        if value:
            self.current_value.value = 1
        else:
            self.current_value.value = 0

        self.label_count.setText(count)

    def cb_edge_count_config(self, conf):
        edge_type, debounce = conf
        self.combo_edge_type.setCurrentIndex(edge_type)
        self.spin_debounce.setValue(debounce)

    def get_edge_count_async(self, count):
        self.label_count.setText(count)

    def get_value_async(self, value):
        if value:
            self.current_value.value = 1
        else:
            self.current_value.value = 0

    def reset_count(self):
        self.hf.get_edge_count(True)

    def start(self):
        async_call(self.hf.get_edge_count_config, None, self.cb_edge_count_config, self.increase_error_count)
        async_call(self.hf.get_edge_count, False, self.get_edge_count_async, self.increase_error_count)
        async_call(self.hf.get_value, None, self.get_value_async, self.increase_error_count)
        self.cbe_edge_count.set_period(50)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_edge_count.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHallEffect.DEVICE_IDENTIFIER
