import base64
import json
import urllib.error
import urllib.parse
import urllib.request


class GitHubAPIError(Exception):
    pass


class GitHubClient:
    API = "https://api.github.com"

    def __init__(self, repository, branch="main", token="", timeout=30):
        if "/" not in repository:
            raise ValueError("Le dépôt doit être au format propriétaire/nom.")
        self.repository = repository.strip()
        self.branch = branch.strip() or "main"
        self.token = token.strip()
        self.timeout = timeout

    def _request(self, method, endpoint, payload=None):
        url = self.API + endpoint
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Pyto-GitHub-Content-Manager-V6",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(body).get("message", body)
            except Exception:
                message = body
            raise GitHubAPIError(f"GitHub {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError("Connexion impossible : " + str(exc.reason)) from exc

    @staticmethod
    def _quote_path(path):
        return "/".join(urllib.parse.quote(part, safe="") for part in path.strip("/").split("/") if part)

    def get_repo(self):
        return self._request("GET", f"/repos/{self.repository}")

    def list_path(self, path=""):
        quoted = self._quote_path(path)
        endpoint = f"/repos/{self.repository}/contents"
        if quoted:
            endpoint += "/" + quoted
        endpoint += "?ref=" + urllib.parse.quote(self.branch, safe="")
        result = self._request("GET", endpoint)
        if not isinstance(result, list):
            raise GitHubAPIError("Le chemin demandé n’est pas un dossier.")
        return sorted(result, key=lambda item: (item.get("type") != "dir", item.get("name", "").lower()))

    def get_file(self, path):
        quoted = self._quote_path(path)
        endpoint = f"/repos/{self.repository}/contents/{quoted}?ref=" + urllib.parse.quote(self.branch, safe="")
        data = self._request("GET", endpoint)
        if data.get("type") != "file":
            raise GitHubAPIError("Le chemin demandé n’est pas un fichier.")
        if data.get("encoding") != "base64":
            raise GitHubAPIError("Encodage GitHub non pris en charge.")
        try:
            content = base64.b64decode(data.get("content", "")).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GitHubAPIError("Ce fichier n’est pas un fichier texte UTF-8.") from exc
        return {"path": data["path"], "sha": data["sha"], "content": content}

    def put_file(self, path, content, message, sha=None):
        quoted = self._quote_path(path)
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        if sha:
            payload["sha"] = sha
        return self._request("PUT", f"/repos/{self.repository}/contents/{quoted}", payload)

    def delete_file(self, path, sha, message):
        quoted = self._quote_path(path)
        return self._request("DELETE", f"/repos/{self.repository}/contents/{quoted}", {
            "message": message,
            "sha": sha,
            "branch": self.branch,
        })

    def create_folder(self, path):
        path = path.strip("/") + "/.gitkeep"
        return self.put_file(path, "", "Create folder " + path.rsplit("/", 1)[0])

    def rename_file(self, old_path, new_path):
        source = self.get_file(old_path)
        self.put_file(new_path, source["content"], f"Rename {old_path} to {new_path}")
        self.delete_file(old_path, source["sha"], f"Remove old path {old_path}")
