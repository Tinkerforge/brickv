# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_openhab.py: RED settings openHAB tab implementation

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
import posixpath
import html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QInputDialog, QPlainTextEdit, QLabel, QMessageBox
from PyQt5.QtGui import QFont, QTextOption

from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.ui_red_tab_settings_openhab import Ui_REDTabSettingsOpenHAB
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import ExpandingProgressDialog, ExpandingInputDialog
from brickv.plugin_system.plugins.red.script_manager import check_script_result, report_script_result

class ConfigFile(object):
    def __init__(self, display_name, absolute_name, tab, deletable=True):
        self.display_name   = display_name # is unique
        self.absolute_name  = absolute_name # is also unique
        self.tab            = tab
        self.deletable      = deletable
        self.index          = -1
        self.modified       = False
        self.content        = None
        self.edit           = QPlainTextEdit()

        font = QFont('monospace')
        font.setStyleHint(QFont.TypeWriter)

        self.edit.setWordWrapMode(QTextOption.NoWrap)
        self.edit.setFont(font)
        self.edit.textChanged.connect(self.check_content)

    def check_content(self):
        self.set_modified(self.content != self.edit.toPlainText())

    def set_modified(self, modified):
        if self.modified == modified:
            return

        self.modified = modified

        self.tab.combo_config.setItemText(self.index, self.get_combo_item())
        self.tab.update_ui_state()

    def set_content(self, content):
        # FIXME: QPlainTextEdit does not preserve the original line endings, but
        #        converts all line endings to \n. this results in a difference
        #        between self.content and the content stored in the QPlainTextEdit
        #        even if the user did not edit the content. avoid this problem
        #        by converting all line endings to \n before setting the content
        #        of the QPlainTextEdit
        content = content.replace('\r\n', '\n')

        if self.content == None:
            self.edit.setPlainText(content)

        self.content = content

        self.check_content()

    def get_combo_item(self):
        if self.modified:
            return self.display_name + ' (modified)'
        else:
            return self.display_name

    def discard_changes(self):
        self.edit.setPlainText(self.content)
        self.set_modified(False)

class REDTabSettingsOpenHAB(QWidget, Ui_REDTabSettingsOpenHAB):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session             = None # Set from REDTabSettings
        self.script_manager      = None # Set from REDTabSettings
        self.image_version       = None # Set from REDTabSettings
        self.service_state       = None # Set from REDTabSettings
        self.action_in_progress  = False
        self.configs             = None

        self.recreate_widgets()

        self.combo_config.currentIndexChanged.connect(self.update_ui_state)
        self.button_refresh.clicked.connect(lambda: self.refresh_all_configs(None))
        self.button_new.clicked.connect(self.new_config)
        self.button_delete.clicked.connect(self.delete_config)
        self.button_discard.clicked.connect(self.discard_changes)
        self.button_apply.clicked.connect(self.apply_changes)

        self.label_progress.setVisible(False)
        self.progress.setVisible(False)
        self.edit_errors.setVisible(False)

        self.stacked_container.setCurrentIndex(self.combo_config.currentIndex())

    def tab_on_focus(self):
        if self.image_version.number < (1, 6):
            self.label_unsupported.show()
            self.label_disabled.hide()
            self.widget_controls.hide()
        elif not self.service_state.openhab:
            self.label_unsupported.hide()
            self.label_disabled.show()
            self.widget_controls.hide()
        else:
            self.label_unsupported.hide()
            self.label_disabled.hide()
            self.widget_controls.show()
            self.refresh_all_configs(None)

        if self.image_version.number < (1, 10):
            self.configs = [
                ConfigFile('openhab.cfg', '/etc/openhab/configurations/openhab.cfg', self, deletable=False),
                ConfigFile('logback.xml', '/etc/openhab/logback.xml', self, deletable=False)
            ]
        else:
            self.configs = [
                ConfigFile('tinkerforge.cfg', '/etc/openhab2/services/tinkerforge.cfg', self, deletable=False),
                ConfigFile('org.ops4j.pax.logging.cfg', '/var/lib/openhab2/etc/org.ops4j.pax.logging.cfg', self, deletable=False)
            ]

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def update_ui_state(self):
        index  = self.combo_config.currentIndex()

        if self.configs:
            config = self.configs[index]

        self.stacked_container.setCurrentIndex(index)

        self.label_progress.setVisible(self.action_in_progress)
        self.progress.setVisible(self.action_in_progress)

        self.combo_config.setEnabled(not self.action_in_progress)
        self.button_refresh.setEnabled(not self.action_in_progress)
        self.button_new.setEnabled(not self.action_in_progress)
        self.button_delete.setEnabled(not self.action_in_progress and config.deletable)
        self.stacked_container.setEnabled(not self.action_in_progress)
        self.button_discard.setEnabled(not self.action_in_progress and config.modified)
        self.button_apply.setEnabled(not self.action_in_progress and config.modified)

    def recreate_widgets(self):
        index = self.combo_config.currentIndex()

        if index >= 0:
            selected_display_name = self.combo_config.itemData(index)
        else:
            selected_display_name = None

        self.combo_config.clear()

        while self.stacked_container.count() > 0:
            self.stacked_container.removeWidget(self.stacked_container.widget(0))

        index = -1

        if self.configs:
            for config in self.configs:
                if config == None:
                    self.combo_config.insertSeparator(self.combo_config.count())
                    self.stacked_container.addWidget(QLabel('<dummy>'))
                else:
                    config.index = self.combo_config.count()

                    self.combo_config.addItem(config.get_combo_item(), config.display_name)
                    self.stacked_container.addWidget(config.edit)

                    if config.display_name == selected_display_name:
                        index = config.index

        if index >= 0:
            self.combo_config.setCurrentIndex(index)

    def log_error(self, message):
        self.edit_errors.show()
        self.edit_errors.appendHtml('<b>{0}</b>'.format(html.escape(message)))

    def refresh_config(self, index, done_callback):
        if index >= len(self.configs):
            self.action_in_progress = False
            self.update_ui_state()

            if done_callback != None:
                done_callback()

            return

        config = self.configs[index]

        if config == None:
            self.refresh_config(index + 1, done_callback)
            return

        self.action_in_progress = True
        self.update_ui_state()

        self.label_progress.setText('Downloading ' + config.absolute_name)

        def cb_open(red_file):
            def cb_read(result):
                red_file.release()

                self.action_in_progress = False
                self.update_ui_state()

                if result.error != None:
                    if result.error.error_code != REDError.E_OPERATION_ABORTED and \
                       result.error.error_code != REDError.E_DOES_NOT_EXIST:
                        self.log_error('Error while reading {0}: {1}'.format(config.display_name, error))
                    else:
                        config.set_content('')
                else:
                    try:
                        content = result.data.decode('utf-8')
                    except UnicodeDecodeError:
                        # FIXME: maybe add a encoding guesser here or try some common encodings if UTF-8 fails
                        self.log_error('Error: Config file {0} is not UTF-8 encoded'.format(config.display_name))
                    else:
                        config.set_content(content)

                self.refresh_config(index + 1, done_callback)

            red_file.read_async(red_file.length, cb_read)

        def cb_open_error(error):
            if isinstance(error, REDError) and \
               error.error_code != REDError.E_OPERATION_ABORTED and \
               error.error_code != REDError.E_DOES_NOT_EXIST:
                self.log_error('Error while opening {0}: {1}'.format(config.display_name, error))
            else:
                config.set_content('')

            self.refresh_config(index + 1, done_callback)

        async_call(REDFile(self.session).open,
                   (config.absolute_name, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open, cb_open_error, report_exception=True)

    def refresh_all_configs(self, done_callback):
        self.edit_errors.hide()
        self.edit_errors.setPlainText('')

        def cb_openhab_configs_list(result):
            okay, message = check_script_result(result, decode_stderr=True)

            def fatal_error(text):
                self.log_error(text)
                self.action_in_progress = False
                self.update_ui_state()

            if not okay:
                fatal_error('Error while collecting config files: {0}'.format(message))
                return

            try:
                config_names = json.loads(result.stdout)
            except Exception as e:
                fatal_error('Received invalid config file collection: {0}'.format(e))
                return

            if not isinstance(config_names, dict):
                fatal_error('Received invalid config file collection: Not a dictionary')
                return

            try:
                configs_by_basename = {}

                for name in config_names['items']:
                    if self.image_version.number < (1, 10):
                        configs_by_basename.setdefault(name[:-len('.items')], []).append((name, posixpath.join('/etc/openhab/configurations/items', name)))
                    else:
                        configs_by_basename.setdefault(name[:-len('.items')], []).append((name, posixpath.join('/etc/openhab2/items', name)))

                for name in config_names['sitemaps']:
                    if self.image_version.number < (1, 10):
                        configs_by_basename.setdefault(name[:-len('.sitemap')], []).append((name, posixpath.join('/etc/openhab/configurations/sitemaps', name)))
                    else:
                        configs_by_basename.setdefault(name[:-len('.sitemap')], []).append((name, posixpath.join('/etc/openhab2/sitemaps', name)))

                for name in config_names['rules']:
                    if self.image_version.number < (1, 10):
                        configs_by_basename.setdefault(name[:-len('.rules')], []).append((name, posixpath.join('/etc/openhab/configurations/rules', name)))
                    else:
                        configs_by_basename.setdefault(name[:-len('.rules')], []).append((name, posixpath.join('/etc/openhab2/rules', name)))

                for name in config_names['persistence']:
                    if self.image_version.number < (1, 10):
                        configs_by_basename.setdefault(name[:-len('.persist')], []).append((name, posixpath.join('/etc/openhab/configurations/persistence', name)))
                    else:
                        configs_by_basename.setdefault(name[:-len('.persist')], []).append((name, posixpath.join('/etc/openhab2/persistence', name)))

                for name in config_names['scripts']:
                    if self.image_version.number < (1, 10):
                        configs_by_basename.setdefault(name[:-len('.script')], []).append((name, posixpath.join('/etc/openhab/configurations/scripts', name)))
                    else:
                        configs_by_basename.setdefault(name[:-len('.script')], []).append((name, posixpath.join('/etc/openhab2/scripts', name)))

                for name in config_names['transform']:
                    if self.image_version.number < (1, 10):
                        configs_by_basename.setdefault(name[:-len('.transform')], []).append((name, posixpath.join('/etc/openhab/configurations/transform', name)))
                    else:
                        configs_by_basename.setdefault(name[:-len('.transform')], []).append((name, posixpath.join('/etc/openhab2/transform', name)))

            except Exception as e:
                fatal_error('Received invalid config file collection: {0}'.format(e))
                return

            old_configs = {}

            for config in self.configs:
                if config != None:
                    old_configs[config.display_name] = config

            if self.image_version.number < (1, 10):
                self.configs = [old_configs['openhab.cfg'], old_configs['logback.xml']]
            else:
                self.configs = [old_configs['tinkerforge.cfg'], old_configs['org.ops4j.pax.logging.cfg']]

            for key in sorted(configs_by_basename):
                value = configs_by_basename[key]

                if len(value) > 0:
                    self.configs.append(None)

                    for display_name, absolute_name in sorted(value):
                        if display_name in old_configs:
                            self.configs.append(old_configs[display_name])
                        else:
                            self.configs.append(ConfigFile(display_name, absolute_name, self))

            self.recreate_widgets()
            self.refresh_config(0, done_callback)

        self.label_progress.setText('Collecting config files')
        self.action_in_progress = True
        self.update_ui_state()

        self.script_manager.execute_script('openhab_configs_list', cb_openhab_configs_list, max_length=1024*1024)

    def new_config(self):
        dialog = ExpandingInputDialog(get_main_window())
        dialog.setModal(True)
        dialog.setWindowTitle('New Config File')
        dialog.setLabelText('Enter name for new openHAB config file:')
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setOkButtonText('Create')

        if dialog.exec_() != QDialog.Accepted:
            return

        name = dialog.textValue()

        # check that new name is valid as filename
        if len(name) == 0 or name == '.' or name == '..' or '/' in name:
            QMessageBox.critical(get_main_window(), 'New Config File Error',
                                 'A config file name cannot be empty, cannot be one dot [.], cannot be two dots [..] and cannot contain a forward slash [/].')
            return

        endswith_items     = name.endswith('.items')
        endswith_sitemap   = name.endswith('.sitemap')
        endswith_rules     = name.endswith('.rules')
        endswith_persist   = name.endswith('.persist')
        endswith_script    = name.endswith('.script')
        endswith_transform = name.endswith('.transform')

        if not endswith_items and not endswith_sitemap and not endswith_rules and not endswith_persist and not endswith_script and not endswith_transform:
            QMessageBox.critical(get_main_window(), 'New Config File Error',
                                 'A config file name has to end with .items, .sitemap, .rules, .persist, .script or .transform.')
            return

        if name in ['.items', '.sitemap', '.rules', '.persist', '.script', '.transform']:
            QMessageBox.critical(get_main_window(), 'New Config File Error',
                                 '.items, .sitemap, .rules, .persist, .script and .transform cannot be used as config file names.')
            return

        if endswith_items:
            if self.image_version.number < (1, 10):
                target_path = posixpath.join('/', 'etc', 'openhab', 'configurations', 'items', name)
            else:
                target_path = posixpath.join('/', 'etc', 'openhab2', 'items', name)
        elif endswith_sitemap:
            if self.image_version.number < (1, 10):
                target_path = posixpath.join('/', 'etc', 'openhab', 'configurations', 'sitemaps', name)
            else:
                target_path = posixpath.join('/', 'etc', 'openhab2', 'sitemaps', name)
        elif endswith_rules:
            if self.image_version.number < (1, 10):
                target_path = posixpath.join('/', 'etc', 'openhab', 'configurations', 'rules', name)
            else:
                target_path = posixpath.join('/', 'etc', 'openhab2', 'rules', name)
        elif endswith_persist:
            if self.image_version.number < (1, 10):
                target_path = posixpath.join('/', 'etc', 'openhab', 'configurations', 'persistence', name)
            else:
                target_path = posixpath.join('/', 'etc', 'openhab2', 'persistence', name)
        elif endswith_script:
            if self.image_version.number < (1, 10):
                target_path = posixpath.join('/', 'etc', 'openhab', 'configurations', 'scripts', name)
            else:
                target_path = posixpath.join('/', 'etc', 'openhab2', 'scripts', name)
        elif endswith_transform:
            if self.image_version.number < (1, 10):
                target_path = posixpath.join('/', 'etc', 'openhab', 'configurations', 'transform', name)
            else:
                target_path = posixpath.join('/', 'etc', 'openhab2', 'transform', name)

        def cb_open(red_file):
            red_file.release()

            def select_new():
                index = -1

                for config in self.configs:
                    if config != None and config.display_name == name:
                        index = config.index

                if index >= 0:
                    self.combo_config.setCurrentIndex(index)

            self.refresh_all_configs(select_new)

        def cb_open_error(error):
            if isinstance(error, REDError) and error.error_code == REDError.E_ALREADY_EXISTS:
                QMessageBox.critical(get_main_window(), 'New Config File Error',
                                     'Config file {0} already exists.'.format(name))
            else:
                QMessageBox.critical(get_main_window(), 'New Config File Error',
                                     'Could not create config file {0}:\n\n{1}'.format(name, error))

        async_call(REDFile(self.session).open,
                   (target_path, REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_EXCLUSIVE, 0o644, 0, 0),
                   cb_open, cb_open_error, report_exception=True)

    def delete_config(self):
        config = self.configs[self.combo_config.currentIndex()]
        button = QMessageBox.question(get_main_window(), 'Delete Config File',
                                      'Irreversibly deleting config file {0}.'.format(config.display_name),
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if button != QMessageBox.Ok: # FIXME: check if tab is still alive
            return

        self.action_in_progress = True
        self.update_ui_state()

        self.label_progress.setText('Deleting ' + config.absolute_name)

        def cb_delete(result):
            self.action_in_progress = False
            self.update_ui_state()
            self.refresh_all_configs(None)

            report_script_result(result, 'Delete Config File Error', 'Could not delete config file {0}:'.format(config.display_name))

        self.script_manager.execute_script('delete', cb_delete,
                                           [json.dumps([config.absolute_name]), json.dumps([])])

    def discard_changes(self):
        self.configs[self.combo_config.currentIndex()].discard_changes()

    def apply_changes(self):
        config  = self.configs[self.combo_config.currentIndex()]
        content = config.edit.toPlainText()

        self.action_in_progress = True
        self.update_ui_state()

        self.label_progress.setText('Uploading ' + config.absolute_name)

        def cb_open(red_file):
            def cb_write(error):
                def cb_openhab_set_configs_ownership(result):
                    okay, message = check_script_result(result, decode_stderr=True)

                    if not okay:
                        QMessageBox.critical(get_main_window(),
                                             'Apply Changes Error',
                                             'Error while setting ownership of {0}: {1}'.format(config.display_name, message))
                    else:
                        config.set_content(content)

                red_file.release()

                self.action_in_progress = False
                self.update_ui_state()

                if error != None:
                    QMessageBox.critical(get_main_window(),
                                        'Apply Changes Error',
                                         'Error while writing {0}: {1}'.format(config.display_name, error))
                    return

                self.script_manager.execute_script('openhab_set_configs_ownership', cb_openhab_set_configs_ownership)

            red_file.write_async(content.encode('utf-8'), cb_write)

        def cb_open_error(error):
            self.action_in_progress = False
            self.update_ui_state()

            QMessageBox.critical(get_main_window(), 'Apply Changes Error',
                                 'Error while opening {0}: {1}'.format(config.display_name, error))

        async_call(REDFile(self.session).open,
                   (config.absolute_name, REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0o644, 0, 0),
                   cb_open, cb_open_error, report_exception=True)
