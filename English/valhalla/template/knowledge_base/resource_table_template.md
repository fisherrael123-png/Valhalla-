# <local_resources | required_resources | excluded_resources>

> This file is the human-readable projection of the authoritative YAML table with the same name.
> Resource membership and status are governed by `<resource-table-name>.yaml`.
> This file is maintained incrementally. After user confirmation, lint may batch-remove entries pending deletion and refresh projected fields.

## Basic Information

| Field | Value |
| --- | --- |
| Authoritative machine table | `<resource-table-name>.yaml` |
| Last updated | `YYYY-MM-DD` |
| Active count | `0` |
| Pending cleanup count | `0` |

## Resources

| resource_id | Canonical name | Input at time of addition | Current source path | Type/version | Membership status | Added at | Removal marked at | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Field Sources

- `resource_id`, membership status, original input, addition time, removal-mark time, and notes come from the YAML file with the same name.
- The input submitted by the user at the time of addition is retained permanently and does not change when a file is renamed or moved.
- The current source path, canonical name, type, and version are dynamically projected from the root-level `resource_registry.yaml`.
- `active` means the resource currently participates in resource-scope calculations.
- `pending_removal` appears as “Pending cleanup” in the human-readable table. It immediately leaves the effective resource set but remains until lint performs batch cleanup.
- Markdown does not overwrite membership data in YAML.
