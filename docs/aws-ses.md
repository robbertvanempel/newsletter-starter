# Amazon SES and SNS setup

Use **your own AWS account, verified domain and email addresses**. Work in one commercial AWS region that supports SES; keep identity, SMTP credentials, API sending and SNS in that region. Frankfurt (`eu-central-1`) is an example, not a required account setting. Check [AWS's current endpoints](https://docs.aws.amazon.com/general/latest/gr/ses.html) for your selected region.

## 1. Account, costs and sender identity

1. Log in to the [AWS Console](https://console.aws.amazon.com/). The owner handles account signup, billing details and MFA. Use an administrative identity for setup only; never create root access keys for this application.
2. Select your region. Open **Amazon SES → Configuration → Identities → Create identity → Domain**. Enter a domain you control and enable Easy DKIM. AWS may also present a guided account setup flow; use the same verified-domain goal.
3. At your DNS provider, create the exact DKIM CNAME records shown by AWS. If the provider automatically appends your domain, avoid adding the suffix twice. Use DNS-only records where a provider offers proxying.
4. Add a custom MAIL FROM subdomain such as `bounce.YOUR_DOMAIN` if you want SPF alignment. Use the exact MX and SPF TXT values shown by SES for your region. An existing domain's SPF record must be merged correctly; do not publish two SPF records at one name. Do not replace your normal mailbox MX records.
5. Publish an appropriate `_dmarc.YOUR_DOMAIN` TXT record. If no policy exists, `v=DMARC1; p=none` can be a monitoring starting point; review your legitimate senders before tightening enforcement. Preserve an existing policy rather than weakening it. DKIM/MAIL FROM alignment must match your actual From domain.
6. Wait until SES reports the identity and DKIM as successful. DNS propagation is not proof of verification; inspect SES status. If using custom MAIL FROM, check its status too.
7. Review [SES pricing](https://aws.amazon.com/ses/pricing/) and the other services you enable. In **Billing and Cost Management → Budgets**, create a monthly cost budget chosen by the owner, with actual and forecast notifications to their own address. Complete any recipient confirmation. Verify the notifications are active. A budget alert does not stop charges or sending.

Sources: [domain verification and Easy DKIM](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html), [custom MAIL FROM](https://docs.aws.amazon.com/ses/latest/dg/mail-from.html), [DMARC](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dmarc.html), [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html).

## 2. Create restricted API and SMTP credentials

Keila uses two delivery paths:

| Used by | Credential | Enter it in |
| --- | --- | --- |
| Keila system mail, such as password reset | Region-specific SES SMTP username and SMTP password | Private `.env`, through `scripts/configure.py` |
| Native Amazon SES campaign sender | IAM access key ID and its API secret | Keila's authenticated sender settings |
| Optional draft import helper | Keila project API token | Hidden terminal prompt in `scripts/create_draft.py` |

An AWS API secret is **not** the SES SMTP password. Do not paste either into the web editor or an AI chat.

For campaigns, create a dedicated IAM user without console access, with only the sending permissions it needs. Create an access key for the external application when your deployment requires a key. Restrict the policy to the verified identity and sender, for example this template:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["ses:SendEmail", "ses:SendRawEmail"],
    "Resource": "arn:aws:ses:YOUR_REGION:YOUR_AWS_ACCOUNT_ID:identity/YOUR_DOMAIN",
    "Condition": {
      "StringEquals": {
        "ses:FromAddress": "YOUR_SENDER_EMAIL",
        "aws:RequestedRegion": "YOUR_REGION"
      }
    }
  }]
}
```

Replace every uppercase placeholder with values from the owner's account. This is a template, not a policy to paste unchanged. Leave configuration sets out of the first installation. If you later use one, review and permit its actual resource as required by the current SES API and IAM evaluation. Never attach AdministratorAccess to solve a send error.

For system mail, use **SES → SMTP settings → Create SMTP credentials**. Use a dedicated SMTP user, review the permissions created by the console and restrict SendRawEmail to your intended identity/sender where supported. Securely store the resulting regional SMTP username/password. Delete unused downloaded credential files after placing credentials in the intended private stores.

Sources: [SMTP credentials](https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html), [SMTP endpoints and TLS](https://docs.aws.amazon.com/ses/latest/dg/smtp-connect.html), [SES sending authorization examples](https://docs.aws.amazon.com/ses/latest/dg/sending-authorization-policy-examples.html), [IAM least privilege](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).

## 3. Sandbox and production access

SES starts new regional accounts in a sandbox. Check the actual account dashboard for current limits. Sandbox recipients generally must be verified, except the SES mailbox simulator. Verify your own receiving test address before trying a normal inbox test. The sandbox is regional: approval elsewhere does not enable sending here.

In **SES → Account dashboard**, request production access. Supply truthful information: your website, what readers subscribe to, how you obtain consent, example content and how you handle unsubscribe, bounces and complaints. The owner reviews any commitments and confirms the request. AWS may ask for more information or decline it.

Record the actual approval status, daily quota and per-second rate; set Keila below them. Request submission is not approval. See [AWS production-access instructions](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html) and [sending quotas](https://docs.aws.amazon.com/ses/latest/dg/manage-sending-quotas.html).

## 4. Wire bounces and complaints back to Keila

Do this after your Keila hostname has working HTTPS and before sending subscriber campaigns.

1. In the **same region**, open **Amazon SNS → Topics → Create topic → Standard**. Give it a name such as `newsletter-feedback`. Keep message encryption disabled for this basic recipe unless you deliberately configure the KMS permissions required for SES publishing.
2. Limit the topic's publish policy to the SES service and your own account/identity. Preserve SNS's owner-management statements. A publish statement follows this template:

```json
{
  "Sid": "AllowOwnSesIdentity",
  "Effect": "Allow",
  "Principal": {"Service": "ses.amazonaws.com"},
  "Action": "sns:Publish",
  "Resource": "arn:aws:sns:YOUR_REGION:YOUR_AWS_ACCOUNT_ID:newsletter-feedback",
  "Condition": {
    "StringEquals": {"AWS:SourceAccount": "YOUR_AWS_ACCOUNT_ID"},
    "ArnEquals": {"AWS:SourceArn": "arn:aws:ses:YOUR_REGION:YOUR_AWS_ACCOUNT_ID:identity/YOUR_DOMAIN"}
  }
}
```

3. The pinned **Keila 0.30.3** SES adapter verifies SNS messages with SHA-1. Use SNS topic **SignatureVersion 1**, and recheck compatibility when upgrading Keila. Do not weaken verification or expose an unsigned replacement webhook.
4. Create an **HTTPS** subscription to `https://YOUR_NEWSLETTER_HOST/api/webhooks/senders/ses`. Keep **Raw message delivery disabled**: Keila expects the signed SNS envelope. The upstream controller validates the signature and handles the subscription confirmation. Check SNS until the subscription is **Confirmed**; merely creating it is insufficient.
5. In **SES → Identities → your sending domain → Notifications**, choose this topic for **Bounce** and **Complaint** notifications. If you separately verified the exact sending address, inspect that identity's notification settings too; apply the feedback configuration to identities you actually send through. Keep email feedback forwarding on until you have verified the automated route.
6. Confirm your **native SES sender in Keila** uses that same region/identity. A plain SMTP campaign sender is not a substitute for checking this integration.
7. With owner approval, use Keila to send a test campaign to SES simulator contacts such as `bounce@simulator.amazonses.com` and `complaint@simulator.amazonses.com`. AWS supports these test addresses; they are not real subscribers. Verify actual notifications reach Keila and that the matching Keila message/contact is marked unreachable, unsubscribed or otherwise suppressed as appropriate. Sending from AWS's own console alone does not create Keila's message record and does not prove the mapping works.
8. Keep production suppression in place. Remove only dedicated simulator fixture contacts when finished, and preserve the test evidence privately.

The public webhook should reject a malformed/unsigned POST; a GET may return 404. Do not block the real SNS endpoint with Studio Basic Auth, a CAPTCHA or an interactive login.

Sources: [SES notifications with SNS](https://docs.aws.amazon.com/ses/latest/dg/configure-sns-notifications.html), [SNS access policies](https://docs.aws.amazon.com/ses/latest/dg/receiving-email-permissions.html#receiving-email-permissions-sns), [SNS signature versions](https://docs.aws.amazon.com/sns/latest/dg/sns-verify-signature-of-message.html), [SES mailbox simulator](https://docs.aws.amazon.com/ses/latest/dg/send-an-email-from-console.html), and the pinned [Keila SES adapter](https://github.com/pentacent/keila/blob/v0.30.3/lib/keila/mailings/sender_adapters/ses.ex) / [webhook controller](https://github.com/pentacent/keila/blob/v0.30.3/lib/keila_web/controllers/ses_webhook_controller.ex).
