# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
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
from bindings.ip_connection import IPConnection, Error, base58encode, base58decode, BASE58, uid64_to_uid32
from plugin_system.plugins.imu.calibrate_import_export import parse_imu_calibration
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication, QColor, QFrame, QFileDialog, QMessageBox, QProgressDialog, QStandardItemModel, QStandardItem, QBrush
from samba import SAMBA, SAMBAException, get_serial_ports
from infos import get_version_string
import infos

import sys
import os
import urllib2
import re
import time
import struct
from xml.etree.ElementTree import fromstring as etreefromstring
from serial import SerialException

FIRMWARE_URL = 'http://download.tinkerforge.com/firmwares/'

check_for_brickv_update = True

if sys.platform.startswith('linux'):
    BRICKV_URL = 'http://download.tinkerforge.com/tools/brickv/linux/'
elif sys.platform == 'darwin':
    BRICKV_URL = 'http://download.tinkerforge.com/tools/brickv/macos/'
elif sys.platform == 'win32':
    BRICKV_URL = 'http://download.tinkerforge.com/tools/brickv/windows/'
elif sys.platform.startswith('freebsd'):
    check_for_brickv_update = False
    BRICKV_URL = 'http://freshports.org/devel/brickv/'
else:
    check_for_brickv_update = False
    BRICKV_URL = None

SELECT = 'Select...'
CUSTOM = 'Custom...'
FIRMWARE_URL = 'http://download.tinkerforge.com/firmwares/'
IMU_CALIBRATION_URL = 'http://download.tinkerforge.com/imu_calibration/'
NO_BRICK = 'No Brick found'
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

class ProgressWrapper:
    def __init__(self, progress):
        self.progress = progress
    
    def reset(self, title, length):
        self.progress.setLabelText(title)
        self.progress.setMaximum(length)
        self.progress.setValue(0)
        self.progress.show()
            
    def update(self, value):
        self.progress.setValue(value)
        QApplication.processEvents()
    
    def cancel(self):
        self.progress.cancel()
        
    def setMaximum(self, value):
        self.progress.setMaximum(value)
        
class FlashingWindow(QFrame, Ui_widget_flashing):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)
        
        self.firmware_infos = {}
        self.plugin_infos = {}
        self.brick_infos = []

        self.parent = parent
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.button_serial_port_refresh.pressed.connect(self.refresh_serial_ports)
        self.combo_firmware.currentIndexChanged.connect(self.firmware_changed)
        self.button_firmware_save.pressed.connect(self.firmware_save_pressed)
        self.button_firmware_browse.pressed.connect(self.firmware_browse_pressed)
        self.button_uid_load.pressed.connect(self.uid_load_pressed)
        self.button_uid_save.pressed.connect(self.uid_save_pressed)
        self.combo_brick.currentIndexChanged.connect(self.brick_changed)
        self.combo_port.currentIndexChanged.connect(self.port_changed)
        self.combo_plugin.currentIndexChanged.connect(self.plugin_changed)
        self.button_plugin_save.pressed.connect(self.plugin_save_pressed)
        self.button_plugin_browse.pressed.connect(self.plugin_browse_pressed)
        
        self.update_tool_label.hide()
        self.no_connection_label.hide()

        self.refresh_serial_ports()

        self.combo_firmware.addItem(CUSTOM)
        self.firmware_changed(0)

        self.combo_plugin.addItem(CUSTOM)
        self.plugin_changed(0)

        self.brick_changed(0)
        
        self.update_tree_view_model_labels = ['Name', 'UID', 'Installed', 'Latest']
        self.update_tree_view_model = QStandardItemModel()
        self.update_tree_view.setModel(self.update_tree_view_model)
        self.update_tree_view.setSortingEnabled(True)
        self.update_tree_view.header().setSortIndicator(0, Qt.AscendingOrder)

        self.update_button_refresh.pressed.connect(self.refresh_updates_pressed)
        self.update_button_bricklets.pressed.connect(self.auto_update_bricklets_pressed)

        self.update_ui_state()

    def get_body(self, url):
        response = urllib2.urlopen(url)
        data = response.read().replace('<hr>', '').replace('<br>', '')
        response.close()
        tree = etreefromstring(data)
        return tree.find('body')

    def get_firmware_versions(self, url, prefix):
        body = self.get_body(url)
        versions = []

        for a in body.getiterator('a'):
            if 'href' not in a.attrib:
                continue

            url_part = a.attrib['href'].replace('/', '')

            if url_part == '..':
                continue

            m = re.match(prefix + '_firmware_(\d+)_(\d+)_(\d+)(?:_beta\d+)?\.bin', url_part)

            if m is None:
                continue

            versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))

            QApplication.processEvents()

        return sorted(versions)

    def refresh_firmware_info(self, url_part, update_combo_box=False):
        name = url_part

        if name in ['dc', 'imu']:
            name = name.upper()
        else:
            words = name.split('_')
            parts = []
            for word in words:
                parts.append(word[0].upper() + word[1:])
            name = ' '.join(parts)

        versions = self.get_firmware_versions(FIRMWARE_URL + 'bricks/' + url_part + '/', 'brick_' + url_part)

        if len(versions) < 1:
            return

        firmware_info = infos.FirmwareInfo()
        firmware_info.name = name
        firmware_info.url_part = url_part
        firmware_info.firmware_version_latest = versions[-1]

        self.firmware_infos[url_part] = firmware_info

        if update_combo_box:
            i = self.combo_firmware.findData(url_part)
            if i >= 0:
                name = '{0} ({1}.{2}.{3})'.format(firmware_info.name,
                                                  *firmware_info.firmware_version_latest)
                self.combo_firmware.setItemText(i, name)

    def refresh_plugin_info(self, url_part, update_combo_box=False):
        name = url_part

        if name in ['gps']:
            name = name.upper()
        elif name.startswith('lcd_'):
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
        name = name.replace('Voltage Current', 'Voltage/Current')

        versions = self.get_firmware_versions(FIRMWARE_URL + 'bricklets/' + url_part + '/', 'bricklet_' + url_part)

        if len(versions) < 1:
            return

        plugin_info = infos.PluginInfo()
        plugin_info.name = name
        plugin_info.url_part = url_part
        plugin_info.firmware_version_latest = versions[-1]

        self.plugin_infos[url_part] = plugin_info

        if update_combo_box:
            i = self.combo_plugin.findData(url_part)
            if i >= 0:
                name = '{0} ({1}.{2}.{3})'.format(plugin_info.name,
                                                  *plugin_info.firmware_version_latest)
                self.combo_plugin.setItemText(i, name)

    def refresh_firmware_and_plugin_infos(self):
        progress = self.create_progress_bar('Discovering')

        self.firmware_infos = {}
        self.plugin_infos = {}

        self.combo_firmware.clear()
        self.combo_plugin.clear()

        available = False

        try:
            urllib2.urlopen(FIRMWARE_URL).read()
            available = True
        except urllib2.URLError:
            self.combo_firmware.setDisabled(True)
            self.combo_plugin.setDisabled(True)
            self.popup_fail('Brick and Bricklet', 'Could not connect to tinkerforge.com.\nFirmwares and plugins can be flashed from local files only.')

        if available:
            # discover firmwares
            try:
                progress.setLabelText('Discovering firmwares on tinkerforge.com')
                progress.setMaximum(0)
                progress.setValue(0)
                progress.show()

                body = self.get_body(FIRMWARE_URL + 'bricks/')
                elements = list(body.getiterator('a'))

                progress.setMaximum(len(elements))

                for a in elements:
                    progress.setValue(progress.value() + 1)

                    if 'href' not in a.attrib:
                        continue

                    url_part = a.attrib['href'].replace('/', '')

                    if url_part == '..':
                        continue

                    self.refresh_firmware_info(url_part)

                    QApplication.processEvents()

                progress.setValue(len(elements))

                if len(self.firmware_infos) > 0:
                    self.combo_firmware.addItem(SELECT)
                    self.combo_firmware.insertSeparator(self.combo_firmware.count())

                for firmware_info in sorted(self.firmware_infos.values(), cmp=lambda x, y: cmp(x.name, y.name)):
                    name = '{0} ({1}.{2}.{3})'.format(firmware_info.name, *firmware_info.firmware_version_latest)
                    self.combo_firmware.addItem(name, firmware_info.url_part)

                if self.combo_firmware.count() > 0:
                    self.combo_firmware.insertSeparator(self.combo_firmware.count())
            except urllib2.URLError:
                progress.cancel()
                self.combo_firmware.setDisabled(True)
                self.popup_fail('Brick', 'Could not discover firmwares on tinkerforge.com.\nFirmwares can be flashed from local files.')

        self.combo_firmware.addItem(CUSTOM)
        self.firmware_changed(0)

        if available:
            # discover plugins
            try:
                progress.setLabelText('Discovering plugins on tinkerforge.com')
                progress.setMaximum(0)
                progress.setValue(0)
                progress.show()

                body = self.get_body(FIRMWARE_URL + 'bricklets/')
                elements = list(body.getiterator('a'))

                progress.setMaximum(len(elements))

                for a in elements:
                    progress.setValue(progress.value() + 1)

                    if 'href' not in a.attrib:
                        continue

                    url_part = a.attrib['href'].replace('/', '')

                    if url_part == '..':
                        continue

                    self.refresh_plugin_info(url_part)

                    QApplication.processEvents()

                progress.setValue(len(elements))

                if len(self.plugin_infos) > 0:
                    self.combo_plugin.addItem(SELECT)
                    self.combo_plugin.insertSeparator(self.combo_plugin.count())

                for plugin_info in sorted(self.plugin_infos.values(), cmp=lambda x, y: cmp(x.name, y.name)):
                    name = '{0} ({1}.{2}.{3})'.format(plugin_info.name, *plugin_info.firmware_version_latest)
                    self.combo_plugin.addItem(name, plugin_info.url_part)

                if self.combo_plugin.count() > 0:
                    self.combo_plugin.insertSeparator(self.combo_plugin.count())
            except urllib2.URLError:
                progress.cancel()
                self.combo_plugin.setDisabled(True)
                self.popup_fail('Bricklet', 'Could not discover plugins on tinkerforge.com.\nPlugins can be flashed from local files.')

        self.combo_plugin.addItem(CUSTOM)
        self.plugin_changed(0)

        progress.cancel()

        self.update_ui_state()

    def update_bricks(self):
        self.brick_infos = []
        self.combo_brick.clear()
        for info in infos.infos.values():
            if info.type == 'brick':
                self.brick_infos.append(info)
                self.combo_brick.addItem(info.get_combo_item())

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
                       'GPS Camera Detect' in port[1]:
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
        self.combo_serial_port.setEnabled(not is_no_bootloader)
        self.button_firmware_save.setEnabled(not is_firmware_select and not is_no_bootloader)
        self.edit_custom_firmware.setEnabled(is_firmware_custom)
        self.button_firmware_browse.setEnabled(is_firmware_custom)

        is_plugin_select = self.combo_plugin.currentText() == SELECT
        is_plugin_custom = self.combo_plugin.currentText() == CUSTOM
        is_no_brick = self.combo_brick.currentText() == NO_BRICK
        self.combo_brick.setEnabled(not is_no_brick)
        self.button_plugin_save.setEnabled(not is_plugin_select and not is_no_brick)
        self.edit_custom_plugin.setEnabled(is_plugin_custom)
        self.button_plugin_browse.setEnabled(is_plugin_custom)

        self.tab_widget.setTabEnabled(2, len(self.brick_infos) > 0)

    def firmware_changed(self, index):
        self.update_ui_state()

    def firmware_browse_pressed(self):
        last_dir = ''
        if len(self.edit_custom_firmware.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(unicode(self.edit_custom_firmware.text().toUtf8(), 'utf-8')))

        file_name = QFileDialog.getOpenFileName(self,
                                                'Open Firmware',
                                                last_dir,
                                                '*.bin')
        if len(file_name) > 0:
            self.edit_custom_firmware.setText(file_name)
            self.update_ui_state()

    def firmware_save_pressed(self):
        port = str(self.combo_serial_port.itemData(self.combo_serial_port.currentIndex()).toString())

        try:
            samba = SAMBA(port)
        except SAMBAException, e:
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not connect to Brick: {0}'.format(str(e)))
            return
        except SerialException, e:
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
            firmware_file_name = unicode(firmware_file_name.toUtf8(), 'utf-8').encode(sys.getfilesystemencoding())

            try:
                firmware = file(firmware_file_name, 'rb').read()
            except IOError:
                progress.cancel()
                self.popup_fail('Brick', 'Could not read firmware file')
                return
        else:
            url_part = str(self.combo_firmware.itemData(self.combo_firmware.currentIndex()).toString())
            name = self.firmware_infos[url_part].name
            version = self.firmware_infos[url_part].firmware_version_latest

            progress.reset('Downloading {0} Brick firmware {1}.{2}.{3}'.format(name, *version), 0)

            response = None

            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'bricks/{0}/brick_{0}_firmware_{1}_{2}_{3}.bin'.format(url_part, *version))
            except urllib2.URLError:
                pass

            beta = 5

            while response is None and beta > 0:
                try:
                    response = urllib2.urlopen(FIRMWARE_URL + 'bricks/{0}/brick_{0}_firmware_{2}_{3}_{4}_beta{1}.bin'.format(url_part, beta, *version))
                except urllib2.URLError:
                    beta -= 1

            if response is None:
                progress.cancel()
                self.popup_fail('Brick', 'Could not download {0} Brick firmware {1}.{2}.{3}'.format(name, *version))
                return

            try:
                length = int(response.headers['Content-Length'])
                progress.setMaximum(length)
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
            except SerialException, e:
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
                    response = urllib2.urlopen(IMU_CALIBRATION_URL + '{0}.txt'.format(imu_uid))
                    chunk = response.read(1024)

                    while len(chunk) > 0:
                        imu_calibration_text += chunk
                        chunk = response.read(1024)

                    response.close()
                except urllib2.HTTPError, e:
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
        try:
            samba.flash(firmware, imu_calibration, lock_imu_calibration_pages)
            progress.cancel()

            if current_text == CUSTOM:
                self.popup_ok('Brick', 'Successfully flashed firmware.\nSuccessfully restarted Brick!')
            elif imu_calibration is not None:
                self.popup_ok('Brick', 'Successfully flashed {0} Brick firmware {1}.{2}.{3}.\n'.format(name, *version) +
                                       'Successfully restored factory calibration.\n' +
                                       'Successfully restarted {0} Brick!'.format(name))
            else:
                self.popup_ok('Brick', 'Successfully flashed {0} Brick firmware {1}.{2}.{3}.\n'.format(name, *version) +
                                       'Successfully restarted {0} Brick!'.format(name))
        except SAMBAException, e:
            progress.cancel()
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not flash Brick: {0}'.format(str(e)))
            return
        except SerialException, e:
            progress.cancel()
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not flash Brick: {0}'.format(str(e)))
            return
        except:
            progress.cancel()
            self.refresh_serial_ports()
            self.popup_fail('Brick', 'Could not flash Brick')
            return

    def uid_save_pressed(self):
        device, port = self.current_device_and_port()
        uid = str(self.edit_uid.text())

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
            self.popup_ok('Bricklet', 'Successfully wrote UID')
        else:
            self.popup_fail('Bricklet', 'Could not write UID: Verification failed')

    def uid_load_pressed(self):
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

        for key in sorted(brick_info.bricklets.keys()):
            bricklet_info = brick_info.bricklets[key]

            if bricklet_info is None:
                self.combo_port.addItem(key.upper())
            else:
                name = '{0}: {1}'.format(key.upper(), bricklet_info.get_combo_item())
                self.combo_port.addItem(name, bricklet_info.url_part)

        self.update_ui_state()

    def port_changed(self, index):
        self.edit_uid.setText('')

        if index < 0:
            self.combo_plugin.setCurrentIndex(0)
            return

        url_part = str(self.combo_port.itemData(index).toString())

        if len(url_part) == 0:
            self.combo_plugin.setCurrentIndex(0)
            return

        i = self.combo_plugin.findData(url_part)

        if i < 0:
            self.combo_plugin.setCurrentIndex(0)
            return

        self.combo_plugin.setCurrentIndex(i)

        b = self.combo_brick.currentIndex()
        p = self.combo_port.currentIndex()

        if b < 0 or p < 0:
            return

        self.edit_uid.setText(self.brick_infos[b].bricklets[('a', 'b', 'c', 'd')[p]].uid)

    def plugin_changed(self, index):
        self.update_ui_state()
        
    def download_bricklet_firmware(self, progress, url_part, name, version, popup=False):
        progress.setLabelText('Downloading {0} Bricklet plugin {1}.{2}.{3}'.format(name, *version))
        progress.setMaximum(0)
        progress.show()

        response = None

        try:
            response = urllib2.urlopen(FIRMWARE_URL + 'bricklets/{0}/bricklet_{0}_firmware_{1}_{2}_{3}.bin'.format(url_part, *version))
        except urllib2.URLError:
            pass

        beta = 5

        while response is None and beta > 0:
            try:
                response = urllib2.urlopen(FIRMWARE_URL + 'bricklets/{0}/bricklet_{0}_firmware_{2}_{3}_{4}_beta{1}.bin'.format(url_part, beta, *version))
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
    
    def write_bricklet_firmware(self, plugin, device, port, name, progress, popup=True):
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
                plugin = map(ord, file(plugin_file_name, 'rb').read()) # Convert plugin to list of bytes
            except IOError:
                progress.cancel()
                self.popup_fail('Bricklet', 'Could not read plugin file')
                return
        else:
            url_part = str(self.combo_plugin.itemData(self.combo_plugin.currentIndex()).toString())
            name = self.plugin_infos[url_part].name
            version = self.plugin_infos[url_part].firmware_version_latest
            plugin = self.download_bricklet_firmware(progress, url_part, name, version)
            if not plugin:
                return

        # Flash plugin
        device, port = self.current_device_and_port()

        url_part = str(self.combo_plugin.itemData(self.combo_plugin.currentIndex()).toString())
        
        if current_text == CUSTOM:
            if not self.write_bricklet_firmware(plugin, device, port, plugin_file_name, progress):
                return
        else:
            if not self.write_bricklet_firmware(plugin, device, port, name, progress):
                return

        progress.cancel()

        if current_text == CUSTOM:
            self.popup_ok('Bricklet', 'Successfully flashed plugin')
        else:
            self.popup_ok('Bricklet', 'Successfully flashed {0} Bricklet plugin {1}.{2}.{3}'.format(name, *version))

    def current_device_and_port(self):
        port_names = ['a', 'b', 'c', 'd']

        return (self.current_device(),
                port_names[self.combo_port.currentIndex()])

    def current_device(self):
        try:
            return self.brick_infos[self.combo_brick.currentIndex()].plugin.device
        except:
            return None

    def plugin_browse_pressed(self):
        last_dir = ''
        if len(self.edit_custom_plugin.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(unicode(self.edit_custom_plugin.text().toUtf8(), 'utf-8')))

        file_name = QFileDialog.getOpenFileName(self,
                                                'Open Plugin',
                                                last_dir,
                                                '*.bin')
        if len(file_name) > 0:
            self.edit_custom_plugin.setText(file_name)

    # Updates tab
    def auto_update_bricklets_pressed(self):
        def brick_for_bricklet(bricklet):
            for device_info in infos.infos.values():
                if device_info.type == 'brick':
                    if bricklet.position in device_info.bricklets and \
                       device_info.bricklets[bricklet.position] == bricklet:
                        return device_info

        progress = self.create_progress_bar('Auto-Updating Bricklets')
        
        bricks_to_reset = set()
        
        for device_info in infos.infos.values():
            if device_info.type == 'bricklet':
                if device_info.protocol_version == 2 and device_info.firmware_version_installed < device_info.firmware_version_latest:
                    plugin = self.download_bricklet_firmware(progress, device_info.url_part, device_info.name, device_info.firmware_version_latest)
                    if plugin:
                        brick = brick_for_bricklet(device_info)
                        if self.write_bricklet_firmware(plugin, brick.plugin.device, device_info.position, device_info.name, progress):
                            bricks_to_reset.add(brick)
                        else:
                            progress.cancel()
                            self.refresh_updates_pressed()
                            return
                    else:
                        progress.cancel()
                        self.refresh_updates_pressed()
                        return
            elif device_info.type == 'brick':
                for port in device_info.bricklets:
                    if device_info.bricklets[port]:
                        if device_info.bricklets[port].protocol_version == 1 and device_info.bricklets[port].firmware_version_installed < device_info.bricklets[port].firmware_version_latest:
                            plugin = self.download_bricklet_firmware(progress, device_info.bricklets[port].url_part, device_info.bricklets[port].name, device_info.bricklets[port].firmware_version_latest)
                            if plugin:
                                brick = brick_for_bricklet(device_info.bricklets[port])
                                if self.write_bricklet_firmware(plugin, brick.plugin.device, port, device_info.bricklets[port].name, progress):
                                    bricks_to_reset.add(brick)
                                else:
                                    progress.cancel()
                                    self.refresh_updates_pressed()
                                    return
                            else:
                                progress.cancel()
                                self.refresh_updates_pressed()
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
            self.refresh_updates_pressed()

    def refresh_updates_pressed(self):
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
            'LCD 20x4 Bricklet': 'lcd_20x4',
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
            urllib2.urlopen(FIRMWARE_URL).read()
            self.no_connection_label.hide()
        except urllib2.URLError:
            progress.cancel()
            self.no_connection_label.show()
            return

        def get_tools_versions(url, tool):
            body = self.get_body(url)
            versions = []

            for a in body.getiterator('a'):
                if 'href' not in a.attrib:
                    continue

                url_part = a.attrib['href'].replace('/', '')

                if url_part == '..':
                    continue

                if sys.platform.startswith('linux'):
                    if tool == 'brickd':
                        m = re.match(tool + '-(\d+).(\d+).(\d+)(?:_beta\d+)?(?:_amd64|i386)\.deb', url_part)
                    else:
                        m = re.match(tool + '-(\d+).(\d+).(\d+)(?:_beta\d+)?_all\.deb', url_part)
                elif sys.platform == 'darwin':
                    m = re.match(tool + '_macos_(\d+)_(\d+)_(\d+)(?:_beta\d+)?\.dmg', url_part)
                elif sys.platform == 'win32':
                    m = re.match(tool + '_windows_(\d+)_(\d+)_(\d+)(?:_beta\d+)?\.exe', url_part)

                if m is None:
                    continue

                versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))

                QApplication.processEvents()

            return sorted(versions)
        
        def get_color_for_device(device):
            if device.firmware_version_installed >= device.firmware_version_latest:
                return None, False
            
            if device.firmware_version_installed[0] <= 1:
                return QBrush(Qt.red), True
            
            return QBrush(QColor(255, 160, 55)), True

        progress.setLabelText('Checking for updates on tinkerforge.com')
        progress.setMaximum(len(infos.infos))
        progress.setValue(0)
        progress.show()

        brickv_info = infos.infos[infos.UID_BRICKV]
        if check_for_brickv_update:
            try:
                versions = get_tools_versions(BRICKV_URL, 'brickv')
                if len(versions) > 0:
                    brickv_info.firmware_version_latest = versions[-1]
            except urllib2.URLError:
                pass
        progress.setValue(progress.value() + 1)

        for device_info in sorted(infos.infos.values(), cmp=lambda x, y: cmp(x.name, y.name)):
            if device_info.type == 'brick':
                try:
                    self.refresh_firmware_info(device_info.url_part, True)
                    device_info.firmware_version_latest = self.firmware_infos[device_info.url_part].firmware_version_latest
                except:
                    pass
                progress.setValue(progress.value() + 1)
            elif device_info.type == 'bricklet':
                try:
                    self.refresh_plugin_info(device_info.url_part, True)
                    device_info.firmware_version_latest = self.plugin_infos[device_info.url_part].firmware_version_latest
                except:
                    pass
                progress.setValue(progress.value() + 1)

        progress.cancel()

        self.update_tree_view_model.clear()
        self.update_tree_view_model.setHorizontalHeaderLabels(self.update_tree_view_model_labels)

        is_update = False
        protocol1_errors = set()
        items = []

        for device_uid, device_info in infos.infos.iteritems():
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
                parent[0].setData(device_uid, Qt.UserRole)
                items.append(parent)

                brick_got_removed = False
                for port in device_info.bricklets:
                    if not device_info.bricklets[port] or device_info.bricklets[port].protocol_version == 1:
                        try:
                            protv, fw, name = device_info.plugin.device.get_protocol1_bricklet_name(port)
                        except:
                            protocol1_errors.add(device_uid)
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
                                versions = self.get_firmware_versions(FIRMWARE_URL + 'bricklets/' + bricklet_info.url_part + '/', 'bricklet_' + bricklet_info.url_part)
                                if len(versions) > 0:
                                    bricklet_info.firmware_version_latest = versions[-1]
                            except urllib2.URLError:
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

            elif device_info.type == 'tool' and 'Brick Viewer' in device_info.name:
                parent = [QStandardItem(device_info.name), 
                          QStandardItem(''), 
                          QStandardItem(get_version_string(device_info.firmware_version_installed)), 
                          QStandardItem(get_version_string(device_info.firmware_version_latest))]

                color, update = get_color_for_device(device_info)
                if update:
                    self.update_tool_label.show()
                else:
                    self.update_tool_label.hide()
                    
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
        QTimer.singleShot(t, lambda: self.refresh_updates_pressed_second_step(is_update, items, protocol1_errors))

    def refresh_updates_pressed_second_step(self, is_update, items, protocol1_errors):
        protocol1_error_still_there = False

        # filter out false-positive protocol1 errors
        for device_uid in protocol1_errors:
            if device_uid in infos.infos:
                protocol1_error_still_there = True
                continue
            for i in range(len(items)):
                if str(items[i][0].data(Qt.UserRole).toString()) == device_uid:
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
