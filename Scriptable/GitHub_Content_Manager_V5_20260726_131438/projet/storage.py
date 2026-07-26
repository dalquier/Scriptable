import json
import os
from datetime import datetime

APP_NAME = "GitHubContentManagerV5"
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", APP_NAME)
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
LOG_FILE = os.path.join(BASE_DIR, "activity.json")
KEYRING_SERVICE = "GitHubContentManagerV5"
KEYRING_USER = "github_token"

DEFAULT_SETTINGS = {
    "repository": "dalquier/Scriptable",
    "branch": "main",
    "root_path": "Scriptable",
}


def _ensure_dir():
    os.makedirs(BASE_DIR, exist_ok=True)


def load_settings():
    _ensure_dir()
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        result = dict(DEFAULT_SETTINGS)
        result.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
        return result
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    _ensure_dir()
    safe = {k: settings.get(k, DEFAULT_SETTINGS[k]) for k in DEFAULT_SETTINGS}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(safe, file, ensure_ascii=False, indent=2)


def load_token():
    try:
        import keyring
        return keyring.get_password(KEYRING_SERVICE, KEYRING_USER) or ""
    except Exception:
        return ""


def save_token(token):
    token = (token or "").strip()
    try:
        import keyring
        if token:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USER, token)
        else:
            try:
                keyring.delete_password(KEYRING_SERVICE, KEYRING_USER)
            except Exception:
                pass
        return True
    except Exception:
        return False


def append_activity(action, path, detail=""):
    _ensure_dir()
    activities = load_activities()
    activities.insert(0, {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "path": path,
        "detail": detail,
    })
    activities = activities[:100]
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(activities, file, ensure_ascii=False, indent=2)


def load_activities():
    _ensure_dir()
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except Exception:
        return []
