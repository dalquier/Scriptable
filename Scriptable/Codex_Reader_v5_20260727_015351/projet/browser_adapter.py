# -*- coding: utf-8 -*-
"""Compatibilité WebView entre versions de Pyto."""

import threading


class JavaScriptUnavailable(RuntimeError):
    pass


class BrowserAdapter:
    """Encapsule pyto_ui.WebView et teste plusieurs API JavaScript."""

    METHOD_NAMES = (
        "evaluate_javascript",
        "evaluateJavaScript",
        "eval_js",
        "evaluate_js",
        "run_javascript",
        "runJavaScript",
    )

    def __init__(self, webview):
        self.webview = webview

    def load_url(self, url):
        return self.webview.load_url(url)

    def load_html(self, content):
        return self.webview.load_html(content)

    def capabilities(self):
        return {
            "type": type(self.webview).__name__,
            "methods": [name for name in dir(self.webview) if "javascript" in name.lower() or "js" in name.lower()],
        }

    def evaluate(self, script, timeout=20):
        errors = []
        for name in self.METHOD_NAMES:
            method = getattr(self.webview, name, None)
            if not callable(method):
                continue
            try:
                return method(script)
            except TypeError as exc:
                errors.append(f"{name}: {exc}")
            except Exception as exc:
                errors.append(f"{name}: {type(exc).__name__}: {exc}")

        native = self._native_webview()
        if native is not None:
            try:
                return self._evaluate_native(native, script, timeout)
            except Exception as exc:
                errors.append(f"WKWebView: {type(exc).__name__}: {exc}")

        details = " | ".join(errors) if errors else "aucune méthode JavaScript détectée"
        raise JavaScriptUnavailable(details)

    def _native_webview(self):
        """Cherche prudemment le WKWebView sous-jacent exposé par Pyto."""
        candidates = (
            "managed", "__py_view__", "native", "objc_instance",
            "_objc", "_view", "web_view", "wk_web_view"
        )
        for name in candidates:
            value = getattr(self.webview, name, None)
            if value is None:
                continue
            # Certains wrappers exposent directement evaluateJavaScript_completionHandler_.
            if hasattr(value, "evaluateJavaScript_completionHandler_"):
                return value
            # D'autres exposent une propriété native imbriquée.
            for nested_name in ("webView", "web_view", "view"):
                nested = getattr(value, nested_name, None)
                if nested is not None and hasattr(nested, "evaluateJavaScript_completionHandler_"):
                    return nested
        return None

    @staticmethod
    def _evaluate_native(native, script, timeout):
        event = threading.Event()
        box = {"value": None, "error": None}

        def completion(value, error):
            box["value"] = value
            box["error"] = error
            event.set()

        native.evaluateJavaScript_completionHandler_(script, completion)
        if not event.wait(timeout):
            raise TimeoutError("Délai WKWebView dépassé")
        if box["error"] is not None:
            raise RuntimeError(str(box["error"]))
        return box["value"]
