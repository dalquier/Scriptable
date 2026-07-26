import json
import os
import tempfile

from config import DEFAULT_SETTINGS, LOCAL_SETTINGS_FILENAME


def _settings_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_SETTINGS_FILENAME)


def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    path = _settings_path()
    if not os.path.exists(path):
        return settings
    try:
        with open(path, "r", encoding="utf-8") as handle:
            saved = json.load(handle)
        if isinstance(saved, dict):
            for key in settings:
                if key in saved and isinstance(saved[key], str):
                    settings[key] = saved[key]
    except Exception:
        pass
    return settings


def save_settings(settings):
    folder = os.path.dirname(_settings_path())
    fd, temp_path = tempfile.mkstemp(prefix="github_manager_", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, _settings_path())
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
