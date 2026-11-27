#!/bin/sh
set -e

gunicorn --chdir /app/backend --bind 127.0.0.1:5000 --workers 2 app:app --daemon
exec nginx -g "daemon off;"
