#! /bin/sh

PART_START=$(/bin/cat /sys/block/mmcblk0/mmcblk0p1/start)

# prefer parted if available (since image version 1.4), because fdisk
# on debian jessie reports a warning and exits with an error. this makes
# it harder to automatically tell real errors apart from simple warnings

if [ -x "/sbin/parted" ]; then

/sbin/parted /dev/mmcblk0 <<EOF
resizepart 1 -1s
I
quit
EOF

else

/sbin/fdisk /dev/mmcblk0 <<EOF
d
n
p
1
$PART_START

w
EOF

fi

/bin/cp /etc/rc.local /etc/rc.local.org

/bin/echo -e "#!/bin/sh -e
/sbin/resize2fs -p /dev/mmcblk0p1
/bin/rm \$0
/bin/mv /etc/rc.local.org /etc/rc.local
exit 0" > /etc/rc.local
