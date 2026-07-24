import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

try:
    import mainthread
    import pyto_ui as ui
except ImportError:
    mainthread = None
    ui = None


class TCCBudyWebView:
    """Interface Pyto reliée à Python par un serveur HTTP local."""

    def __init__(self, root: Path, service):
        self.root = Path(root)
        self.service = service
        self.view = None
        self.web = None
        self.server = None
        self.server_thread = None
        self._closing = False
        self.html = self._build_html()

    def present(self):
        if ui is None:
            raise RuntimeError("Ce projet doit être lancé dans Pyto sur iOS.")

        self._start_server()

        self.view = ui.View()
        self.view.title = "TCC Budy"
        system_colors = getattr(ui, "SystemColors", None)
        background_color = (
            getattr(system_colors, "SYSTEM_BACKGROUND", None)
            if system_colors is not None
            else None
        )
        if background_color is not None:
            self.view.background_color = background_color

        self.web = ui.WebView()
        self._set_web_frame()
        self.view.add_subview(self.web)

        if not hasattr(self.web, "load_url"):
            self._stop_server()
            raise RuntimeError(
                "Cette version de Pyto ne fournit pas WebView.load_url()."
            )

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
            self._closing = False

    @property
    def base_url(self):
        if self.server is None:
            raise RuntimeError("Le serveur local n’est pas démarré.")
        host, port = self.server.server_address[:2]
        return f"http://{host}:{port}/"

    def _presentation_mode(self):
        mode = getattr(getattr(ui, "PresentationMode", object), "SHEET", None)
        if mode is None:
            mode = getattr(ui, "PRESENTATION_MODE_SHEET", None)
        if mode is None:
            mode = getattr(
                getattr(ui, "PresentationMode", object), "FULLSCREEN", None
            )
        if mode is None:
            mode = getattr(ui, "PRESENTATION_MODE_FULLSCREEN", None)
        return mode

    def _start_server(self):
        if self.server is not None:
            return

        owner = self

        class RequestHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_GET(self):
                path = urlsplit(self.path).path
                if path not in ("/", "/index.html"):
                    self._send_json(
                        {"type": "error", "message": "Ressource introuvable."},
                        404,
                    )
                    return

                body = owner.html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def do_POST(self):
                path = urlsplit(self.path).path
                if path != "/api":
                    self._send_json(
                        {"type": "error", "message": "Route inconnue."}, 404
                    )
                    return

                try:
                    raw_length = self.headers.get("Content-Length", "0")
                    size = int(raw_length)
                    if size <= 0 or size > 1_000_000:
                        raise ValueError("Taille de commande invalide.")

                    raw = self.rfile.read(size)
                    if not raw:
                        raise ValueError("Commande vide.")

                    request = json.loads(raw.decode("utf-8"))
                    if not isinstance(request, dict):
                        raise ValueError("La commande doit être un objet JSON.")

                    action = request.get("action")
                    if not isinstance(action, str) or not action.strip():
                        raise ValueError("Action absente.")

                    payload = request.get("payload") or {}
                    if not isinstance(payload, dict):
                        raise ValueError("Le contenu de la commande est invalide.")

                    response = owner._dispatch(action.strip(), payload)
                    self._send_json(response, 200)
                except Exception as exc:
                    self._send_json(
                        {"type": "error", "message": str(exc)}, 400
                    )

            def _send_json(self, payload, status):
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

            def log_message(self, format_string, *args):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
        self.server.daemon_threads = True
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            name="TCCBudyLocalServer",
            daemon=True,
        )
        self.server_thread.start()

    def _stop_server(self):
        server = self.server
        self.server = None
        if server is None:
            return
        try:
            server.shutdown()
        except Exception:
            pass
        try:
            server.server_close()
        except Exception:
            pass

    def _set_web_frame(self):
        auto_resizing = getattr(ui, "AutoResizing", None)
        self.web.flex = [
            value
            for value in (
                getattr(auto_resizing, "FLEXIBLE_WIDTH", None),
                getattr(auto_resizing, "FLEXIBLE_HEIGHT", None),
            )
            if value is not None
        ]
        try:
            self.web.frame = self.view.bounds
        except Exception:
            self.web.frame = (0, 0, self.view.width, self.view.height)

    def _request_close(self):
        """Ferme la vue sur le thread principal après la réponse HTTP."""
        if self._closing:
            return
        self._closing = True

        def close_view():
            view = self.view
            if view is None:
                self._closing = False
                return

            for method_name in ("close", "dismiss"):
                method = getattr(view, method_name, None)
                if callable(method):
                    try:
                        method()
                        return
                    except Exception:
                        continue

            self._closing = False

        callback = close_view
        if mainthread is not None:
            run_async = getattr(mainthread, "run_async", None)
            if callable(run_async):
                callback = run_async(close_view)

        timer = threading.Timer(0.25, callback)
        timer.daemon = True
        timer.start()

    def _build_html(self) -> str:
        assets = self.root / "tcc_budy" / "ui" / "assets"
        template = (assets / "index.html").read_text(encoding="utf-8")
        css = (assets / "app.css").read_text(encoding="utf-8")
        javascript = (assets / "app.js").read_text(encoding="utf-8")
        return template.replace("/*__APP_CSS__*/", css).replace(
            "/*__APP_JS__*/", javascript
        )

    def _dispatch(self, action, payload):
        if action in ("app_ready", "list_conversations"):
            return {
                "type": "initial_state",
                "conversations": self.service.list_conversations(),
            }
        if action == "create_conversation":
            return {
                "type": "conversation_created",
                "conversation": self.service.create_conversation(),
            }
        if action == "open_conversation":
            data = self.service.load_conversation(payload["conversation_id"])
            return {"type": "conversation_loaded", **data}
        if action == "send_message":
            data = self.service.send_message(
                payload["conversation_id"],
                payload["text"],
                payload.get("request_id"),
            )
            return {"type": "message_result", **data}
        if action == "retry_response":
            data = self.service.retry_response(
                payload["conversation_id"],
                payload["user_message_id"],
            )
            return {"type": "message_result", **data}
        if action == "delete_conversation":
            data = self.service.delete_conversation(payload["conversation_id"])
            return {"type": "conversation_deleted", **data}
        if action == "close_app":
            self._request_close()
            return {"type": "closed"}
        raise ValueError(f"Action inconnue : {action}")
