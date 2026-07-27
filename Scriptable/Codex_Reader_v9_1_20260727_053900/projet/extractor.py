# -*- coding: utf-8 -*-
"""Moteur d'extraction multi-échanges Codex Reader v9.1."""

import json

CHECK_SESSION_JS = r'''
JSON.stringify({
  url: location.href,
  connected: !location.pathname.includes('/auth/') &&
    !document.querySelector('a[href*="/auth/login"], button[data-testid*="login"]')
})
'''

PREPARE_JS = r'''
(function(){
  const nodes=[document.scrollingElement,...document.querySelectorAll('*')];
  for(const el of nodes){
    try{if(el && el.scrollHeight>el.clientHeight+80) el.scrollTop=el.scrollHeight;}catch(_){}
  }
  window.scrollTo(0,document.documentElement.scrollHeight);
  return JSON.stringify({prepared:true});
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
    const r=el.getBoundingClientRect();
    const c=getComputedStyle(el);
    const radius=parseFloat(c.borderRadius||'0');
    const bg=c.backgroundColor||'';
    return r.width>240&&r.height>55&&radius>=10&&bg!=='transparent'&&bg!=='rgba(0, 0, 0, 0)';
  };

  api.questionCards=function(){
    let items=[...document.querySelectorAll('div[role="button"],section[role="button"],article[role="button"]')]
      .filter(api.isQuestionCard);
    if(!items.length){
      items=[...document.querySelectorAll('div,section,article')].filter(api.isQuestionCard);
    }
    items.sort((a,b)=>a===b?0:(api.before(a,b)?-1:1));
    items=items.filter((el,index,all)=>{
      if(all.some(other=>other!==el&&el.contains(other)&&api.isQuestionCard(other))) return false;
      const fp=api.text(el).replace(/\s+/g,' ').trim();
      return all.findIndex(x=>api.text(x).replace(/\s+/g,' ').trim()===fp)===index;
    });
    return items;
  };

  api.findComposer=function(){
    const controls=[...document.querySelectorAll('textarea,input,[contenteditable="true"],[role="textbox"],[data-testid*="composer"]')];
    for(const el of controls){
      const label=[el.getAttribute('placeholder')||'',el.getAttribute('aria-label')||'',api.text(el)].join(' ');
      if(/demander des modifications|poser une question|ask for changes/i.test(label)){
        let n=el;
        while(n&&n!==document.body){
          const r=n.getBoundingClientRect();
          if(r.width>250&&r.height>40&&r.height<320) return n;
          n=n.parentElement;
        }
        return el;
      }
    }
    return null;
  };

  api.feedbacks=function(){
    return [...document.querySelectorAll('[aria-label*="avis positif" i],[aria-label*="avis négatif" i],[aria-label*="thumbs up" i],[aria-label*="thumbs down" i]')];
  };

  api.endForQuestion=function(question,nextQuestion){
    if(nextQuestion) return nextQuestion;
    const feedbacks=api.feedbacks().filter(el=>api.before(question,el));
    if(feedbacks.length) return feedbacks[feedbacks.length-1];
    return api.findComposer()||document.body.lastElementChild;
  };

  api.isNoise=function(el){
    if(!el) return true;
    if(el.closest('header,nav,form,[data-testid*="composer"]')) return true;
    const label=[el.getAttribute&&el.getAttribute('aria-label')||'',el.getAttribute&&el.getAttribute('data-testid')||'',el.className&&String(el.className)||''].join(' ');
    if(/feedback|composer|toolbar|navigation|avis positif|avis négatif|copier|partager|soumettre/i.test(label)) return true;
    const t=api.text(el);
    if(!t||/demander des modifications|poser une question/i.test(t)) return true;
    return false;
  };

  api.cleanClone=function(source){
    const clone=source.cloneNode(true);
    clone.querySelectorAll('script,style,input,textarea,form,svg,canvas,noscript,[data-testid*="feedback"],[data-testid*="composer"],[aria-label*="avis positif" i],[aria-label*="avis négatif" i],[aria-label*="copier" i],[aria-label*="partager" i],[aria-label*="soumettre" i]').forEach(el=>el.remove());
    clone.querySelectorAll('button,[role="button"]').forEach(el=>{
      const label=(el.getAttribute('aria-label')||'').toLowerCase();
      if(/avis positif|avis négatif|copier|partager|soumettre/.test(label)) el.remove();
      else el.replaceWith(...el.childNodes);
    });
    return clone;
  };

  api.semanticHTML=function(source){
    const allowed=new Set(['P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE','BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A','DIV','SPAN','HR','DETAILS','SUMMARY']);
    const copy=api.cleanClone(source);
    [...copy.querySelectorAll('*')].forEach(el=>{
      if(!allowed.has(el.tagName)){el.replaceWith(...el.childNodes);return;}
      [...el.attributes].forEach(a=>{if(!(el.tagName==='A'&&a.name==='href')) el.removeAttribute(a.name);});
    });
    return copy.innerHTML;
  };

  api.isFilePanel=function(el){
    if(!api.rendered(el)) return false;
    const t=api.text(el);
    if(!/^(fichiers|files)\s*\(\d+\)/i.test(t)) return false;
    const r=el.getBoundingClientRect();
    return r.width>250&&r.height>100;
  };

  api.collect=function(question,nextQuestion,index,total){
    const end=api.endForQuestion(question,nextQuestion);
    const qText=api.text(question);
    if(!qText) return {error:'Question détectée mais vide'};
    const qHTML=api.semanticHTML(question);
    const selector='h1,h2,h3,h4,h5,h6,p,ul,ol,pre,table,blockquote,details';
    let candidates=[...document.querySelectorAll(selector)].filter(el=>{
      if(api.isNoise(el)||question.contains(el)) return false;
      if(!api.before(question,el)) return false;
      if(end&&!api.before(el,end)) return false;
      return api.text(el).length>=2;
    });
    const panels=[...document.querySelectorAll('div,section,article')].filter(el=>{
      if(api.isNoise(el)||!api.before(question,el)) return false;
      if(end&&!api.before(el,end)) return false;
      return api.isFilePanel(el);
    });
    candidates=candidates.filter(el=>!panels.some(p=>p.contains(el)));
    candidates.push(...panels);
    candidates.sort((a,b)=>a===b?0:(api.before(a,b)?-1:1));
    const selected=[];const seen=new Set();
    for(const el of candidates){
      if(selected.some(p=>p.contains(el))) continue;
      const fp=api.text(el).replace(/\s+/g,' ').trim();
      if(!fp||seen.has(fp)) continue;
      seen.add(fp);selected.push(el);
    }
    const root=document.createElement('div');
    selected.forEach(el=>root.appendChild(api.cleanClone(el)));
    const answerText=api.text(root);
    if(answerText.length<20) return {error:'Réponse reconstruite mais vide ou trop courte',debug:{index:index,total:total,candidateCount:candidates.length,selectedCount:selected.length,answerLength:answerText.length}};
    return {url:location.href,title:document.title,question:qText,question_html:qHTML,answer:answerText,answer_html:api.semanticHTML(root),debug:{method:'multi-turn-pairing',exchangeIndex:index+1,exchangeCount:total,candidateCount:candidates.length,selectedCount:selected.length,answerLength:answerText.length,questionLength:qText.length}};
  };

  window.__codexReaderV91=api;
})();
'''

AUTO_EXTRACT_JS = COMMON_JS + r'''
(function(){
  const api=window.__codexReaderV91;
  const questions=api.questionCards();
  if(!questions.length) return JSON.stringify({error:'Aucune question détectée'});
  const index=questions.length-1;
  return JSON.stringify(api.collect(questions[index],null,index,questions.length));
})()
'''

START_MANUAL_JS = COMMON_JS + r'''
(function(){
  const api=window.__codexReaderV91;
  window.__codexReaderSelectedQuestion=null;
  if(window.__codexReaderManualHandler) document.removeEventListener('click',window.__codexReaderManualHandler,true);
  const handler=function(event){
    event.preventDefault();event.stopPropagation();
    let node=event.target;
    while(node&&node!==document.body&&!api.isQuestionCard(node)) node=node.parentElement;
    if(!node||node===document.body) return;
    window.__codexReaderSelectedQuestion=node;
    node.style.outline='4px solid #0a84ff';node.style.outlineOffset='3px';
    document.removeEventListener('click',handler,true);
  };
  window.__codexReaderManualHandler=handler;
  document.addEventListener('click',handler,true);
  return JSON.stringify({manual:true});
})()
'''

MANUAL_EXTRACT_JS = COMMON_JS + r'''
(function(){
  const api=window.__codexReaderV91;
  const question=window.__codexReaderSelectedQuestion;
  if(!question) return JSON.stringify({error:'Aucune question sélectionnée'});
  const questions=api.questionCards();
  let index=questions.indexOf(question);
  if(index<0){questions.push(question);questions.sort((a,b)=>api.before(a,b)?-1:1);index=questions.indexOf(question);}
  const next=questions[index+1]||null;
  return JSON.stringify(api.collect(question,next,index,questions.length));
})()
'''


def parse(raw):
    if raw is None:
        raise ValueError('Aucun résultat JavaScript')
    data=raw if isinstance(raw,dict) else json.loads(str(raw))
    if data.get('error'):
        debug=data.get('debug') or {}
        raise ValueError(data['error']+(f' | debug={debug}' if debug else ''))
    return data
