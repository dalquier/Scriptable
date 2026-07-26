import json
from pathlib import Path

from openai_client import OpenAIClient, OpenAIClientError
from planner import SYSTEM_INSTRUCTIONS, build_prompt, choose_context_paths
from project_index import build_index, save_index
from state import load_state, save_state
from validator import validate_python_files
from workspace import Workspace, WorkspaceError


def load_settings(builder_root: Path) -> dict:
    settings_path = builder_root / "settings.json"
    if not settings_path.exists():
        settings_path = builder_root / "settings.example.json"
    return json.loads(settings_path.read_text(encoding="utf-8"))


def parse_plan(text: str) -> dict:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Réponse JSON invalide: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Le plan doit être un objet JSON")
    status = data.get("status")
    if status not in {"continue", "done", "blocked"}:
        raise ValueError("Statut invalide")
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError("changes doit être une liste")
    return data


def run() -> None:
    builder_root = Path(__file__).resolve().parent
    settings = load_settings(builder_root)
    project_root = (builder_root / settings.get("project_root", "..")).resolve()
    state_path = builder_root / settings.get("state_file", "state.json")
    index_path = builder_root / settings.get("index_file", "project_index.json")

    state = load_state(state_path)
    workspace = Workspace(project_root, builder_root)
    client = OpenAIClient(
        api_url=settings["api_url"],
        model=settings["model"],
        max_output_tokens=int(settings.get("max_output_tokens", 8000)),
    )

    max_iterations = int(settings.get("max_iterations_per_run", 3))
    for _ in range(max_iterations):
        index = build_index(
            project_root,
            settings.get("include_extensions", [".py", ".json", ".md", ".txt"]),
            settings.get("exclude_directories", []),
        )
        save_index(index_path, index)

        context_paths = choose_context_paths(index)
        context = workspace.collect_context(context_paths)
        prompt = build_prompt(state, index, context)

        state["status"] = "planning"
        save_state(state_path, state)

        response = client.ask(SYSTEM_INSTRUCTIONS, prompt)
        plan = parse_plan(response)
        state["last_goal"] = plan.get("goal")
        state["last_result"] = plan.get("summary")

        if plan["status"] == "blocked":
            state["status"] = "blocked"
            state["blocked_reason"] = plan.get("summary")
            save_state(state_path, state)
            print("Builder bloqué:", state["blocked_reason"])
            return

        if plan["status"] == "done":
            state["status"] = "done"
            save_state(state_path, state)
            print("DeveloperOS déclaré terminé par le planificateur.")
            return

        changes = plan.get("changes", [])
        if not changes:
            state["status"] = "blocked"
            state["blocked_reason"] = "Aucune modification proposée"
            save_state(state_path, state)
            print(state["blocked_reason"])
            return

        if not settings.get("allow_write", True):
            state["status"] = "preview"
            state["last_result"] = plan
            save_state(state_path, state)
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return

        written = workspace.apply_changes(
            changes,
            backup=bool(settings.get("backup_before_write", True)),
        )
        errors = validate_python_files(project_root, written)
        if errors:
            state["status"] = "blocked"
            state["blocked_reason"] = {"validation_errors": errors}
            save_state(state_path, state)
            print("Erreurs de validation:", errors)
            return

        state["iteration"] = int(state.get("iteration", 0)) + 1
        state["status"] = "ready"
        state["blocked_reason"] = None
        state.setdefault("completed_tasks", []).append(
            {
                "iteration": state["iteration"],
                "goal": plan.get("goal"),
                "files": written,
            }
        )
        save_state(state_path, state)
        print(f"Itération {state['iteration']} terminée: {plan.get('goal')}")


if __name__ == "__main__":
    try:
        run()
    except (OpenAIClientError, WorkspaceError, OSError, ValueError, KeyError) as exc:
        print("DeveloperOS Builder arrêté:", exc)
