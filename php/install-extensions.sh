#!/bin/sh
set -eu
export DEBIAN_FRONTEND=noninteractive
major="$(php -r 'echo PHP_MAJOR_VERSION;')"
if [ "$major" = 5 ]; then
    # Stretch is archived; retain package signature verification.
    printf '%s\n' \
      'deb [check-valid-until=no] http://archive.debian.org/debian stretch main' \
      'deb [check-valid-until=no] http://archive.debian.org/debian-security stretch/updates main' > /etc/apt/sources.list
elif [ "$major" = 7 ]; then
    sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list
    sed -i 's|https://deb.debian.org/debian-security|https://security.debian.org/debian-security|g; /debian-security/s/^deb /deb [check-valid-until=no] /' /etc/apt/sources.list
fi
apt-get -o Acquire::Retries=3 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30 update
apt-get install -y --no-install-recommends \
    libpng-dev libjpeg-dev libfreetype6-dev libwebp-dev libicu-dev \
    libzip-dev libpq-dev libxml2-dev libxslt1-dev libgmp-dev libbz2-dev \
    libldap2-dev libsasl2-dev libtidy-dev libmagickwand-dev unzip git
if [ "$major" = 5 ]; then
    apt-get install -y --no-install-recommends libmcrypt-dev
    docker-php-ext-configure gd --with-freetype-dir=/usr --with-jpeg-dir=/usr
    # PHP 5's configure expects the GMP header outside the multiarch directory.
    if [ ! -f /usr/include/gmp.h ]; then
        ln -s "/usr/include/$(dpkg-architecture -qDEB_HOST_MULTIARCH)/gmp.h" /usr/include/gmp.h
    fi
else
    docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp
fi
docker-php-ext-configure ldap --with-libdir="lib/$(dpkg-architecture -qDEB_HOST_MULTIARCH)"
extensions='bcmath bz2 calendar exif ftp gd gettext gmp intl ldap mysqli pdo_mysql pdo_pgsql pgsql pcntl shmop soap sockets sysvmsg sysvsem sysvshm tidy xsl zip'
if [ "$major" = 5 ]; then extensions="$extensions mysql mcrypt"; fi
if [ "$major" != 8 ]; then extensions="$extensions opcache"; fi
# Skip modules already compiled into the official base image.
missing=''
for extension in $extensions; do
    if ! php -r "exit(extension_loaded('$extension') ? 0 : 1);"; then
        missing="$missing $extension"
    fi
done
# Limit compiler parallelism so three simultaneous builds do not exhaust RAM.
docker-php-ext-install -j2 $missing
rm -rf /var/lib/apt/lists/*
