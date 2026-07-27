# -*- coding: utf-8 -*-
"""Vue de résultat moderne et sûre."""

import html


def _fallback(text):
    escaped = html.escape(text or "")
    parts = [part.strip() for part in escaped.split("\n\n") if part.strip()]
    return "".join(
        f"<p>{part.replace(chr(10), '<br>')}</p>" for part in parts
    )


def build(question, question_html, answer, answer_html, source):
    q_html = question_html.strip() if question_html and question_html.strip() else _fallback(question)
    a_html = answer_html.strip() if answer_html and answer_html.strip() else _fallback(answer)
    q_text = html.escape(question or "")
    a_text = html.escape(answer or "")
    source_html = html.escape(source or "")

    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<style>
:root{{--bg:#f2f2f7;--card:#fff;--text:#111;--muted:#6e6e73;--blue:#0a84ff;--border:#d1d1d6;--code:#ececf1}}
@media(prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--text:#fff;--muted:#98989d;--border:#38383a;--code:#2c2c2e}}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:18px 18px 42px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif}}
h1{{font-size:30px;line-height:1.1;margin:8px 0 5px}}
.sub{{color:var(--muted);margin-bottom:12px}}
.source{{font-size:11px;color:var(--muted);overflow-wrap:anywhere;margin-bottom:16px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:18px;margin-bottom:18px;box-shadow:0 8px 28px rgba(0,0,0,.08)}}
.label{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700;margin-bottom:12px}}
.content{{max-height:480px;overflow:auto;line-height:1.55;-webkit-user-select:text;user-select:text}}
.content p{{margin:0 0 12px}}
.content h1,.content h2,.content h3,.content h4,.content h5,.content h6{{margin:20px 0 10px;line-height:1.2}}
.content ul,.content ol{{padding-left:24px;margin:8px 0 14px}}
.content li{{margin:5px 0}}
.content pre{{white-space:pre-wrap;overflow:auto;background:var(--code);border-radius:14px;padding:14px;font-size:13px}}
.content code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--code);padding:2px 5px;border-radius:6px}}
.content pre code{{padding:0;background:transparent}}
.content table{{width:100%;border-collapse:collapse;display:block;overflow:auto;margin:12px 0}}
.content th,.content td{{border:1px solid var(--border);padding:8px;text-align:left;vertical-align:top}}
.content details{{border:1px solid var(--border);border-radius:14px;padding:10px;margin:10px 0}}
.content summary{{font-weight:700}}
.copy{{width:100%;border:0;border-radius:15px;padding:14px;background:var(--blue);color:white;font-size:17px;font-weight:700;margin-top:14px}}
textarea{{position:fixed;left:-10000px;top:-10000px;width:1px;height:1px;opacity:0}}
#toast{{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#30d158;color:white;padding:10px 16px;border-radius:20px;opacity:0;transition:.2s}}
</style>
</head>
<body>
<h1>Dernier échange</h1>
<div class="sub">Question et réponse prêtes à copier.</div>
<div class="source">{source_html}</div>
<div class="card">
  <div class="label">Question</div>
  <div class="content">{q_html}</div>
  <textarea id="question">{q_text}</textarea>
  <button class="copy" onclick="copyText('question')">Copier la question</button>
</div>
<div class="card">
  <div class="label">Réponse</div>
  <div class="content">{a_html}</div>
  <textarea id="answer">{a_text}</textarea>
  <button class="copy" onclick="copyText('answer')">Copier la réponse</button>
</div>
<div id="toast">Copié ✓</div>
<script>
async function copyText(id){{
  const element=document.getElementById(id);
  try{{await navigator.clipboard.writeText(element.value)}}
  catch(_){{element.focus();element.select();document.execCommand('copy')}}
  const toast=document.getElementById('toast');
  toast.style.opacity='1';
  setTimeout(()=>toast.style.opacity='0',1200);
}}
</script>
</body>
</html>'''
