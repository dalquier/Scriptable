# -*- coding: utf-8 -*-
"""Adaptateur de compatibilité pour pyto_ui.WebView."""


class JavaScriptUnavailable(RuntimeError):
    pass


class BrowserAdapter:
    def __init__(self, webview):
        self.webview = webview

    def load_url(self, url):
        self.webview.load_url(url)

    def load_html(self, content):
        self.webview.load_html(content)

    def evaluate(self, source):
        errors = []
        for name in (
            "evaluate_javascript",
            "evaluate_java_script",
            "eval_js",
            "run_javascript",
            "run_java_script",
        ):
            method = getattr(self.webview, name, None)
            if callable(method):
                try:
                    return method(source)
                except Exception as exc:
                    errors.append(f"{name}: {exc}")

        for attr_name in ("web_view", "wk_web_view", "native_view", "managed"):
            native = getattr(self.webview, attr_name, None)
            if native is None:
                continue
            for name in ("evaluate_javascript", "evaluateJavaScript", "eval_js"):
                method = getattr(native, name, None)
                if callable(method):
                    try:
                        return method(source)
                    except Exception as exc:
                        errors.append(f"{attr_name}.{name}: {exc}")

        raise JavaScriptUnavailable("; ".join(errors) or "Aucune méthode JavaScript exposée par cette version de Pyto.")
