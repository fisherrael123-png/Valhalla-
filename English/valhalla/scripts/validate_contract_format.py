from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contract"

REQUIRED_OPERATION_KEYS = {
    "input",
    "permissions",
    "risk",
    "state_constraints",
    "preconditions",
    "access",
    "output",
}

ALLOWED_TOP_LEVEL_KEYS = {"contract", "dispatch", "operations"}
ALLOWED_CONTRACT_KEYS = {"name", "purpose", "status", "version"}
ALLOWED_OPERATION_KEYS = REQUIRED_OPERATION_KEYS | {"constraints", "executor", "intent", "phases"}
ALLOWED_INPUT_KEYS = {"optional", "pattern", "required"}
ALLOWED_INPUT_PATTERN_KEYS = {
    "canonical",
    "compatible",
    "examples",
    "path_form",
    "unsupported",
}
ALLOWED_PERMISSIONS_KEYS = {"read", "write"}
ALLOWED_RISK_KEYS = {"confirmation_required", "level"}
ALLOWED_STATE_RULE_KEYS = {"allowed", "on_denied"}
ALLOWED_PRECONDITION_KEYS = {"id", "on_failed", "parameters", "type"}
ALLOWED_ACCESS_KEYS = {"read_scope", "restrictions", "write_scope"}
ALLOWED_SCOPE_KEYS = {
    "allowed",
    "denied",
    "forbidden",
    "knowledge_base_write_policy",
    "no_target_path_policy",
}
ALLOWED_OUTPUT_KEYS = {"required"}
ALLOWED_WORKFLOW_EXECUTOR_KEYS = {"load_after_validation", "paths", "section", "type"}
ALLOWED_COMMAND_EXECUTOR_KEYS = {"command", "type"}
ALLOWED_PHASE_KEYS = {
    "confirmation_required",
    "constraints",
    "depends_on",
    "executor",
    "input",
    "order",
    "output",
    "permissions",
}
ALLOWED_DEPENDS_ON_KEYS = {"phase", "required_outputs"}

LEGACY_KEYS = {
    "input_pattern",
    "input_required",
    "input_optional",
    "read_allowed",
    "write_allowed",
    "risk_level",
    "read_scope",
    "write_scope",
    "write_targets",
    "load",
    "command",
    "output_required",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_yaml(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    require(isinstance(data, dict), f"{path}: YAML root must be an object")
    return data


def require_no_unknown_keys(path, label, data, allowed_keys):
    unknown = set(data) - allowed_keys
    require(not unknown, f"{path}: {label} contains unknown keys: {sorted(unknown)}")


def validate_input(path, label, input_spec, allow_pattern=True):
    require(isinstance(input_spec, dict), f"{path}: {label} input must be an object")
    require_no_unknown_keys(path, f"{label} input", input_spec, ALLOWED_INPUT_KEYS)
    require(
        isinstance(input_spec.get("required"), list)
        and isinstance(input_spec.get("optional"), list),
        f"{path}: {label} input requires required/optional lists",
    )
    if "pattern" in input_spec:
        require(allow_pattern, f"{path}: {label} input.pattern is not allowed here")
        pattern = input_spec["pattern"]
        require(isinstance(pattern, dict), f"{path}: {label} input.pattern must be an object")
        require_no_unknown_keys(path, f"{label} input.pattern", pattern, ALLOWED_INPUT_PATTERN_KEYS)
        for key in {"canonical", "compatible", "path_form"} & set(pattern):
            require(
                isinstance(pattern[key], str),
                f"{path}: {label} input.pattern.{key} must be a string",
            )
        for key in {"examples", "unsupported"} & set(pattern):
            require(
                isinstance(pattern[key], list),
                f"{path}: {label} input.pattern.{key} must be a list",
            )


def validate_permissions(path, label, permissions):
    require(isinstance(permissions, dict), f"{path}: {label} permissions must be an object")
    require_no_unknown_keys(path, f"{label} permissions", permissions, ALLOWED_PERMISSIONS_KEYS)
    require(
        permissions.get("read") in {True, False}
        and permissions.get("write") in {True, False, "conditional"},
        f"{path}: {label} has invalid permissions",
    )


def validate_output(path, label, output):
    require(isinstance(output, dict), f"{path}: {label} output must be an object")
    require_no_unknown_keys(path, f"{label} output", output, ALLOWED_OUTPUT_KEYS)
    require(
        isinstance(output.get("required"), list),
        f"{path}: {label} requires output.required",
    )


def validate_constraints(path, label, constraints):
    require(
        isinstance(constraints, (dict, list)),
        f"{path}: {label} constraints must be an object or list",
    )


def validate_access_scope(path, label, scope_name, scope):
    require(isinstance(scope, dict), f"{path}: {label} access.{scope_name} must be an object")
    require_no_unknown_keys(path, f"{label} access.{scope_name}", scope, ALLOWED_SCOPE_KEYS)
    require(
        isinstance(scope.get("allowed"), list),
        f"{path}: {label} access.{scope_name}.allowed must be a list",
    )
    for key in {"denied", "forbidden"} & set(scope):
        require(
            isinstance(scope[key], list),
            f"{path}: {label} access.{scope_name}.{key} must be a list",
        )
    for key in {"knowledge_base_write_policy", "no_target_path_policy"} & set(scope):
        require(
            isinstance(scope[key], str),
            f"{path}: {label} access.{scope_name}.{key} must be a string",
        )


def validate_access(path, label, access):
    require(isinstance(access, dict), f"{path}: {label} access must be an object")
    require_no_unknown_keys(path, f"{label} access", access, ALLOWED_ACCESS_KEYS)
    for scope_name in {"read_scope", "write_scope"} & set(access):
        validate_access_scope(path, label, scope_name, access[scope_name])
    if "restrictions" in access:
        require(
            isinstance(access["restrictions"], list),
            f"{path}: {label} access.restrictions must be a list",
        )


def validate_executor(path, executor):
    require(isinstance(executor, dict), f"{path}: executor must be an object")
    executor_type = executor.get("type")
    require(
        executor_type in {"workflow", "command"},
        f"{path}: executor.type must be workflow or command",
    )

    if executor_type == "workflow":
        require_no_unknown_keys(path, "workflow executor", executor, ALLOWED_WORKFLOW_EXECUTOR_KEYS)
        require(
            executor.get("load_after_validation") is True,
            f"{path}: workflow must load only after validation",
        )
        paths = executor.get("paths")
        require(
            isinstance(paths, list) and paths,
            f"{path}: workflow executor requires non-empty paths",
        )
        for relative_path in paths:
            require(
                (ROOT / relative_path).exists(),
                f"{path}: workflow does not exist: {relative_path}",
            )
        if "section" in executor:
            require(isinstance(executor["section"], str), f"{path}: executor.section must be a string")
    else:
        require_no_unknown_keys(path, "command executor", executor, ALLOWED_COMMAND_EXECUTOR_KEYS)
        command = executor.get("command")
        require(
            isinstance(command, list) and command,
            f"{path}: command executor requires a command list",
        )


def validate_phase(path, phase_name, phase):
    require(isinstance(phase, dict), f"{path}: phase {phase_name} must be an object")
    require_no_unknown_keys(path, f"phase {phase_name}", phase, ALLOWED_PHASE_KEYS)
    require(
        isinstance(phase.get("order"), int),
        f"{path}: phase {phase_name} requires integer order",
    )
    validate_permissions(path, f"phase {phase_name}", phase.get("permissions"))
    require(
        isinstance(phase.get("confirmation_required"), bool),
        f"{path}: phase {phase_name} requires confirmation_required",
    )
    if "depends_on" in phase:
        depends_on = phase["depends_on"]
        require(isinstance(depends_on, dict), f"{path}: phase {phase_name} depends_on must be an object")
        require_no_unknown_keys(path, f"phase {phase_name} depends_on", depends_on, ALLOWED_DEPENDS_ON_KEYS)
        require(
            isinstance(depends_on.get("phase"), str)
            and isinstance(depends_on.get("required_outputs"), list),
            f"{path}: phase {phase_name} depends_on requires phase and required_outputs",
        )
    if "input" in phase:
        validate_input(path, f"phase {phase_name}", phase["input"], allow_pattern=False)
    if "constraints" in phase:
        validate_constraints(path, f"phase {phase_name}", phase["constraints"])
    validate_executor(path, phase.get("executor"))
    validate_output(path, f"phase {phase_name}", phase.get("output"))


def validate_operation(path, name, operation):
    require(isinstance(operation, dict), f"{path}: operation {name} must be an object")
    legacy = LEGACY_KEYS & set(operation)
    require(not legacy, f"{path}: operation {name} contains legacy keys: {sorted(legacy)}")
    require_no_unknown_keys(path, f"operation {name}", operation, ALLOWED_OPERATION_KEYS)

    missing = REQUIRED_OPERATION_KEYS - set(operation)
    require(not missing, f"{path}: operation {name} missing keys: {sorted(missing)}")

    validate_input(path, f"operation {name}", operation["input"])
    validate_permissions(path, f"operation {name}", operation["permissions"])

    risk = operation["risk"]
    require(isinstance(risk, dict), f"{path}: operation {name} risk must be an object")
    require_no_unknown_keys(path, f"operation {name} risk", risk, ALLOWED_RISK_KEYS)
    require(
        risk.get("level") in {"low", "medium", "high"},
        f"{path}: operation {name} has invalid risk level",
    )
    require(
        isinstance(risk.get("confirmation_required"), bool),
        f"{path}: operation {name} requires explicit confirmation policy",
    )

    require(
        isinstance(operation["state_constraints"], dict),
        f"{path}: operation {name} state_constraints must be an object",
    )
    for state_name, rule in operation["state_constraints"].items():
        require(isinstance(rule, dict), f"{path}: {name}.{state_name} must be an object")
        require_no_unknown_keys(path, f"{name}.{state_name}", rule, ALLOWED_STATE_RULE_KEYS)
        require("denied" not in rule, f"{path}: {name}.{state_name} must not define denied")
        require(
            isinstance(rule.get("allowed"), list) and "on_denied" in rule,
            f"{path}: {name}.{state_name} requires allowed and on_denied",
        )
        require(
            name in rule["on_denied"],
            f"{path}: {name}.{state_name} on_denied must name its operation",
        )

    for precondition in operation["preconditions"]:
        require(isinstance(precondition, dict), f"{path}: operation {name} has invalid precondition")
        require_no_unknown_keys(path, f"operation {name} precondition", precondition, ALLOWED_PRECONDITION_KEYS)
        require(
            {"id", "type", "parameters", "on_failed"} <= set(precondition),
            f"{path}: operation {name} has invalid precondition",
        )

    validate_access(path, f"operation {name}", operation["access"])
    validate_output(path, f"operation {name}", operation["output"])
    if "intent" in operation:
        require(isinstance(operation["intent"], str), f"{path}: operation {name} intent must be a string")
    if "constraints" in operation:
        validate_constraints(path, f"operation {name}", operation["constraints"])

    if "phases" in operation:
        require("executor" not in operation, f"{path}: phased operation must not define executor")
        phases = operation["phases"]
        require(
            set(phases) == {"inspect", "fix"},
            f"{path}: phased operation must define inspect and fix",
        )
        for phase_name, phase in phases.items():
            validate_phase(path, phase_name, phase)
        require(
            phases["inspect"]["confirmation_required"] is False
            and phases["fix"]["confirmation_required"] is True,
            f"{path}: lint confirmation policy is invalid",
        )
    else:
        validate_executor(path, operation.get("executor"))


def validate_contract(path):
    data = load_yaml(path)
    require_no_unknown_keys(path, "Contract root", data, ALLOWED_TOP_LEVEL_KEYS)
    metadata = data.get("contract")
    require(isinstance(metadata, dict), f"{path}: missing contract metadata")
    require_no_unknown_keys(path, "contract metadata", metadata, ALLOWED_CONTRACT_KEYS)
    require(metadata.get("version") == "0.5.11", f"{path}: version must be 0.5.11")
    if "status" in metadata:
        require(
            metadata["status"] in {"active", "deprecated"},
            f"{path}: contract.status must be active or deprecated",
        )

    operations = data.get("operations")
    require(isinstance(operations, dict) and operations, f"{path}: operations are required")

    dispatch = data.get("dispatch")
    if len(operations) == 1:
        require(dispatch is None, f"{path}: single-operation Contract must not define dispatch")
    else:
        require(isinstance(dispatch, dict), f"{path}: multi-operation Contract requires dispatch")
        require(dispatch.get("required") is True, f"{path}: dispatch.required must be true")
        require(
            dispatch.get("fallback") == "clarify"
            and dispatch.get("on_ambiguous") == "clarify",
            f"{path}: dispatch must clarify unmatched or ambiguous requests",
        )
        require(
            set(dispatch.get("operations", {})) == set(operations),
            f"{path}: dispatch operations must match operations",
        )

    for name, operation in operations.items():
        validate_operation(path, name, operation)


def main():
    paths = sorted(CONTRACT_ROOT.rglob("*.yaml"))
    require(paths, "No Contract files found")
    for path in paths:
        validate_contract(path)
    print(f"PASS: {len(paths)} Contract files use the 0.5.11 format")


if __name__ == "__main__":
    main()

