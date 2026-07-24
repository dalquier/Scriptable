"""PYTO_PROJECT_EXCHANGE 5.0

Outil Pyto monofichier pour exporter et importer un projet complet au format
Markdown multipartie. La V5 reste volontairement proche de la V3, mais ajoute :

- project_uuid ;
- snapshot_id et parent_snapshot_id ;
- modes FULL et DELTA ;
- SHA-256 de chaque fichier et du projet ;
- validation transactionnelle avant import ;
- prompt ChatGPT V5 prêt à copier.

Aucune dépendance externe n'est requise.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import pyto_ui as ui
except Exception:
    ui = None

FORMAT_VERSION = "5.0"
HEADER_MARKER = "<!-- PYTO_PROJECT_EXCHANGE:5.0 -->"
INDEX_NAME = "00_INDEX.md"
TARGET_PART_CHARACTERS = 60_000
MAX_CONTENT_CHUNK_CHARACTERS = 48_000
SNAPSHOT_DIRNAME = ".pyto_exchange"
SNAPSHOT_FILENAME = "snapshot_v5.json"

TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".ini",
    ".cfg", ".csv", ".html", ".css", ".js", ".ts", ".xml", ".plist",
    ".sh", ".bat", ".sql", ".rst", ".gitignore",
}

CHATGPT_PROMPT = r"""
Tu vas recevoir un projet logiciel au format PYTO_PROJECT_EXCHANGE version 5.0.

RÈGLES IMPÉRATIVES

1. Lis toujours 00_INDEX.md en premier.
2. Le champ `part_count` est l'unique source de vérité concernant le nombre de
   fichiers PART_xxx.md attendus.
3. N'invente jamais une partie supplémentaire.
4. Si `part_count = 1`, PART_001.md constitue la première et la dernière partie.
5. Le nombre de parties en sortie est indépendant du nombre de parties reçu.
6. Tu peux augmenter ou diminuer automatiquement `part_count` selon la taille du
   projet final.
7. Une limite de taille de réponse ne justifie jamais un refus.
8. Si la livraison est trop volumineuse, répartis-la sur plusieurs réponses.
9. Ne coupe jamais un fichier Markdown de livraison au milieu de son contenu.
10. Interromps une réponse uniquement entre deux fichiers Markdown complets.
11. Ne renvoie jamais seulement un patch, un diff, un résumé ou des extraits.
12. Le résultat doit toujours représenter le projet final complet, sauf lorsque
    le mode demandé est explicitement DELTA.
13. Mets à jour les champs suivants :
    - protocol_version ;
    - project_uuid ;
    - mode ;
    - snapshot_id ;
    - parent_snapshot_id ;
    - generated_at ;
    - project_sha256 ;
    - file_count ;
    - part_count ;
    - files ;
    - parts.
14. Pour chaque fichier modifié ou ajouté, calcule `size_bytes` et `sha256` si tu
    peux le faire exactement ; sinon mets ces valeurs à null.
15. Les chemins doivent rester relatifs et ne doivent contenir ni chemin absolu,
    ni `..`.
16. Les fragments sont identifiés par `path`, `chunk_index`, `chunk_count` et
    doivent être concaténés dans l'ordre croissant.
17. Un fichier supprimé doit disparaître de l'index et des parties.
18. Un fichier renommé doit disparaître sous son ancien chemin et réapparaître
    sous son nouveau chemin.

FORMAT DE LIVRAISON

La première réponse doit contenir 00_INDEX.md, puis autant de PART_xxx.md complets
que possible. Chaque fichier Markdown doit être placé dans son propre bloc.

Si d'autres fichiers restent à livrer, termine uniquement par :

SUITE REQUISE — PROCHAIN FICHIER : PART_XXX.md

Lorsque l'utilisateur écrit `Continue`, reprends exactement au fichier annoncé,
sans répéter les fichiers déjà livrés.

Pour reprendre à un endroit précis, accepte également :

- Reprendre PART_005.md
- Relivrer PART_003.md
- Reprendre après PART_006.md

Après la dernière partie, termine uniquement par :

FIN DU LOT — N PARTIES LIVRÉES
""".strip()


class ExchangeError(Exception):
    """Erreur lisible du protocole."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative_path(value: str) -> str:
    value = value.replace("\\", "/").strip("/")
    if not value or value.startswith("/"):
        raise ExchangeError("Chemin vide ou absolu interdit.")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ExchangeError(f"Chemin non sûr : {value}")
    return value


def is_text_file(path: Path) -> bool:
    if path.name == ".gitignore":
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def list_project_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == SNAPSHOT_DIRNAME:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.as_posix().lower())


def read_file_record(root: Path, path: Path) -> dict:
    relative = safe_relative_path(path.relative_to(root).as_posix())
    raw = path.read_bytes()
    if is_text_file(path):
        try:
            content = raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            content = base64.b64encode(raw).decode("ascii")
            encoding = "base64"
    else:
        content = base64.b64encode(raw).decode("ascii")
        encoding = "base64"
    return {
        "path": relative,
        "encoding": encoding,
        "content": content,
        "size_bytes": len(raw),
        "sha256": sha256_bytes(raw),
    }


def split_content(record: dict) -> list[dict]:
    content = record["content"]
    if not content:
        chunks = [""]
    else:
        chunks = [
            content[index:index + MAX_CONTENT_CHUNK_CHARACTERS]
            for index in range(0, len(content), MAX_CONTENT_CHUNK_CHARACTERS)
        ]
    count = len(chunks)
    return [
        {
            "path": record["path"],
            "encoding": record["encoding"],
            "size_bytes": record["size_bytes"],
            "sha256": record["sha256"],
            "chunk_index": index + 1,
            "chunk_count": count,
            "content": chunk,
        }
        for index, chunk in enumerate(chunks)
    ]


def render_file_block(fragment: dict) -> str:
    metadata = {
        "path": fragment["path"],
        "encoding": fragment["encoding"],
        "size_bytes": fragment["size_bytes"],
        "sha256": fragment["sha256"],
        "chunk_index": fragment["chunk_index"],
        "chunk_count": fragment["chunk_count"],
    }
    return (
        "<!-- PYTO_FILE_BEGIN\n"
        + json.dumps(metadata, ensure_ascii=False, indent=2)
        + "\n-->\n"
        + fragment["content"]
        + "\n<!-- PYTO_FILE_END -->\n"
    )


def group_fragments_into_parts(fragments: list[dict]) -> list[list[dict]]:
    by_path = {}
    order = []
    for fragment in fragments:
        path = fragment["path"]
        if path not in by_path:
            by_path[path] = []
            order.append(path)
        by_path[path].append(fragment)

    parts = []
    current = []
    current_size = 0

    for path in order:
        group = sorted(by_path[path], key=lambda item: item["chunk_index"])
        lengths = [len(render_file_block(item)) for item in group]
        group_size = sum(lengths)

        if group_size <= TARGET_PART_CHARACTERS:
            if current and current_size + group_size > TARGET_PART_CHARACTERS:
                parts.append(current)
                current = []
                current_size = 0
            current.extend(group)
            current_size += group_size
            continue

        if current:
            parts.append(current)
            current = []
            current_size = 0

        large_part = []
        large_size = 0
        for fragment, block_size in zip(group, lengths):
            if large_part and large_size + block_size > TARGET_PART_CHARACTERS:
                parts.append(large_part)
                large_part = []
                large_size = 0
            large_part.append(fragment)
            large_size += block_size
        if large_part:
            parts.append(large_part)

    if current:
        parts.append(current)
    return parts or [[]]


def project_digest(file_entries: list[dict]) -> str:
    canonical = "\n".join(
        f"{entry['path']}:{entry['sha256']}"
        for entry in sorted(file_entries, key=lambda item: item["path"])
    ).encode("utf-8")
    return sha256_bytes(canonical)


def snapshot_path(root: Path) -> Path:
    return root / SNAPSHOT_DIRNAME / SNAPSHOT_FILENAME


def load_snapshot(root: Path) -> dict | None:
    path = snapshot_path(root)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_snapshot(root: Path, index_data: dict) -> None:
    folder = root / SNAPSHOT_DIRNAME
    folder.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "protocol_version": FORMAT_VERSION,
        "project_uuid": index_data["project_uuid"],
        "snapshot_id": index_data["snapshot_id"],
        "project_sha256": index_data["project_sha256"],
        "generated_at": index_data["generated_at"],
        "files": {
            item["path"]: {
                "sha256": item["sha256"],
                "size_bytes": item["size_bytes"],
            }
            for item in index_data["files"]
        },
    }
    snapshot_path(root).write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_export(root: Path, mode: str = "FULL") -> tuple[dict, list[str]]:
    mode = mode.upper()
    if mode not in {"FULL", "DELTA"}:
        raise ExchangeError("Le mode doit être FULL ou DELTA.")

    records = [read_file_record(root, path) for path in list_project_files(root)]
    previous = load_snapshot(root)
    project_uuid = (previous or {}).get("project_uuid") or str(uuid.uuid4())
    parent_snapshot_id = (previous or {}).get("snapshot_id")
    snapshot_id = str(uuid.uuid4())

    deleted_paths = []
    selected = records
    if mode == "DELTA" and previous:
        old_files = previous.get("files", {})
        current_by_path = {item["path"]: item for item in records}
        selected = [
            item for item in records
            if old_files.get(item["path"], {}).get("sha256") != item["sha256"]
        ]
        deleted_paths = sorted(set(old_files) - set(current_by_path))

    fragments = []
    for record in selected:
        fragments.extend(split_content(record))
    parts = group_fragments_into_parts(fragments)

    file_entries = [
        {
            "path": item["path"],
            "encoding": item["encoding"],
            "size_bytes": item["size_bytes"],
            "sha256": item["sha256"],
        }
        for item in records
    ]

    index = {
        "protocol_version": FORMAT_VERSION,
        "project_uuid": project_uuid,
        "project_name": root.name,
        "mode": mode,
        "snapshot_id": snapshot_id,
        "parent_snapshot_id": parent_snapshot_id,
        "generated_at": utc_now_iso(),
        "project_sha256": project_digest(file_entries),
        "file_count": len(file_entries),
        "part_count": len(parts),
        "deleted_paths": deleted_paths,
        "files": file_entries,
        "parts": [],
    }

    part_documents = []
    for number, part in enumerate(parts, start=1):
        name = f"PART_{number:03d}.md"
        body = [
            HEADER_MARKER,
            f"# Partie {number:03d}/{len(parts):03d}",
            "",
            json.dumps(
                {
                    "protocol_version": FORMAT_VERSION,
                    "project_uuid": project_uuid,
                    "snapshot_id": snapshot_id,
                    "part_number": number,
                    "part_count": len(parts),
                },
                ensure_ascii=False,
                indent=2,
            ),
            "",
        ]
        for fragment in part:
            body.append(render_file_block(fragment))
        document = "\n".join(body).rstrip() + "\n"
        part_documents.append(document)
        index["parts"].append({
            "name": name,
            "part_number": number,
            "sha256": sha256_bytes(document.encode("utf-8")),
            "paths": sorted({fragment["path"] for fragment in part}),
        })

    save_snapshot(root, index)
    return index, part_documents


def render_index(index: dict) -> str:
    return (
        HEADER_MARKER
        + "\n# PYTO_PROJECT_EXCHANGE 5.0\n\n"
        + json.dumps(index, ensure_ascii=False, indent=2)
        + "\n"
    )


def export_project(root: Path, destination: Path, mode: str = "FULL") -> Path:
    index, parts = build_export(root, mode)
    output = destination / f"{root.name}__PYTO_EXCHANGE_V5"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / INDEX_NAME).write_text(render_index(index), encoding="utf-8")
    for number, document in enumerate(parts, start=1):
        (output / f"PART_{number:03d}.md").write_text(document, encoding="utf-8")
    return output


def parse_index(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if HEADER_MARKER not in text:
        raise ExchangeError("Marqueur V5 absent de 00_INDEX.md.")
    json_start = text.find("{")
    if json_start < 0:
        raise ExchangeError("JSON d'index introuvable.")
    return json.loads(text[json_start:])


def parse_file_blocks(text: str) -> list[dict]:
    begin = "<!-- PYTO_FILE_BEGIN\n"
    metadata_end = "\n-->\n"
    end = "\n<!-- PYTO_FILE_END -->"
    blocks = []
    cursor = 0
    while True:
        start = text.find(begin, cursor)
        if start < 0:
            break
        metadata_start = start + len(begin)
        metadata_stop = text.find(metadata_end, metadata_start)
        if metadata_stop < 0:
            raise ExchangeError("Métadonnées de fichier incomplètes.")
        content_start = metadata_stop + len(metadata_end)
        content_stop = text.find(end, content_start)
        if content_stop < 0:
            raise ExchangeError("Bloc PYTO_FILE_END manquant.")
        metadata = json.loads(text[metadata_start:metadata_stop])
        metadata["content"] = text[content_start:content_stop]
        metadata["path"] = safe_relative_path(metadata["path"])
        blocks.append(metadata)
        cursor = content_stop + len(end)
    return blocks


def import_project(exchange_dir: Path, destination_parent: Path) -> Path:
    index_path = exchange_dir / INDEX_NAME
    if not index_path.exists():
        raise ExchangeError("00_INDEX.md est introuvable.")
    index = parse_index(index_path)
    if index.get("protocol_version") != FORMAT_VERSION:
        raise ExchangeError("Cette version importe uniquement le protocole 5.0.")

    expected_count = int(index["part_count"])
    all_blocks = []
    for number in range(1, expected_count + 1):
        name = f"PART_{number:03d}.md"
        path = exchange_dir / name
        if not path.exists():
            raise ExchangeError(f"Partie manquante : {name}")
        document = path.read_text(encoding="utf-8")
        expected = next(
            (item for item in index.get("parts", []) if item.get("name") == name),
            None,
        )
        if expected and expected.get("sha256"):
            actual = sha256_bytes(document.encode("utf-8"))
            if actual != expected["sha256"]:
                raise ExchangeError(f"SHA-256 invalide pour {name}.")
        all_blocks.extend(parse_file_blocks(document))

    grouped = {}
    for block in all_blocks:
        grouped.setdefault(block["path"], []).append(block)

    temp_root = Path(tempfile.mkdtemp(prefix="pyto_exchange_v5_"))
    try:
        project_name = safe_relative_path(index.get("project_name") or "Projet_importe")
        project_root = temp_root / project_name
        project_root.mkdir(parents=True)

        for relative, blocks in grouped.items():
            blocks.sort(key=lambda item: int(item["chunk_index"]))
            chunk_count = int(blocks[0]["chunk_count"])
            if len(blocks) != chunk_count:
                raise ExchangeError(f"Fragments incomplets pour {relative}.")
            if [int(item["chunk_index"]) for item in blocks] != list(range(1, chunk_count + 1)):
                raise ExchangeError(f"Ordre de fragments invalide pour {relative}.")
            content = "".join(item["content"] for item in blocks)
            encoding = blocks[0]["encoding"]
            raw = content.encode("utf-8") if encoding == "utf-8" else base64.b64decode(content)
            expected_sha = blocks[0].get("sha256")
            if expected_sha and sha256_bytes(raw) != expected_sha:
                raise ExchangeError(f"SHA-256 invalide pour {relative}.")
            target = project_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

        for relative in index.get("deleted_paths", []):
            target = project_root / safe_relative_path(relative)
            if target.exists():
                target.unlink()

        destination = destination_parent / project_name
        if destination.exists():
            destination = destination_parent / f"{project_name}_importe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(project_root), str(destination))
        return destination
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def choose_directory(title: str) -> Path | None:
    if ui is None:
        value = input(f"{title} : ").strip()
        return Path(value).expanduser() if value else None
    picker = ui.FilePicker(title=title, allows_multiple_selection=False, select_folders=True)
    result = picker.show()
    if not result:
        return None
    return Path(result[0])


def copy_prompt() -> None:
    try:
        import pasteboard
        pasteboard.set_string(CHATGPT_PROMPT)
    except Exception:
        print(CHATGPT_PROMPT)


class App:
    def __init__(self):
        if ui is None:
            raise ExchangeError("pyto_ui est indisponible.")
        self.view = ui.View()
        self.view.background_color = ui.SystemColors.SECONDARY_SYSTEM_BACKGROUND
        self.title = ui.Label("Pyto Project Exchange 5.0")
        self.title.font = ui.Font.bold_system_font_of_size(22)
        self.title.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        self.status = ui.Label("Prêt")
        self.status.number_of_lines = 0
        self.status.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        self.buttons = []
        self._add_button("Exporter FULL", self.export_full)
        self._add_button("Exporter DELTA", self.export_delta)
        self._add_button("Importer un lot V5", self.import_lot)
        self._add_button("Copier le prompt ChatGPT", self.copy_chatgpt_prompt)
        self.view.add_subview(self.title)
        self.view.add_subview(self.status)
        self.view.layout = self.layout

    def _add_button(self, title, action):
        button = ui.Button(title=title)
        button.action = action
        self.buttons.append(button)
        self.view.add_subview(button)

    def layout(self, _sender=None):
        width = self.view.width
        self.title.frame = (20, 24, width - 40, 42)
        y = 82
        for button in self.buttons:
            button.frame = (24, y, width - 48, 48)
            y += 58
        self.status.frame = (24, y + 10, width - 48, 100)

    def _export(self, mode):
        root = choose_directory("Sélectionne le dossier du projet")
        if root is None:
            return
        destination = choose_directory("Sélectionne le dossier de destination")
        if destination is None:
            return
        try:
            output = export_project(root, destination, mode)
            self.status.text = f"Export {mode} terminé :\n{output}"
        except Exception as exc:
            self.status.text = f"Erreur : {exc}"

    def export_full(self, _sender):
        self._export("FULL")

    def export_delta(self, _sender):
        self._export("DELTA")

    def import_lot(self, _sender):
        source = choose_directory("Sélectionne le dossier du lot")
        if source is None:
            return
        destination = choose_directory("Sélectionne le dossier de destination")
        if destination is None:
            return
        try:
            output = import_project(source, destination)
            self.status.text = f"Import terminé :\n{output}"
        except Exception as exc:
            self.status.text = f"Erreur : {exc}"

    def copy_chatgpt_prompt(self, _sender):
        copy_prompt()
        self.status.text = "Prompt V5 copié dans le presse-papiers."


def main() -> None:
    if ui is None:
        print("PYTO_PROJECT_EXCHANGE 5.0")
        print("Interface Pyto indisponible.")
        return
    app = App()
    ui.show_view(app.view, ui.PRESENTATION_MODE_SHEET)


if __name__ == "__main__":
    main()
