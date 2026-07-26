from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from core.importer import add_project, import_script
from core.paths import HISTORY_FILE, PROJECTS_DIR, REGISTRY_FILE, SCRIPTS_DIR, ensure_directories
from core.registry import Registry
from core.service import rename_item, run_by_id


def reset_data() -> None:
    ensure_directories()
    REGISTRY_FILE.write_text('{"version": 1, "items": []}\n', encoding="utf-8")
    HISTORY_FILE.write_text('{"version": 1, "runs": []}\n', encoding="utf-8")
    shutil.rmtree(SCRIPTS_DIR, ignore_errors=True)
    shutil.rmtree(PROJECTS_DIR, ignore_errors=True)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def run_cycle(index: int) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        standalone = tmp_path / f"standalone_{index}.py"
        standalone.write_text(f"print('standalone-{index}')\n", encoding="utf-8")
        script_item = import_script(standalone, registry=Registry.load())
        renamed = rename_item(script_item.id, f"Script {index}")
        assert renamed.name == f"Script {index}"
        _, script_result = run_by_id(script_item.id)
        assert script_result.success
        assert f"standalone-{index}" in script_result.output

        project_root = tmp_path / f"project_{index}"
        project_root.mkdir()
        (project_root / "helper.py").write_text("def value():\n    return 'project-ok'\n", encoding="utf-8")
        (project_root / "main.py").write_text("from helper import value\nprint(value())\n", encoding="utf-8")
        project_item = add_project(project_root, "main.py", registry=Registry.load())
        assert project_item.entry_script == "main.py"
        _, project_result = run_by_id(project_item.id)
        assert project_result.success
        assert "project-ok" in project_result.output

        registry = Registry.load()
        assert registry.require(script_item.id).run_count == 1
        assert registry.require(project_item.id).run_count == 1


def main() -> None:
    reset_data()
    for index in range(1, 11):
        run_cycle(index)
        print(f"Cycle {index}/10 : OK")

    payload = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    assert len(payload.get("runs", [])) == 20
    print("=== 10 CYCLES VALIDÉS ===")


if __name__ == "__main__":
    main()
