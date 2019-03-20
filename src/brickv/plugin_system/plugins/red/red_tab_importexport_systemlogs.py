# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015, 2017 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_importexport_systemlogs.py: RED import/export system logs tab implementation

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

import posixpath
import re
import os
import html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QMessageBox
from PyQt5.QtGui import QTextOption, QFont

from brickv.plugin_system.plugins.red.ui_red_tab_importexport_systemlogs import Ui_REDTabImportExportSystemLogs
from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call
from brickv.utils import get_main_window, get_home_path, get_save_file_name

class SystemLog:
    def __init__(self, display_name, source_name):
        self.display_name   = display_name
        self.source_name    = source_name # FIXME: need to handle rotated logs
        self.last_filename  = os.path.join(get_home_path(), display_name)
        self.content        = ''
        self.edit           = QPlainTextEdit()
        self.normal_font    = self.edit.font()
        self.monospace_font = QFont('monospace')

        self.edit.setUndoRedoEnabled(False)
        self.edit.setReadOnly(True)
        self.edit.setWordWrapMode(QTextOption.NoWrap)
        self.edit.setPlainText('Click "Refresh" to download {0}.'.format(display_name))

        self.monospace_font.setStyleHint(QFont.TypeWriter)

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit.appendHtml('<b>{0}</b>'.format(html.escape(message)))
        elif pre:
            self.edit.appendHtml('<pre>{0}</pre>'.format(message))
        else:
            self.edit.appendPlainText(message)

    def reset(self):
        self.content = None

        self.edit.setPlainText('')
        self.edit.setFont(self.normal_font)

    def set_content(self, content):
        self.content = content

        self.edit.setPlainText('')
        self.edit.setFont(self.monospace_font)
        self.edit.setPlainText(content)

class REDTabImportExportSystemLogs(QWidget, Ui_REDTabImportExportSystemLogs):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabImportExport
        self.script_manager = None # Set from REDTabImportExport
        self.image_version  = None # Set from REDTabImportExport
        self.log_file       = None
        self.image_version_lt_1_10 = True
        self.populated_custom_log_files = False
        self.logs           = [
            SystemLog('brickd.log', '/var/log/brickd.log'),
            SystemLog('redapid.log', '/var/log/redapid.log'),
            SystemLog('messages', '/var/log/messages'),
            SystemLog('syslog', '/var/log/syslog'),
            SystemLog('kern.log', '/var/log/kern.log'),
            SystemLog('daemon.log', '/var/log/daemon.log')
        ]

        while self.stacked_container.count() > 0:
            self.stacked_container.removeWidget(self.stacked_container.widget(0))

        for log in self.logs:
            self.combo_log.addItem(log.display_name)
            self.stacked_container.addWidget(log.edit)

        self.combo_log.currentIndexChanged.connect(self.stacked_container.setCurrentIndex)
        self.button_cancel.clicked.connect(self.cancel_download)
        self.button_refresh.clicked.connect(self.refresh_log)
        self.button_save.clicked.connect(self.save_log)

        self.label_download.setVisible(False)
        self.progress_download.setVisible(False)
        self.button_cancel.setVisible(False)

        self.stacked_container.setCurrentIndex(self.combo_log.currentIndex())

    def tab_on_focus(self):
        if not self.image_version:
            self.image_version_lt_1_10 = True
        else:
            self.image_version_lt_1_10 = self.image_version.number < (1, 10)

        if not self.populated_custom_log_files:
            self.populated_custom_log_files = True

            if self.image_version_lt_1_10:
                self.logs.append(SystemLog('openhab.log', '/var/log/openhab/openhab.log'))
            else:
                self.logs.append(SystemLog('openhab.log', '/var/log/openhab2/openhab.log'))

            self.combo_log.addItem(self.logs[-1].display_name)
            self.stacked_container.addWidget(self.logs[-1].edit)

            if self.image_version_lt_1_10:
                self.logs.append(SystemLog('Xorg.0.log', '/var/log/Xorg.0.log'))

            else:
                self.logs.append(SystemLog('Xorg.0.log', '/home/tf/.local/share/xorg/Xorg.0.log'))

            self.combo_log.addItem(self.logs[-1].display_name)
            self.stacked_container.addWidget(self.logs[-1].edit)

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def refresh_log(self):
        if self.log_file != None:
            return

        log = self.logs[self.combo_log.currentIndex()]

        log.reset()

        self.label_download.setVisible(True)
        self.label_download.setText('Downloading ' + log.source_name)
        self.progress_download.setRange(0, 0)
        self.progress_download.setVisible(True)
        self.button_cancel.setVisible(True)
        self.button_refresh.setEnabled(False)

        def done():
            self.log_file.release()
            self.log_file = None

            self.label_download.setVisible(False)
            self.progress_download.setVisible(False)
            self.button_cancel.setVisible(False)
            self.button_refresh.setEnabled(True)

        def cb_open(dummy):
            def cb_read_status(bytes_read, max_length):
                self.progress_download.setValue(bytes_read)

            def cb_read(result):
                done()

                if result.error != None:
                    if result.error.error_code != REDError.E_OPERATION_ABORTED:
                        log.log('Error: ' + html.escape(str(result.error)), bold=True)

                    return

                try:
                    content = result.data.decode('utf-8')
                except UnicodeDecodeError:
                    # FIXME: maybe add a encoding guesser here or try some common encodings if UTF-8 fails
                    log.log('Error: Log file is not UTF-8 encoded', bold=True)
                    return

                if '\x00' in content:
                    content = re.sub(r'(\n?)\x00+(\n?)', '\n[REBOOT]\n', content)

                log.set_content(content)

            self.progress_download.setRange(0, self.log_file.length)
            self.log_file.read_async(self.log_file.length, cb_read, cb_read_status)

        def cb_open_error(error):
            log.log('Error: {0}'.format(error), bold=True)

            done()

        self.log_file = REDFile(self.session)

        async_call(self.log_file.open,
                   (log.source_name, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open, cb_open_error, pass_exception_to_error_callback=True)

    def save_log(self):
        log      = self.logs[self.combo_log.currentIndex()]
        content  = log.content
        filename = get_save_file_name(get_main_window(), 'Save System Log', log.last_filename)

        if len(filename) == 0:
            return

        log.last_filename = filename

        try:
            f = open(filename, 'w')
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save System Log Error',
                                 'Could not open {0} for writing:\n\n{1}'.format(filename, e))
            return

        try:
            # FIXME: add progress dialog if content is bigger than some megabytes
            f.write(content)
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save System Log Error',
                                 'Could not write to {0}:\n\n{1}'.format(filename, e))

        f.close()

    def cancel_download(self):
        log_file = self.log_file

        if log_file != None:
            try:
                log_file.abort_async_read()
            except:
                pass
