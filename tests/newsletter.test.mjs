import test from 'node:test';
import assert from 'node:assert/strict';
import {sample,render,campaign,validate,safeUrl} from '../studio/newsletter.mjs';
test('email export retains the native unsubscribe placeholder and inline layout',()=>{
  const html=render(sample);assert.match(html,/\{\{ unsubscribe_link \}\}/);assert.match(html,/<table role="presentation"/);assert.doesNotMatch(html,/<script|<iframe|<link/);
});
test('user text cannot inject HTML or Liquid directives',()=>{
  const doc=structuredClone(sample);doc.subject='<script>alert(1)</script> {{ contact.email }}';
  const html=render(doc);assert.doesNotMatch(html,/<script|\{\{ contact\.email/);assert.match(html,/&lt;script&gt;/);
});
test('links and images reject active schemes and embedded credentials',()=>{
  for(const url of ['javascript:alert(1)','data:text/html,bad','https://a:b@example.com','http://example.com']) assert.equal(safeUrl(url),'');
  const doc=structuredClone(sample);doc.sections[0].image='javascript:alert(1)';assert.throws(()=>validate(doc));
});
test('Keila export can create only an unassigned draft',()=>{
  const payload=campaign(sample);assert.deepEqual(payload.data.settings,{type:'html',do_not_track:true});assert.deepEqual(Object.keys(payload.data).sort(),['html_body','preview_text','settings','subject']);
});
test('malformed and oversized imported source is rejected',()=>{
  assert.throws(()=>validate({version:2,sections:[]}));const doc=structuredClone(sample);doc.sections=Array(41).fill(doc.sections[0]);assert.throws(()=>validate(doc));
});
