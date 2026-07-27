# -*- coding: utf-8 -*-
"""JavaScript de diagnostic DOM pour la page Codex."""

import json

DIAGNOSTIC_JS = r'''
(function(){
  const norm=s=>(s||'').replace(/\r/g,'').replace(/\s+/g,' ').trim();
  const visible=el=>!!el && !!(el.offsetWidth||el.offsetHeight||el.getClientRects().length);
  const path=el=>{
    if(!el) return '';
    const out=[];
    while(el && el.nodeType===1 && out.length<8){
      let part=el.tagName.toLowerCase();
      if(el.id) part+='#'+el.id;
      if(el.classList && el.classList.length) part+='.'+[...el.classList].slice(0,3).join('.');
      out.unshift(part); el=el.parentElement;
    }
    return out.join(' > ');
  };
  const rect=el=>{const r=el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};};
  const buttons=[...document.querySelectorAll('button,[role="button"]')].filter(visible).map((el,i)=>({
    i, tag:el.tagName, text:norm(el.innerText), aria:el.getAttribute('aria-label')||'', title:el.getAttribute('title')||'',
    testid:el.getAttribute('data-testid')||'', cls:el.className||'', rect:rect(el), path:path(el)
  }));
  const candidates=[...document.querySelectorAll('main div,main section,main article')].filter(visible).map((el,i)=>{
    const cs=getComputedStyle(el); const t=norm(el.innerText);
    return {i,text:t.slice(0,500),len:t.length,bg:cs.backgroundColor,radius:cs.borderRadius,display:cs.display,rect:rect(el),
      role:el.getAttribute('data-message-author-role')||el.getAttribute('data-author')||'',testid:el.getAttribute('data-testid')||'',path:path(el)};
  }).filter(x=>x.len>5 && x.rect.w>120 && x.rect.h>20).slice(-250);
  return JSON.stringify({url:location.href,title:document.title,ready:document.readyState,buttons,candidates,html:document.documentElement.outerHTML});
})()
'''


def parse(raw):
    if raw is None:
        raise ValueError("Aucun résultat JavaScript")
    return raw if isinstance(raw, dict) else json.loads(str(raw))
