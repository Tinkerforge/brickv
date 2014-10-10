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
    process_dict = {'command':p.name, 'pid':p.pid, 'user':p.username,\
    'cpu':"%.1f" % p.get_cpu_percent(interval=0),\
    'memory':"%.1f" % p.get_memory_percent()}
    all_process_info.append(process_dict)

print psutil.used_phymem()
print psutil.TOTAL_PHYMEM
print du.used
print du.total
print json.dumps(psutil.network_io_counters(pernic=True))
print json.dumps(all_process_info )
