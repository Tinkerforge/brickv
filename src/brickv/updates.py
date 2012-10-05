# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

updates.py: GUI for showing available updates

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

from ui_updates import Ui_widget_updates
import time

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QApplication, QFrame, QMessageBox, QProgressDialog

import sys
import os
import urllib2
import re
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import fromstring as etreefromstring

FIRMWARE_URL = 'http://download.tinkerforge.com/firmwares/'

if sys.platform == 'linux2':
    BRICKV_URL = 'http://download.tinkerforge.com/tools/brickv/linux/'
elif sys.platform == 'darwin':
    BRICKV_URL = 'http://download.tinkerforge.com/tools/brickv/macos/'
elif sys.platform == 'win32':
    BRICKV_URL = 'http://download.tinkerforge.com/tools/brickv/windows/'

class UpdatesWindow(QFrame, Ui_widget_updates):
    def __init__(self, parent, config):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)

        self.parent = parent
        self.config = config
        self.button_refresh.pressed.connect(self.refresh)

        self.bricks = []
        self.bricklets = []

    def refresh(self):
        progress = self.create_progress_bar('Discovering')

        try:
            urllib2.urlopen(FIRMWARE_URL).read()
        except urllib2.URLError:
            progress.cancel()
            self.browser.setHtml('Could not connect to tinkerforge.com')
            return

        def get_body(url):
            response = urllib2.urlopen(url)
            data = response.read().replace('<hr>', '').replace('<br>', '')
            response.close()
            tree = etreefromstring(data)
            return tree.find('body')

        def get_firmware_versions(url, prefix):
            body = get_body(url)
            versions = []

            for a in body.getiterator('a'):
                url_part = a.text.replace('/', '')

                if url_part == '..':
                    continue

                m = re.match(prefix + '_firmware_(\d+)_(\d+)_(\d+)\.bin', url_part)

                if m is None:
                    continue

                versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))

                QApplication.processEvents()

            return sorted(versions)

        def get_tools_versions(url, tool):
            body = get_body(url)
            versions = []

            for a in body.getiterator('a'):
                url_part = a.text.replace('/', '')

                if url_part == '..':
                    continue

                if sys.platform == 'linux2':
                    m = re.match(tool + '-(\d+).(\d+).(\d+)_all\.deb', url_part)
                elif sys.platform == 'darwin':
                    m = re.match(tool + '_macos_(\d+)_(\d+)_(\d+)\.dmg', url_part)
                elif sys.platform == 'win32':
                    m = re.match(tool + '_windows_(\d+)_(\d+)_(\d+)\.exe', url_part)

                if m is None:
                    continue

                versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))

                QApplication.processEvents()

            return sorted(versions)

        progress.setLabelText('Checking for updates on tinkerforge.com')
        progress.setMaximum(1 + len(self.bricks) + len(self.bricklets))
        progress.setValue(0)
        progress.show()

        # Tools
        html = '<h3>Tools</h3>'

        tool_updates = []

        try:
            versions = get_tools_versions(BRICKV_URL, 'brickv')

            if len(versions) < 1:
                tool_updates.append('Could not discover latest Brick Viewer on tinkerforge.com')
            else:
                latest = '.'.join(map(str, versions[-1]))
                if self.config.BRICKV_VERSION != latest:
                    tool_updates.append('Brick Viewer, {0} is installed, {1} is latest'.format(self.config.BRICKV_VERSION, latest))
        except urllib2.URLError:
            tool_updates.append('Could not discover latest Brick Viewer on tinkerforge.com')

        progress.setValue(progress.value() + 1)

        if len(tool_updates) > 0:
            html += '<br/>'.join(tool_updates)
        else:
            html += 'All tools are up-to-date.'

        # Firmwares
        html += '<h3>Firmwares</h3>'

        firmware_updates = []

        for brick in self.bricks:
            url_part = ' '.join(brick[0].split(' ')[:-2]).lower()

            try:
                versions = get_firmware_versions(FIRMWARE_URL + 'bricks/' + url_part + '/', 'brick_' + url_part)

                if len(versions) < 1:
                    firmware_updates.append('Could not discover latest {0} Brick firmware on tinkerforge.com'.format(brick[0]))
                else:
                    flashed = '.'.join(brick[2])
                    latest = '.'.join(map(str, versions[-1]))
                    if flashed != latest:
                        firmware_updates.append('{0} [{1}], {2} is flashed, {3} is latest'.format(brick[0], brick[1], flashed, latest))
            except urllib2.URLError:
                firmware_updates.append('Could not discover latest {0} Brick firmware on tinkerforge.com'.format(brick[0]))

            progress.setValue(progress.value() + 1)

        if len(firmware_updates) > 0:
            html += '<br/>'.join(firmware_updates)
        elif len(self.bricks) > 0:
            html += 'All connected Bricks have up-to-date firmwares.'
        else:
            html += 'No Bricks connected.'

        # Plugins
        html += '<h3>Plugins</h3>'

        plugin_updates = []

        for bricklet in self.bricklets:
            url_part = ' '.join(bricklet[0].split(' ')[:-2]).lower().replace(' ', '_').replace('-', '')

            try:
                versions = get_firmware_versions(FIRMWARE_URL + 'bricklets/' + url_part + '/', 'bricklet_' + url_part)

                if len(versions) < 1:
                    plugin_updates.append('Could not discover latest {0} Bricklet plugin on tinkerforge.com'.format(bricklet[0]))
                else:
                    flashed = '.'.join(bricklet[2])
                    latest = '.'.join(map(str, versions[-1]))
                    if flashed != latest:
                        plugin_updates.append('{0} [{1}], {2} is flashed, {3} is latest'.format(bricklet[0], bricklet[1], flashed, latest))
            except urllib2.URLError:
                plugin_updates.append('Could not discover latest {0} Bricklet plugin on tinkerforge.com'.format(bricklet[0]))

            progress.setValue(progress.value() + 1)

        if len(plugin_updates) > 0:
            html += '<br/>'.join(plugin_updates)
        elif len(self.bricklets) > 0:
            html += 'All connected Bricklets have up-to-date plugins.'
        else:
            html += 'No Bricklets connected.'

        self.browser.setHtml(html)

        progress.cancel()

    def set_devices(self, devices):
        self.bricks = []
        self.bricklets = []

        for device in devices:
            if ' Brick ' in device[0]:
                self.bricks.append(device)
            else:
                self.bricklets.append(device)

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
