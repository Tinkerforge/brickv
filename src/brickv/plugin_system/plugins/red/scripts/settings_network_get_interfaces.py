#!/usr/bin/env python2

import os
import json
import netifaces

return_dict = {'wireless': None, 'wired':None}
lwireless = []
lwired = []

for intf in netifaces.interfaces():
     if os.path.isdir("/sys/class/net/"+intf+"/wireless"):
        lwireless.append(intf)
     else:
        lwired.append(intf)

if len(lwireless) > 0:
    return_dict['wireless'] = lwireless
if len(lwired) > 0:
    return_dict['wired'] = lwired

print json.dumps(return_dict)
