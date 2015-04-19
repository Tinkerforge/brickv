# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

generate_mobile_internet_dicts.py: Generate python dicts for mobile internet feature

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

print("Generating mobile internet dicts:")

try:
    import xmltodict
except:
    print "----> Python module xmltodict not installed."
    exit(1)

try:
    import pycountry
except:
    print "----> Python module pycountry not installed."
    exit(1)

import os
import json
import urllib

URL_XML = 'https://git.gnome.org/browse/mobile-broadband-provider-info/plain/serviceproviders.xml'
FILE_PATH_XML = './serviceproviders.xml'
FILE_PATH_PY = './_mobile_internet_dicts.py'

try:
    if os.path.isfile(FILE_PATH_XML):
        os.remove(FILE_PATH_XML)

    print '[*] Downloading provider database'

    urllib.urlretrieve(URL_XML, FILE_PATH_XML)

    if not os.path.isfile(FILE_PATH_XML):
        print "----> No XML file found."
        exit(1)

    print '[*] Processing provider dict'

    with open(FILE_PATH_XML, 'r') as fh_xml:
        dict_provider = xmltodict.parse(fh_xml)

    dict_json_provider = json.dumps(dict_provider)

    os.remove(FILE_PATH_XML)

    dict_country = {}

    dict_provider = json.loads(dict_json_provider)

    print '[*] Processing country dict'

    for dict_c in dict_provider['serviceproviders']['country']:
        code_country = dict_c['@code']
        dict_country[code_country] = pycountry.countries.get(alpha2=code_country.upper()).name

    dict_json_country = json.dumps(dict_country)

    print '[*] Writing provider and country dicts'

    with open(FILE_PATH_PY, 'w') as fh_py:
        fh_py.write('# -*- coding: utf-8 -*-\n')
        fh_py.write('# This file is generated, don\'t edit it.\n')
        fh_py.write('\n')
        fh_py.write('dict_provider = ' + dict_json_provider.replace('null', "''") + '\n')
        fh_py.write('dict_country = ' + dict_json_country.replace('null', "''") + '\n')

except Exception as e:
    print "----> Error occurred : " + str(e)
    exit(1)
