#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import psutil
import sys
import json
import zlib
import os

if psutil.version_info >= (2, 1, 0): # image version >= 1.4 (jessie)
    def get_cmdline(p):
        return p.cmdline()
    def get_name(p):
        return p.name()
    def get_username(p):
        return p.username()
else: # image version < 1.4 (wheezy)
    def get_cmdline(p):
        return p.cmdline
    def get_name(p):
        return p.name
    def get_username(p):
        return p.username

result = {}

with open("/proc/uptime", "r") as utf:
    result['uptime'] = utf.readline().split(".")[0]

du = psutil.disk_usage("/")

all_process_info = []

for p in psutil.process_iter(): # update CPU usage info
    p.get_cpu_percent(interval=0)

if len(sys.argv) < 2:
    result['cpu_used'] = psutil.cpu_percent(1)
else:
    result['cpu_used'] = psutil.cpu_percent(float(sys.argv[1]))

all_process_info = []
own_pid = os.getpid()
for p in psutil.process_iter():
    if p.pid == own_pid:
        continue

    process_dict = {'cmd': ' '.join(get_cmdline(p)),
                    'name': get_name(p),
                    'pid': p.pid,
                    'user': get_username(p),
                    'cpu': int(p.get_cpu_percent(interval=0) * 10),
                    'mem': int(p.get_memory_percent() * 10)}
    all_process_info.append(process_dict)

result['processes'] = all_process_info

result['mem_used'] = psutil.used_phymem() - psutil.phymem_buffers() - psutil.cached_phymem()
result['mem_total'] = psutil.TOTAL_PHYMEM
result['disk_used'] = du.used
result['disk_total'] = du.total

interfaces = psutil.network_io_counters(pernic=True)
if 'tunl0' in interfaces: # ignore tunl0 interface
    del interfaces['tunl0']

result['ifaces'] = interfaces

sys.stdout.write(zlib.compress(json.dumps(result, separators=(',', ':'))))
