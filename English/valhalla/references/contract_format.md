# Unified Contract Format

## Execution Order

```text
Router
  → Load Contract
  → Dispatch selects exactly one operation
  → Validate operation eligibility
  → Load the executor after validation passes
  → Execute and verify output
```

If no operation matches, or multiple operations match, stop without loading an executor.

## Cross-Service Handoffs

When a Workflow needs another operation, it may only request a service handoff:

1. Pause the current operation; do not directly load the target Workflow.
2. Return the target operation to the Router.
3. Load and fully validate the target Contract.
4. Confirmation granted to the current operation must not be inherited by the target operation.
5. Services may exchange only formal outputs declared by the target Contract.
6. Before resuming the original operation, reload and validate its Contract.
7. Do not resume the original operation if the target operation fails, is denied, or returns incomplete output.

## Top-Level Structure

```yaml
contract:
  name: example_contract
  version: "0.5.11"
  status: active
  purpose: "Describe the responsibility of this Contract."

operations:
  example:
    intent: "Describe the execution intent of this operation."
    input:
      required: []
      optional: []
      pattern:
        canonical: "Canonical input form."
        examples:
          - "Example input"
        unsupported:
          - "Unsupported input"
    permissions:
      read: true
      write: false
    risk:
      level: low
      confirmation_required: false
    state_constraints: {}
    preconditions: []
    access:
      read_scope:
        allowed:
          - Wiki/Wiki_<knowledge-base-name>/
        denied: []
      write_scope:
        allowed:
          - user_explicit_target_paths
        denied:
          - Library/
        no_target_path_policy: "If the user has not specified a target path, confirm the exact write scope first."
      restrictions:
        - "Read only the effective resource collection."
    executor:
      type: workflow
      paths:
        - workflows/example.md
      load_after_validation: true
    output:
      required: []
    constraints:
      must_not:
        - "Skip validation."
```

The Contract top level may contain only `contract`, `dispatch`, and `operations`. The `contract` metadata may contain only `name`, `version`, `status`, and `purpose`. `version` must be `"0.5.11"`. `status` is optional; when present, it must be either `active` or `deprecated`.

An Operation may contain only `intent`, `input`, `permissions`, `risk`, `state_constraints`, `preconditions`, `access`, `executor`, `output`, `constraints`, and `phases`. Unknown fields must be treated as format errors.

`input` must contain the two lists `required` and `optional`. The optional `pattern` object may contain only `canonical`, `compatible`, `path_form`, `examples`, and `unsupported`.

`access` may be an empty object or contain `read_scope`, `write_scope`, and `restrictions`. `read_scope` and `write_scope` must contain an `allowed` list. The optional `denied` / `forbidden` fields must be lists. The optional policy fields `no_target_path_policy` and `knowledge_base_write_policy` must be strings.

`constraints` is a formal field. It may be an object or a list and stores execution constraints that cannot be reduced to `risk`, `access`, or `preconditions`.

## Dispatch

Only a Contract containing multiple operations may define `dispatch`:

```yaml
dispatch:
  required: true
  fallback: clarify
  on_ambiguous: clarify
  operations:
    create_item:
      triggers:
        - create item
    remove_item:
      triggers:
        - delete item
```

`dispatch.operations` must correspond one-to-one with `operations`. Both no match and multiple matches require clarification.

## Executor

Workflow executor:

```yaml
executor:
  type: workflow
  paths:
    - workflows/example.md
  section: inspect
  load_after_validation: true
```

`section` is optional and is commonly used for phased operations within a single Workflow file. A Workflow executor may contain only `type`, `paths`, `section`, and `load_after_validation`.

Command executor:

```yaml
executor:
  type: command
  command:
    - python
    - scripts/example.py
```

A Command executor may contain only `type` and `command`; it must not contain `paths`, `section`, or `load_after_validation`.

## Phased Operations

A phased operation does not define an executor at the operation's top level. Instead, each phase defines its own executor:

```yaml
phases:
  inspect:
    order: 1
    permissions:
      read: true
      write: false
    confirmation_required: false
    executor:
      type: workflow
      paths:
        - workflows/lint/lint.md
      section: inspect
      load_after_validation: true
    output:
      required:
        - lint_report

  fix:
    order: 2
    permissions:
      read: true
      write: true
    confirmation_required: true
    depends_on:
      phase: inspect
      required_outputs:
        - lint_report
    input:
      required:
        - user_confirmed
      optional: []
    constraints:
      - selected_issues_must_exist_in_lint_report
    executor:
      type: workflow
      paths:
        - workflows/lint/lint.md
      section: fix
      load_after_validation: true
    output:
      required:
        - lint_fix_report
```

Each phase must independently pass its qualification and confirmation checks.

A Phase may contain only `order`, `permissions`, `confirmation_required`, `depends_on`, `input`, `constraints`, `executor`, and `output`. `depends_on` may contain only `phase` and `required_outputs`.

The machine-authoritative format constraints are defined by `scripts/validate_contract_format.py`. Before changing Contract fields, update this document and the validator first, then update the individual Contracts.
