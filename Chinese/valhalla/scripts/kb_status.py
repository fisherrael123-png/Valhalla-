#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path
from datetime import datetime
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
        fail(f"文件不存在：{path}")

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"JSON 格式错误：{path} | {e}")
    except OSError as e:
        fail(f"读取文件失败：{path} | {e}")

    if not isinstance(data, dict):
        fail(f"JSON 根结构必须是 object：{path}")

    return data


def load_yaml(path: Path) -> dict:
    if not path.exists():
        fail(f"文件不存在：{path}")

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            data = yaml.load(f, Loader=StatusLoader)
    except yaml.YAMLError as e:
        fail(f"YAML 格式错误：{path} | {e}")
    except OSError as e:
        fail(f"读取文件失败：{path} | {e}")

    if not isinstance(data, dict):
        fail(f"YAML 根结构必须是 object：{path}")

    return data


def validate_date(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        fail(f"{field_name} 必须是字符串。")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        fail(f"{field_name} 必须使用 YYYY-MM-DD 格式。")


def validate_roots_registry(registry: dict) -> None:
    required = ["version", "current_root", "roots"]

    for key in required:
        if key not in registry:
            fail(f"roots.json 缺少字段：{key}")

    if registry["version"] != 1:
        fail("roots.json 的 version 必须为 1。")

    if registry["current_root"] is not None and not isinstance(registry["current_root"], str):
        fail("roots.json 的 current_root 必须是 string 或 null。")

    if not isinstance(registry["roots"], list):
        fail("roots.json 的 roots 必须是 array。")

    for index, root in enumerate(registry["roots"]):
        if not isinstance(root, dict):
            fail(f"roots[{index}] 必须是 object。")

        allowed = {"alias", "path", "created_at", "last_used_at", "note"}
        required_root_keys = allowed

        extra = set(root.keys()) - allowed
        if extra:
            fail(f"roots[{index}] 存在非法字段：{', '.join(sorted(extra))}")

        missing = required_root_keys - set(root.keys())
        if missing:
            fail(f"roots[{index}] 缺少字段：{', '.join(sorted(missing))}")

        if not isinstance(root["alias"], str) or not root["alias"].strip():
            fail(f"roots[{index}].alias 必须是非空字符串。")

        if not isinstance(root["path"], str) or not root["path"].strip():
            fail(f"roots[{index}].path 必须是非空字符串。")

        validate_date(root["created_at"], f"roots[{index}].created_at")
        validate_date(root["last_used_at"], f"roots[{index}].last_used_at")

        if not isinstance(root["note"], str):
            fail(f"roots[{index}].note 必须是字符串。")


def get_current_root(registry: dict) -> dict:
    current_alias = registry["current_root"]

    if current_alias is None:
        fail("当前没有激活任何 Valhalla Root：current_root 为 null。")

    matches = [
        root for root in registry["roots"]
        if root["alias"] == current_alias
    ]

    if not matches:
        fail(f"current_root 指向的 root 不存在：{current_alias}")

    if len(matches) > 1:
        fail(f"roots.json 中存在重复 alias：{current_alias}")

    return matches[0]


def validate_idle_state(data: dict) -> None:
    if data["target_wiki_path"] is not None:
        fail("idle 状态下，target_wiki_path 必须为 null。")


def validate_kb_state(data: dict, state: str) -> None:
    kb_name = state.removeprefix("kb:")
    if not kb_name or any(character in kb_name for character in " \t\r\n:/\\"):
        fail("kb_status 必须使用 kb:<name>，且名称不得包含空白、冒号或路径分隔符。")

    expected_path = f"Wiki/Wiki_{kb_name}"
    if data["target_wiki_path"] != expected_path:
        fail(f"target_wiki_path 与 kb_status 不一致，应为：{expected_path}")


def validate_current_state(data: dict) -> str:
    required = {"kb_status", "target_wiki_path"}
    missing = required - set(data)
    if missing:
        fail(f"kb_status.md 缺少字段：{', '.join(sorted(missing))}")

    allowed = required
    extra = set(data.keys()) - allowed
    if extra:
        fail(f"kb_status.md 存在非法字段：{', '.join(sorted(extra))}")

    state = data["kb_status"]

    if state == "idle":
        validate_idle_state(data)
        return "idle"

    if isinstance(state, str) and state.startswith("kb:"):
        validate_kb_state(data, state)
        return "kb"

    fail("kb_status 只能是 idle 或 kb:<name>。")


def print_status(root: dict, current_state: dict, status_type: str) -> None:
    print("Valhalla Root")
    print(f"Root Alias：{root['alias']}")
    print(f"Root Path ：{root['path']}")
    print("")

    if status_type == "idle":
        print("KB Status ：idle")
        print("当前模式：未激活知识库")
        return

    kb_name = current_state["kb_status"].removeprefix("kb:")
    print(f"KB Status ：{current_state['kb_status']}")
    print("当前模式：知识库已激活")
    print(f"知识库名称：{kb_name}")
    print(f"目标路径：{current_state['target_wiki_path']}")


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



