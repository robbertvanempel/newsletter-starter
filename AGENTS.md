# Instructions for an AI installing this newsletter system

These instructions describe an installation on the requesting user's own accounts and infrastructure. Read `README.md`, `INSTALL.md`, `docs/aws-ses.md`, `docs/studio.md` and `docs/maintenance.md` before acting. They are also readable by assistants that do not automatically load AGENTS.md.

## Start with capabilities and a short intake

State whether you can browse documentation, control an authenticated browser, run a terminal, and access the target server. Do not claim to click or install anything without the corresponding tool. If only chat is available, give the user one small set of concrete actions at a time and wait for their result. Use the user's preferred language; the repository is written in English.

Ask only for missing decisions: newsletter name, domain/DNS provider, desired sender address, existing server or approved hosting budget, preferred AWS region, approximate list size and whether the contacts opted in. Inspect existing infrastructure before proposing changes. Reuse an appropriate existing server and reverse proxy when authorized; do not overwrite its routes, firewall, certificates or unrelated services. The included Compose stack binds ports 80/443 and is intended for a dedicated host or free ports. Adapt its proxy section if another proxy already owns them.

## Carry out authorized work

Use browser tools for the AWS, DNS and Keila pages when available. Navigate using the actual UI and current official documentation; labels may change. Inspect state after each meaningful action. Prefer scoped CLI/API operations for verifiable configuration when available. Show what you completed and what remains; never report a plan as a completed installation.

Prepare files and previews before asking for a decision. Routine reversible setup within the user's request does not need repeated approval. Explain and obtain authorization before buying infrastructure or enabling paid services when not already authorized. The user completes account creation, passwords, MFA, CAPTCHA, payment and contractual confirmations when required. Stop dependent work at a tool-required approval; continue unrelated preparation.

## Keep the installation private

- Use the user's own accounts and a fresh clone of this public repository. Do not seek access to its author's deployment, subscribers or credentials.
- Generate secrets on the user's machine/server. Use `scripts/configure.py` interactively in a user-controlled terminal; do not ask for secret values in chat. If the tool cannot support a private interactive prompt, have the user run it themselves.
- Store `.env` with mode 600. Keep it out of webroots, Git, screenshots and reports. Do not run `docker compose config` without `--quiet` on real configuration; it expands secrets. Do not print environment variables, authorization headers or email lists.
- The AWS API access key/secret, region-specific SES SMTP credentials and Keila API token are different credentials. Explain where each is entered. Never use root access keys or an AdministratorAccess policy for sending.
- Never put AWS or Keila API credentials in Studio, HTML exports, localStorage or frontend JavaScript. The draft helper reads a project-scoped token using a hidden terminal prompt.
- Preserve unsubscribe/suppression status on imports. Do not upload contacts until the user chooses their own source list and confirms permission. Never use sample addresses as actual recipients.

## Follow verified phases

1. Check costs, domain, architecture, server access, Docker and occupied ports.
2. Follow `docs/aws-ses.md`: verify SES identity, DKIM, optional custom MAIL FROM, DMARC, restricted API/SMTP credentials and cost notifications. Do not invent DNS records or account-specific values.
3. Generate the private configuration. Use Compose `config --quiet`, validate Caddy, then start the new stack.
4. Verify public HTTPS and separate Studio/Keila authentication. Set up a project and a native **Amazon SES** sender with the user's regional API credentials. Set a conservative rate below the user's current AWS quota.
5. Wire SNS to Keila, verify the subscription and test feedback with the SES mailbox simulator through actual Keila messages. An unconfirmed subscription is unfinished work.
6. Create a branded edition in Studio, save its editable source, export and validate a Keila draft, import once and inspect the actual Keila record. Imports create a draft only. They do not authorize a send.
7. Ask for approval of the exact test recipient and draft before sending a test. Verify actual inbox headers and rendering. Use native signup/double opt-in and unsubscribe checks with a consenting test contact. Create and test a private backup.
8. Request SES production access using truthful details supplied by the owner. Pending AWS review is a pending milestone. Never claim that application submission means approval.

## Sending and completion

Do not schedule or send a subscriber campaign unless the user explicitly approves that campaign, audience and timing. Keep sent/scheduled campaigns and their statistics intact. The provided helper only calls `POST /api/v1/campaigns`; do not add delivery calls to make installation easier.

If a create request times out, inspect Keila before retrying. The helper keeps a private receipt and blocks uncertain retries. Do not delete the receipt to suppress the warning without checking the actual campaign list.

Use the acceptance checklist in INSTALL.md. Report tested facts, remaining owner actions, AWS approval status, backup location and the user's two URLs. Leave all content as unscheduled drafts unless sending was explicitly approved. Do not claim a production-ready installation while delivery, feedback or restore checks are still outstanding.
