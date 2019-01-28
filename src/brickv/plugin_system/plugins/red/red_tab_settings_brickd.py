# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_brickd.py: RED settings brickd tab implementation

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

from PyQt5.QtWidgets import QMessageBox, QWidget

from brickv.plugin_system.plugins.red.ui_red_tab_settings_brickd import Ui_REDTabSettingsBrickd
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

# Constants
BRICKD_CONF_PATH = '/etc/brickd.conf'
CBOX_BRICKD_LOG_LEVEL_ERROR = 0
CBOX_BRICKD_LOG_LEVEL_WARN = 1
CBOX_BRICKD_LOG_LEVEL_INFO = 2
CBOX_BRICKD_LOG_LEVEL_DEBUG = 3
CBOX_BRICKD_LED_TRIGGER_CPU = 0
CBOX_BRICKD_LED_TRIGGER_GPIO = 1
CBOX_BRICKD_LED_TRIGGER_HEARTBEAT = 2
CBOX_BRICKD_LED_TRIGGER_MMC = 3
CBOX_BRICKD_LED_TRIGGER_OFF = 4
CBOX_BRICKD_LED_TRIGGER_ON = 5

class REDTabSettingsBrickd(QWidget, Ui_REDTabSettingsBrickd):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.brickd_conf = {}

        self.cbox_brickd_ll.addItem('Error')
        self.cbox_brickd_ll.addItem('Warn')
        self.cbox_brickd_ll.addItem('Info')
        self.cbox_brickd_ll.addItem('Debug')
        self.cbox_brickd_rt.addItem('cpu')
        self.cbox_brickd_rt.addItem('gpio')
        self.cbox_brickd_rt.addItem('heartbeat')
        self.cbox_brickd_rt.addItem('mmc')
        self.cbox_brickd_rt.addItem('off')
        self.cbox_brickd_rt.addItem('on')
        self.cbox_brickd_gt.addItem('cpu')
        self.cbox_brickd_gt.addItem('gpio')
        self.cbox_brickd_gt.addItem('heartbeat')
        self.cbox_brickd_gt.addItem('mmc')
        self.cbox_brickd_gt.addItem('off')
        self.cbox_brickd_gt.addItem('on')

        # Signals/slots
        self.pbutton_brickd_save.clicked.connect(self.slot_brickd_save_clicked)
        self.pbutton_brickd_refresh.clicked.connect(self.slot_brickd_refresh_clicked)
        self.sbox_brickd_la_ip1.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip2.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip3.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip4.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_lp.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_lwsp.valueChanged.connect(self.brickd_settings_changed)
        self.ledit_brickd_secret.textEdited.connect(self.brickd_settings_changed)
        self.cbox_brickd_ll.currentIndexChanged.connect(self.brickd_settings_changed)
        self.cbox_brickd_rt.currentIndexChanged.connect(self.brickd_settings_changed)
        self.cbox_brickd_gt.currentIndexChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_spi_dly.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_rs485_dly.valueChanged.connect(self.brickd_settings_changed)

    def tab_on_focus(self):
        self.brickd_conf_rfile = REDFile(self.session)
        self.slot_brickd_refresh_clicked()

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def brickd_button_refresh_enabled(self, state):
        self.pbutton_brickd_refresh.setEnabled(state)

        if state:
            self.pbutton_brickd_refresh.setText('Refresh')
        else:
            self.pbutton_brickd_refresh.setText('Refreshing...')

    def brickd_button_save_enabled(self, state):
        self.pbutton_brickd_save.setEnabled(state)

    def update_brickd_widget_data(self):
        if self.brickd_conf == None:
            return

        # Fill keys with default values if not available
        if not 'listen.address' in self.brickd_conf:
            self.brickd_conf['listen.address'] = '0.0.0.0'
        if not 'listen.plain_port' in self.brickd_conf:
            self.brickd_conf['listen.plain_port'] = '4223'
        if not 'listen.websocket_port' in self.brickd_conf:
            self.brickd_conf['listen.websocket_port'] = '0'
        if not 'authentication.secret' in self.brickd_conf:
            self.brickd_conf['authentication.secret'] = ''
        if not 'log.level' in self.brickd_conf:
            self.brickd_conf['log.level'] = 'info'
        if not 'led_trigger.green' in self.brickd_conf:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        if not 'led_trigger.red' in self.brickd_conf:
            self.brickd_conf['led_trigger.red'] = 'off'
        if not 'poll_delay.spi' in self.brickd_conf:
            self.brickd_conf['poll_delay.spi'] = '50'
        if not 'poll_delay.rs485' in self.brickd_conf:
            self.brickd_conf['poll_delay.rs485'] = '4000'

        l_addr = self.brickd_conf['listen.address'].split('.')
        self.sbox_brickd_la_ip1.setValue(int(l_addr[0]))
        self.sbox_brickd_la_ip2.setValue(int(l_addr[1]))
        self.sbox_brickd_la_ip3.setValue(int(l_addr[2]))
        self.sbox_brickd_la_ip4.setValue(int(l_addr[3]))

        self.sbox_brickd_lp.setValue(int(self.brickd_conf['listen.plain_port']))
        self.sbox_brickd_lwsp.setValue(int(self.brickd_conf['listen.websocket_port']))
        self.ledit_brickd_secret.setText(self.brickd_conf['authentication.secret'])

        log_level = self.brickd_conf['log.level']
        if log_level == 'debug':
            self.cbox_brickd_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_DEBUG)
        elif log_level == 'info':
            self.cbox_brickd_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_INFO)
        elif log_level == 'warn':
            self.cbox_brickd_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_WARN)
        elif log_level == 'error':
            self.cbox_brickd_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_ERROR)

        trigger_green = self.brickd_conf['led_trigger.green']
        if trigger_green == 'cpu':
            self.cbox_brickd_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_CPU)
        elif trigger_green == 'gpio':
            self.cbox_brickd_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_GPIO)
        elif trigger_green == 'heartbeat':
            self.cbox_brickd_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_HEARTBEAT)
        elif trigger_green == 'mmc':
            self.cbox_brickd_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_MMC)
        elif trigger_green == 'off':
            self.cbox_brickd_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_OFF)
        elif trigger_green == 'on':
            self.cbox_brickd_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_ON)

        trigger_red = self.brickd_conf['led_trigger.red']
        if trigger_red == 'cpu':
            self.cbox_brickd_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_CPU)
        elif trigger_red == 'gpio':
            self.cbox_brickd_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_GPIO)
        elif trigger_red == 'heartbeat':
            self.cbox_brickd_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_HEARTBEAT)
        elif trigger_red == 'mmc':
            self.cbox_brickd_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_MMC)
        elif trigger_red == 'off':
            self.cbox_brickd_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_OFF)
        elif trigger_red == 'on':
            self.cbox_brickd_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_ON)

        self.sbox_brickd_spi_dly.setValue(int(self.brickd_conf['poll_delay.spi']))
        self.sbox_brickd_rs485_dly.setValue(int(self.brickd_conf['poll_delay.rs485']))

    # The slots
    def brickd_settings_changed(self, value):
        self.brickd_button_save_enabled(True)

    def slot_brickd_refresh_clicked(self):
        self.brickd_button_refresh_enabled(False)

        def cb_open(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result and result.data is not None:
                    self.brickd_conf = config_parser.parse(result.data.decode('utf-8'))
                    self.update_brickd_widget_data()
                else:
                    QMessageBox.critical(get_main_window(),
                                               'Settings | Brickd',
                                               'Error reading brickd config file.')

                self.brickd_button_refresh_enabled(True)
                self.brickd_button_save_enabled(False)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error():
            self.brickd_button_refresh_enabled(True)
            QMessageBox.critical(get_main_window(),
                                       'Settings | Brickd',
                                       'Error opening brickd config file.')

        async_call(self.brickd_conf_rfile.open,
                   (BRICKD_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open,
                   cb_open_error)

    def slot_brickd_save_clicked(self):
        adr = '.'.join((str(self.sbox_brickd_la_ip1.value()),
                        str(self.sbox_brickd_la_ip2.value()),
                        str(self.sbox_brickd_la_ip3.value()),
                        str(self.sbox_brickd_la_ip4.value())))
        self.brickd_conf['listen.address'] = adr
        self.brickd_conf['listen.plain_port'] = str(self.sbox_brickd_lp.value())
        self.brickd_conf['listen.websocket_port'] = str(self.sbox_brickd_lwsp.value())
        self.brickd_conf['authentication.secret'] = self.ledit_brickd_secret.text()

        index = self.cbox_brickd_ll.currentIndex()
        if index == CBOX_BRICKD_LOG_LEVEL_ERROR:
            self.brickd_conf['log.level'] = 'error'
        elif index == CBOX_BRICKD_LOG_LEVEL_WARN:
            self.brickd_conf['log.level'] = 'warn'
        elif index == CBOX_BRICKD_LOG_LEVEL_INFO:
            self.brickd_conf['log.level'] = 'info'
        elif index == CBOX_BRICKD_LOG_LEVEL_DEBUG:
            self.brickd_conf['log.level'] = 'debug'

        index = self.cbox_brickd_gt.currentIndex()
        if index == CBOX_BRICKD_LED_TRIGGER_CPU:
            self.brickd_conf['led_trigger.green'] = 'cpu'
        elif index == CBOX_BRICKD_LED_TRIGGER_GPIO:
            self.brickd_conf['led_trigger.green'] = 'gpio'
        elif index == CBOX_BRICKD_LED_TRIGGER_HEARTBEAT:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        elif index == CBOX_BRICKD_LED_TRIGGER_MMC:
            self.brickd_conf['led_trigger.green'] = 'mmc'
        elif index == CBOX_BRICKD_LED_TRIGGER_OFF:
            self.brickd_conf['led_trigger.green'] = 'off'
        elif index == CBOX_BRICKD_LED_TRIGGER_ON:
            self.brickd_conf['led_trigger.green'] = 'on'

        index = self.cbox_brickd_rt.currentIndex()
        if index == CBOX_BRICKD_LED_TRIGGER_CPU:
            self.brickd_conf['led_trigger.red'] = 'cpu'
        elif index == CBOX_BRICKD_LED_TRIGGER_GPIO:
            self.brickd_conf['led_trigger.red'] = 'gpio'
        elif index == CBOX_BRICKD_LED_TRIGGER_HEARTBEAT:
            self.brickd_conf['led_trigger.red'] = 'heartbeat'
        elif index == CBOX_BRICKD_LED_TRIGGER_MMC:
            self.brickd_conf['led_trigger.red'] = 'mmc'
        elif index == CBOX_BRICKD_LED_TRIGGER_OFF:
            self.brickd_conf['led_trigger.red'] = 'off'
        elif index == CBOX_BRICKD_LED_TRIGGER_ON:
            self.brickd_conf['led_trigger.red'] = 'on'

        self.brickd_conf['poll_delay.spi'] = str(self.sbox_brickd_spi_dly.value())
        self.brickd_conf['poll_delay.rs485'] = str(self.sbox_brickd_rs485_dly.value())

        config = config_parser.to_string(self.brickd_conf)

        def cb_open(config, red_file):
            def cb_write(red_file, result):
                red_file.release()
                get_main_window().setEnabled(True)

                if result is not None:
                    QMessageBox.critical(get_main_window(),
                                               'Settings | Brickd',
                                               'Error writing brickd config file.')
                    return

                QMessageBox.information(get_main_window(),
                                              'Settings | Brick Daemon',
                                              'Saved configuration successfully, will now restart Brick Daemon.')

                self.script_manager.execute_script('restart_brickd', None)

            red_file.write_async(config, lambda x: cb_write(red_file, x), None)

        def cb_open_error():
            get_main_window().setEnabled(True)
            QMessageBox.critical(get_main_window(),
                                       'Settings | Brickd',
                                       'Error opening brickd config file.')

        get_main_window().setEnabled(False)

        async_call(self.brickd_conf_rfile.open,
                   (BRICKD_CONF_PATH,
                   REDFile.FLAG_WRITE_ONLY |
                   REDFile.FLAG_CREATE |
                   REDFile.FLAG_NON_BLOCKING |
                   REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                   lambda x: cb_open(config, x),
                   cb_open_error)
