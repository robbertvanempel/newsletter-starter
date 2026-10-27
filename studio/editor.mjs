import {sample, validate, render, campaign} from './newsletter.mjs';
const key = 'newsletter-starter-v1';
const $ = id => document.getElementById(id);
let doc = structuredClone(sample);
try { const saved = localStorage.getItem(key); if (saved) doc = validate(JSON.parse(saved)); } catch { $('status').textContent = 'Recovery needed: open a saved source file.'; }
const fields = ['brand','subject','preheader','intro','accent','footer'];
function preview() {
  try {
    $('preview').srcdoc = render(doc, true);
    try { localStorage.setItem(key, JSON.stringify(doc)); $('status').textContent = 'Saved in this browser'; }
    catch { $('status').textContent = 'Browser storage unavailable. Save a file.'; }
  } catch (e) { $('status').textContent = e.message; }
}
function draw() {
  fields.forEach(field => { $(field).value = doc[field]; });
  $('sections').replaceChildren();
  doc.sections.forEach((story, index) => {
    const box = document.createElement('div'); box.className = 'story';
    const head = document.createElement('div'); head.className = 'story-head';
    const name = document.createElement('strong'); name.textContent = `Story ${index+1}`; head.append(name);
    for (const [text, title, action, disabled] of [
      ['↑','Move story up',()=>{[doc.sections[index-1],doc.sections[index]]=[doc.sections[index],doc.sections[index-1]];},index===0],
      ['↓','Move story down',()=>{[doc.sections[index+1],doc.sections[index]]=[doc.sections[index],doc.sections[index+1]];},index===doc.sections.length-1],
      ['×','Remove story',()=>doc.sections.splice(index,1),false]
    ]) { const button=document.createElement('button');button.className='small';button.textContent=text;button.title=title;button.setAttribute('aria-label',title);button.disabled=disabled;button.onclick=()=>{action();draw();};head.append(button); }
    box.append(head);
    for(const [field,title] of [['title','Headline'],['body','Story'],['url','Link URL (HTTPS)'],['linkText','Link label'],['image','Image URL (optional, HTTPS)'],['alt','Image description']]) {
      const label=document.createElement('label');label.textContent=title;
      const input=document.createElement(field==='body'?'textarea':'input');if(field==='body') input.rows=4;
      input.value=story[field];input.addEventListener('input',()=>{story[field]=input.value;preview();});label.append(input);box.append(label);
    }
    $('sections').append(box);
  });
  preview();
}
fields.forEach(field=>$(field).addEventListener('input',()=>{doc[field]=$(field).value;preview();}));
$('add').onclick=()=>{if(doc.sections.length>=40)return;doc.sections.push({title:'Another story',body:'Write your story here.',url:'',linkText:'Read more',image:'',alt:''});draw();};
function download(name,type,content){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}
function perform(fn){try{fn();}catch(e){$('status').textContent=e.message;}}
$('html').onclick=()=>perform(()=>download('newsletter.html','text/html',render(doc)));
$('keila').onclick=()=>perform(()=>download('newsletter.keila.json','application/json',JSON.stringify(campaign(doc),null,2)));
$('source').onclick=()=>perform(()=>download('newsletter.source.json','application/json',JSON.stringify(validate(doc),null,2)));
$('open').onchange=async e=>{const file=e.target.files[0];if(!file)return;if(file.size>2_000_000){$('status').textContent='Choose a source file smaller than 2 MB.';return;}try{const next=validate(JSON.parse(await file.text()));doc=next;draw();}catch(error){$('status').textContent=error.message;}e.target.value='';};
$('reset').onclick=()=>{if(confirm('Start a new edition? Save an editable file first if you need this draft.')){doc=structuredClone(sample);draw();}};
for(const [id,width] of [['desktop','100%'],['mobile','375px']]) $(id).onclick=()=>{$('preview').style.maxWidth=width;$('desktop').setAttribute('aria-pressed',String(id==='desktop'));$('mobile').setAttribute('aria-pressed',String(id==='mobile'));};
draw();
