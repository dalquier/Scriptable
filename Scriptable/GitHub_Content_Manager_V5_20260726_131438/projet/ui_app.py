import json
import posixpath
import threading

import pyto_ui as ui

from github_api import GitHubAPIError, GitHubClient
from storage import (
    append_activity,
    load_activities,
    load_settings,
    load_token,
    save_settings,
    save_token,
)


HTML = r'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
:root{color-scheme:light dark;--bg:#f4f6fb;--card:#fff;--text:#172033;--muted:#6f7787;--line:#e4e8f0;--blue:#1867d8;--danger:#d33b3b}
@media(prefers-color-scheme:dark){:root{--bg:#10131a;--card:#191e28;--text:#f4f6fb;--muted:#9da7b7;--line:#2a3140;--blue:#68a7ff;--danger:#ff7474}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.app{min-height:100vh;padding:env(safe-area-inset-top) 14px env(safe-area-inset-bottom)}
header{position:sticky;top:0;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(16px);z-index:5;padding:10px 0}.title{font-size:22px;font-weight:800}.sub{font-size:12px;color:var(--muted);margin-top:3px;word-break:break-all}.bar{display:flex;gap:8px;margin-top:12px}.bar input{flex:1}.btn,input,textarea{border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:12px;padding:11px;font:inherit}.btn{font-weight:700}.primary{background:var(--blue);color:white;border-color:transparent}.danger{color:var(--danger)}.list{display:grid;gap:9px;padding:10px 0 88px}.item{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:13px;display:flex;gap:11px;align-items:center}.icon{font-size:25px;width:32px;text-align:center}.meta{flex:1;min-width:0}.name{font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.detail{font-size:12px;color:var(--muted);margin-top:4px}.actions{display:flex;gap:4px}.mini{border:0;background:transparent;color:var(--blue);font-size:20px;padding:5px}.fab{position:fixed;right:20px;bottom:calc(22px + env(safe-area-inset-bottom));width:58px;height:58px;border-radius:29px;border:0;background:var(--blue);color:#fff;font-size:30px;box-shadow:0 8px 28px #0005}.empty{text-align:center;color:var(--muted);padding:55px 20px}.overlay{position:fixed;inset:0;background:#0008;display:none;align-items:flex-end;z-index:20}.panel{background:var(--card);width:100%;max-height:92vh;border-radius:22px 22px 0 0;padding:18px;overflow:auto}.panel h2{margin:0 0 12px}.panel input,.panel textarea{width:100%;margin:6px 0}.panel textarea{min-height:45vh;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.row{display:flex;gap:8px}.row>*{flex:1}.toast{position:fixed;left:20px;right:20px;bottom:95px;background:#222;color:#fff;padding:12px;border-radius:12px;display:none;z-index:40;text-align:center}.tabs{display:flex;gap:8px;margin-top:10px}.tabs .btn{flex:1;padding:8px}.activity{font-size:13px;border-bottom:1px solid var(--line);padding:10px 0}.hidden{display:none!important}
</style></head><body><div class="app">
<header><div class="title">GitHub Content Manager</div><div id="context" class="sub"></div><div class="bar"><button class="btn" onclick="goUp()">←</button><input id="search" placeholder="Filtrer ce dossier" oninput="render()"><button class="btn" onclick="refresh()">↻</button><button class="btn" onclick="openSettings()">⚙︎</button></div><div class="tabs"><button class="btn" onclick="showFiles()">Fichiers</button><button class="btn" onclick="showActivity()">Journal</button></div></header>
<div id="files" class="list"></div><div id="activity" class="list hidden"></div><button class="fab" onclick="openCreate()">+</button></div>
<div id="overlay" class="overlay" onclick="if(event.target===this)closePanel()"><div id="panel" class="panel"></div></div><div id="toast" class="toast"></div>
<script>
let state={items:[],path:'',repository:'',branch:'',activities:[]};let selected=null;
function send(action,payload={}){window.location.href='pyto://'+encodeURIComponent(JSON.stringify({action,...payload}))}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function setState(s){state=s;document.getElementById('context').textContent=s.repository+' · '+s.branch+' / '+(s.path||'');render()}
function render(){let q=document.getElementById('search').value.toLowerCase();let a=state.items.filter(x=>x.name.toLowerCase().includes(q));document.getElementById('files').innerHTML=a.length?a.map(x=>`<div class="item" onclick="openItem('${encodeURIComponent(x.path)}','${x.type}')"><div class="icon">${x.type==='dir'?'📁':'📄'}</div><div class="meta"><div class="name">${esc(x.name)}</div><div class="detail">${x.type==='dir'?'Dossier':formatSize(x.size)}</div></div>${x.type==='file'?`<div class="actions"><button class="mini" onclick="event.stopPropagation();renameItem('${encodeURIComponent(x.path)}')">✎</button><button class="mini danger" onclick="event.stopPropagation();deleteItem('${encodeURIComponent(x.path)}')">⌫</button></div>`:''}</div>`).join(''):'<div class="empty">Aucun élément</div>'}
function formatSize(n){if(!n)return'0 o';if(n<1024)return n+' o';if(n<1048576)return(n/1024).toFixed(1)+' Ko';return(n/1048576).toFixed(1)+' Mo'}
function openItem(p,t){p=decodeURIComponent(p);t==='dir'?send('open_dir',{path:p}):send('open_file',{path:p})}
function refresh(){send('refresh')}function goUp(){send('up')}
function showFiles(){document.getElementById('files').classList.remove('hidden');document.getElementById('activity').classList.add('hidden')}
function showActivity(){document.getElementById('files').classList.add('hidden');let d=document.getElementById('activity');d.classList.remove('hidden');d.innerHTML=state.activities.length?state.activities.map(x=>`<div class="item"><div class="meta"><div class="name">${esc(x.action)} · ${esc(x.path)}</div><div class="detail">${esc(x.timestamp)} ${esc(x.detail||'')}</div></div></div>`).join(''):'<div class="empty">Journal vide</div>'}
function openCreate(){panel(`<h2>Créer</h2><input id="newName" placeholder="Nom ou chemin relatif"><div class="row"><button class="btn primary" onclick="createFile()">Fichier</button><button class="btn" onclick="createFolder()">Dossier</button></div><button class="btn" style="width:100%;margin-top:8px" onclick="closePanel()">Annuler</button>`)}
function createFile(){let n=document.getElementById('newName').value.trim();if(n)send('create_file',{name:n})}function createFolder(){let n=document.getElementById('newName').value.trim();if(n)send('create_folder',{name:n})}
function showEditor(f){selected=f;panel(`<h2>${esc(f.path)}</h2><textarea id="editor">${esc(f.content)}</textarea><div class="row"><button class="btn primary" onclick="saveEditor()">Enregistrer</button><button class="btn" onclick="closePanel()">Fermer</button></div>`)}
function saveEditor(){send('save_file',{path:selected.path,sha:selected.sha,content:document.getElementById('editor').value})}
function renameItem(p){p=decodeURIComponent(p);panel(`<h2>Renommer</h2><input id="renamePath" value="${esc(p)}"><div class="row"><button class="btn primary" onclick="doRename('${encodeURIComponent(p)}')">Renommer</button><button class="btn" onclick="closePanel()">Annuler</button></div>`)}
function doRename(oldp){send('rename_file',{old_path:decodeURIComponent(oldp),new_path:document.getElementById('renamePath').value.trim()})}
function deleteItem(p){p=decodeURIComponent(p);if(confirm('Supprimer définitivement '+p+' ?'))send('delete_file',{path:p})}
function openSettings(){panel(`<h2>Réglages</h2><input id="repo" placeholder="propriétaire/dépôt" value="${esc(state.repository)}"><input id="branch" placeholder="Branche" value="${esc(state.branch)}"><input id="root" placeholder="Dossier racine" value="${esc(state.root_path||'')}"><input id="token" type="password" placeholder="Jeton GitHub (laisser vide pour conserver)"><div class="row"><button class="btn primary" onclick="saveSettings()">Enregistrer</button><button class="btn" onclick="closePanel()">Annuler</button></div>`)}
function saveSettings(){send('settings',{repository:repo.value.trim(),branch:branch.value.trim(),root_path:root.value.trim(),token:token.value.trim()})}
function panel(html){document.getElementById('panel').innerHTML=html;document.getElementById('overlay').style.display='flex'}function closePanel(){document.getElementById('overlay').style.display='none'}
function toast(msg){let t=document.getElementById('toast');t.textContent=msg;t.style.display='block';setTimeout(()=>t.style.display='none',2500)}
</script></body></html>'''


class GitHubContentManagerApp:
    def __init__(self):
        self.settings = load_settings()
        self.token = load_token()
        self.current_path = self.settings.get("root_path", "").strip("/")
        self.client = None
        self.web = None
        self.root = None
        self._build_client()

    def _build_client(self):
        self.client = GitHubClient(
            self.settings["repository"],
            self.settings["branch"],
            self.token,
        )

    def run(self):
        self.root = ui.View()
        self.root.name = "GitHub Content Manager V5"
        self.web = ui.WebView(frame=(0, 0, self.root.width, self.root.height))
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.web.load_html(HTML)
        self.web.delegate = self
        self.root.add_subview(self.web)
        self.root.present("fullscreen")
        threading.Timer(0.6, self.refresh).start()

    def webview_should_start_load(self, webview, url, navigation_type):
        if not url.startswith("pyto://"):
            return True
        try:
            payload = json.loads(__import__("urllib.parse").parse.unquote(url[7:]))
            self._dispatch(payload)
        except Exception as exc:
            self._toast(str(exc))
        return False

    def _dispatch(self, data):
        action = data.get("action")
        handlers = {
            "refresh": self.refresh,
            "open_dir": lambda: self.open_dir(data["path"]),
            "open_file": lambda: self.open_file(data["path"]),
            "up": self.go_up,
            "create_file": lambda: self.create_file(data["name"]),
            "create_folder": lambda: self.create_folder(data["name"]),
            "save_file": lambda: self.save_file(data),
            "rename_file": lambda: self.rename_file(data["old_path"], data["new_path"]),
            "delete_file": lambda: self.delete_file(data["path"]),
            "settings": lambda: self.update_settings(data),
        }
        if action in handlers:
            self._background(handlers[action])

    def _background(self, fn):
        threading.Thread(target=self._safe_call, args=(fn,), daemon=True).start()

    def _safe_call(self, fn):
        try:
            fn()
        except (GitHubAPIError, ValueError, KeyError) as exc:
            self._toast(str(exc))
        except Exception as exc:
            self._toast("Erreur inattendue : " + str(exc))

    def refresh(self):
        items = self.client.list_path(self.current_path)
        state = {
            "repository": self.settings["repository"],
            "branch": self.settings["branch"],
            "root_path": self.settings.get("root_path", ""),
            "path": self.current_path,
            "items": [
                {"name": x.get("name", ""), "path": x.get("path", ""), "type": x.get("type", "file"), "size": x.get("size", 0)}
                for x in items
            ],
            "activities": load_activities(),
        }
        self._js("setState(" + json.dumps(state, ensure_ascii=False) + ")")

    def open_dir(self, path):
        self.current_path = path.strip("/")
        self.refresh()

    def go_up(self):
        root = self.settings.get("root_path", "").strip("/")
        if self.current_path == root:
            return
        parent = posixpath.dirname(self.current_path)
        if root and not (parent == root or parent.startswith(root + "/")):
            parent = root
        self.current_path = parent
        self.refresh()

    def open_file(self, path):
        file_data = self.client.get_file(path)
        self._js("showEditor(" + json.dumps(file_data, ensure_ascii=False) + ")")

    def _resolve(self, name):
        clean = name.strip().strip("/")
        if not clean or ".." in clean.split("/"):
            raise ValueError("Nom ou chemin invalide.")
        return posixpath.join(self.current_path, clean) if self.current_path else clean

    def create_file(self, name):
        path = self._resolve(name)
        self.client.put_file(path, "", f"Create {path}")
        append_activity("Création fichier", path)
        self._close_and_refresh("Fichier créé")

    def create_folder(self, name):
        path = self._resolve(name)
        self.client.create_folder(path, f"Create folder {path}")
        append_activity("Création dossier", path)
        self._close_and_refresh("Dossier créé")

    def save_file(self, data):
        path = data["path"]
        self.client.put_file(path, data.get("content", ""), f"Update {path}", data["sha"])
        append_activity("Modification", path)
        self._close_and_refresh("Fichier enregistré")

    def rename_file(self, old_path, new_path):
        new_path = new_path.strip().strip("/")
        if not new_path or ".." in new_path.split("/"):
            raise ValueError("Nouveau chemin invalide.")
        self.client.rename_file(old_path, new_path)
        append_activity("Renommage", old_path, "→ " + new_path)
        self._close_and_refresh("Fichier renommé")

    def delete_file(self, path):
        file_data = self.client.get_file(path)
        self.client.delete_file(path, file_data["sha"], f"Delete {path}")
        append_activity("Suppression", path)
        self._close_and_refresh("Fichier supprimé")

    def update_settings(self, data):
        repository = data.get("repository", "").strip()
        branch = data.get("branch", "").strip() or "main"
        if "/" not in repository:
            raise ValueError("Le dépôt doit être au format propriétaire/nom.")
        self.settings = {
            "repository": repository,
            "branch": branch,
            "root_path": data.get("root_path", "").strip().strip("/"),
        }
        token = data.get("token", "").strip()
        if token:
            self.token = token
            stored = save_token(token)
            if not stored:
                self._toast("Jeton actif pour cette session, mais keyring est indisponible.")
        save_settings(self.settings)
        self.current_path = self.settings["root_path"]
        self._build_client()
        self.client.get_repo()
        append_activity("Configuration", repository, branch)
        self._close_and_refresh("Réglages enregistrés")

    def _close_and_refresh(self, message):
        self._js("closePanel()")
        self._toast(message)
        self.refresh()

    def _toast(self, message):
        self._js("toast(" + json.dumps(message, ensure_ascii=False) + ")")

    def _js(self, script):
        if self.web is not None:
            ui.run_on_main_thread(lambda: self.web.evaluate_javascript(script))
