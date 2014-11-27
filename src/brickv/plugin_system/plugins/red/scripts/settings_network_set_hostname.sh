#!/bin/sh

if [ "$#" -lt 2 ]
then
    exit 1
else
    old=$1
    new=$2
    /bin/sed -i "s/$old/$new/g" /etc/hostname
    # Apply changes
    /usr/bin/sudo /usr/sbin/service hostname.sh
    /bin/sed -i "s/$old/$new/g" /etc/hosts
    # Apply changes
    /usr/bin/sudo /usr/sbin/service hostname.sh
fi

# Apply changes
/usr/bin/sudo /usr/sbin/service hostname.sh
