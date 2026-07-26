import json
import urllib.request

from config import Config
from planner import Planner
from state import StateStore


class AutonomousExecutor:
    def __init__(self) -> None:
        self.config = Config.load()
        self.planner = Planner()
        self.store = StateStore()

    def _call_openai(self, prompt: str) -> str:
        payload = {
            "model": self.config.model,
            "input": prompt,
            "max_output_tokens": 1200,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data.get("output_text", "").strip()
        if text:
            return text
        chunks = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    chunks.append(content.get("text", ""))
        return "\n".join(chunks).strip()

    @staticmethod
    def _parse_status(text: str) -> str:
        try:
            data = json.loads(text)
            return str(data.get("status", "continue")).lower()
        except Exception:
            return "continue" if text.rstrip().endswith("En cours") else "blocked"

    def run(self) -> None:
        state = self.store.load()
        task = self.planner.current_task()
        state.status = "running"

        while state.iteration < self.config.max_iterations:
            state.iteration += 1
            prompt = self.planner.build_prompt(task, state.last_response, state.iteration)
            response = self._call_openai(prompt)
            state.last_response = response
            state.history.append(response)
            state.status = self._parse_status(response)
            self.store.save(state)
            print(f"[{state.iteration}] {state.status}: {response}")

            if state.status == "continue":
                continue
            break

        if state.iteration >= self.config.max_iterations and state.status == "continue":
            state.status = "paused"
            self.store.save(state)


if __name__ == "__main__":
    AutonomousExecutor().run()
