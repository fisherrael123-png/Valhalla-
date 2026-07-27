# Command Reference

Use this document to help research-group members understand how to invoke Valhalla and to help Codex map user requests to the categories and Contracts defined by the latest Router.

Group members do not need to remember internal category names. Prefer the natural-language expressions under “Common Commands for Group Members.” As long as the intent is clear, Codex should process the request under the corresponding category. If the category is uncertain, consult this document first; if uncertainty remains, use the trigger conditions and load target in `router.md`.

## Risk-Level Conventions

| Risk level | Meaning | Default handling |
|---|---|---|
| `low` | Read-only work, status queries, ordinary questions, or work that does not enter a Valhalla write process. | May execute directly; ask if the target is unclear. |
| `medium` | Includes writes, but both the target and operation are explicit. | May execute directly; ask if the target is unclear. |
| `high` | Includes broad graph reconstruction, cross-knowledge-base or global maintenance, writes whose targets or results are not predetermined, and root-level creation or switching. | Must obtain explicit confirmation before acting. |

## State Model

The Valhalla system has only two states:

- `base`: General state; only non-administrative operations are permitted.
- `admin`: Administrative state; administrative operations are permitted.

## Session State

A session has only two states:

- `idle`: Idle state; no knowledge base is currently active.
- `kb:<name>`: The knowledge base named <name> is active, and some operations use it as their default target.

## Core Principles

- Every instruction follows the execution path `router` → `contract` → `workflow`.
- The `router` classifies the instruction and loads the relevant operation-entry `contract`.
- A `contract` is a state and eligibility gate. It checks the current system and session states, loads the working `workflow` only when all requirements are satisfied, and assigns a risk level to the operation. It functions like a security checkpoint through which only authorized operations may pass.
- A `workflow` contains the actual working procedure.

## Common Commands for Group Members

### Help Navigation

Help is a read-only documentation entry point. It does not load a Contract or execute a system service.

| What you want to learn | Example wording | Router category | Read |
|---|---|---|---|
| Display the help menu | `help`, `Valhalla help` | `help` | Display only the four-part help menu; do not read every Reference. |
| System overview | `system overview`, `what is Valhalla`, `system principles` | `help` | `references/system_overview.md` |
| Commands and usage | `command help`, `available commands`, `how to use Valhalla` | `help` | `references/command_reference.md` |
| Bootstrap startup process | `startup help`, `what is bootstrap` | `help` | `references/bootstrap.md` |
| Contract format and execution model | `Contract help`, `Contract format` | `help` | `references/contract_format.md` |

### Inspect Status and Select a Knowledge Base

| What you want to do | Example wording | Router category | Risk level | Result |
|---|---|---|---|---|
| Inspect the complete current state | `current Valhalla`, `current status`, `status` | `status` | `low` | Report both system state and current knowledge-base state. |
| Inspect only the current system state | `current system status`, `os_status` | `os_status` | `low` | Report the current Valhalla root and system state. |
| Inspect the current root | `current root`, `current Valhalla root` | `show_current_root` | `low` | Report only the current Valhalla root. |
| Inspect the current knowledge base | `current knowledge base`, `which knowledge base is active` | `kb_status` | `low` | Report whether the session is currently in a knowledge-base state. |
| List knowledge bases under the current root | `which knowledge bases are under the current root`, `knowledge-base list`, `list knowledge bases under the current root` | `list_root` | `low` | Read `wiki_registry.yaml` and list the knowledge bases registered under the current root. |
| Create a knowledge base | `new knowledge base <knowledge-base name>`, `create knowledge base <knowledge-base name>` | `create_kb` | `high` | Create a new Wiki directory and knowledge-base scaffold. |
| Register an existing knowledge-base directory | `register existing knowledge base <knowledge-base name>`, `register knowledge base <knowledge-base name>` | `register_existing_kb` | `high` | Add an existing, structurally valid `Wiki/Wiki_<knowledge-base-name>/` directory to `wiki_registry.yaml/md`; verify that resources referenced by the KB's `entity_resource_map.yaml` exist; and hand off to `sync_resource_usage` to populate usage back-references in `resource_registry.yaml/md`. This operation does not create or modify the directory and does not start the knowledge base. |
| Start or switch knowledge base | `start knowledge base <knowledge-base name>`, `switch to knowledge base <knowledge-base name>` | `start_kb` | `medium` | Set the target as the active knowledge base. |
| Exit the current knowledge base | `exit knowledge base`, `stop using the current knowledge base` | `exit_kb` | `medium` | Leave the current knowledge-base state. |
| Remove or unregister a knowledge base | `delete knowledge base <knowledge-base name>`, `unregister knowledge base <knowledge-base name>` | `remove_kb` | `high` | Unregister the knowledge base from the current root and hand off to `sync_resource_usage` to remove usage back-references to that KB from `resource_registry.yaml/md`. The `Wiki/Wiki_<knowledge-base-name>/` directory is not deleted. |
| Rename a knowledge base | `rename knowledge base <old name> to <new name>`, `change knowledge-base name from <old name> to <new name>` | `rename_kb` | `high` | Change the display name, registered name, and Wiki directory name. Then hand off to `sync_resource_usage` to refresh the usage back-reference index. The current knowledge base must be exited and the impact scope confirmed before execution. |
| Fuse multiple knowledge bases | `fuse knowledge bases A, B, C into Combined`, `merge knowledge bases A and B into Combined` | `fuse_kbs` | `high` | Requires admin state and an idle session. Only an explicit list of source knowledge bases is supported; fusing every knowledge base in the current root is not. First perform a read-only review of conflicts in entities, relationships, conversations, engineering records, and resource tables. After confirmation, create the target knowledge base and hand off to `sync_resource_usage`. Report `excluded_but_used_resources`. |
| Migrate a knowledge base from an external root | `migrate knowledge base root2:ai-engineering`, `migrate knowledge base root2:ai-engineering new name ai-engineering-migrated`, `migrate knowledge base E:\valhallaroot2\Wiki\Wiki_ai-engineering` | `migrate_kb` | `high` | Requires admin state and an idle session. The target root is always the current root. The source knowledge base must be registered under a registered, non-current root; path input must exactly match a registered KB path. After confirmation, copy the KB, rewrite `resource_id` values, supply public copies, record source-blacklist differences in the migrated KB's exclusion table, register the result, and hand off to `sync_resource_usage`. The migrated knowledge base is not started automatically. |

### Root Management

A Root is the top-level directory of an entire Valhalla system. Most group members only need to inspect the current root. Creating, registering, switching, or removing a root is a maintenance operation.

| What you want to do | Example wording | Router category | Risk level | Result |
|---|---|---|---|---|
| List all roots | `list Valhalla roots`, `list roots`, `root list` | `list_roots` | `low` | List all registered Valhalla roots. |
| Create a Valhalla root | `create Valhalla <path> [alias]`, `initialize Valhalla <path> [alias]` | `create_root` | `high` | Create the root structure and register it as required by the Contract. |
| Register an existing root | `register Valhalla <alias> <path>` | `register_root` | `high` | Add an existing root to the root registry. |
| Switch the default root | `switch Valhalla <alias or path>` | `switch_root` | `high` | Switch the current default Valhalla root. |
| Remove a root registration | `remove Valhalla <alias or path>`, `forget Valhalla <alias or path>` | `remove_root` | `high` | Remove the entry from the root registry; this does not delete the directory. |
| Fuse multiple roots | `fuse sources <source-root-1>, <source-root-2> into <new-root-path> [alias <new-root-alias>]`, `merge roots into <new-root-path> from <source-root-list>` | `fuse_roots` | `high` | Read-only audit multiple source roots, resolve resource identity, blacklist, and KB naming decisions, then create a new derived root without modifying any source root. If no alias is provided, enter `post_fusion_registration` and ask at the end whether the new root should be registered. |

### Query and Organize Knowledge

| What you want to do | Example wording | Router category | Risk level | Result |
|---|---|---|---|---|
| Ask the current knowledge base a question | `query <question>`, `ask the current knowledge base <question>` | `query` | `low` | Answer using the active knowledge base while distinguishing knowledge-base sources, external sources, inferences, and uncertainty. Search the web only with the user's permission when knowledge-base evidence is insufficient. |
| Register a resource | `register resource <filename or Library-relative path>`, `register resource <path>` | `register_resource` | `high` | Assign a stable `resource_id` to source material in a non-public Library directory, synchronize the YAML and Markdown resource registries, and create or bind a public copy. |
| Synchronize resource usage | `synchronize resource usage`, `clean historical resource usage`, `rebuild the resource-reference index` | `sync_resource_usage` | `high` | May run in base or admin state and while idle or in `kb:<name>`. Using the KBs registered in the target root's `wiki_registry.yaml`, rebuild usage back-references in `resource_registry.yaml/md` from each KB's `entity_registry.yaml` and `entity_resource_map.yaml`, and remove stale historical usage. |
| Ingest source material | `ingest <path>`, `add <path> to the current knowledge base` | `ingest` | `high` | Summarize the material as an entity, write its content, synchronize `.registry/machine/entity_registry.yaml` and `.registry/human/entity_registry.md`, and register provenance mappings. |
| Organize entity relationships | `organize entity relationships`, `summarize entity relationships in this knowledge base` | `relate_entities` | `high` | Analyze entity relationships and write confirmed relationship facts to `.registry/machine/relationship_registry.yaml`; the graph projects only these relationships. |
| Build or edit the knowledge graph | `update knowledge graph`, `rebuild knowledge graph`, `organize knowledge graph` | `edit_knowledge_graph` | `high` | Build, organize, or edit the current knowledge base's knowledge graph. |
| Ingest a conversation archive | `ingest conversation`, `archive this conversation`, `ingest this conversation summary` | `ingest_conversation` | `high` | Integrate the conversation summary as conversation entities. |
| Ingest engineering experience | `ingest engineering experience`, `archive engineering experience`, `record this engineering experience` | `ingest_engineering` | `high` | Integrate engineering experience as engineering entities. |
| Initialize the engineering-entity structure | `initialize engineering-entity structure`, `create engineering-entity registry` | `init_engineering_entities` | `medium` | Create only the empty engineering-entity registry and directories; do not write example entities. |

### Resource-Table Operations

All resource-table operations enter `edit_resource_table`. Users do not need to know the internal structure of the three tables; they need only specify the table, action, and path or name.

Each resource table has same-named YAML and Markdown files. YAML is the machine-authoritative membership table; Markdown displays the canonical name, admission input, and current source path. Adding a resource appends it incrementally. Removing a resource immediately marks it for cleanup and removes it from the effective resource collection; lint performs the later batch cleanup.

| What you want to do | Example wording | Router category | Risk level | Result |
|---|---|---|---|---|
| Add to this KB's resource table | `this-KB resource table, add <path>` | `edit_resource_table` | `medium` | Make the resource available to the current knowledge base. |
| Remove from this KB's resource table | `this-KB resource table, remove <path>` | `edit_resource_table` | `medium` | Remove the resource from the current knowledge base's resource scope. |
| Mark as required | `required-resource table, add <path>` | `edit_resource_table` | `medium` | Mark the resource as mandatory for this knowledge base. |
| Remove the required designation | `required-resource table, remove <path>` | `edit_resource_table` | `medium` | Remove the mandatory-use designation. |
| Exclude a resource | `excluded-resource table, add <path>` | `edit_resource_table` | `medium` | Mark the resource as unavailable to this knowledge base. |
| Cancel resource exclusion | `excluded-resource table, remove <path>` | `edit_resource_table` | `medium` | Remove the resource from the exclusion table. |
| Inspect or explain resource tables | `show resource tables`, `explain the current resource scope` | `edit_resource_table` or `query` | `low` | For a read-only explanation, use query/read-only handling. For a change, enter `edit_resource_table` and raise risk to `medium`. |

### Administration and Inspection

| What you want to do | Example wording | Router category | Risk level | Result |
|---|---|---|---|---|
| Enter administrative state | `activate administrative state`, `enter admin state` | `admin_operation` → `admin_enter` | `medium` | Enter admin state. |
| Exit administrative state | `end administrative state`, `exit admin state` | `admin_operation` → `admin_exit` | `medium` | Exit admin state and return to the general state. |
| Inspect the blacklist | `show blacklist`, `list blacklisted resources` | `blacklist_operation` → `list_blacklist` | `low` | Read and list globally blacklisted resources. |
| Add to the blacklist | `blacklist, add <path or name>` | `blacklist_operation` → `add_blacklist` | `high` | Add the entire resolved `resource_id` to the blacklist. |
| Remove from the blacklist | `blacklist, remove <blacklist_id>` | `blacklist_operation` → `remove_blacklist` | `high` | Remove the specified blacklist entry. |
| Inspect a knowledge base | `inspect <knowledge-base name>`, `inspect current knowledge base` | `lint` | `high` | Inspect structure, links, resource tables, indexes, and registries. |
| Deeply inspect a knowledge base | `deep inspection <knowledge-base name>`, `inspect all knowledge bases` | `lint` | `high` | Perform a broader or deeper inspection, including reporting registered entities whose context files are missing. |
| Fix inspection issues | `fix inspection issues <scope>` | `lint_fix` | `high` | Fix only previously listed issues or an explicit scope; confirm first when high-risk items are involved. To clean registrations with missing entity context, use `fix inspection issues missing_entity_content_file`. |

Recommended process for missing entity context:

```text
Enter admin state
Deep inspection <knowledge-base name>
Fix inspection issues missing_entity_content_file
```

After confirmation, this process removes only registrations from `entity_registry` and `entity_resource_map`. It does not delete files, modify `resource_registry.yaml`, or reconstruct missing content files.

### Advance a Project

Use `project_work` to complete a practical task with the knowledge base—for example, drafting a paper section, designing an experiment, organizing a review, developing a plan, advancing code, or analyzing results. It reads the knowledge base by default and does not automatically write anything back.

| What you want to do | Example wording | Router category | Risk level | Result |
|---|---|---|---|---|
| Advance a task using the current knowledge base | `Using the current knowledge base, advance: <task>` | `project_work` | `medium` | Convert current knowledge-base content into task context and produce the requested deliverable. |
| Draft a paper or review | `Using the current knowledge base, help me write/edit <paper section or review content>` | `project_work` | `medium` | Produce an argument structure, draft, evidence, and citations still needed. |
| Design an experiment or plan | `Using the current knowledge base, design <experiment/plan>` | `project_work` | `medium` | Produce objectives, hypotheses, variables, steps, risks, and evaluation criteria. |
| Advance code or an engineering implementation | `Using the current knowledge base, implement/modify <coding task>` | `project_work` | `medium` | Extract requirements, constraints, interfaces, test points, or an implementation plan. |
| Archive project-work results | `archive this project-work result`, `write this project decision back to Valhalla` | `ingest_engineering` or `ingest_conversation` | `high` | Write back only when the user explicitly asks to archive. Engineering experience uses `ingest_engineering`; a conversation or decision summary uses `ingest_conversation`. |

## Router Category Mapping

The Router selects a category from the user's intent. Business categories load their corresponding Contracts; `help` and `ordinary_file_work` follow the Router's direct-processing rules.
The Router does not execute Workflows, modify files directly, or bypass state checks and risk decisions in business Contracts.

| Router category | Trigger wording | Risk level | Load |
| --- | --- | --- | --- |
| `status` | current Valhalla, current status, status, show Valhalla status | `low` | `contract\status\status_contract.yaml` |
| `os_status` | current system status, os_status | `low` | `contract\status\os_status_contract.yaml` |
| `show_current_root` | current root, current Valhalla root, which root is active | `low` | `contract\valhalla_root_operation\show_current_root_contract.yaml` |
| `kb_status` | current knowledge base, which knowledge base is active, current KB status | `low` | `contract\status\kb_status_contract.yaml` |
| `list_roots` | list Valhalla roots, list roots, root list, available Valhalla roots | `low` | `contract\valhalla_root_operation\list_roots_contract.yaml` |
| `list_root` | which knowledge bases are under the current root, knowledge-base list, list knowledge bases under the current root | `low` | `contract\kb_operation\list_root_contract.yaml` |
| `create_root` | create Valhalla, initialize Valhalla, create Valhalla root | `high` | `contract\valhalla_root_operation\root_operation_contract.yaml` |
| `register_root` | register Valhalla, register existing root, register Valhalla root | `high` | `contract\valhalla_root_operation\root_operation_contract.yaml` |
| `switch_root` | switch Valhalla, switch root, use another Valhalla root | `high` | `contract\valhalla_root_operation\root_operation_contract.yaml` |
| `remove_root` | remove Valhalla, forget Valhalla, delete root registration, remove root registration | `high` | `contract\valhalla_root_operation\root_operation_contract.yaml` |
| `fuse_roots` | fuse roots, merge roots, consolidate roots, fuse source roots into a new root | `high` | `contract\valhalla_root_operation\root_operation_contract.yaml` |
| `create_kb` | new knowledge base, create knowledge base, new Wiki, create Wiki | `high` | `contract\kb_operation\create_kb_contract.yaml` |
| `register_existing_kb` | register existing knowledge base, register existing KB, register an existing Wiki as a knowledge base | `high` | `contract\kb_operation\register_existing_kb_contract.yaml` |
| `start_kb` | start knowledge base, switch knowledge base, enter knowledge base, use a knowledge base | `medium` | `contract\kb_operation\start_kb_contract.yaml` |
| `exit_kb` | exit knowledge base, stop using current knowledge base, close current knowledge base | `medium` | `contract\kb_operation\exit_kb_contract.yaml` |
| `remove_kb` | delete knowledge base, remove knowledge base, unregister knowledge base, remove knowledge base from current root | `high` | `contract\kb_operation\remove_kb_contract.yaml` |
| `rename_kb` | change knowledge-base name, rename knowledge base, give knowledge base another name | `high` | `contract\kb_operation\rename_kb_contract.yaml` |
| `fuse_kbs` | fuse knowledge bases, merge knowledge bases, consolidate knowledge bases, fuse knowledge bases A and B into Combined; fusing every KB in the current root is unsupported | `high` | `contract\kb_operation\fuse_kbs_contract.yaml` |
| `migrate_kb` | migrate knowledge base, copy a knowledge base from another root, migrate a knowledge base from a root; use `new name` to resolve a target-name conflict | `high` | `contract\kb_operation\migrate_kb_contract.yaml` |
| `query` | query, ask current knowledge base, answer from current knowledge base, explain current knowledge-base content | `low` | `contract\kb_operation\query_contract.yaml` |
| `project_work` | advance task using current knowledge base, use knowledge base to draft a paper, edit a review, design an experiment, develop a plan, advance code, or analyze results | `medium` | `contract\project_work\project_work_contract.yaml` |
| `edit_resource_table` | edit this-KB resource table, required-resource table, or excluded-resource table; add, remove, exclude, or unexclude a resource | `medium` | `contract\kb_operation\edit_resource_table_contract.yaml` |
| `register_resource` | register a resource, register Library material as a resource | `high` | `contract\resource\register_resource_contract.yaml` |
| `sync_resource_usage` | synchronize resource usage, clean historical resource usage, rebuild the resource-reference index | `high` | `contract\resource\sync_resource_usage_contract.yaml` |
| `ingest` | ingest source material, add material to current knowledge base, summarize material as an entity, import material | `high` | `contract\kb_operation\ingest_contract.yaml` |
| `relate_entities` | organize entity relationships, summarize entity relationships, analyze knowledge-item relationships, establish entity relationships | `high` | `contract\kb_operation\relate_entities_contract.yaml` |
| `edit_knowledge_graph` | update, rebuild, organize, or edit knowledge graph | `high` | `contract\kb_operation\edit_knowledge_graph_contract.yaml` |
| `ingest_conversation` | ingest conversation, archive this conversation, ingest this conversation summary, write conversation back to knowledge base | `high` | `contract\kb_operation\ingest_conversation_contract.yaml` |
| `ingest_engineering` | ingest engineering experience, archive engineering experience, record this engineering experience, write engineering lessons back to knowledge base | `high` | `contract\kb_operation\ingest_engineering_contract.yaml` |
| `init_engineering_entities` | initialize engineering-entity structure, create engineering-entity registry | `medium` | `contract\kb_operation\ingest_engineering_contract.yaml` |
| `admin_operation` | activate or enter administrative state; end or exit administrative state; dispatch to `admin_enter` or `admin_exit` | `medium` | `contract\status\admin_operation_contract.yaml` |
| `blacklist_operation` | show, add to, or remove from blacklist; dispatch to `list_blacklist`, `add_blacklist`, or `remove_blacklist` | `low/high` | `contract\resource\blacklist_operation_contract.yaml` |
| `lint` / `lint_fix` | inspect, deeply inspect, or inspect every knowledge base; fix confirmed issues after inspection | `high` | `contract\lint\lint_contract.yaml` |
| `help` | help, system overview, command help, startup help, Contract help | `low` | Read the Reference specified by `SKILL.md` for the topic; do not load a Contract |
| `ordinary_file_work` | ordinary file work, rewriting, summarization, code, or document processing unrelated to Valhalla | `low` | Do not enter a Valhalla workflow |
