FROM php:5.6.40-fpm

# The base image predates newer signatures on the Stretch archive metadata.
RUN set -eux; for key in archive-key-10 archive-key-10-security archive-key-11; do \
      curl -fSL --retry 3 "https://ftp-master.debian.org/keys/$key.asc" \
        -o "/etc/apt/trusted.gpg.d/$key.asc"; \
    done

COPY install-extensions.sh /usr/local/bin/project-install-extensions
RUN sh /usr/local/bin/project-install-extensions

COPY install-pecl.sh /usr/local/bin/project-install-pecl
RUN sh /usr/local/bin/project-install-pecl

COPY entrypoint.sh /usr/local/bin/project-php-entrypoint
RUN chmod +x /usr/local/bin/project-php-entrypoint
ENTRYPOINT ["project-php-entrypoint"]
CMD ["php-fpm"]
