import json
from pathlib import Path

STATE_DIR = Path.home() / ".codex" / "valhalla"
STATUS_FILE = STATE_DIR / "os_status.json"
ROOTS_FILE = STATE_DIR / "roots.json"


def load_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def main():
    status_data = load_json(STATUS_FILE)
    roots_data = load_json(ROOTS_FILE)

    print(f"当前状态：{status_data['status']}")
    print(f"当前根目录：{roots_data['current_root']}")


if __name__ == "__main__":
    main()


