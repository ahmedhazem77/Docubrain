#!/bin/sh
set -e

cd /var/www/html

if [ -z "$APP_KEY" ] || [ "$APP_KEY" = "base64:" ]; then
    php artisan key:generate --force --no-interaction
fi

echo "Waiting for PostgreSQL..."
until php -r "
    try {
        new PDO(
            'pgsql:host=' . getenv('DB_HOST') . ';port=' . getenv('DB_PORT') . ';dbname=' . getenv('DB_DATABASE'),
            getenv('DB_USERNAME'),
            getenv('DB_PASSWORD')
        );
        exit(0);
    } catch (Throwable \$e) {
        exit(1);
    }
"; do
    sleep 2
done

php artisan migrate --force --no-interaction

php artisan queue:work --sleep=3 --tries=3 --timeout=300 &
QUEUE_PID=$!

trap 'kill $QUEUE_PID 2>/dev/null || true' EXIT TERM INT

exec docker-php-entrypoint php-fpm
