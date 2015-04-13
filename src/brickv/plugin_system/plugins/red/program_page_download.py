# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_download.py: Program Wizard Download Page

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
from PyQt4.QtGui import QWizard, QTextCursor
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_download import Ui_ProgramPageDownload
from brickv.load_pixmap import load_pixmap
import os
import posixpath
import re
import sys
import errno

class ChunkedDownloader(ChunkedDownloaderBase):
    def __init__(self, page):
        ChunkedDownloaderBase.__init__(self, page.wizard().session)

        self.page = page

    def report_error(self, message, *args):
        self.page.download_error(u'...error: ' + message, *args)

    def set_progress_maximum(self, maximum):
        self.page.progress_file.setRange(0, maximum)

    def set_progress_value(self, value, message):
        self.page.progress_file.setValue(value)
        self.page.progress_file.setFormat(message)

    def done(self):
        self.page.chunked_downloader = None

        self.page.log('...done')
        self.page.download_next_file()


class ProgramPageDownload(ProgramPage, Ui_ProgramPageDownload):
    CONFLICT_RESOLUTION_REPLACE = 1
    CONFLICT_RESOLUTION_RENAME  = 2
    CONFLICT_RESOLUTION_SKIP    = 3

    def __init__(self, download_kind, download_directory, downloads, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.download_kind                   = download_kind # 'logs' or 'files'
        self.download_directory              = download_directory # absolute path on host in host format
        self.conflict_resolution_in_progress = False
        self.auto_conflict_resolution        = None
        self.download_successful             = False
        self.root_directory                  = None
        self.remaining_downloads             = downloads
        self.download                        = None
        self.created_directories             = set()
        self.target_path                     = None # abolsute path on host in host format
        self.chunked_downloader              = None
        self.replace_help_template           = self.label_replace_help.text()
        self.canceled                        = False

        self.setTitle(title_prefix + 'Download')

        self.progress_file.setVisible(False)

        self.check_rename_new_file.stateChanged.connect(self.update_ui_state)
        self.edit_new_name.textChanged.connect(self.check_new_name)
        self.button_reset_new_name.clicked.connect(self.reset_new_name)
        self.button_replace.clicked.connect(self.resolve_conflict_by_replace)
        self.button_rename.clicked.connect(self.resolve_conflict_by_rename)
        self.button_skip.clicked.connect(self.skip_conflict)
        self.button_start_download.clicked.connect(self.start_download)

        self.label_replace_icon.clear()
        self.label_replace_icon.setPixmap(load_pixmap('dialog-warning.png'))

        self.edit_new_name_checker = MandatoryLineEditChecker(self, self.label_new_name, self.edit_new_name)

        self.log(u'Going to download {0} to {1}'.format(self.download_kind, self.download_directory))
        self.edit_log.moveCursor(QTextCursor.StartOfLine)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Download {0} of the {{language}} program [{{name}}].'.format(self.download_kind))

        self.wizard().rejected.connect(self.cancel_download)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.download_successful and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        rename_new_file = self.check_rename_new_file.isChecked()

        self.line1.setVisible(self.conflict_resolution_in_progress)
        self.label_replace_icon.setVisible(self.conflict_resolution_in_progress)
        self.label_replace_help.setVisible(self.conflict_resolution_in_progress)
        self.label_existing_file.setVisible(self.conflict_resolution_in_progress)
        self.label_existing_stats.setVisible(self.conflict_resolution_in_progress)
        self.label_new_file.setVisible(self.conflict_resolution_in_progress)
        self.label_new_stats.setVisible(self.conflict_resolution_in_progress)
        self.check_rename_new_file.setVisible(self.conflict_resolution_in_progress)
        self.label_new_name.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.edit_new_name.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.button_reset_new_name.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.label_new_name_help_posix.setVisible(self.conflict_resolution_in_progress and rename_new_file and sys.platform != 'win32')
        self.label_new_name_help_windows.setVisible(self.conflict_resolution_in_progress and rename_new_file and sys.platform == 'win32')
        self.check_remember_decision.setVisible(self.conflict_resolution_in_progress)
        self.button_replace.setVisible(self.conflict_resolution_in_progress and not rename_new_file)
        self.button_rename.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.button_skip.setVisible(self.conflict_resolution_in_progress)
        self.line2.setVisible(self.conflict_resolution_in_progress)

    def cancel_download(self):
        self.canceled      = True
        chunked_downloader = self.chunked_downloader

        if chunked_downloader != None:
            chunked_downloader.canceled = True

    def check_new_name(self, name):
        target = os.path.split(self.download.target)[1]

        if len(name) == 0:
            self.edit_new_name.setStyleSheet('')
            self.button_rename.setEnabled(False)
        elif name == target or \
             (sys.platform != 'win32' and (name == '.' or name == '..' or '/' in name)) or \
             (sys.platform == 'win32' and re.search('[\\/:?*"<>|]', name) != None):
            self.edit_new_name.setStyleSheet('QLineEdit { color : red }')
            self.button_rename.setEnabled(False)
        else:
            self.edit_new_name.setStyleSheet('')
            self.button_rename.setEnabled(True)

    def reset_new_name(self):
        self.edit_new_name.setText(os.path.split(self.download.target)[1])

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit_log.appendHtml(u'<b>{0}</b>'.format(Qt.escape(message)))
        elif pre:
            self.edit_log.appendHtml(u'<pre>{0}</pre>'.format(message))
        else:
            self.edit_log.appendPlainText(message)

        self.edit_log.verticalScrollBar().setValue(self.edit_log.verticalScrollBar().maximum())

    def next_step(self, message, increase=1, log=True):
        self.progress_total.setValue(self.progress_total.value() + increase)
        self.label_current_step.setText(message)

        if log:
            self.log(message)

    def download_error(self, message, *args):
        string_args = []

        for arg in args:
            string_args.append(Qt.escape(unicode(arg)))

        if len(string_args) > 0:
            message = unicode(message).format(*tuple(string_args))

        self.log(message, bold=True)

    def get_total_step_count(self):
        count = 0

        count += 1 # download files
        count += len(self.remaining_downloads)
        count += 1 # download successful

        return count

    def start_download(self):
        self.button_start_download.setEnabled(False)
        self.wizard().setOption(QWizard.DisabledBackButtonOnLastPage, True)

        self.progress_total.setRange(0, self.get_total_step_count())

        # download files
        self.next_step(u'Downloading {0}...'.format(self.download_kind), log=False)

        self.root_directory = self.wizard().program.root_directory

        self.progress_file.setRange(0, len(self.remaining_downloads))

        self.download_next_file()

    def download_next_file(self):
        if self.canceled:
            return

        if len(self.remaining_downloads) == 0:
            self.download_files_done()
            return

        self.download            = self.remaining_downloads[0]
        self.remaining_downloads = self.remaining_downloads[1:]

        if self.download_kind == 'logs':
            source_path = posixpath.join(self.root_directory, 'log', self.download.source)
        else:
            source_path = posixpath.join(self.root_directory, 'bin', self.download.source)

        self.next_step(u'Downloading {0}...'.format(self.download.source))

        self.chunked_downloader = ChunkedDownloader(self)

        if not self.chunked_downloader.prepare(source_path):
            return

        self.target_path = os.path.join(self.download_directory, self.download.target)

        # create target directory, if necessary
        if len(os.path.split(self.download.target)[0]) > 0:
            target_directory = os.path.split(self.target_path)[0]

            if target_directory not in self.created_directories:
                try:
                    os.makedirs(target_directory, 0o755)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        self.download_error('...error: Could not create target directory {0}: {1}', target_directory, e)
                        return
                except Exception as e:
                    self.download_error('...error: Could not create target directory {0}: {1}', target_directory, e)
                    return

                self.created_directories.add(target_directory)

        self.continue_download_file()

    def continue_download_file(self, replace_existing=False):
        if os.path.exists(self.target_path):
            if replace_existing:
                try:
                    os.remove(self.target_path)
                except Exception as e:
                    self.download_error('...error: Could not replace target file {0}: {1}', self.target_path, e)
                    return
            else:
                self.start_conflict_resolution()
                return

        self.progress_file.setVisible(True)
        self.chunked_downloader.start(self.target_path)

    def start_conflict_resolution(self):
        self.log(u'...target file {0} already exists'.format(self.target_path))

        if self.auto_conflict_resolution == ProgramPageDownload.CONFLICT_RESOLUTION_REPLACE:
            self.log(u'...replacing {0}'.format(self.download.target))
            self.continue_download_file(True)
        elif self.auto_conflict_resolution == ProgramPageDownload.CONFLICT_RESOLUTION_SKIP:
            self.log('...skipped')
            self.download_next_file()
        else:
            self.progress_file.setVisible(False)

            try:
                target_stat = os.stat(self.target_path)

                self.label_existing_stats.setText('{0}, last modified on {1}'
                                                  .format(get_file_display_size(target_stat.st_size),
                                                          timestamp_to_date_at_time(int(target_stat.st_mtime))))
            except Exception as e:
                self.label_existing_stats.setText(u'<b>Error</b>: Could not get informarion for target file: {0}', Qt.escape(unicode(e)))

            self.label_new_stats.setText('{0}, last modified on {1}'
                                         .format(self.chunked_downloader.source_display_size,
                                                 timestamp_to_date_at_time(int(self.chunked_downloader.source_file.modification_time))))

            self.label_replace_help.setText(self.replace_help_template.replace('<FILE>', Qt.escape(self.download.target)))
            self.check_rename_new_file.setChecked(self.auto_conflict_resolution == ProgramPageDownload.CONFLICT_RESOLUTION_RENAME)
            self.edit_new_name.setText('') # force a new-name check
            self.edit_new_name.setText(os.path.split(self.download.target)[1])

            self.conflict_resolution_in_progress = True
            self.update_ui_state()

    def resolve_conflict_by_replace(self):
        if not self.conflict_resolution_in_progress or self.check_rename_new_file.isChecked():
            return

        self.log(u'...replacing {0}'.format(self.download.target))

        if self.check_remember_decision.isChecked():
            self.auto_conflict_resolution = ProgramPageDownload.CONFLICT_RESOLUTION_REPLACE
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.continue_download_file(True)

    def rename_download_target(self, new_name):
        if not self.conflict_resolution_in_progress:
            return

        self.download    = Download(self.download.source, os.path.join(os.path.split(self.download.target)[0], new_name))
        self.target_path = os.path.join(self.download_directory, self.download.target)

    def resolve_conflict_by_rename(self):
        if not self.conflict_resolution_in_progress or not self.check_rename_new_file.isChecked():
            return

        self.rename_download_target(self.edit_new_name.text())
        self.log(u'...downloading as {0}'.format(self.download.target))

        if self.check_remember_decision.isChecked():
            self.auto_conflict_resolution = ProgramPageDownload.CONFLICT_RESOLUTION_RENAME
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.continue_download_file(False)

    def skip_conflict(self):
        if not self.conflict_resolution_in_progress:
            return

        if self.check_remember_decision.isChecked():
            self.auto_conflict_resolution = ProgramPageDownload.CONFLICT_RESOLUTION_SKIP
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.log('...skipped')
        self.download_next_file()

    def download_files_done(self):
        self.progress_file.setVisible(False)

        # download successful
        self.next_step('Download successful!')

        self.progress_total.setValue(self.progress_total.maximum())

        self.wizard().setOption(QWizard.NoCancelButton, True)
        self.download_successful = True
        self.completeChanged.emit()
