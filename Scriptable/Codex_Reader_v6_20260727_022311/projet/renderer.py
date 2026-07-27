# -*- coding: utf-8 -*-
"""Rendu HTML moderne des résultats."""

import html
import json


def _safe_fragment(fragment, fallback_text):
    fragment = fragment or ""
    if fragment.strip():
        return fragment
    return "<pre>" + html.escape(fallback_text or "") + "</pre>"


def build_result_html(question, question_html, answer, answer_html, source_url):
    q = _safe_fragment(question_html, question)
    a = _safe_fragment(answer_html, answer)
    q_json = json.dumps(question or "", ensure_ascii=False)
    a_json = json.dumps(answer or "", ensure_ascii=False)
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<style>
:root{{--bg:#f4f6fa;--card:#fff;--text:#151820;--muted:#707887;--line:#dfe4ec;--blue:#1769e0;--soft:#eef4ff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0f1217;--card:#191d24;--text:#f6f8fb;--muted:#9aa4b2;--line:#313844;--blue:#5b9cff;--soft:#202b3d}}}}
*{{box-sizing:border-box}} body{{margin:0;padding:16px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif}}
.hero{{padding:4px 2px 14px}} .hero h1{{font-size:24px;margin:0 0 5px}} .source{{font-size:12px;color:var(--muted);overflow-wrap:anywhere}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px;margin-bottom:16px;box-shadow:0 8px 24px rgba(0,0,0,.05)}}
.card-head{{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}} .label{{font-size:18px;font-weight:760}}
.content{{line-height:1.55;overflow:auto;max-height:42vh;-webkit-user-select:text;user-select:text}}
.content pre{{white-space:pre-wrap;word-break:break-word;background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:12px;overflow:auto}}
.content code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}} .content img{{max-width:100%}}
button{{width:100%;border:0;border-radius:13px;padding:13px;background:var(--blue);color:white;font-size:15px;font-weight:740;margin-top:14px}}
button:active{{transform:scale(.99)}} #status{{color:var(--muted);text-align:center;font-size:13px;min-height:24px;padding:2px}}
</style></head><body>
<div class="hero"><h1>Extraction terminée</h1><div class="source">{html.escape(source_url or '')}</div></div>
<section class="card"><div class="card-head"><div class="label">Question</div></div><div class="content">{q}</div><button onclick="copyValue(Q,'Question copiée')">Copier la question</button></section>
<section class="card"><div class="card-head"><div class="label">Réponse</div></div><div class="content">{a}</div><button onclick="copyValue(A,'Réponse copiée')">Copier la réponse</button></section>
<div id="status"></div>
<script>const Q={q_json}; const A={a_json}; async function copyValue(v,m){{try{{await navigator.clipboard.writeText(v)}}catch(e){{const t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();document.execCommand('copy');t.remove()}}document.getElementById('status').textContent=m}}</script>
</body></html>'''
