# -*- coding: utf-8 -*-
"""Extraction intégrale du dernier échange pour Codex Reader v10."""

import json

CHECK_SESSION_JS = r'''
JSON.stringify({
  url: location.href,
  connected: !location.pathname.includes('/auth/') &&
    !document.querySelector('a[href*="/auth/login"],button[data-testid*="login"]')
})
'''

PREPARE_JS = r'''
(function(){
  const nodes=[document.scrollingElement,...document.querySelectorAll('*')];
  for(const el of nodes){
    try{if(el&&el.scrollHeight>el.clientHeight+80) el.scrollTop=el.scrollHeight}catch(_){}
  }
  window.scrollTo(0,document.documentElement.scrollHeight);
  return JSON.stringify({prepared:true,height:document.documentElement.scrollHeight});
})()
'''

COMMON_JS = r'''
(function(){
  const api={};
  api.norm=s=>(s||'').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  api.text=el=>api.norm(el?(el.innerText||el.textContent||''):'');
  api.rendered=el=>!!el&&!!(el.offsetWidth||el.offsetHeight||el.getClientRects().length);
  api.before=(a,b)=>!!(a&&b&&(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING));
  api.isQuestionCard=function(el){
    if(!api.rendered(el)) return false;
    const t=api.text(el);
    if(t.length<20||t.length>80000) return false;
    if(/demander des modifications|poser une question|ask for changes/i.test(t)) return false;
    const r=el.getBoundingClientRect();const c=getComputedStyle(el);
    const radius=parseFloat(c.borderRadius||'0');const bg=c.backgroundColor||'';
    return r.width>220&&r.height>45&&radius>=8&&bg!=='transparent'&&bg!=='rgba(0, 0, 0, 0)';
  };
  api.questions=function(){
    let items=[...document.querySelectorAll('div[role="button"],section[role="button"],article[role="button"]')].filter(api.isQuestionCard);
    if(!items.length) items=[...document.querySelectorAll('div,section,article')].filter(api.isQuestionCard);
    items.sort((a,b)=>a===b?0:(api.before(a,b)?-1:1));
    items=items.filter((el,i,all)=>!all.some(o=>o!==el&&el.contains(o)&&api.isQuestionCard(o)));
    const seen=new Set();
    return items.filter(el=>{const fp=api.text(el).replace(/\s+/g,' ').trim();if(!fp||seen.has(fp)) return false;seen.add(fp);return true});
  };
  api.composer=function(){
    const controls=[...document.querySelectorAll('textarea,input,[contenteditable="true"],[role="textbox"],[data-testid*="composer"]')];
    for(const el of controls){
      const label=[el.getAttribute('placeholder')||'',el.getAttribute('aria-label')||'',api.text(el)].join(' ');
      if(/demander des modifications|poser une question|ask for changes/i.test(label)){
        let n=el;while(n&&n!==document.body){const r=n.getBoundingClientRect();if(r.width>220&&r.height>35&&r.height<360)return n;n=n.parentElement}return el;
      }
    }
    return null;
  };
  api.clean=function(root){
    root.querySelectorAll('script,style,form,input,textarea,select,option,svg,canvas,noscript,nav,header,[data-testid*="composer"],[data-testid*="feedback"],[aria-label*="avis positif" i],[aria-label*="avis négatif" i],[aria-label*="thumbs up" i],[aria-label*="thumbs down" i],[aria-label*="copier" i],[aria-label*="partager" i],[aria-label*="soumettre" i]').forEach(el=>el.remove());
    root.querySelectorAll('button,[role="button"]').forEach(el=>{const label=(el.getAttribute('aria-label')||'').toLowerCase();if(/avis positif|avis négatif|thumbs|copier|partager|soumettre/.test(label))el.remove();else el.replaceWith(...el.childNodes)});
    return root;
  };
  api.sanitizeHTML=function(root){
    const allowed=new Set(['DIV','SPAN','P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE','BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','B','EM','I','A','HR','DETAILS','SUMMARY']);
    const copy=api.clean(root.cloneNode(true));
    [...copy.querySelectorAll('*')].forEach(el=>{
      if(!allowed.has(el.tagName)){el.replaceWith(...el.childNodes);return}
      [...el.attributes].forEach(a=>{if(!(el.tagName==='A'&&a.name==='href')) el.removeAttribute(a.name)});
    });
    return copy.innerHTML;
  };
  api.rangeClone=function(question,end){
    const range=document.createRange();
    try{range.setStartAfter(question)}catch(_){range.setStart(question.parentNode,Array.prototype.indexOf.call(question.parentNode.childNodes,question)+1)}
    if(end){try{range.setEndBefore(end)}catch(_){range.setEnd(end.parentNode,Array.prototype.indexOf.call(end.parentNode.childNodes,end))}}
    else range.setEndAfter(document.body.lastChild||document.body);
    const wrap=document.createElement('div');wrap.appendChild(range.cloneContents());return api.clean(wrap);
  };
  api.collectAllTextNodes=function(question,end){
    const root=document.createElement('div');
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
    let node;let count=0;
    while((node=walker.nextNode())){
      if(node===question||question.contains(node)) continue;
      const container=node.nodeType===Node.TEXT_NODE?node.parentElement:node;
      if(!container||!api.before(question,container)) continue;
      if(end&&!api.before(container,end)) continue;
      if(container.closest('header,nav,form,[data-testid*="composer"],[data-testid*="feedback"]')) continue;
      if(node.nodeType===Node.TEXT_NODE){
        const t=node.nodeValue||'';if(!t.trim()) continue;
        root.appendChild(document.createTextNode(t));root.appendChild(document.createTextNode('\n'));count++;
      }
    }
    return {root:root,count:count};
  };
  api.extract=function(index){
    const qs=api.questions();if(!qs.length)return {error:'Aucune question détectée'};
    const i=index==null?qs.length-1:index;const q=qs[i];const next=qs[i+1]||null;const end=next||api.composer();
    const rangeRoot=api.rangeClone(q,end);
    const rangeText=api.text(rangeRoot);
    const all=api.collectAllTextNodes(q,end);const allText=api.text(all.root);
    const fullText=allText.length>rangeText.length?allText:rangeText;
    const fullHTML=rangeText?api.sanitizeHTML(rangeRoot):'<pre>'+fullText.replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]))+'</pre>';
    if(fullText.length<20)return {error:'Réponse vide ou trop courte',debug:{rangeLength:rangeText.length,allTextLength:allText.length}};
    return {url:location.href,title:document.title,question:api.text(q),question_html:api.sanitizeHTML(q),answer:fullText,answer_html:fullHTML,debug:{method:allText.length>rangeText.length?'all-text-nodes':'dom-range',exchangeIndex:i+1,exchangeCount:qs.length,answerLength:fullText.length,rangeLength:rangeText.length,allTextLength:allText.length,nodeCount:all.count}};
  };
  window.__codexReaderV10=api;
})();
'''

AUTO_EXTRACT_JS = COMMON_JS + r'''
(function(){return JSON.stringify(window.__codexReaderV10.extract(null))})()
'''

START_MANUAL_JS = COMMON_JS + r'''
(function(){
 const api=window.__codexReaderV10;window.__codexReaderV10Selected=null;
 if(window.__codexReaderV10Handler)document.removeEventListener('click',window.__codexReaderV10Handler,true);
 const h=function(e){e.preventDefault();e.stopPropagation();let n=e.target;while(n&&n!==document.body&&!api.isQuestionCard(n))n=n.parentElement;if(!n||n===document.body)return;window.__codexReaderV10Selected=n;n.style.outline='4px solid #0a84ff';n.style.outlineOffset='3px';document.removeEventListener('click',h,true)};
 window.__codexReaderV10Handler=h;document.addEventListener('click',h,true);return JSON.stringify({manual:true});
})()
'''

MANUAL_EXTRACT_JS = COMMON_JS + r'''
(function(){
 const api=window.__codexReaderV10;const q=window.__codexReaderV10Selected;if(!q)return JSON.stringify({error:'Aucune question sélectionnée'});
 const qs=api.questions();let i=qs.indexOf(q);if(i<0){qs.push(q);qs.sort((a,b)=>api.before(a,b)?-1:1);i=qs.indexOf(q)}
 return JSON.stringify(api.extract(i));
})()
'''


def parse(raw):
    if raw is None:
        raise ValueError("Aucun résultat JavaScript")
    data = raw if isinstance(raw, dict) else json.loads(str(raw))
    if data.get("error"):
        debug = data.get("debug") or {}
        suffix = f" | debug={debug}" if debug else ""
        raise ValueError(data["error"] + suffix)
    return data
