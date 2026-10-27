# Starter verification

Baseline checked on 27 October 2026.

- Five JavaScript tests cover the email layout/unsubscribe placeholder, HTML and Liquid escaping, URL restrictions, imported-source validation and unscheduled campaign payload.
- Four Python tests cover draft-only validation, HTTPS origin restrictions, duplicate import prevention and uncertain-response handling.
- Browser checks covered editing, adding and reordering stories, mobile preview, browser persistence after reload and exporting a Keila draft.
- A disposable Linux x86-64 Compose installation started the pinned upstream Keila and PostgreSQL images. The real Keila API accepted the exported payload and created an unscheduled HTML draft with matching subject and HTML.
- Private configuration generation and Caddy password hashing passed; Compose and Caddy configuration validation passed.
- The backup script produced a database dump and media archive; the dump restored successfully into an isolated database with 30 public tables.
- GitHub Actions passed the source tests and example Compose validation.

These checks used generic fixtures and an isolated database. No private subscriber list, author's AWS credentials or production newsletter settings were used. They do not establish SES production access or real inbox delivery for a reader's account. Each installation must complete the acceptance checklist in INSTALL.md, including its own approved inbox, signup, unsubscribe and feedback checks.
