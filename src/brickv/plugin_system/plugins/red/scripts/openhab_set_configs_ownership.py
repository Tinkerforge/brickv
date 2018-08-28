#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import pwd
import grp
from distutils.version import StrictVersion

IMAGE_VERSION = None
MIN_VERSION_WITH_OPENHAB2 = StrictVersion('1.10')

with open('/etc/tf_image_version', 'r') as f:
    IMAGE_VERSION = StrictVersion(f.read().split(' ')[0].strip())

try:
    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/services/'):
            if name.endswith('.cfg'):
                os.chown(os.path.join('/etc/openhab2/services/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

        for name in os.listdir('/var/lib/openhab2/etc/'):
            if name.endswith('.cfg'):
                os.chown(os.path.join('/var/lib/openhab2/etc/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/'):
            if name.endswith('.cfg'):
                os.chown(os.path.join('/etc/openhab/configurations/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

        for name in os.listdir('/etc/openhab/'):
            if name.endswith('.xml'):
                os.chown(os.path.join('/etc/openhab/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/items/'):
            if name.endswith('.items'):
                os.chown(os.path.join('/etc/openhab2/items/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/items/'):
            if name.endswith('.items'):
                os.chown(os.path.join('/etc/openhab/configurations/items/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/sitemaps/'):
            if name.endswith('.sitemap'):
                os.chown(os.path.join('/etc/openhab2/sitemaps/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/sitemaps/'):
            if name.endswith('.sitemap'):
                os.chown(os.path.join('/etc/openhab/configurations/sitemaps/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/rules/'):
            if name.endswith('.rules'):
                os.chown(os.path.join('/etc/openhab2/rules/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/rules/'):
            if name.endswith('.rules'):
                os.chown(os.path.join('/etc/openhab/configurations/rules/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/persistence/'):
            if name.endswith('.persist'):
                os.chown(os.path.join('/etc/openhab2/persistence/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/persistence/'):
            if name.endswith('.persist'):
                os.chown(os.path.join('/etc/openhab/configurations/persistence/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/scripts/'):
            if name.endswith('.script'):
                os.chown(os.path.join('/etc/openhab2/scripts/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/scripts/'):
            if name.endswith('.script'):
                os.chown(os.path.join('/etc/openhab/configurations/scripts/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        for name in os.listdir('/etc/openhab2/transform/'):
            if name.endswith('.transform'):
                os.chown(os.path.join('/etc/openhab2/transform/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)
    else:
        for name in os.listdir('/etc/openhab/configurations/transform/'):
            if name.endswith('.transform'):
                os.chown(os.path.join('/etc/openhab/configurations/transform/', name),
                         pwd.getpwnam('openhab').pw_uid,
                         grp.getgrnam('openhab').gr_gid)

except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

exit(0)
