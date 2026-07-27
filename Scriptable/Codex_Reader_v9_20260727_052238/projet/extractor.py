# -*- coding: utf-8 -*-
"""Moteur d'extraction Codex Reader v9."""

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
  const scrollables = [document.scrollingElement, ...document.querySelectorAll('*')];
  for(const el of scrollables){
    try{
      if(el && el.scrollHeight > el.clientHeight + 80){
        el.scrollTop = el.scrollHeight;
      }
    }catch(_){}
  }
  window.scrollTo(0, document.documentElement.scrollHeight);
  return JSON.stringify({prepared:true, height:document.documentElement.scrollHeight});
})()
'''


COMMON_JS = r'''
(function(){
  if(window.__codexReaderV9) return;

  const api = {};

  api.norm = function(value){
    return (value || '')
      .replace(/\r/g, '')
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  };

  api.text = function(el){
    return api.norm(el ? (el.innerText || el.textContent || '') : '');
  };

  api.rendered = function(el){
    return !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  };

  api.before = function(a, b){
    return !!(a && b && (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING));
  };

  api.findComposer = function(){
    const controls = [...document.querySelectorAll(
      'textarea,input,[contenteditable="true"],[role="textbox"],[data-testid*="composer"]'
    )];
    for(const el of controls){
      const label = [
        el.getAttribute('placeholder') || '',
        el.getAttribute('aria-label') || '',
        api.text(el)
      ].join(' ');
      if(/demander des modifications|poser une question|ask for changes/i.test(label)){
        let node = el;
        while(node && node !== document.body){
          const rect = node.getBoundingClientRect();
          if(rect.width > 250 && rect.height > 40 && rect.height < 300) return node;
          node = node.parentElement;
        }
        return el;
      }
    }
    return null;
  };

  api.findFeedback = function(){
    const items = [...document.querySelectorAll([
      '[aria-label*="avis positif" i]',
      '[aria-label*="avis négatif" i]',
      '[aria-label*="thumbs up" i]',
      '[aria-label*="thumbs down" i]'
    ].join(','))];
    return items.length ? items[items.length - 1] : null;
  };

  api.endBoundary = function(){
    return api.findFeedback() || api.findComposer() || document.body.lastElementChild;
  };

  api.findRunMarker = function(end){
    const items = [...document.querySelectorAll('div,span,p')];
    for(const el of items){
      if(end && !api.before(el, end)) continue;
      const t = api.text(el);
      if(t.length > 5 && t.length < 120 &&
         /^(exécution durant|execution took|ran for|duration)/i.test(t)){
        return el;
      }
    }
    return null;
  };

  api.isQuestionCard = function(el, limit){
    if(!api.rendered(el)) return false;
    if(limit && !api.before(el, limit)) return false;
    const t = api.text(el);
    if(t.length < 20 || t.length > 80000) return false;
    if(/demander des modifications|poser une question/i.test(t)) return false;
    const rect = el.getBoundingClientRect();
    const css = getComputedStyle(el);
    const radius = parseFloat(css.borderRadius || '0');
    const bg = css.backgroundColor || '';
    return rect.width > 240 && rect.height > 55 && radius >= 10 &&
      bg !== 'transparent' && bg !== 'rgba(0, 0, 0, 0)';
  };

  api.autoQuestion = function(){
    const end = api.endBoundary();
    const runMarker = api.findRunMarker(end);
    const limit = runMarker || end;

    let candidates = [...document.querySelectorAll(
      'div[role="button"],section[role="button"],article[role="button"]'
    )].filter(el => api.isQuestionCard(el, limit));

    if(candidates.length) return candidates[candidates.length - 1];

    candidates = [...document.querySelectorAll('div,section,article')]
      .filter(el => api.isQuestionCard(el, limit))
      .filter(el => ![...el.children].some(child => api.isQuestionCard(child, limit)));

    return candidates[candidates.length - 1] || null;
  };

  api.isNoise = function(el){
    if(!el) return true;
    if(el.closest('header,nav,form,[data-testid*="composer"]')) return true;
    const label = [
      el.getAttribute && (el.getAttribute('aria-label') || ''),
      el.getAttribute && (el.getAttribute('data-testid') || ''),
      el.className && String(el.className)
    ].join(' ');
    if(/feedback|composer|toolbar|navigation|avis positif|avis négatif|copier|partager|soumettre/i.test(label)){
      return true;
    }
    const t = api.text(el);
    if(!t || /demander des modifications|poser une question/i.test(t)) return true;
    return false;
  };

  api.cleanClone = function(source){
    const clone = source.cloneNode(true);
    clone.querySelectorAll([
      'script','style','input','textarea','form','svg','canvas','noscript',
      '[data-testid*="feedback"]','[data-testid*="composer"]',
      '[aria-label*="avis positif" i]','[aria-label*="avis négatif" i]',
      '[aria-label*="copier" i]','[aria-label*="partager" i]',
      '[aria-label*="soumettre" i]','[aria-label*="saisie vocale" i]'
    ].join(',')).forEach(el => el.remove());

    clone.querySelectorAll('button,[role="button"]').forEach(el => {
      const label = (el.getAttribute('aria-label') || '').toLowerCase();
      if(/avis positif|avis négatif|copier|partager|soumettre|saisie vocale/.test(label)){
        el.remove();
      }else{
        el.replaceWith(...el.childNodes);
      }
    });
    return clone;
  };

  api.semanticHTML = function(source){
    const allowed = new Set([
      'P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE',
      'BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A',
      'DIV','SPAN','HR','DETAILS','SUMMARY'
    ]);
    const copy = api.cleanClone(source);
    [...copy.querySelectorAll('*')].forEach(el => {
      if(!allowed.has(el.tagName)){
        el.replaceWith(...el.childNodes);
        return;
      }
      [...el.attributes].forEach(attr => {
        if(el.tagName === 'A' && attr.name === 'href') return;
        el.removeAttribute(attr.name);
      });
    });
    return copy.innerHTML;
  };

  api.isFilePanel = function(el){
    if(!api.rendered(el)) return false;
    const t = api.text(el);
    if(!/^(fichiers|files)\s*\(\d+\)/i.test(t)) return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 250 && rect.height > 100;
  };

  api.collect = function(question){
    const end = api.endBoundary();
    if(!question) return {error:'Question introuvable'};

    const qText = api.text(question);
    const qHTML = api.semanticHTML(question);
    if(!qText) return {error:'Question détectée mais vide'};

    const selector = [
      'h1','h2','h3','h4','h5','h6','p','ul','ol','pre','table','blockquote','details'
    ].join(',');

    let candidates = [...document.querySelectorAll(selector)].filter(el => {
      if(api.isNoise(el)) return false;
      if(question.contains(el)) return false;
      if(!api.before(question, el)) return false;
      if(end && !api.before(el, end)) return false;
      return api.text(el).length >= 2;
    });

    const panels = [...document.querySelectorAll('div,section,article')].filter(el => {
      if(api.isNoise(el)) return false;
      if(!api.before(question, el)) return false;
      if(end && !api.before(el, end)) return false;
      return api.isFilePanel(el);
    });

    // Les panneaux de fichiers remplacent leurs descendants atomiques.
    candidates = candidates.filter(el => !panels.some(panel => panel.contains(el)));
    candidates.push(...panels);

    candidates.sort((a, b) => {
      if(a === b) return 0;
      return api.before(a, b) ? -1 : 1;
    });

    const selected = [];
    const fingerprints = new Set();

    for(const el of candidates){
      if(selected.some(parent => parent.contains(el))) continue;
      const t = api.text(el);
      const fp = t.replace(/\s+/g, ' ').trim();
      if(!fp || fingerprints.has(fp)) continue;
      fingerprints.add(fp);
      selected.push(el);
    }

    const root = document.createElement('div');
    for(const el of selected){
      root.appendChild(api.cleanClone(el));
    }

    const answerText = api.text(root);
    const answerHTML = api.semanticHTML(root);

    if(answerText.length < 20){
      return {
        error:'Réponse reconstruite mais vide ou trop courte',
        debug:{candidateCount:candidates.length, selectedCount:selected.length, answerLength:answerText.length}
      };
    }

    return {
      url:location.href,
      title:document.title,
      question:qText,
      question_html:qHTML,
      answer:answerText,
      answer_html:answerHTML,
      debug:{
        method:'semantic-block-collector',
        candidateCount:candidates.length,
        selectedCount:selected.length,
        answerLength:answerText.length,
        questionLength:qText.length,
        boundary:api.findFeedback() ? 'feedback' : (api.findComposer() ? 'composer' : 'document-end')
      }
    };
  };

  window.__codexReaderV9 = api;
})();
'''


AUTO_EXTRACT_JS = COMMON_JS + r'''
(function(){
  const question = window.__codexReaderV9.autoQuestion();
  return JSON.stringify(window.__codexReaderV9.collect(question));
})()
'''


START_MANUAL_JS = COMMON_JS + r'''
(function(){
  const api = window.__codexReaderV9;
  window.__codexReaderSelectedQuestion = null;
  if(window.__codexReaderManualHandler){
    document.removeEventListener('click', window.__codexReaderManualHandler, true);
  }

  const handler = function(event){
    event.preventDefault();
    event.stopPropagation();

    let node = event.target;
    while(node && node !== document.body){
      const rect = node.getBoundingClientRect();
      const css = getComputedStyle(node);
      const radius = parseFloat(css.borderRadius || '0');
      if(api.text(node).length >= 20 && rect.width > 240 && rect.height > 55 && radius >= 10){
        break;
      }
      node = node.parentElement;
    }

    if(!node || node === document.body) return;
    window.__codexReaderSelectedQuestion = node;
    node.style.outline = '4px solid #0a84ff';
    node.style.outlineOffset = '3px';
    document.removeEventListener('click', handler, true);
  };

  window.__codexReaderManualHandler = handler;
  document.addEventListener('click', handler, true);
  return JSON.stringify({manual:true});
})()
'''


MANUAL_EXTRACT_JS = COMMON_JS + r'''
(function(){
  const question = window.__codexReaderSelectedQuestion;
  if(!question) return JSON.stringify({error:'Aucune question sélectionnée'});
  return JSON.stringify(window.__codexReaderV9.collect(question));
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
