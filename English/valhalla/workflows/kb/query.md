# query

## Objective

Answer `query_text` from the currently active knowledge base while preserving traceable provenance and clearly distinguishing knowledge-base evidence, web sources, and model inference.

## Effective Resource Scope

1. Compute the effective resources from the three YAML resource tables and the global blacklist:

   ```text
   (resource_id values with membership_status == active in .virtualDatabase/machine/local_resources.yaml
   ∪ resource_id values with membership_status == active in .virtualDatabase/machine/required_resources.yaml)
   - resource_id values with membership_status == active in .virtualDatabase/machine/excluded_resources.yaml
   - resource_id values listed in blacklist_registry.yaml
   ```

2. Markdown resource tables are for human inspection only and do not determine resource membership.
3. Original source material may be read only from public representations under `Library/public_resources/` for effective `resource_id` values.
4. Do not read or cite resources in the exclusion table, global blacklist, or inactive membership entries.

## Query Process

1. Parse `query_text`, optional `query_scope`, and expected output to define the question's boundary.
2. Search the following parts of the current knowledge base first:
   - `.registry/machine/entity_registry.yaml` and `entities/`;
   - `.registry/machine/relationship_registry.yaml`;
   - `.registry/machine/knowledge_graph_registry.yaml` and `knowledge_graph/`;
   - `conversation_entity_registry.yaml` and `conversation_entities/`;
   - `engineering_entity_registry.yaml` and `engineering_entities/`.
3. Record the actual `entity_id` values, relationships, and graphs used.
4. If existing knowledge is insufficient, select relevant `resource_id` values from the effective resource scope and read their available public representations.
5. Record each `resource_id`, representation type, and internal evidence location actually used.
6. If knowledge-base evidence is still insufficient:
   - Search the web only if `allow_network_search: true`.
   - If the field is absent or `false`, ask the user for permission first.
   - Treat web search results only as temporary external sources.
   - Do not describe web results as pre-existing knowledge-base knowledge.
7. Answer from the evidence and clearly distinguish:
   - Conclusions explicitly supported by the knowledge base;
   - Information provided by external sources;
   - Inferences derived from evidence;
   - Uncertain or conflicting content.
8. Do not modify or archive any knowledge-base file unless the user explicitly requests it.

## Stop or Provide a Qualified Answer

Do not state a definitive conclusion when:

- Evidence is insufficient;
- Resources contradict one another;
- A resource is excluded or blacklisted;
- Resource content or version cannot be confirmed;
- Provenance location is insufficient;
- The question falls outside the current knowledge base's scope.

Instead, report confirmed information, evidence gaps, uncertainty, and suggested next steps.

## query_report

Output at least:

- `answer`
- `target_kb`
- `knowledge_used`
- `source_records`
- `external_sources`
- `inferences`
- `conflicts`
- `uncertainty`
- `suggested_follow_up`

Prefer the following form for `source_records`:

```text
resource_id → entity_id → evidence_location → supported_claim
```

Do not use only a filename as provenance. Record web sources under `external_sources`; do not mix them into knowledge-base provenance records.
