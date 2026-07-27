# -*- coding: utf-8 -*-
"""Vue HTML moderne des résultats."""

import html
import json


def _safe_fragment(fragment, fallback_text):
    fragment = fragment or ""
    if fragment.strip():
        return fragment
    return "<p>" + html.escape(fallback_text or "") + "</p>"


def build_result_html(question, question_html, answer, answer_html, source_url):
    q = _safe_fragment(question_html, question)
    a = _safe_fragment(answer_html, answer)
    q_js = json.dumps(question or "", ensure_ascii=False)
    a_js = json.dumps(answer or "", ensure_ascii=False)

    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<style>
:root {{ color-scheme: light dark; --bg:#f2f2f7; --card:#fff; --text:#111; --muted:#6e6e73; --line:#d1d1d6; --blue:#0a84ff; --green:#30d158; }}
@media(prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--text:#fff;--muted:#98989d;--line:#38383a;--blue:#0a84ff;--green:#30d158;}}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif}}
.header{{margin:2px 2px 18px}}
.header h1{{font-size:28px;line-height:1.1;margin:0 0 6px}}
.header p{{margin:0;color:var(--muted);font-size:14px;overflow-wrap:anywhere}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:16px;margin-bottom:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}}
.label{{font-size:13px;color:var(--muted);font-weight:700;letter-spacing:.02em;text-transform:uppercase;margin-bottom:10px}}
.content{{max-height:44vh;overflow:auto;font-size:16px;line-height:1.52;-webkit-user-select:text;user-select:text}}
.content h1,.content h2,.content h3{{line-height:1.18}}
.content pre{{overflow:auto;white-space:pre-wrap;word-break:break-word;background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:12px}}
.content code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}}
.content table{{display:block;overflow:auto;border-collapse:collapse}}
.content td,.content th{{border:1px solid var(--line);padding:7px}}
.content img{{max-width:100%;height:auto}}
.copy{{width:100%;margin-top:14px;border:0;border-radius:14px;padding:13px;background:var(--blue);color:white;font-size:16px;font-weight:750}}
.copy.done{{background:var(--green);color:#000}}
.footer{{text-align:center;color:var(--muted);font-size:12px;padding:2px 0 12px}}
</style>
</head>
<body>
<div class="header"><h1>Dernier échange</h1><p>{html.escape(source_url or '')}</p></div>
<section class="card"><div class="label">Question</div><div class="content">{q}</div><button class="copy" onclick="copyBlock(this,'question')">Copier la question</button></section>
<section class="card"><div class="label">Réponse</div><div class="content">{a}</div><button class="copy" onclick="copyBlock(this,'answer')">Copier la réponse</button></section>
<div class="footer">Codex Reader v8.1</div>
<script>
const values={{question:{q_js},answer:{a_js}}};
async function copyBlock(button,key){{
  const value=values[key]||'';
  try{{await navigator.clipboard.writeText(value)}}catch(e){{
    const t=document.createElement('textarea');t.value=value;document.body.appendChild(t);t.select();document.execCommand('copy');t.remove();
  }}
  const old=button.textContent;button.textContent='Copié ✓';button.classList.add('done');
  setTimeout(()=>{{button.textContent=old;button.classList.remove('done')}},1300);
}}
</script>
</body></html>'''
