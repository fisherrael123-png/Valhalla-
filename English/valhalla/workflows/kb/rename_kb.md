# Rename a Knowledge Base

## Purpose

Rename a registered knowledge base under the current Valhalla root.

This Workflow is designed for ordinary research-group members. The user only needs to understand that this service “changes the knowledge-base name.” Internally, the system synchronizes the knowledge-base list, the knowledge-base directory name, and the knowledge base's own titles.

## Input

- Old knowledge-base name.
- New knowledge-base name.

## inspect: Pre-Rename Inspection

1. Confirm that the current Valhalla root is known.
2. Confirm that current system state is `base`.
3. Confirm that current knowledge-base state is `idle`. If the state is `kb:<name>`, stop and ask the user to exit the knowledge base first.
4. Read `wiki_registry.yaml` under the current root; this YAML file is the machine-authoritative table.
5. Exactly match the old knowledge-base name by `kb_name`; do not fuzzy-match.
6. If the old knowledge base does not exist, stop and report.
7. If the old name matches multiple entries, stop and list the candidates.
8. Confirm that the new knowledge-base name is not present in `wiki_registry.yaml`.
9. Confirm that the old directory exists: `Wiki/Wiki_<old-knowledge-base-name>/`.
10. Confirm that the target directory does not exist: `Wiki/Wiki_<new-knowledge-base-name>/`.
11. Confirm that both old and new directories are under the current root's `Wiki/` directory and that neither path contains `..`.
12. Output `rename_kb_inspect_report`, listing:
    - Current root;
    - Old knowledge-base name;
    - New knowledge-base name;
    - Old directory's relative and absolute paths;
    - New directory's relative and absolute paths;
    - File scope that will be modified;
    - Scope that explicitly will not be modified.
13. Request user confirmation. Before explicit confirmation, do not rename or move a directory or write any file.

## Items That Must Be Listed for Confirmation

Will be modified:

- `wiki_registry.yaml`
- `wiki_registry.md`
- `Wiki/Wiki_<old-knowledge-base-name>/` will move to `Wiki/Wiki_<new-knowledge-base-name>/`
- Knowledge-base title, index title, and log title inside the new directory
- Knowledge-base name fields in machine registries inside the new directory
- Knowledge-base name descriptions in human-readable projections inside the new directory

Will not be modified:

- `resource_registry.md`
- `resource_registry.yaml`
- `Library/`
- `Library/public_resources/`
- Other knowledge-base directories
- Original source files
- Public resource copies
- Academic knowledge content in Entity content files

## fix: Rename After Confirmation

Execute this phase only after the user explicitly confirms the inspect report.

1. Reconfirm that the old directory exists and the new directory does not.
2. Move `Wiki/Wiki_<old-knowledge-base-name>/` to `Wiki/Wiki_<new-knowledge-base-name>/`.
3. Changes to `usage.referenced_by.entity_file` and `kb_name` caused by the rename must be synchronized to `resource_registry.yaml/md` within this operation.
4. Modify the old knowledge-base entry in `wiki_registry.yaml`:
   - Set `kb_name` to the new knowledge-base name;
   - Set `wiki_path` to `Wiki/Wiki_<new-knowledge-base-name>`;
   - Set `updated_at` to the current date;
   - If `description` previously equaled the old knowledge-base name, set it to the new name; otherwise preserve the original description.
5. Synchronize `wiki_registry.md` from `wiki_registry.yaml`:
   - Find the table row for the old knowledge base;
   - Change the first-column `kb_name` to the new name;
   - Change the second-column `wiki_path` to `Wiki/Wiki_<new-knowledge-base-name>`;
   - Preserve `created_at`;
   - Set `updated_at` to the current date;
   - If `description` previously equaled the old knowledge-base name, change it to the new name;
   - If `description` is other explanatory text, preserve it;
   - Do not modify any other knowledge-base row;
   - If `wiki_registry.yaml` and `wiki_registry.md` conflict, rebuild this row from `wiki_registry.yaml`.
6. Update these entry files in the new directory:
   - `Wiki.md`: Replace the knowledge-base name in the title and purpose description;
   - `index.md`: Change the first-line title to the new name;
   - `log.md`: Change the first-line title to the new name and append a `rename | <old-name> -> <new-name>` log entry.
7. Update knowledge-base name fields in these machine YAML files in the new directory:
   - `.virtualDatabase/machine/local_resources.yaml`
   - `.virtualDatabase/machine/required_resources.yaml`
   - `.virtualDatabase/machine/excluded_resources.yaml`
   - `.registry/machine/entity_registry.yaml`
   - `.registry/machine/entity_resource_map.yaml`
   - `.registry/machine/relationship_registry.yaml`
   - `.registry/machine/knowledge_graph_registry.yaml`
   - `.registry/machine/conversation_entity_registry.yaml`
   - `.registry/machine/engineering_entity_registry.yaml`
8. If Relationship-fact or Knowledge Graph-fact files exist, update only their `kb` field representing the owning knowledge base; do not alter fact content.
9. In the corresponding human-readable Markdown projections, replace `Knowledge base: <old-name>` with `Knowledge base: <new-name>`.
10. Do not change historical notes, historical logs, or old names in resource-admission descriptions; these are audit records and may be preserved.
11. Derive and update `usage.referenced_by`, `reference_count`, and `usage.computed_at` in `resource_registry.yaml/md` from `.registry/machine/entity_resource_map.yaml` and `.registry/machine/entity_registry.yaml` of the renamed active KB.
12. `usage.referenced_by` may contain only canonical entries with `kb_name`, `entity_id`, and `entity_file`. `entity_file` must be `Wiki/Wiki_<knowledge-base-name>/<content_file>`. Calculate `reference_count` over unique `(kb_name, entity_id)` pairs. Do not write legacy usage, including string paths, `entities/`-relative paths, or the old `kb` field format.
13. Synchronize `resource_registry.md` within the same operation, refreshing reference-count projections solely from `resource_registry.yaml`.
15. Output `rename_kb_report`.

## Output

- `rename_kb_inspect_report`: Pre-rename inspection report;
- `rename_kb_report`: Rename-completion report;
- `renamed_kb`: Old and new names;
- `moved_paths`: Old and new directories;
- `next_operation`: `null` after rename and usage synchronization complete;
- `modified_files`: Files actually modified;
- `current_state`: Current root, `os_status`, and `kb_status`.

## Prohibited Actions

- Do not delete any source file.
- Do not modify resource identity, representations, lifecycle, or policy fields in `resource_registry.yaml` or `resource_registry.md`; only derived usage fields may be synchronized.
- Do not modify `Library/` or `Library/public_resources/`.
- Do not modify other knowledge bases.
- Do not execute while a knowledge base is active.
- Do not select a knowledge base through fuzzy matching.
- Do not interpret confirmation of the rename as authorization to delete, clean, ingest into, or rebuild the knowledge base.
