# -*- coding: utf-8 -*-
"""Extraction déterministe du dernier échange Codex."""

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

  function meaningfulQuestion(el){
    if(!visible(el)) return false;
    const t = text(el);
    if(t.length < 20 || t.length > 60000) return false;
    if(/demander des modifications|poser une question/i.test(t)) return false;
    if(/conversation|journaux|archiver la tâche|partager la tâche/i.test(t) && t.length < 200) return false;

    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const radius = parseFloat(cs.borderRadius || '0');
    const bg = cs.backgroundColor || '';

    return r.width > 240 && r.height > 60 && radius >= 10 &&
      bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
  }

  function feedbackButtons(){
    const selectors = [
      'button[aria-label="Donner un avis positif"]',
      'button[aria-label="Donner un avis négatif"]',
      'button[aria-label*="avis positif" i]',
      'button[aria-label*="avis négatif" i]',
      '[role="button"][aria-label*="avis positif" i]',
      '[role="button"][aria-label*="avis négatif" i]'
    ];
    return [...document.querySelectorAll(selectors.join(','))].filter(visible);
  }

  function commonFeedbackBar(button){
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
    // Le diagnostic réel montre que l’encadré gris est un DIV role=button.
    let candidates = [...document.querySelectorAll('div[role="button"], section[role="button"], article[role="button"]')]
      .filter(el => visible(el) && isBefore(el, feedback) && meaningfulQuestion(el));

    if(candidates.length) return candidates[candidates.length - 1];

    // Secours : dernier bloc arrondi et coloré avant la barre des pouces.
    candidates = [...document.querySelectorAll('div, section, article')]
      .filter(el => visible(el) && isBefore(el, feedback) && meaningfulQuestion(el));

    // Évite de sélectionner un parent contenant plusieurs gros blocs.
    candidates = candidates.filter(el => {
      const nested = [...el.children].filter(meaningfulQuestion);
      return nested.length === 0;
    });

    return candidates[candidates.length - 1] || null;
  }

  function removeNoise(root){
    root.querySelectorAll([
      'script','style','button','input','textarea','form','svg','canvas','noscript',
      '[role="button"]','[data-testid*="feedback"]','[data-testid*="composer"]',
      '[aria-label*="avis positif" i]','[aria-label*="avis négatif" i]',
      '[aria-label*="copier" i]','[aria-label*="partager" i]',
      '[aria-label*="fichier" i]','[aria-label*="saisie vocale" i]',
      '[aria-label*="soumettre" i]'
    ].join(',')).forEach(n => n.remove());
  }

  function semanticHTML(root){
    const allowed = new Set([
      'P','BR','H1','H2','H3','H4','H5','H6','UL','OL','LI','PRE','CODE',
      'BLOCKQUOTE','TABLE','THEAD','TBODY','TR','TH','TD','STRONG','EM','A',
      'DIV','SPAN','HR'
    ]);

    const copy = root.cloneNode(true);
    removeNoise(copy);

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

  const feedbacks = feedbackButtons();
  if(!feedbacks.length){
    return JSON.stringify({error:'Barre des pouces introuvable'});
  }

  const feedback = feedbacks[feedbacks.length - 1];
  const feedbackBar = commonFeedbackBar(feedback);
  const question = findQuestion(feedbackBar);

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

  // L’encadré est cliquable ; ce clic demande son expansion dans Codex.
  try { question.click(); } catch(_) {}

  // Extraction exacte de tout ce qui se trouve entre la question et les pouces.
  const range = document.createRange();
  range.setStartAfter(question);
  range.setEndBefore(feedbackBar);
  const fragment = range.cloneContents();
  const answerRoot = document.createElement('div');
  answerRoot.appendChild(fragment);
  removeNoise(answerRoot);

  const questionCopy = question.cloneNode(true);
  removeNoise(questionCopy);

  const questionText = text(questionCopy);
  const answerText = text(answerRoot);

  if(!questionText){
    return JSON.stringify({error:'Question détectée mais vide'});
  }
  if(!answerText || answerText.length < 20){
    return JSON.stringify({error:'Réponse extraite mais vide ou trop courte'});
  }

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: questionText,
    question_html: semanticHTML(question),
    answer: answerText,
    answer_html: semanticHTML(answerRoot),
    debug: {
      method: 'role-button-plus-dom-range',
      feedbackAria: feedback.getAttribute('aria-label') || '',
      questionTag: question.tagName,
      questionRole: question.getAttribute('role') || '',
      questionLength: questionText.length,
      answerLength: answerText.length
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
