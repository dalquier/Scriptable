# -*- coding: utf-8 -*-
"""Vue HTML moderne des résultats."""

import html
import json


def build(question, question_html, answer, answer_html, source_url):
    qh = question_html or f"<p>{html.escape(question)}</p>"
    ah = answer_html or f"<p>{html.escape(answer)}</p>"
    qj = json.dumps(question or "", ensure_ascii=False)
    aj = json.dumps(answer or "", ensure_ascii=False)
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><style>
:root{{--bg:#f2f2f7;--card:#fff;--text:#111;--muted:#6e6e73;--blue:#0a84ff;--border:#d1d1d6}}
@media(prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--text:#fff;--muted:#98989d;--border:#38383a}}}}
*{{box-sizing:border-box}}body{{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif}}h1{{font-size:30px;margin:8px 0 6px}}.sub{{color:var(--muted);margin-bottom:18px}}.card{{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:18px;margin-bottom:18px;box-shadow:0 8px 30px rgba(0,0,0,.08)}}.label{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700;margin-bottom:12px}}.content{{max-height:420px;overflow:auto;line-height:1.55;-webkit-user-select:text;user-select:text}}pre{{white-space:pre-wrap;overflow:auto;background:var(--bg);border-radius:14px;padding:14px}}code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}button{{width:100%;border:0;border-radius:15px;padding:14px;background:var(--blue);color:white;font-size:17px;font-weight:700;margin-top:14px}}.source{{font-size:12px;color:var(--muted);overflow-wrap:anywhere}}#toast{{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#30d158;color:white;padding:10px 16px;border-radius:20px;opacity:0;transition:.2s}}
</style></head><body><h1>Dernier échange</h1><div class="sub">Question et réponse prêtes à copier.</div><div class="source">{html.escape(source_url or '')}</div>
<div class="card"><div class="label">Question</div><div class="content">{qh}</div><button onclick='copyValue({qj})'>Copier la question</button></div>
<div class="card"><div class="label">Réponse</div><div class="content">{ah}</div><button onclick='copyValue({aj})'>Copier la réponse</button></div><div id="toast">Copié ✓</div>
<script>async function copyValue(v){{try{{await navigator.clipboard.writeText(v)}}catch(e){{const t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();document.execCommand('copy');t.remove()}}const x=document.getElementById('toast');x.style.opacity=1;setTimeout(()=>x.style.opacity=0,1200)}}</script></body></html>'''
