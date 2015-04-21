# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_mobile_internet_provider_preset_dialog.py: RED settings mobile internet provider preset dialog implementation

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

from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet_provider_preset_dialog import Ui_REDTabSettingsMobileInternetProviderPresetDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window

INDEX_NETWORK_GSM   = 0
INDEX_NETWORK_CDMA  = 1
INDEX_PLAN_POSTPAID = 0
INDEX_PLAN_PREPAID  = 1

class REDTabSettingsMobileInternetProviderPresetDialog(QtGui.QDialog, Ui_REDTabSettingsMobileInternetProviderPresetDialog):
    def __init__(self, parent, session, dict_provider, dict_country):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        self.dict_country = dict_country
        self.dict_provider = dict_provider

        self.pbutton_mi_presets_select.clicked.connect(self.pbutton_mi_presets_select_clicked)
        self.pbutton_mi_presets_close.clicked.connect(self.pbutton_mi_presets_close_clicked)
        self.cbox_mi_presets_country.currentIndexChanged.connect(self.cbox_mi_presets_country_current_index_changed)
        self.cbox_mi_presets_provider.currentIndexChanged.connect(self.cbox_mi_presets_provider_index_changed)
        self.cbox_mi_presets_network_type.currentIndexChanged.connect(self.cbox_mi_presets_network_type_index_changed)

        self.populate_cbox_mi_presets_country()

    def cbox_mi_presets_network_type_index_changed(self):
        pass

    def cbox_mi_presets_provider_index_changed(self):
        pass

    def cbox_mi_presets_country_current_index_changed(self, current_index):
        code_country = self.cbox_mi_presets_country.itemData(self.cbox_mi_presets_country.currentIndex())
        self.cbox_mi_presets_provider.clear()

        for i, dict_c in enumerate(self.dict_provider['country']):
            if 'provider' not in dict_c:
                continue

            if code_country != dict_c['@code']:
                continue

            if isinstance(dict_c['provider'], dict):
                self.cbox_mi_presets_provider.addItem(dict_c['provider']['name'])
                self.cbox_mi_presets_provider.setItemData(i, code_country)
                continue

            for dict_p in dict_c['provider']:
                if isinstance(dict_p['name'], list):
                    self.cbox_mi_presets_provider.addItem(dict_p['name'][0])
                    self.cbox_mi_presets_provider.setItemData(i, code_country)
                    continue

                self.cbox_mi_presets_provider.addItem(dict_p['name'])
                self.cbox_mi_presets_provider.setItemData(i, code_country)

            self.cbox_mi_presets_provider.setCurrentIndex(-1)
            self.cbox_mi_presets_provider.setCurrentIndex(0)

    def populate_cbox_mi_presets_country(self):
        self.cbox_mi_presets_country.clear()
        dict_c = {}

        for key in self.dict_country:
            dict_c[self.dict_country[key]] = key

        for i, key in enumerate(sorted(dict_c)):
            self.cbox_mi_presets_country.addItem(key)
            self.cbox_mi_presets_country.setItemData(i, dict_c[key])

        self.cbox_mi_presets_country.setCurrentIndex(-1)
        self.cbox_mi_presets_country.setCurrentIndex(0)

    def pbutton_mi_presets_select_clicked(self):
        self.accept()

    def pbutton_mi_presets_close_clicked(self):
        self.reject()
