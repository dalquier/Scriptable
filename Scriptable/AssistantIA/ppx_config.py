FORMAT_VERSION = "5.0"
APP_TITLE = "Pyto Project Exchange V5"
TARGET_PART_CHARACTERS = 60000
MAX_FRAGMENT_CHARACTERS = 50000
TEXT_EXTENSIONS = {
    ".py", ".pyi", ".txt", ".md", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".csv", ".xml", ".html", ".css", ".js", ".ts",
    ".sh", ".bat", ".sql", ".rst", ".gitignore"
}
EXCLUDED_DIR_NAMES = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv"
}
EXCLUDED_FILE_NAMES = {
    ".env", "secrets.py", "secrets.json", ".DS_Store"
}
INDEX_FILENAME = "00_INDEX.md"
PART_PREFIX = "PART_"
PART_SUFFIX = ".md"
FILE_BEGIN = "PYTO_FILE_BEGIN"
FILE_END = "PYTO_FILE_END"
