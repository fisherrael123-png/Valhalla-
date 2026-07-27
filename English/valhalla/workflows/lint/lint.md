# lint Workflow

## Phase 1: Inspect

### 1. Resolve the Target

Locate the inspection target from `scope`:

* `current_kb`: Read current state and locate the active knowledge base.
* `named_kb`: Locate `Wiki/Wiki_<kb_name>/`.
* `all_kbs`: Enumerate `Wiki/Wiki_*/`.
* `root`: Inspect the current Valhalla root.
* `file`: Inspect `target_path` and its direct references.

If the target is ambiguous, probe read-only and do not write.

### 2. Inspect

Inspect the root.
Inspect knowledge bases using the template rules under `schema`.

### 3. Deep Inspection

If `depth = deep`, also inspect:

* Duplicate Entity candidates.
* Orphan resources: resources registered in `resource_registry.yaml` with `usage.reference_count = 0`; record the corresponding `resource_id` in `orphan_resources.md` under this root.
* Whether resource tables contain only valid `resource_id` values and no source-copy or public-copy paths.
* Whether every source copy is under a non-public `Library/` directory in the current root.
* Whether every public copy is under `Library/public_resources/<resource_id>/`.
* Whether every resource has exactly one canonical name and whether aliases are duplicated.
* Whether every resource has at least one `authoritative` representation.
* Whether blacklist entries bind to valid `resource_id` values and Resource-layer blacklist projections are consistent.
* Whether `resource_registry.yaml` and `resource_registry.md` both exist.
* Whether resources, representations, current paths, synchronization states, reference counts, and blacklist states in `resource_registry.md` agree with YAML.
* Whether all three machine-authoritative YAML resource tables have same-named human-readable Markdown projections.
* Whether `resource_id`, membership state, and admission input agree between YAML and Markdown.
* Whether one YAML resource table registers the same `resource_id` more than once.
* Whether canonical names, current source paths, types, and versions in Markdown agree with `resource_registry.yaml`.
* Whether `pending_removal` entries have left the effective resource collection and await batch physical cleanup.
* Entities with provenance but no content.
* Entities with content but no provenance.
* Inconsistencies between content references and the Resource map.
* Relationship nodes absent from the registry.
* Graph nodes or edges absent from the registry.
* Existing file entry points omitted from the index.
* Resource-state conflicts across knowledge bases.

Report semantic-judgment issues found during deep inspection; do not repair them automatically.

### 3.1 Missing Entity Content Inspection

When `depth = deep` and the target is the current or a named knowledge base, inspect the ordinary Entity registry:

1. Read the target knowledge base's `.registry/machine/entity_registry.yaml`.
2. Read `content_file` for each Entity.
3. `content_file` must be an `entities/` path relative to the knowledge-base directory. It must not be absolute or contain `..`.
4. If `content_file` is valid but the target content file does not exist, output a `missing_entity_content_file` issue.
5. Every issue must contain:
   - `issue_id`: `missing_entity_content_file:<entity_id>`;
   - `issue_type`: `missing_entity_content_file`;
   - `entity_id`, `canonical_name`, and `content_file`;
   - Absolute expected path of the missing content;
   - `fixable: true`;
   - `requires_confirmation: false`;
   - `affected_paths`:
     - `.registry/machine/entity_registry.yaml`
     - `.registry/human/entity_registry.md`
     - `.registry/machine/entity_resource_map.yaml`
     - `.registry/human/entity_resource_map.md`

This inspection does not read or rewrite missing content and does not guess the missing Entity context.

### 4. Output lint_report

Every issue must have a unique `issue_id` and specify:

- `fixable`: Whether automatic repair is permitted;
- `requires_confirmation`: Whether separate confirmation is required;
- `affected_paths`: Exact paths that may be modified.

Also output `fixable_issue_ids` for selection in a confirmed fix phase. The fix phase must not process an issue absent from the current `lint_report`.

---

## Phase 2: Fix After Confirmation

### 1. Entry Condition

Enter the fix phase only after the user has seen and explicitly confirmed `lint_report`.

If the user selects a partial fix, repair only the specified issues.

### 2. Pre-Fix Filtering

Repair only issues that satisfy every condition below:

* Listed in the current `lint_report`.
* Confirmed by the user.
* Do not involve deleting, moving, merging, splitting, or rewriting content.
* Do not change the effective resource scope.
* Do not change Entity, Relationship, or Graph semantics.
* Do not modify resource identity in `resource_registry`.

### 3. Generate the Fix Plan

High-risk fixes include:

* Deleting files.
* Moving files.
* Merging entities.
* Splitting entities.
* Rewriting content.
* Summarizing source content.
* Changing resource-table inclusion scope.
* Changing the semantic content of the exclusion table.
* Changing resource identity in `resource_registry`.
* Judging source authenticity.
* Deciding whether a source belongs on the blacklist.
* Changing semantic relationships in the Knowledge Graph.
* Reversing a Relationship's direction.
* Changing an `entity_id`, `relationship_id`, or `graph_id`.
* Inferring missing provenance.
* Deciding whether two entities are synonymous.

These issues may enter the fix plan only after human confirmation.

### 4. Execute Fixes

For each fix:

1. Read the target file's current content.
2. Record its pre-change state.
3. Perform one fix.
4. Write the file.
5. Validate immediately.
6. If it fails, attempt a rollback.
7. Record the result.

One failed fix must not expand the modification scope.

### 4.1 Batch Resource-Table Cleanup

Run these batch operations only after the user confirms a fix from `lint_report`:

1. Collect every `pending_removal` entry from the three YAML resource tables.
2. Confirm that those entries no longer participate in any effective resource-collection calculation.
3. Physically remove those tombstone entries from the machine-authoritative YAML tables.
4. Delete the corresponding `pending cleanup` rows from the same-named Markdown files.
5. Compare Markdown in a batch against the remaining active YAML entries:
   - Add missing rows;
   - Remove orphan rows with no YAML member;
   - Preserve the `admission input` from YAML;
   - Refresh canonical name, current source paths, type, and version from `resource_registry.yaml`;
   - Synchronize membership state, admission time, removal-mark time, and note.
6. Update active and pending-cleanup counts and the last-updated time in Markdown.
7. Update `updated_at` in YAML.
8. If one YAML file contains duplicate `resource_id` values, report the conflict only. Do not merge automatically unless the entries' audit information is proven identical and the user confirms.

This batch cleanup removes only resource-table membership tombstones and projection rows. It does not delete any source file, public copy, `resource_id`, or Resource Registry entry.

### 4.2 Batch Synchronization of resource_registry.md

Run only after the user confirms a fix from `lint_report`:

1. Use `resource_registry.yaml` as the sole source of truth.
2. Add missing resource-summary and representation rows to Markdown.
3. Delete orphan Markdown rows that do not exist in YAML.
4. Refresh canonical names, aliases, types, versions, lifecycle, reference counts, and blacklist states.
5. Refresh source copies, public copies, representation types, formats, and synchronization states.
6. Update the resource count and last-updated time.
7. If Markdown is missing or severely damaged, rebuild it completely from YAML.

Do not overwrite YAML from Markdown.
Do not rebuild or rewrite `usage.referenced_by`, `usage.reference_count`, or `usage.computed_at` in `resource_registry.yaml` during this step. Only a fix that changes an Entity–Resource mapping may synchronize and rebuild usage.

### 4.3 Clean Registrations with Missing Entity Content

Run this cleanup only after the user confirms fixing `missing_entity_content_file` from `lint_report`.

For each confirmed `missing_entity_content_file:<entity_id>`:

1. Re-read the target knowledge base's `.registry/machine/entity_registry.yaml`.
2. Confirm that the issue was listed in the current `lint_report`, with `fixable: true` and `requires_confirmation: false`.
3. Delete the Entity entry for that `entity_id` from `.registry/machine/entity_registry.yaml`.
4. Delete every mapping to that `entity_id` from `.registry/machine/entity_resource_map.yaml`.
5. Rebuild from updated YAML:
   - `.registry/human/entity_registry.md`
   - `.registry/human/entity_resource_map.md`
6. Within the current `lint` operation, re-read `.registry/machine/entity_registry.yaml` and `.registry/machine/entity_resource_map.yaml` for every active knowledge base registered under the current root. Treat `entity_resource_map.yaml` as the authority for Entity–Resource evidence mappings and rebuild usage in `resource_registry.yaml/md`.
7. `usage.referenced_by` may contain only canonical entries with `kb_name`, `entity_id`, and `entity_file`. `entity_file` must be `Wiki/Wiki_<knowledge-base-name>/<content_file>`. Calculate `reference_count` over unique `(kb_name, entity_id)` pairs. Do not write legacy usage, including string paths, `entities/`-relative paths, or the old `kb` field form.
8. Synchronize `resource_registry.md` within the same operation, refreshing reference-count projections solely from `resource_registry.yaml`.
9. Output removed `entity_id` values, removed `map_id` values, preserved paths for the missing original content, the modified-file list, and `next_operation: null`.

This cleanup must not:

* Delete, move, or rename any file under `entities/`.
* Modify non-usage fields in `resource_registry.yaml` or `resource_registry.md`.
* Modify resource tables, Relationships, Knowledge Graphs, Conversation Entities, or Engineering Entities.
* Regenerate, supplement, or summarize missing Entity context.

### 5. Post-Fix Reinspection

Perform a minimum reinspection of modified files:

* Does the file exist?
* Can YAML be parsed?
* Can Markdown links be resolved?
* Can the registry still find its corresponding files?
* Do all three YAML and all three Markdown resource tables exist in pairs?
* If the fix changed an Entity–Resource mapping, was usage in `resource_registry.yaml/md` synchronized?
* Does the set of active YAML members agree with active Markdown rows?
* Were all `pending_removal` entries within the confirmed scope removed?
* Was each confirmed `missing_entity_content_file` removed from the Entity registry and Entity Resource map?
* Does `entity_resource_map` still contain a mapping to a deleted `entity_id`?
* Are the retained `entity_resource_map` and `entity_registry` sufficient to rebuild resource usage?
* Has the original issue disappeared?
* Did the fix introduce a new direct error?

### 5. Output lint_fix_report
