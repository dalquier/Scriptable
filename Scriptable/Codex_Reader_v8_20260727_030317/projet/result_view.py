# -*- coding: utf-8 -*-
"""Vue HTML moderne du résultat."""

import html
import json


def build_result_html(question, question_html, answer, answer_html, source_url):
    q_text = json.dumps(question or "", ensure_ascii=False)
    a_text = json.dumps(answer or "", ensure_ascii=False)
    q_html = question_html or html.escape(question or "").replace("\n", "<br>")
    a_html = answer_html or html.escape(answer or "").replace("\n", "<br>")

    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<style>
:root{{--bg:#f2f2f7;--card:#fff;--text:#111;--muted:#6e6e73;--blue:#0a84ff;--border:#e5e5ea}}
@media(prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--text:#fff;--muted:#98989d;--border:#38383a}}}}
*{{box-sizing:border-box}} body{{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif}}
.hero{{padding:8px 2px 18px}} h1{{font-size:30px;margin:0 0 5px}} .source{{font-size:12px;color:var(--muted);overflow-wrap:anywhere}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:16px;margin-bottom:18px;box-shadow:0 8px 24px rgba(0,0,0,.06)}}
.label{{font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}}
.content{{max-height:340px;overflow:auto;line-height:1.5;font-size:16px;-webkit-user-select:text;user-select:text}}
.content pre{{white-space:pre-wrap;overflow:auto;padding:12px;border-radius:12px;background:var(--bg)}}
.content code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}} .content img{{max-width:100%;height:auto}}
button{{width:100%;border:0;border-radius:14px;padding:14px;margin-top:14px;background:var(--blue);color:#fff;font-size:16px;font-weight:700}}
button.ok{{background:#34c759}} #toast{{min-height:24px;text-align:center;color:var(--muted);font-size:13px}}
</style></head><body>
<div class="hero"><h1>Dernier échange</h1><div class="source">{html.escape(source_url or '')}</div></div>
<div class="card"><div class="label">Question</div><div class="content">{q_html}</div><button id="qbtn" onclick="copyValue('q')">Copier la question</button></div>
<div class="card"><div class="label">Réponse</div><div class="content">{a_html}</div><button id="abtn" onclick="copyValue('a')">Copier la réponse</button></div>
<div id="toast"></div>
<script>
const values={{q:{q_text},a:{a_text}}};
async function copyValue(k){{const b=document.getElementById(k+'btn');try{{await navigator.clipboard.writeText(values[k]);}}catch(e){{const t=document.createElement('textarea');t.value=values[k];document.body.appendChild(t);t.select();document.execCommand('copy');t.remove();}}const old=b.textContent;b.textContent='Copié ✓';b.classList.add('ok');setTimeout(()=>{{b.textContent=old;b.classList.remove('ok')}},1200);}}
</script></body></html>'''
