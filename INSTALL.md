# Install your own newsletter system

Run all commands from a fresh clone of this repository on **your own server**, unless a step says otherwise. Replace example domains and addresses with yours. Never copy an existing private newsletter installation.

## 1. Prepare your domain and server

1. Choose two hostnames, for example `newsletter.example.com` for Keila and `studio.example.com` for Studio. Use a verified sending address on your domain.
2. Create DNS A records for both hostnames pointing to your server. Add AAAA records only if IPv6 works on that server. Remove stale AAAA records that point elsewhere. If using a DNS proxy/CDN, use DNS-only while obtaining the initial certificates unless your provider's setup is verified.
3. Use a maintained Linux distribution. Install Docker Engine and the Compose plugin using [Docker's official installation instructions](https://docs.docker.com/engine/install/). Check `docker version`, `docker compose version` and `uname -m`. Never run an unreviewed install script supplied by an arbitrary website.
4. Inspect listeners with `sudo ss -ltnp`. The included Caddy service needs public TCP 80/443; UDP 443 is optional for HTTP/3. Allow your SSH access before changing firewall rules. PostgreSQL and Keila have no published host ports. If you already have a reverse proxy, adapt the Compose proxy/network configuration to it instead of competing for 80/443.
5. Review server, domain and AWS costs with the owner. SES is the AWS requirement; you may host Keila on an existing server or any suitable VPS. Amazon EC2 is optional.

```sh
git clone https://github.com/robbertvanempel/newsletter-starter.git
cd newsletter-starter
```

Before starting containers, inspect the pinned manifests for your architecture, for example `docker buildx imagetools inspect pentacent/keila:0.30.3`. The baseline was exercised on Linux x86-64. On another architecture, verify all three images rather than assuming that a digest supports it.

## 2. Set up Amazon SES

Follow [docs/aws-ses.md](docs/aws-ses.md). Complete domain verification and create **regional SES SMTP credentials** for system emails. Keep the separate **SES API access key and secret** available privately for Keila's campaign sender. Verify the administrator's receiving address too if your account is still in the SES sandbox.

SES sandbox test delivery can work before production access is approved. Do not promise subscriber delivery until the region's account status and quotas allow it.

## 3. Create your private configuration

Run this in a private, interactive terminal controlled by you. The helper asks for your hostnames and addresses, hidden passwords and your SES SMTP credentials. It generates independent database, signing and ID secrets locally. It invokes the pinned Caddy image to hash the Studio password and creates a mode-600 `.env` without displaying the credentials.

```sh
python3 scripts/configure.py
docker compose --env-file .env -f deploy/compose.yml config --quiet
```

The Studio username is `editor`; the password is the one you chose. Keila uses your administrator email and a different password. Keep both in your password manager. `.env.example` documents names only; do not start the real stack with its placeholders. The helper refuses to overwrite an existing `.env`.

The `.env` belongs in the repository root; the static webroot is **only `studio/`**. Never serve the repository root. Do not paste the output of an expanded Compose configuration into chat.

## 4. Validate and start the services

```sh
docker compose --env-file .env -f deploy/compose.yml pull
docker compose --env-file .env -f deploy/compose.yml run --rm --no-deps proxy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose --env-file .env -f deploy/compose.yml up -d
docker compose --env-file .env -f deploy/compose.yml ps
```

Keila's startup script runs its database migrations. Give the first startup time to finish. Caddy obtains certificates automatically when DNS points correctly and ports 80/443 are reachable.

Open your two URLs:

- `https://newsletter.YOUR-DOMAIN` should show the Keila login. Log in with your own administrator credentials. A fresh instance bootstraps the root account from `KEILA_USER` and `KEILA_PASSWORD`; these variables are not a general password-reset mechanism after initial setup.
- `https://studio.YOUR-DOMAIN` should request the Studio login before showing the editor. Use `editor` and your chosen Studio password.

Check that an unauthenticated request to Studio gets HTTP 401 and that Keila's contact/project pages require login. Public signup forms, unsubscribe routes, uploaded email images and the SES webhook must remain reachable as designed; do not place blanket Basic Auth in front of Keila.

## 5. Configure Keila

1. Create a project with your own newsletter name. Keep this project separate from unrelated lists.
2. Open **Senders**, create a sender with your verified address, and choose the native **Amazon SES** integration. Enter your selected region and restricted **API access key + API secret**. These are not the SMTP password. Leave the configuration-set field empty unless you deliberately created and permitted one.
3. Choose a conservative sender rate, initially at most one message per second and always within your actual SES quota. Verify or confirm the sender if Keila asks.
4. Follow the [SNS feedback setup](docs/aws-ses.md#4-wire-bounces-and-complaints-back-to-keila). Do this before sending to subscribers.
5. Create a native Keila signup form. Choose double opt-in where appropriate, add your own privacy notice and configure its confirmation email/sender. Copy the form URL or embed code to your website; use Keila's generated URL, not a guessed endpoint. Test it with a consenting address. Configure a supported CAPTCHA if your public form needs abuse protection.
6. Import an existing list only if it is your own permission-based list. Export and preserve unsubscribe, hard-bounce and complaint suppressions from the old provider. Do not reimport suppressed contacts as active. Start with a small consenting sample and verify field/status mappings before the full import.
7. Create a project-scoped API key in the project's API settings if you want to use the draft helper. Do not put it in the web editor. Revoke it when no longer needed.

For branding, sender identity and content requirements, use your own organisation details, consent records and privacy policy. Check the rules applicable to your activity and audience; this starter is not a legal compliance certification.

## 6. Write and import the first edition

Use [docs/studio.md](docs/studio.md). Studio supplies a working generic email layout; no page needs to be generated from scratch. Change the branding and footer, replace the example story, save editable source, then export a Keila draft.

Validate the export without contacting Keila:

```sh
python3 scripts/create_draft.py /path/to/newsletter.keila.json --base-url https://newsletter.YOUR-DOMAIN --check
```

Import it from a computer with the file, Python and network access to Keila:

```sh
python3 scripts/create_draft.py /path/to/newsletter.keila.json --base-url https://newsletter.YOUR-DOMAIN
```

Enter your Keila project API key at the hidden prompt. The helper creates an **unscheduled HTML draft without sender or audience assignment**. It never calls a send endpoint. Open the campaign in Keila and inspect its subject, preheader, HTML and unsubscribe rendering. Assign the intended sender and audience there when ready.

Use Keila's native editor for subsequent changes to that imported campaign. Studio source and Keila are separate: a changed export intentionally creates another draft; importing an identical file from the same clone returns the existing receipt. A different machine has a different receipt store, so check Keila before reimporting there.

Ask the owner to approve the exact test draft and recipient. Send a preview/test through Keila; check real inbox delivery and SPF/DKIM/DMARC headers. This approval is separate from approving a full subscriber campaign.

## 7. Acceptance checklist

Record a verified result or an explicit pending item for each:

- [ ] Both own hostnames resolve to the intended server and have valid HTTPS.
- [ ] Studio requires its login; Keila requires its own authenticated session for private pages.
- [ ] Database has no public host port; `.env` and backups cannot be fetched over HTTP.
- [ ] Studio loads, edits, reorders, previews and exports correctly; editable source reopens with the same content.
- [ ] Imported Keila record is an unscheduled HTML draft; repeat import does not create another record from this clone.
- [ ] SES identity and Easy DKIM show verified/successful status in the selected region.
- [ ] The owner-approved test is actually received; email headers show expected SPF, DKIM and DMARC alignment.
- [ ] Signup and confirmation work for a consenting test contact; unsubscribe prevents that contact from receiving another campaign.
- [ ] SNS subscription is confirmed; simulator feedback from a Keila message changes the test contact's delivery/suppression state.
- [ ] A private backup was created, copied off-server in encrypted form, and restored into an isolated test database.
- [ ] Actual SES production-access status and sending quota are recorded. Pending review means subscriber sending is still pending.
- [ ] Cost notifications reach the owner's chosen address; the owner understands they do not cap spending.

Finish by giving the owner the two URLs, where to keep private configuration and backups, how to create an edition, and which checks remain pending. Do not send or schedule a subscriber campaign as part of finishing the installation unless the owner separately approves it.

## Official references

- [Keila installation](https://www.keila.io/docs/installation/), [configuration](https://www.keila.io/docs/configuration/), [senders](https://www.keila.io/docs/senders/) and [campaign API](https://www.keila.io/docs/api/campaigns/).
- [Docker Engine installation](https://docs.docker.com/engine/install/) and [Compose](https://docs.docker.com/compose/).
- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https) and [basic_auth](https://caddyserver.com/docs/caddyfile/directives/basic_auth).
