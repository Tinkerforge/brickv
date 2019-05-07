# -*- coding: utf-8 -*-
"""
Industrial Dual Analog In 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

industrial_dual_analog_in_v2.py: Industrial Dual Analog In 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, \
                            QComboBox, QPushButton, QFrame, QDialog, QMessageBox, \
                            QSizePolicy, QSpinBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_industrial_dual_analog_in_v2 import BrickletIndustrialDualAnalogInV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
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

        self.values0 = [0] * 10
        self.values1 = [0] * 10
        self.values_index = 0

        self.setupUi(self)

        self.button_cal_remove.clicked.connect(self.remove_clicked)
        self.button_cal_offset.clicked.connect(self.offset_clicked)
        self.button_cal_gain.clicked.connect(self.gain_clicked)

        self.cbe_adc_values = CallbackEmulator(self.parent.analog_in.get_adc_values,
                                               None,
                                               self.cb_adc_values,
                                               self.parent.increase_error_count)

    def show(self):
        QDialog.show(self)

        self.cbe_adc_values.set_period(100)

        self.current_offset0 = 0
        self.current_offset1 = 0
        self.current_gain0 = 0
        self.current_gain1 = 0

        self.update_calibration()

    def update_calibration(self):
        async_call(self.parent.analog_in.get_calibration, None, self.get_calibration_async, self.parent.increase_error_count)

    def remove_clicked(self):
        self.parent.analog_in.set_calibration((0, 0), (0, 0))
        self.update_calibration()

    def offset_clicked(self):
        self.parent.analog_in.set_calibration((-sum(self.values0)//10, -sum(self.values1)//10), (self.current_gain0, self.current_gain1))
        self.update_calibration()

    def gain_clicked(self):
        try:
            measured0 = (sum(self.values0)/10.0)*244/44983
            measured1 = (sum(self.values1)/10.0)*244/44983
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

    def get_calibration_async(self, cal):
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

        self.label_adc0.setText(str(sum(self.values0)//10))
        self.label_adc1.setText(str(sum(self.values1)//10))

    def closeEvent(self, event):
        self.parent.calibration_button.setEnabled(True)
        self.cbe_adc_values.set_period(0)

class IndustrialDualAnalogInV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletIndustrialDualAnalogInV2, *args)

        self.analog_in = self.device

        self.cbe_voltage0 = CallbackEmulator(self.analog_in.get_voltage,
                                             0,
                                             self.cb_voltage,
                                             self.increase_error_count,
                                             pass_arguments_to_result_callback=True)

        self.cbe_voltage1 = CallbackEmulator(self.analog_in.get_voltage,
                                             1,
                                             self.cb_voltage,
                                             self.increase_error_count,
                                             pass_arguments_to_result_callback=True)

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

        self.current_voltage = [CurveValueWrapper(), CurveValueWrapper()] # float, V
        self.calibration_button = QPushButton('Calibration...')

        self.sample_rate_combo.currentIndexChanged.connect(self.sample_rate_combo_index_changed)
        self.calibration_button.clicked.connect(self.calibration_button_clicked)

        plots = [('Channel 0', Qt.red, self.current_voltage[0], format_voltage),
                 ('Channel 1', Qt.blue, self.current_voltage[1], format_voltage)]
        self.plot_widget = PlotWidget('Voltage [V]', plots, y_resolution=0.001)

        # Define lines
        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        line1 = QFrame()
        line1.setObjectName("line1")
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame()
        line2.setObjectName("line2")
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        # Define channel LED status config widgets
        self.led_config_ch0_label = QLabel('Channel 0')
        self.led_config_ch1_label = QLabel('Channel 1')
        self.led_config_label = QLabel('LED Config:')
        self.led_status_config_label = QLabel('LED Status Config:')
        self.led_status_config_ch0_min_label = QLabel('Min:')
        self.led_status_config_ch0_max_label = QLabel('Max:')
        self.led_status_config_ch1_min_label = QLabel('Min:')
        self.led_status_config_ch1_max_label = QLabel('Max:')

        self.led_config_ch0_combo = QComboBox()
        self.led_config_ch0_combo.addItem('Off')
        self.led_config_ch0_combo.addItem('On')
        self.led_config_ch0_combo.addItem('Show Heartbeat')
        self.led_config_ch0_combo.addItem('Show Channel Status')
        self.led_config_ch0_combo.currentIndexChanged.connect(self.led_config_ch0_combo_changed)

        self.led_config_ch1_combo = QComboBox()
        self.led_config_ch1_combo.addItem('Off')
        self.led_config_ch1_combo.addItem('On')
        self.led_config_ch1_combo.addItem('Show Heartbeat')
        self.led_config_ch1_combo.addItem('Show Channel Status')
        self.led_config_ch1_combo.currentIndexChanged.connect(self.led_config_ch1_combo_changed)

        self.led_status_config_ch0_combo = QComboBox()
        self.led_status_config_ch0_combo.addItem('Threshold')
        self.led_status_config_ch0_combo.addItem('Intensity')
        self.led_status_config_ch0_combo.currentIndexChanged.connect(self.led_status_config_ch0_combo_changed)

        self.led_status_config_ch1_combo = QComboBox()
        self.led_status_config_ch1_combo.addItem('Threshold')
        self.led_status_config_ch1_combo.addItem('Intensity')
        self.led_status_config_ch1_combo.currentIndexChanged.connect(self.led_status_config_ch1_combo_changed)

        self.led_status_config_ch0_min_sbox = QSpinBox()
        self.led_status_config_ch0_min_sbox.setMinimum(-35000)
        self.led_status_config_ch0_min_sbox.setMaximum(35000)
        self.led_status_config_ch0_min_sbox.setValue(0)
        self.led_status_config_ch0_min_sbox.setSingleStep(1)
        self.led_status_config_ch0_min_sbox.setSuffix(' mV')
        self.led_status_config_ch0_min_sbox.valueChanged.connect(self.led_status_config_ch0_min_sbox_changed)

        self.led_status_config_ch0_max_sbox = QSpinBox()
        self.led_status_config_ch0_max_sbox.setMinimum(-35000)
        self.led_status_config_ch0_max_sbox.setMaximum(35000)
        self.led_status_config_ch0_max_sbox.setValue(0)
        self.led_status_config_ch0_max_sbox.setSingleStep(1)
        self.led_status_config_ch0_max_sbox.setSuffix(' mV')
        self.led_status_config_ch0_max_sbox.valueChanged.connect(self.led_status_config_ch0_max_sbox_changed)

        self.led_status_config_ch1_min_sbox = QSpinBox()
        self.led_status_config_ch1_min_sbox.setMinimum(-35000)
        self.led_status_config_ch1_min_sbox.setMaximum(35000)
        self.led_status_config_ch1_min_sbox.setValue(0)
        self.led_status_config_ch1_min_sbox.setSingleStep(1)
        self.led_status_config_ch1_min_sbox.setSuffix(' mV')
        self.led_status_config_ch1_min_sbox.valueChanged.connect(self.led_status_config_ch1_min_sbox_changed)

        self.led_status_config_ch1_max_sbox = QSpinBox()
        self.led_status_config_ch1_max_sbox.setMinimum(-35000)
        self.led_status_config_ch1_max_sbox.setMaximum(35000)
        self.led_status_config_ch1_max_sbox.setValue(0)
        self.led_status_config_ch1_max_sbox.setSingleStep(1)
        self.led_status_config_ch1_max_sbox.setSuffix(' mV')
        self.led_status_config_ch1_max_sbox.valueChanged.connect(self.led_status_config_ch1_max_sbox_changed)

        # Define size policies
        h_sp = QSizePolicy()
        h_sp.setHorizontalPolicy(QSizePolicy.Expanding)

        # Set size policies
        self.sample_rate_combo.setSizePolicy(h_sp)
        self.led_config_ch0_combo.setSizePolicy(h_sp)
        self.led_config_ch1_combo.setSizePolicy(h_sp)
        self.led_status_config_ch0_combo.setSizePolicy(h_sp)
        self.led_status_config_ch1_combo.setSizePolicy(h_sp)
        self.led_status_config_ch0_min_sbox.setSizePolicy(h_sp)
        self.led_status_config_ch0_max_sbox.setSizePolicy(h_sp)
        self.led_status_config_ch1_min_sbox.setSizePolicy(h_sp)
        self.led_status_config_ch1_max_sbox.setSizePolicy(h_sp)

        # Define layouts
        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        glayout = QGridLayout()
        layout = QVBoxLayout(self)
        hlayout_ch0_min_max = QHBoxLayout()
        hlayout_ch1_min_max = QHBoxLayout()

        # Populate layouts
        vlayout.addWidget(self.calibration_button)
        hlayout.addWidget(self.sample_rate_label)
        hlayout.addWidget(self.sample_rate_combo)
        vlayout.addLayout(hlayout)
        vlayout.addWidget(line1)

        hlayout_ch0_min_max.addWidget(self.led_status_config_ch0_min_label)
        hlayout_ch0_min_max.addWidget(self.led_status_config_ch0_min_sbox)
        hlayout_ch0_min_max.addWidget(self.led_status_config_ch0_max_label)
        hlayout_ch0_min_max.addWidget(self.led_status_config_ch0_max_sbox)

        hlayout_ch1_min_max.addWidget(self.led_status_config_ch1_min_label)
        hlayout_ch1_min_max.addWidget(self.led_status_config_ch1_min_sbox)
        hlayout_ch1_min_max.addWidget(self.led_status_config_ch1_max_label)
        hlayout_ch1_min_max.addWidget(self.led_status_config_ch1_max_sbox)

        glayout.addWidget(self.led_config_ch0_label, 0, 1, 1, 1) # R, C, RS, CS
        glayout.addWidget(self.led_config_ch1_label, 0, 2, 1, 1)

        glayout.addWidget(line2, 1, 0, 1, 3)

        glayout.addWidget(self.led_config_label, 2, 0, 1, 1)
        glayout.addWidget(self.led_config_ch0_combo, 2, 1, 1, 1)
        glayout.addWidget(self.led_config_ch1_combo, 2, 2, 1, 1)

        glayout.addWidget(self.led_status_config_label, 3, 0, 1, 1)
        glayout.addWidget(self.led_status_config_ch0_combo, 3, 1, 1, 1)
        glayout.addWidget(self.led_status_config_ch1_combo, 3, 2, 1, 1)

        glayout.addLayout(hlayout_ch0_min_max, 4, 1, 1, 1)
        glayout.addLayout(hlayout_ch1_min_max, 4, 2, 1, 1)

        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(vlayout)
        layout.addLayout(glayout)

        self.ui_group_ch_status_ch0 = [self.led_status_config_ch0_combo,
                                       self.led_status_config_ch0_min_sbox,
                                       self.led_status_config_ch0_max_sbox]

        self.ui_group_ch_status_ch1 = [self.led_status_config_ch1_combo,
                                       self.led_status_config_ch1_min_sbox,
                                       self.led_status_config_ch1_max_sbox]

    def start(self):
        async_call(self.analog_in.get_sample_rate, None, self.get_sample_rate_async, self.increase_error_count)

        for channel in range(2):
            async_call(self.analog_in.get_channel_led_config, channel, self.get_channel_led_config_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True)
            async_call(self.analog_in.get_channel_led_status_config, channel, self.get_channel_led_status_config_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True)

        self.cbe_voltage0.set_period(100)
        self.cbe_voltage1.set_period(100)

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
        return device_identifier == BrickletIndustrialDualAnalogInV2.DEVICE_IDENTIFIER

    def calibration_button_clicked(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.calibration_button.setEnabled(False)
        self.calibration.show()

    def sample_rate_combo_index_changed(self, index):
        async_call(self.analog_in.set_sample_rate, index, None, self.increase_error_count)

    def led_config_ch0_combo_changed(self, index):
        if index != self.analog_in.CHANNEL_LED_CONFIG_SHOW_CHANNEL_STATUS:
            for e in self.ui_group_ch_status_ch0:
                e.setEnabled(False)
        else:
            for e in self.ui_group_ch_status_ch0:
                e.setEnabled(True)

        self.analog_in.set_channel_led_config(0, index)

    def led_config_ch1_combo_changed(self, index):
        if index != self.analog_in.CHANNEL_LED_CONFIG_SHOW_CHANNEL_STATUS:
            for e in self.ui_group_ch_status_ch1:
                e.setEnabled(False)
        else:
            for e in self.ui_group_ch_status_ch1:
                e.setEnabled(True)

        self.analog_in.set_channel_led_config(1, index)

    def led_status_config_ch0_combo_changed(self, index):
        self.analog_in.set_channel_led_status_config(0,
                                                     self.led_status_config_ch0_min_sbox.value(),
                                                     self.led_status_config_ch0_max_sbox.value(),
                                                     index)

    def led_status_config_ch1_combo_changed(self, index):
        self.analog_in.set_channel_led_status_config(1,
                                                     self.led_status_config_ch1_min_sbox.value(),
                                                     self.led_status_config_ch1_max_sbox.value(),
                                                     index)

    def led_status_config_ch0_min_sbox_changed(self, value):
        self.analog_in.set_channel_led_status_config(0,
                                                     self.led_status_config_ch0_min_sbox.value(),
                                                     self.led_status_config_ch0_max_sbox.value(),
                                                     self.led_status_config_ch0_combo.currentIndex())

    def led_status_config_ch0_max_sbox_changed(self, value):
        self.analog_in.set_channel_led_status_config(0,
                                                     self.led_status_config_ch0_min_sbox.value(),
                                                     self.led_status_config_ch0_max_sbox.value(),
                                                     self.led_status_config_ch0_combo.currentIndex())

    def led_status_config_ch1_min_sbox_changed(self, value):
        self.analog_in.set_channel_led_status_config(1,
                                                     self.led_status_config_ch1_min_sbox.value(),
                                                     self.led_status_config_ch1_max_sbox.value(),
                                                     self.led_status_config_ch1_combo.currentIndex())

    def led_status_config_ch1_max_sbox_changed(self, value):
        self.analog_in.set_channel_led_status_config(1,
                                                     self.led_status_config_ch1_min_sbox.value(),
                                                     self.led_status_config_ch1_max_sbox.value(),
                                                     self.led_status_config_ch1_combo.currentIndex())

    def get_voltage_value0(self):
        return self.voltage_value[0]

    def get_voltage_value1(self):
        return self.voltage_value[1]

    def get_sample_rate_async(self, rate):
        self.sample_rate_combo.blockSignals(True)

        self.sample_rate_combo.setCurrentIndex(rate)

        self.sample_rate_combo.blockSignals(False)

    def get_channel_led_config_async(self, channel, config):
        self.led_config_ch0_combo.blockSignals(True)
        self.led_config_ch1_combo.blockSignals(True)

        if channel == 0:
            self.led_config_ch0_combo.setCurrentIndex(config)
        elif channel == 1:
            self.led_config_ch1_combo.setCurrentIndex(config)

        self.led_config_ch0_combo.blockSignals(False)
        self.led_config_ch1_combo.blockSignals(False)

    def get_channel_led_status_config_async(self, channel, config):
        self.led_status_config_ch0_combo.blockSignals(True)
        self.led_status_config_ch1_combo.blockSignals(True)

        if channel == 0:
            self.led_status_config_ch0_combo.setCurrentIndex(config.config)
            self.led_status_config_ch0_max_sbox.setValue(config.max)
            self.led_status_config_ch0_min_sbox.setValue(config.min)
        elif channel == 1:
            self.led_status_config_ch1_combo.setCurrentIndex(config.config)
            self.led_status_config_ch1_max_sbox.setValue(config.max)
            self.led_status_config_ch1_min_sbox.setValue(config.min)

        self.led_status_config_ch0_combo.blockSignals(False)
        self.led_status_config_ch1_combo.blockSignals(False)

    def cb_voltage(self, sensor, voltage):
        self.current_voltage[sensor].value = voltage / 1000.0
