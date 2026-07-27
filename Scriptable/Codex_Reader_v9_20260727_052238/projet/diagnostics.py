# -*- coding: utf-8 -*-
"""Diagnostic DOM pour Codex Reader v9."""

import json
from datetime import datetime

from storage import save_diagnostic


DIAGNOSTIC_JS = r'''
(function(){
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const visible = el => !!el && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const items = [...document.querySelectorAll(
    'h1,h2,h3,h4,h5,h6,p,ul,ol,pre,table,blockquote,details,div[role="button"],section[role="button"]'
  )].filter(visible).slice(-250).map((el,index) => {
    const rect = el.getBoundingClientRect();
    const css = getComputedStyle(el);
    return {
      index:index,
      tag:el.tagName,
      role:el.getAttribute('role') || '',
      aria:el.getAttribute('aria-label') || '',
      text:norm(el.innerText || el.textContent || '').slice(0,500),
      rect:{x:rect.x,y:rect.y,w:rect.width,h:rect.height},
      background:css.backgroundColor || '',
      radius:css.borderRadius || '',
      className:String(el.className || '').slice(0,300)
    };
  });
  return JSON.stringify({
    url:location.href,
    title:document.title,
    ready:document.readyState,
    items:items,
    html:document.documentElement.outerHTML
  });
})()
'''


def save_from_webview(webview):
    raw = webview.evaluate_js(DIAGNOSTIC_JS)
    data = raw if isinstance(raw, dict) else json.loads(str(raw))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_content = data.pop("html", "")
    json_path = save_diagnostic(
        f"diagnostic_{stamp}.json",
        json.dumps(data, ensure_ascii=False, indent=2),
    )
    html_path = save_diagnostic(f"page_{stamp}.html", html_content)
    return json_path, html_path
