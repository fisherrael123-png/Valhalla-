import importlib.util
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_contract_format.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_contract_format", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def base_operation():
    return {
        "input": {"required": [], "optional": []},
        "permissions": {"read": True, "write": False},
        "risk": {"level": "low", "confirmation_required": False},
        "state_constraints": {},
        "preconditions": [],
        "access": {},
        "executor": {
            "type": "workflow",
            "paths": ["workflows/example.md"],
            "load_after_validation": True,
        },
        "output": {"required": []},
    }


def base_contract(operation):
    return {
        "contract": {
            "name": "example_contract",
            "version": "0.5.11",
            "purpose": "fixture",
        },
        "operations": {"example": operation},
    }


def assert_invalid(validator, root, data, expected_fragment):
    path = root / "contract" / "example.yaml"
    write_yaml(path, data)
    try:
        validator.validate_contract(path)
    except AssertionError as error:
        assert expected_fragment in str(error), str(error)
        return
    raise AssertionError(f"expected invalid contract: {expected_fragment}")


def assert_valid(validator, root, data):
    path = root / "contract" / "example.yaml"
    write_yaml(path, data)
    validator.validate_contract(path)


def run_with_temp_root(callback):
    validator = load_validator()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "workflows").mkdir()
        (root / "workflows" / "example.md").write_text("# workflow\n", encoding="utf-8")
        validator.ROOT = root
        validator.CONTRACT_ROOT = root / "contract"
        callback(validator, root)


def test_unknown_operation_keys_are_rejected():
    def case(validator, root):
        operation = base_operation()
        operation["legacy_or_typo"] = True
        assert_invalid(validator, root, base_contract(operation), "contains unknown keys")

    run_with_temp_root(case)


def test_unknown_phase_keys_are_rejected():
    def case(validator, root):
        operation = base_operation()
        operation.pop("executor")
        operation["phases"] = {
            "inspect": {
                "order": 1,
                "permissions": {"read": True, "write": False},
                "confirmation_required": False,
                "executor": {
                    "type": "workflow",
                    "paths": ["workflows/example.md"],
                    "section": "inspect",
                    "load_after_validation": True,
                },
                "output": {"required": []},
            },
            "fix": {
                "order": 2,
                "permissions": {"read": True, "write": True},
                "confirmation_required": True,
                "depends_on": {"phase": "inspect", "required_outputs": []},
                "input": {"required": ["user_confirmed"], "optional": []},
                "unexpected": True,
                "executor": {
                    "type": "workflow",
                    "paths": ["workflows/example.md"],
                    "section": "fix",
                    "load_after_validation": True,
                },
                "output": {"required": []},
            },
        }
        assert_invalid(validator, root, base_contract(operation), "contains unknown keys")

    run_with_temp_root(case)


def test_access_scopes_must_use_allowed_and_denied_lists():
    def case(validator, root):
        operation = base_operation()
        operation["access"] = {"read_scope": {"allowed": "not-a-list"}}
        assert_invalid(validator, root, base_contract(operation), "read_scope.allowed")

    run_with_temp_root(case)


def test_command_executor_rejects_workflow_only_keys():
    def case(validator, root):
        operation = base_operation()
        operation["executor"] = {
            "type": "command",
            "command": ["python", "scripts/example.py"],
            "load_after_validation": True,
        }
        assert_invalid(validator, root, base_contract(operation), "contains unknown keys")

    run_with_temp_root(case)


def test_documented_extensions_are_allowed():
    def case(validator, root):
        operation = base_operation()
        operation["intent"] = "exercise the current contract format"
        operation["input"]["pattern"] = {"canonical": "example", "examples": ["example"]}
        operation["access"] = {
            "read_scope": {"allowed": ["Wiki/"], "denied": []},
            "write_scope": {
                "allowed": ["user_explicit_target_paths"],
                "denied": ["Library/"],
                "no_target_path_policy": "ask before writing",
            },
            "restrictions": ["read-only until confirmed"],
        }
        operation["constraints"] = {"must_not": ["skip validation"]}
        assert_valid(validator, root, base_contract(operation))

    run_with_temp_root(case)


def main():
    test_unknown_operation_keys_are_rejected()
    test_unknown_phase_keys_are_rejected()
    test_access_scopes_must_use_allowed_and_denied_lists()
    test_command_executor_rejects_workflow_only_keys()
    test_documented_extensions_are_allowed()
    print("PASS: contract format validator tests")


if __name__ == "__main__":
    main()
