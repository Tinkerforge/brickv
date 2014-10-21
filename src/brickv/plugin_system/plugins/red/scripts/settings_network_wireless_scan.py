#!/usr/bin/env python2

import sys
import subprocess

if len(sys.argv) < 2:
    cmd = '''wicd-cli --wireless -Sl | tail -n+2 | pawk -s -B "d={};dd={}" -E "print json.dumps(d)" "dd['bssid']=f[1];\
dd['channel']=f[2];dd['essid']=f[3];d[f[0]]=dd"'''
elif len(sys.argv) >= 2:
    cmd = '''wicd-cli --wireless -l | tail -n+2 | pawk -s -B "d={};dd={}" -E "print json.dumps(d)" "dd['bssid']=f[1];\
dd['channel']=f[2];dd['essid']=f[3];d[f[0]]=dd"'''

ps_wireless_scan = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
print ps_wireless_scan.communicate()[0]
