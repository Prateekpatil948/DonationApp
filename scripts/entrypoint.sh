#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/wait_for_db.sh"

python manage.py migrate --noinput
python manage.py bootstrap_superuser
python manage.py collectstatic --noinput --clear

exec "$@"
