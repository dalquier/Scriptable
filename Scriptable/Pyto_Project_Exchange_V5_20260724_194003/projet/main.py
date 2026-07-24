import base64
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import file_system
import pasteboard
import pyto_ui as ui

FORMAT_NAME = "PYTO_PROJECT_EXCHANGE"
FORMAT_VERSION = "5.0"
HEADER_MARKER = "<!-- PYTO_PROJECT_EXCHANGE:5.0 -->"
INDEX_MARKER = "<!-- PYTO_EXCHANGE_INDEX -->"
PART_MARKER = "<!-- PYTO_EXCHANGE_PART -->"
MANIFEST_BEGIN = "<!-- PYTO_MANIFEST_BEGIN -->"
MANIFEST_END = "<!-- PYTO_MANIFEST_END -->"
TARGET_PART_CHARACTERS = 70000
MAX_FRAGMENT_CHARACTERS = 55000
IGNORED_NAMES = {".git", "__pycache__", ".DS_Store", ".idea", ".vscode"}

CHATGPT_PROMPT = r"""
Tu vas recevoir un projet logiciel au format PYTO_PROJECT_EXCHANGE version 5.0.

RÈGLE ABSOLUE

Le champ JSON `part_count` de `00_INDEX.md` est l’unique source de vérité concernant le nombre de parties reçues. N’invente jamais de partie supplémentaire.

RÉCEPTION

1. Lis toujours `00_INDEX.md` en premier.
2. Attends exactement `PART_001.md` à `PART_NNN.md`, où N est la valeur de `part_count`.
3. Si `part_count` vaut 1, `PART_001.md` est la dernière partie.
4. Si la mission est déjà fournie avec la dernière partie, commence immédiatement le travail.
5. Lorsque toutes les parties annoncées sont présentes, il est interdit d’affirmer que le projet est incomplet.

MODIFICATION

- Reconstitue tous les fichiers à partir des fragments ordonnés par `chunk_index`.
- Tu peux ajouter, modifier, renommer, déplacer ou supprimer des fichiers.
- Renvoie toujours le projet final complet, jamais seulement un patch, un diff, un résumé ou des extraits.
- Mets à jour le manifeste, `file_count`, `part_count`, les chemins, les tailles et les SHA-256 lorsque tu peux les calculer exactement.
- Tous les chemins doivent être relatifs et sûrs.

SORTIE

Le nombre de parties de sortie est indépendant du nombre de parties d’entrée. Tu dois augmenter automatiquement `part_count` si nécessaire.

La première réponse doit commencer par `00_INDEX.md`, suivi d’autant de fichiers `PART_XXX.md` complets que possible.

Chaque fichier Markdown doit être livré dans son propre bloc Markdown complet. N’interromps jamais un fichier Markdown au milieu de son contenu. Tu peux interrompre la livraison uniquement entre deux fichiers Markdown.

Si des parties restent à livrer, termine uniquement par :

SUITE REQUISE — PROCHAIN FICHIER : PART_XXX.md

Lorsque l’utilisateur écrit `Continue`, reprends exactement au fichier annoncé, sans introduction et sans répéter les fichiers déjà livrés.

Après la dernière partie, termine uniquement par :

FIN DU LOT — N PARTIES LIVRÉES

Une limite de taille de réponse ne justifie jamais un refus : augmente `part_count` et poursuis sur plusieurs réponses.
""".strip()

EXISTING_CONVERSATION_PROMPT = r"""
À partir de maintenant, nous utilisons exclusivement PYTO_PROJECT_EXCHANGE version 5.0.

Ignore tout format d’échange précédent.

- `00_INDEX.md` est canonique.
- `part_count` est l’unique source de vérité.
- N’invente jamais de partie supplémentaire.
- Si `part_count = 1`, `PART_001.md` constitue le lot complet.
- Renvoie toujours le projet final complet.
- N’utilise jamais seulement un patch, un diff, un résumé ou des extraits.
- Augmente automatiquement `part_count` si la sortie est trop volumineuse.
- Livre les fichiers Markdown complets sur plusieurs réponses si nécessaire.
- Interromps la livraison uniquement entre deux fichiers Markdown.
- Termine une réponse incomplète par :
  SUITE REQUISE — PROCHAIN FICHIER : PART_XXX.md
- Quand j’écris `Continue`, reprends exactement au fichier annoncé.
- Termine la dernière réponse par :
  FIN DU LOT — N PARTIES LIVRÉES
""".strip()

TEXT_EXTENSIONS = {
    ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".csv", ".xml", ".html", ".css", ".js", ".ts", ".sh",
    ".sql", ".env", ".gitignore", ".swift", ".java", ".c", ".h", ".cpp",
}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def language_for(path):
    suffix = Path(path).suffix.lower()
    return {
        ".py": "python", ".json": "json", ".md": "markdown", ".txt": "text",
        ".js": "javascript", ".ts": "typescript", ".html": "html", ".css": "css",
        ".yaml": "yaml", ".yml": "yaml", ".xml": "xml", ".sh": "shell",
    }.get(suffix, "text")


def safe_relative_path(value):
    value = value.replace("\\", "/").strip("/")
    if not value or value.startswith("/"):
        raise ValueError("Chemin vide ou absolu interdit")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Chemin relatif non sûr")
    return "/".join(parts)


def is_text_file(path, data):
    if path.suffix.lower() in TEXT_EXTENSIONS or path.name == ".gitignore":
        try:
            data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    try:
        decoded = data.decode("utf-8")
        return "\x00" not in decoded
    except UnicodeDecodeError:
        return False


def iter_project_files(root):
    root = Path(root)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORED_NAMES for part in rel_parts):
            continue
        yield path


def split_content(content, maximum):
    if len(content) <= maximum:
        return [content]
    return [content[index:index + maximum] for index in range(0, len(content), maximum)]


def make_fragments(root):
    root = Path(root)
    files = []
    fragments = []
    for path in iter_project_files(root):
        relative = safe_relative_path(path.relative_to(root).as_posix())
        raw = path.read_bytes()
        if is_text_file(path, raw):
            encoding = "utf-8"
            content = raw.decode("utf-8")
        else:
            encoding = "base64"
            content = base64.b64encode(raw).decode("ascii")
        chunks = split_content(content, MAX_FRAGMENT_CHARACTERS)
        files.append({
            "path": relative,
            "encoding": encoding,
            "language": language_for(relative),
            "size_bytes": len(raw),
            "sha256": sha256_bytes(raw),
            "chunk_count": len(chunks),
        })
        for index, chunk in enumerate(chunks, 1):
            fragments.append({
                "path": relative,
                "encoding": encoding,
                "chunk_index": index,
                "chunk_count": len(chunks),
                "content": chunk,
            })
    return files, fragments


def render_file_block(fragment):
    metadata = {
        "path": fragment["path"],
        "encoding": fragment["encoding"],
        "chunk_index": fragment["chunk_index"],
        "chunk_count": fragment["chunk_count"],
    }
    return (
        f"<!-- PYTO_FILE_BEGIN {json.dumps(metadata, ensure_ascii=False, separators=(',', ':'))} -->\n"
        f"{fragment['content']}\n"
        "<!-- PYTO_FILE_END -->\n"
    )


def group_fragments(fragments):
    groups = {}
    order = []
    for fragment in fragments:
        path = fragment["path"]
        if path not in groups:
            groups[path] = []
            order.append(path)
        groups[path].append(fragment)
    parts = []
    current = []
    current_size = 0
    for path in order:
        file_fragments = sorted(groups[path], key=lambda item: item["chunk_index"])
        rendered_sizes = [len(render_file_block(item)) for item in file_fragments]
        total = sum(rendered_sizes)
        if total <= TARGET_PART_CHARACTERS:
            if current and current_size + total > TARGET_PART_CHARACTERS:
                parts.append(current)
                current = []
                current_size = 0
            current.extend(file_fragments)
            current_size += total
            continue
        if current:
            parts.append(current)
            current = []
            current_size = 0
        oversized = []
        oversized_size = 0
        for fragment, size in zip(file_fragments, rendered_sizes):
            if oversized and oversized_size + size > TARGET_PART_CHARACTERS:
                parts.append(oversized)
                oversized = []
                oversized_size = 0
            oversized.append(fragment)
            oversized_size += size
        if oversized:
            parts.append(oversized)
    if current:
        parts.append(current)
    return parts or [[]]


def build_part_document(project_name, part_number, part_count, fragments):
    manifest = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "document_type": "part",
        "project_name": project_name,
        "part_number": part_number,
        "part_count": part_count,
        "fragment_count": len(fragments),
        "fragments": [
            {
                "path": item["path"],
                "encoding": item["encoding"],
                "chunk_index": item["chunk_index"],
                "chunk_count": item["chunk_count"],
            }
            for item in fragments
        ],
    }
    blocks = "\n".join(render_file_block(item) for item in fragments)
    return (
        f"{HEADER_MARKER}\n{PART_MARKER}\n\n"
        f"# {project_name} — Partie {part_number:03d}/{part_count:03d}\n\n"
        f"{MANIFEST_BEGIN}\n{json.dumps(manifest, ensure_ascii=False, indent=2)}\n{MANIFEST_END}\n\n"
        f"{blocks}"
    )


def build_index_document(project_name, files, parts):
    generated = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    part_entries = []
    for number, fragments in enumerate(parts, 1):
        paths = []
        for fragment in fragments:
            if fragment["path"] not in paths:
                paths.append(fragment["path"])
        part_entries.append({
            "filename": f"PART_{number:03d}.md",
            "part_number": number,
            "fragment_count": len(fragments),
            "paths": paths,
        })
    manifest = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "document_type": "index",
        "project_name": project_name,
        "created_at": generated,
        "file_count": len(files),
        "part_count": len(parts),
        "target_part_characters": TARGET_PART_CHARACTERS,
        "files": files,
        "parts": part_entries,
    }
    return (
        f"{HEADER_MARKER}\n{INDEX_MARKER}\n\n"
        f"# Index du projet Pyto : {project_name}\n\n"
        "> Ce fichier est canonique. Le champ `part_count` indique exactement le nombre de parties attendues.\n\n"
        f"{MANIFEST_BEGIN}\n{json.dumps(manifest, ensure_ascii=False, indent=2)}\n{MANIFEST_END}\n\n"
        "## Prompt ChatGPT\n\n"
        "Copie le prompt intégré depuis l’interface, puis joins cet index et toutes les parties annoncées.\n"
    )


def export_project(root, output_parent):
    root = Path(root)
    output_parent = Path(output_parent)
    project_name = root.name or "Projet_Pyto"
    files, fragments = make_fragments(root)
    parts = group_fragments(fragments)
    bundle = output_parent / f"{project_name}__PYTO_EXCHANGE_5"
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "00_INDEX.md").write_text(build_index_document(project_name, files, parts), encoding="utf-8")
    for number, part_fragments in enumerate(parts, 1):
        document = build_part_document(project_name, number, len(parts), part_fragments)
        (bundle / f"PART_{number:03d}.md").write_text(document, encoding="utf-8")
    (bundle / "PROMPT_CHATGPT.md").write_text(CHATGPT_PROMPT + "\n", encoding="utf-8")
    (bundle / "PROMPT_CONVERSATION_EXISTANTE.md").write_text(EXISTING_CONVERSATION_PROMPT + "\n", encoding="utf-8")
    return bundle


def extract_manifest(text):
    pattern = re.escape(MANIFEST_BEGIN) + r"\s*(.*?)\s*" + re.escape(MANIFEST_END)
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise ValueError("Manifeste introuvable")
    return json.loads(match.group(1))


def extract_blocks(text):
    pattern = re.compile(
        r"<!-- PYTO_FILE_BEGIN (\{.*?\}) -->\n(.*?)\n<!-- PYTO_FILE_END -->",
        re.DOTALL,
    )
    result = []
    for metadata_text, content in pattern.findall(text):
        metadata = json.loads(metadata_text)
        metadata["content"] = content
        result.append(metadata)
    return result


def import_bundle(bundle, destination):
    bundle = Path(bundle)
    destination = Path(destination)
    index_path = bundle / "00_INDEX.md"
    index_manifest = extract_manifest(index_path.read_text(encoding="utf-8"))
    if index_manifest.get("version") != FORMAT_VERSION:
        raise ValueError("Version PPE incompatible")
    expected_parts = int(index_manifest["part_count"])
    collected = {}
    for number in range(1, expected_parts + 1):
        part_path = bundle / f"PART_{number:03d}.md"
        if not part_path.exists():
            raise FileNotFoundError(f"Partie manquante : {part_path.name}")
        text = part_path.read_text(encoding="utf-8")
        part_manifest = extract_manifest(text)
        if int(part_manifest["part_number"]) != number or int(part_manifest["part_count"]) != expected_parts:
            raise ValueError(f"Numérotation invalide dans {part_path.name}")
        for block in extract_blocks(text):
            path = safe_relative_path(block["path"])
            collected.setdefault(path, []).append(block)
    destination.mkdir(parents=True, exist_ok=True)
    expected_files = {item["path"]: item for item in index_manifest["files"]}
    if set(collected) != set(expected_files):
        missing = sorted(set(expected_files) - set(collected))
        extra = sorted(set(collected) - set(expected_files))
        raise ValueError(f"Écart de fichiers. Manquants={missing}, supplémentaires={extra}")
    for relative, blocks in collected.items():
        blocks.sort(key=lambda item: int(item["chunk_index"]))
        chunk_count = int(blocks[0]["chunk_count"])
        if [int(item["chunk_index"]) for item in blocks] != list(range(1, chunk_count + 1)):
            raise ValueError(f"Fragments incomplets : {relative}")
        content = "".join(item["content"] for item in blocks)
        encoding = blocks[0]["encoding"]
        raw = content.encode("utf-8") if encoding == "utf-8" else base64.b64decode(content, validate=True)
        metadata = expected_files[relative]
        if metadata.get("sha256") and sha256_bytes(raw) != metadata["sha256"]:
            raise ValueError(f"SHA-256 invalide : {relative}")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return destination


def choose_directory(title):
    try:
        return file_system.pick_directory(title)
    except TypeError:
        return file_system.pick_directory()


def alert(title, message):
    ui.alert(title, message, ["OK"])


class ExchangeApp:
    def __init__(self):
        self.view = ui.View()
        self.view.background_color = ui.COLOR_SYSTEM_BACKGROUND
        self.title = ui.Label("Pyto Project Exchange 5.0")
        self.title.font = ui.Font.bold_system_font_of_size(23)
        self.title.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        self.subtitle = ui.Label("Export, import et prompts ChatGPT")
        self.subtitle.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        self.subtitle.text_color = ui.COLOR_SECONDARY_LABEL
        self.export_button = self.make_button("Exporter un projet", self.export_action)
        self.import_button = self.make_button("Importer un lot", self.import_action)
        self.copy_button = self.make_button("Copier le prompt principal", self.copy_action)
        self.copy_existing_button = self.make_button("Prompt conversation existante", self.copy_existing_action)
        self.close_button = self.make_button("Fermer", self.close_action)
        for item in [self.title, self.subtitle, self.export_button, self.import_button, self.copy_button, self.copy_existing_button, self.close_button]:
            self.view.add_subview(item)
        self.view.layout = self.layout

    def make_button(self, title, action):
        button = ui.Button(title=title)
        button.action = action
        button.corner_radius = 12
        button.background_color = ui.COLOR_SECONDARY_SYSTEM_BACKGROUND
        return button

    def layout(self, sender):
        width = sender.width
        margin = 22
        usable = width - margin * 2
        self.title.frame = (margin, 35, usable, 38)
        self.subtitle.frame = (margin, 76, usable, 28)
        y = 125
        for button in [self.export_button, self.import_button, self.copy_button, self.copy_existing_button, self.close_button]:
            button.frame = (margin, y, usable, 52)
            y += 64

    def export_action(self, sender):
        source = choose_directory("Choisir le projet à exporter")
        if not source:
            return
        destination = choose_directory("Choisir le dossier de destination")
        if not destination:
            return
        try:
            bundle = export_project(source, destination)
            alert("Export terminé", f"Lot créé :\n{bundle}")
        except Exception as error:
            alert("Erreur d’export", str(error))

    def import_action(self, sender):
        bundle = choose_directory("Choisir le lot PPE5")
        if not bundle:
            return
        destination = choose_directory("Choisir le dossier de restauration")
        if not destination:
            return
        try:
            restored = import_bundle(bundle, destination)
            alert("Import terminé", f"Projet restauré dans :\n{restored}")
        except Exception as error:
            alert("Erreur d’import", str(error))

    def copy_action(self, sender):
        pasteboard.string = CHATGPT_PROMPT
        alert("Prompt copié", "Le prompt principal PPE5 est dans le presse-papiers.")

    def copy_existing_action(self, sender):
        pasteboard.string = EXISTING_CONVERSATION_PROMPT
        alert("Prompt copié", "Le prompt pour conversation existante est dans le presse-papiers.")

    def close_action(self, sender):
        try:
            self.view.close()
        except Exception:
            pass


if __name__ == "__main__":
    app = ExchangeApp()
    ui.show_view(app.view, ui.PRESENTATION_MODE_SHEET)
