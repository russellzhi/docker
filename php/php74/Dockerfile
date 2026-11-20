FROM php:7.4.33-fpm

COPY install-extensions.sh /usr/local/bin/project-install-extensions
# Pin the retired security repository to an official snapshot with matching packages.
RUN sed -i 's|https://security.debian.org/debian-security|https://snapshot.debian.org/archive/debian-security/20260831T000000Z|g' /usr/local/bin/project-install-extensions \
    && sh /usr/local/bin/project-install-extensions

COPY install-pecl.sh /usr/local/bin/project-install-pecl
RUN sh /usr/local/bin/project-install-pecl

COPY entrypoint.sh /usr/local/bin/project-php-entrypoint
RUN chmod +x /usr/local/bin/project-php-entrypoint
ENTRYPOINT ["project-php-entrypoint"]
CMD ["php-fpm"]
