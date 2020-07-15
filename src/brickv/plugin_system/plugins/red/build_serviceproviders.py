#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2020 Erik Fleckstein <erik@tinkerforge.com>

build_serviceproviders.py: Generate python dicts for mobile internet feature

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

print("Generating mobile internet serviceprovider data:")

import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pprint import pformat

def main():
    try:
        XML_URL = 'file://{0}'.format(os.environ['SERVICEPROVIDERS_XML_PATH'])
    except KeyError:
        XML_URL = 'https://git.gnome.org/browse/mobile-broadband-provider-info/plain/serviceproviders.xml'
    try:
        ISO3166_URL = 'file://{0}'.format(os.environ['ISOCODES_JSON_PATH'])
    except KeyError:
        ISO3166_URL = 'https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/master/data/iso_3166-1.json'
    DATA_FILE = 'serviceprovider_data.py'

    print('[*] Downloading provider database')

    xml_data = None
    try:
        response = urllib.request.urlopen(XML_URL, timeout=10)
        xml_data = response.read()
        response.close()
    except Exception as e:
        print("----> Failed to download provider database. Will use old provider database. Error was: {}".format(str(e)))

    print('[*] Downloading ISO-3166 database')

    iso3166_data = None
    try:
        response = urllib.request.urlopen(ISO3166_URL, timeout=10)
        iso3166_data = response.read()
        response.close()
    except Exception as e:
        print("----> Failed to download ISO-3166 database. Will use old provider database. Error was: {}".format(str(e)))

    if xml_data is None or iso3166_data is None:
        return

    try:
        print('[*] Processing provider dict')

        def expand(element):
            result = {}

            for item in element.items():
                result['@' + item[0]] = item[1]

            for child in list(element):
                if child.tag in result:
                    if type(result[child.tag]) != list:
                        result[child.tag] = [result[child.tag]]

                    result[child.tag].append(expand(child))
                else:
                    result[child.tag] = expand(child)

            text = element.text

            if text != None:
                text = text.strip()

                if len(text) == 0:
                    text = None

            if len(result) == 0:
                return text

            if text != None:
                result['#text'] = text

            return result

        root_provider = ET.fromstring(xml_data)
        dict_provider = expand(root_provider)

        print('[*] Processing country dict')

        iso3166 = json.loads(iso3166_data.decode('utf-8'))
        dict_country_all = {}
        dict_country = {}

        for entry_country in iso3166['3166-1']:
            dict_country_all[entry_country.get('alpha_2')] = entry_country.get('name')

        for dict_c in dict_provider['country']:
            code_country = dict_c['@code']
            dict_country[code_country] = dict_country_all[code_country.upper()]

    except Exception as e:
        print('----> Failed to process provider or country dict: ' + str(e))
        exit(1)

    try:
        print('[*] Writing provider and country dicts')

        with open(DATA_FILE + '.tmp', 'w') as f:
            f.write('# -*- coding: utf-8 -*-\n')
            f.write('# This file is generated, don\'t edit it.\n')
            f.write('\n')
            f.write('# The provider data comes from the GNOME mobile-broadband-provider-info package\n')
            f.write('# that is released as public domain:\n')
            f.write('#\n')
            f.write('# https://git.gnome.org/browse/mobile-broadband-provider-info/plain/serviceproviders.xml\n')
            f.write('\n')
            f.write('dict_provider = \\\n')
            f.write(pformat(dict_provider) + '\n')
            f.write('\n')
            f.write('# The country data comes from the Debian iso-codes package that is released\n')
            f.write('# under LGPLv2.1+:\n')
            f.write('#\n')
            f.write('# /usr/share/xml/iso-codes/iso_3166.xml\n')
            f.write('\n')
            f.write('dict_country = \\\n')
            f.write(pformat(dict_country) + '\n')

        os.replace(DATA_FILE + '.tmp', DATA_FILE)
    except Exception as e:
        print('----> Failed to write provider and country dict: ' + str(e))
        exit(1)


if __name__ == '__main__':
    main()
