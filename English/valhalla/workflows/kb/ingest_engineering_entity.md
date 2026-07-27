# workflows/kb/ingest_engineering_entity.md

## Purpose

Preserve engineering-implementation content as an Engineering Entity and register it in the current knowledge base's `engineering_entity_registry.yaml`.

## Output

- `ingest_engineering_entity_report`
- `target_kb`

## Process

1. Locate the current knowledge-base directory.

2. Confirm the foundational Engineering Entity structure.

   If the following do not exist:

   ```text
   engineering_entity_registry.yaml
   engineering_entities/
   ```

   initialize only an empty registry from `template\knowledge_base\engineering\engineering_entity_registry_template.yaml`, and create the `engineering_entities/` directory. The empty registry's `entities` value must be `[]`; do not write an example Entity during initialization.

   `template\knowledge_base\engineering\engineering_entity_registry_entry_template.yaml` is used only to create or update a specific Engineering Entity. It must not initialize the complete registry.

3. Extract engineering experience.

   Focus on lessons from the most recent project work.

4. Determine whether an Entity already exists.

   Search for an existing Entity in `engineering_entity_registry.yaml` using:

   - `canonical_label`
   - `aliases`
   - `category`
   - `scope`
   - `resource_refs.files.path`

   If the same engineering object already exists, do not create a duplicate Entity.

5. Create or update the Engineering Entity.

   For a new Entity:

   - Assign a new ID in `eng_ent_000001` format.
   - Read `engineering_entity_registry_entry_template.yaml`.
   - Replace the ID, date, name, category, content path, and all other actual fields.
   - Append the fully substituted entry to `entities` in `engineering_entity_registry.yaml`.
   - Update the registry's `id_policy.next_id` and `updated_at`.
   - Create the content file:

     ```text
     engineering_entities/eng_ent_000001_<engineering-entity-name>.md
     ```

   For an existing Entity:

   - Preserve the original `id`.
   - Update `updated_at`.
   - Extend `resource_refs`.
   - Revise the corresponding content file.

   Before writing to the formal registry, do not preserve `<...>`, `YYYY-MM-DD`, or any other template placeholder literally. If any placeholder remains unsubstituted, stop the write and report the missing information.

6. Write the content file.

   Use `template\knowledge_base\engineering\engineering_entity_content_template.md`.

7. Update the registry.

   Update:

   - `updated_at`
   - The corresponding Entity's `updated_at`
   - `summary`
   - `scope`
   - `resource_refs`
   - `related_entities`
   - `dependencies`
   - `tags`

   Do not modify:

   - `.registry/machine/entity_registry.yaml`
   - `conversation_entity_registry.yaml`
   - `.registry/machine/relationship_registry.yaml`
   - `.registry/machine/knowledge_graph_registry.yaml`
   - Any of the three resource tables

8. Append to the log.

   Append the following to `log.md`:

   ```markdown
   ## [YYYY-MM-DD] ingest_engineering_entity | <knowledge-base-name>

   - Created or updated Engineering Entity: <eng_ent_id> <canonical_label>
   - Content file: <content_file>
   ```

9. Output the report.

   Output:

   ```yaml
   operation: ingest_engineering_entity
   target_kb: <knowledge-base-name>
   created_entities:
     - <eng_ent_id>
   updated_entities:
     - <eng_ent_id>
   content_files:
     - engineering_entities/<filename>.md
   registry: engineering_entity_registry.yaml
   status: success
   ```
