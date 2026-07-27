import argparse
import json
from datetime import date
from pathlib import Path

import yaml


MACHINE_ENTITY_REGISTRY = Path(".registry/machine/entity_registry.yaml")
HUMAN_ENTITY_REGISTRY = Path(".registry/human/entity_registry.md")
MACHINE_ENTITY_RESOURCE_MAP = Path(".registry/machine/entity_resource_map.yaml")
HUMAN_ENTITY_RESOURCE_MAP = Path(".registry/human/entity_resource_map.md")


def read_yaml(path):
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


def md_escape(value):
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def normalize_content_file(content_file):
    rel = str(content_file or "").replace("\\", "/")
    parts = Path(rel).parts
    if not rel or Path(rel).is_absolute() or ".." in parts or not rel.startswith("entities/"):
        raise ValueError(f"unsafe entity content_file: {content_file}")
    return rel


def expected_content_path(kb_path, content_file):
    rel = normalize_content_file(content_file)
    return Path(kb_path) / Path(rel)


def registry_paths(kb_path):
    kb_path = Path(kb_path)
    return {
        "entity_registry": kb_path / MACHINE_ENTITY_REGISTRY,
        "entity_registry_md": kb_path / HUMAN_ENTITY_REGISTRY,
        "entity_resource_map": kb_path / MACHINE_ENTITY_RESOURCE_MAP,
        "entity_resource_map_md": kb_path / HUMAN_ENTITY_RESOURCE_MAP,
    }


def inspect_kb(kb_path):
    kb_path = Path(kb_path)
    paths = registry_paths(kb_path)
    registry = read_yaml(paths["entity_registry"])
    issues = []

    for entity in registry.get("entities", []) or []:
        entity_id = entity.get("entity_id")
        content_file = entity.get("content_file")
        try:
            expected_path = expected_content_path(kb_path, content_file)
        except ValueError as exc:
            issues.append(
                {
                    "issue_id": f"unsafe_entity_content_file:{entity_id}",
                    "issue_type": "unsafe_entity_content_file",
                    "fixable": False,
                    "requires_confirmation": True,
                    "entity_id": entity_id,
                    "canonical_name": entity.get("canonical_name"),
                    "content_file": content_file,
                    "message": str(exc),
                    "affected_paths": [str(paths["entity_registry"])],
                }
            )
            continue

        if not expected_path.exists():
            affected_paths = [
                str(paths["entity_registry"]),
                str(paths["entity_registry_md"]),
                str(paths["entity_resource_map"]),
                str(paths["entity_resource_map_md"]),
            ]
            try:
                root = find_root_for_kb(kb_path)
            except ValueError:
                root = None
            if root:
                affected_paths.extend(
                    [
                        str(root / "resource_registry.yaml"),
                        str(root / "resource_registry.md"),
                    ]
                )
            issues.append(
                {
                    "issue_id": f"missing_entity_content_file:{entity_id}",
                    "issue_type": "missing_entity_content_file",
                    "fixable": True,
                    "requires_confirmation": False,
                    "entity_id": entity_id,
                    "canonical_name": entity.get("canonical_name"),
                    "content_file": normalize_content_file(content_file),
                    "expected_path": str(expected_path),
                    "affected_paths": affected_paths,
                }
            )

    return {
        "kb_path": str(kb_path),
        "lint_report": "missing_entity_content_file",
        "issues": issues,
        "fixable_issue_ids": [
            issue["issue_id"]
            for issue in issues
            if issue.get("fixable") and not issue.get("requires_confirmation")
        ],
    }


def rebuild_entity_registry_md(path, registry):
    lines = [
        "# entity_registry",
        "",
        "This is the human-readable projection of the current knowledge-base entity registry.",
        "",
        "Machine authority: `.registry/machine/entity_registry.yaml`",
        "",
        "When files conflict, YAML is authoritative. Do not reverse-apply this Markdown file to YAML.",
        "",
        "| entity_id | name | type | status | content_file | resource_refs |",
        "|---|---|---|---|---|---|",
    ]
    for entity in registry.get("entities", []) or []:
        refs = entity.get("ingestion", {}).get("resource_refs", []) or []
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(entity.get("entity_id")),
                    md_escape(entity.get("canonical_name")),
                    md_escape(entity.get("entity_type")),
                    md_escape(entity.get("status")),
                    md_escape(entity.get("content_file")),
                    md_escape(", ".join(refs)),
                ]
            )
            + " |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def locator_summary(locator):
    if not isinstance(locator, dict):
        return ""
    fields = []
    for key in ("page", "section", "heading", "path_in_resource"):
        value = locator.get(key)
        if value not in (None, ""):
            fields.append(f"{key}={value}")
    quote = locator.get("quote")
    if quote:
        fields.append(f"quote={quote}")
    return "; ".join(fields)


def rebuild_entity_resource_map_md(path, entity_map):
    lines = [
        "# entity_resource_map",
        "",
        "This is the human-readable projection of entity-to-resource evidence mappings.",
        "",
        "Machine authority: `.registry/machine/entity_resource_map.yaml`",
        "",
        "When files conflict, YAML is authoritative. Do not reverse-apply this Markdown file to YAML.",
        "",
        "| entity_id | resource_id | evidence_type | evidence_location | note |",
        "|---|---|---|---|---|",
    ]
    for item in entity_map.get("mappings", []) or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(item.get("entity_id")),
                    md_escape(item.get("resource_id")),
                    md_escape(item.get("evidence_type")),
                    md_escape(locator_summary(item.get("locator"))),
                    md_escape(item.get("note")),
                ]
            )
            + " |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_root_for_kb(kb_path):
    kb_path = Path(kb_path).resolve()
    for parent in (kb_path, *kb_path.parents):
        if (parent / "resource_registry.yaml").exists():
            return parent
    raise ValueError(f"could not locate Valhalla root for kb_path: {kb_path}")


def active_wikis(root, fallback_kb_path):
    wiki_registry_path = root / "wiki_registry.yaml"
    if wiki_registry_path.exists():
        registry = read_yaml(wiki_registry_path)
        return [
            {"kb_name": item["kb_name"], "wiki_path": item["wiki_path"]}
            for item in registry.get("wikis", []) or []
            if item.get("status") == "active"
        ]

    fallback_kb_path = Path(fallback_kb_path).resolve()
    wiki_path = fallback_kb_path.relative_to(root).as_posix()
    kb_name = fallback_kb_path.name.removeprefix("Wiki_")
    return [{"kb_name": kb_name, "wiki_path": wiki_path}]


def build_resource_usage_index(root, fallback_kb_path):
    root = Path(root)
    index = {}
    for wiki in active_wikis(root, fallback_kb_path):
        kb_name = wiki["kb_name"]
        wiki_path = wiki["wiki_path"]
        wiki_root = root / wiki_path
        registry = read_yaml(wiki_root / MACHINE_ENTITY_REGISTRY)
        entity_map = read_yaml(wiki_root / MACHINE_ENTITY_RESOURCE_MAP)
        entity_files = {
            entity.get("entity_id"): entity.get("content_file")
            for entity in registry.get("entities", []) or []
            if entity.get("entity_id")
        }
        for mapping in entity_map.get("mappings", []) or []:
            resource_id = mapping.get("resource_id")
            entity_id = mapping.get("entity_id")
            content_file = entity_files.get(entity_id)
            if not resource_id or not entity_id or not content_file:
                continue
            content_file = normalize_content_file(content_file)
            index.setdefault(resource_id, {})[(kb_name, entity_id)] = {
                "kb_name": kb_name,
                "entity_id": entity_id,
                "entity_file": f"{wiki_path}/{content_file}".replace("\\", "/"),
            }
    return index


def public_copy_path(resource):
    for representation in resource.get("representations", []) or []:
        public_copy = representation.get("public_copy") or {}
        path = public_copy.get("path")
        if path:
            return path
    return ""


def rebuild_resource_registry_md(path, registry):
    lines = [
        "# Resource Registry",
        "",
        "| resource_id | canonical_name | status | reference_count | public_copy |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for resource in registry.get("resources", []) or []:
        identity = resource.get("identity") or {}
        lifecycle = resource.get("lifecycle") or {}
        usage = resource.get("usage") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(resource.get("resource_id")),
                    md_escape(identity.get("canonical_name") or resource.get("canonical_name")),
                    md_escape(lifecycle.get("status") or resource.get("status")),
                    md_escape(usage.get("reference_count", 0)),
                    md_escape(public_copy_path(resource)),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_resource_usage(root, fallback_kb_path):
    root = Path(root)
    registry_path = root / "resource_registry.yaml"
    registry_md_path = root / "resource_registry.md"
    registry = read_yaml(registry_path)
    usage_index = build_resource_usage_index(root, fallback_kb_path)
    today = date.today().isoformat()

    for resource in registry.get("resources", []) or []:
        resource_id = resource.get("resource_id")
        refs = sorted(
            usage_index.get(resource_id, {}).values(),
            key=lambda item: (item["kb_name"], item["entity_id"], item["entity_file"]),
        )
        resource["usage"] = {
            "referenced_by": refs,
            "reference_count": len(refs),
            "computed_at": today,
        }

    write_yaml(registry_path, registry)
    rebuild_resource_registry_md(registry_md_path, registry)
    return [str(registry_path), str(registry_md_path)]


def fix_kb(kb_path, selected_issue_ids, lint_report):
    kb_path = Path(kb_path)
    paths = registry_paths(kb_path)
    selected = set(selected_issue_ids)
    report_issues = {
        issue["issue_id"]: issue for issue in lint_report.get("issues", []) or []
    }

    missing_issue_ids = []
    for issue_id in selected:
        issue = report_issues.get(issue_id)
        if not issue:
            raise ValueError(f"selected issue not found in lint_report: {issue_id}")
        if issue.get("issue_type") != "missing_entity_content_file":
            raise ValueError(f"selected issue is not a missing content issue: {issue_id}")
        if not issue.get("fixable") or issue.get("requires_confirmation"):
            raise ValueError(f"selected issue is not automatically fixable: {issue_id}")
        missing_issue_ids.append(issue_id)

    remove_entity_ids = {report_issues[issue_id]["entity_id"] for issue_id in missing_issue_ids}
    registry = read_yaml(paths["entity_registry"])
    entity_map = read_yaml(paths["entity_resource_map"])

    original_entities = registry.get("entities", []) or []
    original_mappings = entity_map.get("mappings", []) or []
    kept_entities = [
        entity for entity in original_entities if entity.get("entity_id") not in remove_entity_ids
    ]
    removed_entities = [
        entity for entity in original_entities if entity.get("entity_id") in remove_entity_ids
    ]
    kept_mappings = [
        item for item in original_mappings if item.get("entity_id") not in remove_entity_ids
    ]
    removed_mappings = [
        item for item in original_mappings if item.get("entity_id") in remove_entity_ids
    ]

    today = date.today().isoformat()
    registry["entities"] = kept_entities
    registry["updated_at"] = today
    entity_map["mappings"] = kept_mappings
    entity_map["updated_at"] = today

    write_yaml(paths["entity_registry"], registry)
    write_yaml(paths["entity_resource_map"], entity_map)
    rebuild_entity_registry_md(paths["entity_registry_md"], registry)
    rebuild_entity_resource_map_md(paths["entity_resource_map_md"], entity_map)
    root = find_root_for_kb(kb_path)
    resource_usage_files = sync_resource_usage(root, kb_path) if removed_entities else []

    return {
        "lint_fix_report": "missing_entity_content_file",
        "kb_path": str(kb_path),
        "selected_issue_ids": sorted(selected),
        "removed_entity_ids": [entity.get("entity_id") for entity in removed_entities],
        "removed_mapping_ids": [item.get("map_id") for item in removed_mappings],
        "next_operation": None,
        "modified_files": [
            str(paths["entity_registry"]),
            str(paths["entity_registry_md"]),
            str(paths["entity_resource_map"]),
            str(paths["entity_resource_map_md"]),
            *resource_usage_files,
        ],
        "preserved_files": [
            issue.get("expected_path")
            for issue in report_issues.values()
            if issue.get("issue_id") in selected
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--kb", required=True)

    fix_parser = subparsers.add_parser("fix")
    fix_parser.add_argument("--kb", required=True)
    fix_parser.add_argument("--issue-id", action="append", required=True)
    fix_parser.add_argument("--report-json")

    args = parser.parse_args()
    if args.command == "inspect":
        print(json.dumps(inspect_kb(args.kb), ensure_ascii=False, indent=2))
        return

    if args.report_json:
        report = json.loads(Path(args.report_json).read_text(encoding="utf-8-sig"))
    else:
        report = inspect_kb(args.kb)
    print(json.dumps(fix_kb(args.kb, args.issue_id, report), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
