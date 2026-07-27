# blacklist_operation Workflow

## Purpose

Maintain the Valhalla root-level global resource blacklist.

The blacklisted object is always the entire resource (`resource_id`). Every PDF, Markdown, TXT, OCR output, extracted-text file, source copy, and public copy under that resource is restricted together.

The user need not know the `resource_id`; they may enter a source filename or `Library/`-relative path. The system resolves that input and confirms the stable resource identity before writing.

## Input

### list_blacklist

No required input.

### add_blacklist

Required:

- `resource_query`: Source filename or `Library/`-relative path;
- `reason`: Reason for adding the resource to the blacklist.

Optional:

- `evidence`: Evidence link, explanation, or review record;
- `note`: Additional notes.

### remove_blacklist

Required:

- `blacklist_id`.

Optional:

- `reason`;
- `evidence`;
- `note`.

## Preflight Checks

1. Read the current Valhalla root.
2. Read `resource_registry.yaml` and `blacklist_registry.yaml`.
3. If `blacklist_registry.yaml` does not exist, initialize it from the corresponding template.
4. Check the operation and `admin` state constraints specified by the Contract.

## Resolve a Filename to resource_id

1. First treat the input as a `Library/`-relative path and exactly match `source_copies.path`.
2. If no exact match exists, treat the input as a filename and match:
   - `source_copies.local_name`;
   - The final filename component of `source_copies.path`;
   - When necessary, resource aliases whose `type` is `filename`.
3. If multiple files match but all belong to one `resource_id`, resolve to that resource.
4. If candidates belong to different `resource_id` values:
   - Display each candidate's `resource_id`, canonical name, version, file path, and format;
   - Ask the user to choose;
   - Do not select automatically.
5. If the file exists but is not registered:
   - Run `register_resource` first;
   - Registration must still preserve unique information and version boundaries;
   - Continue blacklisting only after registration completes.
6. If no candidate exists, stop. Do not create a blacklist entry without a linked resource identity.

A filename or path is only human input and an audit record, not the blacklist's stable identity.

## list_blacklist Process

1. Read `blacklist_registry.yaml`.
2. Select entries with `status: listed`.
3. Output:
   - `blacklist_id`
   - `resource_id`
   - Resource canonical name
   - Original user input
   - Reason
   - Date listed

## add_blacklist Process

1. Resolve `resource_query` to exactly one `resource_id` using the rules above.
2. Check whether the `resource_id` already has a blacklist entry.
3. If it is already `listed`:
   - Do not add a duplicate;
   - Append evidence or a note when appropriate;
   - Update `updated_at`.
4. If it has an existing `removed` entry:
   - Restore it to `listed`;
   - Record the new reason, evidence, and date.
5. If no entry exists:
   - Create a `blacklist_id`;
   - Record the `resource_id`;
   - Save the user's input and resolved source path in `matched_input`;
   - Save a snapshot of the resource's canonical name and version identity.
6. Set the corresponding resource's `policy.blacklist_status` in `resource_registry.yaml` to `listed` and write the `blacklist_id`.
7. In `.virtualDatabase/machine/local_resources.yaml` and `.virtualDatabase/machine/required_resources.yaml` for every knowledge base:
   - Mark matching active entries `pending_removal`;
   - Write `removed_at`;
   - Incrementally mark the corresponding row `pending cleanup` in the same-named Markdown file;
   - Do not rebuild the entire Markdown file or physically delete the YAML entry.
8. Remove the `resource_id` from every effective resource collection immediately and report the affected knowledge bases.
9. Do not modify `usage.referenced_by`, `reference_count`, or `entity_resource_map.yaml`; blacklist state does not delete historical provenance. `entity_resource_map.yaml` is the sole authority for Entity–Resource evidence mappings, and usage in `resource_registry.yaml` is only a derived reverse index that `sync_resource_usage` can rebuild.
10. Synchronize the resource's blacklist-status projection in `resource_registry.md`.
11. Prevent the resource from participating in ingestion, citation, Entity updates, Relationship construction, graph construction, and report generation.
12. Write the registries and output the report.

Blacklisting alone must not move or delete source copies or public copies. Physical movement or deletion is a separate high-risk operation that requires fresh user confirmation.

## remove_blacklist Process

1. Find the entry by `blacklist_id`.
2. If it does not exist, stop and report that fact.
3. If it exists, mark it `removed` and record the reason, basis, and date of removal.
4. Update the resource registry's blacklist projection to `not_listed`.
5. Synchronize the resource's blacklist-status projection in `resource_registry.md`.
6. Removing a resource from the blacklist does not automatically restore knowledge-base references. Reuse requires fresh review and an explicit resource-table edit.

## Output Formats

### blacklist_list_report

```markdown
| blacklist_id | resource_id | canonical name | user input | reason | listed_at |
| --- | --- | --- | --- | --- | --- |
```

### blacklist_add_report

Must include:

- Operation result;
- `blacklist_id`;
- `resource_id`;
- Resource canonical name;
- Original user input;
- Resolved source path;
- Affected knowledge bases;
- Statement that no physical movement or deletion was performed.

### blacklist_remove_report

Must include:

- `blacklist_id`;
- `resource_id`;
- Removal reason and date;
- Statement that knowledge-base references will not be restored automatically.
