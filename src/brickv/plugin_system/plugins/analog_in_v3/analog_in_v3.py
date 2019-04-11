# -*- coding: utf-8 -*-
"""
Analog In 3.0 Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

analog_in_v3.py: Analog In 3.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QFrame, QComboBox, QDialog, QPushButton

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_analog_in_v3 import BrickletAnalogInV3
from brickv.plugin_system.plugins.analog_in_v3.ui_calibration import Ui_Calibration
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_voltage
from brickv.utils import get_modeless_dialog_flags

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())
        self.parent = parent

        self.setupUi(self)

        self.current_value = 0

        self.button_cal_remove.clicked.connect(self.remove_clicked)
        self.button_cal_offset.clicked.connect(self.offset_clicked)
        self.button_cal_gain.clicked.connect(self.gain_clicked)

        self.cbe_voltage = CallbackEmulator(self.parent.ai.get_voltage,
                                            self.cb_voltage,
                                            self.parent.increase_error_count)

    def show(self):
        QDialog.show(self)

        self.cbe_voltage.set_period(100)

        self.current_value = 0
        self.current_offset = 0
        self.current_multiplier = 0
        self.current_divisor = 0

        self.update_calibration()

    def update_calibration(self):
        async_call(self.parent.ai.get_calibration, None, self.get_calibration_async, self.parent.increase_error_count)

    def remove_clicked(self):
        self.parent.ai.set_calibration(0, 1, 1)
        self.update_calibration()

    def offset_clicked(self):
        self.parent.ai.set_calibration(-self.current_value, 1, 1)
        self.update_calibration()

    def gain_clicked(self):
        self.parent.ai.set_calibration(self.current_offset, self.spinbox_voltage.value(), self.current_value)
        self.update_calibration()

    def get_calibration_async(self, cal):
        self.current_offset     = cal.offset
        self.current_multiplier = cal.multiplier
        self.current_divisor    = cal.divisor

        self.label_offset.setText(str(cal.offset))
        self.label_multiplier.setText(str(cal.multiplier))
        self.label_divisor.setText(str(cal.divisor))

    def cb_voltage(self, value):
        self.current_value = value
        self.label_voltage.setText(str(value) + " mV")

    def closeEvent(self, event):
        self.parent.calibration_button.setEnabled(True)
        self.cbe_voltage.set_period(0)

class AnalogInV3(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletAnalogInV3, *args)

        self.ai = self.device

        self.cbe_voltage = CallbackEmulator(self.ai.get_voltage,
                                            self.cb_voltage,
                                            self.increase_error_count)

        self.current_voltage = CurveValueWrapper() # float, V

        plots = [('Voltage', Qt.red, self.current_voltage, format_voltage)]
        self.plot_widget = PlotWidget('Voltage [V]', plots, y_resolution=0.001)

        self.oversampling_combo = QComboBox()
        self.oversampling_combo.addItem('32x (0.56ms)')
        self.oversampling_combo.addItem('64x (1.12ms)')
        self.oversampling_combo.addItem('128x (2.24ms)')
        self.oversampling_combo.addItem('256x (4.48ms)')
        self.oversampling_combo.addItem('512x (8.96ms)')
        self.oversampling_combo.addItem('1024x (17.92ms)')
        self.oversampling_combo.addItem('2048x (35.84ms)')
        self.oversampling_combo.addItem('4096x (71.68ms)')
        self.oversampling_combo.addItem('8192x (143.36ms)')
        self.oversampling_combo.addItem('16384x (286.72ms)')

        self.oversampling_combo.currentIndexChanged.connect(self.oversampling_combo_index_changed)

        self.calibration = None
        self.calibration_button = QPushButton('Calibration...')
        self.calibration_button.clicked.connect(self.calibration_button_clicked)

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(QLabel('Oversampling:'))
        layout_h1.addWidget(self.oversampling_combo)
        layout_h1.addStretch()
        layout_h1.addWidget(self.calibration_button)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(layout_h1)

    def calibration_button_clicked(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.calibration_button.setEnabled(False)
        self.calibration.show()

    def get_oversampling_async(self, oversampling):
        self.oversampling_combo.setCurrentIndex(oversampling)

    def start(self):
        async_call(self.ai.get_oversampling, None, self.get_oversampling_async, self.increase_error_count)

        self.cbe_voltage.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_voltage.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        if self.calibration != None:
            self.calibration.close()

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogInV3.DEVICE_IDENTIFIER

    def cb_voltage(self, voltage):
        self.current_voltage.value = voltage / 1000.0

    def oversampling_combo_index_changed(self, index):
        async_call(self.ai.set_oversampling, index, None, self.increase_error_count)
