# relate_entities Workflow

## Purpose

Summarize and organize relationships among existing entities in the current knowledge base, then write confirmed relationship facts to relationship-fact files grouped by `predicate.id`.

A relationship fact is an edge fact between entities. `.registry/machine/relationship_registry.yaml` indexes relationship-fact files; it does not store complete relationship facts.

Machine YAML is authoritative data, and human Markdown is a human-readable review projection. Markdown must not overwrite YAML.

## Input

- The user's relationship-organization request.
- The current knowledge base's `.registry/machine/entity_registry.yaml`.
- The current knowledge base's `.registry/machine/entity_resource_map.yaml`.
- The current knowledge base's `.registry/machine/relationship_registry.yaml`.
- The current knowledge base's `.registry/human/relationship_registry.md`.
- Content files referenced by relevant entities.
- Source material from the effective virtual resource collection when necessary.

## Workflow

### 1. Determine Scope

Determine the Entity scope from the user's request. If the user does not specify a scope, organize significant, well-evidenced relationships among existing entities in the current knowledge base.

Do not invent entities that do not exist.

### 2. Read Entities and Evidence

Read `.registry/machine/entity_registry.yaml` and confirm the following for relevant entities:

- `entity_id`
- Names and aliases
- Type and status
- Content-file path
- `ingestion.resource_refs`

Read the relevant Entity content files and `.registry/machine/entity_resource_map.yaml` to establish a traceable evidence chain. Read corresponding public representations when necessary, but do not write file paths into relationship facts as stable identities.

### 3. Form Candidate Relationships

Each candidate relationship must contain at least:

- `subject_entity_id`: Subject Entity;
- `object_entity_id`: Object Entity;
- `predicate`: Predicate ID, English name, Chinese name, direction, hierarchy, and mechanism;
- `description`: Relationship description;
- `confidence` and optional `weight`;
- `evidence.resource_refs`;
- `evidence.entity_resource_map_refs`;
- `evidence.evidence_note`;
- `scope`: Applicable scope, conditions, and limitations.

Do not create relationships from name similarity alone, and do not use source files, sections, or resources as relationship nodes.

### 4. Locate the Relationship-Fact File by Predicate

Use `predicate.id` as the grouping key to locate or create:

- `relationships/machine/<predicate_id>.yaml`
- `relationships/human/<predicate_id>.md`

Use:

- Fact-file template: `template/knowledge_base/relationship/relationship_fact_file_template.yaml`
- Human fact-projection template: `template/knowledge_base/relationship/relationship_fact_file_template.md`
- Fact Schema: `schema/relationship_fact_file_schema.json`

Every relationship in one fact file must have a `predicate.id` matching the file-level `predicate_id`.

### 5. Inspect Existing Relationships

Use `subject_entity_id + object_entity_id + predicate.id + scope` as the semantic deduplication key within the corresponding `relationships/machine/<predicate_id>.yaml`:

- If the same relationship already exists, add only evidence, description, scope, or an updated timestamp.
- If the direction is reversed and the predicate is directional, do not automatically treat it as the same relationship.
- If evidence conflicts or scopes differ, retain it as a candidate and request confirmation in the report.
- Do not register the same relationship fact more than once.

### 6. Write the Relationship Fact and Projection

Assign a unique `relationship_id` to each new relationship and write each new or updated complete fact to the corresponding `relationships/machine/<predicate_id>.yaml`.

Synchronize the corresponding `relationships/human/<predicate_id>.md` for human review of facts under that predicate.

Also synchronize:

- `.registry/machine/relationship_registry.yaml`
- `.registry/human/relationship_registry.md`

`.registry/machine/relationship_registry.yaml` registers only `predicate_id`, names, the machine fact-file path, the human fact-file path, relationship count, status, and update time.

Before writing, confirm that both subject and object exist in the current `.registry/machine/entity_registry.yaml`, and that every referenced `resource_id` and `entity_resource_map` entry exists.

This operation does not invoke `edit_knowledge_graph` and does not write `.registry/machine/knowledge_graph_registry.yaml`, `.registry/human/knowledge_graph_registry.md`, or `knowledge_graph/**`. If the user later requests a graph fact, return to the Router so `edit_knowledge_graph` can be validated and confirmed separately.

### 7. Output Report

Output `relate_entities_report` containing at least:

- Number of entities read;
- Numbers of relationships created, updated, and skipped;
- Each relationship's `relationship_id`, subject, object, and predicate;
- Affected `relationships/machine/<predicate_id>.yaml` and `relationships/human/<predicate_id>.md` files;
- Synchronized machine and human Relationship registry files;
- Evidence references;
- Reasons for skipped items and questions requiring confirmation;
- Whether a separate follow-up `edit_knowledge_graph` operation is recommended.

## Constraints

- Do not modify `.registry/machine/entity_registry.yaml` or `.registry/human/entity_registry.md`.
- Do not create entities.
- Do not modify resource tables, the resource registry, or Entity content.
- Do not write to the Knowledge Graph registry or graph-fact files.
- Relationship nodes may only be entities present in the current `.registry/machine/entity_registry.yaml`.
- Every relationship must be traceable to an Entity content file or source material.
- Uncertain relationships may appear only as candidates in the report.
