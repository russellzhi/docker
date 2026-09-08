#!/bin/sh
set -eu
mkdir -p /var/log/mysql
touch /var/log/mysql/error.log /var/log/mysql/slow.log
chown mysql:mysql /var/log/mysql /var/log/mysql/error.log /var/log/mysql/slow.log
chmod 0644 /var/log/mysql/error.log /var/log/mysql/slow.log
chmod 0755 /var/log/mysql
exec docker-entrypoint.sh "$@"
