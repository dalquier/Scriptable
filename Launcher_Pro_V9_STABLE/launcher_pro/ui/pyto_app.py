"""Pyto-only user interface adapter."""

import json
import threading
from urllib.parse import unquote

import file_system
import pyto_ui as ui


HTML = r'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><style>
:root{color-scheme:light dark;--bg:#f3f5fa;--card:#fff;--text:#182033;--muted:#727a8c;--blue:#286be6;--red:#da3a42;--line:#e1e5ee}@media(prefers-color-scheme:dark){:root{--bg:#10131a;--card:#1b202b;--text:#f5f7fb;--muted:#a1a9b8;--blue:#6da3ff;--red:#ff737a;--line:#303746}}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px -apple-system,sans-serif}.app{padding:calc(env(safe-area-inset-top) + 14px) 14px 100px}.head{font-size:28px;font-weight:800}.caption{color:var(--muted);margin:4px 0 14px}.toolbar,.imports{display:flex;gap:8px;margin:9px 0}.search,.button{border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:12px;padding:11px;font:inherit}.search{width:100%}.button{font-weight:700;flex:1}.primary{background:var(--blue);color:white;border-color:transparent}.filter.active{color:var(--blue)}#list{display:grid;gap:10px;margin-top:14px}.item{display:flex;align-items:center;gap:11px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:13px}.star{font-size:23px;border:0;background:none;color:#f5a500}.info{min-width:0;flex:1}.name{font-weight:750;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail{color:var(--muted);font-size:12px;margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.run{border:0;border-radius:10px;padding:9px 12px;background:var(--blue);color:#fff;font-weight:700}.more{border:0;background:none;color:var(--muted);font-size:23px}.empty{text-align:center;color:var(--muted);padding:55px 15px}.toast{position:fixed;left:18px;right:18px;bottom:25px;background:#20232b;color:white;border-radius:13px;padding:13px;display:none;z-index:9;white-space:pre-wrap;max-height:45vh;overflow:auto}
</style></head><body><main class="app"><div class="head">Launcher Pro <span style="color:var(--blue)">V9</span></div><div class="caption">Scripts et projets Python</div><div class="imports"><button class="button primary" onclick="send('import_script')">＋ Script</button><button class="button" onclick="send('import_project')">＋ Projet</button></div><div class="toolbar"><input class="search" placeholder="Rechercher" oninput="send('search',{query:this.value})"><button id="fav" class="button filter" onclick="toggleFilter()">★</button></div><div id="list"></div></main><div id="toast" class="toast"></div><script>
let onlyFav=false,state=[];function send(action,data={}){location.href='launcher://'+encodeURIComponent(JSON.stringify({action,...data}))}function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function setItems(items){state=items;document.getElementById('list').innerHTML=items.length?items.map(x=>`<div class="item"><button class="star" onclick="send('favorite',{id:'${x.id}'})">${x.favorite?'★':'☆'}</button><div class="info"><div class="name">${esc(x.name)}</div><div class="detail">${x.kind==='project'?'Projet':'Script'} · ${esc(x.entrypoint)}</div></div><button class="run" onclick="send('run',{id:'${x.id}'})">Lancer</button><button class="more" onclick="menu('${x.id}')">•••</button></div>`).join(''):'<div class="empty">Votre bibliothèque est vide.<br>Importez un script ou un projet.</div>'}function toggleFilter(){onlyFav=!onlyFav;document.getElementById('fav').classList.toggle('active',onlyFav);send('filter',{enabled:onlyFav})}function menu(id){let item=state.find(x=>x.id===id);let action=prompt('Action : renommer ou supprimer','renommer');if(action==='renommer'){let name=prompt('Nouveau nom',item.name);if(name)send('rename',{id,name})}else if(action==='supprimer'&&confirm('Retirer « '+item.name+' » de la bibliothèque ?'))send('delete',{id})}function toast(message){let node=document.getElementById('toast');node.textContent=message;node.style.display='block';setTimeout(()=>node.style.display='none',message.length>200?8000:2600)}
</script></body></html>'''


class PytoLauncherApp:
    def __init__(self, controller):
        self.controller = controller
        self.query = ""
        self.favorites_only = False
        self.web = None
        self.view = None

    def present(self):
        self.view = ui.View()
        self.view.name = "Launcher Pro V9"
        self.web = ui.WebView(frame=(0, 0, self.view.width, self.view.height))
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.web.delegate = self
        self.web.load_html(HTML)
        self.view.add_subview(self.web)
        self.view.present("fullscreen")
        threading.Timer(0.4, self.refresh).start()

    def webview_should_start_load(self, webview, url, navigation_type):
        if not url.startswith("launcher://"):
            return True
        try:
            data = json.loads(unquote(url[len("launcher://"):]))
            self._dispatch(data)
        except Exception as exc:
            self._toast("Erreur : {}".format(exc))
        return False

    def _dispatch(self, data):
        action = data.get("action")
        if action == "search": self.query = data.get("query", ""); self.refresh()
        elif action == "filter": self.favorites_only = bool(data.get("enabled")); self.refresh()
        elif action == "import_script": self._background(self._import_script)
        elif action == "import_project": self._background(self._import_project)
        elif action == "favorite": self.controller.toggle_favorite(data["id"]); self.refresh()
        elif action == "rename": self.controller.rename(data["id"], data["name"]); self.refresh()
        elif action == "delete": self.controller.delete(data["id"]); self.refresh()
        elif action == "run": self._background(lambda: self._run(data["id"]))

    def _import_script(self):
        try:
            selected = file_system.import_file(multiple_selection=False)
        except TypeError:
            selected = file_system.import_file()
        path = self._one_path(selected)
        if path:
            item = self.controller.import_script(path)
            self._toast("{} importé".format(item.name)); self.refresh()

    def _import_project(self):
        path = self._one_path(file_system.pick_directory())
        if path:
            item = self.controller.import_project(path)
            self._toast("Projet {} importé".format(item.name)); self.refresh()

    def _run(self, item_id):
        self._toast("Exécution en cours…")
        result = self.controller.run(item_id)
        self._toast("Exécution terminée" if result.succeeded else result.error)

    def refresh(self):
        items = [dict(id=x.id, name=x.name, kind=x.kind.value, entrypoint=x.entrypoint, favorite=x.favorite)
                 for x in self.controller.items(self.query, self.favorites_only)]
        self._js("setItems({})".format(json.dumps(items, ensure_ascii=False)))

    def _background(self, callback):
        def safe():
            try: callback()
            except Exception as exc: self._toast(str(exc))
        threading.Thread(target=safe, daemon=True).start()

    @staticmethod
    def _one_path(result):
        if isinstance(result, (list, tuple)):
            result = result[0] if result else None
        return str(result) if result else None

    def _toast(self, message):
        self._js("toast({})".format(json.dumps(str(message), ensure_ascii=False)))

    def _js(self, script):
        if self.web is not None:
            ui.run_on_main_thread(lambda: self.web.evaluate_javascript(script))
