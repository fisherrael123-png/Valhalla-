# edit_resource_table Workflow

## Purpose

Edit the current knowledge base's `local_resources`, `required_resources`, or `excluded_resources`.

Each resource table consists of two parallel files:

- `<resource-table-name>.yaml`: Machine-authoritative membership table;
- `<resource-table-name>.md`: Human-readable projection.

The knowledge-base layer uses `resource_id` as the stable identity. Markdown displays both the user's admission input and the current Resource-layer source path.

## Input

```yaml
target_table: <local_resources | required_resources | excluded_resources>
action: <add | delete | remove>
resource_query: <resource_id | filename | Library-relative path | Library directory>
note: <optional note>
```

Natural-language aliases:

- “this-KB resource table” -> `local_resources`
- “required-resource table” -> `required_resources`
- “excluded-resource table” -> `excluded_resources`

## Resolve the Resource

1. If the input is a valid `resource_id`, look it up directly in `resource_registry.yaml`.
2. If the input is a filename, `Library/`-relative path, or directory, resolve it only at the Resource layer:
   - Match `representations[*].source_copies`;
   - Match public copies;
   - Match canonical and alternate names.
3. If candidates belong to different resources, list them and ask the user to choose; do not select automatically.
4. If an unregistered file must be added, run `register_resource` first.
5. Store the user's original `resource_query` in `added_via.value` and the resolution method in `added_via.input_type`.

## Blacklist Validation

Check whether the resource is blacklisted. If it is, stop this process immediately and ask whether the user wants to continue with other files.

## Add

1. If the YAML does not contain the `resource_id`:
   - Append an entry to the end of `resources`;
   - Set `membership_status: active`;
   - Write `added_via`, `added_at`, `removed_at: null`, and the note.
2. If the entry is already `active`:
   - Do not add a duplicate;
   - Update the note only if requested by the user.
3. If the entry is `pending_removal`:
   - Restore `membership_status: active`;
   - Clear `removed_at`;
   - Update `added_via` and `added_at` from the current input.
4. Obtain the canonical name, current source paths, type, and version from `resource_registry.yaml`.
5. Append the corresponding row to the end of the Markdown table. When restoring an entry, update only the existing row.
6. Update only the Markdown count and timestamp; do not rebuild the entire file.
7. Do not modify `resource_registry.yaml` or `resource_registry.md`. Resource-table membership affects only the effective resource scope and is not a source for `usage.referenced_by`; resource usage is derived only from `entity_resource_map.yaml` and `entity_registry.yaml`.

## Delete or Remove

1. Locate the `resource_id` in YAML.
2. Do not physically delete the entry immediately:
   - Set `membership_status: pending_removal`;
   - Write `removed_at`.
3. The resource leaves the effective resource-scope calculation as soon as the state change completes.
4. Update only the corresponding Markdown row:
   - Display the membership state as `pending cleanup`;
   - Record the removal-mark timestamp.
5. Do not rebuild the complete Markdown file or delete the corresponding row immediately.
6. If the entry is already `pending_removal`, do not repeat the operation.
7. Do not modify `resource_registry.yaml` or `resource_registry.md`. Resource-table entries pending cleanup no longer participate in the effective resource calculation, but provenance mappings are not removed automatically. If another operation modifies an Entity–Resource mapping, that operation must synchronize usage.

## Current Source-Path Projection

- Current source paths come from every `representations[*].source_copies[*].path` in `resource_registry.yaml`.
- Separate multiple paths with `<br>` inside the Markdown cell.
- Moving or renaming a file, or changing a source copy, does not alter membership in the YAML resource table.
- Lint refreshes drifted path projections in a batch.

## Effective Members

Only the following entries participate in knowledge-base resource-scope calculation:

```text
membership_status == active
```

## Prohibited Actions

- Do not make Markdown authoritative for membership;
- Do not allow `pending_removal` entries to remain in the effective resource scope;
- Do not physically delete YAML entries during an ordinary removal;
- Do not change a `resource_id` because a path changed;
- Do not rebuild the entire Markdown file when adding one resource;
- Do not modify resource identities or file mappings;
- Do not move or delete source files or public copies.
