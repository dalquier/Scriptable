# -*- coding: utf-8 -*-
"""JavaScript d’analyse du dernier échange ChatGPT/Codex."""

import json

CHECK_SESSION_JS = r'''
JSON.stringify({
  ready: document.readyState,
  url: location.href,
  connected: !location.pathname.includes('/auth/') &&
    !document.querySelector('a[href*="/auth/login"], button[data-testid*="login"]')
})
'''

ANALYZE_LAST_EXCHANGE_JS = r'''
(function(){
  const norm = s => (s || '').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const visible = el => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const text = el => norm(el ? (el.innerText || el.textContent || '') : '');
  const all = sel => [...document.querySelectorAll(sel)].filter(visible);

  function lastUser(){
    let items = all('[data-message-author-role="user"], [data-author="user"], [data-testid*="user-message"]');
    if(items.length) return items[items.length - 1];

    const candidates = all('main article, main section, main div').filter(el => {
      const t = text(el);
      if(t.length < 8 || t.length > 20000) return false;
      const cs = getComputedStyle(el);
      const rounded = parseFloat(cs.borderRadius || '0') >= 8;
      const bg = cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)';
      return rounded && bg;
    });
    return candidates[candidates.length - 1] || null;
  }

  function expandQuestion(el){
    const scope = el.closest('article, section, [data-message-author-role], main') || el.parentElement;
    if(!scope) return;
    const words = ['show more','read more','expand','afficher plus','voir plus','développer'];
    const buttons = [...scope.querySelectorAll('button')];
    const target = buttons.find(b => words.some(w => (b.innerText || b.getAttribute('aria-label') || '').toLowerCase().includes(w)));
    if(target) target.click();
  }

  function cleanClone(el){
    const clone = el.cloneNode(true);
    clone.querySelectorAll('script,style,button,textarea,input,form,[role="button"],[data-testid*="feedback"],[aria-label*="thumb" i],[aria-label*="copy" i],[aria-label*="share" i]').forEach(n => n.remove());
    return clone;
  }

  function assistantAfter(user){
    const assistants = all('[data-message-author-role="assistant"], [data-author="assistant"], [data-testid*="assistant-message"]');
    if(assistants.length){
      const after = assistants.filter(a => user.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING);
      if(after.length) return after[0];
      return assistants[assistants.length - 1];
    }

    let node = user;
    while(node){
      node = node.nextElementSibling;
      if(!node) break;
      const t = text(node);
      if(t.length > 20) return node;
    }
    return null;
  }

  const user = lastUser();
  if(!user) return JSON.stringify({error:'Dernière question introuvable'});
  expandQuestion(user);

  const assistant = assistantAfter(user);
  if(!assistant) return JSON.stringify({error:'Réponse associée introuvable'});

  const q = cleanClone(user);
  const a = cleanClone(assistant);

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: text(q),
    question_html: q.innerHTML,
    answer: text(a),
    answer_html: a.innerHTML
  });
})()
'''


def parse_json(raw):
    if raw is None:
        raise ValueError("Aucun résultat JavaScript")
    if isinstance(raw, dict):
        data = raw
    else:
        data = json.loads(str(raw))
    if data.get("error"):
        raise ValueError(data["error"])
    return data
