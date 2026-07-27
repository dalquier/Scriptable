# -*- coding: utf-8 -*-
"""Extraction du dernier échange Codex — v8.4."""

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
  const norm = s => (s || '')
    .replace(/\r/g, '')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  const visible = el => !!el && !!(
    el.offsetWidth || el.offsetHeight || el.getClientRects().length
  );

  const text = el => norm(el ? (el.innerText || el.textContent || '') : '');

  function isBefore(a, b){
    return !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);
  }

  function isQuestionCandidate(el){
    if(!visible(el)) return false;
    const t = text(el);
    if(t.length < 20 || t.length > 60000) return false;
    if(/demander des modifications|poser une question/i.test(t)) return false;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const radius = parseFloat(cs.borderRadius || '0');
    const bg = cs.backgroundColor || '';
    return r.width > 240 && r.height > 60 && radius >= 10 &&
      bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
  }

  function findFeedback(){
    const selectors = [
      'button[aria-label="Donner un avis positif"]',
      'button[aria-label="Donner un avis négatif"]',
      'button[aria-label*="avis positif" i]',
      'button[aria-label*="avis négatif" i]',
      '[role="button"][aria-label*="avis positif" i]',
      '[role="button"][aria-label*="avis négatif" i]'
    ];
    const items = [...document.querySelectorAll(selectors.join(','))].filter(visible);
    return items[items.length - 1] || null;
  }

  function feedbackBar(button){
    let n = button;
    while(n && n !== document.body){
      const count = n.querySelectorAll(
        'button[aria-label*="avis positif" i],button[aria-label*="avis négatif" i],' +
        '[role="button"][aria-label*="avis positif" i],[role="button"][aria-label*="avis négatif" i]'
      ).length;
      const r = n.getBoundingClientRect();
      if(count >= 2 && r.height < 140) return n;
      n = n.parentElement;
    }
    return button.parentElement || button;
  }

  function findQuestion(feedback){
    let candidates = [...document.querySelectorAll('div[role="button"],section[role="button"],article[role="button"]')]
      .filter(el => visible(el) && isBefore(el, feedback) && isQuestionCandidate(el));

    if(candidates.length) return candidates[candidates.length - 1];

    candidates = [...document.querySelectorAll('div,section,article')]
      .filter(el => visible(el) && isBefore(el, feedback) && isQuestionCandidate(el));

    candidates = candidates.filter(el => {
      const nested = [...el.children].filter(isQuestionCandidate);
      return nested.length === 0;
    });

    return candidates[candidates.length - 1] || null;
  }

  function removeControls(root){
    root.querySelectorAll([
      'script','style','input','textarea','form','svg','canvas','noscript',
      'button[aria-label*="avis positif" i]','button[aria-label*="avis négatif" i]',
      'button[aria-label*="copier" i]','button[aria-label*="partager" i]',
      'button[aria-label*="fichier" i]','button[aria-label*="saisie vocale" i]',
      'button[aria-label*="soumettre" i]',
      '[data-testid*="feedback"]','[data-testid*="composer"]'
    ].join(',')).forEach(n => n.remove());
  }

  function unwrapInteractive(root){
    // Conserve le contenu textuel des wrappers interactifs au lieu de les supprimer.
    root.querySelectorAll('[role="button"],button').forEach(el => {
      el.replaceWith(...el.childNodes);
    });
  }

  function semanticHTML(root){
    const allowed = new Set([
      'P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE',
      'BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A',
      'DIV','SPAN','HR'
    ]);

    const copy = root.cloneNode(true);
    removeControls(copy);
    unwrapInteractive(copy);

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
  }

  const feedback = findFeedback();
  if(!feedback) return JSON.stringify({error:'Barre des pouces introuvable'});

  const bar = feedbackBar(feedback);
  const question = findQuestion(bar);
  if(!question){
    return JSON.stringify({
      error:'Question introuvable',
      debug:{
        feedbackAria: feedback.getAttribute('aria-label') || '',
        roleButtons: document.querySelectorAll('[role="button"]').length,
        visibleRoleButtons: [...document.querySelectorAll('[role="button"]')].filter(visible).length
      }
    });
  }

  // Capture avant le clic et avant nettoyage : évite le cas « détectée mais vide ».
  const rawQuestionText = text(question);
  const rawQuestionHTML = semanticHTML(question);

  try { question.click(); } catch(_) {}

  const range = document.createRange();
  range.setStartAfter(question);
  range.setEndBefore(bar);
  const fragment = range.cloneContents();
  const answerRoot = document.createElement('div');
  answerRoot.appendChild(fragment);
  removeControls(answerRoot);
  unwrapInteractive(answerRoot);

  const answerText = text(answerRoot);
  const answerHTML = semanticHTML(answerRoot);

  if(!rawQuestionText){
    return JSON.stringify({
      error:'Question détectée mais vide',
      debug:{
        questionTag: question.tagName,
        questionRole: question.getAttribute('role') || '',
        questionOuterHTML: (question.outerHTML || '').slice(0, 1000)
      }
    });
  }

  if(!answerText || answerText.length < 20){
    return JSON.stringify({
      error:'Réponse extraite mais vide ou trop courte',
      debug:{answerLength: answerText.length}
    });
  }

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: rawQuestionText,
    question_html: rawQuestionHTML,
    answer: answerText,
    answer_html: answerHTML,
    debug:{
      method:'capture-before-click-plus-dom-range',
      questionLength: rawQuestionText.length,
      answerLength: answerText.length,
      questionRole: question.getAttribute('role') || ''
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
