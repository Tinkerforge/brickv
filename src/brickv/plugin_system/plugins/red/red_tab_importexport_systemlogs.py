# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QPlainTextEdit, QTextOption, QFont, QFileDialog, QMessageBox
from brickv.plugin_system.plugins.red.ui_red_tab_importexport_systemlogs import Ui_REDTabImportExportSystemLogs
from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call
import posixpath

class SystemLog(object):
    def __init__(self, display_name):
        self.display_name = display_name
        self.file_name    = posixpath.join('/', 'var', 'log', display_name) # FIXME: need to handle rotated logs
        self.content      = ''
        self.edit         = QPlainTextEdit()

        self.edit.setUndoRedoEnabled(False)
        self.edit.setReadOnly(True)
        self.edit.setWordWrapMode(QTextOption.NoWrap)
        self.edit.setPlainText('Click "Refresh" to download {0}.'.format(display_name))

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit.appendHtml(u'<b>{0}</b>'.format(Qt.escape(message)))
        elif pre:
            self.edit.appendHtml(u'<pre>{0}</pre>'.format(message))
        else:
            self.edit.appendPlainText(message)

class REDTabImportExportSystemLogs(QWidget, Ui_REDTabImportExportSystemLogs):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabImportExport
        self.script_manager = None # Set from REDTabImportExport
        self.log_file       = None
        self.logs           = [
            SystemLog('brickd.log'),
            SystemLog('redapid.log'),
            SystemLog('dmesg'),
            SystemLog('syslog'),
            SystemLog('kern.log'),
            SystemLog('daemon.log'),
            SystemLog('Xorg.0.log')
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
        pass

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def refresh_log(self):
        if self.log_file != None:
            return

        log = self.logs[self.combo_log.currentIndex()]

        self.label_download.setVisible(True)
        self.progress_download.setRange(0, 0)
        self.progress_download.setVisible(True)
        self.button_cancel.setVisible(True)
        self.button_refresh.setEnabled(False)
        self.label_download.setText('Downloading ' + log.file_name)

        def done():
            self.label_download.setVisible(False)
            self.progress_download.setVisible(False)
            self.button_cancel.setVisible(False)
            self.button_refresh.setEnabled(True)

        def cb_open(dummy):
            def cb_read_status(bytes_read, max_length):
                self.progress_download.setValue(bytes_read)

            def cb_read(result):
                self.log_file.release()
                self.log_file = None

                done()

                if result.error != None:
                    if result.error.error_code != REDError.E_OPERATION_ABORTED:
                        log.log(u'Error: ' + Qt.escape(unicode(result.error)), bold=True)

                    return

                try:
                    content = result.data.decode('utf-8')
                except UnicodeDecodeError:
                    # FIXME: maybe add a encoding guesser here or try some common encodings if UTF-8 fails
                    log.log(u'Error: Log file is not UTF-8 encoded', bold=True)
                    return

                log.content = content

                log.edit.setPlainText('')

                font = QFont('monospace')
                font.setStyleHint(QFont.TypeWriter)

                log.edit.setFont(font)
                log.edit.setPlainText(content)

            self.progress_download.setRange(0, self.log_file.length)
            self.log_file.read_async(self.log_file.length, cb_read, cb_read_status)

        def cb_open_error():
            done()
            log.log(u'Error: Could not open log file', bold=True)

        self.log_file = REDFile(self.session)

        async_call(self.log_file.open,
                   (log.file_name, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open, cb_open_error)

    def save_log(self):
        log       = self.logs[self.combo_log.currentIndex()]
        content   = log.content
        file_name = QFileDialog.getSaveFileName(get_main_window(), 'Save System Log',
                                                posixpath.split(log.file_name)[1])

        if len(file_name) == 0:
            return

        try:
            f = open(file_name, 'wb')
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save System Log Error',
                                 u"Could not open {0} for writing:\n\n{1}".format(file_name, unicode(e)))
            return

        try:
            # FIXME: add progress dialog if content is bigger than some megabytes
            f.write(content)
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save System Log Error',
                                 u"Could not write to {0}:\n\n{1}".format(file_name, unicode(e)))

        f.close()

    def cancel_download(self):
        log_file = self.log_file

        if log_file != None:
            try:
                log_file.abort_async_read()
            except:
                pass
