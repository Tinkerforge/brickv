# -*- coding: utf-8 -*-
"""
Thermocouple V2 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

thermocouple_v2.py: Thermocouple V2 Plugin Implementation

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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QFrame

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_thermocouple_v2 import BrickletThermocoupleV2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class ThermocoupleV2(COMCUPluginBase):
    qtcb_error_state = pyqtSignal(bool, bool)

    def __init__(self, *args):
        super().__init__(BrickletThermocoupleV2, *args)

        self.thermo2 = self.device

        self.qtcb_error_state.connect(self.cb_error_state)
        self.thermo2.register_callback(self.thermo2.CALLBACK_ERROR_STATE,
                                      self.qtcb_error_state.emit)

        self.cbe_temperature = CallbackEmulator(self.thermo2.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.current_temperature = None # float, °C

        self.error_label = QLabel('Current Errors: None')
        self.error_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        plots = [('Temperature', Qt.red, lambda: self.current_temperature, '{:.2f} °C'.format)]
        self.plot_widget = PlotWidget('Temperature [°C]', plots, extra_key_widgets=[self.error_label])

        self.averaging_label = QLabel('Averaging:')
        self.averaging_combo = QComboBox()
        self.averaging_combo.addItem('1', BrickletThermocoupleV2.AVERAGING_1)
        self.averaging_combo.addItem('2', BrickletThermocoupleV2.AVERAGING_2)
        self.averaging_combo.addItem('4', BrickletThermocoupleV2.AVERAGING_4)
        self.averaging_combo.addItem('8', BrickletThermocoupleV2.AVERAGING_8)
        self.averaging_combo.addItem('16', BrickletThermocoupleV2.AVERAGING_16)

        self.type_label = QLabel('Thermocouple Type:')
        self.type_combo = QComboBox()
        self.type_combo.addItem('B', BrickletThermocoupleV2.TYPE_B)
        self.type_combo.addItem('E', BrickletThermocoupleV2.TYPE_E)
        self.type_combo.addItem('J', BrickletThermocoupleV2.TYPE_J)
        self.type_combo.addItem('K', BrickletThermocoupleV2.TYPE_K)
        self.type_combo.addItem('N', BrickletThermocoupleV2.TYPE_N)
        self.type_combo.addItem('R', BrickletThermocoupleV2.TYPE_R)
        self.type_combo.addItem('S', BrickletThermocoupleV2.TYPE_S)
        self.type_combo.addItem('T', BrickletThermocoupleV2.TYPE_T)
        self.type_combo.addItem('Gain 8', BrickletThermocoupleV2.TYPE_G8)
        self.type_combo.addItem('Gain 32', BrickletThermocoupleV2.TYPE_G32)

        self.filter_label = QLabel('Noise Rejection Filter:')
        self.filter_combo = QComboBox()
        self.filter_combo.addItem('50 Hz', BrickletThermocoupleV2.FILTER_OPTION_50HZ)
        self.filter_combo.addItem('60 Hz', BrickletThermocoupleV2.FILTER_OPTION_60HZ)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.averaging_label)
        hlayout.addWidget(self.averaging_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.type_label)
        hlayout.addWidget(self.type_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.filter_label)
        hlayout.addWidget(self.filter_combo)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

        self.averaging_combo.currentIndexChanged.connect(self.configuration_changed)
        self.type_combo.currentIndexChanged.connect(self.configuration_changed)
        self.filter_combo.currentIndexChanged.connect(self.configuration_changed)

    def start(self):
        async_call(self.thermo2.get_temperature, None, self.cb_temperature, self.increase_error_count)
        async_call(self.thermo2.get_configuration, None, self.cb_configuration, self.increase_error_count)
        async_call(self.thermo2.get_error_state, None, lambda e: self.cb_error_state(e.over_under, e.open_circuit))
        self.cbe_temperature.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_temperature.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletThermocoupleV2.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def configuration_changed(self, _):
        conf_averaging = self.averaging_combo.itemData(self.averaging_combo.currentIndex())
        conf_type = self.type_combo.itemData(self.type_combo.currentIndex())
        conf_filter = self.filter_combo.itemData(self.filter_combo.currentIndex())

        self.thermo2.set_configuration(conf_averaging, conf_type, conf_filter)

    def cb_temperature(self, temperature):
        self.current_temperature = temperature / 100.0

    def cb_configuration(self, conf):
        self.averaging_combo.blockSignals(True)
        self.averaging_combo.setCurrentIndex(self.averaging_combo.findData(conf.averaging))
        self.averaging_combo.blockSignals(False)

        self.type_combo.blockSignals(True)
        self.type_combo.setCurrentIndex(self.type_combo.findData(conf.thermocouple_type))
        self.type_combo.blockSignals(False)

        self.filter_combo.blockSignals(True)
        self.filter_combo.setCurrentIndex(self.filter_combo.findData(conf.filter))
        self.filter_combo.blockSignals(False)

    def cb_error_state(self, over_under, open_circuit):
        if over_under or open_circuit:
            text = 'Current Errors: '
            if over_under:
                text += 'Over/Under Voltage'
            if over_under and open_circuit:
                text += ' and '
            if open_circuit:
                text += 'Open Circuit\n(defective thermocouple or nothing connected)'

            self.error_label.setStyleSheet('QLabel { color : red }')
            self.error_label.setText(text)
        else:
            self.error_label.setStyleSheet('')
            self.error_label.setText('Current Errors: None')
