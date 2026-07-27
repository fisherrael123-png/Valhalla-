# Register an Existing Knowledge Base

## Purpose

Register an existing `Wiki/Wiki_<knowledge-base-name>/` directory under the current Valhalla root in the root-level `wiki_registry.yaml`, synchronize `wiki_registry.md`, and validate resource identities from the knowledge base's existing Entity–Resource mappings. The Resource-layer reverse index must be synchronized within this operation.

This Workflow modifies:

- `wiki_registry.yaml`
- `wiki_registry.md`

This Workflow does not create or move directories, modify files inside the knowledge base, start the knowledge base, or repair damaged structure.

`entity_resource_map.yaml` is the sole authority for Entity–Resource evidence mappings. `usage.referenced_by` in `resource_registry.yaml` is a reverse index derived from it. This Workflow must synchronize usage within the same operation. Usage may contain only canonical `kb_name`, `entity_id`, and `entity_file` entries; do not write legacy usage.

## Input

- Knowledge-base name.

## inspect: Pre-Registration Inspection

1. Confirm that the current Valhalla root is known.
2. Confirm that system state is `base`.
3. Confirm that knowledge-base state is `idle`.
4. Read `wiki_registry.yaml` as the machine-authoritative table.
5. Match the input name exactly against `kb_name`; if already registered, stop.
6. Confirm that `Wiki/Wiki_<knowledge-base-name>/` exists.
7. Confirm that the directory is under the current root's `Wiki/` directory and that its path contains no `..`.
8. Confirm that the minimum structure exists:
   - `Wiki.md`
   - `index.md`
   - `log.md`
   - `.virtualDatabase/machine/local_resources.yaml`
   - `.virtualDatabase/machine/required_resources.yaml`
   - `.virtualDatabase/machine/excluded_resources.yaml`
   - `.registry/machine/entity_registry.yaml`
   - `.registry/machine/entity_resource_map.yaml`
9. Read the target knowledge base's `.registry/machine/entity_registry.yaml` and `.registry/machine/entity_resource_map.yaml`.
10. Extract unique `(resource_id, entity_id)` pairs from `entity_resource_map.yaml`.
11. Find `content_file` for each `entity_id` in `entity_registry.yaml`. Each `content_file` must be an `entities/` path relative to the knowledge-base directory; otherwise report the violation and stop.
12. Read the current root's `resource_registry.yaml`.
13. Verify that every mapped `resource_id` exists in `resource_registry.yaml`.
14. If any resource is missing, output `missing_resource_ids` and stop; do not invent resource entries automatically.
15. Generate `resource_usage_sync_plan`:
   - After registration succeeds, usage in `resource_registry.yaml/md` must be synchronized within the current `register_existing_kb` operation;
   - Rebuild usage consistently from `entity_resource_map.yaml` and `entity_registry.yaml` for every registered active KB;
   - Existing legacy usage is not a completed state and must be migrated or removed within this operation;
   - `affected_paths` must include `resource_registry.yaml` and `resource_registry.md`.
16. Do not inspect, repair, or rewrite internal knowledge-base titles or content.
17. Output `register_existing_kb_inspect_report`, explicitly listing that the following will be modified:
   - `wiki_registry.yaml`
   - `wiki_registry.md`
18. Explicitly state that the following will not be modified:
   - `Wiki/Wiki_<knowledge-base-name>/**`
   - `Library/`
   - `Library/public_resources/`
   - Other knowledge-base directories
19. Request user confirmation. Do not write any file before explicit confirmation.

## fix: Register After Confirmation

1. Reconfirm that the target directory exists.
2. Reconfirm that no same-named `kb_name` exists in `wiki_registry.yaml`.
3. Re-read `entity_registry.yaml`, `entity_resource_map.yaml`, and `resource_registry.yaml`.
4. Reconfirm that every mapped `resource_id` exists in `resource_registry.yaml`.
5. Append an entry to `wikis` in `wiki_registry.yaml`:
   - `kb_name: <knowledge-base-name>`
   - `wiki_path: Wiki/Wiki_<knowledge-base-name>`
   - `status: active`
   - `created_at: <current date>`
   - `updated_at: <current date>`
   - `description: <knowledge-base-name>`
6. Rebuild or synchronize the `wiki_registry.md` table from `wiki_registry.yaml`.
7. Derive and update `usage.referenced_by`, `reference_count`, and `usage.computed_at` in `resource_registry.yaml/md` from `.registry/machine/entity_resource_map.yaml` and `.registry/machine/entity_registry.yaml` for every active KB registered under the current root.
8. `usage.referenced_by` may contain only canonical `kb_name`, `entity_id`, and `entity_file` entries. `entity_file` must be `Wiki/Wiki_<knowledge-base-name>/<content_file>`. Do not write legacy usage, including string paths, `entities/`-relative paths, or the old `kb` field format.
9. Calculate `reference_count` over unique `(kb_name, entity_id)` pairs.
10. Synchronize `resource_registry.md` within the same operation, refreshing the reference-count projection solely from `resource_registry.yaml`.
11. Do not modify any file inside the target Wiki directory.
12. Output `register_existing_kb_report`, `resource_usage_sync_report`, and `next_operation: null`.

## Output

- `register_existing_kb_inspect_report`
- `resource_usage_sync_plan`
- `affected_resource_ids`
- `missing_resource_ids`
- `register_existing_kb_report`
- `registered_kb`
- `resource_usage_sync_report`
- `next_operation`
- `modified_files`
- `current_state`

## Prohibited Actions

- Do not create `Wiki/Wiki_<knowledge-base-name>/`.
- Do not modify `Wiki/Wiki_<knowledge-base-name>/**`.
- Do not start the knowledge base.
- Do not repair internal structure.
- Do not delete any file.
- Do not delete any `resource_id`.
- Do not modify `Library/` or `Library/public_resources/`.
- Do not fuzzy-match knowledge-base names.
- Do not automatically create a resource entry for a missing `resource_id`.
