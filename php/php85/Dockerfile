FROM php:8.5.10-fpm

COPY install-extensions.sh /usr/local/bin/project-install-extensions
RUN sh /usr/local/bin/project-install-extensions

COPY install-pecl.sh /usr/local/bin/project-install-pecl
RUN sh /usr/local/bin/project-install-pecl

COPY entrypoint.sh /usr/local/bin/project-php-entrypoint
RUN chmod +x /usr/local/bin/project-php-entrypoint
ENTRYPOINT ["project-php-entrypoint"]
CMD ["php-fpm"]
