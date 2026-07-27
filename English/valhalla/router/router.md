# Router

The Router maps each user request to exactly one business category. Section headings are for navigation only and are not runtime categories. If a request is ambiguous or matches multiple categories, stop and list the candidate categories.

## Status and Navigation

Use these categories to inspect the current system state, current knowledge-base state, or help documentation. These operations are normally read-only; `help` does not load a Contract.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `status` | current status, current Valhalla status, status | `contract\status\status_contract.yaml` |
| `os_status` | current system status, os_status | `contract\status\os_status_contract.yaml` |
| `kb_status` | current knowledge-base status, which knowledge base is active, current knowledge base | `contract\status\kb_status_contract.yaml` |
| `help` | help, Valhalla help, how to use Valhalla, available commands, what is the system, what is bootstrap, what is a contract | Use the Reference and Help navigation in `SKILL.md` for the requested help topic; do not load a Contract |

## Root Management

Use these categories to inspect, create, register, switch, remove, or fuse Valhalla roots. Root-level writes have a broad impact and normally require admin state and explicit confirmation.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `list_roots` | list available Valhalla roots, list roots, show roots, root list | `contract\valhalla_root_operation\list_roots_contract.yaml` |
| `show_current_root` | show the current Valhalla root, current root | `contract\valhalla_root_operation\show_current_root_contract.yaml` |
| `create_root` / `register_root` / `switch_root` / `remove_root` / `fuse_roots` | create, register, switch, remove, fuse, merge, or consolidate a Valhalla root | `contract\valhalla_root_operation\root_operation_contract.yaml` |

## Knowledge-Base Lifecycle

Use these categories to list, create, register, start, exit, unregister, or rename knowledge bases under the current root. These operations manage the knowledge bases themselves; they do not perform semantic processing of source material.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `list_root` | list knowledge bases under the current root, which knowledge bases are under the current root, knowledge-base list | `contract\kb_operation\list_root_contract.yaml` |
| `create_kb` | create a knowledge base, new knowledge base | `contract\kb_operation\create_kb_contract.yaml` |
| `register_existing_kb` | register an existing knowledge base, register an existing Wiki as a knowledge base, register an existing KB | `contract\kb_operation\register_existing_kb_contract.yaml` |
| `start_kb` | start or switch knowledge base | `contract\kb_operation\start_kb_contract.yaml` |
| `exit_kb` | exit the current knowledge base | `contract\kb_operation\exit_kb_contract.yaml` |
| `remove_kb` | delete, remove, or unregister a knowledge base; remove a knowledge base from the current root | `contract\kb_operation\remove_kb_contract.yaml` |
| `rename_kb` | change or rename a knowledge base; rename knowledge base <old name> to <new name> | `contract\kb_operation\rename_kb_contract.yaml` |

## Cross-Knowledge-Base Maintenance

Use these categories to fuse knowledge bases or migrate a knowledge base across roots. These operations rewrite many registries, resource mappings, or target knowledge-base files, so they must inspect first and require confirmation before fixing.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `fuse_kbs` | fuse, merge, or consolidate knowledge bases; fuse knowledge bases <source list> into <new knowledge base>; fusing every knowledge base in the current root is not supported | `contract\kb_operation\fuse_kbs_contract.yaml` |
| `migrate_kb` | migrate a knowledge base, copy a knowledge base from another root, migrate a knowledge base from a root; the target root is always the current root | `contract\kb_operation\migrate_kb_contract.yaml` |

## Resources and Resource Tables

Use these categories to register source material, edit knowledge-base resource tables, or maintain the global blacklist. Resource identity is determined by `resource_id`; resource tables reference only resource identities.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `register_resource` | register a source file in resource_registry | `contract\resource\register_resource_contract.yaml` |
| `edit_resource_table` | edit a resource table | `contract\kb_operation\edit_resource_table_contract.yaml` |
| `blacklist_operation` | add to or remove from the blacklist | `contract\resource\blacklist_operation_contract.yaml` |
| `sync_resource_usage` | synchronize resource usage, clean up historical resource usage, rebuild the resource-reference index | `contract\resource\sync_resource_usage_contract.yaml` |

## Knowledge Processing and Project Work

Use these categories to ingest sources, query a knowledge base, organize entity relationships, maintain a knowledge graph, or use a knowledge base to advance papers, code, experiments, reviews, plans, reports, or engineering tasks.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `ingest` | ingest source material | `contract\kb_operation\ingest_contract.yaml` |
| `query` | ask a question about the currently active knowledge base | `contract\kb_operation\query_contract.yaml` |
| `relate_entities` | summarize or organize relationships among entities in this knowledge base | `contract\kb_operation\relate_entities_contract.yaml` |
| `edit_knowledge_graph` | build, organize, or edit the knowledge graph among entities in this knowledge base | `contract\kb_operation\edit_knowledge_graph_contract.yaml` |
| `ingest_conversation` | ingest or archive a conversation | `contract\kb_operation\ingest_conversation_contract.yaml` |
| `ingest_engineering` | ingest or archive engineering experience | `contract\kb_operation\ingest_engineering_contract.yaml` |
| `project_work` | use a knowledge base to advance a paper, codebase, experiment, review, plan, report, or engineering task | `contract\project_work\project_work_contract.yaml` |

## Administration, Inspection, and Ordinary File Tasks

Use these categories to enter or exit admin state, inspect knowledge bases, fix reported inspection issues, or identify ordinary tasks outside Valhalla.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `admin_operation` | enter or exit admin state | `contract\status\admin_operation_contract.yaml` |
| `lint` / `lint_fix` | inspect, deeply inspect, or inspect every knowledge base; fix previously listed inspection issues | `contract\lint\lint_contract.yaml` |
| `ordinary_file_work` | the request is unrelated to Valhalla | Do not enter a Valhalla workflow; handle it as an ordinary file task |

If the help topic is unclear, display only the help menu rather than loading every Reference at once. For available commands, read `references\command_reference.md`. For system concepts, read `references\system_overview.md`.
