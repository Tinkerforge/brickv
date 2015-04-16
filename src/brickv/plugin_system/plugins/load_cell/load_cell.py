# -*- coding: utf-8 -*-  
"""
Load Cell Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

load_cell.py: Load Cell Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, \
                        QPushButton, QFrame, QComboBox, QCheckBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_load_cell import BrickletLoadCell
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class WeightLabel(QLabel):
    def setText(self, weight):
        if weight < 1000:
            text = "Weight: " + str(weight) + " g"
        else:
            text = "Weight: " + "{0:.3f}".format(round(weight/1000.0, 3)) + " kg"
        super(WeightLabel, self).setText(text)
    
class LoadCell(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletLoadCell, *args)
        
        self.lc = self.device

        self.cbe_weight = CallbackEmulator(self.lc.get_weight,
                                           self.cb_weight,
                                           self.increase_error_count)

        self.weight_label = WeightLabel()
        
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Weight [g]', plot_list)
        
        self.button_zero = QPushButton("Calibrate Zero")
        self.button_calibrate = QPushButton("Calibrate Weight")
        self.spin_calibrate = QSpinBox()
        self.spin_calibrate.setMinimum(100)
        self.spin_calibrate.setMaximum(1000*1000*1000) # 1 ton
        self.spin_calibrate.setSingleStep(100)
        self.label_average = QLabel('Current Weight (g):')
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.label_calibrate = QLabel('To calibrate your Load Cell Bricklet you have to\n 1) Empty the scale and press "Calibrate Zero".\n 2) Add a known weight to the scale, enter it as "Current Weight" and press "Calibrate Weight".\nThe calibration is saved on the EEPROM and only has to be done once.')
        
        self.button_zero.pressed.connect(self.button_zero_pressed)
        self.button_calibrate.pressed.connect(self.button_calibrate_pressed)
        layout_cal1 = QHBoxLayout()
        layout_cal1.addWidget(self.button_zero)
        layout_cal1.addStretch()
        
        layout_cal2 = QHBoxLayout()
        layout_cal2.addWidget(self.button_calibrate)
        layout_cal2.addWidget(self.label_average)
        layout_cal2.addWidget(self.spin_calibrate)
        layout_cal2.addStretch()
        
        self.enable_led = QCheckBox("LED On")
        self.enable_led.stateChanged.connect(self.enable_led_changed)
        
        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(0)
        self.spin_average.setMaximum(40)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(5)
        self.spin_average.editingFinished.connect(self.spin_average_finished)
        self.label_average = QLabel('Length of moving average:')
        layout_avg = QHBoxLayout()
        layout_avg.addWidget(self.label_average)
        layout_avg.addWidget(self.spin_average)
        layout_avg.addStretch()
        layout_avg.addWidget(self.enable_led)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.weight_label)
        layout_h.addStretch()
        
        self.gain_label = QLabel('Gain: ')
        self.gain_combo = QComboBox()
        self.gain_combo.addItem("128x")
        self.gain_combo.addItem("64x")
        self.gain_combo.addItem("32x")
        self.gain_combo.activated.connect(self.new_config)
        
        self.rate_label = QLabel('Rate: ')
        self.rate_combo = QComboBox()
        self.rate_combo.addItem("10Hz")
        self.rate_combo.addItem("80Hz")
        self.rate_combo.activated.connect(self.new_config)
        
        self.label_configuration = QLabel('Increasing the rate will increase the samples per second but also increase the noise on the data.\nChanging the gain is only necessary if your load cell is out of range. 128x is most likely OK.\nThe Gain and Rate configuration is also saved on the EEPROm and only has to be done once.')
        
        layout_hc = QHBoxLayout()
        layout_hc.addWidget(self.rate_label)
        layout_hc.addWidget(self.rate_combo)
        layout_hc.addWidget(self.gain_label)
        layout_hc.addWidget(self.gain_combo)
        layout_hc.addStretch()
       
        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_avg)
        layout.addWidget(self.line)
        layout.addWidget(self.label_calibrate)
        layout.addLayout(layout_cal1)
        layout.addLayout(layout_cal2)
        layout.addWidget(self.label_configuration)
        layout.addLayout(layout_hc)

    def start(self):
        async_call(self.lc.is_led_on, None, self.is_led_on_async, self.increase_error_count)
        async_call(self.lc.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.lc.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.lc.get_weight, None, self.cb_weight, self.increase_error_count)
        self.cbe_weight.set_period(100)
        
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_weight.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'load_cell'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLoadCell.DEVICE_IDENTIFIER

    def get_moving_average_async(self, avg):
        self.spin_average.setValue(avg)
        
    def get_configuration_async(self, conf):
        self.gain_combo.setCurrentIndex(conf.gain)
        self.rate_combo.setCurrentIndex(conf.rate)
        
    def is_led_on_async(self, value):
        if value:
            self.enable_led.setChecked(True)
        else:
            self.enable_led.setChecked(False)

    def button_zero_pressed(self):
        self.lc.calibrate(0)
        
    def button_calibrate_pressed(self):
        self.lc.calibrate(self.spin_calibrate.value())
    
    def enable_led_changed(self, state):
        if state == Qt.Checked:
            self.lc.led_on()
        else:
            self.lc.led_off()
    
    def new_config(self, value):
        rate = self.rate_combo.currentIndex()
        gain = self.gain_combo.currentIndex()
        self.lc.set_configuration(rate, gain)
    
    def spin_average_finished(self):
        self.lc.set_moving_average(self.spin_average.value())

    def get_current_value(self):
        return self.current_value

    def cb_weight(self, weight):
        self.current_value = weight
        self.weight_label.setText(weight)
