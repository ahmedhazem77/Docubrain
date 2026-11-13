# syntax=docker/dockerfile:1

FROM node:20-alpine AS frontend

WORKDIR /app

COPY package.json package-lock.json vite.config.js ./
COPY resources ./resources

ARG VITE_RAG_API_URL=http://localhost:8000
ENV VITE_RAG_API_URL=$VITE_RAG_API_URL

RUN npm ci && npm run build

FROM composer:2 AS vendor

WORKDIR /app

COPY composer.json composer.lock ./
RUN composer install --no-dev --optimize-autoloader --no-interaction --no-scripts --prefer-dist

COPY . .
RUN composer dump-autoload --optimize --no-interaction

FROM php:8.2-fpm-alpine AS php_base

RUN apk add --no-cache \
    postgresql-dev \
    icu-dev \
    libzip-dev \
    libxml2-dev \
    oniguruma-dev \
    && docker-php-ext-install \
        pdo_pgsql \
        mbstring \
        xml \
        bcmath \
        opcache \
        zip

WORKDIR /var/www/html

COPY --from=vendor /app /var/www/html
COPY --from=frontend /app/public/build /var/www/html/public/build

RUN mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs storage/app/public bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache

COPY docker/api/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

FROM php_base AS api

EXPOSE 9000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

FROM nginx:1.27-alpine AS web

COPY docker/web/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=php_base /var/www/html/public /var/www/html/public

EXPOSE 80
