# -*- coding: utf-8 -*-
"""Extraction Codex v8.6 : collecte des blocs frères entre question et borne basse."""

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
  const nodes = [document.scrollingElement, ...document.querySelectorAll('*')];
  nodes.forEach(el => {
    try {
      if(el && el.scrollHeight > el.clientHeight + 80){ el.scrollTop = el.scrollHeight; }
    } catch(_) {}
  });
  window.scrollTo(0, document.documentElement.scrollHeight);
  return JSON.stringify({prepared:true});
})()
'''

EXTRACT_JS = r'''
(function(){
  const norm = s => (s || '').replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  const text = el => norm(el ? (el.innerText || el.textContent || '') : '');
  const rendered = el => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const before = (a,b) => !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);

  function feedbackButtons(){
    return [...document.querySelectorAll([
      'button[aria-label="Donner un avis positif"]',
      'button[aria-label="Donner un avis négatif"]',
      'button[aria-label*="avis positif" i]',
      'button[aria-label*="avis négatif" i]',
      '[role="button"][aria-label*="avis positif" i]',
      '[role="button"][aria-label*="avis négatif" i]'
    ].join(','))];
  }

  function feedbackBar(button){
    let node = button;
    while(node && node !== document.body){
      const count = node.querySelectorAll('[aria-label*="avis positif" i],[aria-label*="avis négatif" i]').length;
      const rect = node.getBoundingClientRect();
      if(count >= 2 && rect.height < 180) return node;
      node = node.parentElement;
    }
    return button.parentElement || button;
  }

  function findComposer(){
    const controls = [...document.querySelectorAll('textarea,input,[contenteditable="true"],[role="textbox"],[data-testid*="composer"]')];
    for(const el of controls){
      const label = [el.getAttribute('placeholder') || '', el.getAttribute('aria-label') || '', text(el)].join(' ');
      if(/demander des modifications|poser une question|ask for changes/i.test(label)){
        let node = el;
        while(node && node !== document.body){
          const rect = node.getBoundingClientRect();
          if(rect.width > 250 && rect.height > 45 && rect.height < 280) return node;
          node = node.parentElement;
        }
        return el;
      }
    }
    return null;
  }

  function isQuestion(el, endBoundary){
    if(!el || !before(el,endBoundary)) return false;
    const t = text(el);
    if(t.length < 20 || t.length > 70000) return false;
    if(/demander des modifications|poser une question/i.test(t)) return false;
    const rect = el.getBoundingClientRect();
    const css = getComputedStyle(el);
    const radius = parseFloat(css.borderRadius || '0');
    const bg = css.backgroundColor || '';
    return rect.width > 240 && rect.height > 60 && radius >= 10 && bg !== 'transparent' && bg !== 'rgba(0, 0, 0, 0)';
  }

  function findQuestion(endBoundary){
    let candidates = [...document.querySelectorAll('div[role="button"],section[role="button"],article[role="button"]')]
      .filter(el => isQuestion(el,endBoundary));
    if(candidates.length) return candidates[candidates.length - 1];
    candidates = [...document.querySelectorAll('div,section,article')]
      .filter(el => isQuestion(el,endBoundary))
      .filter(el => ![...el.children].some(child => isQuestion(child,endBoundary)));
    return candidates[candidates.length - 1] || null;
  }

  function removeControls(root){
    root.querySelectorAll([
      'script','style','input','textarea','form','svg','canvas','noscript',
      '[data-testid*="feedback"]','[data-testid*="composer"]',
      '[aria-label*="avis positif" i]','[aria-label*="avis négatif" i]',
      '[aria-label*="copier" i]','[aria-label*="partager" i]',
      '[aria-label*="fichier" i]','[aria-label*="saisie vocale" i]',
      '[aria-label*="soumettre" i]'
    ].join(',')).forEach(el => el.remove());
  }

  function unwrapInteractive(root){
    root.querySelectorAll('[role="button"],button').forEach(el => {
      const label = (el.getAttribute('aria-label') || '').toLowerCase();
      if(/avis positif|avis négatif|copier|partager|soumettre|saisie vocale|fichier/.test(label)) el.remove();
      else el.replaceWith(...el.childNodes);
    });
  }

  function semanticHTML(root){
    const allowed = new Set(['P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE','BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A','DIV','SPAN','HR','DETAILS','SUMMARY']);
    const copy = root.cloneNode(true);
    removeControls(copy);
    unwrapInteractive(copy);
    [...copy.querySelectorAll('*')].forEach(el => {
      if(!allowed.has(el.tagName)) { el.replaceWith(...el.childNodes); return; }
      [...el.attributes].forEach(attr => {
        if(el.tagName === 'A' && attr.name === 'href') return;
        el.removeAttribute(attr.name);
      });
    });
    return copy.innerHTML;
  }

  function ancestorChain(el){
    const out = [];
    let n = el;
    while(n){ out.push(n); n = n.parentElement; }
    return out;
  }

  function commonAncestor(a,b){
    const bSet = new Set(ancestorChain(b));
    return ancestorChain(a).find(n => bSet.has(n)) || document.body;
  }

  function directChildUnder(node, ancestor){
    let current = node;
    while(current && current.parentElement !== ancestor){ current = current.parentElement; }
    return current;
  }

  function siblingFragment(question, endBoundary){
    const common = commonAncestor(question, endBoundary);
    const startChild = directChildUnder(question, common);
    const endChild = directChildUnder(endBoundary, common);
    const root = document.createElement('div');

    if(startChild && endChild && startChild !== endChild){
      let n = startChild.nextElementSibling;
      while(n && n !== endChild){
        root.appendChild(n.cloneNode(true));
        n = n.nextElementSibling;
      }
    }

    if(text(root).length >= 20) return {root, method:'siblings'};

    const range = document.createRange();
    range.setStartAfter(question);
    range.setEndBefore(endBoundary);
    root.appendChild(range.cloneContents());
    return {root, method:'range-fallback'};
  }

  const feedbacks = feedbackButtons();
  const lastFeedback = feedbacks.length ? feedbacks[feedbacks.length - 1] : null;
  const composer = findComposer();
  const endBoundary = lastFeedback ? feedbackBar(lastFeedback) : composer;

  if(!endBoundary){
    return JSON.stringify({error:'Ni barre des pouces ni compositeur détecté',debug:{feedbackCount:feedbacks.length,composerFound:!!composer}});
  }

  const question = findQuestion(endBoundary);
  if(!question){
    return JSON.stringify({error:'Question introuvable',debug:{feedbackCount:feedbacks.length,composerFound:!!composer,roleButtons:document.querySelectorAll('[role="button"]').length}});
  }

  const questionText = text(question);
  const questionHTML = semanticHTML(question);
  try { question.click(); } catch(_) {}

  const extracted = siblingFragment(question,endBoundary);
  const answerRoot = extracted.root;
  removeControls(answerRoot);
  unwrapInteractive(answerRoot);

  const answerText = text(answerRoot);
  const answerHTML = semanticHTML(answerRoot);

  if(!questionText) return JSON.stringify({error:'Question détectée mais vide'});
  if(!answerText || answerText.length < 20){
    return JSON.stringify({
      error:'Réponse extraite mais vide ou trop courte',
      debug:{
        answerLength:answerText.length,
        boundary:lastFeedback ? 'feedback' : 'composer',
        method:extracted.method,
        commonTag:commonAncestor(question,endBoundary).tagName
      }
    });
  }

  return JSON.stringify({
    url:location.href,
    title:document.title,
    question:questionText,
    question_html:questionHTML,
    answer:answerText,
    answer_html:answerHTML,
    debug:{
      method:extracted.method,
      boundary:lastFeedback ? 'feedback' : 'composer',
      feedbackCount:feedbacks.length,
      questionLength:questionText.length,
      answerLength:answerText.length
    }
  });
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
