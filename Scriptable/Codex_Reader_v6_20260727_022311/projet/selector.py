# -*- coding: utf-8 -*-
"""Sélection visuelle et extraction DOM pour ChatGPT/Codex."""

import json


INSTALL_SELECTOR_JS = r'''
(function () {
  const OLD = window.__codexReaderSelection;
  if (OLD && OLD.cleanup) OLD.cleanup();

  const state = {
    selected: null,
    clickHandler: null,
    style: null,
    cleanup: function () {
      if (this.clickHandler) document.removeEventListener('click', this.clickHandler, true);
      if (this.style) this.style.remove();
      document.querySelectorAll('[data-codex-reader-selected="1"]').forEach(el => {
        el.removeAttribute('data-codex-reader-selected');
      });
    }
  };

  const style = document.createElement('style');
  style.textContent = `
    [data-codex-reader-selected="1"] {
      outline: 4px solid #2f80ed !important;
      outline-offset: 4px !important;
      border-radius: 14px !important;
      box-shadow: 0 0 0 8px rgba(47,128,237,.18) !important;
    }
  `;
  document.documentElement.appendChild(style);
  state.style = style;

  function text(el) {
    return ((el && (el.innerText || el.textContent)) || '').trim();
  }

  function looksLikeQuestion(el) {
    const value = text(el);
    if (value.length < 2) return false;
    if (el.closest('button,nav,header,aside,textarea,input')) return false;
    return true;
  }

  function bestContainer(start) {
    let el = start;
    let best = null;
    for (let i = 0; el && i < 9; i++, el = el.parentElement) {
      if (!looksLikeQuestion(el)) continue;
      const role = el.getAttribute && el.getAttribute('data-message-author-role');
      if (role === 'user') return el;
      const cls = String(el.className || '');
      if (/user|message|group|rounded|bg-/.test(cls) && text(el).length < 20000) best = el;
      if (el.tagName === 'ARTICLE') best = el;
    }
    return best || start;
  }

  state.clickHandler = function (event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    const selected = bestContainer(event.target);
    if (state.selected) state.selected.removeAttribute('data-codex-reader-selected');
    state.selected = selected;
    selected.setAttribute('data-codex-reader-selected', '1');
    selected.scrollIntoView({behavior:'smooth', block:'center'});
  };

  document.addEventListener('click', state.clickHandler, true);
  window.__codexReaderSelection = state;
  return JSON.stringify({ok:true, message:'Touchez l’encadré gris de la question.'});
})();
'''


EXTRACT_SELECTED_JS = r'''
(function () {
  function normalize(value) {
    return (value || '').replace(/\r/g, '').replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  }
  function text(el) { return normalize(el ? (el.innerText || el.textContent || '') : ''); }
  function usefulHTML(el) {
    if (!el) return '';
    const clone = el.cloneNode(true);
    clone.querySelectorAll('button,svg,[aria-label*="Copy"],[aria-label*="copier"],script,style').forEach(x => x.remove());
    return clone.innerHTML || '';
  }
  function isFeedback(el) {
    if (!el || el.nodeType !== 1) return false;
    const aria = String(el.getAttribute('aria-label') || '').toLowerCase();
    const testid = String(el.getAttribute('data-testid') || '').toLowerCase();
    const content = text(el).toLowerCase();
    return /thumb|like|dislike|feedback|good response|bad response|pouce/.test(aria + ' ' + testid) ||
      (content.length < 180 && /copier|copy|partager|share|réessayer|retry/.test(content));
  }
  function closestMessage(el) {
    let node = el;
    for (let i = 0; node && i < 12; i++, node = node.parentElement) {
      if (node.getAttribute && node.getAttribute('data-message-author-role')) return node;
      if (node.tagName === 'ARTICLE') return node;
    }
    return el;
  }

  const selected = document.querySelector('[data-codex-reader-selected="1"]');
  if (!selected) return JSON.stringify({ok:false, error:'Aucune question sélectionnée.'});

  const questionRoot = closestMessage(selected);
  const question = text(selected);
  const questionHtml = usefulHTML(selected);

  let answerRoot = null;
  const allAssistant = [...document.querySelectorAll('[data-message-author-role="assistant"], [data-author="assistant"], main article')];
  const qRect = questionRoot.getBoundingClientRect();
  for (const candidate of allAssistant) {
    const rect = candidate.getBoundingClientRect();
    if (rect.top > qRect.top + 4 && text(candidate).length > 2) {
      answerRoot = candidate;
      break;
    }
  }

  if (!answerRoot) {
    let node = questionRoot.nextElementSibling;
    while (node) {
      if (text(node).length > 10) { answerRoot = node; break; }
      node = node.nextElementSibling;
    }
  }

  if (!answerRoot) return JSON.stringify({ok:false, error:'Réponse située sous la question introuvable.'});

  const clone = answerRoot.cloneNode(true);
  const walkers = [...clone.querySelectorAll('*')];
  for (const el of walkers) {
    if (isFeedback(el)) {
      el.remove();
    }
  }
  clone.querySelectorAll('button,script,style').forEach(x => x.remove());

  const answer = text(clone);
  const answerHtml = clone.innerHTML || '';
  const state = window.__codexReaderSelection;
  if (state && state.cleanup) state.cleanup();

  return JSON.stringify({
    ok:true,
    url:location.href,
    title:document.title,
    question:question,
    question_html:questionHtml,
    answer:answer,
    answer_html:answerHtml
  });
})();
'''


def parse_payload(raw):
    if isinstance(raw, dict):
        data = raw
    else:
        data = json.loads(raw or "{}")
    if not data.get("ok"):
        raise ValueError(data.get("error") or "Extraction impossible")
    return data
