# Create a Knowledge Base

## Input

- Knowledge-base name.

## Structure to Create

Create the following under the current Valhalla root:

```text
Wiki/Wiki_<knowledge-base-name>/
    Wiki.md
    index.md
    log.md
    .virtualDatabase/
        machine/
            local_resources.yaml
            required_resources.yaml
            excluded_resources.yaml
        human/
            local_resources.md
            required_resources.md
            excluded_resources.md
    .registry/
        machine/
            entity_registry.yaml
            entity_resource_map.yaml
            relationship_registry.yaml
            knowledge_graph_registry.yaml
            conversation_entity_registry.yaml
            engineering_entity_registry.yaml
        human/
            entity_registry.md
            entity_resource_map.md
            relationship_registry.md
            knowledge_graph_registry.md
            conversation_entity_registry.md
            engineering_entity_registry.md
    entities/
    relationships/
        machine/
        human/
    knowledge_graph/
        machine/
        human/
    conversation_entities/
    engineering_entities/
```

## Initialization

- `Wiki.md`: Record the knowledge-base name, purpose, current scope, and entry links.
- `index.md`: Create empty sections for sources, entities, concepts, questions, and synthesis reports.
- `log.md`: Append `## [YYYY-MM-DD] create | <knowledge-base-name>`.
- Write the three machine resource tables to `.virtualDatabase/machine/`: `.virtualDatabase/machine/local_resources.yaml`, `.virtualDatabase/machine/required_resources.yaml`, and `.virtualDatabase/machine/excluded_resources.yaml`. Initialize them from `template/knowledge_base/resource_table_registry_template.yaml`, setting the appropriate table name and purpose for each. These are the machine-authoritative membership tables.
- Write the three human-readable resource tables to `.virtualDatabase/human/`: `.virtualDatabase/human/local_resources.md`, `.virtualDatabase/human/required_resources.md`, and `.virtualDatabase/human/excluded_resources.md`. Initialize them from `template/knowledge_base/resource_table_template.md`. These are human-readable projections.
- `.registry/machine/entity_registry.yaml`: Create an empty Entity registry from `template/knowledge_base/entity/entity_registry_template.yaml`.
- `.registry/human/entity_registry.md`: Create a human-readable summary scaffold from `template/knowledge_base/entity/entity_registry_template.md`, linking back to `.registry/machine/entity_registry.yaml`.
- `.registry/machine/entity_resource_map.yaml`: Initialize from `template/resource/entity_resource_map_template.yaml`.
- `.registry/human/entity_resource_map.md`: Initialize from `template/resource/entity_resource_map_template.md`.
- `.registry/machine/relationship_registry.yaml`: Initialize from `template/knowledge_base/relationship/relationship_registry_template.yaml` as an empty relationship-fact file index.
- `.registry/human/relationship_registry.md`: Initialize from `template/knowledge_base/relationship/relationship_registry_template.md` as an empty human-readable relationship-fact index.
- `relationships/machine/`: Store relationship-fact YAML files grouped by `predicate_id`, using `template/knowledge_base/relationship/relationship_fact_file_template.yaml`.
- `relationships/human/`: Store the corresponding human-readable Markdown projections of relationship facts, using `template/knowledge_base/relationship/relationship_fact_file_template.md`.
- `.registry/machine/knowledge_graph_registry.yaml`: Initialize from `template/knowledge_base/knowledge_graph/knowledge_graph_registry_template.yaml` as an empty graph-fact index.
- `.registry/human/knowledge_graph_registry.md`: Initialize from `template/knowledge_base/knowledge_graph/knowledge_graph_registry_template.md` as an empty human-readable graph-fact index.
- `knowledge_graph/machine/`: Store user-confirmed graph-fact YAML files, using `template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.yaml`.
- `knowledge_graph/human/`: Store the corresponding human-readable Markdown projections of graph facts, using `template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.md`.
- `.registry/machine/conversation_entity_registry.yaml` and `.registry/human/conversation_entity_registry.md`: Initialize from the Conversation Entity registry templates.
- `.registry/machine/engineering_entity_registry.yaml` and `.registry/human/engineering_entity_registry.md`: Initialize from the Engineering Entity registry templates. An empty registry's `entities` value must be `[]`.
- `entities/`, `conversation_entities/`, and `engineering_entities/`: Store the corresponding Entity content files.
- Add or update the following entry in the current root's `wiki_registry.yaml`: `kb_name`, `wiki_path: Wiki/Wiki_<knowledge-base-name>`, `status: active`, `created_at`, `updated_at`, and `description`.
- Synchronize the human-readable `wiki_registry.md` projection. If it conflicts with YAML, `wiki_registry.yaml` takes precedence.

Machine YAML and human-readable Markdown for resource tables, registries, relationship facts, and graph facts must be created or synchronized in pairs. The effective resource collection reads only entries with `membership_status: active` in YAML. Every Markdown file is a human-readable projection and must never overwrite YAML.

Do not start the knowledge base unless the user explicitly requests “create and start.”
