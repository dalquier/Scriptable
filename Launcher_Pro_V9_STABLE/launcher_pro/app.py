"""Application composition root."""

from pathlib import Path

from launcher_pro.controller import LibraryController
from launcher_pro.registry import LibraryRegistry
from launcher_pro.services import ImportService


def application_directory() -> Path:
    documents = Path.home() / "Documents"
    base = documents if documents.is_dir() else Path.home()
    return base / "Launcher Pro V9"


def main() -> None:
    try:
        from launcher_pro.ui.pyto_app import PytoLauncherApp
    except ImportError as exc:
        raise RuntimeError("Launcher Pro V9 doit être lancé dans Pyto.") from exc
    directory = application_directory()
    controller = LibraryController(
        LibraryRegistry(directory / "library.json"),
        importer=ImportService(storage_root=directory / "library"),
    )
    PytoLauncherApp(controller).present()
