# -*- coding: utf-8 -*-
import json

CHECK_SESSION_JS = "JSON.stringify({url:location.href,connected:!location.pathname.includes('/auth/')&&!document.querySelector('a[href*=\"/auth/login\"],button[data-testid*=\"login\"]')})"

PREPARE_JS = r'''(function(){for(const e of [document.scrollingElement,...document.querySelectorAll('*')]){try{if(e&&e.scrollHeight>e.clientHeight+80){e.scrollTop=0;e.scrollTop=e.scrollHeight}}catch(_){}}document.querySelectorAll('details').forEach(e=>e.open=true);window.scrollTo(0,document.documentElement.scrollHeight);return JSON.stringify({prepared:true})})()'''

COMMON_JS = r'''
(function(){
const A={};
A.n=s=>(s||'').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
A.t=e=>A.n(e?(e.innerText||e.textContent||''):'');
A.v=e=>!!e&&!!(e.offsetWidth||e.offsetHeight||e.getClientRects().length);
A.b=(a,b)=>!!(a&&b&&(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING));
A.q=e=>{if(!A.v(e))return false;const t=A.t(e);if(t.length<20||t.length>80000||/demander des modifications|poser une question/i.test(t))return false;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return r.width>240&&r.height>55&&parseFloat(c.borderRadius||0)>=10&&c.backgroundColor!=='transparent'&&c.backgroundColor!=='rgba(0, 0, 0, 0)'};
A.questions=()=>{let x=[...document.querySelectorAll('div[role=button],section[role=button],article[role=button]')].filter(A.q);if(!x.length)x=[...document.querySelectorAll('div,section,article')].filter(A.q);x.sort((a,b)=>A.b(a,b)?-1:1);return x.filter((e,i,z)=>!z.some(o=>o!==e&&e.contains(o)&&A.q(o))&&z.findIndex(o=>A.t(o).replace(/\s+/g,' ')===A.t(e).replace(/\s+/g,' '))===i)};
A.composer=()=>[...document.querySelectorAll('textarea,input,[contenteditable=true],[role=textbox],[data-testid*=composer]')].find(e=>/demander des modifications|poser une question|ask for changes/i.test((e.getAttribute('placeholder')||'')+' '+(e.getAttribute('aria-label')||'')))||null;
A.end=(q,next)=>{if(next)return next;const f=[...document.querySelectorAll('[aria-label*=\"avis positif\" i],[aria-label*=\"avis négatif\" i],[aria-label*=\"thumbs up\" i],[aria-label*=\"thumbs down\" i]')].filter(e=>A.b(q,e));return f.pop()||A.composer()||document.body.lastElementChild};
A.clean=s=>{const c=s.cloneNode(true);c.querySelectorAll('script,style,input,textarea,form,svg,canvas,noscript,[data-testid*=feedback],[data-testid*=composer],[aria-label*=\"avis positif\" i],[aria-label*=\"avis négatif\" i],[aria-label*=copier i],[aria-label*=partager i],[aria-label*=soumettre i]').forEach(e=>e.remove());c.querySelectorAll('button,[role=button]').forEach(e=>{const l=(e.getAttribute('aria-label')||'').toLowerCase();/avis positif|avis négatif|copier|partager|soumettre/.test(l)?e.remove():e.replaceWith(...e.childNodes)});return c};
A.html=s=>{const ok=new Set(['P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE','BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A','DIV','SPAN','HR','DETAILS','SUMMARY']),c=A.clean(s);[...c.querySelectorAll('*')].forEach(e=>{if(!ok.has(e.tagName)){e.replaceWith(...e.childNodes);return}[...e.attributes].forEach(a=>{if(!(e.tagName==='A'&&a.name==='href'))e.removeAttribute(a.name)})});return c.innerHTML};
A.noise=e=>!e||e.closest('header,nav,form,[data-testid*=composer]')||/demander des modifications|poser une question/i.test(A.t(e));
A.semantic=(q,end)=>{const root=document.createElement('div'),sel='h1,h2,h3,h4,h5,h6,p,ul,ol,pre,table,blockquote,details';let x=[...document.querySelectorAll(sel)].filter(e=>!A.noise(e)&&!q.contains(e)&&A.b(q,e)&&(!end||A.b(e,end))&&A.t(e).length>1);const p=[...document.querySelectorAll('div,section,article')].filter(e=>!A.noise(e)&&A.b(q,e)&&(!end||A.b(e,end))&&/^(fichiers|files)\s*\(\d+\)/i.test(A.t(e)));x=x.filter(e=>!p.some(v=>v.contains(e))).concat(p);x.sort((a,b)=>A.b(a,b)?-1:1);const chosen=[],seen=new Set();for(const e of x){if(chosen.some(v=>v.contains(e)))continue;const f=A.t(e).replace(/\s+/g,' ');if(!f||seen.has(f))continue;seen.add(f);chosen.push(e);root.appendChild(A.clean(e))}return {root,method:'semantic',count:chosen.length}};
A.range=(q,end)=>{const root=document.createElement('div');try{const r=document.createRange();r.setStartAfter(q);r.setEndBefore(end);root.appendChild(r.cloneContents())}catch(_){}return {root,method:'range',count:root.children.length}};
A.siblings=(q,end)=>{const root=document.createElement('div');let a=q;while(a&&!a.contains(end))a=a.parentElement;if(!a)return {root,method:'siblings',count:0};let qc=q;while(qc.parentElement!==a)qc=qc.parentElement;let ec=end;while(ec.parentElement!==a)ec=ec.parentElement;for(let n=qc.nextElementSibling;n&&n!==ec;n=n.nextElementSibling)root.appendChild(A.clean(n));return {root,method:'siblings',count:root.children.length}};
A.collect=(q,next,i,total)=>{const end=A.end(q,next),qt=A.t(q);if(!qt)return {error:'Question vide'};const tries=[A.semantic(q,end),A.range(q,end),A.siblings(q,end)];let best=null;for(const z of tries){const root=A.clean(z.root),text=A.t(root);if(!best||text.length>best.text.length)best={...z,root,text}}if(!best||best.text.length<20)return {error:'Réponse trop courte',debug:{lengths:tries.map(z=>A.t(z.root).length)}};return {url:location.href,question:qt,question_html:A.html(q),answer:best.text,answer_html:A.html(best.root),debug:{method:best.method,exchangeIndex:i+1,exchangeCount:total,selectedCount:best.count,answerLength:best.text.length}}};
window.__cr92=A;
})();
'''

AUTO_EXTRACT_JS=COMMON_JS+r'''(function(){const A=window.__cr92,q=A.questions();if(!q.length)return JSON.stringify({error:'Aucune question'});const i=q.length-1;return JSON.stringify(A.collect(q[i],null,i,q.length))})()'''
START_MANUAL_JS=COMMON_JS+r'''(function(){const A=window.__cr92;window.__crq=null;const h=e=>{e.preventDefault();e.stopPropagation();let n=e.target;while(n&&n!==document.body&&!A.q(n))n=n.parentElement;if(!n||n===document.body)return;window.__crq=n;n.style.outline='4px solid #0a84ff';document.removeEventListener('click',h,true)};document.addEventListener('click',h,true);return JSON.stringify({manual:true})})()'''
MANUAL_EXTRACT_JS=COMMON_JS+r'''(function(){const A=window.__cr92,q=window.__crq;if(!q)return JSON.stringify({error:'Aucune question sélectionnée'});const all=A.questions();let i=all.indexOf(q);if(i<0){all.push(q);all.sort((a,b)=>A.b(a,b)?-1:1);i=all.indexOf(q)}return JSON.stringify(A.collect(q,all[i+1]||null,i,all.length))})()'''

def parse(raw):
    if raw is None: raise ValueError('Aucun résultat JavaScript')
    data=raw if isinstance(raw,dict) else json.loads(str(raw))
    if data.get('error'): raise ValueError(data['error']+(f" | debug={data.get('debug')}" if data.get('debug') else ''))
    return data
