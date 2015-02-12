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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QPlainTextEdit, QFont, QTextOption, QLabel

from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.ui_red_tab_settings_openhab import Ui_REDTabSettingsOpenHAB
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import check_script_result

class ConfigFile(object):
    def __init__(self, display_name, source_name, tab, deletable=True):
        self.display_name   = display_name # is unique
        self.source_name    = source_name # is also unique
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
        self.refresh_in_progress = False
        self.configs             = [
            ConfigFile('openhab.cfg', '/etc/openhab/configurations/openhab.cfg', self, deletable=False),
            ConfigFile('logback.xml', '/etc/openhab/configurations/logback.xml', self, deletable=False)
        ]

        self.recreate_widgets()

        self.combo_config.currentIndexChanged.connect(self.update_ui_state)
        self.button_refresh.clicked.connect(self.refresh_configs)
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
            self.refresh_configs()

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def update_ui_state(self):
        index  = self.combo_config.currentIndex()
        config = self.configs[index]

        self.stacked_container.setCurrentIndex(index)

        self.label_progress.setVisible(self.refresh_in_progress)
        self.progress.setVisible(self.refresh_in_progress)

        self.button_refresh.setEnabled(not self.refresh_in_progress)
        self.button_new.setEnabled(not self.refresh_in_progress)
        self.button_delete.setEnabled(not self.refresh_in_progress and config.deletable)
        self.button_discard.setEnabled(not self.refresh_in_progress and config.modified)
        self.button_apply.setEnabled(not self.refresh_in_progress and config.modified)

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
        self.edit_errors.appendHtml(u'<b>{0}</b>'.format(Qt.escape(message)))

    def refresh_config(self, index):
        if index >= len(self.configs):
            self.refresh_in_progress = False
            self.update_ui_state()
            return

        config = self.configs[index]

        if config == None:
            self.refresh_config(index + 1)
            return

        self.refresh_in_progress = True
        self.update_ui_state()

        self.label_progress.setText('Downloading ' + config.source_name)

        def cb_open(red_file):
            def cb_read(result):
                red_file.release()

                self.refresh_in_progress = False
                self.update_ui_state()

                if result.error != None:
                    if result.error.error_code != REDError.E_OPERATION_ABORTED and \
                       result.error.error_code != REDError.E_DOES_NOT_EXIST:
                        self.log_error(u'Error while reading {0}: {1}'.format(config.display_name, error))
                    else:
                        config.set_content('')
                else:
                    try:
                        content = result.data.decode('utf-8')
                    except UnicodeDecodeError:
                        # FIXME: maybe add a encoding guesser here or try some common encodings if UTF-8 fails
                        self.log_error(u'Error: Config file {0} is not UTF-8 encoded'.format(config.display_name))
                    else:
                        config.set_content(content)

                self.refresh_config(index + 1)

            red_file.read_async(red_file.length, cb_read)

        def cb_open_error(error):
            if isinstance(error, REDError) and \
               error.error_code != REDError.E_OPERATION_ABORTED and \
               error.error_code != REDError.E_DOES_NOT_EXIST:
                self.log_error(u'Error while opening {0}: {1}'.format(config.display_name, error))
            else:
                config.set_content('')

            self.refresh_config(index + 1)

        async_call(REDFile(self.session).open,
                   (config.source_name, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open, cb_open_error, report_exception=True)

    def refresh_configs(self):
        self.edit_errors.hide()
        self.edit_errors.setPlainText('')

        def cb_openhab_configs_list(result):
            okay, message = check_script_result(result, decode_stderr=True)

            def fatal_error(text):
                self.log_error(text)
                self.refresh_in_progress = False
                self.update_ui_state()

            if not okay:
                fatal_error(u'Error while collecting config files: {0}'.format(message))
                return

            try:
                config_names = json.loads(result.stdout)
            except Exception as e:
                fatal_error(u'Received invalid config file collection: {0}'.format(e))
                return

            if not isinstance(config_names, dict):
                fatal_error(u'Received invalid config file collection: Not a dictionary')
                return

            try:
                configs_by_basename = {}

                for name in config_names['items']:
                    configs_by_basename.setdefault(name[:-len('.items')], []).append((name, posixpath.join('/etc/openhab/configurations/items', name)))

                for name in config_names['sitemaps']:
                    configs_by_basename.setdefault(name[:-len('.sitemap')], []).append((name, posixpath.join('/etc/openhab/configurations/sitemaps', name)))

                for name in config_names['rules']:
                    configs_by_basename.setdefault(name[:-len('.rules')], []).append((name, posixpath.join('/etc/openhab/configurations/rules', name)))
            except Exception as e:
                fatal_error(u'Received invalid config file collection: {0}'.format(e))
                return

            old_configs = {}

            for config in self.configs:
                if config != None:
                    old_configs[config.display_name] = config

            self.configs = [old_configs['openhab.cfg'], old_configs['logback.xml']]

            for value in configs_by_basename.values():
                if len(value) > 0:
                    self.configs.append(None)

                    for display_name, source_name in sorted(value):
                        if display_name in old_configs:
                            self.configs.append(old_configs[display_name])
                        else:
                            self.configs.append(ConfigFile(display_name, source_name, self))

            self.recreate_widgets()
            self.refresh_config(0)

        self.label_progress.setText('Collecting config files')
        self.refresh_in_progress = True
        self.update_ui_state()

        self.script_manager.execute_script('openhab_configs_list', cb_openhab_configs_list, max_length=1024*1024)

    def new_config(self):
        pass

    def delete_config(self):
        pass

    def discard_changes(self):
        self.configs[self.combo_config.currentIndex()].discard_changes()

    def apply_changes(self):
        pass
