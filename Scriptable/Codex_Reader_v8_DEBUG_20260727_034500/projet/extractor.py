# -*- coding: utf-8 -*-
"""Extraction automatique et contournement manuel."""

import json

AUTO_JS = r'''
(function(){
  const norm=s=>(s||'').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const visible=el=>!!el && !!(el.offsetWidth||el.offsetHeight||el.getClientRects().length);
  const txt=el=>norm(el?(el.innerText||el.textContent||''):'');
  const clean=el=>{const c=el.cloneNode(true);c.querySelectorAll('script,style,button,[role="button"],textarea,input,form,[data-testid*="feedback"],[aria-label*="thumb" i],[aria-label*="copy" i],[aria-label*="share" i]').forEach(n=>n.remove());return c;};
  const users=[...document.querySelectorAll('[data-message-author-role="user"],[data-author="user"],[data-testid*="user-message"]')].filter(visible);
  const assistants=[...document.querySelectorAll('[data-message-author-role="assistant"],[data-author="assistant"],[data-testid*="assistant-message"]')].filter(visible);
  let user=users[users.length-1]||null;
  let assistant=null;
  if(user && assistants.length){assistant=assistants.filter(a=>user.compareDocumentPosition(a)&Node.DOCUMENT_POSITION_FOLLOWING)[0]||assistants[assistants.length-1];}
  if(!user){
    const blocks=[...document.querySelectorAll('main div,main section,main article')].filter(visible).filter(el=>{
      const t=txt(el); if(t.length<20||t.length>20000||/Demander des modifications|poser une question/i.test(t)) return false;
      const cs=getComputedStyle(el); const r=parseFloat(cs.borderRadius||'0'); const bg=cs.backgroundColor||'';
      return r>=12 && bg!=='rgba(0, 0, 0, 0)' && bg!=='transparent';
    });
    user=blocks[blocks.length-1]||null;
  }
  if(!assistant && user){
    let n=user;
    while(n){n=n.nextElementSibling;if(!n)break;const t=txt(n);if(t.length>100 && !/Demander des modifications|poser une question/i.test(t)){assistant=n;break;}}
  }
  if(!user) return JSON.stringify({error:'QUESTION_NOT_FOUND'});
  if(!assistant) return JSON.stringify({error:'ANSWER_NOT_FOUND'});
  const q=clean(user), a=clean(assistant);
  return JSON.stringify({url:location.href,title:document.title,question:txt(q),question_html:q.innerHTML,answer:txt(a),answer_html:a.innerHTML});
})()
'''

INSTALL_MANUAL_JS = r'''
(function(){
  window.__codexManual={question:null,end:null};
  const style=document.createElement('style');style.id='__codex_debug_style';style.textContent='.__codex_pick{outline:4px solid #0A84FF!important;outline-offset:3px!important}';document.head.appendChild(style);
  const handler=function(ev){
    ev.preventDefault();ev.stopPropagation();
    const el=ev.target.closest('div,section,article,button,[role="button"]')||ev.target;
    if(!window.__codexManual.question){window.__codexManual.question=el;el.classList.add('__codex_pick');document.title='CODEX_PICK_QUESTION';}
    else if(!window.__codexManual.end){window.__codexManual.end=el;el.classList.add('__codex_pick');document.title='CODEX_PICK_END';document.removeEventListener('click',handler,true);}
  };
  document.addEventListener('click',handler,true);
  return 'MANUAL_READY';
})()
'''

MANUAL_EXTRACT_JS = r'''
(function(){
  const state=window.__codexManual||{}; const q=state.question, end=state.end;
  if(!q) return JSON.stringify({error:'MANUAL_QUESTION_MISSING'});
  if(!end) return JSON.stringify({error:'MANUAL_END_MISSING'});
  const norm=s=>(s||'').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const txt=el=>norm(el?(el.innerText||el.textContent||''):'');
  let container=end;
  for(let i=0;i<8&&container;i++){
    const t=txt(container);
    if(t.length>200 && q.compareDocumentPosition(container)&Node.DOCUMENT_POSITION_FOLLOWING) break;
    container=container.parentElement;
  }
  if(!container) return JSON.stringify({error:'MANUAL_ANSWER_CONTAINER_MISSING'});
  const qc=q.cloneNode(true), ac=container.cloneNode(true);
  [qc,ac].forEach(c=>c.querySelectorAll('script,style,button,[role="button"],textarea,input,form,[data-testid*="feedback"],[aria-label*="thumb" i],[aria-label*="copy" i],[aria-label*="share" i]').forEach(n=>n.remove()));
  return JSON.stringify({url:location.href,title:document.title,question:txt(qc),question_html:qc.innerHTML,answer:txt(ac),answer_html:ac.innerHTML});
})()
'''


def parse(raw):
    if raw is None:
        raise ValueError("Aucun résultat JavaScript")
    data=raw if isinstance(raw,dict) else json.loads(str(raw))
    if data.get('error'):
        raise ValueError(data['error'])
    return data
