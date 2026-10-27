#!/usr/bin/env sh
set -eu
umask 077
cd "$(dirname "$0")/.."
backup_dir="backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$backup_dir"
chmod 700 backups "$backup_dir"
docker compose --env-file .env -f deploy/compose.yml exec -T postgres pg_dump -U keila -Fc keila > "$backup_dir/database.dump"
docker compose --env-file .env -f deploy/compose.yml exec -T postgres pg_restore --list < "$backup_dir/database.dump" > /dev/null
docker compose --env-file .env -f deploy/compose.yml exec -T keila tar -C /opt/keila/uploads -cf - . > "$backup_dir/uploads.tar"
cp .env "$backup_dir/config.env"
git rev-parse HEAD > "$backup_dir/source-revision.txt"
echo 'Consistent database dump; uploads copied separately. Avoid uploads during backup.' > "$backup_dir/COMPLETE"
echo "Private backup created: $backup_dir. Encrypt it and copy it off this server."
