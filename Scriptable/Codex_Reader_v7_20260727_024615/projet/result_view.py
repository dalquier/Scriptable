# -*- coding: utf-8 -*-
"""Vue résultat moderne de Codex Reader v7."""

import html
import json


def _safe_html(fragment, fallback_text):
    fragment = (fragment or '').strip()
    if fragment:
        return fragment
    return '<p>' + html.escape(fallback_text or '') + '</p>'


def build_result_html(question, question_html, answer, answer_html, source_url):
    q_html = _safe_html(question_html, question)
    a_html = _safe_html(answer_html, answer)
    q_json = json.dumps(question or '', ensure_ascii=False)
    a_json = json.dumps(answer or '', ensure_ascii=False)

    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<style>
:root {{ color-scheme: light dark; --bg:#f2f2f7; --card:#fff; --text:#111; --muted:#6e6e73; --line:#e5e5ea; --blue:#007aff; --green:#34c759; }}
@media(prefers-color-scheme:dark) {{ :root {{ --bg:#000; --card:#1c1c1e; --text:#fff; --muted:#98989d; --line:#38383a; --blue:#0a84ff; --green:#30d158; }} }}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif;padding:18px 14px 34px}}
.hero{{padding:8px 4px 18px}} .eyebrow{{font-size:13px;color:var(--blue);font-weight:700}} h1{{font-size:30px;line-height:1.08;margin:5px 0 7px}} .source{{font-size:12px;color:var(--muted);overflow-wrap:anywhere}}
.card{{background:var(--card);border-radius:22px;padding:16px;margin-bottom:18px;box-shadow:0 8px 28px rgba(0,0,0,.07)}}
.card-head{{display:flex;align-items:center;gap:10px;margin-bottom:12px}} .badge{{width:32px;height:32px;border-radius:10px;background:rgba(0,122,255,.12);display:grid;place-items:center;font-weight:800;color:var(--blue)}} .title{{font-weight:760;font-size:18px}}
.content{{font-size:16px;line-height:1.55;max-height:430px;overflow:auto;-webkit-user-select:text;user-select:text}} .content pre{{overflow:auto;background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:13px;white-space:pre-wrap;word-break:break-word}} .content code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}} .content img{{max-width:100%;height:auto}} .content table{{display:block;overflow:auto;border-collapse:collapse}} .content td,.content th{{border:1px solid var(--line);padding:8px}}
.copy{{width:100%;border:0;border-radius:14px;margin-top:14px;padding:14px 16px;background:var(--blue);color:white;font-size:16px;font-weight:750}} .copy.ok{{background:var(--green)}} #toast{{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:rgba(28,28,30,.92);color:white;padding:10px 16px;border-radius:20px;font-size:13px;opacity:0;transition:.2s;pointer-events:none}} #toast.show{{opacity:1}}
</style>
</head>
<body>
<section class="hero"><div class="eyebrow">ANALYSE TERMINÉE</div><h1>Dernier échange</h1><div class="source">{html.escape(source_url or '')}</div></section>
<section class="card"><div class="card-head"><div class="badge">Q</div><div class="title">Question</div></div><div class="content">{q_html}</div><button class="copy" onclick="copyValue(this, questionText, 'Question copiée')">Copier la question</button></section>
<section class="card"><div class="card-head"><div class="badge">R</div><div class="title">Réponse</div></div><div class="content">{a_html}</div><button class="copy" onclick="copyValue(this, answerText, 'Réponse copiée')">Copier la réponse</button></section>
<div id="toast"></div>
<script>
const questionText={q_json}; const answerText={a_json};
async function copyValue(button,value,message){{try{{await navigator.clipboard.writeText(value)}}catch(e){{const t=document.createElement('textarea');t.value=value;document.body.appendChild(t);t.select();document.execCommand('copy');t.remove()}}button.classList.add('ok');button.textContent='Copié ✓';const toast=document.getElementById('toast');toast.textContent=message;toast.classList.add('show');setTimeout(()=>{{button.classList.remove('ok');button.textContent=message.includes('Question')?'Copier la question':'Copier la réponse';toast.classList.remove('show')}},1300)}}
</script>
</body></html>'''
