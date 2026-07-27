import json
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
STATE_DIR = Path.home() / ".codex" / "valhalla"
STATUS_FILE = STATE_DIR / "os_status.json"
ROOTS_FILE = STATE_DIR / "roots.json"
STATUS_TEMPLATE = SKILL_DIR / "template" / "status_template.json"
ROOTS_TEMPLATE = SKILL_DIR / "template" / "roots_template.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def valid_status(data):
    return (
        isinstance(data, dict)
        and set(data) == {"version", "status"}
        and data["version"] == 1
        and data["status"] in {"base", "admin"}
    )


def valid_root_entry(entry):
    required = {"alias", "path", "created_at", "last_used_at", "note"}
    return (
        isinstance(entry, dict)
        and set(entry) == required
        and all(isinstance(entry[key], str) for key in required)
        and bool(entry["alias"].strip())
        and bool(entry["path"].strip())
    )


def valid_roots(data):
    return (
        isinstance(data, dict)
        and set(data) == {"version", "current_root", "roots"}
        and data["version"] == 1
        and (
            data["current_root"] is None
            or isinstance(data["current_root"], str)
        )
        and isinstance(data["roots"], list)
        and all(valid_root_entry(entry) for entry in data["roots"])
    )


def load_or_rebuild(path, template_path, validator):
    try:
        data = load_json(path)
        if not validator(data):
            raise ValueError(f"invalid data: {path}")
        return data, False
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        data = load_json(template_path)
        write_json(path, data)
        return data, True


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    status, status_rebuilt = load_or_rebuild(
        STATUS_FILE,
        STATUS_TEMPLATE,
        valid_status,
    )
    _, roots_rebuilt = load_or_rebuild(
        ROOTS_FILE,
        ROOTS_TEMPLATE,
        valid_roots,
    )

    status["status"] = "base"
    write_json(STATUS_FILE, status)

    print(f"[OK] os_status.json: {'rebuilt' if status_rebuilt else 'validated'}")
    print("[OK] os_status reset to base")
    print(f"[OK] roots.json: {'rebuilt' if roots_rebuilt else 'validated'}")


if __name__ == "__main__":
    main()


