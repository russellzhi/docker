FROM php:8.6.0-fpm

COPY install-extensions.sh /usr/local/bin/project-install-extensions
RUN sh /usr/local/bin/project-install-extensions

COPY install-pecl.sh /usr/local/bin/project-install-pecl
# Pin upstream commits with PHP 8.6 compatibility fixes.
RUN PHPREDIS_SOURCE=https://codeload.github.com/phpredis/phpredis/tar.gz/a6ce1e60b3e81ce3b25174aa5aaefd5590dc64fd \
    APCU_SOURCE=https://codeload.github.com/krakjoe/apcu/tar.gz/fb2c942552a3f5dab7f4dea4afb5cf0831222c57 \
    IMAGICK_SOURCE=https://codeload.github.com/Imagick/imagick/tar.gz/55ed2e9fda264395636a2e27e51f31673f5566ab \
    sh /usr/local/bin/project-install-pecl

# PHP 8.6's base image does not include mbstring.
RUN apt-get -o Acquire::Retries=3 update \
    && apt-get install -y --no-install-recommends libonig-dev \
    && docker-php-ext-install -j2 mbstring \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/project-php-entrypoint
RUN chmod +x /usr/local/bin/project-php-entrypoint
ENTRYPOINT ["project-php-entrypoint"]
CMD ["php-fpm"]
