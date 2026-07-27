import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml


STATE_DIR = Path.home() / ".codex" / "valhalla"
ROOTS_FILE = STATE_DIR / "roots.json"
ENTITY_ID_RE = re.compile(r"^ent_[0-9]{6}$")
ENTITY_FILE_RE = re.compile(r"^Wiki/Wiki_[^/\\]+/entities/ent_[0-9]{6}[^/]*\.md$")


def load_yaml(path):
    with path.open("r", encoding="utf-8-sig") as file:
        return yaml.safe_load(file) or {}


def load_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def current_root():
    roots = load_json(ROOTS_FILE)
    current_alias = roots["current_root"]
    for root in roots.get("roots", []):
        if root.get("alias") == current_alias:
            return Path(root["path"])
    raise SystemExit(f"current root alias not found: {current_alias}")


def active_wikis(root):
    registry = load_yaml(root / "wiki_registry.yaml")
    return [
        {"kb_name": item["kb_name"], "wiki_path": item["wiki_path"]}
        for item in registry.get("wikis") or []
        if item.get("status") == "active"
    ]


def build_target_usage(root, wikis):
    target = defaultdict(dict)
    missing_resource_refs = set()
    invalid_content_files = []
    resource_registry = load_yaml(root / "resource_registry.yaml")
    resource_ids = {
        resource.get("resource_id")
        for resource in resource_registry.get("resources") or []
        if resource.get("resource_id")
    }

    entity_count = 0
    mapping_count = 0
    for wiki in wikis:
        kb_name = wiki["kb_name"]
        wiki_path = wiki["wiki_path"]
        wiki_root = root / wiki_path
        entity_registry = load_yaml(wiki_root / ".registry" / "machine" / "entity_registry.yaml")
        entity_resource_map = load_yaml(wiki_root / ".registry" / "machine" / "entity_resource_map.yaml")

        entity_files = {}
        for entity in entity_registry.get("entities") or []:
            entity_id = entity.get("entity_id")
            content_file = entity.get("content_file")
            if not entity_id:
                continue
            entity_count += 1
            entity_files[entity_id] = content_file

        for mapping in entity_resource_map.get("mappings") or []:
            resource_id = mapping.get("resource_id")
            entity_id = mapping.get("entity_id")
            if not resource_id or not entity_id:
                continue
            mapping_count += 1
            if resource_id not in resource_ids:
                missing_resource_refs.add(resource_id)
                continue
            content_file = entity_files.get(entity_id)
            if (
                not isinstance(content_file, str)
                or not content_file.startswith("entities/")
                or ".." in Path(content_file).parts
            ):
                invalid_content_files.append(
                    {"kb_name": kb_name, "entity_id": entity_id, "content_file": content_file}
                )
                continue
            target[resource_id][(kb_name, entity_id)] = {
                "kb_name": kb_name,
                "entity_id": entity_id,
                "entity_file": f"{wiki_path}/{content_file}".replace("\\", "/"),
            }

    return {
        "target": target,
        "entity_count": entity_count,
        "mapping_count": mapping_count,
        "missing_resource_refs": sorted(missing_resource_refs),
        "invalid_content_files": invalid_content_files,
    }


def classify_reference(reference):
    if isinstance(reference, str):
        if reference.startswith("Wiki/Wiki_"):
            return "legacy_full_path_string"
        if reference.startswith("entities/"):
            return "legacy_relative_entity_string"
        return "legacy_other_string"
    if isinstance(reference, dict):
        if set(reference) == {"kb_name", "entity_id", "entity_file"}:
            return "canonical"
        if "kb" in reference:
            return "legacy_kb_dict"
        return "legacy_other_dict"
    return type(reference).__name__


def validate_registry(root):
    wikis = active_wikis(root)
    active_names = {wiki["kb_name"] for wiki in wikis}
    target_result = build_target_usage(root, wikis)
    target = target_result["target"]
    registry = load_yaml(root / "resource_registry.yaml")

    legacy_counts = defaultdict(int)
    malformed_refs = []
    extra_refs = []
    missing_refs = []
    reference_count_mismatches = []

    for resource in registry.get("resources") or []:
        resource_id = resource.get("resource_id")
        usage = resource.get("usage") or {}
        references = usage.get("referenced_by") or []
        actual = {}
        for index, reference in enumerate(references):
            kind = classify_reference(reference)
            if kind != "canonical":
                legacy_counts[kind] += 1
                malformed_refs.append({"resource_id": resource_id, "index": index, "kind": kind})
                continue
            kb_name = reference["kb_name"]
            entity_id = reference["entity_id"]
            entity_file = reference["entity_file"]
            if kb_name not in active_names or not ENTITY_ID_RE.match(entity_id) or not ENTITY_FILE_RE.match(entity_file):
                malformed_refs.append({"resource_id": resource_id, "index": index, "kind": "invalid_canonical"})
                continue
            actual[(kb_name, entity_id)] = reference

        expected = target.get(resource_id, {})
        for key, expected_ref in expected.items():
            if actual.get(key) != expected_ref:
                missing_refs.append({"resource_id": resource_id, "kb_name": key[0], "entity_id": key[1]})
        for key in actual:
            if key not in expected:
                extra_refs.append({"resource_id": resource_id, "kb_name": key[0], "entity_id": key[1]})

        expected_count = len(expected)
        actual_count = usage.get("reference_count")
        if actual_count != expected_count:
            reference_count_mismatches.append(
                {"resource_id": resource_id, "actual": actual_count, "expected": expected_count}
            )

    errors = []
    if target_result["missing_resource_refs"]:
        errors.append(f"missing resource ids: {', '.join(target_result['missing_resource_refs'])}")
    if target_result["invalid_content_files"]:
        errors.append(f"invalid content_file entries: {len(target_result['invalid_content_files'])}")
    if malformed_refs:
        errors.append(f"malformed or legacy usage entries: {len(malformed_refs)}")
    if missing_refs:
        errors.append(f"missing canonical usage entries: {len(missing_refs)}")
    if extra_refs:
        errors.append(f"extra canonical usage entries: {len(extra_refs)}")
    if reference_count_mismatches:
        errors.append(f"reference_count mismatches: {len(reference_count_mismatches)}")

    print("RESOURCE_USAGE_CANONICAL_CHECK")
    print(f"root: {root}")
    print(f"active_kbs: {', '.join(sorted(active_names)) if active_names else '[]'}")
    print(f"active_entity_count: {target_result['entity_count']}")
    print(f"entity_resource_mapping_count_raw: {target_result['mapping_count']}")
    print(f"target_resource_count: {len(target)}")
    print(f"legacy_counts: {dict(sorted(legacy_counts.items()))}")
    print(f"malformed_or_legacy_usage_entries: {len(malformed_refs)}")
    print(f"missing_canonical_usage_entries: {len(missing_refs)}")
    print(f"extra_canonical_usage_entries: {len(extra_refs)}")
    print(f"reference_count_mismatches: {len(reference_count_mismatches)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PASS: resource usage is canonical and derived from entity_resource_map")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    validate_registry(args.root or current_root())


if __name__ == "__main__":
    main()
