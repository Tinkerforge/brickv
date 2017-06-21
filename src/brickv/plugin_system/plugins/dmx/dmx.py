# -*- coding: utf-8 -*-
"""
DMX Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

dmx.py: DMX Plugin Implementation

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

from PyQt4.QtGui import QSpinBox, QSlider, QWidget, QImage, QPainter, QPen, QAction
from PyQt4.QtCore import pyqtSignal, Qt, QPoint, QSize

from brickv.bindings.bricklet_dmx import BrickletDMX
from brickv.plugin_system.plugins.dmx.ui_dmx import Ui_DMX
from brickv.async_call import async_call
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase

class DMXOverview(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)

        self.parent = parent
        self.width = 512
        self.height = 32
        self.pen_width = 1
        self.image = QImage(QSize(self.width, self.height), QImage.Format_RGB32)

        self.setMaximumSize(self.width, self.height)
        self.setMinimumSize(self.width, self.height)

        self.last_point = QPoint()
        self.clear_image()
        
        self.white_pen = QPen(Qt.white, 1)
        self.black_pen = QPen(Qt.black, 1)
        
    def draw_frame(self, frame):
        painter = QPainter(self.image)
        for line, value in enumerate(frame):
            self.draw_line(line, value, painter)
        self.update()
        
    def draw_line(self, line, value, painter = None, update = False):
        if painter == None:
            painter = QPainter(self.image)
            
        painter.setPen(Qt.black)
        painter.drawLine(QPoint(line, 31-value//8), QPoint(line, 31))
        painter.setPen(Qt.white)
        painter.drawLine(QPoint(line, 0), QPoint(line, 31-value//8))
        
        if update:
            self.update()
        
    def fill_image(self, color):
        self.image.fill(color)
        self.update()

    def clear_image(self):
        self.image.fill(Qt.white)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            line = event.pos().x()
            self.parent.address_table.verticalScrollBar().setSliderPosition(line)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image)


class DMX(COMCUPluginBase, Ui_DMX):
    qtcb_frame_started = pyqtSignal()
    qtcb_frame = pyqtSignal(object, int)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletDMX, *args)

        self.setupUi(self)

        self.dmx = self.device
        
        self.wait_for_first_read = True
        
        self.dmx_overview = DMXOverview(self)
        self.layout_dmx_overview.insertWidget(1, self.dmx_overview)
        
        self.qtcb_frame_started.connect(self.cb_frame_started)
        self.qtcb_frame.connect(self.cb_frame)
        
        self.mode_combobox.currentIndexChanged.connect(self.mode_changed)
        self.frame_duration_spinbox.valueChanged.connect(self.frame_duration_changed)
        
        self.address_spinboxes = []
        self.address_slider = []
        
        for i in range(512):
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(255)
            
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(255)

            spinbox.valueChanged.connect(slider.setValue)
            slider.valueChanged.connect(spinbox.setValue)
            
            def get_frame_value_changed_func(i):
                return lambda x: self.frame_value_changed(i, x)
            slider.valueChanged.connect(get_frame_value_changed_func(i))
            
            self.address_table.setCellWidget(i, 0, spinbox)
            self.address_table.setCellWidget(i, 1, slider)
            
            self.address_spinboxes.append(spinbox)
            self.address_slider.append(slider)
            
            
        self.address_table.horizontalHeader().setStretchLastSection(True)
        self.address_table.show()
        
        self.current_frame = [0]*512

        self.com_led_off_action = QAction('Off', self)
        self.com_led_off_action.triggered.connect(lambda: self.dmx.set_communication_led_config(BrickletDMX.COMMUNICATION_LED_CONFIG_OFF))
        self.com_led_on_action = QAction('On', self)
        self.com_led_on_action.triggered.connect(lambda: self.dmx.set_communication_led_config(BrickletDMX.COMMUNICATION_LED_CONFIG_ON))
        self.com_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.com_led_show_heartbeat_action.triggered.connect(lambda: self.dmx.set_communication_led_config(BrickletDMX.COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT))
        self.com_led_show_communication_action = QAction('Show Com', self)
        self.com_led_show_communication_action.triggered.connect(lambda: self.dmx.set_communication_led_config(BrickletDMX.COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION))

        self.extra_configs += [(1, 'Com LED:', [self.com_led_off_action,
                                                self.com_led_on_action,
                                                self.com_led_show_heartbeat_action,
                                                self.com_led_show_communication_action])]

        self.error_led_off_action = QAction('Off', self)
        self.error_led_off_action.triggered.connect(lambda: self.dmx.set_error_led_config(BrickletDMX.ERROR_LED_CONFIG_OFF))
        self.error_led_on_action = QAction('On', self)
        self.error_led_on_action.triggered.connect(lambda: self.dmx.set_error_led_config(BrickletDMX.ERROR_LED_CONFIG_ON))
        self.error_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.error_led_show_heartbeat_action.triggered.connect(lambda: self.dmx.set_error_led_config(BrickletDMX.ERROR_LED_CONFIG_SHOW_HEARTBEAT))
        self.error_led_show_error_action = QAction('Show Error', self)
        self.error_led_show_error_action.triggered.connect(lambda: self.dmx.set_error_led_config(BrickletDMX.ERROR_LED_CONFIG_SHOW_ERROR))

        self.extra_configs += [(1, 'Error LED:', [self.error_led_off_action,
                                                  self.error_led_on_action,
                                                  self.error_led_show_heartbeat_action,
                                                  self.error_led_show_error_action])]
        
    def frame_value_changed(self, line, value):
        self.current_frame[line] = value
        self.dmx_overview.draw_line(line, value, None, True)
        
    def mode_changed(self, index, update=True):
        if index == 0:
            for spinbox in self.address_spinboxes:
                spinbox.setReadOnly(False)
            for slider in self.address_slider:
                slider.setEnabled(True)
                
            self.frame_duration_label.setVisible(True)
            self.frame_duration_unit.setVisible(True)
            self.frame_duration_spinbox.setVisible(True)
        else:
            for spinbox in self.address_spinboxes:
                spinbox.setReadOnly(True)
            for slider in self.address_slider:
                slider.setEnabled(False)
                
            self.frame_duration_label.setVisible(False)
            self.frame_duration_unit.setVisible(False)
            self.frame_duration_spinbox.setVisible(False)
            
        if update:
            self.dmx.set_dmx_mode(index)
        
    def frame_duration_changed(self, value):
        self.dmx.set_frame_duration(value)
        
    def handle_new_frame(self, frame):
        for i, value in enumerate(frame):
            self.address_spinboxes[i].setValue(value)
            self.frame_value_changed(i, value)
            
        self.wait_for_first_read = False
        
    def cb_get_frame_duration(self, frame_duration):
        self.frame_duration_spinbox.blockSignals(True)
        self.frame_duration_spinbox.setValue(frame_duration)
        self.frame_duration_spinbox.blockSignals(False)
    
    def cb_get_dmx_mode(self, mode):
        self.mode_combobox.blockSignals(True)
        self.mode_combobox.setCurrentIndex(mode)
        self.mode_changed(mode, False)
        self.mode_combobox.blockSignals(False)
        
        if mode == self.dmx.DMX_MODE_MASTER:
            async_call(self.dmx.read_frame, None, self.cb_read_frame, self.increase_error_count)
        
    def cb_read_frame(self, frame):
        self.handle_new_frame(frame.frame)

    def cb_frame_started(self):
        if not self.wait_for_first_read:
            async_call(self.dmx.write_frame, self.current_frame, None, self.increase_error_count)
        
    def cb_frame(self, frame, frame_number):
        if frame == None:
            return

        self.handle_new_frame(frame)

    def get_communication_led_config_async(self, config):
        if config == BrickletDMX.COMMUNICATION_LED_CONFIG_OFF:
            self.com_led_off_action.trigger()
        elif config == BrickletDMX.COMMUNICATION_LED_CONFIG_ON:
            self.com_led_on_action.trigger()
        elif config == BrickletDMX.COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT:
            self.com_led_show_heartbeat_action.trigger()
        elif config == BrickletDMX.COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION:
            self.com_led_show_communication_action.trigger()

    def get_error_led_config_async(self, config):
        if config == BrickletDMX.ERROR_LED_CONFIG_OFF:
            self.error_led_off_action.trigger()
        elif config == BrickletDMX.ERROR_LED_CONFIG_ON:
            self.error_led_on_action.trigger()
        elif config == BrickletDMX.ERROR_LED_CONFIG_SHOW_HEARTBEAT:
            self.error_led_show_heartbeat_action.trigger()
        elif config == BrickletDMX.ERROR_LED_CONFIG_SHOW_ERROR:
            self.error_led_show_error_action.trigger()

    def start(self):
        async_call(self.dmx.get_communication_led_config, None, self.get_communication_led_config_async, self.increase_error_count)
        async_call(self.dmx.get_error_led_config, None, self.get_error_led_config_async, self.increase_error_count)

        async_call(self.dmx.get_frame_duration, None, self.cb_get_frame_duration, self.increase_error_count)
        async_call(self.dmx.get_dmx_mode, None, self.cb_get_dmx_mode, self.increase_error_count)

        self.dmx.register_callback(self.dmx.CALLBACK_FRAME_STARTED, self.qtcb_frame_started.emit)
        self.dmx.register_callback(self.dmx.CALLBACK_FRAME, self.qtcb_frame.emit)
        
        self.dmx.set_frame_callback_config(True, False, True, False)

    def stop(self):
        self.dmx.register_callback(self.dmx.CALLBACK_FRAME, None)
        self.dmx.register_callback(self.dmx.CALLBACK_FRAME_STARTED, None)
        self.wait_for_first_read = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'dmx'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDMX.DEVICE_IDENTIFIER
