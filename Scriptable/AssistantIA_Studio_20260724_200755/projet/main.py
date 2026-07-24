"""Point d'entrée d'AssistantIA Studio.

Cette première version propose un mode console fiable. L'interface Pyto native
sera branchée ensuite sur la classe ``AssistantIAApp`` sans modifier le cœur
métier.
"""

from __future__ import annotations

import sys
import traceback

from api_client import OpenAIClientError
from app import AssistantIAApp
from config import APP_NAME, APP_VERSION


HELP_TEXT = """
Commandes disponibles :
  /new             créer une nouvelle conversation
  /list            afficher les conversations récentes
  /use <id>        ouvrir une conversation
  /web on|off      activer ou désactiver la recherche Web
  /help            afficher cette aide
  /quit            quitter
""".strip()


def print_banner() -> None:
    print(f"\n{APP_NAME} — version {APP_VERSION}")
    print("Assistant OpenAI local pour Pyto")
    print("Tapez /help pour afficher les commandes.\n")


def run_console() -> None:
    print_banner()
    web_search_enabled = False

    with AssistantIAApp() as app:
        conversation = app.start()
        print(f"Conversation : {conversation.get('title', 'Nouvelle conversation')}")

        while True:
            try:
                text = input("\nVous > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nFermeture.")
                return

            if not text:
                continue

            if text == "/quit":
                print("Fermeture.")
                return

            if text == "/help":
                print(HELP_TEXT)
                continue

            if text == "/new":
                conversation = app.new_conversation()
                print(f"Nouvelle conversation créée : {conversation['id']}")
                continue

            if text == "/list":
                conversations = app.list_conversations(limit=20)
                if not conversations:
                    print("Aucune conversation enregistrée.")
                    continue
                for item in conversations:
                    marker = "*" if item["id"] == app.current_conversation_id else " "
                    print(f"{marker} {item['id']} — {item.get('title', 'Sans titre')}")
                continue

            if text.startswith("/use "):
                conversation_id = text[5:].strip()
                if not conversation_id:
                    print("Indiquez l'identifiant de la conversation.")
                    continue
                conversation = app.start(conversation_id)
                print(f"Conversation ouverte : {conversation.get('title', conversation_id)}")
                continue

            if text.startswith("/web "):
                value = text[5:].strip().lower()
                if value not in {"on", "off"}:
                    print("Utilisez /web on ou /web off.")
                    continue
                web_search_enabled = value == "on"
                print(
                    "Recherche Web activée."
                    if web_search_enabled
                    else "Recherche Web désactivée."
                )
                continue

            try:
                print("Assistant > ", end="", flush=True)
                answer = app.send_message(
                    text,
                    enable_web_search=web_search_enabled,
                )
                print(answer)
            except (OpenAIClientError, RuntimeError, ValueError) as exc:
                print(f"\nErreur : {exc}")
            except Exception as exc:  # garde-fou pour l'exécution sous Pyto
                print(f"\nErreur inattendue : {exc}")
                traceback.print_exc()


def main() -> int:
    try:
        run_console()
        return 0
    except RuntimeError as exc:
        print(f"Configuration incomplète : {exc}")
        return 2
    except Exception as exc:
        print(f"Échec du démarrage : {exc}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
