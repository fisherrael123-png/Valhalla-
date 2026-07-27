import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8-sig")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_kb_status_contract():
    template = yaml.safe_load(read_text("template/kb_status_template.yaml"))
    require(
        template == {"kb_status": "idle", "target_wiki_path": None},
        "kb status template must contain only idle kb_status and null target_wiki_path",
    )

    schema = json.loads(read_text("schema/kb_status_schema.json"))
    require(
        schema["required"] == ["kb_status", "target_wiki_path"],
        "kb status schema must require exactly kb_status and target_wiki_path",
    )
    require(
        set(schema["properties"]) == {"kb_status", "target_wiki_path"},
        "kb status schema must define only kb_status and target_wiki_path",
    )

    script = read_text("scripts/kb_status.py")
    for legacy_field in ("session_state", "active_kb", "updated_at", 'data["note"]'):
        require(legacy_field not in script, f"kb_status.py still uses {legacy_field}")

    start_workflow = read_text("workflows/kb/start_kb.md")
    require("kb_status: kb:<name>" in start_workflow, "start_kb must write kb_status")
    require(
        "target_wiki_path: Wiki/Wiki_<name>" in start_workflow,
        "start_kb must write target_wiki_path",
    )

    exit_workflow = read_text("workflows/kb/exit_kb.md")
    require("kb_status: idle" in exit_workflow, "exit_kb must restore idle")
    require("target_wiki_path: null" in exit_workflow, "exit_kb must clear target path")


def validate_entity_content_file_contract():
    template = yaml.safe_load(
        read_text("template/knowledge_base/entity/entity_entry_template.yaml")
    )
    require(
        template[0]["content_file"] == "entities/ent_000001_knowledge_graph.md",
        "entity template content_file must be relative to the knowledge-base directory",
    )

    schema = json.loads(read_text("schema/entity_registry_schema.json"))
    pattern = schema["$defs"]["entity"]["properties"]["content_file"]["pattern"]
    require(
        pattern == r"^entities/ent_[0-9]{6}_[^/\\]+\.md$",
        "entity content_file schema must accept only a direct entities/ relative path",
    )

    ingest = read_text("workflows/kb/ingest.md")
    for token in (
        "relative to the current knowledge-base directory",
        "must not contain a `Wiki/Wiki_<knowledge-base-name>/` prefix",
        "be absolute",
        "contain `..`",
    ):
        require(token in ingest, f"ingest workflow is missing entity path rule: {token}")


def main():
    validate_kb_status_contract()
    validate_entity_content_file_contract()
    print("PASS: kb status and entity content-file contracts are synchronized")


if __name__ == "__main__":
    main()



