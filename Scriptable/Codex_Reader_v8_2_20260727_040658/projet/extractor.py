# -*- coding: utf-8 -*-
"""Extraction robuste du dernier échange Codex."""

import json

CHECK_SESSION_JS = r'''
JSON.stringify({
  url: location.href,
  connected: !location.pathname.includes('/auth/') &&
    !document.querySelector('a[href*="/auth/login"], button[data-testid*="login"]')
})
'''

EXTRACT_JS = r'''
(function(){
  const norm = s => (s || '').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const visible = el => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const txt = el => norm(el ? (el.innerText || el.textContent || '') : '');

  function nearestBlock(el){
    let n = el;
    while(n && n !== document.body){
      const t = txt(n);
      const r = n.getBoundingClientRect();
      if(t.length > 40 && r.width > 250 && r.height > 40) return n;
      n = n.parentElement;
    }
    return el;
  }

  function clean(root){
    const clone = root.cloneNode(true);
    clone.querySelectorAll([
      'script','style','button','input','textarea','form','svg','canvas',
      '[role="button"]','[data-testid*="feedback"]','[data-testid*="composer"]',
      '[aria-label*="avis positif" i]','[aria-label*="avis négatif" i]',
      '[aria-label*="thumb" i]','[aria-label*="copier" i]','[aria-label*="partager" i]',
      '[aria-label*="fichier" i]','[aria-label*="saisie vocale" i]','[aria-label*="soumettre" i]'
    ].join(',')).forEach(n => n.remove());
    return clone;
  }

  function semanticHTML(root){
    const allowed = new Set(['P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE','BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A','DIV','SPAN']);
    const copy = clean(root);
    [...copy.querySelectorAll('*')].forEach(el => {
      if(!allowed.has(el.tagName)) {
        el.replaceWith(...el.childNodes);
        return;
      }
      [...el.attributes].forEach(a => {
        if(el.tagName === 'A' && a.name === 'href') return;
        el.removeAttribute(a.name);
      });
    });
    return copy.innerHTML;
  }

  // 1. Dernier encadré utilisateur : le diagnostic montre un grand DIV gris.
  let users = [...document.querySelectorAll('[data-message-author-role="user"], [data-author="user"], [data-testid*="user-message"]')].filter(visible);
  let user = users[users.length - 1] || null;

  if(!user){
    const all = [...document.querySelectorAll('main div')].filter(visible).filter(el => {
      const t = txt(el);
      if(t.length < 20 || t.length > 30000) return false;
      if(/demander des modifications|poser une question/i.test(t)) return false;
      const cs = getComputedStyle(el);
      const radius = parseFloat(cs.borderRadius || '0');
      const bg = cs.backgroundColor || '';
      const r = el.getBoundingClientRect();
      return radius >= 12 && r.width > 260 && r.height > 70 && bg !== 'rgba(0, 0, 0, 0)';
    });
    user = all[all.length - 1] || null;
  }

  if(!user) return JSON.stringify({error:'Question introuvable'});

  // 2. Les vrais pouces sont explicitement identifiés dans le diagnostic.
  const positive = [...document.querySelectorAll('button[aria-label="Donner un avis positif"], button[aria-label*="avis positif" i]')].filter(visible).pop();
  const negative = [...document.querySelectorAll('button[aria-label="Donner un avis négatif"], button[aria-label*="avis négatif" i]')].filter(visible).pop();
  const feedback = positive || negative;

  // 3. Trouver le conteneur de réponse par le bouton de feedback.
  let answer = null;
  if(feedback){
    let n = feedback.parentElement;
    while(n && n !== document.body){
      const t = txt(n);
      const hasUser = n.contains(user);
      const r = n.getBoundingClientRect();
      if(!hasUser && t.length > 100 && r.width > 250){ answer = n; break; }
      n = n.parentElement;
    }
  }

  // Secours : premier grand bloc après la question dans l'ordre du DOM.
  if(!answer){
    const candidates = [...document.querySelectorAll('main article, main section, main div')].filter(visible).filter(el => {
      if(!(user.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING)) return false;
      const t = txt(el);
      if(t.length < 100) return false;
      if(/demander des modifications|poser une question/i.test(t)) return false;
      return true;
    });
    answer = candidates[0] || null;
  }

  if(!answer) return JSON.stringify({error:'Bloc de réponse introuvable'});

  const q = clean(user);
  const a = clean(answer);
  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: txt(q),
    question_html: semanticHTML(user),
    answer: txt(a),
    answer_html: semanticHTML(answer)
  });
})()
'''


def parse(raw):
    if raw is None:
        raise ValueError("Aucun résultat JavaScript")
    data = raw if isinstance(raw, dict) else json.loads(str(raw))
    if data.get("error"):
        raise ValueError(data["error"])
    return data
