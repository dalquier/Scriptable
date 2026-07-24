from pathlib import Path

from tcc_budy.application.conversation_service import ConversationService
from tcc_budy.providers.simulator import SimulatorProvider
from tcc_budy.storage.database import Database
from tcc_budy.storage.migrations import MigrationRunner
from tcc_budy.storage.conversation_repository import ConversationRepository
from tcc_budy.ui.webview import TCCBudyWebView
from tcc_budy.support.logging_config import configure_logging


def build_app():
    root = Path(__file__).resolve().parent
    configure_logging(root / "logs")

    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    db = Database(data_dir / "tcc_budy.sqlite3")
    MigrationRunner(db, root / "migrations").apply_all()

    repository = ConversationRepository(db)
    provider = SimulatorProvider()
    service = ConversationService(repository, provider)
    return TCCBudyWebView(root=root, service=service)


def run():
    app = build_app()
    app.present()
