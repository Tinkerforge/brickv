# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

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

from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_versions import Ui_REDTabVersions
from brickv.plugin_system.plugins.red.api import *

import json

from brickv.async_call import async_call

DEFAULT_NAME_HEADER_WIDTH = 200
DEFAULT_VERSION_HEADER_WIDTH = 100
DEFAULT_DESCRIPTION_HEADER_WIDTH = 300

NUM_TABS = 8

class REDTabVersions(QtGui.QWidget, Ui_REDTabVersions):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # set from RED after construction
        self.script_manager = None # set from RED after construction

        self.package_list = [[] for i in range(NUM_TABS)]

        self.language_packages = None
        self.language_packages_file = None

        languages = "C#/mono", "C/C++", "Delphi/Lazarus", "Java", "JavaScript", "Octave", "Perl", "PHP", "Python", "Ruby", "Shell", "VB.NET"

        self.package_list[0].append({'name': 'Brick Daemon', 'version': 'Collecting Data...', 'description': 'Daemon that manages Bricks/Bricklets'})
        self.package_list[0].append({'name': 'RED Brick API Daemon', 'version': 'Collecting Data...', 'description': 'Daemon that implements RED Brick API'})
        self.package_list[0].append({'name': 'RED Brick Image', 'version': 'Collecting Data...', 'description': 'SD card image of RED Brick'})
        for language in languages:
            self.package_list[0].append({'name': 'Bindings ' + language, 'version': 'Collecting Data...', 'description': 'Tinkerforge bindings for ' + language })

        for i in range(1, NUM_TABS):
            self.package_list[i].append({'name': 'Collecting Data...', 'version': 'Collecting Data...', 'description': 'Collecting Data...'})

        self.tables = [
            self.tree_main,
            self.tree_csharp,
            self.tree_c,
            self.tree_java,
            self.tree_perl,
            self.tree_php,
            self.tree_python,
            self.tree_ruby,
        ]
        self.update_funcs = [
            self.update_main,
            lambda: self.update_language((1, "mono")),
            lambda: self.update_language((2, "c")),
            lambda: self.update_language((3, "java")),
            lambda: self.update_language((4, "perl")),
            lambda: self.update_language((5, "php")),
            lambda: self.update_language((6, "python")),
            lambda: self.update_language((7, "ruby")),
        ]

        self.tab_data = []

        self.models = []
        for i in range(NUM_TABS):
            self.models.append(Qt.QStandardItemModel(0, 3, self))
            self.models[i].setHorizontalHeaderItem(0, Qt.QStandardItem("Package"))
            self.models[i].setHorizontalHeaderItem(1, Qt.QStandardItem("Version"))
            self.models[i].setHorizontalHeaderItem(2, Qt.QStandardItem("Description"))
            self.models[i].setItem(0, 0, Qt.QStandardItem("Collecting data..."))

            self.tables[i].setModel(self.models[i])
            self.tables[i].setColumnWidth(0, DEFAULT_NAME_HEADER_WIDTH)
            self.tables[i].setColumnWidth(1, DEFAULT_VERSION_HEADER_WIDTH)
            self.tables[i].setColumnWidth(2, DEFAULT_DESCRIPTION_HEADER_WIDTH)

            self.tab_data.append({'table': self.tables[i], 'model': self.models[i], 'list': self.package_list[i], 'update_func': self.update_funcs[i], 'updated': False})

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
            if result == None:
                return

            versions = result.stdout.split('\n')
            num_versions = len(self.package_list[0])
            if len(versions) < num_versions:
                # TODO: Error for user?
                return

            self.label_version.setText(versions[2])
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

    def update_language_packages_read(self, language, result):
        self.language_packages_file.release()

        if result.error == None:
            self.language_packages = json.loads(result.data.decode('utf-8'))
            self.update_language_table(language)

    def update_language_packages_open(self, language, result):
        self.language_packages_file.read_async(64000, lambda x: self.update_language_packages_read(language, x))

    def update_language_packages_error(self):
        # TODO: Error popup for user?
        pass

    def update_language_packages(self, language):
        self.language_packages_file = REDFile(self.session)
        async_call(self.language_packages_file.open,
                   ("/etc/tf_installed_versions", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   lambda x: self.update_language_packages_open(language, x),
                   self.update_language_packages_error)

    def update_table(self):
        tab_data = self.tab_data[self.tabs.currentIndex()]
        tab_data['model'].removeRows(0, tab_data['model'].rowCount())

        for i, p in enumerate(tab_data['list']):
            for j, item_name in enumerate(['name', 'version', 'description']):
                item = tab_data['model'].item(i, j)
                if item == None:
                    tab_data['model'].setItem(i, j, Qt.QStandardItem(p[item_name]))
                else:
                    tab_data['model'].item(i, j).setText(p[item_name])
