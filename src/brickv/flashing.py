# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

flashing.py: GUI for flashing features

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

from ui_flashing import Ui_widget_flashing
import time

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QFrame, QFileDialog, QMessageBox, QProgressDialog

import sys
import urllib2
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import fromstring as etreefromstring
from samba import SAMBA, SAMBAException, get_serial_ports
from serial import SerialException

SELECT = 'Select...'
CUSTOM = 'Custom...'
FIRMWARE_URL = 'http://download.tinkerforge.com/firmwares/'

class FlashingWindow(QFrame, Ui_widget_flashing):
    def __init__(self, app, devices, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)

        self.app = app
        self.ipcon = parent.ipcon
        self.button_serial_port_refresh.pressed.connect(self.serial_port_refresh)
        self.combo_firmware.currentIndexChanged.connect(self.firmware_changed)
        self.button_firmware_save.pressed.connect(self.firmware_save_pressed)
        self.button_firmware_browse.pressed.connect(self.firmware_browse_pressed)
        self.button_uid_load.pressed.connect(self.uid_load_pressed)
        self.button_uid_save.pressed.connect(self.uid_save_pressed)
        self.combo_plugin.currentIndexChanged.connect(self.plugin_changed)
        self.button_plugin_save.pressed.connect(self.plugin_save_pressed)
        self.button_plugin_browse.pressed.connect(self.plugin_browse_pressed)

        self.devices = []
        if len(devices) == 0:
            self.tab_widget.setTabEnabled(1, False)
        else:
            for device in devices:
                self.combo_brick.addItem(device[0])
                self.devices.append(device[1])

        progress = self.create_progress_bar('Discovering')

        # discover serial ports
        self.serial_port_refresh(progress)

        # discover firmwares
        try:
            progress.setLabelText('Discovering firmwares on tinkerforge.com')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            response = urllib2.urlopen(FIRMWARE_URL + 'bricks/')
            data = response.read().replace('<hr>', '').replace('<br>', '')
            tree = etreefromstring(data)
            body = tree.find('body')
            firmwares = []

            for a in body.getiterator('a'):
                url_part = a.text.replace('/', '')
                name = url_part
                if name == '..':
                    continue
                elif name in ['dc', 'imu']:
                    name = name.upper()
                else:
                    words = name.split('_')
                    parts = []
                    for word in words:
                        parts.append(word[0].upper() + word[1:])
                    name = ' '.join(parts)

                firmwares.append((name, url_part))

            if len(firmwares) > 0:
                self.combo_firmware.addItem(SELECT)
                self.combo_firmware.insertSeparator(self.combo_firmware.count())

            for firmware in firmwares:
                self.combo_firmware.addItem(*firmware)

            if self.combo_firmware.count() > 0:
                self.combo_firmware.insertSeparator(self.combo_firmware.count())
        except:
            self.combo_firmware.setDisabled(True)
            self.popup_fail('Brick', 'Could not discover firmwares on tinkerforge.com. Flashing firmwares from local files is still possible.')

        self.combo_firmware.addItem(CUSTOM)
        self.firmware_changed(0)

        # discover plugins
        try:
            progress.setLabelText('Discovering plugins on tinkerforge.com')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            response = urllib2.urlopen(FIRMWARE_URL + 'bricklets/')
            data = response.read().replace('<hr>', '').replace('<br>', '')
            tree = etreefromstring(data)
            body = tree.find('body')
            plugins = []

            for a in body.getiterator('a'):
                url_part = a.text.replace('/', '')
                name = url_part
                if name == '..':
                    continue

                if name.startswith('lcd_'):
                    name = name.replace('lcd_', 'LCD_')
                elif name.startswith('io'):
                    name = name.replace('io', 'IO-')
                elif name.endswith('_ir'):
                    name = name.replace('_ir', '_IR')

                words = name.split('_')
                parts = []
                for word in words:
                    parts.append(word[0].upper() + word[1:])
                name = ' '.join(parts)

                plugins.append((name, url_part))

            if len(plugins) > 0:
                self.combo_plugin.addItem(SELECT)
                self.combo_plugin.insertSeparator(self.combo_plugin.count())

            for plugin in plugins:
                self.combo_plugin.addItem(*plugin)

            if self.combo_plugin.count() > 0:
                self.combo_plugin.insertSeparator(self.combo_plugin.count())
        except:
            self.combo_plugin.setDisabled(True)
            self.popup_fail('Bricklet', 'Could not discover plugins on tinkerforge.com. Flashing plugins from local files is still possible.')

        self.combo_plugin.addItem(CUSTOM)
        self.plugin_changed(0)

        progress.cancel()

        self.update_ui_state()

    def create_progress_bar(self, title):
        progress = QProgressDialog(self)
        progress.setAutoClose(False)
        progress.setWindowTitle(title)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)
        return progress

    def popup_ok(self, title, message):
        QMessageBox.information(self, title, message, QMessageBox.Ok)

    def popup_fail(self, title, message):
        QMessageBox.critical(self, title, message, QMessageBox.Ok)

    def serial_port_refresh(self, progress=None):
        self.combo_serial_port.clear()

        if progress is None:
            progress = self.create_progress_bar('Discovering')

        try:
            progress.setLabelText('Discovering serial ports')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            ports = get_serial_ports()
        except:
            self.update_ui_state()
            self.popup_fail('Brick', 'Could not discover serial ports')
        else:
            for port in ports:
                if len(port[1]) > 0 and port[0] != port[1]:
                    self.combo_serial_port.addItem('{0} - {1}'.format(port[0], port[1]), port[0])
                else:
                    self.combo_serial_port.addItem(port[0], port[0])


            self.update_ui_state()

        progress.cancel()

    def update_ui_state(self):
        is_firmware_select = self.combo_firmware.currentText() == SELECT
        is_firmware_custom = self.combo_firmware.currentText() == CUSTOM
        self.combo_serial_port.setEnabled(self.combo_serial_port.count() > 0)
        self.button_firmware_save.setEnabled(not is_firmware_select and self.combo_serial_port.count() > 0)
        self.edit_custom_firmware.setEnabled(is_firmware_custom)
        self.button_firmware_browse.setEnabled(is_firmware_custom)

        is_plugin_select = self.combo_plugin.currentText() == SELECT
        is_plugin_custom = self.combo_plugin.currentText() == CUSTOM
        self.combo_brick.setEnabled(self.combo_brick.count() > 0)
        self.button_plugin_save.setEnabled(not is_plugin_select and self.combo_brick.count() > 0)
        self.edit_custom_plugin.setEnabled(is_plugin_custom)
        self.button_plugin_browse.setEnabled(is_plugin_custom)

    def firmware_changed(self, index):
        self.update_ui_state()

    def firmware_browse_pressed(self):
        file_name = QFileDialog.getOpenFileName(self,
                                                'Open Firmware',
                                                '',
                                                '*.bin')
        self.edit_custom_firmware.setText(file_name)
        self.update_ui_state()

    def firmware_save_pressed(self):
        port = str(self.combo_serial_port.itemData(self.combo_serial_port.currentIndex()).toString())
        try:
            samba = SAMBA(port, self.app)
        except SAMBAException, e:
            self.serial_port_refresh()
            self.popup_fail('Brick', 'Could not connect to Brick: {0}'.format(str(e)))
            return
        except:
            self.serial_port_refresh()
            self.popup_fail('Brick', 'Could not connect to Brick')
            return

        progress = self.create_progress_bar('Flashing')

        current_text = self.combo_firmware.currentText()

        # Get firmware
        if current_text == SELECT:
            return
        elif current_text == CUSTOM:
            firmware_file_name = self.edit_custom_firmware.text()
            firmware_file_name = unicode(firmware_file_name.toUtf8(), 'utf-8').encode(sys.getfilesystemencoding())

            try:
                firmware = file(firmware_file_name, 'rb').read()
            except IOError:
                progress.cancel()
                self.popup_fail('Brick', 'Could not read firmware file')
                return
        else:
            url_part = self.combo_firmware.itemData(self.combo_firmware.currentIndex()).toString()

            progress.setLabelText('Downloading latest {0} Brick firmware'.format(current_text))
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'bricks/{0}/brick_{0}_firmware_latest.bin'.format(url_part))
                length = int(response.headers['Content-Length'])
                progress.setMaximum(length)
                progress.setValue(0)
                self.app.processEvents()
                firmware = ''
                chunk = response.read(1024)

                while len(chunk) > 0:
                    firmware += chunk
                    progress.setValue(len(firmware))
                    self.app.processEvents()
                    chunk = response.read(1024)
            except:
                progress.cancel()
                self.popup_fail('Brick', 'Could not download latest {0} Brick firmware'.format(current_text))
                return

        # Flash firmware
        try:
            samba.flash(firmware, progress)
            progress.cancel()
            if current_text == CUSTOM:
                self.popup_ok('Brick', 'Succesfully flashed firmware')
            else:
                self.popup_ok('Brick', 'Succesfully flashed latest {0} Brick firmware'.format(current_text))
        except SAMBAException, e:
            progress.cancel()
            self.serial_port_refresh()
            self.popup_fail('Brick', 'Could not flash Brick: {0}'.format(str(e)))
        except:
            progress.cancel()
            self.serial_port_refresh()
            self.popup_fail('Brick', 'Could not flash Brick')

    def uid_save_pressed(self):
        device, port = self.current_device_and_port()
        uid = str(self.edit_uid.text())
        try:
            self.ipcon.write_bricklet_uid(device, port, uid)
        except:
            self.popup_fail('Bricklet', 'Could not write UID')
            return

        try:
            uid_read = self.ipcon.read_bricklet_uid(device, port)
        except:
            self.popup_fail('Bricklet', 'Could not read written UID')
            return

        if uid == uid_read:
            self.popup_ok('Bricklet', 'Succesfully wrote UID')
        else:
            self.popup_fail('Bricklet', 'Could not write UID: Verification failed')

    def uid_load_pressed(self):
        device, port = self.current_device_and_port()
        try:
            uid = self.ipcon.read_bricklet_uid(device, port)
        except:
            self.edit_uid.setText('')
            self.popup_fail('Bricklet', 'Could not read UID')
            return

        self.edit_uid.setText(uid)

    def plugin_changed(self, index):
        self.update_ui_state()

    def plugin_save_pressed(self):
        progress = self.create_progress_bar('Flashing')
        current_text = self.combo_plugin.currentText()

        # Get plugin
        if current_text == SELECT:
            return
        elif current_text == CUSTOM:
            plugin_file_name = self.edit_custom_plugin.text()
            plugin_file_name = unicode(plugin_file_name.toUtf8(), 'utf-8').encode(sys.getfilesystemencoding())

            try:
                plugin = file(plugin_file_name, 'rb').read()
            except IOError:
                progress.cancel()
                self.popup_fail('Brick', 'Could not read plugin file')
                return
        else:
            url_part = self.combo_plugin.itemData(self.combo_plugin.currentIndex()).toString()

            progress.setLabelText('Downloading latest {0} Bricklet plugin'.format(current_text))
            progress.setMaximum(0)
            progress.show()

            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'bricklets/{0}/bricklet_{0}_firmware_latest.bin'.format(url_part))
                length = int(response.headers['Content-Length'])
                progress.setMaximum(length)
                progress.setValue(0)
                self.app.processEvents()
                plugin = ''
                chunk = response.read(1024)

                while len(chunk) > 0:
                    plugin += chunk
                    progress.setValue(len(plugin))
                    self.app.processEvents()
                    chunk = response.read(1024)
            except:
                progress.cancel()
                self.popup_fail('Bricklet', 'Could not download latest {0} Bricklet plugin'.format(current_text))
                return

        # Flash plugin
        device, port = self.current_device_and_port()

        try:
            # Write
            progress.setLabelText('Writing plugin')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()
            self.app.processEvents()

            self.ipcon.write_bricklet_plugin(device, port, plugin)
            time.sleep(1)

            # Verify
            progress.setLabelText('Verifing written plugin')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()
            self.app.processEvents()

            time.sleep(1)
            read_plugin = self.ipcon.read_bricklet_plugin(device,
                                                          port,
                                                          len(plugin))

            if plugin != read_plugin:
                raise Exception()

            progress.cancel()

            if current_text == CUSTOM:
                self.popup_ok('Bricklet', 'Succesfully flashed plugin')
            else:
                self.popup_ok('Bricklet', 'Succesfully flashed latest {0} Bricklet plugin'.format(current_text))
        except:
            progress.cancel()
            self.popup_fail('Bricklet', 'Could not flash Bricklet')

    def current_device_and_port(self):
        return (self.current_device(),
                str(self.combo_port.currentText()).lower())

    def current_device(self):
        return self.devices[self.combo_brick.currentIndex()]

    def plugin_browse_pressed(self):
        file_name = QFileDialog.getOpenFileName(self,
                                                'Open Plugin',
                                                '',
                                                '*.bin')
        self.edit_custom_plugin.setText(file_name)
