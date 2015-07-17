#!/bin/sh -e

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

t=$(tempfile)

/bin/echo -e "#!/bin/sh
### BEGIN INIT INFO
# Provides:          brickv-expand-filesystem
# Required-Start:    \$remote_fs \$syslog
# Required-Stop:     \$remote_fs \$syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# X-Start-Before:    redapid brickd
# Short-Description: brickv-expand-filesystem
# Description:       Finishes filesystem expansion before RED Brick API Daemon starts
### END INIT INFO

. /lib/lsb/init-functions

case \"\$1\" in
  start)
	log_daemon_msg \"Finishes filesystem expansion\" \"brickv-expand-filesystem\"

	/sbin/resize2fs -p /dev/mmcblk0p1

	if [ -x /bin/systemctl ]; then
		systemctl disable brickv-expand-filesystem
	else
		update-rc.d -f brickv-expand-filesystem remove
	fi

	rm -f /etc/init.d/brickv-expand-filesystem

	if [ -x /bin/systemctl ]; then
		systemctl daemon-reload
	fi

	log_end_msg 0
	;;
  stop)
	;;
  restart|force-reload)
	;;
  status)
	;;
  *)
	echo \"Usage: /etc/init.d/brickv-expand-filesystem {{start|stop|restart|force-reload|status}}\" >&2
	exit 1
	;;
esac

exit 0
" > $t

chmod 0755 $t
mv $t /etc/init.d/brickv-expand-filesystem

if [ -x /bin/systemctl ]; then
	systemctl daemon-reload
	systemctl enable brickv-expand-filesystem
else
	update-rc.d brickv-expand-filesystem defaults
fi
