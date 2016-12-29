# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011-2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2012-2016 Matthias Bolte <matthias@tinkerforge.com>

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

from brickv.ui_flashing import Ui_Flashing
from brickv.bindings.brick_master import BrickMaster
from brickv.bindings.ip_connection import IPConnection, Error, base58encode, \
                                          base58decode, BASE58, uid64_to_uid32
from brickv.imu_calibration import parse_imu_calibration, IMU_CALIBRATION_URL
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication, QColor, QDialog, QMessageBox, \
                        QProgressDialog, QStandardItemModel, QStandardItem, QBrush
from brickv.samba import SAMBA, SAMBAException, SAMBARebootError, get_serial_ports
from brickv.infos import get_version_string
from brickv.utils import get_main_window, get_home_path, get_open_file_name, \
                         get_modeless_dialog_flags
from brickv.esp_flash import ESPFlash
from brickv import infos

from zipfile import ZipFile
try:
    from StringIO import StringIO as FileLike
except ImportError:
    from io import BytesIO as FileLike

import zipfile
import os
import urllib2
import time
import struct
import math
import traceback
from serial import SerialException

LATEST_VERSIONS_URL = 'http://download.tinkerforge.com/latest_versions.txt'
FIRMWARE_URL = 'http://download.tinkerforge.com/firmwares/'
SELECT = 'Select...'
CUSTOM = 'Custom...'
NO_BRICK = 'No Brick found'
NO_EXTENSION = 'No Extension found'
NO_BOOTLOADER = 'No Brick in Bootloader found'

def error_to_name(e):
    if e.value == Error.TIMEOUT:
        return 'Timeout'
    elif e.value == Error.NOT_CONNECTED:
        return 'No TCP/IP connection'
    elif e.value == Error.INVALID_PARAMETER:
        return 'Invalid parameter'
    elif e.value == Error.NOT_SUPPORTED:
        return 'Not supported'
    else:
        return e.message

class ProgressWrapper(object):
    def __init__(self, progress):
        self.progress = progress

    def reset(self, title, length):
        if title != None:
            self.progress.setLabelText(title)

        self.progress.setMaximum(length)
        self.progress.setValue(0)
        self.progress.show()
        QApplication.processEvents()

    def update(self, value=None):
        if value != None:
            self.progress.setValue(value)

        QApplication.processEvents()

    def cancel(self):
        self.progress.cancel()

class FlashingWindow(QDialog, Ui_Flashing):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.tool_infos = {}
        self.firmware_infos = {}
        self.plugin_infos = {}
        self.extension_firmware_infos = {}
        self.brick_infos = []
        self.extension_infos = []
        self.refresh_updates_pending = False

        self.parent = parent
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.button_serial_port_refresh.clicked.connect(self.refresh_serial_ports)
        self.combo_firmware.currentIndexChanged.connect(self.firmware_changed)
        self.button_firmware_save.clicked.connect(self.firmware_save_clicked)
        self.button_firmware_browse.clicked.connect(self.firmware_browse_clicked)
        self.button_uid_load.clicked.connect(self.uid_load_clicked)
        self.button_uid_save.clicked.connect(self.uid_save_clicked)
        self.combo_brick.currentIndexChanged.connect(self.brick_changed)
        self.combo_port.currentIndexChanged.connect(self.port_changed)
        self.combo_plugin.currentIndexChanged.connect(self.plugin_changed)
        self.button_plugin_save.clicked.connect(self.plugin_save_clicked)
        self.button_plugin_browse.clicked.connect(self.plugin_browse_clicked)
        self.combo_extension.currentIndexChanged.connect(self.extension_changed)
        self.combo_extension_firmware.currentIndexChanged.connect(self.extension_firmware_changed)
        self.button_extension_firmware_save.clicked.connect(self.extension_firmware_save_clicked)
        self.button_extension_firmware_browse.clicked.connect(self.extension_firmware_browse_clicked)

        infos.get_infos_changed_signal().connect(self.update_bricks)
        infos.get_infos_changed_signal().connect(self.update_extensions)

        self.label_update_tool.hide()
        self.label_no_update_connection.hide()
        self.label_no_firmware_connection.hide()
        self.label_no_plugin_connection.hide()
        self.label_no_extension_firmware_connection.hide()
        self.label_extension_firmware_usb_hint.hide()

        self.refresh_serial_ports()

        self.combo_firmware.addItem(CUSTOM)
        self.combo_firmware.setEnabled(False)
        self.firmware_changed(0)

        self.combo_plugin.addItem(CUSTOM)
        self.combo_plugin.setEnabled(False)
        self.plugin_changed(0)

        self.combo_extension_firmware.addItem(CUSTOM)
        self.combo_extension_firmware.setEnabled(False)
        self.extension_firmware_changed(0)

        self.brick_changed(0)
        self.extension_changed(0)

        self.update_tree_view_model_labels = ['Name', 'UID', 'Installed', 'Latest']
        self.update_tree_view_model = QStandardItemModel(self)
        self.update_tree_view.setModel(self.update_tree_view_model)
        self.update_tree_view.setSortingEnabled(True)
        self.update_tree_view.header().setSortIndicator(0, Qt.AscendingOrder)

        self.update_button_refresh.clicked.connect(self.refresh_updates_clicked)
        self.update_button_bricklets.clicked.connect(self.auto_update_bricklets_clicked)

        self.update_ui_state()
        self.update_bricks()
        self.update_extensions()

    def refresh_latest_version_info(self, progress):
        self.tool_infos = {}
        self.firmware_infos = {}
        self.plugin_infos = {}
        self.extension_firmware_infos = {}

        self.combo_firmware.clear()
        self.combo_plugin.clear()
        self.combo_extension_firmware.clear()
        self.combo_firmware.setEnabled(True)
        self.combo_plugin.setEnabled(True)
        self.combo_extension_firmware.setEnabled(True)

        progress.setLabelText('Discovering latest versions on tinkerforge.com')
        progress.setMaximum(0)
        progress.setValue(0)
        progress.show()

        okay = True

        try:
            response = urllib2.urlopen(LATEST_VERSIONS_URL, timeout=10)
            latest_versions_data = response.read()
            response.close()
        except urllib2.URLError:
            okay = False
            progress.cancel()
            self.combo_firmware.setEnabled(False)
            self.combo_plugin.setEnabled(False)
            self.combo_extension_firmware.setEnabled(False)
            self.popup_fail('Updates / Flashing', 'Latest version information on tinkerforge.com is not available (error code 1). Please report this to info@tinkerforge.com.\n\nFirmwares and plugins can be flashed from local files only.')

        if okay:
            def report_malformed(error_code):
                progress.cancel()
                self.combo_firmware.setEnabled(False)
                self.combo_plugin.setEnabled(False)
                self.combo_extension_firmware.setEnabled(False)
                self.popup_fail('Updates / Flashing', 'Latest version information on tinkerforge.com is malformed (error code {0}). Please report this to info@tinkerforge.com.\n\nFirmwares and plugins can be flashed from local files only.'.format(error_code))

            for line in latest_versions_data.split('\n'):
                line = line.strip()

                if len(line) < 1:
                    continue

                parts = line.split(':')

                if len(parts) != 3:
                    okay = False
                    report_malformed(2)
                    break

                latest_version_parts = parts[2].split('.')

                if len(latest_version_parts) != 3:
                    okay = False
                    report_malformed(3)
                    break

                try:
                    latest_version = int(latest_version_parts[0]), int(latest_version_parts[1]), int(latest_version_parts[2])
                except:
                    okay = False
                    report_malformed(4)
                    break

                if parts[0] == 'tools':
                    tool_info = infos.ToolInfo()
                    tool_info.firmware_version_latest = latest_version

                    self.tool_infos[parts[1]] = tool_info
                elif parts[0] == 'bricks':
                    self.refresh_firmware_info(parts[1], latest_version)
                elif parts[0] == 'bricklets':
                    self.refresh_plugin_info(parts[1], latest_version)
                elif parts[0] == 'extensions':
                    self.refresh_extension_firmware_info(parts[1], latest_version)

        if okay:
            # update combo_firmware
            if len(self.firmware_infos) > 0:
                self.combo_firmware.addItem(SELECT)
                self.combo_firmware.insertSeparator(self.combo_firmware.count())

            for firmware_info in sorted(self.firmware_infos.values(), key=lambda x: x.name):
                name = '{0} ({1}.{2}.{3})'.format(firmware_info.name, *firmware_info.firmware_version_latest)
                self.combo_firmware.addItem(name, firmware_info.url_part)

            if self.combo_firmware.count() > 0:
                self.combo_firmware.insertSeparator(self.combo_firmware.count())

            # update combo_plugin
            if len(self.plugin_infos) > 0:
                self.combo_plugin.addItem(SELECT)
                self.combo_plugin.insertSeparator(self.combo_plugin.count())

            for plugin_info in sorted(self.plugin_infos.values(), key=lambda x: x.name):
                name = '{0} ({1}.{2}.{3})'.format(plugin_info.name, *plugin_info.firmware_version_latest)
                self.combo_plugin.addItem(name, plugin_info.url_part)

            if self.combo_plugin.count() > 0:
                self.combo_plugin.insertSeparator(self.combo_plugin.count())

            # update combo_extension_firmware
            if len(self.extension_firmware_infos) > 0:
                self.combo_extension_firmware.addItem(SELECT)
                self.combo_extension_firmware.insertSeparator(self.combo_extension_firmware.count())

            for extension_firmware_info in sorted(self.extension_firmware_infos.values(), key=lambda x: x.name):
                name = '{0} ({1}.{2}.{3})'.format(extension_firmware_info.name, *extension_firmware_info.firmware_version_latest)
                self.combo_extension_firmware.addItem(name, extension_firmware_info.url_part)

            if self.combo_extension_firmware.count() > 0:
                self.combo_extension_firmware.insertSeparator(self.combo_extension_firmware.count())

        self.combo_firmware.addItem(CUSTOM)
        self.firmware_changed(0)

        self.combo_plugin.addItem(CUSTOM)
        self.plugin_changed(0)

        self.combo_extension_firmware.addItem(CUSTOM)
        self.extension_firmware_changed(0)

        self.update_ui_state()

    def refresh_firmware_info(self, url_part, latest_version):
        name = url_part

        if name.endswith('_v2'):
            name = name.replace('_v2', '_2.0')

        if name in ['dc', 'imu', 'imu_2.0']:
            name = name.upper()

        words = name.split('_')
        parts = []

        for word in words:
            parts.append(word[0].upper() + word[1:])

        name = ' '.join(parts)

        firmware_info = infos.FirmwareInfo()
        firmware_info.name = name
        firmware_info.url_part = url_part
        firmware_info.firmware_version_latest = latest_version

        self.firmware_infos[url_part] = firmware_info

    def refresh_plugin_info(self, url_part, latest_version):
        name = url_part

        if name.endswith('_v2'):
            name = name.replace('_v2', '_2.0')

        if name in ['gps', 'ptc', 'rs232', 'co2', 'can', 'rgb_led']:
            name = name.upper()
        elif name.startswith('lcd_'):
            name = name.replace('lcd_', 'LCD_')
            if url_part.startswith('lcd_20x4_'):
                name = name.replace('_v11', '_1.1').replace('_v12', '_1.2')
        elif name.startswith('io'):
            name = name.replace('io', 'IO-')
        elif name.endswith('_ir'):
            name = name.replace('_ir', '_IR')
        elif name.endswith('_us'):
            name = name.replace('_us', '_US')
        elif name.startswith('led_'):
            name = name.replace('led_', 'LED_')
        elif name.startswith('oled_'):
            name = name.replace('oled_', 'OLED_')
        elif name.startswith('uv_'):
            name = name.replace('uv_', 'UV_')
        elif name.startswith('rgb_led_'):
            name = name.replace('rgb_led_', 'RGB_LED_')

        words = name.split('_')
        parts = []

        for word in words:
            parts.append(word[0].upper() + word[1:])

        name = ' '.join(parts)
        name = name.replace('Voltage Current', 'Voltage/Current')
        name = name.replace('Nfc Rfid', 'NFC/RFID')
        name = name.replace('0 20ma', '0-20mA')
        name = name.replace('Real Time', 'Real-Time')

        plugin_info = infos.PluginInfo()
        plugin_info.name = name
        plugin_info.url_part = url_part
        plugin_info.firmware_version_latest = latest_version

        self.plugin_infos[url_part] = plugin_info

    def refresh_extension_firmware_info(self, url_part, latest_version):
        name = url_part

        if name.endswith('_v2'):
            name = name.replace('_v2', '_2.0')

        if name in ['wifi_2.0']:
            name = name.upper()

        words = name.split('_')
        parts = []

        for word in words:
            parts.append(word[0].upper() + word[1:])

        name = ' '.join(parts)

        extension_firmware_info = infos.ExtensionFirmwareInfo()
        extension_firmware_info.name = name
        extension_firmware_info.url_part = url_part
        extension_firmware_info.firmware_version_latest = latest_version

        self.extension_firmware_infos[url_part] = extension_firmware_info

    def update_bricks(self):
        self.brick_infos = []
        self.combo_brick.clear()
        items = {}

        for info in infos.get_brick_infos():
            items[info.get_combo_item()] = info

        for item in sorted(items.keys()):
            self.brick_infos.append(items[item])
            self.combo_brick.addItem(item)

        if self.combo_brick.count() == 0:
            self.combo_brick.addItem(NO_BRICK)

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

    def refresh_serial_ports(self):
        progress = self.create_progress_bar('Discovering')
        current_text = self.combo_serial_port.currentText()
        self.combo_serial_port.clear()

        try:
            progress.setLabelText('Discovering serial ports')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            ports = get_serial_ports()
        except:
            progress.cancel()
            self.combo_serial_port.addItem(NO_BOOTLOADER)
            self.update_ui_state()
            self.popup_fail('Brick', 'Could not discover serial ports')
        else:
            preferred_index = None

            for port in ports:
                if preferred_index is None:
                    if 'ttyACM' in port[0] or \
                       'ttyUSB' in port[0] or \
                       'usbmodemfd' in port[0] or \
                       'AT91 USB to Serial Converter' in port[1] or \
                       'GPS Camera Detect' in port[1] or \
                       'Bossa Program Port' in port[1]:
                        preferred_index = self.combo_serial_port.count()

                if len(port[1]) > 0 and port[0] != port[1]:
                    self.combo_serial_port.addItem(u'{0} - {1}'.format(port[0], port[1]), port[0])
                else:
                    self.combo_serial_port.addItem(port[0], port[0])

            if self.combo_serial_port.count() == 0:
                self.combo_serial_port.addItem(NO_BOOTLOADER)
            elif preferred_index is not None:
                self.combo_serial_port.setCurrentIndex(preferred_index)
            else:
                index = self.combo_serial_port.findText(current_text)
                if index >= 0:
                    self.combo_serial_port.setCurrentIndex(index)

            self.update_ui_state()

        progress.cancel()

    def update_ui_state(self):
        is_firmware_select = self.combo_firmware.currentText() == SELECT
        is_firmware_custom = self.combo_firmware.currentText() == CUSTOM
        is_no_bootloader = self.combo_serial_port.currentText() == NO_BOOTLOADER
        has_bricklet_ports = self.combo_port.count() > 0
        self.combo_serial_port.setEnabled(not is_no_bootloader)
        self.combo_port.setEnabled(has_bricklet_ports)
        self.combo_plugin.setEnabled(has_bricklet_ports and self.combo_plugin.count() > 1)
        self.button_firmware_save.setEnabled(not is_firmware_select and not is_no_bootloader)
        self.edit_custom_firmware.setEnabled(is_firmware_custom)
        self.button_firmware_browse.setEnabled(is_firmware_custom)
        self.edit_uid.setEnabled(has_bricklet_ports)
        self.button_uid_load.setEnabled(has_bricklet_ports)
        self.button_uid_save.setEnabled(has_bricklet_ports)

        has_comcu = self.current_bricklet_has_comcu()
        is_plugin_select = self.combo_plugin.currentText() == SELECT
        is_plugin_custom = self.combo_plugin.currentText() == CUSTOM
        is_no_brick = self.combo_brick.currentText() == NO_BRICK
        self.combo_brick.setEnabled(not is_no_brick)
        self.button_plugin_save.setEnabled(not is_plugin_select and not is_no_brick)
        self.edit_custom_plugin.setEnabled(is_plugin_custom)
        self.button_plugin_browse.setEnabled(is_plugin_custom)
        self.label_bricklet_uid.setVisible(not has_comcu)
        self.edit_uid.setVisible(not has_comcu)
        self.button_uid_load.setVisible(not has_comcu)
        self.button_uid_save.setVisible(not has_comcu)

        is_extension_firmware_select = self.combo_extension_firmware.currentText() == SELECT
        is_extension_firmware_custom = self.combo_extension_firmware.currentText() == CUSTOM
        is_no_extension = self.combo_extension.currentText() == NO_EXTENSION

        try:
            extension_connection_type = self.extension_infos[self.combo_extension.currentIndex()].master_info.connection_type
        except:
            extension_connection_type = None

        if extension_connection_type == None:
            is_extension_connection_type_usb = False
        else:
            is_extension_connection_type_usb = extension_connection_type == BrickMaster.CONNECTION_TYPE_USB

        self.combo_extension.setEnabled(not is_no_extension)
        self.button_extension_firmware_save.setEnabled(not is_extension_firmware_select and not is_no_extension and is_extension_connection_type_usb)
        self.edit_custom_extension_firmware.setEnabled(is_extension_firmware_custom)
        self.button_extension_firmware_browse.setEnabled(is_extension_firmware_custom)
        self.label_extension_firmware_usb_hint.setVisible(not is_extension_connection_type_usb)

        self.tab_widget.setTabEnabled(2, len(self.brick_infos) > 0)
        self.tab_widget.setTabEnabled(3, len(self.extension_infos) > 0)

    def firmware_changed(self, index):
        self.update_ui_state()

    def firmware_browse_clicked(self):
        if len(self.edit_custom_firmware.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.edit_custom_firmware.text()))
        else:
            last_dir = get_home_path()

        filename = get_open_file_name(get_main_window(), 'Open Firmware', last_dir, '*.bin')

        if len(filename) > 0:
            self.edit_custom_firmware.setText(filename)

    def firmware_save_clicked(self):
        port_name = self.combo_serial_port.itemData(self.combo_serial_port.currentIndex())

        try:
            samba = SAMBA(port_name)
        except SAMBAException as e:
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not connect to Brick: {0}'.format(str(e)))
            return
        except SerialException as e:
            self.refresh_serial_ports()
            self.popup_fail('Brick', str(e)[0].upper() + str(e)[1:])
            return
        except:
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not connect to Brick')
            return

        progress = ProgressWrapper(self.create_progress_bar('Flashing'))
        samba.progress = progress
        current_text = self.combo_firmware.currentText()

        # Get firmware
        name = None
        version = None

        if current_text == SELECT:
            return
        elif current_text == CUSTOM:
            firmware_file_name = self.edit_custom_firmware.text()

            try:
                with open(firmware_file_name, 'rb') as f:
                    firmware = f.read()
            except IOError:
                progress.cancel()
                self.popup_fail('Brick', 'Could not read firmware file')
                return
        else:
            url_part = self.combo_firmware.itemData(self.combo_firmware.currentIndex())
            name = self.firmware_infos[url_part].name
            version = self.firmware_infos[url_part].firmware_version_latest

            progress.reset('Downloading {0} Brick firmware {1}.{2}.{3}'.format(name, *version), 0)

            response = None

            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'bricks/{0}/brick_{0}_firmware_{1}_{2}_{3}.bin'.format(url_part, *version), timeout=10)
            except urllib2.URLError:
                pass

            beta = 5

            while response is None and beta > 0:
                try:
                    response = urllib2.urlopen(FIRMWARE_URL + 'bricks/{0}/brick_{0}_firmware_{2}_{3}_{4}_beta{1}.bin'.format(url_part, beta, *version), timeout=10)
                except urllib2.URLError:
                    beta -= 1

            if response is None:
                progress.cancel()
                self.popup_fail('Brick', 'Could not download {0} Brick firmware {1}.{2}.{3}'.format(name, *version))
                return

            try:
                length = int(response.headers['Content-Length'])
                progress.reset(None, length)
                progress.update(0)
                QApplication.processEvents()
                firmware = ''
                chunk = response.read(1024)

                while len(chunk) > 0:
                    firmware += chunk
                    progress.update(len(firmware))
                    chunk = response.read(1024)

                response.close()
            except urllib2.URLError:
                progress.cancel()
                self.popup_fail('Brick', 'Could not download {0} Brick firmware {1}.{2}.{3}'.format(name, *version))
                return

        # Get IMU UID
        imu_uid = None
        imu_calibration = None
        lock_imu_calibration_pages = False

        if name == 'IMU':
            # IMU 1.0.9 and earlier have a bug in their flash locking that makes
            # them unlook the wrong pages. Therefore, the calibration pages
            # must not be locked for this versions
            if version[1] > 0 or (version[1] == 0 and version[2] > 9):
                lock_imu_calibration_pages = True

            try:
                imu_uid = base58encode(uid64_to_uid32(samba.read_uid64()))
            except SerialException as e:
                progress.cancel()
                self.popup_fail('Brick', 'Could read UID of IMU Brick: {0}'.format(str(e)))
                return
            except:
                progress.cancel()
                self.popup_fail('Brick', 'Could read UID of IMU Brick')
                return

            result = QMessageBox.question(self, 'IMU Brick',
                                          'Restore factory calibration for IMU Brick [{0}] from tinkerforge.com?'.format(imu_uid),
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            # Download IMU calibration
            if result == QMessageBox.Yes:
                progress.reset('Downloading factory calibration for IMU Brick', 0)

                try:
                    imu_calibration_text = ''
                    response = urllib2.urlopen(IMU_CALIBRATION_URL + '{0}.txt'.format(imu_uid), timeout=10)
                    chunk = response.read(1024)

                    while len(chunk) > 0:
                        imu_calibration_text += chunk
                        chunk = response.read(1024)

                    response.close()
                except urllib2.HTTPError as e:
                    if e.code == 404:
                        imu_calibration_text = None
                        self.popup_ok('IMU Brick', 'No factory calibration for IMU Brick [{0}] available'.format(imu_uid))
                    else:
                        progress.cancel()
                        self.popup_fail('IMU Brick', 'Could not download factory calibration for IMU Brick [{0}]'.format(imu_uid))
                        return
                except urllib2.URLError:
                    progress.cancel()
                    self.popup_fail('IMU Brick', 'Could not download factory calibration for IMU Brick [{0}]'.format(imu_uid))
                    return

                if imu_calibration_text is not None:
                    if len(imu_calibration_text) == 0:
                        progress.cancel()
                        self.popup_fail('IMU Brick', 'Could not download factory calibration for IMU Brick [{0}]'.format(imu_uid))
                        return

                    try:
                        imu_calibration_matrix = parse_imu_calibration(imu_calibration_text)

                        # Ensure proper temperature relation
                        if imu_calibration_matrix[5][1][7] <= imu_calibration_matrix[5][1][3]:
                            imu_calibration_matrix[5][1][7] = imu_calibration_matrix[5][1][3] + 1

                        imu_calibration_array = imu_calibration_matrix[0][1][:6] + \
                                                imu_calibration_matrix[1][1][:3] + \
                                                imu_calibration_matrix[2][1][:6] + \
                                                imu_calibration_matrix[3][1][:3] + \
                                                imu_calibration_matrix[4][1][:6] + \
                                                imu_calibration_matrix[5][1][:8]

                        imu_calibration = struct.pack('<32h', *imu_calibration_array)
                    except:
                        progress.cancel()
                        self.popup_fail('IMU Brick', 'Could not parse factory calibration for IMU Brick [{0}]'.format(imu_uid))
                        return

        # Flash firmware
        def report_result(reboot_okay):
            if current_text == CUSTOM:
                if reboot_okay:
                    message = 'Successfully restarted Brick!'
                else:
                    message = 'Manual restart of Brick required!'
            else:
                if reboot_okay:
                    message = 'Successfully restarted {0} Brick!'.format(name)
                else:
                    message = 'Manual restart of {0} Brick required!'.format(name)

            if current_text == CUSTOM:
                self.popup_ok('Brick', 'Successfully flashed firmware.\n' + message)
            elif imu_calibration is not None:
                self.popup_ok('Brick', 'Successfully flashed {0} Brick firmware {1}.{2}.{3}.\n'.format(name, *version) +
                                       'Successfully restored factory calibration.\n' + message)
            else:
                self.popup_ok('Brick', 'Successfully flashed {0} Brick firmware {1}.{2}.{3}.\n'.format(name, *version) +
                                       message)

        try:
            samba.flash(firmware, imu_calibration, lock_imu_calibration_pages)
            # close serial device before showing dialog, otherwise exchanging
            # the brick while the dialog is open will force it to show up as ttyACM1
            samba = None
            progress.cancel()
            report_result(True)
        except SAMBARebootError as e:
            samba = None
            progress.cancel()
            self.refresh_serial_ports()
            report_result(False)
        except SAMBAException as e:
            samba = None
            progress.cancel()
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not flash Brick: {0}'.format(str(e)))
        except SerialException as e:
            samba = None
            progress.cancel()
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not flash Brick: {0}'.format(str(e)))
        except:
            samba = None
            progress.cancel()
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not flash Brick')

    def uid_save_clicked(self):
        device, port = self.current_device_and_port()
        uid = self.edit_uid.text()

        if len(uid) == 0:
            self.popup_fail('Bricklet', 'UID cannot be empty')
            return

        for c in uid:
            if c not in BASE58:
                self.popup_fail('Bricklet', "UID cannot contain '{0}'".format(c))
                return

        try:
            if base58decode(uid) > 0xFFFFFFFF:
                self.popup_fail('Bricklet', 'UID is too long')
                return
        except:
            self.popup_fail('Bricklet', 'UID is invalid')
            return

        try:
            self.parent.ipcon.write_bricklet_uid(device, port, uid)
        except Error as e:
            self.popup_fail('Bricklet', 'Could not write UID: ' + error_to_name(e))
            return

        try:
            uid_read = self.parent.ipcon.read_bricklet_uid(device, port)
        except Error as e:
            self.popup_fail('Bricklet', 'Could not read written UID: ' + error_to_name(e))
            return

        if uid == uid_read:
            self.popup_ok('Bricklet', 'Successfully wrote UID.\nNew UID will be used after reset of the connected Brick.')
        else:
            self.popup_fail('Bricklet', 'Could not write UID: Verification failed')

    def uid_load_clicked(self):
        device, port = self.current_device_and_port()
        try:
            uid = self.parent.ipcon.read_bricklet_uid(device, port)
        except Error as e:
            self.edit_uid.setText('')
            self.popup_fail('Bricklet', 'Could not read UID: ' + error_to_name(e))
            return

        self.edit_uid.setText(uid)

    def brick_changed(self, index):
        self.combo_port.clear()

        if index < 0 or len(self.brick_infos) == 0:
            self.combo_port.addItems(['A', 'B', 'C', 'D'])
            return

        brick_info = self.brick_infos[index]
        first_index = None

        for key in sorted(brick_info.bricklets.keys()):
            bricklet_info = brick_info.bricklets[key]

            if bricklet_info is None:
                self.combo_port.addItem(key.upper())
            else:
                if first_index == None:
                    first_index = self.combo_port.count()

                name = '{0}: {1}'.format(key.upper(), bricklet_info.get_combo_item())
                self.combo_port.addItem(name, bricklet_info.url_part)

        if first_index != None:
            self.combo_port.setCurrentIndex(first_index)

        self.update_ui_state()

    def port_changed(self, index):
        self.update_ui_state()
        self.edit_uid.setText('')

        if index < 0:
            self.combo_plugin.setCurrentIndex(0)
            return

        url_part = self.combo_port.itemData(index)

        if url_part == None or len(url_part) == 0:
            self.combo_plugin.setCurrentIndex(0)
            return

        i = self.combo_plugin.findData(url_part)

        if i < 0:
            self.combo_plugin.setCurrentIndex(0)
        else:
            self.combo_plugin.setCurrentIndex(i)

        b = self.combo_brick.currentIndex()
        p = self.combo_port.currentIndex()

        if b < 0 or p < 0:
            return

        self.edit_uid.setText(self.brick_infos[b].bricklets[('a', 'b', 'c', 'd')[p]].uid)

    def plugin_changed(self, index):
        self.update_ui_state()

    def download_bricklet_plugin(self, progress, url_part, name, version, popup=False):
        progress.setLabelText('Downloading {0} Bricklet plugin {1}.{2}.{3}'.format(name, *version))
        progress.setMaximum(0)
        progress.show()

        response = None

        try:
            response = urllib2.urlopen(FIRMWARE_URL + 'bricklets/{0}/bricklet_{0}_firmware_{1}_{2}_{3}.bin'.format(url_part, *version), timeout=10)
        except urllib2.URLError:
            pass

        beta = 5

        while response is None and beta > 0:
            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'bricklets/{0}/bricklet_{0}_firmware_{2}_{3}_{4}_beta{1}.bin'.format(url_part, beta, *version), timeout=10)
            except urllib2.URLError:
                beta -= 1

        if response is None:
            progress.cancel()
            if popup:
                self.popup_fail('Bricklet', 'Could not download {0} Bricklet plugin {1}.{2}.{3}'.format(name, *version))
            return None

        try:
            length = int(response.headers['Content-Length'])
            progress.setMaximum(length)
            progress.setValue(0)
            QApplication.processEvents()
            plugin = []
            chunk = response.read(256)

            while len(chunk) > 0:
                plugin += map(ord, chunk) # Convert plugin to list of bytes
                progress.setValue(len(plugin))
                chunk = response.read(256)

            response.close()
        except urllib2.URLError:
            progress.cancel()
            if popup:
                self.popup_fail('Bricklet', 'Could not download {0} Bricklet plugin {1}.{2}.{3}'.format(name, *version))
            return None

        return plugin

    def write_bricklet_plugin(self, plugin, device, port, name, progress, popup=True):
        if self.current_bricklet_has_comcu():
            return self.write_bricklet_plugin_comcu(plugin, device, port, name, progress, popup)
        else:
            return self.write_bricklet_plugin_standard(plugin, device, port, name, progress, popup)

    def write_bricklet_plugin_comcu(self, plugin, device, port, name, progress, popup=True):
        try:
            progress.setLabelText('Starting bootloader mode')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            # Convert plugin back from list of bytes to something we can put in ZipFile
            zip_file = str(bytearray(plugin))
            try:
                zf = ZipFile(FileLike(zip_file), 'r')
            except:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not open Bricklet plugin:\n\n' + traceback.format_exc())
                return False

            plugin_data = None
            for name in zf.namelist():
                if name.endswith('firmware.bin'):
                    plugin_data = zf.read(name)
                    break

            if plugin_data == None:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not find firmware in zbin')
                return False

            # Now convert plugin to list of bytes
            plugin = map(ord, plugin_data)
            regular_plugin_upto = -1
            for i in reversed(range(4, len(plugin)-12)):
                if plugin[i] == 0x12 and plugin[i-1] == 0x34 and plugin[i-2] == 0x56 and plugin[i-3] == 0x78:
                    regular_plugin_upto = i
                    break

            if regular_plugin_upto == -1:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not find magic number in firmware')

            device = self.current_bricklet_device()
            if device == None:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not find device object for flashing')
                return False

            device.set_bootloader_mode(device.BOOTLOADER_MODE_BOOTLOADER)
            counter = 0
            while True:
                try:
                    if device.get_bootloader_mode() == device.BOOTLOADER_MODE_BOOTLOADER:
                        break
                except:
                    pass

                if counter == 10:
                    progress.cancel()
                    if popup:
                        self.popup_fail('Bricklet', 'Device did not enter bootloader mode in 2.5s')
                    return False

                time.sleep(0.25)
                counter += 1

            num_packets = len(plugin)/64
            # If the magic number is in in the last page of the
            # flash, we write the whole thing
            if regular_plugin_upto >= (len(plugin) - 64*4):
                index_list = range(num_packets)
            else:
                # We write the 64 byte packets up to the end of the last page that has meaningful data
                packet_up_to = ((regular_plugin_upto // 256)+1)*4
                index_list = range(0, packet_up_to) + [num_packets-4, num_packets-3, num_packets-2, num_packets-1]

            progress.setLabelText('Writing plugin: ' + name)
            progress.setMaximum(len(index_list))
            progress.setValue(0)
            progress.show()
            for position in index_list:
                start = position*64
                end   = (position+1)*64
                device.set_write_firmware_pointer(start)
                device.write_firmware(plugin[start:end])
                progress.setValue(position)

            progress.setLabelText('Changing from bootloader mode to firmware mode')
            progress.setMaximum(0)
            progress.setValue(0)
            progress.show()

            device.set_bootloader_mode(device.BOOTLOADER_MODE_FIRMWARE)
            counter = 0
            while True:
                try:
                    if device.get_bootloader_mode() == device.BOOTLOADER_MODE_FIRMWARE:
                        break
                except:
                    pass

                if counter == 10:
                    progress.cancel()
                    if popup:
                        self.popup_fail('Bricklet', 'Device did not enter firmware mode in 2.5s')
                    return False

                time.sleep(0.25)
                counter += 1

            progress.cancel()
            return True
        except:
            if popup:
                self.popup_fail('Bricklet', 'Unexpected error:\n\n' + traceback.format_exc())
            progress.cancel()
            return False

    def write_bricklet_plugin_standard(self, plugin, device, port, name, progress, popup=True):
        # Write
        progress.setLabelText('Writing plugin: ' + name)
        progress.setMaximum(0)
        progress.setValue(0)
        progress.show()

        plugin_chunks = []
        offset = 0

        while offset < len(plugin):
            chunk = plugin[offset:offset + IPConnection.PLUGIN_CHUNK_SIZE]

            if len(chunk) < IPConnection.PLUGIN_CHUNK_SIZE:
                chunk += [0] * (IPConnection.PLUGIN_CHUNK_SIZE - len(chunk))

            plugin_chunks.append(chunk)
            offset += IPConnection.PLUGIN_CHUNK_SIZE

        progress.setMaximum(len(plugin_chunks))

        position = 0

        for chunk in plugin_chunks:
            try:
                self.parent.ipcon.write_bricklet_plugin(device, port, position, chunk)
            except Error as e:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not write Bricklet plugin: ' + error_to_name(e))
                return False

            position += 1
            progress.setValue(position)

            time.sleep(0.015)
            QApplication.processEvents()

        time.sleep(0.1)

        # Verify
        progress.setLabelText('Verifying written plugin: ' + name)
        progress.setMaximum(len(plugin_chunks))
        progress.setValue(0)
        progress.show()

        time.sleep(0.1)
        position = 0

        for chunk in plugin_chunks:
            try:
                read_chunk = list(self.parent.ipcon.read_bricklet_plugin(device, port, position))
            except Error as e:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not read Bricklet plugin back for verification: ' + error_to_name(e))
                return False

            if read_chunk != chunk:
                progress.cancel()
                if popup:
                    self.popup_fail('Bricklet', 'Could not flash Bricklet plugin: Verification error')
                return False

            position += 1
            progress.setValue(position)

            time.sleep(0.015)
            QApplication.processEvents()

        return True

    def plugin_save_clicked(self):
        progress = self.create_progress_bar('Flashing')
        current_text = self.combo_plugin.currentText()

        # Get plugin
        if current_text == SELECT:
            return
        elif current_text == CUSTOM:
            plugin_file_name = self.edit_custom_plugin.text()

            try:
                with open(plugin_file_name, 'rb') as f:
                    plugin = map(ord, f.read()) # Convert plugin to list of bytes
            except IOError:
                progress.cancel()
                self.popup_fail('Bricklet', 'Could not read plugin file')
                return
        else:
            url_part = self.combo_plugin.itemData(self.combo_plugin.currentIndex())
            name = self.plugin_infos[url_part].name
            version = self.plugin_infos[url_part].firmware_version_latest
            plugin = self.download_bricklet_plugin(progress, url_part, name, version)

            if not plugin:
                return

        # Flash plugin
        device, port = self.current_device_and_port()

        if current_text == CUSTOM:
            if not self.write_bricklet_plugin(plugin, device, port, os.path.split(plugin_file_name)[-1], progress):
                return
        else:
            if not self.write_bricklet_plugin(plugin, device, port, name, progress):
                return

        progress.cancel()

        if current_text == CUSTOM:
            self.popup_ok('Bricklet', 'Successfully flashed plugin.\nNew plugin will be used after reset of the connected Brick.')
        else:
            self.popup_ok('Bricklet', 'Successfully flashed {0} Bricklet plugin {1}.{2}.{3}.\nNew plugin will be used after reset of the connected Brick.'.format(name, *version))

    def current_device_and_port(self):
        port_names = ['a', 'b', 'c', 'd']

        return (self.current_device(),
                port_names[self.combo_port.currentIndex()])

    def current_device(self):
        try:
            return self.brick_infos[self.combo_brick.currentIndex()].plugin.device
        except:
            return None

    def current_bricklet_plugin(self):
        port_names = ['a', 'b', 'c', 'd']
        try:
            return self.brick_infos[self.combo_brick.currentIndex()].bricklets[port_names[self.combo_port.currentIndex()]].plugin
        except:
            return None

    def current_bricklet_device(self):
        try:
            return self.current_bricklet_plugin().device
        except:
            return None

    def current_bricklet_has_comcu(self):
        try:
            return self.current_bricklet_plugin().has_comcu
        except:
            return False

    def plugin_browse_clicked(self):
        file_ending = '*.bin'
        try:
            if self.current_bricklet_has_comcu():
                file_ending = '*.zbin'
        except:
            pass

        last_dir = get_home_path()

        if len(self.edit_custom_plugin.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.edit_custom_plugin.text()))

        filename = get_open_file_name(get_main_window(), 'Open Plugin', last_dir, file_ending)

        if len(filename) > 0:
            self.edit_custom_plugin.setText(filename)

    def auto_update_bricklets_clicked(self):
        def brick_for_bricklet(bricklet):
            for device_info in infos.get_brick_infos():
                if bricklet.position in device_info.bricklets and \
                   device_info.bricklets[bricklet.position] == bricklet:
                    return device_info

        progress = self.create_progress_bar('Auto-Updating Bricklets')

        bricks_to_reset = set()

        for device_info in infos.get_device_infos():
            if device_info.type == 'bricklet':
                if device_info.protocol_version == 2 and device_info.firmware_version_installed < device_info.firmware_version_latest:
                    plugin = self.download_bricklet_plugin(progress, device_info.url_part, device_info.name, device_info.firmware_version_latest)

                    if not plugin:
                        progress.cancel()
                        self.refresh_updates_clicked()
                        return

                    brick = brick_for_bricklet(device_info)
                    if self.write_bricklet_plugin(plugin, brick.plugin.device, device_info.position, device_info.name, progress):
                        bricks_to_reset.add(brick)
                    else:
                        progress.cancel()
                        self.refresh_updates_clicked()
                        return
            elif device_info.type == 'brick':
                for port in device_info.bricklets:
                    if not device_info.bricklets[port]:
                        continue

                    if device_info.bricklets[port].protocol_version == 1 and \
                       device_info.bricklets[port].firmware_version_installed < device_info.bricklets[port].firmware_version_latest:
                        plugin = self.download_bricklet_plugin(progress, device_info.bricklets[port].url_part,
                                                               device_info.bricklets[port].name,
                                                               device_info.bricklets[port].firmware_version_latest)

                        if not plugin:
                            progress.cancel()
                            self.refresh_updates_clicked()
                            return

                        brick = brick_for_bricklet(device_info.bricklets[port])
                        if self.write_bricklet_plugin(plugin, brick.plugin.device, port, device_info.bricklets[port].name, progress):
                            bricks_to_reset.add(brick)
                        else:
                            progress.cancel()
                            self.refresh_updates_clicked()
                            return

        for brick in bricks_to_reset:
            try:
                brick.plugin.device.reset()
            except:
                pass

        progress.setLabelText('Waiting for Bricks to reset')
        progress.setMaximum(400)
        progress.setValue(0)

        for i in range(400):
            time.sleep(0.03)
            progress.setValue(i)

        progress.cancel()

    def tab_changed(self, i):
        if i == 0 and self.refresh_updates_pending:
            self.refresh_updates_clicked()
        elif i == 2:
            self.brick_changed(self.combo_brick.currentIndex())
            self.port_changed(self.combo_port.currentIndex())
        elif i == 3:
            self.extension_changed(self.combo_extension.currentIndex())

    def refresh_updates_clicked(self):
        if self.tab_widget.currentIndex() != 0:
            self.refresh_updates_pending = True
            return

        self.update_button_refresh.setDisabled(True)

        self.refresh_updates_pending = False

        url_part_proto1_map = {
            # 'name': 'url_part'
            'Ambient Light Bricklet': 'ambient_light',
            'Analog In Bricklet': 'analog_in',
            'Analog Out Bricklet': 'analog_out',
            'Barometer Bricklet': 'barometer',
            'Current12 Bricklet': 'current12',
            'Current25 Bricklet': 'current25',
            'Distance IR Bricklet': 'distance_ir',
            'Dual Relay Bricklet': 'dual_relay',
            'GPS Bricklet': 'gps',
            'Humidity Bricklet': 'humidity',
            'Industrial Digital In 4 Bricklet': 'industrial_digital_in_4',
            'Industrial Digital Out 4 Bricklet': 'industrial_digital_out_4',
            'Industrial Quad Relay Bricklet': 'industrial_quad_relay',
            'IO-16 Bricklet': 'io16',
            'IO-4 Bricklet': 'io4',
            'Joystick Bricklet': 'joystick',
            'LCD 16x2 Bricklet': 'lcd_16x2',
            'LCD 20x4 Bricklet': 'lcd_20x4_v11',
            'Linear Poti Bricklet': 'linear_poti',
            'Piezo Buzzer Bricklet': 'piezo_buzzer',
            'Rotary Poti Bricklet': 'rotary_poti',
            'Temperature Bricklet': 'temperature',
            'Temperature-IR Bricklet': 'temperature_ir',
            'Voltage Bricklet': 'voltage',
            'Voltage/Current Bricklet': 'voltage_current',
        }

        progress = self.create_progress_bar('Discovering')

        try:
            urllib2.urlopen("http://tinkerforge.com", timeout=10).read()
            self.label_no_update_connection.hide()
            self.label_no_firmware_connection.hide()
            self.label_no_plugin_connection.hide()
        except urllib2.URLError:
            progress.cancel()
            self.label_no_update_connection.show()
            self.label_no_firmware_connection.show()
            self.label_no_plugin_connection.show()
            return

        self.refresh_latest_version_info(progress)

        def get_color_for_device(device):
            if device.firmware_version_installed >= device.firmware_version_latest:
                return None, False

            if device.firmware_version_installed[0] <= 1:
                return QBrush(Qt.red), True

            return QBrush(QColor(255, 160, 55)), True

        try:
            infos.get_info(infos.UID_BRICKV).firmware_version_latest = self.tool_infos['brickv'].firmware_version_latest
        except:
            infos.get_info(infos.UID_BRICKV).firmware_version_latest = (0, 0, 0)

        for device_info in infos.get_device_infos():
            if device_info.type == 'brick':
                try:
                    device_info.firmware_version_latest = self.firmware_infos[device_info.url_part].firmware_version_latest
                except:
                    device_info.firmware_version_latest = (0, 0, 0)
            elif device_info.type == 'bricklet':
                try:
                    device_info.firmware_version_latest = self.plugin_infos[device_info.url_part].firmware_version_latest
                except:
                    device_info.firmware_version_latest = (0, 0, 0)

        for extension_info in infos.get_extension_infos():
            if extension_info.type == 'extension':
                try:
                    extension_info.firmware_version_latest = self.extension_firmware_infos[extension_info.url_part].firmware_version_latest
                except:
                    extension_info.firmware_version_latest = (0, 0, 0)

        progress.cancel()

        self.update_tree_view_model.clear()
        self.update_tree_view_model.setHorizontalHeaderLabels(self.update_tree_view_model_labels)

        is_update = False
        protocol1_errors = set()
        items = []

        for device_info in infos.get_infos():
            if device_info.type == 'brick':
                parent = [QStandardItem(device_info.name),
                          QStandardItem(device_info.uid),
                          QStandardItem(get_version_string(device_info.firmware_version_installed)),
                          QStandardItem(get_version_string(device_info.firmware_version_latest))]

                color, update = get_color_for_device(device_info)
                if update:
                    is_update = True
                for item in parent:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setData(color, Qt.BackgroundRole)
                parent[0].setData(device_info.uid, Qt.UserRole)
                items.append(parent)

                for port in device_info.bricklets:
                    if not device_info.bricklets[port] or device_info.bricklets[port].protocol_version == 1:
                        try:
                            protv, fw, name = device_info.plugin.device.get_protocol1_bricklet_name(port)
                        except:
                            protocol1_errors.add(device_info.uid)
                            child = [QStandardItem(port.upper() + ': Protocol 1.0 Bricklet with Error'),
                                     QStandardItem(''),
                                     QStandardItem(''),
                                     QStandardItem('')]

                            for item in child:
                                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                                item.setData(QBrush(Qt.magenta), Qt.BackgroundRole)
                            parent[0].appendRow(child)
                            continue

                        if protv == 1:
                            # Hack for LCD 20x4 Bricklet (name is not set early enough in firmware)
                            if fw == (1, 1, 1) and name == '':
                                name = 'LCD 20x4 Bricklet'
                            bricklet_info = infos.BrickletInfo()
                            bricklet_info.protocol_version = 1
                            bricklet_info.name = name
                            bricklet_info.position = port
                            bricklet_info.firmware_version_installed = tuple(fw)

                            device_info.bricklets[port] = bricklet_info
                            for key in url_part_proto1_map:
                                if key in device_info.bricklets[port].name:
                                    bricklet_info.url_part = url_part_proto1_map[key]
                                    break

                            try:
                                bricklet_info.firmware_version_latest = self.plugin_infos[bricklet_info.url_part].firmware_version_latest
                            except KeyError:
                                pass

                    if device_info.bricklets[port]:
                        child = [QStandardItem(port.upper() + ': ' + device_info.bricklets[port].name),
                                 QStandardItem(device_info.bricklets[port].uid),
                                 QStandardItem(get_version_string(device_info.bricklets[port].firmware_version_installed)),
                                 QStandardItem(get_version_string(device_info.bricklets[port].firmware_version_latest))]

                        color, update = get_color_for_device(device_info.bricklets[port])
                        if update:
                            is_update = True
                        for item in child:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            item.setData(color, Qt.BackgroundRole)
                        parent[0].appendRow(child)

                if device_info.can_have_extension:
                    for ext in device_info.extensions:
                        if device_info.extensions[ext]:
                            child = [QStandardItem(ext.capitalize() + ': ' + device_info.extensions[ext].name),
                                     QStandardItem(''),
                                     QStandardItem(get_version_string(device_info.extensions[ext].firmware_version_installed)),
                                     QStandardItem(get_version_string(device_info.extensions[ext].firmware_version_latest))]

                            color, update = get_color_for_device(device_info.extensions[ext])
                            if update:
                                is_update = True
                            for item in child:
                                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                                item.setData(color, Qt.BackgroundRole)
                            parent[0].appendRow(child)

            elif device_info.type == 'tool' and 'Brick Viewer' in device_info.name:
                parent = [QStandardItem(device_info.name),
                          QStandardItem(''),
                          QStandardItem(get_version_string(device_info.firmware_version_installed)),
                          QStandardItem(get_version_string(device_info.firmware_version_latest))]

                color, update = get_color_for_device(device_info)
                if update:
                    self.label_update_tool.show()
                else:
                    self.label_update_tool.hide()

                for item in parent:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setData(color, Qt.BackgroundRole)
                items.append(parent)

        t = 0
        if len(protocol1_errors) > 0:
            # if there were protocol1 errors give the enumerate callback a
            # chance to update the infos to have correct information to filter
            # out false-positive protocol1 errors that were detected due to
            # fast USB unplug
            t = 200

        QTimer.singleShot(t, lambda: self.refresh_updates_clicked_second_step(is_update, items, protocol1_errors))

    def refresh_updates_clicked_second_step(self, is_update, items, protocol1_errors):
        protocol1_error_still_there = False

        # filter out false-positive protocol1 errors
        for device_uid in protocol1_errors:
            if infos.get_info(device_uid) != None:
                protocol1_error_still_there = True
                continue

            for i in range(len(items)):
                if items[i][0].data(Qt.UserRole) == device_uid:
                    del items[i]
                    break

        for item in items:
            self.update_tree_view_model.appendRow(item)

        self.update_tree_view.expandAll()
        self.update_tree_view.setColumnWidth(0, 260)
        self.update_tree_view.setColumnWidth(1, 75)
        self.update_tree_view.setColumnWidth(2, 75)
        self.update_tree_view.setColumnWidth(3, 75)
        self.update_tree_view.setSortingEnabled(True)
        self.update_tree_view.header().setSortIndicator(0, Qt.AscendingOrder)

        if is_update:
            self.update_button_bricklets.setEnabled(True)
        else:
            self.update_button_bricklets.setEnabled(False)

        self.brick_changed(self.combo_brick.currentIndex())

        self.update_button_refresh.setDisabled(False)

        if protocol1_error_still_there:
            message = """
There was an error during the auto-detection of Bricklets with Protocol 1.0 plugins. Those cannot be updated automatically, but you can update them manually:

- Disconnect the affected Bricklets from their Brick and restart the Brick without the Bricklets.
- Ensure that the Brick shows up correctly.
- Connect the Bricklet to the Brick again, while the Brick is already running.
- Select the "Bricklet" tab and update the plugin manually.
"""
            QMessageBox.critical(self, "Bricklet with Error", message, QMessageBox.Ok)

    def extension_changed(self, index):
        if index < 0:
            self.combo_extension.setCurrentIndex(0)
            return

        url_part = self.combo_extension.itemData(index)

        if url_part == None or len(url_part) == 0:
            self.combo_extension_firmware.setCurrentIndex(0)
            return

        i = self.combo_extension_firmware.findData(url_part)

        if i < 0:
            self.combo_extension_firmware.setCurrentIndex(0)
        else:
            self.combo_extension_firmware.setCurrentIndex(i)

        self.update_ui_state()

    def extension_firmware_changed(self, index):
        self.update_ui_state()

    def download_extension_firmware(self, progress, url_part, name, version, popup=False):
        progress.reset('Downloading {0} Extension firmware {1}.{2}.{3}'.format(name, *version), 0)

        response = None

        try:
            response = urllib2.urlopen(FIRMWARE_URL + 'extensions/{0}/extension_{0}_firmware_{1}_{2}_{3}.zbin'.format(url_part, *version), timeout=10)
        except urllib2.URLError:
            pass

        beta = 5

        while response is None and beta > 0:
            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'extensions/{0}/extension{0}_firmware_{2}_{3}_{4}_beta{1}.zbin'.format(url_part, beta, *version), timeout=10)
            except urllib2.URLError:
                beta -= 1

        if response is None:
            progress.cancel()
            if popup:
                self.popup_fail('Extension', 'Could not download {0} Extension firmware {1}.{2}.{3}'.format(name, *version))
            return None

        try:
            length = int(response.headers['Content-Length'])
            progress.reset('Downloading {0} Extension firmware {1}.{2}.{3}'.format(name, *version), length)
            progress.update(0)
            firmware = b''
            chunk = response.read(256)

            while len(chunk) > 0:
                firmware += chunk
                progress.update(len(firmware))
                chunk = response.read(256)

            response.close()
        except urllib2.URLError:
            progress.cancel()
            if popup:
                self.popup_fail('Extension', 'Could not download {0} Extension firmware {1}.{2}.{3}'.format(name, *version))
            return None

        return firmware

    def extension_firmware_save_clicked(self):
        # FIXME: check Master.get_connection_type()

        current_text = self.combo_extension_firmware.currentText()
        progress = ProgressWrapper(self.create_progress_bar('Flashing'))

        if current_text == SELECT:
            return
        elif current_text == CUSTOM:
            firmware_file_name = self.edit_custom_extension_firmware.text()

            if not zipfile.is_zipfile(firmware_file_name):
                progress.cancel()
                self.popup_fail('Extension Firmware', 'Firmware file does not have correct format')
                return

            try:
                with open(firmware_file_name, 'rb') as f:
                    firmware = f.read()
            except IOError:
                progress.cancel()
                self.popup_fail('Extension Firmware', 'Could not read firmware file')
                return

            name = None
            version = None
        else:
            url_part = self.combo_extension_firmware.itemData(self.combo_extension_firmware.currentIndex())
            name = self.extension_firmware_infos[url_part].name
            version = self.extension_firmware_infos[url_part].firmware_version_latest
            firmware = self.download_extension_firmware(progress, url_part, name, version)

            if not firmware:
                return

        progress.reset('Connecting to bootloader', 0)
        progress.update(0)

        extension_info = self.extension_infos[self.combo_extension.currentIndex()]
        master = None

        # Find master from infos again, our info object may be outdated at this point
        for info in infos.get_brick_infos():
            if info.uid == extension_info.master_info.uid:
                master = info.plugin.device

        if master == None:
            progress.cancel()
            self.popup_fail('Extension Firmware', 'Error during Extension flashing: Could not find choosen Master Brick')
            return

        try:
            ESPFlash(master, progress).flash(firmware)
        except:
            progress.cancel()
            self.popup_fail('Extension Firmware', 'Error during Extension flashing: ' + traceback.format_exc())
            return

        progress.cancel()
        master.reset()

        if name != None and version != None:
            self.popup_ok('Extension Firmware', 'Successfully flashed {0} Extension firmware {1}.{2}.{3}.\nMaster Brick will now restart automatically.'.format(name, *version))
        else:
            self.popup_ok('Extension Firmware', 'Successfully flashed Extension firmware.\nMaster Brick will now restart automatically.')

    def extension_firmware_browse_clicked(self):
        if len(self.edit_custom_extension_firmware.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.edit_custom_extension_firmware.text()))
        else:
            last_dir = get_home_path()

        filename = get_open_file_name(get_main_window(), 'Open Extension Firmware', last_dir, '*.zbin')

        if len(filename) > 0:
            self.edit_custom_extension_firmware.setText(filename)

    def update_extensions(self):
        self.extension_infos = []
        self.combo_extension.clear()
        items = {}

        for info in infos.get_extension_infos():
            if info.extension_type == BrickMaster.EXTENSION_TYPE_WIFI2:
                items[info.get_combo_item()] = info

        for item in sorted(items.keys()):
            self.extension_infos.append(items[item])
            self.combo_extension.addItem(item, items[item].url_part)

        if self.combo_extension.count() == 0:
            self.combo_extension.addItem(NO_EXTENSION)

        self.update_ui_state()
