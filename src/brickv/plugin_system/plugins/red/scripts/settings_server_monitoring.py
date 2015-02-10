#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import netifaces
from sys import argv

TEMPLATE_NAGIOS_COMMAND = '''define command{
    command_name    {0}
    command_line    /usr/local/bin/tinkerforge_nagios_service.py \
                    -b {1} \
                    -u {2} \
                    -m range \
                    -w {3} \
                    -c {4} \
                    -w2 {5} \
                    -c2 {6}
}

'''

NAGIOS_CONTACT_COMMANDS = '''
define command{
	command_name	tinkerforge-notify-host-by-email
	command_line    /usr/bin/printf "%b" "***** Nagios *****\n\n\
                    Notification Type: $NOTIFICATIONTYPE$\n\
                    Host: $HOSTNAME$\n\
                    State: $HOSTSTATE$\n\
                    Address: $HOSTADDRESS$\n\
                    Info: $HOSTOUTPUT$\n\n\
                    Date/Time: $LONGDATETIME$\n" | \
                    /usr/bin/sendemail \
                    -f $_CONTACTTFFROMADDRESS$ \
                    -t $CONTACTEMAIL$ \
                    -u "** $NOTIFICATIONTYPE$ Host Alert: $HOSTNAME$ is $HOSTSTATE$ **" \
                    -s $_CONTACTTFSMTPSERVER$:$_CONTACTTFSMTPSERVERPORT$ \
                    -o username=$_CONTACTTFSMTPUSERNAME$ \
                    -o password=$_CONTACTTFSMTPPASSWORD$ \
                    -o tls=$_CONTACTTFSMTPTLS$
}

define command{
	command_name	tinkerforge-notify-service-by-email
	command_line    /usr/bin/printf "%b" "***** Nagios *****\n\n\
                    Notification Type: $NOTIFICATIONTYPE$\n\n\
                    Service: $SERVICEDESC$\n\
                    Host: $HOSTALIAS$\n\
                    Address: $HOSTADDRESS$\n\
                    State: $SERVICESTATE$\n\n\
                    Date/Time: $LONGDATETIME$\n\n\
                    Additional Info:\n\n$SERVICEOUTPUT$\n" | \
                    /usr/bin/sendemail \
                    -f $_CONTACTTFFROMADDRESS$ \
                    -t $CONTACTEMAIL$ \
                    -u "** $NOTIFICATIONTYPE$ Service Alert: $HOSTALIAS$/$SERVICEDESC$ is $SERVICESTATE$ **" \
                    -s $_CONTACTTFSMTPSERVER$:$_CONTACTTFSMTPSERVERPORT$ \
                    -o username=$_CONTACTTFSMTPUSERNAME$ \
                    -o password=$_CONTACTTFSMTPPASSWORD$ \
                    -o tls=$_CONTACTTFSMTPTLS$
}
'''

TEMPLATE_NAGIOS_CONTACT = '''define contact{
    _tffromaddress		            $0                
    _tfsmtpserver                   $1
    _tfsmtpserverport               $2
    _tfsmtpusername                 $3
    _tfsmtppassword                 $4
    _tfsmtptls                      $5
    host_notifications_enabled	    0
    service_notifications_enabled   1
    contact_name                    tf_nagios_contact
    alias                           Tinkerforge Nagios Contact
    service_notification_options    w,u,c,r
    host_notification_commands      tinkerforge-notify-host-by-email
    service_notification_commands   tinkerforge-notify-service-by-email
    email			                $6            
}
'''

TEMPLATE_NAGIOS_SERVICE = '''define service {
    use                     generic-service
    host_name               localhost
    service_description     $0
    check_command           $1
    check_interval          1
    notification_options    $2
    contacts	            tf_nagios_contact
}
'''

if len(argv) < 2:
    exit (1)

try:
    if os.system('/bin/systemctl restart nagios3') != 0:
        exit(1)

except Exception as e:
    exit(1)
