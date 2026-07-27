import subprocess
import sys
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).parent

def load_file(path):
    file_path = BASE_DIR / path
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    content = file_path.read_text(encoding="utf-8")
    print(f"\n[LOAD] {path}")
    print(content)
    return content


def run_script(command):
    resolved_command = [
        sys.executable if argument == "python" else argument
        for argument in command
    ]
    print(f"\n[RUN] {' '.join(resolved_command)}")

    result = subprocess.run(
        resolved_command,
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Script execution failed: {command}")


def execute_operation(name, operation):
    op_type = operation["type"]

    if op_type == "load_file":
        return load_file(operation["path"])

    if op_type == "run_script":
        return run_script(operation["command"])

    raise ValueError(f"Unknown operation type: {op_type}")


def main():
    config_path = BASE_DIR / "bootstrap_config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    operations = config["operations"]

    print("[VALHALLA] Initialization started")

    for op_name in config["bootstrap"]:
        if op_name not in operations:
            raise KeyError(f"Undefined operation: {op_name}")

        print(f"\n=== Operation: {op_name} ===")
        execute_operation(op_name, operations[op_name])

    print("\n[VALHALLA] Initialization complete")


if __name__ == "__main__":
    main()


