#!/bin/sh

DAEMON=/usr/bin/brickd
# TODO: Change in final version
#DAEMON=/home/olaf/ee/brickd/src/brickd/brickd
OPTIONS=daemon
NAME=brickd
PIDFILE=/var/run/$NAME.pid

start-stop-daemon --verbose --pidfile $PIDFILE --stop
sleep 1
start-stop-daemon --verbose --pidfile $PIDFILE --exec $DAEMON --start --$OPTIONS
