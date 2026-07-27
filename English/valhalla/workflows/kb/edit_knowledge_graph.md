# edit_knowledge_graph Workflow

## Purpose

Create or modify a graph fact from existing Entity facts and Relationship facts according to graph requirements confirmed by the user.

A graph fact is a user-confirmed graph fact: it records the user's decision to organize selected relationship types, relationship facts, and entities into a graph. A graph fact may only combine, filter, and confirm existing relationship facts; it must not create or modify Entity facts or Relationship facts.

Machine YAML is authoritative data, and human Markdown is a human-readable review projection. Markdown must not overwrite YAML.

## Workflow

### 1. Determine Graph Requirements

From the user's request, determine the graph fact's purpose, name, relationship-type scope, and selection rules. For example, the user may decide to create a graph composed of relationship types A, B, and C.

If the user has not explicitly confirmed the graph scope, output only the questions requiring confirmation and do not write a graph fact.

### 2. Locate the Current Knowledge Base

Confirm the following paths:

- `Wiki/Wiki_<knowledge-base-name>/.registry/machine/entity_registry.yaml`
- `Wiki/Wiki_<knowledge-base-name>/.registry/machine/relationship_registry.yaml`
- `Wiki/Wiki_<knowledge-base-name>/.registry/human/relationship_registry.md`
- `Wiki/Wiki_<knowledge-base-name>/relationships/machine/*.yaml`
- `Wiki/Wiki_<knowledge-base-name>/relationships/human/*.md`
- `Wiki/Wiki_<knowledge-base-name>/.registry/machine/knowledge_graph_registry.yaml`
- `Wiki/Wiki_<knowledge-base-name>/.registry/human/knowledge_graph_registry.md`
- `Wiki/Wiki_<knowledge-base-name>/knowledge_graph/machine/`
- `Wiki/Wiki_<knowledge-base-name>/knowledge_graph/human/`

Create `knowledge_graph/machine/` or `knowledge_graph/human/` if missing. If a graph registry is missing, initialize it from the corresponding template.

### 3. Read Fact Sources

- `.registry/machine/entity_registry.yaml` is the source of node facts.
- `.registry/machine/relationship_registry.yaml` is the Relationship-fact file index.
- `relationships/machine/<predicate_id>.yaml` is the source of edge facts for that relationship type.

A graph fact must reference existing `entity_id` and `relationship_id` values. Do not create or modify Relationship facts, and do not use a graph-fact file as a second Relationship registry.

### 4. Create or Modify a Graph Fact

The machine-authoritative file is `knowledge_graph/machine/<graph_id>.yaml`, created from:

`template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.yaml`

The human-review projection is `knowledge_graph/human/<graph_id>.md`, created from:

`template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.md`

The graph fact must record at least:

- `graph_id`, name, purpose, status, creator, and update time;
- User-confirmed `relationship_sources`;
- `included_relationships`;
- `included_entities`;
- `selection_rule`;
- `layout` and display notes;
- `provenance.authority_note`.

### 5. Validate Consistency

Before writing, verify that:

- The `graph_id`, machine path, and human path are unique;
- The Graph registry entry and graph-fact file use the same `graph_id`;
- Every `predicate_id` in `relationship_sources` exists in `.registry/machine/relationship_registry.yaml`;
- Each `relationship_sources.fact_file` points to an existing `relationships/machine/<predicate_id>.yaml`;
- Every item in `included_relationships` exists in the corresponding Relationship-fact file;
- Every item in `included_entities` exists in `.registry/machine/entity_registry.yaml`;
- `included_entities` contains at least every subject and object endpoint in `included_relationships`;
- The graph fact does not introduce new Entity or Relationship facts.

If validation fails, do not publish the change; explain the failure in the report.

### 6. Synchronize the Registry and Human Projection

When creating or modifying a graph fact, synchronize:

- `knowledge_graph/machine/<graph_id>.yaml`
- `knowledge_graph/human/<graph_id>.md`
- `.registry/machine/knowledge_graph_registry.yaml`
- `.registry/human/knowledge_graph_registry.md`

`.registry/machine/knowledge_graph_registry.yaml` only indexes graph facts; it does not store complete node and edge facts.

`.registry/human/knowledge_graph_registry.md` and `knowledge_graph/human/<graph_id>.md` are human-readable review projections and must not overwrite YAML.

### 7. Output

Output `edit_knowledge_graph_report` containing the operation type, target knowledge base, created or modified `graph_id`, user-confirmed relationship types, counts of included Relationships and entities, modified files, Relationship-fact files used, skipped content, and questions requiring confirmation.

## Constraints

- `.registry/machine/knowledge_graph_registry.yaml` is the graph-fact index layer.
- `knowledge_graph/machine/*.yaml` is the machine-authoritative graph-fact layer.
- `knowledge_graph/human/*.md` is the human-review projection of graph facts.
- `.registry/machine/entity_registry.yaml` is the node-fact layer.
- `relationships/machine/*.yaml` is the Relationship-fact layer.
- A graph fact must not create or modify Relationship facts.
- Do not modify resource tables, the Entity registry, Entity content, the Relationship registry, or Relationship-fact files.
