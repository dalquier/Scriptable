# -*- coding: utf-8 -*-
"""Adaptateur tolérant aux variantes de pyto_ui.WebView."""


class JavaScriptUnavailable(RuntimeError):
    pass


class BrowserAdapter:
    def __init__(self, webview):
        self.webview = webview

    def load_url(self, url):
        self.webview.load_url(url)

    def load_html(self, content):
        self.webview.load_html(content)

    def evaluate(self, script):
        errors = []
        for name in (
            "evaluate_javascript",
            "evaluateJavaScript",
            "eval_js",
            "run_javascript",
            "runJavaScript",
        ):
            method = getattr(self.webview, name, None)
            if callable(method):
                try:
                    return method(script)
                except Exception as exc:
                    errors.append(f"{name}: {exc}")

        native = getattr(self.webview, "__py_view__", None)
        if native is not None:
            for name in ("evaluateJavaScript_completionHandler_", "evaluateJavaScript"):
                method = getattr(native, name, None)
                if callable(method):
                    try:
                        return method(script)
                    except Exception as exc:
                        errors.append(f"native.{name}: {exc}")

        detail = "; ".join(errors[-3:]) if errors else "aucune méthode JavaScript trouvée"
        raise JavaScriptUnavailable(detail)
