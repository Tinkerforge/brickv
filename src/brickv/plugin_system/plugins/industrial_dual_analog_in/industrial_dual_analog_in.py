# -*- coding: utf-8 -*-
"""
Industrial Dual Analog In Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015-2016 Matthias Bolte <matthias@tinkerforge.com>

industrial_dual_analog_in.py: Industrial Dual Analog In Plugin Implementation

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

import functools

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton, QFrame, QDialog, QMessageBox
from PyQt5.QtCore import Qt

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_industrial_dual_analog_in import BrickletIndustrialDualAnalogIn
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_modeless_dialog_flags
from brickv.plugin_system.plugins.industrial_dual_analog_in.ui_calibration import Ui_Calibration
from brickv.utils import format_voltage

def is_int32(value):
    return value >= -2147483648 and value <= 2147483647

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())
        self.parent = parent

        self.values0 = [0]*10
        self.values1 = [0]*10
        self.values_index = 0

        self.setupUi(self)

        self.button_cal_remove.clicked.connect(self.remove_clicked)
        self.button_cal_offset.clicked.connect(self.offset_clicked)
        self.button_cal_gain.clicked.connect(self.gain_clicked)

        self.cbe_adc = CallbackEmulator(self.parent.analog_in.get_adc_values,
                                        self.cb_adc_values,
                                        self.parent.increase_error_count)

    def show(self):
        QDialog.show(self)

        self.cbe_adc.set_period(100)

        self.current_offset0 = 0
        self.current_offset1 = 0
        self.current_gain0 = 0
        self.current_gain1 = 0

        self.update_calibration()

    def update_calibration(self):
        async_call(self.parent.analog_in.get_calibration, None, self.cb_get_calibration, self.parent.increase_error_count)

    def remove_clicked(self):
        self.parent.analog_in.set_calibration((0, 0), (0, 0))
        self.update_calibration()

    def offset_clicked(self):
        self.parent.analog_in.set_calibration((-sum(self.values0)/10, -sum(self.values1)/10), (self.current_gain0, self.current_gain1))
        self.update_calibration()

    def gain_clicked(self):
        try:
            if self.parent.firmware_version >= (2, 0, 1): # fixed computation in 2.0.1
                measured0 = (sum(self.values0)/10.0)*244/44983
                measured1 = (sum(self.values1)/10.0)*244/44983
            else:
                measured0 = (sum(self.values0)/10.0)*244/38588
                measured1 = (sum(self.values1)/10.0)*244/38588
            factor0 = self.spinbox_voltage_ch0.value()/measured0
            factor1 = self.spinbox_voltage_ch1.value()/measured1
            gain0 = int((factor0-1)*2**23)
            gain1 = int((factor1-1)*2**23)

            if not is_int32(gain0) or not is_int32(gain1):
                raise ValueError("Out of range")
        except:
            QMessageBox.critical(self, "Failure during Calibration", "Calibration values are not in range.", QMessageBox.Ok)
            return

        self.parent.analog_in.set_calibration((self.current_offset0, self.current_offset1), (gain0, gain1))
        self.update_calibration()

    def cb_get_calibration(self, cal):
        self.current_offset0 = cal.offset[0]
        self.current_offset1 = cal.offset[1]
        self.current_gain0 = cal.gain[0]
        self.current_gain1 = cal.gain[1]

        self.label_offset0.setText(str(cal.offset[0]))
        self.label_offset1.setText(str(cal.offset[1]))
        self.label_gain0.setText(str(cal.gain[0]))
        self.label_gain1.setText(str(cal.gain[1]))

    def cb_adc_values(self, values):
        self.values0[self.values_index] = values[0]
        self.values1[self.values_index] = values[1]

        self.values_index += 1
        if self.values_index >= 10:
            self.values_index = 0

        self.label_adc0.setText(str(sum(self.values0)/10))
        self.label_adc1.setText(str(sum(self.values1)/10))

    def closeEvent(self, event):
        self.parent.calibration_button.setEnabled(True)
        self.cbe_adc.set_period(0)

class IndustrialDualAnalogIn(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletIndustrialDualAnalogIn, *args)

        self.analog_in = self.device

        self.cbe_voltage0 = CallbackEmulator(functools.partial(self.analog_in.get_voltage, 0),
                                             functools.partial(self.cb_voltage, 0),
                                             self.increase_error_count)
        self.cbe_voltage1 = CallbackEmulator(functools.partial(self.analog_in.get_voltage, 1),
                                             functools.partial(self.cb_voltage, 1),
                                             self.increase_error_count)

        self.calibration = None

        self.sample_rate_label = QLabel('Sample Rate:')
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItem('976 Hz')
        self.sample_rate_combo.addItem('488 Hz')
        self.sample_rate_combo.addItem('244 Hz')
        self.sample_rate_combo.addItem('122 Hz')
        self.sample_rate_combo.addItem('61 Hz')
        self.sample_rate_combo.addItem('4 Hz')
        self.sample_rate_combo.addItem('2 Hz')
        self.sample_rate_combo.addItem('1 Hz')

        self.current_voltage = [None, None] # float, V
        self.calibration_button = QPushButton('Calibration...')

        self.sample_rate_combo.currentIndexChanged.connect(self.sample_rate_combo_index_changed)
        self.calibration_button.clicked.connect(self.calibration_button_clicked)

        plots = [('Channel 0', Qt.red, lambda: self.current_voltage[0], format_voltage),
                 ('Channel 1', Qt.blue, lambda: self.current_voltage[1], format_voltage)]
        self.plot_widget = PlotWidget('Voltage [V]', plots, y_resolution=0.001)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.sample_rate_label)
        hlayout.addWidget(self.sample_rate_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.calibration_button)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.analog_in.get_voltage, 0, lambda x: self.cb_voltage(0, x), self.increase_error_count)
        async_call(self.analog_in.get_voltage, 1, lambda x: self.cb_voltage(1, x), self.increase_error_count)
        self.cbe_voltage0.set_period(100)
        self.cbe_voltage1.set_period(100)

        async_call(self.analog_in.get_sample_rate, None, self.get_sample_rate_async, self.increase_error_count)
        self.plot_widget.stop = False

    def stop(self):
        self.cbe_voltage0.set_period(0)
        self.cbe_voltage1.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        if self.calibration != None:
            self.calibration.close()

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDualAnalogIn.DEVICE_IDENTIFIER

    def get_voltage_value0(self):
        return self.voltage_value[0]

    def get_voltage_value1(self):
        return self.voltage_value[1]

    def calibration_button_clicked(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.calibration_button.setEnabled(False)
        self.calibration.show()

    def sample_rate_combo_index_changed(self, index):
        async_call(self.analog_in.set_sample_rate, index, None, self.increase_error_count)

    def get_sample_rate_async(self, rate):
        self.sample_rate_combo.setCurrentIndex(rate)

    def cb_voltage(self, sensor, voltage):
        self.current_voltage[sensor] = voltage / 1000.0
