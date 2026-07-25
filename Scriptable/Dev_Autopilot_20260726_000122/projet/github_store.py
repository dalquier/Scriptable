"""Écriture de fichiers dans GitHub via l'API Contents."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


class GitHubStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class WriteResult:
    path: str
    commit_sha: str
    action: str


class GitHubStore:
    API_ROOT = "https://api.github.com"

    def __init__(self, token: str, repository: str, branch: str) -> None:
        self.token = token
        self.repository = repository
        self.branch = branch

    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
    ) -> dict:
        url = f"{self.API_ROOT}{path}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "Dev-Autopilot",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubStoreError(
                f"Erreur GitHub HTTP {exc.code} pour {path}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubStoreError(f"Erreur réseau GitHub: {exc.reason}") from exc

    def _content_path(self, repo_path: str) -> str:
        encoded = urllib.parse.quote(repo_path.strip("/"), safe="/")
        return f"/repos/{self.repository}/contents/{encoded}"

    def get_sha(self, repo_path: str) -> str | None:
        path = self._content_path(repo_path)
        query = urllib.parse.urlencode({"ref": self.branch})
        try:
            data = self._request("GET", f"{path}?{query}")
            sha = data.get("sha")
            return sha if isinstance(sha, str) else None
        except GitHubStoreError as exc:
            if "HTTP 404" in str(exc):
                return None
            raise

    def upsert_text(self, repo_path: str, content: str, message: str) -> WriteResult:
        sha = self.get_sha(repo_path)
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        action = "updated" if sha else "created"
        if sha:
            payload["sha"] = sha

        data = self._request("PUT", self._content_path(repo_path), payload)
        commit_sha = data.get("commit", {}).get("sha", "")
        if not commit_sha:
            raise GitHubStoreError(f"GitHub n'a pas renvoyé de commit pour {repo_path}.")
        return WriteResult(path=repo_path, commit_sha=commit_sha, action=action)
