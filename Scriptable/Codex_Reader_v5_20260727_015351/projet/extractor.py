# -*- coding: utf-8 -*-
"""Extraction DOM pour les pages Codex/ChatGPT."""

import json
import re


EXTRACTION_JS = r"""
(function() {
  function norm(v) {
    return (v || '').replace(/\r/g, '')
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n').trim();
  }
  function text(el) { return norm(el ? (el.innerText || el.textContent || '') : ''); }
  function uniq(values) {
    const out = [], seen = new Set();
    for (const value of values) {
      const clean = norm(value);
      if (!clean || clean.length < 3) continue;
      const key = clean.replace(/\s+/g, ' ');
      if (seen.has(key)) continue;
      seen.add(key); out.push(clean);
    }
    return out;
  }
  function collect(selectors) {
    const values = [];
    for (const selector of selectors) {
      for (const el of document.querySelectorAll(selector)) values.push(text(el));
    }
    return uniq(values);
  }

  let users = collect([
    '[data-message-author-role="user"]',
    '[data-author="user"]',
    '[data-testid*="user-message"]',
    'article [class*="user"] [class*="markdown"]'
  ]);
  let assistants = collect([
    '[data-message-author-role="assistant"]',
    '[data-author="assistant"]',
    '[data-testid*="assistant-message"]',
    'article [class*="assistant"] [class*="markdown"]'
  ]);

  const articles = uniq([...document.querySelectorAll('main article')].map(text))
    .filter(v => v.length > 15);
  if (!users.length && articles.length) users = [articles[0]];
  if (!assistants.length && articles.length > 1) assistants = [articles[articles.length - 1]];

  if (!users.length || !assistants.length) {
    const blocks = uniq([...document.querySelectorAll(
      'main [class*="markdown"], main [class*="prose"], main [class*="message"]'
    )].map(text)).filter(v => v.length > 20);
    if (!users.length && blocks.length) users = [blocks[0]];
    if (!assistants.length && blocks.length) {
      assistants = [blocks.slice().sort((a,b) => b.length - a.length)[0]];
    }
  }

  return JSON.stringify({
    url: location.href,
    title: document.title,
    question: users.join('\n\n---\n\n'),
    answer: assistants.join('\n\n---\n\n'),
    userCount: users.length,
    assistantCount: assistants.length
  });
})();
"""


def clean_text(value):
    value = (value or "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def parse_result(raw):
    if not raw:
        raise ValueError("Le moteur JavaScript n'a renvoyé aucune donnée.")
    if isinstance(raw, dict):
        data = raw
    else:
        data = json.loads(raw)
    return {
        "url": data.get("url", ""),
        "title": data.get("title", ""),
        "question": clean_text(data.get("question", "")),
        "answer": clean_text(data.get("answer", "")),
        "user_count": int(data.get("userCount", 0) or 0),
        "assistant_count": int(data.get("assistantCount", 0) or 0),
    }
