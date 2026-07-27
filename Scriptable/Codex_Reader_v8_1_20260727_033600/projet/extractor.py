# -*- coding: utf-8 -*-
"""Extraction du dernier échange Codex depuis la page authentifiée."""

import json

CHECK_SESSION_JS = r'''
JSON.stringify({
  url: location.href,
  ready: document.readyState,
  connected: !location.pathname.includes('/auth/') &&
    !document.querySelector('a[href*="/auth/login"], button[data-testid*="login"]')
})
'''

# Étape 1 : localiser puis cliquer le dernier encadré de question.
PREPARE_LAST_EXCHANGE_JS = r'''
(function(){
  const norm = s => (s || '').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const text = el => norm(el ? (el.innerText || el.textContent || '') : '');
  const visible = el => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const before = (a,b) => !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);

  function isComposer(el){
    if(!el) return true;
    const t = text(el).toLowerCase();
    if(t.includes('demander des modifications') || t.includes('pose une question')) return true;
    if(el.matches('textarea,input,[contenteditable="true"]')) return true;
    if(el.querySelector('textarea,input,[contenteditable="true"]')) return true;
    return false;
  }

  function thumbButtons(){
    const buttons = [...document.querySelectorAll('button,[role="button"]')].filter(visible);
    const upWords = ['thumbs up','like','good response','bonne réponse','utile'];
    const downWords = ['thumbs down','dislike','bad response','mauvaise réponse','pas utile'];
    const label = b => ((b.getAttribute('aria-label') || '') + ' ' + (b.getAttribute('title') || '') + ' ' + text(b)).toLowerCase();
    let up = null, down = null;
    for(const b of buttons){
      const l = label(b);
      if(!up && upWords.some(w => l.includes(w))) up = b;
      if(!down && downWords.some(w => l.includes(w))) down = b;
    }
    if(!up || !down){
      const svgButtons = buttons.filter(b => b.querySelector('svg'));
      if(svgButtons.length >= 2){
        up = up || svgButtons[svgButtons.length - 2];
        down = down || svgButtons[svgButtons.length - 1];
      }
    }
    return {up, down};
  }

  function commonAncestor(a,b){
    if(!a || !b) return null;
    let n = a;
    while(n){
      if(n.contains(b)) return n;
      n = n.parentElement;
    }
    return null;
  }

  function answerRootFromThumbs(){
    const {up,down} = thumbButtons();
    const bar = commonAncestor(up,down) || up || down;
    if(!bar) return null;
    let n = bar;
    let best = null;
    while(n && n !== document.body){
      const t = text(n);
      if(t.length > 100 && !isComposer(n)) best = n;
      if(n.matches('[data-message-author-role="assistant"],[data-author="assistant"],article')) return n;
      n = n.parentElement;
    }
    return best;
  }

  function semanticAssistant(){
    const items = [...document.querySelectorAll('[data-message-author-role="assistant"],[data-author="assistant"],[data-testid*="assistant-message"]')].filter(visible);
    return items[items.length - 1] || null;
  }

  const answerRoot = answerRootFromThumbs() || semanticAssistant();
  if(!answerRoot) return JSON.stringify({error:'Bloc de réponse introuvable'});

  let users = [...document.querySelectorAll('[data-message-author-role="user"],[data-author="user"],[data-testid*="user-message"]')]
    .filter(visible)
    .filter(el => before(el, answerRoot) && !isComposer(el));

  let question = users[users.length - 1] || null;

  if(!question){
    const candidates = [...document.querySelectorAll('main div, main section, main article')]
      .filter(visible)
      .filter(el => before(el, answerRoot))
      .filter(el => !isComposer(el))
      .filter(el => {
        const t = text(el);
        if(t.length < 20 || t.length > 15000) return false;
        const cs = getComputedStyle(el);
        const radius = parseFloat(cs.borderRadius || '0');
        const bg = cs.backgroundColor || '';
        const hasBg = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
        const rect = el.getBoundingClientRect();
        return radius >= 12 && hasBg && rect.width > 180 && rect.height > 50;
      });

    // Garde les éléments les plus proches du bloc de réponse et évite les gros conteneurs.
    question = candidates
      .filter(el => !candidates.some(other => other !== el && el.contains(other) && text(other).length > 20))
      .pop() || candidates.pop() || null;
  }

  if(!question) return JSON.stringify({error:'Dernier encadré gris de question introuvable'});

  question.scrollIntoView({block:'center', behavior:'auto'});
  try { question.click(); } catch(e) {}

  const expandWords = ['show more','read more','expand','afficher plus','voir plus','développer'];
  const scope = question.closest('article,section,[data-message-author-role]') || question;
  const expand = [...scope.querySelectorAll('button,[role="button"]')].find(b => {
    const l = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')).toLowerCase();
    return expandWords.some(w => l.includes(w));
  });
  if(expand) try { expand.click(); } catch(e) {}

  window.__CODEX_READER_QUESTION = question;
  window.__CODEX_READER_ANSWER = answerRoot;
  return JSON.stringify({ok:true, question_preview:text(question).slice(0,180)});
})()
'''

# Étape 2 : relire les blocs après agrandissement et les nettoyer.
EXTRACT_LAST_EXCHANGE_JS = r'''
(function(){
  const norm = s => (s || '').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const text = el => norm(el ? (el.innerText || el.textContent || '') : '');
  const question = window.__CODEX_READER_QUESTION;
  const answer = window.__CODEX_READER_ANSWER;
  if(!question) return JSON.stringify({error:'Question préparée introuvable'});
  if(!answer) return JSON.stringify({error:'Réponse préparée introuvable'});

  function cleanClone(el, isAnswer){
    const clone = el.cloneNode(true);
    const selectors = [
      'script','style','textarea','input','form','nav',
      '[contenteditable="true"]','[data-testid*="feedback"]',
      '[aria-label*="thumb" i]','[aria-label*="copy" i]',
      '[aria-label*="share" i]','[aria-label*="like" i]',
      '[aria-label*="dislike" i]'
    ];
    if(isAnswer) selectors.push('button','[role="button"]');
    clone.querySelectorAll(selectors.join(',')).forEach(n => n.remove());
    return clone;
  }

  const q = cleanClone(question, false);
  const a = cleanClone(answer, true);
  const qt = text(q);
  const at = text(a);
  if(!qt) return JSON.stringify({error:'Le texte de la question est vide'});
  if(!at) return JSON.stringify({error:'Le texte de la réponse est vide'});

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: qt,
    question_html: q.innerHTML,
    answer: at,
    answer_html: a.innerHTML
  });
})()
'''


def parse_json(raw):
    if raw is None:
        raise ValueError('Aucun résultat JavaScript')
    data = raw if isinstance(raw, dict) else json.loads(str(raw))
    if data.get('error'):
        raise ValueError(data['error'])
    return data
