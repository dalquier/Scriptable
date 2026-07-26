# -*- coding: utf-8 -*-
"""Construction de la vue résultat HTML."""

import html
import re


def markdown_to_html(text):
    escaped = html.escape(text or "")
    blocks = []

    def save_block(match):
        language = match.group(1) or ""
        content = match.group(2)
        marker = f"@@CODE_{len(blocks)}@@"
        blocks.append(
            f'<pre><code class="language-{html.escape(language)}">{content}</code></pre>'
        )
        return marker

    escaped = re.sub(r"```([A-Za-z0-9_+\-]*)\n?(.*?)```", save_block, escaped, flags=re.S)
    output, list_type = [], None

    def close_list():
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    for line in escaped.splitlines():
        stripped = line.strip()
        if not stripped:
            close_list(); output.append("<div class='gap'></div>"); continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            close_list(); level = len(heading.group(1))
            output.append(f"<h{level}>{heading.group(2)}</h{level}>"); continue
        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet:
            if list_type != "ul": close_list(); list_type = "ul"; output.append("<ul>")
            output.append(f"<li>{bullet.group(1)}</li>"); continue
        numbered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if numbered:
            if list_type != "ol": close_list(); list_type = "ol"; output.append("<ol>")
            output.append(f"<li>{numbered.group(1)}</li>"); continue
        close_list(); output.append(f"<p>{stripped}</p>")
    close_list()
    rendered = "\n".join(output)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    for index, block in enumerate(blocks):
        rendered = rendered.replace(f"@@CODE_{index}@@", block)
    return rendered


def build_result_html(question, answer, source_url):
    q_html, a_html = markdown_to_html(question), markdown_to_html(answer)
    return f"""<!doctype html><html lang='fr'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1'>
<style>
:root{{color-scheme:light dark;--bg:#f3f5f8;--card:#fff;--text:#17191d;--muted:#707887;--border:#d9dee7;--secondary:#e8edf5}}
@media(prefers-color-scheme:dark){{:root{{--bg:#101216;--card:#1a1d23;--text:#f6f7f9;--muted:#9ea6b5;--border:#353b47;--secondary:#2b313c}}}}
*{{box-sizing:border-box}}body{{margin:0;padding:14px;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,sans-serif}}
.url{{color:var(--muted);font-size:12px;overflow-wrap:anywhere;margin-bottom:12px}}.card{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:14px;margin-bottom:16px}}
.title{{font-size:18px;font-weight:750;margin-bottom:10px}}.content{{max-height:360px;overflow:auto;background:var(--bg);border:1px solid var(--border);border-radius:12px;padding:13px;line-height:1.5;-webkit-user-select:text;user-select:text}}
button{{width:100%;border:0;border-radius:11px;padding:12px;margin-top:10px;background:var(--secondary);color:var(--text);font-weight:700;font-size:14px}}
pre{{padding:12px;overflow:auto;white-space:pre-wrap;word-break:break-word;border:1px solid var(--border);border-radius:10px;background:var(--card)}}code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}}p{{margin:0 0 10px}}ul,ol{{padding-left:24px}}.gap{{height:8px}}
textarea{{position:fixed;left:-10000px;top:-10000px;width:1px;height:1px;opacity:0}}#status{{min-height:22px;color:var(--muted);text-align:center;font-size:13px}}
</style></head><body>
<div class='url'>{html.escape(source_url)}</div>
<div class='card'><div class='title'>Question</div><div class='content'>{q_html}</div><textarea id='question'>{html.escape(question)}</textarea><button onclick="copyText('question','Question copiée')">Copier toute la question</button></div>
<div class='card'><div class='title'>Réponse Codex</div><div class='content'>{a_html}</div><textarea id='answer'>{html.escape(answer)}</textarea><button onclick="copyText('answer','Réponse copiée')">Copier toute la réponse</button></div><div id='status'></div>
<script>async function copyText(id,message){{const e=document.getElementById(id);try{{await navigator.clipboard.writeText(e.value)}}catch(x){{e.focus();e.select();document.execCommand('copy')}}document.getElementById('status').textContent=message+'.'}}</script>
</body></html>"""
