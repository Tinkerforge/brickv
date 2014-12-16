#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import psutil
import sys
import json
import zlib

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
for p in psutil.process_iter():
    process_dict = {'cmd': ' '.join(p.cmdline),
                    'name': p.name,
                    'pid': p.pid,
                    'user': p.username,
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
