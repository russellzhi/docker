#!/bin/sh
set -eu
major="$(php -r 'echo PHP_MAJOR_VERSION;')"
if [ "$major" = 5 ]; then
    packages='redis-4.3.0 apcu-4.0.11 imagick-3.8.1'
else
    packages='redis-6.3.0 apcu-5.1.28 imagick-3.8.1'
fi
for package in $packages; do
    curl -fSL --retry 3 "https://pecl.php.net/get/$package.tgz" -o /tmp/extension.tgz
    mkdir -p /tmp/extension-build
    tar -xzf /tmp/extension.tgz -C /tmp/extension-build --strip-components=1
    (cd /tmp/extension-build && phpize && ./configure && make -j2 && make install)
    docker-php-ext-enable "${package%%-*}"
    rm -rf /tmp/extension-build /tmp/extension.tgz
done
