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
from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet_provider_preset_dialog import \
    Ui_REDTabSettingsMobileInternetProviderPresetDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_provider
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_country
from operator import itemgetter

class REDTabSettingsMobileInternetProviderPresetDialog(QtGui.QDialog, Ui_REDTabSettingsMobileInternetProviderPresetDialog):
    def __init__(self, parent, session, dict_provider, dict_country):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        self.dict_country = dict_country
        self.dict_provider = dict_provider
        self.number = None
        self.apn = None
        self.username = None
        self.password = None

        self.cbox_mi_presets_country.activated.connect(self.cbox_mi_presets_country_activated)
        self.cbox_mi_presets_provider.activated.connect(self.cbox_mi_presets_provider_activated)
        self.cbox_mi_presets_plan.activated.connect(self.cbox_mi_presets_plan_activated)
        self.pbutton_mi_presets_select.clicked.connect(self.pbutton_mi_presets_select_clicked)
        self.pbutton_mi_presets_close.clicked.connect(self.pbutton_mi_presets_close_clicked)

        if not dict_provider or \
           not dict_country or \
           len(dict_provider) == 0 or \
           len(dict_country) == 0:
                self.label_mi_preview_number.setText('-')
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

    def cbox_mi_presets_country_activated(self, index):
        self.populate_cbox_mi_presets_provider()

    def cbox_mi_presets_provider_activated(self, index):
         self.populate_cbox_mi_presets_plan()

    def cbox_mi_presets_plan_activated(self, index):
        self.update_preview_labels()

    def pbutton_mi_presets_select_clicked(self):
        self.accept()

    def pbutton_mi_presets_close_clicked(self):
        self.reject()

    def update_preview_labels(self):
        self.label_mi_preview_number.setText('-')
        self.label_mi_preview_apn.setText('-')
        self.label_mi_preview_username.setText('-')
        self.label_mi_preview_password.setText('-')

        self.number = None
        self.apn = None
        self.username = None
        self.password = None

        '''
        self.label_mi_preview_number.setText('')
        self.label_mi_preview_apn.setText('')
        self.label_mi_preview_username.setText('')
        self.label_mi_preview_password.setText('')
        '''

    def populate_cbox_mi_presets_plan(self):
        print '*** populate_cbox_mi_presets_plan'
        self.cbox_mi_presets_plan.clear()

        code_country = ''
        provider = ''

        try:
            code_country = self.cbox_mi_presets_country.itemData(self.cbox_mi_presets_country.currentIndex())
            provider = self.cbox_mi_presets_provider.currentText()
        except:
            return

        if not code_country or not provider:
            return

        plans = []

        for dict_c in dict_provider['country']:
            if code_country != dict_c['@code']:
                continue

            if isinstance(dict_c['provider'], list):
                for dict_p in dict_c['provider']:
                    if isinstance(dict_p['name'], list):
                        provider_current = dict_p['name'][0]
                    else:
                        provider_current = dict_p['name']

                    if provider_current != provider or 'gsm' not in dict_p:
                        continue

                    if 'apn' not in dict_p['gsm']:
                        continue

                    if isinstance(dict_p['gsm']['apn'], dict):
                        if '@value' not in dict_p['gsm']['apn']:
                            continue

                        # Setup: usage, name, number, username, password and do an entry
                        if 'usage' not in dict_p['gsm']['apn']:
                            usage =  ''
                        elif dict_p['gsm']['apn']['usage']['@type'] == 'internet':
                            usage = 'internet'
                        else:
                            continue

                        if 'name' not in dict_p['gsm']['apn']:
                            name =  'Default'
                        else:
                            name = dict_p['gsm']['apn']['name']

                        if 'number' not in dict_p['gsm']['apn']:
                            number =  ''
                        else:
                            number = dict_p['gsm']['apn']['number']

                        apn = dict_p['gsm']['apn']['@value']
                        
                        if 'username' not in dict_p['gsm']['apn']:
                            username =  'none'
                        else:
                            username = dict_p['gsm']['apn']['username']
                        
                        if 'password' not in dict_p['gsm']['apn']:
                            password =  'none'
                        else:
                            password = dict_p['gsm']['apn']['password']

                    else:
                        if 'apn' not in dict_p['gsm']:
                            continue

                        for dict_apn in dict_p['gsm']['apn']:
                            if '@value' not in dict_apn:
                                continue

                            # Setup: usage, name, number, username, password and do an entry
                            usage = ''
                            name = ''
                            number = ''
                            apn = ''
                            username = ''
                            password = ''

            else:
                if isinstance(dict_c['provider']['name'], list):
                    provider_current = dict_c['provider']['name'][0]
                else:
                    provider_current = dict_c['provider']['name']

                if provider_current != provider or 'gsm' not in dict_c['provider']:
                    continue

                if 'apn' not in dict_c['provider']['gsm']:
                    continue

                if isinstance(dict_c['provider']['gsm']['apn'], dict):
                    if '@value' not in dict_c['provider']['gsm']['apn']:
                        continue

                    # Setup: usage, name, number, username, password and do an entry
                    usage = ''
                    name = ''
                    number = ''
                    apn = ''
                    username = ''
                    password = ''

                else:
                    if 'apn' not in dict_c['provider']['gsm']:
                        continue

                    for dict_apn in dict_c['provider']['gsm']['apn']:
                        if '@value' not in dict_apn:
                            continue

                        # Setup: usage, name, number, username, password and do an entry
                        usage = ''
                        name = ''
                        number = ''
                        apn = ''
                        username = ''
                        password = ''

    def populate_cbox_mi_presets_provider(self):
        self.pbutton_mi_presets_select.setEnabled(True)
        self.cbox_mi_presets_provider.setEnabled(True)
        self.cbox_mi_presets_plan.setEnabled(True)
        self.cbox_mi_presets_provider.clear()
        code_country = self.cbox_mi_presets_country.itemData(self.cbox_mi_presets_country.currentIndex())
        list_providers = []

        for dict_c in dict_provider['country']:
            if dict_c['@code'] != code_country:
                continue

            list_providers = []

            # Some countries don't have any operators
            if 'provider' not in dict_c:
                self.pbutton_mi_presets_select.setEnabled(False)
                self.cbox_mi_presets_provider.setEnabled(False)
                self.cbox_mi_presets_plan.setEnabled(False)
                continue

            self.pbutton_mi_presets_select.setEnabled(True)
            self.cbox_mi_presets_provider.setEnabled(True)
            self.cbox_mi_presets_plan.setEnabled(True)

            if isinstance(dict_c['provider'], list):
                for dict_p in dict_c['provider']:
                    if isinstance(dict_p['name'], list):
                        list_providers.append(dict_p['name'][0])
                    else:
                        list_providers.append(dict_p['name'])
            else:
                if isinstance(dict_c['provider']['name'], list):
                    list_providers.append(dict_c['provider']['name'][0])
                else:
                    list_providers.append(dict_c['provider']['name'])

        self.cbox_mi_presets_provider.addItems(sorted(list_providers))

    def populate_cbox_mi_presets_country(self):
        self.cbox_mi_presets_country.clear()
        list_countries = []

        for dict_c in dict_provider['country']:
            dict_country_code = {'country': None, 'code': None}
            dict_country_code['country'] = dict_country[dict_c['@code']]
            dict_country_code['code'] = dict_c['@code']
            list_countries.append(dict_country_code)

        list_countries_sorted = sorted(list_countries,
                                       key = itemgetter('country'),
                                       reverse = False)

        for i, dict_c in enumerate(list_countries_sorted):
            self.cbox_mi_presets_country.addItem(dict_c['country'])
            self.cbox_mi_presets_country.setItemData(i, dict_c['code'])
