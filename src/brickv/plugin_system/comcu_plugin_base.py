# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>

comcu_plugin_base.py: COMCU plugin base implementation

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

from PyQt5.QtWidgets import QAction, QMessageBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call
from brickv.utils import get_main_window

class COMCUPluginBase(PluginBase):
    def __init__(self, device_class, ipcon, device_info, override_base_name=None):
        super().__init__(device_class, ipcon, device_info, override_base_name)

        self.actual_start_stop_state = 'stop'
        self.expected_start_stop_state = 'stop'
        self.has_comcu = True
        self.cbe_bootloader_mode = CallbackEmulator(self,
                                                    self.device.get_bootloader_mode,
                                                    None,
                                                    self.cb_bootloader_mode,
                                                    self.increase_error_count)

        self.status_led_off_action = QAction('Off', self)
        self.status_led_off_action.triggered.connect(lambda: self.device.set_status_led_config(device_class.STATUS_LED_CONFIG_OFF))
        self.status_led_on_action = QAction('On', self)
        self.status_led_on_action.triggered.connect(lambda: self.device.set_status_led_config(device_class.STATUS_LED_CONFIG_ON))
        self.status_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.status_led_show_heartbeat_action.triggered.connect(lambda: self.device.set_status_led_config(device_class.STATUS_LED_CONFIG_SHOW_HEARTBEAT))
        self.status_led_show_status_action = QAction('Show Status', self)
        self.status_led_show_status_action.triggered.connect(lambda: self.device.set_status_led_config(device_class.STATUS_LED_CONFIG_SHOW_STATUS))

        self.extra_configs = [(0, 'Status LED:', [self.status_led_off_action,
                                                  self.status_led_on_action,
                                                  self.status_led_show_heartbeat_action,
                                                  self.status_led_show_status_action])]

        self.reset_action = QAction('Reset', self)
        self.reset_action.triggered.connect(self.remove_and_reset)

        self.extra_actions = [(0, None, [self.reset_action])]

    def remove_and_reset(self):
        get_main_window().remove_device_tab(self.uid)

        async_call(self.device.reset, None, None, lambda: QMessageBox.critical(get_main_window(), 'Reset',
                                                                               'Could not trigger device reset via software. Please try hardware reset.',
                                                                               QMessageBox.Ok))

    # overrides PluginBase.get_configs
    def get_configs(self):
        return PluginBase.get_configs(self) + self.extra_configs

    # overrides PluginBase.get_actions
    def get_actions(self):
        return PluginBase.get_actions(self) + self.extra_actions

    def get_status_led_config_async(self, config):
        if config == self.device_class.STATUS_LED_CONFIG_OFF:
            self.status_led_off_action.trigger()
        elif config == self.device_class.STATUS_LED_CONFIG_ON:
            self.status_led_on_action.trigger()
        elif config == self.device_class.STATUS_LED_CONFIG_SHOW_HEARTBEAT:
            self.status_led_show_heartbeat_action.trigger()
        elif config == self.device_class.STATUS_LED_CONFIG_SHOW_STATUS:
            self.status_led_show_status_action.trigger()

    def cb_bootloader_mode(self, mode):
        if mode == self.device.BOOTLOADER_MODE_FIRMWARE:
            if self.actual_start_stop_state == 'stop' and self.expected_start_stop_state == 'start':
                async_call(self.device.get_status_led_config, None, self.get_status_led_config_async, self.increase_error_count)
                self.actual_start_stop_state = 'start'
                self.start()

            if not self.isVisible():
                self.widget_bootloader.hide()
                self.show()
        elif mode == self.device.BOOTLOADER_MODE_BOOTLOADER:
            if self.actual_start_stop_state == 'start':
                self.actual_start_stop_state = 'stop'
                self.stop()

            if self.isVisible():
                self.hide()
                self.widget_bootloader.show()

    def start_comcu(self):
        self.expected_start_stop_state = 'start'
        self.cbe_bootloader_mode.set_period(1000)

    def stop_comcu(self):
        self.expected_start_stop_state = 'stop'
        self.cbe_bootloader_mode.set_period(0)

        if self.actual_start_stop_state == 'start':
            self.actual_start_stop_state = 'stop'
            self.stop()

    def get_health_metric_names(self):
        return ['SPITFP ACK Checksum Errors', 'SPITFP Message Checksum Errors', 'SPITFP Frame Errors', 'SPITFP Overflow Errors']

    def get_health_metric_values(self):
        spitfp_error_count = self.device.get_spitfp_error_count()

        return {
            'SPITFP ACK Checksum Errors': spitfp_error_count.error_count_ack_checksum,
            'SPITFP Message Checksum Errors': spitfp_error_count.error_count_message_checksum,
            'SPITFP Frame Errors': spitfp_error_count.error_count_frame,
            'SPITFP Overflow Errors': spitfp_error_count.error_count_overflow
        }
