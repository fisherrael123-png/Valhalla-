import importlib.util
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "lint_missing_entity_content.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("lint_missing_entity_content", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entity(entity_id, name, content_file):
    return {
        "entity_id": entity_id,
        "canonical_name": name,
        "entity_type": "concept",
        "aliases": [],
        "content_file": content_file,
        "description": name,
        "status": "active",
        "content_status": "active",
        "extraction_status": "complete",
        "language": "en",
        "tags": [],
        "ingestion": {
            "resource_refs": ["res_000001"],
            "last_ingested_at": "2026-06-24",
            "ingestion_note": None,
        },
        "metadata": {
            "created_at": "2026-06-24",
            "updated_at": "2026-06-24",
            "created_by": "script",
        },
    }


def mapping(map_id, entity_id):
    return {
        "map_id": map_id,
        "entity_id": entity_id,
        "resource_id": "res_000001",
        "evidence_type": "mentions",
        "locator": {
            "page": 1,
            "section": None,
            "heading": None,
            "quote": "sample quote",
            "path_in_resource": None,
        },
        "confidence": "high",
        "weight": 1.0,
        "metadata": {
            "created_at": "2026-06-24",
            "updated_at": "2026-06-24",
            "created_by": "script",
        },
    }


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def build_fixture(root):
    kb = root / "Wiki" / "Wiki_Test"
    machine = kb / ".registry" / "machine"
    human = kb / ".registry" / "human"
    (kb / "entities").mkdir(parents=True)
    human.mkdir(parents=True)

    (kb / "entities" / "ent_000001_valid.md").write_text("# Valid\n", encoding="utf-8")

    write_yaml(
        machine / "entity_registry.yaml",
        {
            "version": 1,
            "kb": "Test",
            "updated_at": "2026-06-24",
            "entities": [
                entity("ent_000001", "Valid Entity", "entities/ent_000001_valid.md"),
                entity("ent_000002", "Missing Entity", "entities/ent_000002_missing.md"),
            ],
        },
    )
    write_yaml(
        machine / "entity_resource_map.yaml",
        {
            "version": 1,
            "kb": "Test",
            "updated_at": "2026-06-24",
            "mappings": [
                mapping("erm_000001", "ent_000001"),
                mapping("erm_000002", "ent_000002"),
            ],
        },
    )
    (human / "entity_registry.md").write_text("stale registry projection\n", encoding="utf-8")
    (human / "entity_resource_map.md").write_text("stale map projection\n", encoding="utf-8")

    write_yaml(
        root / "wiki_registry.yaml",
        {
            "registry": "wiki_registry",
            "version": 1,
            "wikis": [
                {
                    "kb_name": "Test",
                    "wiki_path": "Wiki/Wiki_Test",
                    "status": "active",
                }
            ],
        },
    )
    write_yaml(
        root / "resource_registry.yaml",
        {
            "version": 1,
            "resources": [
                {
                    "resource_id": "res_000001",
                    "canonical_name": "Fixture Resource",
                    "usage": {
                        "reference_count": 2,
                        "computed_at": "2026-06-24",
                        "referenced_by": [
                            {
                                "kb_name": "Test",
                                "entity_id": "ent_000001",
                                "entity_file": "Wiki/Wiki_Test/entities/ent_000001_valid.md",
                            },
                            {
                                "kb_name": "Test",
                                "entity_id": "ent_000002",
                                "entity_file": "Wiki/Wiki_Test/entities/ent_000002_missing.md",
                            },
                        ],
                    },
                }
            ],
        },
    )
    (root / "resource_registry.md").write_text("stale resource projection\n", encoding="utf-8")
    return kb


def main():
    helper = load_helper()
    with tempfile.TemporaryDirectory() as tmp:
        kb = build_fixture(Path(tmp))

        report = helper.inspect_kb(kb)
        issues = report["issues"]
        assert len(issues) == 1
        assert issues[0]["issue_id"] == "missing_entity_content_file:ent_000002"
        assert issues[0]["fixable"] is True
        assert issues[0]["requires_confirmation"] is False
        assert issues[0]["entity_id"] == "ent_000002"
        affected_paths = "\n".join(issues[0]["affected_paths"])
        assert "entity_registry.yaml" in affected_paths
        assert "entity_resource_map.yaml" in affected_paths
        assert "resource_registry.yaml" in affected_paths
        assert "resource_registry.md" in affected_paths

        fix_report = helper.fix_kb(
            kb,
            ["missing_entity_content_file:ent_000002"],
            report,
        )
        assert fix_report["removed_entity_ids"] == ["ent_000002"]
        assert fix_report["removed_mapping_ids"] == ["erm_000002"]
        assert fix_report["next_operation"] is None
        modified_files = "\n".join(fix_report["modified_files"])
        assert "resource_registry.yaml" in modified_files
        assert "resource_registry.md" in modified_files

        entity_registry = yaml.safe_load(
            (kb / ".registry" / "machine" / "entity_registry.yaml").read_text(encoding="utf-8")
        )
        entity_ids = [item["entity_id"] for item in entity_registry["entities"]]
        assert entity_ids == ["ent_000001"]

        entity_map = yaml.safe_load(
            (kb / ".registry" / "machine" / "entity_resource_map.yaml").read_text(
                encoding="utf-8"
            )
        )
        map_entity_ids = [item["entity_id"] for item in entity_map["mappings"]]
        assert map_entity_ids == ["ent_000001"]

        resource_registry = yaml.safe_load(
            (Path(tmp) / "resource_registry.yaml").read_text(encoding="utf-8")
        )
        usage = resource_registry["resources"][0]["usage"]
        assert usage["reference_count"] == 1
        assert usage["referenced_by"] == [
            {
                "kb_name": "Test",
                "entity_id": "ent_000001",
                "entity_file": "Wiki/Wiki_Test/entities/ent_000001_valid.md",
            }
        ]
        assert usage["computed_at"]
        resource_registry_md = (Path(tmp) / "resource_registry.md").read_text(encoding="utf-8")
        assert "| res_000001 | Fixture Resource |  | 1 |  |" in resource_registry_md

        registry_md = (kb / ".registry" / "human" / "entity_registry.md").read_text(
            encoding="utf-8"
        )
        map_md = (kb / ".registry" / "human" / "entity_resource_map.md").read_text(
            encoding="utf-8"
        )
        assert "ent_000001" in registry_md
        assert "ent_000002" not in registry_md
        assert "ent_000001" in map_md
        assert "ent_000002" not in map_md
        assert (kb / "entities" / "ent_000001_valid.md").exists()

    print("PASS: missing entity content lint helper")


if __name__ == "__main__":
    main()
