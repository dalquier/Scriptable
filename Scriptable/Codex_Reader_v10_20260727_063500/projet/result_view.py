# -*- coding: utf-8 -*-
"""Vue HTML de résultat Codex Reader v10."""

import base64
import html


def _fallback(text):
    escaped = html.escape(text or "")
    return "<pre class='plain'>" + escaped + "</pre>"


def _b64(text):
    return base64.b64encode((text or "").encode("utf-8")).decode("ascii")


def build(question, question_html, answer, answer_html, source, debug=None):
    q_html = question_html.strip() if question_html and question_html.strip() else _fallback(question)
    a_html = answer_html.strip() if answer_html and answer_html.strip() else _fallback(answer)
    source_html = html.escape(source or "")
    q64 = _b64(question)
    a64 = _b64(answer)
    debug = debug or {}
    exchange = f"{debug.get('exchangeIndex', '?')}/{debug.get('exchangeCount', '?')}"
    length = debug.get("answerLength", len(answer or ""))

    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<style>
:root{{--bg:#f2f2f7;--card:#fff;--text:#111;--muted:#6e6e73;--blue:#0a84ff;--border:#d1d1d6;--code:#ececf1}}
@media(prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--text:#fff;--muted:#98989d;--border:#38383a;--code:#2c2c2e}}}}
*{{box-sizing:border-box}} body{{margin:0;padding:18px 18px 42px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif}}
h1{{font-size:30px;margin:8px 0 5px}} .sub,.source,.meta{{color:var(--muted)}} .source{{font-size:11px;overflow-wrap:anywhere;margin:8px 0 14px}} .meta{{font-size:12px;margin-bottom:16px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:18px;margin-bottom:18px;box-shadow:0 8px 28px rgba(0,0,0,.08)}}
.label{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700;margin-bottom:12px}}
.content{{line-height:1.55;overflow-wrap:anywhere;-webkit-user-select:text;user-select:text}} .content p{{margin:0 0 12px}} .content h1,.content h2,.content h3,.content h4{{margin:20px 0 10px;line-height:1.2}}
.content ul,.content ol{{padding-left:24px}} .content pre,.plain{{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--code);border-radius:14px;padding:14px;font-size:13px}}
.content code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}} .content table{{width:100%;border-collapse:collapse;display:block;overflow:auto;margin:12px 0}} .content th,.content td{{border:1px solid var(--border);padding:8px;text-align:left;vertical-align:top}}
.copy{{width:100%;border:0;border-radius:15px;padding:14px;background:var(--blue);color:white;font-size:17px;font-weight:700;margin-top:14px}}
#copyBuffer{{position:fixed;left:-10000px;top:-10000px;white-space:pre-wrap;user-select:text;-webkit-user-select:text}} #toast{{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#30d158;color:white;padding:10px 16px;border-radius:20px;opacity:0;transition:.2s}}
</style></head><body>
<h1>Dernier échange</h1><div class="sub">Copie intégrale du texte extrait.</div><div class="source">{source_html}</div><div class="meta">Échange {exchange} · {length} caractères</div>
<div class="card"><div class="label">Question</div><div class="content">{q_html}</div><button class="copy" onclick="copyPayload('{q64}')">Copier la question</button></div>
<div class="card"><div class="label">Réponse</div><div class="content">{a_html}</div><button class="copy" onclick="copyPayload('{a64}')">Copier la réponse complète</button></div>
<pre id="copyBuffer" aria-hidden="true"></pre><div id="toast">Copié ✓</div>
<script>
function decode64(value){{const bytes=Uint8Array.from(atob(value),c=>c.charCodeAt(0));return new TextDecoder().decode(bytes)}}
async function copyPayload(payload){{
 const text=decode64(payload);
 try{{await navigator.clipboard.writeText(text)}}catch(_){{
   const b=document.getElementById('copyBuffer');b.textContent=text;
   const r=document.createRange();r.selectNodeContents(b);const s=window.getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();b.textContent='';
 }}
 const t=document.getElementById('toast');t.style.opacity='1';setTimeout(()=>t.style.opacity='0',1200)
}}
</script></body></html>'''
