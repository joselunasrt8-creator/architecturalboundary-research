import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate.py"
spec = importlib.util.spec_from_file_location("repository_validate_workspace_layout", SCRIPT)
repository_validate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = repository_validate
spec.loader.exec_module(repository_validate)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")


def create_workspace(root: Path, base: str) -> None:
    for item in repository_validate.INVESTIGATION_WORKSPACE_ITEMS:
        path = root / base / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")


def test_workspace_layout_includes_every_registered_investigation(tmp_path, monkeypatch):
    create_workspace(tmp_path, "investigations/registered-later")
    write_json(tmp_path / "registry/investigations.json", {"investigations": [
        {"id": "registered-later", "path": "investigations/registered-later"},
    ]})
    monkeypatch.setattr(repository_validate, "ROOT", tmp_path)

    repository_validate.validate_investigation_workspace_layout()


def test_workspace_layout_rejects_missing_item_in_registered_investigation(tmp_path, monkeypatch):
    create_workspace(tmp_path, "investigations/registered-later")
    (tmp_path / "investigations/registered-later/artifacts/README.md").unlink()
    write_json(tmp_path / "registry/investigations.json", {"investigations": [
        {"id": "registered-later", "path": "investigations/registered-later"},
    ]})
    monkeypatch.setattr(repository_validate, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="investigations/registered-later/artifacts/README.md"):
        repository_validate.validate_investigation_workspace_layout()


def test_workspace_layout_reports_registered_workspaces_in_path_order(tmp_path, monkeypatch):
    create_workspace(tmp_path, "investigations/a-study")
    create_workspace(tmp_path, "investigations/z-study")
    (tmp_path / "investigations/a-study/investigation-design.md").unlink()
    (tmp_path / "investigations/z-study/investigation-design.md").unlink()
    write_json(tmp_path / "registry/investigations.json", {"investigations": [
        {"id": "z-study", "path": "investigations/z-study"},
        {"id": "a-study", "path": "investigations/a-study"},
    ]})
    monkeypatch.setattr(repository_validate, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="investigations/a-study/investigation-design.md"):
        repository_validate.validate_investigation_workspace_layout()
