import json
import os


LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_manager_v6.local.json")
DEFAULTS = {
    "repository": "dalquier/Scriptable",
    "branch": "main",
    "root_path": "Scriptable",
    "token": "",
}


def load_settings():
    data = dict(DEFAULTS)
    try:
        with open(LOCAL_FILE, "r", encoding="utf-8") as stream:
            saved = json.load(stream)
        if isinstance(saved, dict):
            data.update({k: saved.get(k, data[k]) for k in data})
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return data


def save_settings(settings):
    clean = {key: str(settings.get(key, DEFAULTS[key])) for key in DEFAULTS}
    with open(LOCAL_FILE, "w", encoding="utf-8") as stream:
        json.dump(clean, stream, ensure_ascii=False, indent=2)
