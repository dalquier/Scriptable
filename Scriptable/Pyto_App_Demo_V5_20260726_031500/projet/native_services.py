from __future__ import annotations

import json
from typing import Optional

import mainthread
from Foundation import NSURL
from UIKit import (
    UIApplication,
    UIAlertAction,
    UIAlertController,
    UIActivityViewController,
)


class NativeServices:
    """Pont minimal vers les fonctions natives iOS."""

    @staticmethod
    def _top_view_controller():
        application = UIApplication.sharedApplication
        window = application.keyWindow
        controller = window.rootViewController if window is not None else None

        while controller is not None:
            presented = controller.presentedViewController
            if presented is None:
                break
            controller = presented
        return controller

    @classmethod
    @mainthread.run_sync
    def show_alert(cls, title: str, message: str) -> None:
        controller = cls._top_view_controller()
        if controller is None:
            raise RuntimeError("Aucun contrôleur iOS actif.")

        alert = UIAlertController.alertControllerWithTitle_message_preferredStyle_(
            str(title), str(message), 1
        )
        action = UIAlertAction.actionWithTitle_style_handler_("OK", 0, None)
        alert.addAction_(action)
        controller.presentViewController_animated_completion_(alert, True, None)

    @classmethod
    @mainthread.run_sync
    def share_text(cls, text: str, source_view=None) -> None:
        controller = cls._top_view_controller()
        if controller is None:
            raise RuntimeError("Aucun contrôleur iOS actif.")

        activity = UIActivityViewController.alloc().initWithActivityItems_applicationActivities_(
            [str(text)], None
        )

        popover = activity.popoverPresentationController
        if popover is not None:
            popover.sourceView = source_view or controller.view
            popover.sourceRect = (0, 0, 1, 1)

        controller.presentViewController_animated_completion_(activity, True, None)

    @classmethod
    @mainthread.run_sync
    def open_url(cls, url: str) -> bool:
        ns_url = NSURL.URLWithString_(str(url))
        if ns_url is None:
            return False
        application = UIApplication.sharedApplication
        return bool(application.openURL_options_completionHandler_(ns_url, {}, None))

    @staticmethod
    def make_share_summary(state: dict) -> str:
        return (
            "Pyto App Demo V5\n\n"
            f"Ouvertures : {state.get('launch_count', 0)}\n"
            f"Actions : {state.get('action_count', 0)}\n"
            f"Utilisateur : {state.get('display_name', 'Damien')}\n\n"
            "Interface hybride Python + WKWebView + UIKit."
        )
