import base64
import json
import urllib.error
import urllib.parse
import urllib.request


class GitHubAPIError(Exception):
    pass


class GitHubClient:
    def __init__(self, repository, branch="main", token=""):
        self.repository = repository.strip()
        self.branch = branch.strip() or "main"
        self.token = token.strip()
        if "/" not in self.repository:
            raise ValueError("Le dépôt doit être au format propriétaire/nom.")

    def _request(self, method, path, payload=None):
        url = "https://api.github.com/repos/{}/{}".format(self.repository, path.lstrip("/"))
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHub-Content-Manager-Pyto/6.2",
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
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(raw).get("message", raw)
            except ValueError:
                detail = raw
            raise GitHubAPIError("GitHub {} : {}".format(exc.code, detail))
        except urllib.error.URLError as exc:
            raise GitHubAPIError("Connexion impossible : {}".format(exc.reason))

    def list_path(self, path=""):
        quoted = urllib.parse.quote(path.strip("/"), safe="/")
        endpoint = "contents/{}?ref={}".format(quoted, urllib.parse.quote(self.branch))
        result = self._request("GET", endpoint)
        return [result] if isinstance(result, dict) else (result or [])

    def get_file(self, path):
        quoted = urllib.parse.quote(path.strip("/"), safe="/")
        result = self._request("GET", "contents/{}?ref={}".format(quoted, urllib.parse.quote(self.branch)))
        if result.get("encoding") != "base64":
            raise GitHubAPIError("Ce fichier n'est pas lisible comme texte UTF-8.")
        try:
            content = base64.b64decode(result.get("content", "")).decode("utf-8")
        except UnicodeDecodeError:
            raise GitHubAPIError("Ce fichier n'est pas un fichier texte UTF-8.")
        return {"path": result["path"], "sha": result["sha"], "content": content}

    def _require_token(self):
        if not self.token:
            raise GitHubAPIError("Un jeton GitHub est requis pour modifier le dépôt.")

    def put_file(self, path, content, message, sha=None):
        self._require_token()
        payload = {"message": message, "content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "branch": self.branch}
        if sha:
            payload["sha"] = sha
        quoted = urllib.parse.quote(path.strip("/"), safe="/")
        return self._request("PUT", "contents/{}".format(quoted), payload)

    def delete_file(self, path, sha, message):
        self._require_token()
        quoted = urllib.parse.quote(path.strip("/"), safe="/")
        return self._request("DELETE", "contents/{}".format(quoted), {"message": message, "sha": sha, "branch": self.branch})

    def create_folder(self, path):
        return self.put_file(path.strip("/") + "/.gitkeep", "", "Create folder {}".format(path))

    def rename_file(self, old_path, new_path):
        current = self.get_file(old_path)
        self.put_file(new_path, current["content"], "Move {} to {}".format(old_path, new_path))
        self.delete_file(old_path, current["sha"], "Remove old path {}".format(old_path))
