#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from datetime import datetime
from pathlib import Path

import yaml


REGISTRY_FILE = Path.home() / ".codex" / "valhalla" / "roots.json"
CURRENT_STATE_RELATIVE_PATH = Path(".valhalla") / "kb_status.md"


class StatusLoader(yaml.SafeLoader):
    pass


StatusLoader.yaml_implicit_resolvers = {
    key: [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def fail(message: str, code: int = 1) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(code)


def load_json(path: Path) -> dict:
    if not path.exists():
        fail(f"File does not exist: {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON: {path} | {e}")
    except OSError as e:
        fail(f"Failed to read file: {path} | {e}")

    if not isinstance(data, dict):
        fail(f"The JSON root must be an object: {path}")

    return data


def load_yaml(path: Path) -> dict:
    if not path.exists():
        fail(f"File does not exist: {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            data = yaml.load(f, Loader=StatusLoader)
    except yaml.YAMLError as e:
        fail(f"Invalid YAML: {path} | {e}")
    except OSError as e:
        fail(f"Failed to read file: {path} | {e}")

    if not isinstance(data, dict):
        fail(f"The YAML root must be an object: {path}")

    return data


def validate_date(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        fail(f"{field_name} must be a string.")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        fail(f"{field_name} must use YYYY-MM-DD format.")


def validate_roots_registry(registry: dict) -> None:
    required = ["version", "current_root", "roots"]

    for key in required:
        if key not in registry:
            fail(f"roots.json is missing field: {key}")

    if registry["version"] != 1:
        fail("roots.json version must be 1.")

    if registry["current_root"] is not None and not isinstance(registry["current_root"], str):
        fail("roots.json current_root must be a string or null.")

    if not isinstance(registry["roots"], list):
        fail("roots.json roots must be an array.")

    for index, root in enumerate(registry["roots"]):
        if not isinstance(root, dict):
            fail(f"roots[{index}] must be an object.")

        allowed = {"alias", "path", "created_at", "last_used_at", "note"}
        required_root_keys = allowed

        extra = set(root.keys()) - allowed
        if extra:
            fail(f"roots[{index}] contains unsupported fields: {', '.join(sorted(extra))}")

        missing = required_root_keys - set(root.keys())
        if missing:
            fail(f"roots[{index}] is missing fields: {', '.join(sorted(missing))}")

        if not isinstance(root["alias"], str) or not root["alias"].strip():
            fail(f"roots[{index}].alias must be a non-empty string.")

        if not isinstance(root["path"], str) or not root["path"].strip():
            fail(f"roots[{index}].path must be a non-empty string.")

        validate_date(root["created_at"], f"roots[{index}].created_at")
        validate_date(root["last_used_at"], f"roots[{index}].last_used_at")

        if not isinstance(root["note"], str):
            fail(f"roots[{index}].note must be a string.")


def get_current_root(registry: dict) -> dict:
    current_alias = registry["current_root"]

    if current_alias is None:
        fail("No Valhalla root is active: current_root is null.")

    matches = [
        root for root in registry["roots"]
        if root["alias"] == current_alias
    ]

    if not matches:
        fail(f"The root referenced by current_root does not exist: {current_alias}")

    if len(matches) > 1:
        fail(f"roots.json contains a duplicate alias: {current_alias}")

    return matches[0]


def validate_idle_state(data: dict) -> None:
    if data["target_wiki_path"] is not None:
        fail("target_wiki_path must be null when the state is idle.")


def validate_kb_state(data: dict, state: str) -> None:
    kb_name = state.removeprefix("kb:")
    if not kb_name or any(character in kb_name for character in " \t\r\n:/\\"):
        fail("kb_status must use kb:<name>, and the name must not contain whitespace, colons, or path separators.")

    expected_path = f"Wiki/Wiki_{kb_name}"
    if data["target_wiki_path"] != expected_path:
        fail(f"target_wiki_path does not match kb_status; expected: {expected_path}")


def validate_current_state(data: dict) -> str:
    required = {"kb_status", "target_wiki_path"}
    missing = required - set(data)
    if missing:
        fail(f"kb_status.md is missing fields: {', '.join(sorted(missing))}")

    allowed = required
    extra = set(data.keys()) - allowed
    if extra:
        fail(f"kb_status.md contains unsupported fields: {', '.join(sorted(extra))}")

    state = data["kb_status"]

    if state == "idle":
        validate_idle_state(data)
        return "idle"

    if isinstance(state, str) and state.startswith("kb:"):
        validate_kb_state(data, state)
        return "kb"

    fail("kb_status must be either idle or kb:<name>.")


def print_status(root: dict, current_state: dict, status_type: str) -> None:
    print("Valhalla Root")
    print(f"Root Alias: {root['alias']}")
    print(f"Root Path:  {root['path']}")
    print("")

    if status_type == "idle":
        print("KB Status: idle")
        print("Current mode: no active knowledge base")
        return

    kb_name = current_state["kb_status"].removeprefix("kb:")
    print(f"KB Status: {current_state['kb_status']}")
    print("Current mode: knowledge base active")
    print(f"Knowledge-base name: {kb_name}")
    print(f"Target path: {current_state['target_wiki_path']}")


def main() -> None:
    registry = load_json(REGISTRY_FILE)
    validate_roots_registry(registry)

    current_root = get_current_root(registry)
    root_path = Path(current_root["path"]).expanduser()
    current_state_file = root_path / CURRENT_STATE_RELATIVE_PATH

    current_state = load_yaml(current_state_file)
    status_type = validate_current_state(current_state)

    print_status(current_root, current_state, status_type)


if __name__ == "__main__":
    main()
