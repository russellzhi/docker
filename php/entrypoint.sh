#!/bin/sh
set -eu
mkdir -p /var/log/php
touch /var/log/php/error.log /var/log/php/fpm-error.log /var/log/php/access.log /var/log/php/slow.log
chown www-data:www-data /var/log/php /var/log/php/*.log
chmod 0755 /var/log/php
chmod 0644 /var/log/php/*.log
exec docker-php-entrypoint "$@"
