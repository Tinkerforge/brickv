# -*- coding: utf-8 -*-
"""
Load Cell 2.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

load_cell_v2.py: Load Cell 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, \
                            QPushButton, QFrame, QComboBox, QDialog

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_load_cell_v2 import BrickletLoadCellV2
from brickv.plugin_system.plugins.load_cell.ui_calibration import Ui_Calibration
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_modeless_dialog_flags

def format_weight(value): # int, g
    if abs(value) < 1000:
        return '{} g'.format(value)
    else:
        return '{:.3f} kg'.format(round(value / 1000.0, 3))

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.parent = parent
        self.lc = parent.lc

        self.button_zero.clicked.connect(self.button_zero_clicked)
        self.button_weight.clicked.connect(self.button_weight_clicked)
        self.button_weight.setEnabled(False)

        self.label_step1.setStyleSheet('QLabel { color : red }')
        self.label_step2.setStyleSheet('')
        self.label_status.setText('Calibration in progress...')

    def button_zero_clicked(self):
        self.lc.calibrate(0)
        self.button_weight.setEnabled(True)

        self.label_step1.setStyleSheet('')
        self.label_step2.setStyleSheet('QLabel { color : red }')

    def button_weight_clicked(self):
        self.lc.calibrate(self.spin_weight.value())

        self.label_step1.setStyleSheet('')
        self.label_step2.setStyleSheet('')
        self.label_status.setText('The new calibration is now saved in the flash.')

    def closeEvent(self, event):
        self.parent.button_calibration.setEnabled(True)
        self.parent.calibration = None

class LoadCellV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletLoadCellV2, *args)

        self.lc = self.device

        self.cbe_weight = CallbackEmulator(self.lc.get_weight,
                                           self.cb_weight,
                                           self.increase_error_count)

        self.current_weight = CurveValueWrapper() # int, g
        self.calibration = None

        plots = [('Weight', Qt.red, self.current_weight, format_weight)]
        self.plot_widget = PlotWidget('Weight [g]', plots, y_resolution=1.0)

        self.button_calibration = QPushButton("Calibration...")
        self.button_calibration.clicked.connect(self.button_calibration_clicked)

        self.button_tare = QPushButton("Tare")
        self.button_tare.clicked.connect(self.button_tare_clicked)

        self.cbox_info_led_config = QComboBox()
        self.cbox_info_led_config.addItem("Off")
        self.cbox_info_led_config.addItem("On")
        self.cbox_info_led_config.addItem("Heartbeat")
        self.cbox_info_led_config.currentIndexChanged.connect(self.cbox_info_led_config_changed)
        self.label_info_led_config = QLabel('Info LED:')

        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(0)
        self.spin_average.setMaximum(40)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(5)
        self.spin_average.editingFinished.connect(self.spin_average_finished)
        self.label_average = QLabel('Moving Average Length:')

        self.rate_label = QLabel('Rate:')
        self.rate_combo = QComboBox()
        self.rate_combo.addItem("10 Hz")
        self.rate_combo.addItem("80 Hz")
        self.rate_combo.currentIndexChanged.connect(self.new_config)

        self.gain_label = QLabel('Gain:')
        self.gain_combo = QComboBox()
        self.gain_combo.addItem("128x")
        self.gain_combo.addItem("64x")
        self.gain_combo.addItem("32x")
        self.gain_combo.currentIndexChanged.connect(self.new_config)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.label_average)
        hlayout.addWidget(self.spin_average)
        hlayout.addWidget(self.rate_label)
        hlayout.addWidget(self.rate_combo)
        hlayout.addWidget(self.gain_label)
        hlayout.addWidget(self.gain_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.button_calibration)
        hlayout.addWidget(self.button_tare)
        hlayout.addWidget(self.label_info_led_config)
        hlayout.addWidget(self.cbox_info_led_config)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.lc.get_info_led_config, None, self.get_info_led_config_async, self.increase_error_count)
        async_call(self.lc.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.lc.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.lc.get_weight, None, self.cb_weight, self.increase_error_count)
        self.cbe_weight.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_weight.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        if self.calibration != None:
            self.calibration.close()

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLoadCellV2.DEVICE_IDENTIFIER

    def get_moving_average_async(self, avg):
        self.spin_average.setValue(avg)

    def get_configuration_async(self, conf):
        self.gain_combo.setCurrentIndex(conf.gain)
        self.rate_combo.setCurrentIndex(conf.rate)

    def get_info_led_config_async(self, value):
        self.cbox_info_led_config.setCurrentIndex(value)

    def button_calibration_clicked(self):
        if self.calibration is None:
            self.calibration = Calibration(self)

        self.button_calibration.setEnabled(False)
        self.calibration.show()

    def button_tare_clicked(self):
        self.lc.tare()

    def cbox_info_led_config_changed(self, index):
        self.lc.set_info_led_config(index)

        async_call(self.lc.get_info_led_config,
                   None, self.get_info_led_config_async,
                   self.increase_error_count)

    def new_config(self, value):
        rate = self.rate_combo.currentIndex()
        gain = self.gain_combo.currentIndex()

        self.lc.set_configuration(rate, gain)

    def spin_average_finished(self):
        self.lc.set_moving_average(self.spin_average.value())

    def cb_weight(self, weight):
        self.current_weight.value = weight
