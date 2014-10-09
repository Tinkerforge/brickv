#!/usr/bin/env python2 

import psutil

with open("/proc/uptime", "r") as utf:
    print utf.readline().split(".")[0]

du = psutil.disk_usage("/")
print psutil.cpu_percent(2)
print psutil.used_phymem()
print psutil.TOTAL_PHYMEM
print du.used
print du.total