#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_HOST:=localhost}"
: "${DATABASE_PORT:=5432}"

echo "Waiting for database at ${DATABASE_HOST}:${DATABASE_PORT}..."
until python -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect(('${DATABASE_HOST}', ${DATABASE_PORT}))
except OSError:
    sys.exit(1)
"; do
    sleep 1
done
echo "Database is available."
