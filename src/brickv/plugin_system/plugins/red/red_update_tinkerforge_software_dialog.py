# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2018-2019 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

red_update_tinkerforge_software.py: RED Brick Tinkerforge Software Update Dialog

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

import json
import queue
import urllib.request
import urllib.error
import posixpath

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QFont

from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call
from brickv.plugin_system.plugins.red.ui_red_update_tinkerforge_software import Ui_REDUpdateTinkerforgeSoftware
import brickv.infos

# As a work-around for https://github.com/pyinstaller/pyinstaller/issues/4064 use a local copy of distutils.version.
from .version import StrictVersion

class REDUpdateTinkerforgeSoftwareDialog(QDialog, Ui_REDUpdateTinkerforgeSoftware):
    # States.
    STATE_INIT = 1
    STATE_CHECKING_FOR_UPDATES = 2
    STATE_NO_UPDATES_AVAILABLE = 3
    STATE_UPDATES_AVAILABLE = 4
    STATE_UPDATE_IN_PROGRESS = 5
    STATE_UPDATE_DONE = 6

    # Messages.
    MESSAGE_INFO_START = '''With this utility you can check and update all the \
Tinkerforge bindings and Tinkerforge Brick Viewer installed in your RED Brick.<br/><br/>
To check whether you need updates click the <b>"Check for Updates"</b> button below.'''
    MESSAGE_INFO_STATE_UPDATE_DONE = 'Update successful!'
    MESSAGE_INFO_STATE_NO_UPDATES_AVAILABLE = 'There are no updates available for the RED Brick.'
    MESSAGE_INFO_STATE_UPDATES_AVAILABLE = '<b>The following updates are available:</b>'
    MESSAGE_INFO_STATE_UPDATE_IN_PROGRESS = 'Updating RED Brick Tinkerforge software.\
\n\nDepending on the number of updates available and the current load of the \
RED Brick it can take a while for the update process to finish. If you close \
this window before the update has finished then the current update process will \
be cancelled.\n\nPlease wait...'
    MESSAGE_INFO_STATE_CHECKING_FOR_UPDATES = 'Checking if Tinkerforge software needs to be updated.\n\nPlease wait...'
    MESSAGE_ERR_UPDATE = 'Error while updating'
    MESSAGE_ERR_CHECK_LATEST_VERSIONS = 'Error while getting latest versions from tinkerforge.com. \
Please make sure that your internet connection is working.'
    MESSAGE_ERR_GET_INSTALLED_VERSIONS = 'Error while getting installed versions from the RED Brick'

    FMT_LI = '<li style="margin-bottom: 5px;">{0} [{1} --> {2}]</li>'
    URL_LATEST_VERSIONS = 'http://download.tinkerforge.com/latest_versions.txt'

    def __init__(self, parent, session, script_manager):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.red_plugin = parent

        self.setAttribute(Qt.WA_DeleteOnClose)

        font = QFont()
        self.tedit_main.setFont(font)

        self.session = session
        self.dialog_session = True
        self.script_manager = script_manager

        self.update_info = None
        self.current_state = self.STATE_INIT
        self.update_install_serialisation_queue = queue.Queue()

        self.pbar.hide()
        self.label_pbar.hide()
        self.tedit_main.setText(self.MESSAGE_INFO_START)

        # Connect signals.
        self.pbutton_n.clicked.connect(self.pbutton_n_clicked)
        self.pbutton_p.clicked.connect(self.pbutton_p_clicked)

    def closeEvent(self, _event):
        self.dialog_session = False
        self.red_plugin.get_bindings_versions_async()

    def handle_update_tf_software_install_cb(self):
        if self.update_info['processed'] == self.update_info['updates_total']:
            self.pbar.setValue(100)
            self.label_pbar.setText('')
            self.label_pbar.hide()

            if self.update_info['error']:
                self.set_current_state(self.STATE_INIT)
                self.tedit_main.setText(self.update_info['error_messages'])
            else:
                self.set_current_state(self.STATE_UPDATE_DONE)
                self.tedit_main.setText(self.MESSAGE_INFO_STATE_UPDATE_DONE)
        else:
            self.pbar.setValue(75 + int(float(self.update_info['processed']) / float(self.update_info['updates_total']) * 25.0))
            # Go for the next update to be installed.
            self.do_next_update_install()

    def cb_update_tf_software_copy_bindings(self, result):
        if not self.dialog_session:
            return

        if not result or result.exit_code != 0:
            self.update_info['error'] = True
            self.update_info['error_messages'] += 'Error while copying bindings:\n'

            if result.stdout:
                self.update_info['error_messages'] += result.stdout

            if result.stderr:
                self.update_info['error_messages'] += result.stderr

            self.update_info['error_messages'] += '\n\n'

        self.handle_update_tf_software_install_cb()

    def cb_update_tf_software_install(self, is_binding, name, result):
        if not self.dialog_session:
            return

        display_name = ''
        self.update_info['processed'] = self.update_info['processed'] + 1

        if name == 'brickv':
            display_name = self.update_info['brickv']['display_name']
        else:
            for d in self.update_info['bindings']:
                if d['name'] != name:
                    continue

                display_name = d['display_name']

                break

        if not result or result.exit_code != 0:
            self.update_info['error'] = True
            self.update_info['error_messages'] += 'Error while installing ' + display_name + ':\n'

            if (not result.stdout) and (not result.stderr):
                self.update_info['error_messages'] += 'Unknown error.\n'
            elif result.stdout and (not result.stderr):
                self.update_info['error_messages'] += result.stdout
            elif (not result.stdout) and result.stderr:
                self.update_info['error_messages'] += result.stderr
            else:
                self.update_info['error_messages'] += result.stdout + '\n' + result.stderr

            self.update_info['error_messages'] += '\n\n'

            self.handle_update_tf_software_install_cb()
        else:
            self.label_pbar.setText('Installed ' + display_name)

            if is_binding:
                '''
                Copy the bindings from the temp directory to the target directory.

                This copy will update the changelog which is the basis of update detection.
                It is important to ensure that the copying is done *AFTER* the update process was successful.
                '''
                self.script_manager.execute_script('update_tf_software_copy_bindings',
                                                   self.cb_update_tf_software_copy_bindings,
                                                   [posixpath.join(self.update_info['temp_dir'], 'bindings'), name])
            else:
                self.handle_update_tf_software_install_cb()

    def do_next_update_install(self):
        if not self.dialog_session:
            return

        update_candidate = self.update_install_serialisation_queue.get()

        # Initiate install of the current update.
        self.script_manager.execute_script('update_tf_software_install',
                                           lambda r: self.cb_update_tf_software_install(update_candidate['is_binding'],
                                                                                        update_candidate['name'],
                                                                                        r),
                                           [update_candidate['name'],
                                            update_candidate['temp_dir'],
                                            update_candidate['temp_dir_abs_path']])

    def write_async_cb_r(self, name, red_file, exception):
        red_file.release()

        if not self.dialog_session:
            return

        display_name = ''
        self.update_info['processed'] = self.update_info['processed'] + 1

        if name == 'brickv':
            display_name = self.update_info['brickv']['display_name']
        else:
            for d in self.update_info['bindings']:
                if d['name'] != name:
                    continue

                display_name = d['display_name']

                break

        if exception is not None:
            self.update_info['error'] = True
            self.update_info['error_messages'] += 'Error while writing' + \
                                                  display_name + 'update:\n' + \
                                                  str(exception) + '\n\n'
        else:
            # Enqueue updates to be installed.
            if name == 'brickv':
                self.update_install_serialisation_queue.put({'is_binding': False,
                                                             'name': self.update_info['brickv']['name'],
                                                             'temp_dir': self.update_info['temp_dir'],
                                                             'temp_dir_abs_path': posixpath.join(self.update_info['temp_dir'], 'brickv_linux_latest.deb')})
            else:
                self.update_install_serialisation_queue.put({'is_binding': True,
                                                             'name': d['name'],
                                                             'temp_dir': self.update_info['temp_dir'],
                                                             'temp_dir_abs_path': posixpath.join(self.update_info['temp_dir'], 'tinkerforge_' + d['name'] + '_bindings_latest.zip')})

        self.pbar.setValue(50 + int(self.update_info['processed'] * 100.00 / self.update_info['updates_total'] / 6.0))
        self.label_pbar.setText('Stored ' + display_name)

        if self.update_info['processed'] == self.update_info['updates_total']:
            self.pbar.setValue(75)
            self.update_info['processed'] = 0
            # Start serially installing the updates.
            self.do_next_update_install()

    def do_write_update_file(self, name, data, red_file):
        if not self.dialog_session:
            return

        red_file.write_async(data, lambda r: self.write_async_cb_r(name, red_file, r), None)

    def start_writing_updates(self):
        if not self.dialog_session:
            return

        if self.update_info['error']:
            self.set_current_state(self.STATE_INIT)
            self.tedit_main.setText(self.update_info['error_messages'])
        else:
            self.update_info['error'] = False
            self.update_info['processed'] = 0
            self.update_info['error_messages'] = ''

            if self.update_info['brickv']['update']:
                self.do_write_update_file('brickv',
                                          self.update_info['brickv']['data'],
                                          self.update_info['brickv']['red_file'])

            for d in self.update_info['bindings']:
                if not d['update']:
                    continue

                self.do_write_update_file(d['name'], d['data'], d['red_file'])

    def cb_rfile_open_s(self, name, red_file):
        if not self.dialog_session:
            return

        self.update_info['processed'] = self.update_info['processed'] + 1

        if not self.update_info['error']:
            if name == 'brickv':
                self.update_info['brickv']['red_file'] = red_file
            else:
                for i, d in enumerate(self.update_info['bindings']):
                    if d['name'] != name:
                        continue

                    self.update_info['bindings'][i]['red_file'] = red_file

                    break

        if self.update_info['processed'] == self.update_info['updates_total']:
            self.start_writing_updates()

    def cb_rfile_open_f(self, name, exception):
        if not self.dialog_session:
            return

        self.update_info['error'] = True
        self.update_info['processed'] = self.update_info['processed'] + 1

        if name == 'brickv':
            self.update_info['error_messages'] += 'Error opening update file ' + self.update_info['brickv']['display_name'] + ':\n'
        else:
            for d in self.update_info['bindings']:
                if d['name'] != name:
                    continue

                self.update_info['error_messages'] += 'Error opening update file ' + d['display_name'] + ':\n'

                break

        self.update_info['error_messages'] += str(exception) + '\n\n'

        if self.update_info['processed'] == self.update_info['updates_total']:
            self.start_writing_updates()

    def do_open_update_file(self, red_file, name, path):
        if not self.dialog_session:
            return

        async_call(red_file.open,
                   (path,
                    REDFile.FLAG_WRITE_ONLY |
                    REDFile.FLAG_CREATE |
                    REDFile.FLAG_NON_BLOCKING |
                    REDFile.FLAG_TRUNCATE,
                    0o755,
                    0,
                    0),
                   lambda red_file: self.cb_rfile_open_s(name, red_file),
                   lambda e: self.cb_rfile_open_f(name, e),
                   pass_exception_to_error_callback=True)

    def do_install_updates(self):
        if not self.dialog_session:
            return

        if self.update_info['error']:
            self.set_current_state(self.STATE_INIT)
            self.tedit_main.setText(self.update_info['error_messages'])
        else:
            def cb_update_tf_software_mkdtemp(result):
                if not self.dialog_session:
                    return

                if result and result.stdout and result.exit_code == 0:
                    self.update_info['processed'] = 0
                    self.update_info['error'] = False
                    self.update_info['error_messages'] = ''
                    self.update_info['temp_dir'] = result.stdout.strip()

                    if self.update_info['brickv']['update']:
                        self.do_open_update_file(REDFile(self.session),
                                                 'brickv',
                                                 posixpath.join(self.update_info['temp_dir'], 'brickv_linux_latest.deb'))

                    for d in self.update_info['bindings']:
                        if not d['update']:
                            continue

                        self.do_open_update_file(REDFile(self.session),
                                                 d['name'],
                                                 posixpath.join(self.update_info['temp_dir'], 'tinkerforge_' + d['name'] + '_bindings_latest.zip'))

                else:
                    if result.stderr:
                        msg = self.MESSAGE_ERR_UPDATE + ':\n' + result.stderr + '\n\n'
                    else:
                        msg = self.MESSAGE_ERR_UPDATE + '.\n\n'

                    self.set_current_state(self.STATE_INIT)
                    self.tedit_main.setText(msg)

            self.script_manager.execute_script('update_tf_software_mkdtemp',
                                               cb_update_tf_software_mkdtemp)

    def download_update_async(self, name, url):
        if not self.dialog_session:
            return '', ''

        response = urllib.request.urlopen(url, timeout=10)

        return name, response.read()

    def download_update_s_async_cb(self, result):
        if not self.dialog_session:
            return

        display_name = ''
        name, data = result

        if not self.update_info['error']:
            if name == 'brickv':
                self.update_info['brickv']['data'] = data
                display_name = self.update_info['brickv']['display_name']

            else:
                for d in self.update_info['bindings']:
                    if d['name'] != name:
                        continue

                    d['data'] = data
                    display_name = d['display_name']

                    break

        self.pbar.setValue(int(self.update_info['processed'] * 100.00 / self.update_info['updates_total'] / 2.0))
        self.label_pbar.setText('Downloaded ' + display_name)

        self.update_info['processed'] = self.update_info['processed'] + 1

        if self.update_info['processed'] == self.update_info['updates_total']:
            self.pbar.setValue(50)
            self.do_install_updates()

    def download_update_f_async_cb(self, name, exception):
        if not self.dialog_session:
            return

        display_name = ''
        _exception = str(exception)
        self.update_info['error'] = True
        self.update_info['processed'] = self.update_info['processed'] + 1

        if _exception.startswith('<') and _exception.endswith('>'):
            _exception = _exception[1:-1]

        if name == 'brickv':
            display_name = self.update_info['brickv']['display_name']
            self.update_info['error_messages'] += 'Error while downloading ' + self.update_info['brickv']['display_name'] + ' update:\n'
        else:
            for d in self.update_info['bindings']:
                if d['name'] != name:
                    continue

                display_name = d['display_name']
                self.update_info['error_messages'] += 'Error while downloading ' + d['display_name'] + ' update:\n'

                break

        self.pbar.setValue(int(self.update_info['processed'] * 100.00 / self.update_info['updates_total'] / 2.0))
        self.label_pbar.setText('Downloaded ' + display_name)

        self.update_info['error_messages'] += _exception + '\n\n'

        if self.update_info['processed'] == self.update_info['updates_total']:
            self.do_install_updates()

    def do_download_update_async_call(self, name, url):
        if not self.dialog_session:
            return

        async_call(self.download_update_async,
                   (name, url),
                   self.download_update_s_async_cb,
                   lambda e: self.download_update_f_async_cb(name, e),
                   pass_exception_to_error_callback=True)

    def check_update_available(self, update_info):
        if not self.dialog_session:
            return False

        if 'brickv' in update_info and \
           'name' in update_info['brickv'] and \
           'display_name' in update_info['brickv'] and \
           'from' in update_info['brickv'] and \
           'to' in update_info['brickv'] and \
           'update' in update_info['brickv']:
            if update_info['brickv']['name'] == '-' or \
               update_info['brickv']['display_name'] == '-' or \
               update_info['brickv']['from'] == '0' or \
               update_info['brickv']['to'] == '0':
                return False
        else:
            return False

        for d in update_info['bindings']:
            if 'name' in d and 'from' in d and 'to' in d and 'update' in d:
                if d['name'] == '-' or \
                   d['display_name'] == '-' or \
                   d['from'] == '0' or \
                   d['to'] == '0':
                    return False
            else:
                return False

        return True

    def do_update_available_message(self, update_info):
        if not self.dialog_session:
            return

        self.update_info = update_info

        msg = self.MESSAGE_INFO_STATE_UPDATES_AVAILABLE + '<ul>'

        image_supports_brickv_2_4 = self.red_plugin.device_info.firmware_version_installed >= (1, 14, 0)

        if self.update_info['brickv']['update']:
            if image_supports_brickv_2_4:
                msg += self.FMT_LI.format('Brick Viewer', self.update_info['brickv']['from'], self.update_info['brickv']['to'])
            else:
                msg += '<li style="margin-bottom: 5px;">{0} [{1} --> {2}] <font color="red">Will not be installed: Brick Viewer 2.4 requires at least RED Brick Image 1.14</font></li>'.format('Brick Viewer', self.update_info['brickv']['from'], self.update_info['brickv']['to'])
                self.update_info['brickv']['update'] = False

        for d in sorted(self.update_info['bindings'], key=lambda d: d['name']):
            if not d['update']:
                continue

            if d['name'] == 'c':
                msg += self.FMT_LI.format('C/C++ Bindings', d['from'], d['to'])

            elif d['name'] == 'csharp':
                msg += self.FMT_LI.format('C#/Mono Bindings', d['from'], d['to'])

            elif d['name'] == 'delphi':
                msg += self.FMT_LI.format('Delphi/Lazarus Bindings', d['from'], d['to'])

            elif d['name'] == 'java':
                msg += self.FMT_LI.format('Java Bindings', d['from'], d['to'])

            elif d['name'] == 'javascript':
                msg += self.FMT_LI.format('JavaScript Bindings', d['from'], d['to'])

            elif d['name'] == 'matlab':
                msg += self.FMT_LI.format('Octave Bindings', d['from'], d['to'])

            elif d['name'] == 'perl':
                msg += self.FMT_LI.format('Perl Bindings', d['from'], d['to'])

            elif d['name'] == 'php':
                msg += self.FMT_LI.format('PHP Bindings', d['from'], d['to'])

            elif d['name'] == 'python':
                msg += self.FMT_LI.format('Python Bindings', d['from'], d['to'])

            elif d['name'] == 'ruby':
                msg += self.FMT_LI.format('Ruby Bindings', d['from'], d['to'])

            elif d['name'] == 'shell':
                msg += self.FMT_LI.format('Shell Bindings', d['from'], d['to'])

            elif d['name'] == 'vbnet':
                msg += self.FMT_LI.format('VB.NET Bindings', d['from'], d['to'])

        msg += '</ul><br/>'

        self.tedit_main.setText(msg)

    def update_latest_version_info(self, update_info, key, version_to, display_name):
        if not self.dialog_session:
            return False, False

        found = False
        updates_available = False

        for d in update_info['bindings']:
            if d['name'] != key:
                continue
            else:
                found = True
                d['to'] = version_to
                d['display_name'] = display_name
                version_to = StrictVersion(d['to'].strip())
                version_from = StrictVersion(d['from'].strip())

                if version_to > version_from:
                    updates_available = True
                    d['update'] = True
                else:
                    d['update'] = False

                break

        return found, updates_available

    def update_state_gui(self, state):
        if not self.dialog_session:
            return

        if state == self.STATE_INIT:
            self.pbar.hide()
            self.label_pbar.hide()
            self.pbutton_n.setEnabled(True)
            self.pbutton_p.setEnabled(True)
            self.pbutton_p.setText('Check for Updates')

        elif state == self.STATE_CHECKING_FOR_UPDATES:
            self.pbar.show()
            self.label_pbar.hide()
            self.pbar.setMinimum(0)
            self.pbar.setMaximum(0)
            self.pbutton_n.setEnabled(False)
            self.pbutton_p.setEnabled(False)
            self.pbutton_p.setText('Checking for Updates...')
            self.tedit_main.setText(self.MESSAGE_INFO_STATE_CHECKING_FOR_UPDATES)

        elif state == self.STATE_NO_UPDATES_AVAILABLE:
            self.pbar.hide()
            self.label_pbar.hide()
            self.pbutton_n.setEnabled(True)
            self.pbutton_p.setEnabled(True)
            self.pbutton_p.setText('Check for Updates')
            self.tedit_main.setText(self.MESSAGE_INFO_STATE_NO_UPDATES_AVAILABLE)

        elif state == self.STATE_UPDATES_AVAILABLE:
            self.pbar.hide()
            self.label_pbar.hide()
            self.tedit_main.setText('')
            self.pbutton_n.setEnabled(True)
            self.pbutton_p.setEnabled(True)
            self.pbutton_p.setText('Update')

        elif state == self.STATE_UPDATE_IN_PROGRESS:
            self.pbar.show()
            self.label_pbar.hide()
            self.pbar.setMinimum(0)
            self.pbar.setMaximum(0)
            self.pbutton_n.setEnabled(False)
            self.pbutton_p.setEnabled(False)
            self.pbutton_p.setText('Updating...')
            self.tedit_main.setText(self.MESSAGE_INFO_STATE_UPDATE_IN_PROGRESS)

        elif state == self.STATE_UPDATE_DONE:
            self.pbar.hide()
            self.label_pbar.hide()
            self.pbutton_n.setEnabled(True)
            self.pbutton_p.setEnabled(True)
            self.pbutton_p.setText('Check for Updates')
            self.tedit_main.setText(self.MESSAGE_INFO_STATE_UPDATE_DONE)

    def set_current_state(self, state):
        if not self.dialog_session:
            return

        self.current_state = state
        self.update_state_gui(self.current_state)

    def pbutton_n_clicked(self):
        self.done(0)

    def pbutton_p_clicked(self):
        if not self.dialog_session:
            return

        if self.current_state == self.STATE_UPDATES_AVAILABLE:
            self.set_current_state(self.STATE_UPDATE_IN_PROGRESS)
            self.tedit_main.setText(self.MESSAGE_INFO_STATE_UPDATE_IN_PROGRESS)

            updates_total = 0

            if self.update_info['brickv']['update']:
                updates_total = updates_total + 1

            for d in self.update_info['bindings']:
                if d['update']:
                    updates_total = updates_total + 1

            if updates_total == 0:
                self.set_current_state(self.STATE_UPDATE_DONE)
                return

            self.update_info['processed'] = 0
            self.update_info['updates_total'] = updates_total

            self.pbar.setMinimum(0)
            self.pbar.setMaximum(100)

            self.label_pbar.show()

            self.pbar.setValue(0)

            if self.update_info['brickv']['update']:
                # Try to get the Brick Viewer update.
                url = 'http://download.tinkerforge.com/tools/brickv/linux/brickv_linux_latest.deb'

                self.do_download_update_async_call(self.update_info['brickv']['name'], url)

            for d in self.update_info['bindings']:
                # Try to get the binding updates.
                if d['update']:
                    url = 'http://download.tinkerforge.com/bindings/' + d['name'] + '/tinkerforge_' + d['name'] + '_bindings_latest.zip'

                    self.do_download_update_async_call(d['name'], url)

        else:
            def cb_update_tf_software_get_installed_versions(result):
                if not self.dialog_session:
                    return

                self.set_current_state(self.STATE_NO_UPDATES_AVAILABLE)

                if result and result.stdout and result.exit_code == 0:
                    updates_available_main = False
                    update_info = {'brickv': {},
                                   'processed': 0,
                                   'temp_dir': '',
                                   'bindings': [],
                                   'error': False,
                                   'updates_total': 0,
                                   'error_messages': ''}

                    installed_versions = json.loads(result.stdout)

                    if not isinstance(installed_versions, dict):
                        self.set_current_state(self.STATE_INIT)
                        self.tedit_main.setText(self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.')

                        return

                    for key, value in installed_versions.items():
                        if key == 'brickv':
                            update_info['brickv']['to'] = '0'
                            update_info['brickv']['name'] = '-'
                            update_info['brickv']['from'] = '0'
                            update_info['brickv']['data'] = None
                            update_info['brickv']['update'] = False
                            update_info['brickv']['display_name'] = '-'

                            if isinstance(value, str) and value != '' and value != '-':
                                update_info['brickv']['from'] = value
                                update_info['brickv']['name'] = 'brickv'

                                continue
                            else:
                                self.set_current_state(self.STATE_INIT)
                                self.tedit_main.setText(self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.')

                                return

                        elif key == 'bindings':
                            if isinstance(value, dict) and value:
                                for k, v in value.items():
                                    d = {}

                                    d['to'] = '0'
                                    d['name'] = '-'
                                    d['from'] = '0'
                                    d['data'] = None
                                    d['update'] = False
                                    d['display_name'] = '-'

                                    if isinstance(v, str) and v != '' and v != '-':
                                        d['from'] = v
                                        d['name'] = k.strip()

                                        update_info['bindings'].append(d)
                                    else:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.')

                                        return
                                continue
                            else:
                                self.set_current_state(self.STATE_INIT)
                                self.tedit_main.setText(self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.')

                                return
                        else:
                            self.set_current_state(self.STATE_INIT)
                            self.tedit_main.setText(self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.')

                            return

                    # Try to get the latest version numbers.
                    try:
                        response = urllib.request.urlopen(self.URL_LATEST_VERSIONS, timeout=10)
                        response_data = response.read().decode('utf-8')
                    except urllib.error.URLError:
                        self.set_current_state(self.STATE_INIT)
                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                        return

                    response_data_lines = response_data.splitlines()

                    if len(response_data_lines) < 1:
                        self.set_current_state(self.STATE_INIT)
                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                        return

                    for l in response_data_lines:
                        l_split = l.strip().split(':')

                        if len(l_split) != 3:
                            self.set_current_state(self.STATE_INIT)
                            self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                            return
                        else:
                            if l_split[0] == 'tools' and l_split[1] == 'brickv':
                                update_info['brickv']['to'] = l_split[2]
                                update_info['brickv']['display_name'] = 'Brick Viewer'
                                version_to = StrictVersion(l_split[2].strip())
                                version_from = StrictVersion(update_info['brickv']['from'].strip())

                                if version_to > version_from:
                                    updates_available_main = True
                                    update_info['brickv']['update'] = True
                                else:
                                    update_info['brickv']['update'] = False

                                continue

                            elif l_split[0] == 'bindings':
                                if l_split[1] == 'c':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'C/C++ Bindings')

                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'csharp':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'C#/Mono Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'delphi':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Delphi/Lazarus Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'java':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Java Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'javascript':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'JavaScript Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'matlab':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Octave Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'perl':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Perl Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'php':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'PHP Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'python':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Python Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'ruby':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Ruby Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'shell':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'Shell Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True

                                elif l_split[1] == 'vbnet':
                                    found, updates_available = self.update_latest_version_info(update_info,
                                                                                               l_split[1],
                                                                                               l_split[2],
                                                                                               'VB.NET Bindings')
                                    if not found:
                                        self.set_current_state(self.STATE_INIT)
                                        self.tedit_main.setText(self.MESSAGE_ERR_CHECK_LATEST_VERSIONS)

                                        return

                                    if updates_available:
                                        updates_available_main = True
                else:
                    if result and result.stderr:
                        msg = self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + ':\n' + result.stderr + '\n\n'
                    else:
                        msg = self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.\n\n'

                    self.set_current_state(self.STATE_INIT)
                    self.tedit_main.setText(msg)

                    return

                self.red_plugin.bindings_version_success(result)

                _check_update_available = self.check_update_available(update_info)

                if not _check_update_available:
                    self.set_current_state(self.STATE_INIT)
                    self.tedit_main.setText(self.MESSAGE_ERR_GET_INSTALLED_VERSIONS + '.')

                    return

                if updates_available_main:
                    self.set_current_state(self.STATE_UPDATES_AVAILABLE)
                    self.do_update_available_message(update_info)
                else:
                    self.set_current_state(self.STATE_NO_UPDATES_AVAILABLE)
                    self.tedit_main.setText(self.MESSAGE_INFO_STATE_NO_UPDATES_AVAILABLE)

            self.set_current_state(self.STATE_CHECKING_FOR_UPDATES)

            self.script_manager.execute_script('update_tf_software_get_installed_versions',
                                               cb_update_tf_software_get_installed_versions)
