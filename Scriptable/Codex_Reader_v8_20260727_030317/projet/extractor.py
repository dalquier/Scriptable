# -*- coding: utf-8 -*-
"""JavaScript robuste d’analyse du dernier échange ChatGPT/Codex."""

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
  const norm = s => (s || '')
    .replace(/\r/g, '')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  const visible = el => !!el && !!(
    el.offsetWidth || el.offsetHeight || el.getClientRects().length
  );

  const text = el => norm(el ? (el.innerText || el.textContent || '') : '');
  const all = sel => [...document.querySelectorAll(sel)].filter(visible);

  function meaningful(el, min=8, max=120000){
    const value = text(el);
    return value.length >= min && value.length <= max;
  }

  function cleanClone(el){
    const clone = el.cloneNode(true);
    clone.querySelectorAll([
      'script','style','button','textarea','input','form','nav',
      '[role="button"]','[role="toolbar"]',
      '[data-testid*="feedback"]','[data-testid*="copy"]',
      '[data-testid*="share"]','[data-testid*="thumb"]',
      '[aria-label*="thumb" i]','[aria-label*="pouce" i]',
      '[aria-label*="copy" i]','[aria-label*="copier" i]',
      '[aria-label*="share" i]','[aria-label*="partager" i]',
      '[aria-label*="regenerate" i]','[aria-label*="réessayer" i]'
    ].join(',')).forEach(n => n.remove());
    return clone;
  }

  function isFeedbackControl(el){
    const value = [
      el.getAttribute('aria-label') || '',
      el.getAttribute('title') || '',
      el.getAttribute('data-testid') || '',
      el.innerText || ''
    ].join(' ').toLowerCase();

    return /thumb|pouce|like|dislike|good response|bad response|feedback/.test(value);
  }

  function findLastFeedback(){
    const controls = all('button,[role="button"],[aria-label],[data-testid]')
      .filter(isFeedbackControl);
    return controls.length ? controls[controls.length - 1] : null;
  }

  function findAssistantFromFeedback(feedback){
    if(!feedback) return null;

    let node = feedback;
    let best = null;

    for(let depth = 0; node && depth < 14; depth++, node = node.parentElement){
      if(!meaningful(node, 20)) continue;

      const value = text(node);
      const rect = node.getBoundingClientRect();
      const hasRichContent = !!node.querySelector(
        'p,h1,h2,h3,h4,h5,h6,pre,code,ul,ol,table,[class*="markdown"],[class*="prose"]'
      );
      const role = node.getAttribute('data-message-author-role') || node.getAttribute('data-author');

      if(role === 'assistant') return node;

      if(hasRichContent && rect.width > 180 && value.length > 40){
        best = node;
      }

      if(node.matches('article,main > section,[data-testid*="assistant"]') && value.length > 40){
        return node;
      }
    }

    return best;
  }

  function semanticLastUser(beforeNode){
    const users = all([
      '[data-message-author-role="user"]',
      '[data-author="user"]',
      '[data-testid*="user-message"]',
      '[data-testid*="prompt"]'
    ].join(','));

    const eligible = beforeNode
      ? users.filter(u => u.compareDocumentPosition(beforeNode) & Node.DOCUMENT_POSITION_FOLLOWING)
      : users;

    return eligible.length ? eligible[eligible.length - 1] : null;
  }

  function looksLikeComposer(el){
    if(!el) return false;
    if(el.matches('textarea,input,form')) return true;
    if(el.querySelector('textarea,input,[contenteditable="true"]')) return true;

    const value = text(el).toLowerCase();
    return value.includes('demander des modifications') ||
      value.includes('pose une question') ||
      value.includes('message chatgpt');
  }

  function looksLikeQuestionCard(el){
    if(!visible(el) || !meaningful(el, 8, 50000) || looksLikeComposer(el)) return false;

    const rect = el.getBoundingClientRect();
    if(rect.width < 140 || rect.height < 35) return false;

    const cs = getComputedStyle(el);
    const radius = parseFloat(cs.borderRadius || '0');
    const bg = cs.backgroundColor || '';
    const transparent = !bg || bg === 'transparent' || bg === 'rgba(0, 0, 0, 0)';

    if(radius < 10 || transparent) return false;

    // La bulle utilisateur est généralement plus étroite que la largeur totale.
    const viewport = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    if(rect.width > viewport * 0.98) return false;

    return true;
  }

  function findQuestionBefore(assistant){
    const semantic = semanticLastUser(assistant);
    if(semantic) return semantic;

    const candidates = all('main div, main article, main section')
      .filter(looksLikeQuestionCard)
      .filter(el => !assistant || (
        el.compareDocumentPosition(assistant) & Node.DOCUMENT_POSITION_FOLLOWING
      ));

    // Élimine les parents contenant un autre candidat : on veut la carte la plus précise.
    const leaves = candidates.filter(el =>
      !candidates.some(other => other !== el && el.contains(other))
    );

    const pool = leaves.length ? leaves : candidates;
    return pool.length ? pool[pool.length - 1] : null;
  }

  function fallbackAssistant(question){
    const assistants = all([
      '[data-message-author-role="assistant"]',
      '[data-author="assistant"]',
      '[data-testid*="assistant-message"]',
      '[data-testid*="response"]'
    ].join(','));

    if(assistants.length){
      const after = question
        ? assistants.filter(a => question.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING)
        : assistants;
      return (after.length ? after[after.length - 1] : assistants[assistants.length - 1]);
    }

    return null;
  }

  function expandQuestion(el){
    if(!el) return;
    const scope = el.closest('article,section,[data-message-author-role],[data-testid],main') || el.parentElement;
    if(!scope) return;

    const words = [
      'show more','read more','expand','afficher plus','voir plus','développer','ouvrir'
    ];

    const target = [...scope.querySelectorAll('button,[role="button"]')].find(button => {
      const value = (
        button.innerText || button.getAttribute('aria-label') || button.getAttribute('title') || ''
      ).toLowerCase();
      return words.some(word => value.includes(word));
    });

    if(target) target.click();
  }

  const feedback = findLastFeedback();
  let assistant = findAssistantFromFeedback(feedback);
  let user = findQuestionBefore(assistant);

  if(!assistant) assistant = fallbackAssistant(user);
  if(!user) user = semanticLastUser(assistant);

  if(!user){
    return JSON.stringify({
      error: 'Dernière question introuvable',
      diagnostics: {
        feedbackFound: !!feedback,
        assistantFound: !!assistant,
        url: location.href
      }
    });
  }

  expandQuestion(user);

  if(!assistant){
    assistant = fallbackAssistant(user);
  }

  if(!assistant){
    return JSON.stringify({
      error: 'Réponse associée introuvable',
      diagnostics: {
        feedbackFound: !!feedback,
        questionLength: text(user).length,
        url: location.href
      }
    });
  }

  const q = cleanClone(user);
  const a = cleanClone(assistant);

  const questionText = text(q);
  const answerText = text(a);

  if(!questionText){
    return JSON.stringify({error:'Question détectée mais vide'});
  }
  if(!answerText){
    return JSON.stringify({error:'Réponse détectée mais vide'});
  }

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: questionText,
    question_html: q.innerHTML,
    answer: answerText,
    answer_html: a.innerHTML,
    diagnostics: {
      feedbackFound: !!feedback,
      questionLength: questionText.length,
      answerLength: answerText.length
    }
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
        diagnostics = data.get("diagnostics") or {}
        suffix = f" — diagnostic: {diagnostics}" if diagnostics else ""
        raise ValueError(str(data["error"]) + suffix)

    return data
