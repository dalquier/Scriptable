from pathlib import Path


class Planner:
    def __init__(self, task_path: str = "task.txt") -> None:
        self.task_path = Path(task_path)

    def current_task(self) -> str:
        if not self.task_path.exists():
            return "Construis progressivement DeveloperOS et termine par En cours tant que la tâche n'est pas finie."
        return self.task_path.read_text(encoding="utf-8").strip()

    def build_prompt(self, task: str, previous_response: str, iteration: int) -> str:
        context = previous_response.strip() or "Aucune réponse précédente."
        return (
            "Tu travailles de manière autonome sur DeveloperOS.\n"
            f"Itération: {iteration}\n"
            f"Mission: {task}\n\n"
            "Réponse précédente:\n"
            f"{context}\n\n"
            "Réponds uniquement avec un objet JSON valide contenant: "
            "status (continue|done|blocked), summary et next_action. "
            "Utilise continue tant que le travail doit se poursuivre."
        )
