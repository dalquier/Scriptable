import json
import os

from config import (
    DEFAULT_BRANCH,
    DEFAULT_REPOSITORY,
    DEFAULT_ROOT_PATH,
    DEFAULT_TOKEN,
)

SETTINGS_FILENAME = "github_manager_v6_1.local.json"


def _settings_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), SETTINGS_FILENAME)


def defaults():
    return {
        "repository": DEFAULT_REPOSITORY,
        "branch": DEFAULT_BRANCH,
        "root_path": DEFAULT_ROOT_PATH,
        "token": DEFAULT_TOKEN,
    }


def load_settings():
    settings = defaults()
    path = _settings_path()
    if not os.path.exists(path):
        return settings

    try:
        with open(path, "r", encoding="utf-8") as handle:
            stored = json.load(handle)
        if isinstance(stored, dict):
            for key in settings:
                value = stored.get(key)
                if isinstance(value, str):
                    settings[key] = value
    except (OSError, ValueError, TypeError):
        pass

    return settings


def save_settings(settings):
    data = defaults()
    for key in data:
        value = settings.get(key, data[key])
        data[key] = value if isinstance(value, str) else data[key]

    path = _settings_path()
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(temporary_path, path)
    return path
