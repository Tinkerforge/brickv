# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

program_info_logs_view.py: Program Logs View Widget

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
import os
import html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtGui import QFont

from brickv.plugin_system.plugins.red.ui_program_info_logs_view import Ui_ProgramInfoLogsView
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import timestamp_to_date_at_time
from brickv.async_call import async_call
from brickv.utils import get_main_window, get_home_path, get_save_file_name

class ProgramInfoLogsView(QDialog, Ui_ProgramInfoLogsView):
    def __init__(self, parent, session, source_name):
        QDialog.__init__(self, parent)

        self.setupUi(self)
        self.setModal(True)

        self.source_name   = source_name
        self.last_filename = os.path.join(get_home_path(), posixpath.split(source_name)[1])
        self.log_file      = None
        self.content       = None

        source_name_parts = posixpath.split(source_name)[1].split('_')

        if source_name_parts[0] == 'continuous':
            date_time       = 'Continuous ({0})'.format(source_name_parts[1])
            self.continuous = True
        else:
            try:
                timestamp = int(source_name_parts[1].split('+')[0]) // 1000000
            except ValueError:
                timestamp = 0

            date_time       = '{0} ({1})'.format(timestamp_to_date_at_time(timestamp), source_name_parts[2])
            self.continuous = False

        self.rejected.connect(self.abort_download)
        self.progress_download.setRange(0, 0)
        self.label_date_time.setText(date_time)
        self.button_save.clicked.connect(self.save_content)
        self.button_close.clicked.connect(self.reject)

        self.button_save.setEnabled(False)

        def cb_open(dummy):
            def cb_read_status(bytes_read, max_length):
                self.progress_download.setValue(bytes_read)

            def cb_read(result):
                self.log_file.release()
                self.log_file = None

                self.label_download.setVisible(False)
                self.progress_download.setVisible(False)

                if result.error != None:
                    self.log('Error: ' + html.escape(str(result.error)), bold=True)
                    return

                try:
                    self.content = result.data.decode('utf-8')
                except UnicodeDecodeError:
                    # FIXME: maybe add a encoding guesser here or try some common encodings if UTF-8 fails
                    self.log('Error: Log file is not UTF-8 encoded', bold=True)
                    return

                self.button_save.setEnabled(True)

                if self.continuous:
                    content = self.content.lstrip()
                else:
                    content = self.content

                self.edit_content.setPlainText('')

                font = QFont('monospace')
                font.setStyleHint(QFont.TypeWriter)

                self.edit_content.setFont(font)
                self.edit_content.setPlainText(content)

            self.progress_download.setRange(0, self.log_file.length)
            self.log_file.read_async(self.log_file.length, cb_read, cb_read_status)

        def cb_open_error():
            self.label_download.setVisible(False)
            self.progress_download.setVisible(False)
            self.log('Error: Could not open log file', bold=True)

        self.log_file = REDFile(session)

        async_call(self.log_file.open,
                   (source_name, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open, cb_open_error)

    def save_content(self):
        filename = get_save_file_name(get_main_window(), 'Save Log', self.last_filename, '*.log')

        if len(filename) == 0:
            return

        self.last_filename = filename

        try:
            f = open(filename, 'w')
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save Log Error',
                                 'Could not open {0} for writing:\n\n{1}'.format(filename, e))
            return

        try:
            # FIXME: add progress dialog if content is bigger than some megabytes
            f.write(self.content)
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save Log Error',
                                 'Could not write to {0}:\n\n{1}'.format(filename, e))

        f.close()

    def abort_download(self):
        log_file = self.log_file

        if log_file != None:
            try:
                log_file.abort_async_read()
            except:
                pass

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit_content.appendHtml('<b>{0}</b>'.format(html.escape(message)))
        elif pre:
            self.edit_content.appendHtml('<pre>{0}</pre>'.format(message))
        else:
            self.edit_content.appendPlainText(message)
