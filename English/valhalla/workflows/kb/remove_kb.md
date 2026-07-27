# Unregister a Knowledge Base

## Purpose

Unregister a knowledge base from the current Valhalla root's knowledge-base registry. Resource-layer back-references must be cleaned within the same operation.

This Workflow modifies:

- `wiki_registry.yaml`
- `wiki_registry.md`

This Workflow does not delete `Wiki/Wiki_<knowledge-base-name>/`; delete any entities, registries, resource tables, Relationships, Knowledge Graphs, Conversation Entities, or Engineering Entities within the knowledge base; or modify `Library/` or `Library/public_resources/`.

`entity_resource_map.yaml` is the sole authority for Entity–Resource evidence mappings. `usage.referenced_by` in `resource_registry.yaml` is a derived reverse index. After unregistering the knowledge base, this Workflow must rebuild the Resource reverse index from active KBs.

## Input

- Knowledge-base name.

## inspect: Pre-Unregistration Inspection

1. Confirm that the current Valhalla root is known.
2. Confirm that system state is `base`.
3. Confirm that knowledge-base state is `idle`.
4. Read `wiki_registry.yaml` under the current root; this YAML file is the machine-authoritative knowledge-base registry.
5. Exactly match the target knowledge base by `kb_name`; do not select through fuzzy matching.
6. If there is no matching entry, stop and report that the target knowledge base is not registered.
7. If multiple entries match, stop and list the candidates; do not select automatically.
8. Read the target entry's `wiki_path` and confirm that it is relative, lies under the current root's `Wiki/` directory, and contains no `..`.
9. Read `resource_registry.yaml` and scan each resource's `usage.referenced_by` read-only to estimate stale usage that this operation will remove after unregistration.
10. Add these usage entries to `resource_usage_cleanup_plan`:
    - Structured entries whose `kb_name` equals the target knowledge base;
    - Compatible old-format structured entries whose `kb` equals the target knowledge base;
    - String paths beginning with `Wiki/Wiki_<knowledge-base-name>/entities/`;
    - Old `entities/`-relative paths only when the target KB's `entity_resource_map.yaml` proves their association; otherwise list them for human confirmation.
11. Estimate resources that may have `reference_count = 0` after cleanup and list them under `orphan_candidate_resource_ids`; report them only, without deleting any resource.
13. Output `remove_kb_inspect_report`, listing:
    - Target knowledge-base name;
    - Current root;
    - Complete entry to be removed from `wiki_registry.yaml`;
    - Absolute path of `Wiki/Wiki_<knowledge-base-name>/`, which will be preserved and not deleted;
    - `affected_resource_ids` whose usage this operation will clean;
    - Number of usage entries this operation will remove;
    - `orphan_candidate_resource_ids`;
    - `affected_paths`:
      - `wiki_registry.yaml`
      - `wiki_registry.md`
    - `next_operation: null`;
    - `confirmation_prompt`.
14. Do not write any file before explicit user confirmation.

## fix: Unregister and Synchronize Usage Cleanup After Confirmation

1. Re-read `wiki_registry.yaml` and again exactly match the target entry by `kb_name`.
2. Re-read `resource_registry.yaml` and regenerate the read-only `resource_usage_cleanup_plan`.
3. Remove the target knowledge-base entry from the `wikis` list in `wiki_registry.yaml`.
4. Rebuild or incrementally update `wiki_registry.md` from the updated `wiki_registry.yaml`. If they conflict, YAML takes precedence.
5. For every active KB in the updated registry, re-read `.registry/machine/entity_registry.yaml` and `.registry/machine/entity_resource_map.yaml`; rebuild `usage.referenced_by`, `reference_count`, and `usage.computed_at` in `resource_registry.yaml/md`, thereby deleting stale usage for the target KB.
6. `usage.referenced_by` may contain only canonical entries with `kb_name`, `entity_id`, and `entity_file`. `entity_file` must be `Wiki/Wiki_<knowledge-base-name>/<content_file>`. Do not write legacy usage, including string paths, `entities/`-relative paths, or the old `kb` field format.
7. Calculate `reference_count` over unique `(kb_name, entity_id)` pairs.
8. Synchronize `resource_registry.md` within the same operation, refreshing reference-count projections solely from `resource_registry.yaml`.
9. Do not delete any `resource_id`. List resources with `reference_count = 0` only as orphan candidates in `resource_usage_cleanup_report`.
10. Do not delete, move, or rename `Wiki/Wiki_<knowledge-base-name>/`.
11. Output `remove_kb_report`, `resource_usage_cleanup_report`, and `next_operation: null`.

## Output

- `remove_kb_inspect_report`: Read-only pre-unregistration inspection summary.
- `resource_usage_cleanup_plan`: Usage references proposed for removal from the Resource layer.
- `affected_resource_ids`: Resources whose usage will change.
- `orphan_candidate_resource_ids`: Resources that may become orphaned after cleanup.
- `remove_kb_report`: Unregistration summary.
- `removed_kb`: Name of the unregistered knowledge base.
- `removed_registry_entry`: Complete entry removed from `wiki_registry.yaml`.
- `resource_usage_cleanup_report`: Number of usage entries actually removed, affected resources, and orphan candidates.
- `preserved_wiki_path`: Preserved relative and absolute Wiki paths.
- `manual_cleanup_path`: Absolute path the user would handle if manual deletion is desired.
- `modified_files`: Must include `wiki_registry.yaml`, `wiki_registry.md`, `resource_registry.yaml`, and `resource_registry.md`.
- `next_operation`: `null` after registry unregistration and usage synchronization complete.
- `current_state`: Current root, `os_status`, and `kb_status`.

## Prohibited Actions

- Do not delete, move, or rename `Wiki/Wiki_<knowledge-base-name>/`.
- Do not delete, move, or rename any file under the target knowledge base.
- Do not delete any `resource_id`.
- Do not modify `Library/` or `Library/public_resources/`.
- Do not modify resource tables, entities, Relationships, or Knowledge Graphs in other knowledge bases.
- Do not execute while session state is `kb:<name>`; first use `exit_kb` to return to `idle`.
- Do not interpret the user's confirmation of this operation as authorization to delete directories or resources, rewrite Entity content, or modify resource tables.
