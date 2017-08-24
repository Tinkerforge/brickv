#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from sys import argv
from reconfigure.configs import HostsConfig

CMD_DHCLIENT = '/sbin/dhclient &> /dev/null'
FILE_PATH_HOSTS = '/etc/hosts'
BIN_HOSTNAMECTL = '/usr/bin/hostnamectl'
CMD_HOSTNAMECTL = BIN_HOSTNAMECTL + ' --static set-hostname '

if len(argv) < 3:
    exit(1)

if not os.path.isfile(FILE_PATH_HOSTS) or not os.path.isfile(BIN_HOSTNAMECTL):
    exit(1)

hostname_old = unicode(argv[1])
hostname_new = unicode(argv[2])

if hostname_old == hostname_new:
    exit(0)

CMD_HOSTNAMECTL = CMD_HOSTNAMECTL + hostname_new

try:
    config_hosts = HostsConfig(path=FILE_PATH_HOSTS)
    config_hosts.load()

    for host_entry in config_hosts.tree.hosts:
        for alias in host_entry.aliases:
            if alias.name != hostname_old:
                continue

            alias.name = hostname_new

        if host_entry.name != hostname_old:
            continue

        host_entry.name = hostname_new

    config_hosts.save()

    if os.system(CMD_HOSTNAMECTL) != 0:
        exit(1)

    try:
        os.system(CMD_DHCLIENT)
    except:
        pass
except:
    exit(1)
