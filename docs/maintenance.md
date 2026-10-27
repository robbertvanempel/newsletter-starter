# Backups, restore, upgrades and troubleshooting

## Back up privately

From the repository root on your server:

```sh
sh scripts/backup.sh
```

The helper makes a consistent PostgreSQL custom-format dump, validates its table of contents, copies uploaded media and saves private configuration plus the Git revision in a mode-restricted folder under `backups/`. Avoid media uploads during the copy; for a single maintenance-point snapshot stop Keila briefly while taking the backup and start it again afterward. The script does not stop it automatically.

The backup contains personal data and passwords. Encrypt it before copying to independent storage. Save your editable Studio `.source.json` files separately: browser localStorage is not in the server backup. A `COMPLETE` marker means the script finished, not that a restore has been tested. Schedule backups using your own chosen scheduler and verify it after a reboot. This starter does not silently install a cron job or delete old backups.

## Test a restore without sending email

Use a separate temporary database that no Keila app or worker can connect to. Do not point the running production application at it. Example, from the server repository root:

```sh
# Choose one existing complete backup and a fresh unique test database name.
docker compose --env-file .env -f deploy/compose.yml exec -T postgres createdb -U keila keila_restore_check
docker compose --env-file .env -f deploy/compose.yml exec -T postgres pg_restore -U keila --exit-on-error --no-owner -d keila_restore_check < backups/YOUR_BACKUP/database.dump
docker compose --env-file .env -f deploy/compose.yml exec -T postgres psql -U keila -d keila_restore_check -c 'SELECT count(*) FROM information_schema.tables WHERE table_schema = '\''public'\'';'
```

Inspect table existence and private row counts without dumping subscriber emails. Validate the media archive with `tar -tf backups/YOUR_BACKUP/uploads.tar` and verify expected media files. When the test is finished, delete only the temporary restore database with `dropdb -U keila keila_restore_check` via the same Compose `exec`. Do not run this command against `keila`.

For a real recovery, first preserve any newer data and take the site out of sending service. Stop **only Keila**, restore into a separately created database, verify rows and uploaded media, then carefully switch configuration to the verified restored database. Reuse the original `SECRET_KEY_BASE` and `HASHID_SALT`; do not regenerate them during a normal recovery. On a new server also restore uploads into the Keila upload volume with the correct ownership. Review any queued or scheduled campaigns before starting workers: restoring an old database can otherwise reintroduce pending sends. Keep the old database until the owner accepts recovery. Never use `docker compose down -v` as a troubleshooting step; it deletes persistent volumes.

## Upgrades

The Compose file pins the baseline images. Check [Keila releases](https://github.com/pentacent/keila/releases), PostgreSQL and Caddy notices before installation and periodically afterward. Back up, inspect release notes and test a proposed image/digest in isolation before changing the production pin. Do not automatically jump PostgreSQL major versions or run unattended `latest` updates. Never start an older application against a database migrated by a newer incompatible version.

For a tested application-only update, pull the chosen version and replace only that service with `docker compose --env-file .env -f deploy/compose.yml up -d --no-deps keila`. Repeat the relevant login, draft, signup, delivery and webhook checks. Preserve the private `.env`, uploads and database. A new clone does not contain your live state.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| HTTPS certificate is not issued | DNS A/AAAA, public TCP 80/443, firewall and occupied ports. Avoid publishing stale IPv6 addresses. |
| Keila cannot connect to PostgreSQL | Compose `ps`, database health and consistency of the original database password. Changing POSTGRES_PASSWORD in `.env` does not change an existing database role automatically. |
| Studio login is rejected | Username `editor`, chosen Studio password and correctly quoted bcrypt hash in `.env`. Do not expose the hash or use a cleartext password as Caddy's hash. |
| System mail fails | Correct regional SMTP endpoint, SMTP username/password, STARTTLS, verified sender and sandbox recipient. A raw API secret is not an SMTP password. |
| Campaign send fails | Native SES sender API credentials, region, restricted policy/identity and quotas. Leave configuration set empty unless you intentionally enabled it. |
| Draft import is rejected | Project-scoped token, exact HTTPS origin, Studio's Keila JSON export and API compatibility with the pinned version. Do not expose the API error payload or token in a public issue. |
| Draft import reports uncertainty | Inspect Keila before retrying. Keep the private receipt until you know whether the campaign exists. |
| SNS remains pending or returns 403 | Public webhook path, topic access policy, SignatureVersion 1 for the pinned Keila version, raw delivery disabled and actual subscription confirmation. |
| Simulator callback returns 404 | Send the simulator message through Keila's native SES sender so Keila has the matching provider receipt. |
| Browser has no edition | Different profile/hostname or cleared storage. Reopen your saved `.source.json`. Keila campaigns remain in Keila. |
| Images missing in email | Public HTTPS asset URL, no authentication/expiring signatures, correct MIME type, and the receiving client's image settings. |

Use `docker compose --env-file .env -f deploy/compose.yml ps` for a summary. Inspect only relevant logs privately; mail logs can contain recipient addresses. Never share an expanded Compose configuration, `.env`, database dump, API token or screenshot containing account secrets in a GitHub issue.
