#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time

def time_utc_offset():
    if time.localtime(time.time()).tm_isdst and time.daylight:
        return -time.altzone/(60*60)
    
    return -time.timezone/(60*60)

print(int(time.time()))
print(time_utc_offset())
