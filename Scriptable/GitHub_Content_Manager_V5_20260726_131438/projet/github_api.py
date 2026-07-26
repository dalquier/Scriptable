import base64
import json
import urllib.error
import urllib.parse
import urllib.request


class GitHubAPIError(Exception):
    pass


class GitHubClient:
    API_ROOT = "https://api.github.com"

    def __init__(self, repository, branch="main", token="", timeout=30):
        if "/" not in repository:
            raise ValueError("Le dépôt doit être au format propriétaire/nom.")
        self.repository = repository.strip().strip("/")
        self.branch = branch.strip() or "main"
        self.token = token.strip()
        self.timeout = timeout

    def _request(self, method, path, payload=None):
        url = self.API_ROOT + path
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Pyto-GitHub-Content-Manager-V5",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(raw).get("message", raw)
            except Exception:
                message = raw
            raise GitHubAPIError(f"GitHub {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError(f"Connexion impossible : {exc.reason}") from exc

    def get_repo(self):
        return self._request("GET", f"/repos/{self.repository}")

    def list_path(self, path=""):
        encoded = urllib.parse.quote(path.strip("/"), safe="/")
        suffix = f"/{encoded}" if encoded else ""
        query = urllib.parse.urlencode({"ref": self.branch})
        data = self._request("GET", f"/repos/{self.repository}/contents{suffix}?{query}")
        if isinstance(data, dict):
            return [data]
        return sorted(data, key=lambda item: (item.get("type") != "dir", item.get("name", "").lower()))

    def get_file(self, path):
        encoded = urllib.parse.quote(path.strip("/"), safe="/")
        query = urllib.parse.urlencode({"ref": self.branch})
        data = self._request("GET", f"/repos/{self.repository}/contents/{encoded}?{query}")
        if data.get("type") != "file":
            raise GitHubAPIError("Cet élément n'est pas un fichier.")
        content = data.get("content", "").replace("\n", "")
        binary = base64.b64decode(content) if content else b""
        try:
            text = binary.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GitHubAPIError("Ce fichier n'est pas un fichier texte UTF-8 éditable.") from exc
        return {"path": path, "sha": data["sha"], "content": text, "size": data.get("size", 0)}

    def put_file(self, path, content, message, sha=None):
        encoded = urllib.parse.quote(path.strip("/"), safe="/")
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        if sha:
            payload["sha"] = sha
        return self._request("PUT", f"/repos/{self.repository}/contents/{encoded}", payload)

    def create_folder(self, path, message=None):
        folder = path.strip("/")
        if not folder:
            raise GitHubAPIError("Nom de dossier invalide.")
        marker = folder + "/.gitkeep"
        return self.put_file(marker, "", message or f"Create folder {folder}")

    def delete_file(self, path, sha, message):
        encoded = urllib.parse.quote(path.strip("/"), safe="/")
        payload = {"message": message, "sha": sha, "branch": self.branch}
        return self._request("DELETE", f"/repos/{self.repository}/contents/{encoded}", payload)

    def rename_file(self, old_path, new_path, message=None):
        current = self.get_file(old_path)
        commit_message = message or f"Rename {old_path} to {new_path}"
        self.put_file(new_path, current["content"], commit_message)
        try:
            self.delete_file(old_path, current["sha"], commit_message)
        except Exception:
            try:
                created = self.get_file(new_path)
                self.delete_file(new_path, created["sha"], f"Rollback incomplete rename of {old_path}")
            except Exception:
                pass
            raise
        return True
