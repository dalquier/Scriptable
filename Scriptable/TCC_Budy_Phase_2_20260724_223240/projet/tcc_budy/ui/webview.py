import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

try:
    import pyto_ui as ui
except ImportError:
    ui = None


class TCCBudyWebView:
    """WebView Pyto avec bridge HTTP local et fermeture native hors WebView."""

    def __init__(self, root: Path, service, settings):
        self.root = Path(root)
        self.service = service
        self.settings = settings
        self.view = None
        self.web = None
        self.server = None
        self.server_thread = None
        self.html = self._build_html()

    def present(self):
        if ui is None:
            raise RuntimeError("Ce projet doit être lancé dans Pyto sur iOS.")
        self._start_server()
        self.view = ui.View()
        self.view.title = "TCC Budy"
        self._set_background()

        self.web = ui.WebView()
        self._set_web_frame()
        self.view.add_subview(self.web)
        if not hasattr(self.web, "load_url"):
            raise RuntimeError("Cette version de Pyto ne fournit pas WebView.load_url().")
        self.web.load_url(self.base_url)

        mode = self._presentation_mode()
        try:
            if hasattr(ui, "show_view"):
                ui.show_view(self.view, mode)
            else:
                self.view.present(mode)
        finally:
            self._stop_server()
            self.view = None
            self.web = None

    @property
    def base_url(self):
        host, port = self.server.server_address[:2]
        return f"http://{host}:{port}/"

    def _presentation_mode(self):
        modes = getattr(ui, "PresentationMode", None)
        return getattr(modes, "SHEET", None) or getattr(ui, "PRESENTATION_MODE_SHEET", None)

    def _set_background(self):
        system_colors = getattr(ui, "SystemColors", None)
        color = getattr(system_colors, "SYSTEM_BACKGROUND", None)
        if color is not None:
            self.view.background_color = color

    def _set_web_frame(self):
        resizing = getattr(ui, "AutoResizing", None)
        self.web.flex = [
            value for value in (
                getattr(resizing, "FLEXIBLE_WIDTH", None),
                getattr(resizing, "FLEXIBLE_HEIGHT", None),
            ) if value is not None
        ]
        try:
            self.web.frame = self.view.bounds
        except Exception:
            self.web.frame = (0, 0, self.view.width, self.view.height)

    def _start_server(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_GET(self):
                path = urlsplit(self.path).path
                if path not in ("/", "/index.html"):
                    return self._json({"type": "error", "message": "Ressource introuvable."}, 404)
                body = owner.html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close")
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def do_POST(self):
                if urlsplit(self.path).path != "/api":
                    return self._json({"type": "error", "message": "Route inconnue."}, 404)
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if size <= 0 or size > 1_000_000:
                        raise ValueError("Taille de commande invalide.")
                    request = json.loads(self.rfile.read(size).decode("utf-8"))
                    action = request.get("action")
                    payload = request.get("payload") or {}
                    response = owner._dispatch(action, payload)
                    self._json(response, 200)
                except Exception as exc:
                    self._json({"type": "error", "message": str(exc)}, 400)

            def _json(self, payload, status):
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close")
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *_):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def _stop_server(self):
        server = self.server
        self.server = None
        if server is None:
            return
        try:
            server.shutdown()
        finally:
            server.server_close()

    def _build_html(self):
        assets = self.root / "tcc_budy" / "ui" / "assets"
        template = (assets / "index.html").read_text(encoding="utf-8")
        css = (assets / "app.css").read_text(encoding="utf-8")
        js = (assets / "app.js").read_text(encoding="utf-8")
        return template.replace("/*__APP_CSS__*/", css).replace("/*__APP_JS__*/", js)

    def _dispatch(self, action, payload):
        if action in ("app_ready", "list_conversations"):
            return {
                "type": "initial_state",
                "conversations": self.service.list_conversations(),
                "provider": self.settings.provider_label,
                "model": self.settings.model if self.settings.provider == "openai" else "local",
            }
        if action == "create_conversation":
            return {"type": "conversation_created", "conversation": self.service.create_conversation()}
        if action == "open_conversation":
            return {"type": "conversation_loaded", **self.service.load_conversation(payload["conversation_id"])}
        if action == "send_message":
            return {"type": "message_result", **self.service.send_message(payload["conversation_id"], payload["text"], payload.get("request_id"))}
        if action == "retry_response":
            return {"type": "message_result", **self.service.retry_response(payload["conversation_id"], payload["user_message_id"])}
        if action == "delete_conversation":
            return {"type": "conversation_deleted", **self.service.delete_conversation(payload["conversation_id"])}
        raise ValueError(f"Action inconnue: {action}")
