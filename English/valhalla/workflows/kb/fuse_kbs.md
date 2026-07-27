# Fuse Knowledge Bases

## Purpose

Fuse multiple source knowledge bases explicitly specified by the user within the current Valhalla root into one new target knowledge base.

This Workflow is designed for research-group members. The user only needs to understand that it is the “fuse knowledge bases” management service. Internally, the system first performs a read-only review of source registries, virtual resource tables, and content to produce a fusion plan. It creates and writes the target knowledge base only after user confirmation.

Source KBs remain read-only throughout. Do not modify, move, delete, or clean any source knowledge-base file.

## Input

- List of source knowledge bases.
- Target knowledge-base name.

The only supported command form is:

```text
fuse knowledge bases <source-knowledge-base-list> into <new-knowledge-base>
```

Separate source knowledge-base names with commas. Names must exactly match `kb_name` entries in the current root's `wiki_registry.yaml`.

Fusing every knowledge base under the current root is not supported. Stop and explain when given input such as:

```text
fuse every knowledge base in the current root into <new-knowledge-base>
fuse all knowledge bases
```

## General Principles

1. This is not root fusion and does not read other roots.
2. This operation requires `admin` state.
3. This operation requires `idle` knowledge-base state.
4. Every source knowledge base must be registered in the current root's `wiki_registry.yaml`.
5. The target must be a new knowledge base; `Wiki/Wiki_<new-knowledge-base>/` must not already exist.
6. This operation fuses `entity`, `relationship`, `conversation_entity`, and `engineering_entity` objects.
7. This operation does not fuse `knowledge_graph`, `.registry/machine/knowledge_graph_registry.yaml`, or `knowledge_graph/**`.
8. This operation does not modify `Library/` or `Library/public_resources/`. Resource usage produced by the target KB must be synchronized to `resource_registry.yaml/md` within the current operation.
9. YAML is machine-authoritative. Markdown is only a human-readable projection; if they conflict, YAML takes precedence.

## inspect: Pre-Fusion Review

The inspect phase is read-only and must not write any file.

### 1. Parse Input

1. Parse the list of source knowledge bases.
2. Remove blank items.
3. Exactly match each name against `kb_name` in `wiki_registry.yaml`.
4. Stop if fewer than two source knowledge bases remain.
5. If any source does not exist or matches multiple entries, stop and list the candidates.
6. Stop if the target knowledge-base name is already registered.
7. Stop if `Wiki/Wiki_<target-knowledge-base-name>/` already exists.
8. If the user requests “all knowledge bases” or “every knowledge base in the current root,” stop; the user must list sources explicitly.

### 2. Read the Source Scope

For each source knowledge base, read these files read-only:

- `.virtualDatabase/machine/local_resources.yaml`
- `.virtualDatabase/machine/required_resources.yaml`
- `.virtualDatabase/machine/excluded_resources.yaml`
- `.virtualDatabase/human/local_resources.md`
- `.virtualDatabase/human/required_resources.md`
- `.virtualDatabase/human/excluded_resources.md`
- `.registry/machine/entity_registry.yaml`
- `.registry/machine/entity_resource_map.yaml`
- `.registry/machine/relationship_registry.yaml`
- `.registry/machine/conversation_entity_registry.yaml`
- `.registry/machine/engineering_entity_registry.yaml`
- `entities/*.md`
- `relationships/machine/*.yaml`
- `relationships/human/*.md`
- `conversation_entities/*.md`
- `engineering_entities/*.md`

Do not read or write `knowledge_graph/**` in a source knowledge base. The inspect phase may read `resource_registry.yaml` and `resource_registry.md` to resolve resource names and verify resource existence, but it must not modify them.

### 3. Review Entities

Read Entity entries from each source knowledge base's `.registry/machine/entity_registry.yaml`.

Identify duplicate candidates as follows:

1. Compare `ingestion.resource_refs` first.
2. Only entities with intersecting `resource_id` values become automatic duplicate candidates.
3. Read and compare the `content_file` content for each candidate.
4. By default, do not automatically merge entities with different `resource_id` values unless the user explicitly selects that decision during review.

Generate `entity_merge_decisions` for each duplicate-candidate group. Available decisions:

- `merge_content`: Default. Generate one new target `ent_id`; merge aliases, tags, and `resource_refs`; integrate content; remove obvious duplication; and preserve conflict notes and provenance.
- `pick_one`: Migrate only the source Entity selected by the user. Exclude the other candidates from the target knowledge base and record them in the report.
- `append_content`: Generate one new target `ent_id`; merge and deduplicate metadata; concatenate content in sections by source knowledge base and source Entity without semantic rewriting.

Do not assign multiple target entities to source entities already identified as one duplicate-candidate group. Migrate each non-duplicate Entity independently and assign it a new target `ent_id`.

The inspect phase must output a draft `entity_id_map`:

```text
<source-knowledge-base>:<old-ent_id> -> <target-knowledge-base>:<new-ent_id or skipped>
```

### 4. Review conversation_entity Objects

Read Conversation Entities from each source knowledge base's `.registry/machine/conversation_entity_registry.yaml`.

Duplicate-candidate key:

```text
canonical_label + scope + summary
```

Generate `conversation_merge_decisions` for each candidate group. Available decisions:

- `merge_content`: Default. Merge aliases, tags, `resource_conversations`, summary, scope, and content.
- `pick_one`: Migrate only the source `conversation_entity` selected by the user.
- `append_content`: Concatenate content in sections by source knowledge base and source Conversation Entity without semantic rewriting.

Remap `related_entities` in the target registry through `entity_id_map`. If a reference points to an object not migrated, omit the reference and record it in the report.

### 5. Review engineering_entity Objects

Read Engineering Entities from each source knowledge base's `.registry/machine/engineering_entity_registry.yaml`.

Duplicate-candidate key:

```text
canonical_label + scope + summary
```

Generate `engineering_merge_decisions` for each candidate group. Available decisions:

- `merge_content`: Default. Merge aliases, tags, `resource_refs`, dependencies, summary, scope, and content.
- `pick_one`: Migrate only the source `engineering_entity` selected by the user.
- `append_content`: Concatenate content in sections by source knowledge base and source Engineering Entity without semantic rewriting.

Remap or deduplicate `related_entities`, `dependencies`, and still-valid resource references in the target registry. If a reference points to an object not migrated, omit the reference and record it in the report.

### 6. Review Relationships

Relationships must be processed after Entity review because their subjects and objects depend on entities.

1. Use the draft `entity_id_map` to rewrite each Relationship's `subject_entity_id` and `object_entity_id`.
2. If either subject or object is absent from the target knowledge base, do not migrate the Relationship; record the reason for skipping it.
3. After rewriting, deduplicate by:

```text
subject_entity_id + object_entity_id + predicate.id + scope
```

4. Merge Relationships with the same key and deduplicate their evidence.
5. Preserve Relationships with identical subject, object, and predicate but different scopes as separate facts.
6. Output `relationship_fusion_plan`, listing new, merged, skipped, and unconfirmed Relationships.

### 7. Review the Virtual Resource Collection

The target knowledge base has one global set of virtual resource tables.

Read only YAML entries with `membership_status: active`.

Build three sets:

- Positive set: Every active entry in `local_resources` and `required_resources` across source knowledge bases.
- Evidence set: Resources referenced by migrated entities, Relationships, Conversation Entities, or Engineering Entities.
- Exclusion set: Every active entry in `excluded_resources` across source knowledge bases.

Draft target rules:

- `required_resources`: Deduplicate and merge all active required resources from source knowledge bases.
- `local_resources`: Deduplicate and merge the positive and evidence sets.
- `excluded_resources`: Include only resources that appear exclusively in the exclusion set and do not appear in the positive or evidence sets.

If a resource is excluded in one source knowledge base but used in another, or referenced by a migrated object, do not place it in the target `excluded_resources`.

Output `excluded_but_used_resources` with:

- `resource_id`
- Resource name
- Source knowledge bases that excluded it
- Source knowledge bases that used it
- Migrated objects that referenced it
- Target resource table in which it will finally appear

If one source knowledge base simultaneously marks a resource as active excluded and active local/required, report an internal contradiction in that source's resource tables. Do not repair the source knowledge base; the target still prioritizes the positive and evidence sets.

### 8. Output the Inspect Report

Output `fuse_kbs_inspect_report` containing at least:

- Current root.
- Source knowledge-base names and paths.
- Target knowledge-base name and path.
- Number of source objects.
- Entity duplicate candidates and default decisions.
- Conversation Entity duplicate candidates and default decisions.
- Engineering Entity duplicate candidates and default decisions.
- `relationship_fusion_plan`.
- Draft target virtual resource tables.
- `excluded_but_used_resources`.
- Exact paths to be written.
- Source knowledge-base paths that explicitly will not be modified.
- Confirmation prompt.

Do not enter fix until the user explicitly confirms this inspect report and the fusion plan.

## fix: Execute Fusion After Confirmation

Execute this phase only after the user explicitly confirms `fuse_kbs_inspect_report` and `fuse_kbs_plan`.

### 1. Pre-Write Revalidation

1. Re-read `wiki_registry.yaml` and confirm that every source knowledge base still exists.
2. Confirm that the target knowledge-base name remains unregistered.
3. Confirm that `Wiki/Wiki_<target-knowledge-base-name>/` still does not exist.
4. Confirm that the user has completed every `merge_content`, `pick_one`, and `append_content` decision.
5. Confirm that no Relationship depends on an incomplete Entity decision.

### 2. Create the Target Knowledge-Base Structure

Create the structure defined by `workflows/kb/create_kb.md`:

- `Wiki.md`
- `index.md`
- `log.md`
- `.virtualDatabase/machine/*.yaml`
- `.virtualDatabase/human/*.md`
- `.registry/machine/*.yaml`
- `.registry/human/*.md`
- `entities/`
- `relationships/machine/`
- `relationships/human/`
- `conversation_entities/`
- `engineering_entities/`

Do not create or migrate any `knowledge_graph/**` content. Retain only the empty Knowledge Graph registry and directories required by the default `create_kb` structure.

### 3. Write Target Entities

1. Assign target `ent_id` values according to the confirmed `entity_merge_decisions`.
2. Write the target `.registry/machine/entity_registry.yaml`.
3. Write the target `.registry/human/entity_registry.md`.
4. Write target `entities/*.md` content.
5. Write the final `entity_id_map.yaml`.

### 4. Write Target Conversation Entities

1. Assign target `conv_ent_id` values according to the confirmed `conversation_merge_decisions`.
2. Remap `related_entities`.
3. Write the target `.registry/machine/conversation_entity_registry.yaml`.
4. Write the target `.registry/human/conversation_entity_registry.md`.
5. Write target `conversation_entities/*.md`.
6. Write the final `conversation_id_map.yaml`.

### 5. Write Target Engineering Entities

1. Assign target `eng_ent_id` values according to the confirmed `engineering_merge_decisions`.
2. Remap `related_entities` and `dependencies`.
3. Write the target `.registry/machine/engineering_entity_registry.yaml`.
4. Write the target `.registry/human/engineering_entity_registry.md`.
5. Write target `engineering_entities/*.md`.
6. Write the final `engineering_id_map.yaml`.

### 6. Write Target Relationships

1. Rewrite Relationships using the final `entity_id_map`.
2. Skip a Relationship if its subject or object was not migrated.
3. Deduplicate by `subject_entity_id + object_entity_id + predicate.id + scope`.
4. Merge evidence.
5. Write `relationships/machine/<predicate_id>.yaml`.
6. Write `relationships/human/<predicate_id>.md`.
7. Synchronize `.registry/machine/relationship_registry.yaml` and `.registry/human/relationship_registry.md`.

### 7. Write Target Virtual Resource Tables

Write the positive, evidence, and exclusion sets confirmed during inspect to:

- `.virtualDatabase/machine/required_resources.yaml`
- `.virtualDatabase/human/required_resources.md`
- `.virtualDatabase/machine/local_resources.yaml`
- `.virtualDatabase/human/local_resources.md`
- `.virtualDatabase/machine/excluded_resources.yaml`
- `.virtualDatabase/human/excluded_resources.md`

Resources in `excluded_but_used_resources` must not enter the target `excluded_resources`.

### 8. Update the Root Knowledge-Base Registry

1. Add the target knowledge-base entry to `wiki_registry.yaml`.
2. Synchronize `wiki_registry.md`.
3. Do not start the target knowledge base unless the user separately requests it.

### 9. Write the Audit Directory

Write under the target knowledge base:

```text
Wiki/Wiki_<target-knowledge-base-name>/.valhalla/imports/kb_fusion_<timestamp>/
  source_kbs.yaml
  fuse_kbs_plan.yaml
  entity_id_map.yaml
  conversation_id_map.yaml
  engineering_id_map.yaml
  relationship_fusion_plan.yaml
  excluded_but_used_resources.yaml
  execution_report.yaml
```

Audit files must be sufficient to determine:

- The source objects from which every target Entity, Conversation Entity, and Engineering Entity originated.
- The source Relationships from which every target Relationship originated.
- Which source objects `pick_one` skipped.
- Which resources were excluded in a source but used in the target knowledge base.
- Which source knowledge bases remained read-only.

### 10. Validate

After writing, verify that:

1. The target knowledge base is registered in `wiki_registry.yaml` and `wiki_registry.md`.
2. Target registries contain only target IDs.
3. Every Relationship subject and object exists in the target Entity registry.
4. Relationship-registry counts match fact files.
5. `id_policy.next_id` is correct in the Conversation and Engineering registries.
6. Virtual resource tables reference only `resource_id` values present in the current root's `resource_registry.yaml`.
7. `excluded_but_used_resources.yaml` agrees with the target virtual resource tables.
8. Source knowledge-base files were not modified.
9. Within the current `fuse_kbs` operation, rebuild usage in `resource_registry.yaml/md` from `.registry/machine/entity_resource_map.yaml` and `.registry/machine/entity_registry.yaml` for every active KB registered under the current root.
10. `usage.referenced_by` may contain only canonical entries with `kb_name`, `entity_id`, and `entity_file`. `entity_file` must be `Wiki/Wiki_<knowledge-base-name>/<content_file>`. Calculate `reference_count` over unique `(kb_name, entity_id)` pairs. Do not write legacy usage, including string paths, `entities/`-relative paths, or the old `kb` field form.
11. Synchronize `resource_registry.md` within the same operation, refreshing reference-count projections solely from `resource_registry.yaml`.

Output `fuse_kbs_report`.

## Failure and Abortion

- If inspect fails, do not write any file.
- If the user has not confirmed the inspect report, do not enter fix.
- If deduplication decisions are incomplete, do not enter fix.
- If a Relationship depends on an incomplete Entity decision, do not enter fix.
- If writing fails during fix, do not roll back or modify a source knowledge base. Report the target path, written files, failed step, whether target registries were written, and validation state.

## Output

- `fuse_kbs_inspect_report`: Pre-fusion review report.
- `fuse_kbs_plan`: Pre-confirmation fusion plan.
- `entity_merge_decisions`: Entity deduplication decisions.
- `conversation_merge_decisions`: Conversation Entity deduplication decisions.
- `engineering_merge_decisions`: Engineering Entity deduplication decisions.
- `relationship_fusion_plan`: Relationship rewrite, merge, and skip plan.
- `excluded_but_used_resources`: Resources excluded in a source but still used by the target knowledge base.
- `fuse_kbs_report`: Fusion-completion report.
- `target_kb`: Target knowledge-base name and path.
- `next_operation`: `null` after target registration and usage synchronization complete.
- `modified_files`: Files actually written.
- `current_state`: Current root, `os_status`, and `kb_status`.

## Prohibited Actions

- Do not support “fuse every knowledge base in the current root.”
- Do not reuse root-fusion logic for knowledge-base fusion.
- Do not modify a source knowledge base.
- Do not delete a source knowledge base.
- Do not modify resource identity, representations, lifecycle, or policy fields in `resource_registry.yaml` or `resource_registry.md`; only derived usage fields may be synchronized.
- Do not modify `Library/` or `Library/public_resources/`.
- Do not migrate or fuse Knowledge Graph facts.
- Do not execute while a knowledge base is active.
- Do not interpret confirmation of inspect as authorization to delete, clean, start a knowledge base, or modify a source knowledge base.
