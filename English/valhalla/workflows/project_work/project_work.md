# project_work Workflow

## Purpose

Use the specified knowledge base to advance a concrete project task, such as a paper, codebase, experiment, review, plan, report, or engineering implementation.

This Workflow is responsible only for project output and does not directly maintain the knowledge base's underlying registries.
If new entities, Entity extensions, Relationship corrections, or additional engineering summaries are needed, propose the relevant follow-up operations in the report.

## Write Boundaries

- Permission to read a knowledge base does not grant permission to modify it.
- Do not modify the Wiki, resource tables, resource registry, entities, Relationships, Knowledge Graphs, Conversation Entities, or Engineering Entities.
- Modify only project files explicitly specified by the user and supporting files necessary to complete those targets.
- If the user does not specify a target path, produce the project deliverable only in the response.
- Before creating or modifying a file that was not explicitly specified, list its exact proposed path and obtain user confirmation.
- If project results should be preserved, recommend `ingest_conversation` or `ingest_engineering` in the report. Do not write results directly back to the knowledge base from this Workflow.

## Process

1. Determine which knowledge to use.

   Search and read content relevant to `project_goal`:

   * `.registry/machine/entity_registry.yaml`
   * `.registry/human/entity_registry.md`
   * `entities/`
   * `.registry/machine/entity_resource_map.yaml`
   * `.registry/human/entity_resource_map.md`
   * `.registry/machine/relationship_registry.yaml`
   * `.registry/human/relationship_registry.md`
   * `.registry/machine/knowledge_graph_registry.yaml`
   * `.registry/human/knowledge_graph_registry.md`
   * `knowledge_graph/`
   * `.registry/machine/conversation_entity_registry.yaml`
   * `.registry/human/conversation_entity_registry.md`
   * `conversation_entities/`
   * `.registry/machine/engineering_entity_registry.yaml`
   * `.registry/human/engineering_entity_registry.md`
   * `engineering_entities/`
   * Public copies of sources within the effective resource scope

   Compute the effective resource scope from the three machine-authoritative YAML resource tables:

   ```text
   (active resource_id values in .virtualDatabase/machine/local_resources.yaml
   ∪ active resource_id values in .virtualDatabase/machine/required_resources.yaml)
   - active resource_id values in .virtualDatabase/machine/excluded_resources.yaml
   - resource_id values in the global blacklist
   ```

   Same-named Markdown resource tables are only for human inspection and do not determine membership.

2. Build the project-work context.

   Organize a working context for the current project that includes at least:

   * Project objective;
   * Project type;
   * Known background;
   * Available sources;
   * Key entities;
   * Key relationships;
   * Existing engineering or conversation summaries;
   * User constraints;
   * Current gaps;
   * Scope that can be completed in this operation.

   If sources are insufficient, do not fabricate content; ask whether web sources may be searched.

3. Develop a project-advancement plan from this knowledge.

   Examples:

   Paper task:

   * Define the thesis;
   * Organize supporting evidence;
   * Develop a section structure;
   * Add citations;
   * Draft or revise the text.

   Coding task:

   * Define functional objectives;
   * Identify relevant Engineering Entities;
   * Locate target files;
   * Design the modification;
   * Produce a patch or implementation notes.

   Experimental task:

   * Define the experimental question;
   * Organize variables and controls;
   * Design the experimental process;
   * Plan record-keeping;
   * Produce an experimental protocol or analysis template.

   Report or review task:

   * Define the topic;
   * Aggregate relevant entities;
   * Organize the source narrative;
   * Produce a structured draft;
   * Mark provenance and uncertainty.

4. Review the project-advancement plan. If it has defects, return to the preceding step and revise it using the review. The `develop plan → review plan` loop must run no more than five times; after five cycles, stop and ask the user.
5. Create or modify project deliverables according to the plan. Before writing, re-check target paths and the read-only knowledge-base boundary.
6. Output `project_work_report`.

## project_work_report

The report must include at least:

- `project_goal`: The current project objective.
- `completion_status`: Complete, partially complete, or blocked.
- `target_kb`: The knowledge base used.
- `knowledge_used`: Key knowledge used, including relevant `entity_id` values.
- `source_records`: Provenance records, preferably in the form `resource_id -> entity_id -> supported conclusion or deliverable`.
- `created_files`: Files created in this operation; explicitly write `none` if there are none.
- `modified_files`: Files modified in this operation; explicitly write `none` if there are none.
- `unresolved_questions`: Remaining questions, evidence gaps, and uncertainty.
- `suggested_knowledge_writeback`: Knowledge worth preserving and the recommended ingestion operation; explicitly write `none` if there is none.

Do not record a filename alone as provenance. When stable identities exist, record both `resource_id` and the relevant `entity_id`.
