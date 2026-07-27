# -*- coding: utf-8 -*-
"""Scripts JavaScript de détection de session et d'analyse Codex."""

import json


CHECK_SESSION_JS = r"""
(function(){
  const href = location.href || '';
  const body = (document.body && document.body.innerText || '').toLowerCase();
  const loginWords = ['log in','sign in','se connecter','continuer avec apple','continue with apple'];
  const hasLoginPrompt = loginWords.some(word => body.includes(word));
  const hasAccountUI = !!document.querySelector('[data-testid*="profile"], button[aria-label*="profil" i], button[aria-label*="account" i]');
  const authRoute = href.includes('/auth/') || href.includes('/login');
  return JSON.stringify({connected: hasAccountUI || (!authRoute && !hasLoginPrompt), url: href});
})();
"""


ANALYZE_LAST_EXCHANGE_JS = r"""
(function(){
  const normalize = value => (value || '')
    .replace(/\r/g,'')
    .replace(/[ \t]+\n/g,'\n')
    .replace(/\n{3,}/g,'\n\n')
    .trim();

  const visible = el => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden';
  };

  const uniqueElements = items => [...new Set(items.filter(Boolean))];

  const userSelectors = [
    '[data-message-author-role="user"]',
    '[data-author="user"]',
    '[data-testid*="user-message"]',
    'main article'
  ];

  let userBlocks = [];
  for (const selector of userSelectors) {
    const found = [...document.querySelectorAll(selector)].filter(visible);
    if (found.length) {
      if (selector === 'main article') {
        userBlocks.push(...found.filter((_, index) => index % 2 === 0));
      } else {
        userBlocks.push(...found);
      }
    }
  }
  userBlocks = uniqueElements(userBlocks).filter(el => normalize(el.innerText).length > 2);
  if (!userBlocks.length) throw new Error('Aucune question utilisateur détectée.');

  const questionBlock = userBlocks[userBlocks.length - 1];

  // Ouvre l'encadré s'il contient un contrôle repliable.
  const expand = questionBlock.querySelector(
    'button[aria-expanded="false"], button[aria-label*="expand" i], button[aria-label*="dévelop" i], details:not([open]) summary'
  );
  if (expand) {
    try { expand.click(); } catch (_) {}
  } else {
    try { questionBlock.click(); } catch (_) {}
  }

  const questionClone = questionBlock.cloneNode(true);
  questionClone.querySelectorAll('button,svg,[role="button"],nav,footer').forEach(el => el.remove());
  const questionText = normalize(questionClone.innerText || questionBlock.innerText);
  const questionHtml = questionClone.innerHTML || '';

  // Cherche la réponse suivant la dernière question.
  const assistantSelectors = [
    '[data-message-author-role="assistant"]',
    '[data-author="assistant"]',
    '[data-testid*="assistant-message"]'
  ];
  let assistants = [];
  for (const selector of assistantSelectors) assistants.push(...document.querySelectorAll(selector));
  assistants = uniqueElements(assistants).filter(visible);

  let responseBlock = null;
  for (const candidate of assistants) {
    const relation = questionBlock.compareDocumentPosition(candidate);
    if (relation & Node.DOCUMENT_POSITION_FOLLOWING) responseBlock = candidate;
  }

  if (!responseBlock) {
    // Fallback : premier article après l'encadré question.
    const articles = [...document.querySelectorAll('main article')].filter(visible);
    const qIndex = articles.indexOf(questionBlock.closest('article') || questionBlock);
    if (qIndex >= 0 && qIndex + 1 < articles.length) responseBlock = articles[qIndex + 1];
  }
  if (!responseBlock) throw new Error('Aucune réponse située sous la dernière question.');

  const responseClone = responseBlock.cloneNode(true);

  // Supprime la zone d'actions située au niveau des pouces et les contrôles parasites.
  const actionSelectors = [
    'button[aria-label*="thumb" i]',
    'button[aria-label*="pouce" i]',
    'button[aria-label*="like" i]',
    'button[aria-label*="dislike" i]',
    'button[aria-label*="copy" i]',
    'button[aria-label*="copier" i]',
    'button[aria-label*="share" i]',
    'button[aria-label*="partager" i]',
    '[data-testid*="feedback"]',
    '[class*="feedback"]',
    'footer',
    'nav'
  ];
  responseClone.querySelectorAll(actionSelectors.join(',')).forEach(el => el.remove());

  // Supprime les groupes de boutons restant en bas du bloc.
  [...responseClone.querySelectorAll('div')].forEach(div => {
    const buttons = div.querySelectorAll(':scope > button');
    const text = normalize(div.innerText).toLowerCase();
    if (buttons.length >= 2 && text.length < 120) div.remove();
  });

  const answerText = normalize(responseClone.innerText || responseBlock.innerText);
  const answerHtml = responseClone.innerHTML || '';
  if (!answerText) throw new Error('La réponse détectée est vide.');

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: questionText,
    question_html: questionHtml,
    answer: answerText,
    answer_html: answerHtml
  });
})();
"""


def parse_json(value):
    if isinstance(value, dict):
        return value
    if not value:
        raise ValueError("Aucune donnée renvoyée par la page.")
    return json.loads(value)
