#! /bin/sh

PART_START=$(/bin/cat /sys/block/mmcblk0/mmcblk0p1/start)

/sbin/fdisk /dev/mmcblk0 <<EOF
d
n
p
1
$PART_START

w
EOF

/bin/cp /etc/rc.local /etc/rc.local.org

/bin/echo -e "#!/bin/sh -e
/sbin/resize2fs -p /dev/mmcblk0p1
/bin/rm \$0
/bin/mv /etc/rc.local.org /etc/rc.local
exit 0" > /etc/rc.local
