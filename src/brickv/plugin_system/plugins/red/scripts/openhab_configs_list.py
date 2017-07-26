#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
from distutils.version import StrictVersion

IMAGE_VERSION = None
MIN_VERSION_WITH_OPENHAB2 = StrictVersion('1.10')

with open('/etc/tf_image_version', 'r') as f:
    IMAGE_VERSION = StrictVersion(f.read().split(' ')[0].strip())

result = {'items': [], 'sitemaps': [], 'rules': [], 'persistence': [], 'scripts': [], 'transform': []}

try:
    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/items/'):
            if name.endswith('.items'):
                result['items'].append(name)
    else:
        for name in os.listdir('/etc/openhab/configurations/items/'):
            if name.endswith('.items'):
                result['items'].append(name)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/sitemaps/'):
            if name.endswith('.sitemap'):
                result['sitemaps'].append(name)
    else:
        for name in os.listdir('/etc/openhab/configurations/sitemaps/'):
            if name.endswith('.sitemap'):
                result['sitemaps'].append(name)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/rules/'):
            if name.endswith('.rules'):
                result['rules'].append(name)
    else:
        for name in os.listdir('/etc/openhab/configurations/rules/'):
            if name.endswith('.rules'):
                result['rules'].append(name)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/persistence/'):
            if name.endswith('.persist'):
                result['persistence'].append(name)
    else:
        for name in os.listdir('/etc/openhab/configurations/persistence/'):
            if name.endswith('.persist'):
                result['persistence'].append(name)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/scripts/'):
            if name.endswith('.script'):
                result['scripts'].append(name)
    else:
        for name in os.listdir('/etc/openhab/configurations/scripts/'):
            if name.endswith('.script'):
                result['scripts'].append(name)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/transform/'):
            if name.endswith('.transform'):
                result['transform'].append(name)
    else:
        for name in os.listdir('/etc/openhab/configurations/transform/'):
            if name.endswith('.transform'):
                result['transform'].append(name)

except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

sys.stdout.write(json.dumps(result, separators=(',', ':')))
exit(0)
