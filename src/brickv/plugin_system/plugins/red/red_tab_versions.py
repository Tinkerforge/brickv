# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_versions.py: RED versions tab implementation

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

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_versions import Ui_REDTabVersions
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import check_script_result
from brickv.async_call import async_call

DEFAULT_NAME_HEADER_WIDTH = 200
DEFAULT_VERSION_HEADER_WIDTH = 100
DEFAULT_DESCRIPTION_HEADER_WIDTH = 300

NUM_TABS = 12

class REDTabVersions(REDTab, Ui_REDTabVersions):
    def __init__(self):
        REDTab.__init__(self)

        self.setupUi(self)

        self.package_list = [[] for i in range(NUM_TABS)]

        self.language_packages = None

        languages = 'C/C++', 'C#/Mono', 'Delphi/Lazarus', 'Java', 'JavaScript', 'Octave', 'Perl', 'PHP', 'Python', 'Ruby', 'Shell', 'VB.NET'

        self.package_list[0].append({'name': 'Brick Daemon', 'version': 'Collecting Data...', 'description': 'Daemon that manages Bricks/Bricklets'})
        self.package_list[0].append({'name': 'RED Brick API Daemon', 'version': 'Collecting Data...', 'description': 'Daemon that implements RED Brick API'})
        self.package_list[0].append({'name': 'RED Brick Image', 'version': 'Collecting Data...', 'description': 'SD card image of RED Brick'})
        for language in languages:
            self.package_list[0].append({'name': 'Bindings ' + language, 'version': 'Collecting Data...', 'description': 'Tinkerforge bindings for ' + language})

        for i in range(1, NUM_TABS):
            self.package_list[i].append({'name': 'Collecting Data...', 'version': 'Collecting Data...', 'description': 'Collecting Data...'})

        self.tables = [
            self.tree_main,
            self.tree_c,
            self.tree_csharp,
            self.tree_delphi,
            self.tree_java,
            self.tree_javascript,
            self.tree_matlab,
            self.tree_perl,
            self.tree_php,
            self.tree_python,
            self.tree_ruby,
            self.tree_shell
        ]
        self.update_funcs = [
            self.update_main,
            lambda: self.update_language((1, "c")),
            lambda: self.update_language((2, "mono")),
            lambda: self.update_language((3, "delphi")),
            lambda: self.update_language((4, "java")),
            lambda: self.update_language((5, "node")),
            lambda: self.update_language((6, "matlab")),
            lambda: self.update_language((7, "perl")),
            lambda: self.update_language((8, "php")),
            lambda: self.update_language((9, "python")),
            lambda: self.update_language((10, "ruby")),
            lambda: self.update_language((11, "shell"))
        ]

        self.tab_data = []

        self.models = []
        for i in range(NUM_TABS):
            self.models.append(QStandardItemModel(0, 3, self))
            self.models[i].setHorizontalHeaderItem(0, QStandardItem("Package"))
            self.models[i].setHorizontalHeaderItem(1, QStandardItem("Version"))
            self.models[i].setHorizontalHeaderItem(2, QStandardItem("Description"))
            self.models[i].setItem(0, 0, QStandardItem("Collecting data..."))

            self.tables[i].setModel(self.models[i])
            self.tables[i].setColumnWidth(0, DEFAULT_NAME_HEADER_WIDTH)
            self.tables[i].setColumnWidth(1, DEFAULT_VERSION_HEADER_WIDTH)
            self.tables[i].setColumnWidth(2, DEFAULT_DESCRIPTION_HEADER_WIDTH)

            self.tab_data.append({'table':       self.tables[i],
                                  'model':       self.models[i],
                                  'list':        self.package_list[i],
                                  'update_func': self.update_funcs[i],
                                  'updated':     False})

        self.tabs.currentChanged.connect(self.version_tab_changed)

    def tab_on_focus(self):
        self.update_table()
        self.version_tab_changed(self.tabs.currentIndex())

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def version_tab_changed(self, index):
        if not self.tab_data[index]['updated']:
            self.tab_data[index]['update_func']()

    def update_main(self):
        def cb_update_main(result):
            okay, _ = check_script_result(result)
            if not okay:
                return

            versions = result.stdout.split('\n')
            num_versions = len(self.package_list[0])

            if len(versions) < num_versions:
                # TODO: Error for user?
                return

            for i in range(num_versions):
                self.package_list[0][i]['version'] = versions[i]

            self.tab_data[0]['updated'] = True
            self.update_table()

        self.script_manager.execute_script('versions_main', cb_update_main)

    def update_language_table(self, language):
        index = language[0]
        packages = self.language_packages[language[1]]

        self.tab_data[index]['list'] = []

        for package in packages['packages']:
            self.tab_data[index]['list'].append({'name': package[0], 'version': package[1], 'description': package[2]})

        self.update_table()

    def update_language(self, language):
        if self.language_packages == None:
            self.update_language_packages(language)
        else:
            self.update_language_table(language)

    def update_language_packages(self, language):
        def cb_open(red_file):
            def cb_read(result):
                red_file.release()

                if result.error == None:
                    self.language_packages = json.loads(result.data.decode('utf-8'))

                    self.update_language_table(language)

            red_file.read_async(64000, cb_read)

        def cb_open_error(error):
            # TODO: Error popup for user?
            pass

        async_call(REDFile(self.session).open,
                   ("/etc/tf_installed_versions", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open, cb_open_error, pass_exception_to_error_callback=True)

    def update_table(self):
        tab_data = self.tab_data[self.tabs.currentIndex()]
        tab_data['model'].removeRows(0, tab_data['model'].rowCount())

        for i, p in enumerate(tab_data['list']):
            for j, item_name in enumerate(['name', 'version', 'description']):
                item = tab_data['model'].item(i, j)
                if item == None:
                    tab_data['model'].setItem(i, j, QStandardItem(p[item_name]))
                else:
                    tab_data['model'].item(i, j).setText(p[item_name])
