# ingest_conversation

## Purpose

Preserve the current session as a Conversation Entity and register it in the current knowledge base's `conversation_entity_registry.yaml`.

This Workflow is responsible only for the ingestion procedure.
Permissions, state constraints, preconditions, and output requirements are governed by `ingest_conversation_contract.yaml`.

## Input

- Current Valhalla root
- Current target knowledge base
- Current session content
- `Wiki/Wiki_<knowledge-base-name>/.registry/machine/conversation_entity_registry.yaml`
- `Wiki/Wiki_<knowledge-base-name>/conversation_entities/`

## Output

- `ingest_conversation_report`
- `target_kb`

## Process

1. Locate the current knowledge-base directory.

   Enter:

   ```text
   Wiki/Wiki_<knowledge-base-name>/
   ```

2. Confirm or create the registry.

   If the following file does not exist:

   ```text
   conversation_entity_registry.yaml
   ```

   create the initial file from:

   ```text
   template\knowledge_base\conversation\conversation_entity_registry_template.yaml
   template\knowledge_base\conversation\conversation_entity_registry_entry_template.yaml
   ```

3. Extract topics from the current session.

   Extract:

   - Principal subjects discussed
   - Knowledge items worth preserving
   - Design decisions finally confirmed by the user
   - Concepts, structures, names, or rules that should be retained long term

4. Match existing Conversation Entities.

   Search these fields in `conversation_entity_registry.yaml`:

   - `canonical_label`
   - `aliases`
   - `scope`
   - `summary`

   If the current session topic matches an existing Entity, reuse its original `id`.
   Do not create duplicate entities for the same conversation topic.

5. Create or update a Conversation Entity.

   For a new Entity:

   - Assign a new ID in `conv_ent_000001` format.
   - Add an entry to `conversation_entity_registry.yaml`.
   - Create the corresponding content file:

     ```text
     conversation_entities/conv_ent_000001_<conversation-entity-name>.md
     ```

   For an existing Entity:

   - Preserve the original `id`.
   - Update `updated_at`.
   - Extend `resource_conversations`.
   - Extend or revise the corresponding content file.

6. Write the Conversation Entity content file.

   The content file must contain at least:

   ```markdown
   # <Conversation Entity Name>

   ## Summary

   ## Content Added in This Session

   ## Confirmed Design

   ## Open Questions

   ## Source Conversations
   ```

7. Update the registry.

   Update:

   - `updated_at`
   - The corresponding Entity's `updated_at`
   - `resource_conversations`
   - `summary`
   - `scope`
   - `related_entities`
   - `tags`

   Do not modify:

   - `.registry/machine/entity_registry.yaml`
   - `engineering_entity_registry.yaml`
   - `.registry/machine/relationship_registry.yaml`
   - `.registry/machine/knowledge_graph_registry.yaml`
   - Any of the three resource tables

8. Append to the log.

   Append the following to `log.md`:

   ```markdown
   ## [YYYY-MM-DD] ingest_conversation | <knowledge-base-name>

   - Created or updated Conversation Entity: <conv_ent_id> <canonical_label>
   - Content file: <content_file>
   ```

9. Output the report.

   Output `ingest_conversation_report` containing:

   ```yaml
   operation: ingest_conversation
   target_kb: <knowledge-base-name>
   created_entities:
     - <conv_ent_id>
   updated_entities:
     - <conv_ent_id>
   content_files:
     - conversation_entities/<filename>.md
   registry: conversation_entity_registry.yaml
   status: success
   ```
