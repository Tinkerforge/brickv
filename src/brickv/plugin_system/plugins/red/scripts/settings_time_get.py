#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import time
import os

def time_utc_offset(t):
    if time.localtime(t).tm_isdst and time.daylight:
        return -time.altzone

    return -time.timezone

def convert_from_posix(tz):
    tz = tz.replace('Etc/', '')
    #.startswith('GMT') breaks the GMT timezone (without offset)
    if tz.startswith('GMT+') or tz.startswith('GMT-'):
        gmt_offset = -int(tz.replace('GMT', '')) # Convert from POSIX offset
        tz = 'UTC' + ('+' if gmt_offset > 0 else '') + str(gmt_offset)
    return tz

def timezone():
    try:
        from tzlocal import get_localzone
        return get_localzone().zone
    except:
        pass

    try:
        if not os.path.islink('/etc/localtime'):
            return 'not set'

        tz = os.readlink('/etc/localtime')
        return convert_from_posix(tz.replace('/usr/share/zoneinfo/', ''))
    except:
        pass

    return 'could not be queried'

def localtime_as_iso8601():
    utc_offset_sec = -(time.altzone if time.localtime().tm_isdst else time.timezone)
    utc_offset_hours = (utc_offset_sec // 3600)
    utc_offset_minutes = (utc_offset_sec % 3600 // 60)
    return "{}{}{:02}:{:02}".format(datetime.datetime.now().replace(microsecond=0).isoformat(),
                                    '+' if utc_offset_sec > 0 else '',
                                    utc_offset_hours,
                                    utc_offset_minutes)

t = time.time()

print(int(t))
print(localtime_as_iso8601())
print(timezone())
