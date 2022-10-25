#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
import tarfile
import tempfile

init_script = """#!/bin/sh
### BEGIN INIT INFO
# Provides:          redapid-program-import
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# X-Start-Before:    redapid
# Short-Description: redapid-program-import
# Description:       Finishes RED Brick program import before RED Brick API Daemon starts
### END INIT INFO

. /lib/lsb/init-functions

case "$1" in
  start)
	log_daemon_msg "Finishing RED Brick program import" "redapid-program-import"

	{0}

	if [ -x /bin/systemctl ]; then
		systemctl disable redapid-program-import
	else
		update-rc.d -f redapid-program-import remove
	fi

	rm -f /etc/init.d/redapid-program-import

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
	echo "Usage: /etc/init.d/redapid-program-import {{start|stop|restart|force-reload|status}}" >&2
	exit 1
	;;
esac

exit 0
"""

if len(sys.argv) < 3:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(2)

archive = os.path.join(sys.argv[1], 'archive.tfrba')
programs = sys.argv[2:]

try:
    with tarfile.open(archive, 'r:gz') as a:
        try:
            v = a.extractfile('tfrba-version')
        except Exception as e:
            raise Exception(u'Could not extract tfrba-version: {0}'.format(e))

        version = v.read()
        v.close()

        if version != '1':
            raise Exception(u'Unknown tfrba-version {0}'.format(version))

        prefixes = []

        for program in programs:
            if len(program) > 0:
                prefixes.append('programs/' + program + '/')

        members = []

        for member in a.getmembers():
            for prefix in prefixes:
                if member.name.startswith(prefix):
                    members.append(member)
                    break

        directory = tempfile.mkdtemp(prefix='extracted-tfrba-import-', dir='/home/tf')

        def is_within_directory(directory, target):
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)

            prefix = os.path.commonprefix([abs_directory, abs_target])

            return prefix == abs_directory

        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")

            tar.extractall(path, members, numeric_owner=numeric_owner)

        safe_extract(a, path=directory, members=members)

    def fixup(path):
        os.chown(path, 1000, 1000)
        os.chmod(path, 0o755)

    if not os.path.exists('/home/tf/programs'):
        os.mkdir('/home/tf/programs')
        fixup('/home/tf/programs')

    fixup(directory)
    fixup(os.path.join(directory, 'programs'))

    for program in programs:
        if len(program) > 0:
            fixup(os.path.join(directory, 'programs', program))

    commands = []

    for program in programs:
        if len(program) > 0:
            commands.append('rm -rf /home/tf/programs/{0}'.format(program))
            commands.append('mv {0} /home/tf/programs/{1}'.format(os.path.join(directory, 'programs', program), program))

    commands.append('rm -rf {0}'.format(directory))

    with open('/etc/init.d/redapid-program-import', 'wb') as f:
        f.write(init_script.format('\n\t'.join(commands)))

    os.chmod('/etc/init.d/redapid-program-import', 0o755)

    if os.path.isfile('/bin/systemctl'):
        if os.system('/bin/systemctl daemon-reload') != 0:
            exit(3)

        if os.system('/bin/systemctl enable redapid-program-import') != 0:
            exit(4)
    else:
        if os.system('/usr/sbin/update-rc.d redapid-program-import defaults') != 0:
            exit(5)
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(6)

exit(0)
