import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('draft',Path(__file__).parents[1]/'scripts/create_draft.py')
draft=importlib.util.module_from_spec(spec)
spec.loader.exec_module(draft)
PAYLOAD={'data':{'subject':'A test','preview_text':'Preview','settings':{'type':'html','do_not_track':True},'html_body':'<p>{{ unsubscribe_link }}</p>'}}

class DraftTests(unittest.TestCase):
    def test_no_delivery_or_schedule_fields(self):
        payload=json.loads(json.dumps(PAYLOAD));payload['data']['scheduled_for']='tomorrow'
        with self.assertRaises(ValueError):draft.validated_payload(payload)
    def test_refuses_insecure_origin_before_request(self):
        with self.assertRaises(ValueError):draft.create('http://example.com',PAYLOAD,'fake')
    def test_confirmed_repeat_does_not_create_another_campaign(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return b'{"data":{"id":"nmc_fixture","scheduled_for":null,"sent_at":null}}'
        with tempfile.TemporaryDirectory() as directory,patch.object(draft.urllib.request,'build_opener') as opener:
            opener.return_value.open.return_value=Response()
            self.assertEqual(draft.create('https://newsletter.example.com',PAYLOAD,'fake',Path(directory)),('nmc_fixture',False))
            self.assertEqual(draft.create('https://newsletter.example.com',PAYLOAD,'fake',Path(directory)),('nmc_fixture',True))
            self.assertEqual(opener.return_value.open.call_count,1)
            request=opener.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url,'https://newsletter.example.com/api/v1/campaigns')
    def test_uncertain_creation_blocks_automatic_retry(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(draft.urllib.request,'build_opener') as opener:
            opener.return_value.open.side_effect=TimeoutError()
            with self.assertRaises(RuntimeError):draft.create('https://newsletter.example.com',PAYLOAD,'fake',Path(directory))
            with self.assertRaises(ValueError):draft.create('https://newsletter.example.com',PAYLOAD,'fake',Path(directory))
            self.assertEqual(opener.return_value.open.call_count,1)

if __name__=='__main__':unittest.main()
