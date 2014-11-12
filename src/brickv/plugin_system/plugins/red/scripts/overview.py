#!/usr/bin/env python2

import psutil
import sys
import json

with open("/proc/uptime", "r") as utf:
    print utf.readline().split(".")[0]

du = psutil.disk_usage("/")

all_process_info = []

for p in psutil.process_iter():
    p.get_cpu_percent(interval=0)
if len(sys.argv) < 2:
    print psutil.cpu_percent(1)
else:
    print psutil.cpu_percent(float(sys.argv[1]))

all_process_info = []
for p in psutil.process_iter():
    process_dict = {'cmd': p.name, 'pid': p.pid, 'usr': p.username,
                    'cpu': int(p.get_cpu_percent(interval=0) * 10),
                    'mem': int(p.get_memory_percent() * 10)}
    all_process_info.append(process_dict)

print psutil.used_phymem()
print psutil.TOTAL_PHYMEM
print du.used
print du.total

interfaces = psutil.network_io_counters(pernic=True)
#remove lo and tunl0 interfaces from list
#if 'lo' in interfaces:
#    del interfaces['lo']
if 'tunl0' in interfaces:
    del interfaces['tunl0']
print json.dumps(interfaces, separators=(',', ':'))

print json.dumps(all_process_info, separators=(',', ':'))
