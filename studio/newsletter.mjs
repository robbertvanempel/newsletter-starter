export const sample = {
  version: 1, brand: 'Your newsletter', subject: 'Something worth sharing',
  preheader: 'A fresh idea, a useful link, and a small next step.',
  intro: 'Hello! Here is this week’s selection. Replace this introduction with your own words.',
  accent: '#306b59', footer: 'Your organisation · Your postal address',
  sections: [{title: 'Your first story', body: 'Explain why this matters to your readers. Keep it useful and make it your own.', url: 'https://example.com/article', linkText: 'Read the story', image: '', alt: ''}]
};
export function escape(value) {
  return String(value ?? '').replace(/[&<>"'{}]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','{':'&#123;','}':'&#125;'}[c]));
}
export function safeUrl(value) {
  if (!value) return '';
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && !url.username && !url.password ? url.href : '';
  } catch { return ''; }
}
export function validate(input) {
  if (!input || input.version !== 1 || !Array.isArray(input.sections) || input.sections.length > 40) throw new Error('Choose a version 1 newsletter source file with at most 40 stories.');
  const doc = {};
  for (const key of ['brand','subject','preheader','intro','accent','footer']) {
    if (typeof input[key] !== 'string' || input[key].length > 20000) throw new Error(`Invalid ${key}.`);
    doc[key] = input[key];
  }
  if (!/^#[0-9a-f]{6}$/i.test(doc.accent)) throw new Error('Choose a six-digit colour.');
  doc.version = 1;
  doc.sections = input.sections.map(section => {
    const clean = {};
    for (const key of ['title','body','url','linkText','image','alt']) {
      if (typeof section[key] !== 'string' || section[key].length > 20000) throw new Error(`Invalid story ${key}.`);
      clean[key] = section[key];
    }
    for (const key of ['url','image']) if (clean[key] && !safeUrl(clean[key])) throw new Error('Story links and images must use a full HTTPS URL without credentials.');
    return clean;
  });
  return doc;
}
const paragraphs = value => escape(value).split(/\n\s*\n/).map(p => `<p style="margin:0 0 18px;line-height:1.65">${p.replaceAll('\n','<br>')}</p>`).join('');
export function render(input, preview = false) {
  const d = validate(input);
  const stories = d.sections.map(s => `<tr><td style="padding:28px 32px;border-top:1px solid #e4e7e2">${s.image ? `<img src="${escape(safeUrl(s.image))}" alt="${escape(s.alt)}" width="576" style="display:block;width:100%;height:auto;border:0;margin-bottom:24px">` : ''}<h2 style="font-size:25px;line-height:1.25;margin:0 0 16px">${escape(s.title)}</h2>${paragraphs(s.body)}${s.url ? `<a href="${preview ? '#preview-only' : escape(safeUrl(s.url))}" style="color:${d.accent};font-weight:bold;${preview ? 'pointer-events:none' : ''}">${escape(s.linkText || 'Read more')} →</a>` : ''}</td></tr>`).join('');
  const unsubscribe = preview ? '#preview-only' : '{{ unsubscribe_link }}';
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(d.subject)}</title></head><body style="margin:0;background:#f0f2ed;color:#1d2923;font-family:Arial,Helvetica,sans-serif"><div style="display:none;max-height:0;overflow:hidden;mso-hide:all">${escape(d.preheader)}</div><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:32px 12px"><table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px;width:100%;background:white"><tr><td style="padding:32px;background:${d.accent};color:white"><p style="margin:0 0 14px;font-size:13px;letter-spacing:2px;text-transform:uppercase">${escape(d.brand)}</p><h1 style="font-size:34px;line-height:1.15;margin:0">${escape(d.subject)}</h1></td></tr><tr><td style="padding:32px 32px 8px">${paragraphs(d.intro)}</td></tr>${stories}<tr><td style="padding:28px 32px;background:#f6f7f3;font-size:12px;line-height:1.7;color:#526057">${paragraphs(d.footer)}<p>You are receiving this because you subscribed to ${escape(d.brand)}.</p><a href="${unsubscribe}" style="color:#526057;${preview ? 'pointer-events:none' : ''}">Unsubscribe</a></td></tr></table></td></tr></table></body></html>`;
}
export function campaign(input) {
  const d = validate(input);
  if (!d.subject.trim()) throw new Error('Add a subject before exporting a Keila draft.');
  return {data: {subject: d.subject, preview_text: d.preheader, settings: {type: 'html', do_not_track: true}, html_body: render(d)}};
}
