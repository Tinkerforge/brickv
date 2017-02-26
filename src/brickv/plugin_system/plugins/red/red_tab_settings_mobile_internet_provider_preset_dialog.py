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

from operator import itemgetter

from PyQt4 import QtCore, QtGui

from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet_provider_preset_dialog import \
    Ui_REDTabSettingsMobileInternetProviderPresetDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_provider
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_country

USER_ROLE_APN      = QtCore.Qt.UserRole
USER_ROLE_USERNAME = QtCore.Qt.UserRole + 1
USER_ROLE_PASSWORD = QtCore.Qt.UserRole + 2
USER_ROLE_DIAL     = QtCore.Qt.UserRole + 3

class REDTabSettingsMobileInternetProviderPresetDialog(QtGui.QDialog, Ui_REDTabSettingsMobileInternetProviderPresetDialog):
    def __init__(self, parent, session, dict_provider, dict_country):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        self.dict_country = dict_country
        self.dict_provider = dict_provider

        self.cbox_mi_presets_country.currentIndexChanged.connect(self.cbox_mi_presets_country_current_index_changed)
        self.cbox_mi_presets_provider.currentIndexChanged.connect(self.cbox_mi_presets_provider_current_index_changed)
        self.cbox_mi_presets_plan.currentIndexChanged.connect(self.cbox_mi_presets_plan_current_index_changed)
        self.pbutton_mi_presets_select.clicked.connect(self.pbutton_mi_presets_select_clicked)
        self.pbutton_mi_presets_close.clicked.connect(self.pbutton_mi_presets_close_clicked)

        if not dict_provider or \
           not dict_country or \
           len(dict_provider) == 0 or \
           len(dict_country) == 0:
                self.label_mi_preview_dial.setText('-')
                self.label_mi_preview_apn.setText('-')
                self.label_mi_preview_username.setText('-')
                self.label_mi_preview_password.setText('-')
                self.cbox_mi_presets_country.clear()
                self.cbox_mi_presets_provider.clear()
                self.cbox_mi_presets_plan.clear()
                self.pbutton_mi_presets_select.setEnabled(False)
                self.cbox_mi_presets_country.setEnabled(False)
                self.cbox_mi_presets_provider.setEnabled(False)
                self.cbox_mi_presets_plan.setEnabled(False)
        else:
            self.populate_cbox_mi_presets_country()

    def cbox_mi_presets_country_current_index_changed(self, index):
        self.populate_cbox_mi_presets_provider()

    def cbox_mi_presets_provider_current_index_changed(self, index):
         self.populate_cbox_mi_presets_plan()

    def cbox_mi_presets_plan_current_index_changed(self, index):
        apn = self.cbox_mi_presets_plan.itemData(index, USER_ROLE_APN)
        username = self.cbox_mi_presets_plan.itemData(index, USER_ROLE_USERNAME)
        password = self.cbox_mi_presets_plan.itemData(index, USER_ROLE_PASSWORD)
        dial = self.cbox_mi_presets_plan.itemData(index, USER_ROLE_DIAL)

        if not apn:
            self.label_mi_preview_apn.setText('-')
        else:
            self.label_mi_preview_apn.setText(apn)

        if not username:
            self.label_mi_preview_username.setText('-')
        else:
            self.label_mi_preview_username.setText(username)

        if not password:
            self.label_mi_preview_password.setText('-')
        else:
            self.label_mi_preview_password.setText(password)

        if not dial:
            self.label_mi_preview_dial.setText('-')
        else:
            self.label_mi_preview_dial.setText(dial)

    def pbutton_mi_presets_select_clicked(self):
        self.accept()

    def pbutton_mi_presets_close_clicked(self):
        self.reject()

    def validate_fields(self, data):
        if 'name' not in data:
            name =  'Default'
        elif isinstance(data['name'], list):
            name = data['name'][0]
        else:
            name = data['name']

        apn = data['@value']

        if 'username' not in data:
            username =  'none'
        else:
            username = data['username']

        if 'password' not in data:
            password =  'none'
        else:
            password = data['password']

        if 'dial' not in data:
            dial =  ''
        else:
            dial = data['dial']

        return True, name, apn, username, password, dial

    def populate_cbox_mi_presets_plan(self):
        self.cbox_mi_presets_plan.clear()

        code_country = ''
        provider = ''

        try:
            current_code_country = self.cbox_mi_presets_country.itemData(self.cbox_mi_presets_country.currentIndex())
            current_provider = self.cbox_mi_presets_provider.currentText()
        except:
            return

        if not current_code_country or not current_provider:
            return

        self.cbox_mi_presets_plan.blockSignals(True)

        for dict_c in dict_provider['country']:
            if current_code_country != dict_c['@code']:
                continue

            # The country has more than one providers
            if isinstance(dict_c['provider'], list):
                for dict_p in dict_c['provider']:
                    if isinstance(dict_p['name'], list):
                        provider = dict_p['name'][0]
                    else:
                        provider = dict_p['name']

                    if provider != current_provider:
                        continue

                    # The provider has more than one plans
                    if isinstance(dict_p['gsm']['apn'], list):
                        for dict_apn in dict_p['gsm']['apn']:
                            if '@value' not in dict_apn:
                                continue

                            if dict_apn['usage']['@type'] != 'internet':
                                continue

                            result, name, apn, username, password, dial = self.validate_fields(dict_apn)

                            if result:
                                self.cbox_mi_presets_plan.addItem(name)
                                current_index = self.cbox_mi_presets_plan.count() - 1
                                self.cbox_mi_presets_plan.setItemData(current_index, apn, USER_ROLE_APN)
                                self.cbox_mi_presets_plan.setItemData(current_index, username, USER_ROLE_USERNAME)
                                self.cbox_mi_presets_plan.setItemData(current_index, password, USER_ROLE_PASSWORD)
                                self.cbox_mi_presets_plan.setItemData(current_index, dial, USER_ROLE_DIAL)
                    # The provider has only one plan
                    else:
                        if '@value' not in dict_p['gsm']['apn']:
                            continue

                        if dict_p['gsm']['apn']['usage']['@type'] != 'internet':
                            continue

                        result, name, apn, username, password, dial = self.validate_fields(dict_p['gsm']['apn'])

                        if result:
                            self.cbox_mi_presets_plan.addItem(name)
                            current_index = self.cbox_mi_presets_plan.count() - 1
                            self.cbox_mi_presets_plan.setItemData(current_index, apn, USER_ROLE_APN)
                            self.cbox_mi_presets_plan.setItemData(current_index, username, USER_ROLE_USERNAME)
                            self.cbox_mi_presets_plan.setItemData(current_index, password, USER_ROLE_PASSWORD)
                            self.cbox_mi_presets_plan.setItemData(current_index, dial, USER_ROLE_DIAL)

            # The country has only one provider
            else:
                if isinstance(dict_c['provider']['name'], list):
                    provider = dict_c['provider']['name'][0]
                else:
                    provider = dict_c['provider']['name']

                if provider != current_provider:
                    continue

                # The provider has more than one plans
                if isinstance(dict_c['provider']['gsm']['apn'], list):
                    for dict_apn in dict_c['provider']['gsm']['apn']:
                        if '@value' not in dict_apn:
                            continue

                        if dict_apn['usage']['@type'] != 'internet':
                            continue

                        result, name, apn, username, password, dial = self.validate_fields(dict_apn)

                        if result:
                            self.cbox_mi_presets_plan.addItem(name)
                            current_index = self.cbox_mi_presets_plan.count() - 1
                            self.cbox_mi_presets_plan.setItemData(current_index, apn, USER_ROLE_APN)
                            self.cbox_mi_presets_plan.setItemData(current_index, username, USER_ROLE_USERNAME)
                            self.cbox_mi_presets_plan.setItemData(current_index, password, USER_ROLE_PASSWORD)
                            self.cbox_mi_presets_plan.setItemData(current_index, dial, USER_ROLE_DIAL)
                # The provider has only one plan
                else:
                    if '@value' not in dict_c['provider']['gsm']['apn']:
                        continue

                    if dict_c['provider']['gsm']['apn']['usage']['@type'] != 'internet':
                        continue

                    result, name, apn, username, password, dial = self.validate_fields(dict_c['provider']['gsm']['apn'])

                    if result:
                        self.cbox_mi_presets_plan.addItem(name)
                        current_index = self.cbox_mi_presets_plan.count() - 1
                        self.cbox_mi_presets_plan.setItemData(current_index, apn, USER_ROLE_APN)
                        self.cbox_mi_presets_plan.setItemData(current_index, username, USER_ROLE_USERNAME)
                        self.cbox_mi_presets_plan.setItemData(current_index, password, USER_ROLE_PASSWORD)
                        self.cbox_mi_presets_plan.setItemData(current_index, dial, USER_ROLE_DIAL)

        self.cbox_mi_presets_plan.blockSignals(False)

        if self.cbox_mi_presets_plan.count() > 0:
            self.cbox_mi_presets_plan.setCurrentIndex(-1)
            self.cbox_mi_presets_plan.setCurrentIndex(0)

    def populate_cbox_mi_presets_provider(self):
        self.cbox_mi_presets_provider.clear()
        code_country = self.cbox_mi_presets_country.itemData(self.cbox_mi_presets_country.currentIndex())
        list_providers = []

        for dict_c in dict_provider['country']:
            if dict_c['@code'] != code_country:
                continue

            list_providers = []

            # Only include providers which has GSM network and at least one internet usage type

            # The country has more than one providers
            if isinstance(dict_c['provider'], list):
                for dict_p in dict_c['provider']:
                    if 'gsm' not in dict_p:
                        continue

                    if 'apn' not in dict_p['gsm']:
                        continue

                    has_internet = False

                    # The provider has more than one APNs
                    if isinstance(dict_p['gsm']['apn'], list):
                        for dict_apn in dict_p['gsm']['apn']:
                            if 'usage' not in dict_apn:
                                continue
                            elif dict_apn['usage']['@type'] == 'internet':
                                has_internet = True
                                break

                    # The provider has only one APN
                    else:
                        if 'usage' not in dict_p['gsm']['apn']:
                            has_internet = False
                        elif dict_p['gsm']['apn']['usage']['@type'] == 'internet':
                            has_internet = True

                    if not has_internet:
                        continue

                    if isinstance(dict_p['name'], list):
                        list_providers.append(dict_p['name'][0])
                    else:
                        list_providers.append(dict_p['name'])

            # The country has only one provider
            else:
                if 'gsm' not in dict_c['provider']:
                    continue

                if 'apn' not in dict_c['provider']['gsm']:
                    continue

                has_internet = False

                # The provider has more than one APNs
                if isinstance(dict_c['provider']['gsm']['apn'], list):
                    for dict_apn in dict_c['provider']['gsm']['apn']:
                        if 'usage' not in dict_apn:
                            continue
                        elif dict_apn['usage']['@type'] == 'internet':
                            has_internet = True
                            break

                # The provider has only one APN
                else:
                    if 'usage' not in dict_c['provider']['gsm']['apn']:
                        has_internet = False
                    elif dict_c['provider']['gsm']['apn']['usage']['@type'] == 'internet':
                        has_internet = True

                if not has_internet:
                    continue

                if isinstance(dict_c['provider']['name'], list):
                    list_providers.append(dict_c['provider']['name'][0])
                else:
                    list_providers.append(dict_c['provider']['name'])

        self.cbox_mi_presets_provider.blockSignals(True)
        self.cbox_mi_presets_provider.addItems(sorted(list_providers))
        self.cbox_mi_presets_provider.blockSignals(False)
        self.cbox_mi_presets_provider.setCurrentIndex(-1)
        self.cbox_mi_presets_provider.setCurrentIndex(0)

    def populate_cbox_mi_presets_country(self):
        self.cbox_mi_presets_country.clear()
        list_countries = []

        for dict_c in dict_provider['country']:
            if 'provider' not in dict_c:
                continue

            dict_country_code = {'country': None, 'code': None}
            dict_country_code['country'] = dict_country[dict_c['@code']]
            dict_country_code['code'] = dict_c['@code']
            list_countries.append(dict_country_code)

        list_countries_sorted = sorted(list_countries,
                                       key = itemgetter('country'),
                                       reverse = False)

        self.cbox_mi_presets_provider.blockSignals(True)

        for i, dict_c in enumerate(list_countries_sorted):
            self.cbox_mi_presets_country.addItem(dict_c['country'])
            self.cbox_mi_presets_country.setItemData(i, dict_c['code'])

        self.cbox_mi_presets_provider.blockSignals(False)
        self.cbox_mi_presets_country.setCurrentIndex(-1)
        self.cbox_mi_presets_country.setCurrentIndex(0)
