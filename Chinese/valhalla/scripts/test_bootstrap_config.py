from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "bootstrap_config.yaml"


def main():
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8-sig"))
    bootstrap_steps = config["bootstrap"]
    operations = config["operations"]

    assert "print_status" in bootstrap_steps
    print_status = operations["print_status"]
    assert print_status == {
        "type": "run_script",
        "command": ["python", "scripts/status.py"],
    }

    print("PASS: bootstrap prints os and kb status")


if __name__ == "__main__":
    main()
