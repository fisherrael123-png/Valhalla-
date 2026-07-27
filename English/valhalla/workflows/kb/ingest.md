# ingest

## Objective

Extract knowledge from the unique source information represented by a specified `resource_id`, then create or update entities in the current knowledge base.

The Entity layer references only `resource_id`; it must not store source-copy or public-copy paths.

If the input contains more than one source—including a directory containing more than one source—treat it as batch processing. The batch loop must be defined here in `ingest.md` as follows.

When more than one source is provided, strictly follow this process:

1. Select exactly one `resource_id` as the current target.
2. For that `resource_id` alone: read the source, extract knowledge, determine whether the Entity already exists, create or update the Entity, maintain `entity_registry`, maintain `entity_resource_map`, synchronize usage in `resource_registry.yaml/md`, and run validation.
3. Do not begin the next `resource_id` until ingestion of the current one has completed and passed validation. If it fails or remains incomplete, resolve or report it first.
4. Do not place multiple `resource_id` values in one extraction prompt, intermediate summary, write script, batch YAML update, batch Entity-generation step, or pre-validation write transaction.
5. A summary report may be generated after every single-resource loop finishes, but it must not replace the independent result for each `resource_id`.
6. If one tool or script is reused to reduce duplicate code, each invocation may accept and write exactly one `resource_id`; it must not accept a list for batch ingestion.
7. Output a separate completion state, modified-file list, failure reason, and validation result for each `resource_id`.

Compliance criterion: The log or execution record must show an independent start, write, validation, and finish for each `resource_id`. If one action simultaneously writes entities, mappings, or registry updates for two or more `resource_id` values, it violates this Workflow.

## Safety Rules

1. Do not ingest a resource whose blacklist status is `listed`.
2. Do not register a source file itself as an Entity.
3. Do not create a duplicate of an existing knowledge item.
4. Do not directly overwrite an existing Entity file; ask before overwriting.
5. Do not modify Contracts, the Router, schemas, or Workflows.
6. Do not merge automatically when resource identity or version cannot be confirmed.
7. Molecular strings in source material may be recorded as facts from published literature, but must not be used to generate, optimize, complete, modify, screen, or recommend experimental execution.
8. For sources involving proteins, antibodies, or peptides, preferentially record accession numbers, PDB, UniProt, GenBank, construct names, variant names, metrics, page numbers, figure or table numbers, and provenance anchors. Do not copy long source passages into a prompt in bulk.
9. Do not record executable wet-lab procedures, experimental conditions, culture/expression/screening parameters, vector or primer construction steps, experiment-optimization paths, or operational details that directly enhance biological-design capability.

## Resource Resolution and Service Handoffs

1. Resolve target resources from `resource_query`:
   - If the input is a `resource_id`, verify that it exists in `resource_registry.yaml`;
   - If the input is a filename, `Library/`-relative path, or directory, find corresponding resources at the Resource layer;
   - Resolve each candidate independently to a definite `resource_id`;
   - If candidates belong to different resources and cannot be disambiguated, stop and ask the user to choose; do not select automatically.
2. If the target sources are registered, obtain one or more validated `resource_id` values and enter “Ingestion Execution.”
3. If a target source is not registered:
   - Pause the current `ingest` operation without writing to the knowledge base;
   - Return to the Router with `register_resource` as a new operation;
   - Load and fully validate `register_resource_contract.yaml`;
   - Independently satisfy its input, permissions, risk, state, preconditions, access scope, and confirmation requirements;
   - Do not directly load or execute `register_resource.md`;
   - Confirmation already granted to `ingest` does not count as confirmation for `register_resource`.
4. After `register_resource` succeeds:
   - Accept only the `resource_id` from its formal Contract output;
   - Return to the Router and reload and validate `ingest_contract.yaml`;
   - Re-check the current root, target knowledge base, state, permissions, and write scope;
   - After validation passes, continue ingestion from the returned `resource_id`;
   - Do not continue using the original filename or path as resource identity.
5. If `register_resource` does not complete:
   - If the user declines confirmation, the file is absent, resource identity conflicts, or registration fails, stop ingestion for that resource;
   - Do not create an Entity or modify resource tables, Entity registries, mapping tables, logs, or resource reference counts;
   - In a batch request, process only resources explicitly selected by the user and successfully registered;
   - Report the stop reason, successfully registered resources, and remaining operations.

## Language Requirements

Entity content must be written in English. If the source material is in Chinese or another language, first understand it and then rewrite it as structured English knowledge. Do not use untranslated source sentences, abstracts, or paragraphs as the Entity's main content.

Original-language text may be retained only for:

1. Paper titles, model names, method names, dataset names, metric names, organization names, software names, API names, and code identifiers;
2. Proper terms that must be preserved exactly;
3. Short quotes used for evidence location in `entity_resource_map.yaml`;
4. A small number of evidence sentences explicitly marked as `original-language excerpt`.

The following must be recorded in English:

- Core definition
- Key points
- Mechanisms, principles, algorithms, and lessons learned
- Scope of applicability
- Experiments and experimental results
- Conclusions
- Limitations and controversies
- `description`, `ingestion_note`, and `metadata.note` in `entity_registry.yaml`

Prohibited:

- Do not split an untranslated abstract, introduction, or conclusion into bullets and write it into an Entity;
- Do not fill main sections such as “Key Points,” “Mechanism,” “Experimental Results,” or “Conclusions” with untranslated source-language sentences;
- Do not substitute machine-extracted source-language fragments for English knowledge synthesis;
- Do not write Entity content in the source language merely because the source itself is not English.

Compliance criterion:
Before ingestion of each `resource_id` completes, validate the corresponding Entity's language. If a main section contains an unmarked long non-English sentence or paragraph, do not report that resource as `completed`. Report it as `partial` or `stopped` and state that an English rewrite is required.

Executable language-validation threshold:

- Except for proper names, metrics, datasets, model names, and marked quotes, no main section may contain an unmarked non-English passage longer than 12 words or 24 CJK characters;
- A bullet must not consist mainly of an untranslated source sentence;
- If non-English characters account for an excessive share of the main content, stop and rewrite it in English;
- If validation fails, do not update `last_ingested_at` to a completed state.

## Ingestion Execution

Before entering this phase, obtain a `resource_id` validated against `resource_registry.yaml`. Do not perform any knowledge-base write without a stable `resource_id`.

1. Compress execution context.
2. Check whether the resource is in the exclusion table or global blacklist. If so, stop and report it.
3. Define the effective virtual resource collection as:

   ```text
   (resource_id values with membership_status == active in .virtualDatabase/machine/local_resources.yaml
   ∪ resource_id values with membership_status == active in .virtualDatabase/machine/required_resources.yaml)
   - resource_id values with membership_status == active in .virtualDatabase/machine/excluded_resources.yaml
   - resource_id values in the global blacklist
   ```

4. If the target resource is not yet in the effective virtual resource collection, add its `resource_id` to `.virtualDatabase/machine/local_resources.yaml` and incrementally append a human-readable row to `.virtualDatabase/human/local_resources.md`.
5. Select a suitable representation through the Resource layer:
   - Prefer an available `authoritative` representation;
   - Use a `converted`, `ocr`, or `extracted_text` representation to assist parsing when appropriate;
   - Do not copy representation-file paths into the Entity registry.
6. Extract knowledge entities from the resource, using `references\entity_context.md` as the Entity-content reference.
   - A knowledge Entity has topic-level granularity and includes the ideas, models, algorithms, plans, experiments, results, and conclusions organized around that topic.
   - Ingest data from the relevant sections—especially experiments, results, and conclusions—to support the Entity. Present the data in tables for comparison.
   - Combine comparable data and concepts into tables.
   - If one source covers several topics, register each topic independently as an Entity at the granularity above.
   - Never register an idea, model, algorithm, plan, experiment, result, conclusion, or any subset of these from one topic as an independent Entity separate from the topic as a whole.
   - If different resources yield the same knowledge Entity, do not merge them; record them as separate entities.
6.1 Calculate `entity_id` only from local state in the current target knowledge base:
   - Read the target knowledge base's `.registry/machine/entity_registry.yaml`;
   - Scan `entities/ent_*.md` in the target knowledge base;
   - Use the next unused local number for the new `entity_id` and content filename;
   - Do not derive the next `entity_id` from `resource_registry.yaml`, usage within it, another knowledge base, historical runs, or old `usage.referenced_by` data;
   - `resource_registry.yaml` validates resource identity and stores the Resource-layer reverse index only; it does not participate in assigning local `entity_id` values.
7. Write ingested Entity content to its `content_file`. The `content_file` must be relative to the current knowledge-base directory and follow `entities/ent_000001_<name>.md`. It must not contain a `Wiki/Wiki_<knowledge-base-name>/` prefix, be absolute, or contain `..`.
8. Maintain both Entity registry files in sync:
   - `.registry/machine/entity_registry.yaml` is machine-authoritative. Record the `resource_id` under the Entity's `ingestion.resource_refs`;
   - `.registry/human/entity_registry.md` is the human-readable projection. Incrementally add or update an Entity row showing at least `entity_id`, name, type, status, content path, and source `resource_id`;
   - Generate the Markdown projection from final YAML state; never overwrite YAML from Markdown;
   - If an Entity changes, synchronize both files within the same operation and include both under `modified_files`;
   - If YAML updates but the Markdown projection fails, do not report this resource as `completed`; report `partial` or `stopped` and list the unfinished work.
9. Register `entity_id`, `resource_id`, evidence type, and internal resource location in `.registry/machine/entity_resource_map.yaml`. `entity_resource_map.yaml` is the sole authority for Entity–Resource evidence mappings; `ingestion.resource_refs` in `entity_registry.yaml` is only a summary.
10. If the Entity already exists, extend its content and provenance; do not create a duplicate.
11. This operation must synchronize usage in `resource_registry.yaml` and `resource_registry.md`. Usage in `resource_registry.yaml` is a derived reverse index and must not be used as the source of Entity–Resource facts.
12. If this operation writes or updates `.registry/machine/entity_resource_map.yaml` or `.registry/machine/entity_registry.yaml`, derive updates to the root resource registry from these two machine-authoritative files within the current `ingest` operation:
   - Read this knowledge base's Entity–Resource evidence mappings from `.registry/machine/entity_resource_map.yaml`;
   - Read each `entity_id`'s `content_file` from `.registry/machine/entity_registry.yaml`;
   - Refresh `usage.referenced_by`, `reference_count`, and `usage.computed_at` for affected resources in the current root's `resource_registry.yaml`;
   - `usage.referenced_by` may contain only canonical entries with `kb_name`, `entity_id`, and `entity_file`;
   - `entity_file` must be `Wiki/Wiki_<knowledge-base-name>/<content_file>`, where `content_file` comes from `entity_registry.yaml`;
   - Calculate `reference_count` over unique `(kb_name, entity_id)` pairs;
   - Do not write legacy usage, including string paths, `entities/`-relative paths, or the old `kb` field form;
   - Synchronize `resource_registry.md` within the same operation, refreshing reference-count projections solely from `resource_registry.yaml`.
13. `resource_registry.yaml` validates resource identity and records the Resource-layer reverse index only. It must not participate in assigning `entity_id` values within the current knowledge base.
14. After synchronization, `modified_files` must include `resource_registry.yaml` and `resource_registry.md`. Unless a preceding `register_resource` handoff is still incomplete, a successful ingestion must set `next_operation: null`.

### Large-Source Ingestion Strategy

1. Inventory the target `resource_id` and its representations before reading the full content.
2. For long works, prioritize the table of contents, abstract, heading hierarchy, conclusions, figure and table captions, references, and user-specified sections.
3. In each batch, extract key claims, entities, concepts, methods, data, limitations, contradictions, and open questions.
4. After each batch, update Entity pages, provenance mappings, indexes, and logs.
5. At the end of each batch, report processed resources, representations used, unread sections, conflicts, and items requiring confirmation.

### Temporary Draft and Cache Rules

Use section-level temporary drafts during ingestion:

1. Inventory the target `resource_id` and its representations before reading the full content.
2. Prioritize the table of contents, abstract, heading hierarchy, conclusions, figure and table captions, references, and user-specified sections. Establish a temporary draft for each section.
3. Extract specific content from each section—including key claims, entities, concepts, methods, data, limitations, contradictions, and open questions—into the corresponding temporary draft. For every section:
   - Extract concrete detail; do not remain generic.
   - Present comparable content in tables.
   - Present each section's data in tables.
4. Review each section draft against the requirements.
5. After all sections pass, consolidate them into the topic's formal Entity content file.

Do not use persistent drafts or historical caches during ingestion:

1. Do not search for, read, load, or reuse any `*_entity_context.md`.
2. Do not read ingestion content from `.tmp*`, `valhalla_entity_contexts/`, or other historical context directories.
3. Do not use an old context file as a template, draft, evidence source, or completion basis.
4. If ingestion fails, do not leave an Entity draft file; report the failure reason only in the operation output.

### Content Quality Gate

Before writing a final Entity, confirm that:

1. The current `references\entity_context.md` was used as the template.
2. The final content covers the template's required sections at the template's required quality.
3. The knowledge Entity is organized around one topic.
4. Core definition, method or mechanism, experiments or cases, results and conclusions, and limitations are grounded in the source.
5. Data from the corresponding source sections has been ingested and presented in comparative tables.
6. Tables required by the template have been generated.
7. The evidence-location table contains locations internal to the resource.
8. The content contains no low-quality markers such as `ent_pending`, `draft`, `draft_for_ingestion`, `to be completed`, `TODO`, `supplement after close reading`, or `first N pages of the PDF`.
9. There is no obvious mojibake, extraction-order corruption, or template residue.

## Output

- `completion_status`: `completed`, `partial`, `paused`, or `stopped`;
- `resource_ids`: Every stable resource identity resolved in this operation;
- `completed_resource_ids`: Resources whose ingestion completed;
- `skipped_resource_queries`: Original inputs not resolved, selected, or processed;
- `registration_results`: Formal results of resource-registration operations;
- `failed_resources`: Resources whose registration or ingestion failed, with reasons;
- `modified_files`: Files actually modified in this operation;
- `target_kb`: Target knowledge base;
- `current_state`: State at the end of the operation;
- `next_operation`: `register_resource` while registration is pending; `null` after successful ingestion and resource-usage synchronization.

## Stop and Ask

- Multiple candidate files resolve to different `resource_id` values;
- A source version or information-identity conflict is found;
- New evidence would overturn an existing core conclusion;
- The operation would rewrite many pages;
- Available context is insufficient to preserve provenance.
