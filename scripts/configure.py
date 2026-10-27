#!/usr/bin/env python3
"""Create private configuration on the owner's machine without printing secrets."""
import getpass
import os
from pathlib import Path
import re
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def ask(label, default=''):
    return input(f'{label}' + (f' [{default}]' if default else '') + ': ').strip() or default

def quote(value):
    if '\n' in value or '\r' in value or '\x00' in value:
        raise ValueError('Configuration values must be one line.')
    return "'" + value.replace("'", "\\'") + "'"

def main():
    target = ROOT / '.env'
    if target.exists():
        raise SystemExit('.env already exists. Edit it privately; this tool will not overwrite it.')
    newsletter = ask('Keila hostname, without https://')
    studio = ask('Studio hostname, without https://')
    for host in [newsletter, studio]:
        if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?', host) or '.' not in host or host.endswith('.example.com'):
            raise SystemExit('Enter real hostnames you control, not example.com placeholders.')
    if newsletter == studio:
        raise SystemExit('Use two different hostnames.')
    admin = ask('Your Keila administrator email')
    sender = ask('Your verified SES sender email')
    if not all('@' in address and not address.endswith('@example.com') for address in [admin,sender]):
        raise SystemExit('Enter your own email addresses.')
    region = ask('AWS SES region', 'eu-central-1')
    if not re.fullmatch(r'[a-z]{2}-[a-z]+-\d', region):
        raise SystemExit('Use a commercial AWS region such as eu-central-1.')
    admin_password = getpass.getpass('Choose your Keila password (at least 16 characters): ')
    studio_password = getpass.getpass('Choose a different Studio password (at least 16 characters): ')
    if min(len(admin_password),len(studio_password)) < 16 or admin_password == studio_password:
        raise SystemExit('Use different passwords of at least 16 characters.')
    smtp_user = ask('Regional SES SMTP username (not an AWS root credential)')
    smtp_password = getpass.getpass('Regional SES SMTP password: ')
    if not smtp_user or not smtp_password:
        raise SystemExit('Create SES SMTP credentials before configuring the stack.')
    # Password goes to Caddy through stdin, not command-line arguments or output.
    result = subprocess.run(['docker','run','--rm','-i','caddy:2.11.7@sha256:eb4d35b7452d1ab6171fbdbe8d9275b2301dad6dad92115d91e19fb9b24d510f','caddy','hash-password'], input=studio_password+'\n', text=True, capture_output=True, check=True)
    hashed = result.stdout.strip()
    if not hashed.startswith('$2'):
        raise SystemExit('Caddy did not return a password hash. No configuration was written.')
    values = {'NEWSLETTER_HOST':newsletter,'STUDIO_HOST':studio,'KEILA_USER':admin,'KEILA_PASSWORD':admin_password,'POSTGRES_PASSWORD':secrets.token_hex(32),'SECRET_KEY_BASE':secrets.token_hex(64),'HASHID_SALT':secrets.token_hex(32),'AWS_REGION':region,'MAILER_SMTP_FROM_EMAIL':sender,'MAILER_SMTP_USER':smtp_user,'MAILER_SMTP_PASSWORD':smtp_password,'STUDIO_USER':'editor','STUDIO_PASSWORD_HASH':hashed}
    content = '# PRIVATE. Never publish or paste this file into a chat.\n' + '\n'.join(f'{key}={quote(value)}' for key,value in values.items())+'\n'
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as file:
        file.write(content)
    print('Private .env created with mode 600. Keep both chosen passwords in your password manager.')

if __name__ == '__main__':
    main()
