#!/usr/bin/env python3
"""Create one unscheduled HTML draft through Keila's official API. Never send."""
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward a private bearer credential to another URL.

def validated_payload(payload):
    if not isinstance(payload, dict) or set(payload) != {'data'} or not isinstance(payload['data'], dict):
        raise ValueError('Expected a Studio Keila draft export.')
    data = payload['data']
    if set(data) != {'subject','preview_text','settings','html_body'} or data['settings'] != {'type':'html','do_not_track':True}:
        raise ValueError('Only an unscheduled, unassigned HTML draft is accepted.')
    if any(not isinstance(data[k],str) for k in ['subject','preview_text','html_body']) or not data['subject'].strip():
        raise ValueError('Add a subject and export again.')
    if '{{ unsubscribe_link }}' not in data['html_body']:
        raise ValueError('The Keila unsubscribe placeholder is missing.')
    return payload

def create(base, payload, token, private_dir=ROOT / '.private'):
    parsed = urllib.parse.urlsplit(base)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
        raise ValueError('Use your exact HTTPS Keila origin, without a path or credentials.')
    base = base.rstrip('/')
    body = json.dumps(validated_payload(payload),sort_keys=True,separators=(',',':')).encode()
    digest = hashlib.sha256(base.encode()+b'\0'+body).hexdigest()
    private_dir.mkdir(mode=0o700,parents=True,exist_ok=True)
    receipt = private_dir / (digest+'.json')
    try:
        descriptor = os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        previous = json.loads(receipt.read_text())
        if previous.get('id'):
            return previous['id'], True
        raise ValueError('A previous attempt has an uncertain result. Check Keila before removing this receipt and retrying.')
    with os.fdopen(descriptor,'w') as file:
        json.dump({'status':'attempted','origin':base},file)
    request = urllib.request.Request(base+'/api/v1/campaigns',data=body,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','Accept':'application/json'},method='POST')
    try:
        with urllib.request.build_opener(NoRedirect).open(request,timeout=30) as response:
            result = json.load(response)
        campaign = result['data']
        campaign_id = campaign['id']
        if not isinstance(campaign_id,str) or not re.fullmatch(r'[A-Za-z0-9_]+',campaign_id) or campaign.get('sent_at') or campaign.get('scheduled_for'):
            raise ValueError('Unexpected campaign response.')
    except Exception:
        raise RuntimeError('No confirmed result. Inspect Keila for the draft before any retry. The attempt receipt was preserved.') from None
    temp = receipt.with_suffix('.tmp')
    descriptor = os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,'w') as file:
        json.dump({'status':'created','origin':base,'id':campaign_id},file)
    os.replace(temp,receipt)
    return campaign_id,False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    parser.add_argument('--base-url',required=True)
    parser.add_argument('--check',action='store_true',help='Validate the export without connecting to Keila')
    args = parser.parse_args()
    if args.file.stat().st_size > 2_000_000:
        raise ValueError('Export is larger than 2 MB.')
    payload = validated_payload(json.loads(args.file.read_text()))
    if args.check:
        print('Valid unscheduled Keila HTML draft. No network request made.')
        return
    token = getpass.getpass('Your project-scoped Keila API token (hidden): ')
    if not token:
        raise ValueError('No API token supplied.')
    campaign_id,existing = create(args.base_url,payload,token)
    print(('Already imported: ' if existing else 'Created private, unscheduled draft: ')+campaign_id)
    print('Open Keila to review it. No message was sent or scheduled.')

if __name__ == '__main__':
    try:
        main()
    except (ValueError,RuntimeError,OSError) as error:
        raise SystemExit(str(error))
