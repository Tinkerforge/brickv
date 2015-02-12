#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
import sys

result = {'items': [], 'sitemaps': [], 'rules': []}

try:
    for name in os.listdir('/etc/openhab/configurations/items/'):
        if name.endswith('.items'):
            result['items'].append(name)

    for name in os.listdir('/etc/openhab/configurations/sitemaps/'):
        if name.endswith('.sitemap'):
            result['sitemaps'].append(name)

    for name in os.listdir('/etc/openhab/configurations/rules/'):
        if name.endswith('.rules'):
            result['rules'].append(name)
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

sys.stdout.write(json.dumps(result, separators=(',', ':')))
exit(0)
