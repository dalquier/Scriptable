from pathlib import Path

from tcc_budy.application.conversation_service import ConversationService
from tcc_budy.providers.factory import build_provider
from tcc_budy.storage.conversation_repository import ConversationRepository
from tcc_budy.storage.database import Database
from tcc_budy.storage.migrations import MigrationRunner
from tcc_budy.support.config import load_settings
from tcc_budy.support.logging_config import configure_logging
from tcc_budy.ui.webview import TCCBudyWebView


def build_app():
    root = Path(__file__).resolve().parent
    settings = load_settings(root)
    configure_logging(root / "logs")

    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    database = Database(data_dir / "tcc_budy.sqlite3")
    MigrationRunner(database, root / "migrations").apply_all()

    repository = ConversationRepository(database)
    provider = build_provider(settings)
    service = ConversationService(
        repository=repository,
        provider=provider,
        context_message_limit=settings.context_message_limit,
    )
    return TCCBudyWebView(root=root, service=service, settings=settings)


def run():
    app = build_app()
    app.present()
