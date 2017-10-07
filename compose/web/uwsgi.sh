#!/bin/sh
python /app/manage.py collectstatic --noinput
uwsgi \
    --chdir=/app \
    --wsgi-file=/app/config/wsgi.py \
    --master \
    --processes=2 \
    --buffer-size=65535 \
    --http-socket=0.0.0.0:8000 \
    --socket=/tmp/uwsgi.sock \
    --vacuum \
    --lazy \
    --lazy-apps \
