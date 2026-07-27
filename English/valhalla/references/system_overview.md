# Valhalla System Overview

Valhalla is a local project-work environment for interdisciplinary research teams.
Built on local knowledge bases and delivered as a skill, it uses an LLM to help maintain and operate those knowledge bases. Research-group members can continuously contribute, share, maintain, and transform interdisciplinary knowledge to advance papers, experiments, code, reviews, plans, and engineering tasks.

## Core Ideas

Valhalla is founded on the following ideas:

1. **From managing materials to advancing projects**

   Valhalla does not treat a knowledge base as an ancillary project folder. It treats the knowledge base as the project's operating environment. Sources, knowledge items, relationships, graphs, and workflows together form the agent's workspace, allowing the agent to use accumulated knowledge to continue advancing paper writing, experiment design, code implementation, review synthesis, proposal development, and engineering maintenance.

2. **From isolated notes to structured knowledge**

   Valhalla does more than retain summaries or notes; it discovers and records semantic relationships among knowledge entities. Through the Entity and Relationship layers, knowledge gradually moves beyond natural-language text scattered across pages and becomes a structured knowledge network that can be inspected, extended, combined, and invoked.

3. **From a static knowledge base to persistent accumulation**

   Valhalla is not satisfied with retrieving temporary source fragments for each question. It emphasizes long-term knowledge accumulation. Conversations and experience gained while using an agent are also knowledge. They should not disappear at the end of a session, but should accumulate into reusable, long-term team assets.

4. **Accessible to researchers outside computer science**

   As a tool for interdisciplinary researchers, the system should allow people without a computer-science background to read and edit system rules, workflows, and service logic directly, enabling customization as needed.

5. **Constrainable**

   Structured constraints are needed at critical points such as permissions and state so that the LLM does not exercise excessive discretion during sensitive operations.

   Valhalla constrains the agent's operating scope through state, permissions, and risk levels, ensuring that each system service is invoked only under appropriate runtime conditions.

## Engineering Characteristics

Valhalla is built on local knowledge bases and delivered as a skill. It integrates source organization, knowledge extraction, system services, task workflows, and project-advancement capabilities into one extensible environment, allowing an agent not merely to access knowledge but to work continuously within a knowledge environment.

Valhalla has the following engineering characteristics:

1. **An agent-oriented working environment**

   Valhalla's goal is not simply to store materials or answer knowledge queries, but to provide an enduring project environment in which an agent can work. In this environment, the agent can read source material, understand knowledge-base structure, invoke system services, execute workflows, and use existing knowledge to keep advancing papers, code, experiments, reviews, plans, and engineering tasks.

   Valhalla is therefore not a passive information container, but working infrastructure that supports an agent's project activities.

2. **Separation of the knowledge-base system from the knowledge-base management system**

   Drawing on basic ideas from database systems, Valhalla divides the overall system into a “knowledge-base system” and a “knowledge-base management system.”

   The `knowledge-base system` stores and organizes project knowledge, including files, resources, entities, relationships, and knowledge graphs.

   The `knowledge-base management system` creates, registers, switches, ingests into, inspects, repairs, invokes, and maintains knowledge bases.

   This separation gives Valhalla both a stable data-organization foundation and extensible operational capabilities. The knowledge-base system provides a persistent project environment, while the knowledge-base management system allows the agent to perform concrete work within it.

3. **A knowledge-base system that exists independently of any model**

   Valhalla's knowledge-base system is constructed from `local directories`; its core data is stored as files, registries, templates, tables, and structured documents. The knowledge base itself therefore does not depend on any particular model.

   Even without an LLM, Valhalla's sources, resources, entities, relationships, and graphs can still be stored, inspected, migrated, and maintained. The LLM is Valhalla's intelligent runtime executor, not a prerequisite for the knowledge base's existence.

4. **A five-layer knowledge-base architecture**

   Valhalla abstracts the knowledge-base system into five layers: the `File layer`, `Resource layer`, `Entity layer`, `Relationship layer`, and `Knowledge Graph layer`.

   The File layer lets users freely organize original materials. Through `resource_id` and a public-copy mechanism, the Resource layer gives underlying files stable abstract identities. The Entity layer extracts and maintains knowledge-item objects from resources. The Relationship layer records entity-relationship facts—with subject, object, predicate, and evidence—in `.registry/machine/relationship_registry.yaml`. The Knowledge Graph layer generates derived graph views for different tasks and relationship types without inventing separate relationship facts.

   Each layer provides services to the layer above and encapsulates its own implementation. Upper layers consume lower-layer capabilities through inter-layer interfaces, while lower layers need not know how upper-layer services are implemented. This layered structure decouples low-level file organization, source identity management, knowledge-entity extraction, entity-relationship modeling, and graph-view construction, thereby improving system stability, maintainability, and extensibility.

   In Valhalla, an original source file is normally registered as a resource, referenced by a knowledge base, ingested as one or more entities, and then used to form relationships and graph views. This process transforms source material into operational knowledge.

   Valhalla emphasizes traceability. Knowledge entities and relationships should not exist independently of their source material; they should retain evidentiary provenance wherever possible so they can later be inspected, updated, and corrected.

5. **A knowledge-base management system inspired by hybrid-kernel architecture**

   Valhalla's knowledge-base management system is inspired by hybrid-kernel architecture and can be understood as a lightweight project operating system built on the skill mechanism.

   In this abstraction, the `LLM is treated as a powerful CPU`; the `context window as memory`; the `session as a process`; and the `session context as the process's memory space`.

   This structure organizes an agent's individual conversational actions into a constrained, schedulable, and reusable project-work process.

6. **Separation of the system kernel from system services**

   `Introduction to hybrid-kernel architecture`

   In operating-system design, the kernel maintains the fundamental capabilities required for system operation, such as process management, memory management, permission control, device access, and system calls. Different approaches to organizing these functions include monolithic kernels, microkernels, and hybrid kernels.

   A monolithic kernel places many system functions inside the kernel. This shortens system-call paths and can improve execution efficiency, but it can also produce a large kernel with tightly coupled modules.

   A microkernel minimizes the kernel, retaining only essential scheduling, communication, and permission mechanisms while moving file systems, drivers, networking, and other functions into user-space services. This creates clear module boundaries and improves maintainability, but inter-service communication and scheduling can cost more.

   A hybrid kernel can be understood as a compromise between the two. It neither places every function in the kernel nor moves every service completely outside it. Instead, it retains core mechanisms in the kernel and organizes extensible, replaceable, task-specific functions as system services according to stability, performance, permission, and maintenance requirements. This preserves operating order and critical control while preventing all system functionality from becoming concentrated in one enormous core.

   Valhalla borrows this idea to organize its knowledge-base management system. The system kernel maintains only the mechanisms necessary for operation, such as startup self-tests, state management, Router loading, permission checks, and operational constraints. Concrete capabilities—including resource registration, knowledge ingestion, relationship construction, graph generation, blacklist management, system inspection, and project advancement—are designed as decoupled system services. Valhalla thus has a stable operational core while allowing services to be extended or replaced as research needs evolve.

   Valhalla's knowledge-base management system consists primarily of a `system kernel` and `system services`.

   The `system kernel` maintains runtime state, performs startup self-tests, loads routing rules, checks permissions, validates state constraints, and preserves basic operating order.

   `System services` address concrete tasks and directly operate on different layers of the knowledge-base system—for example, root management, knowledge-base creation, source registration, knowledge ingestion, relationship construction, graph generation, blacklist management, system inspection, and project advancement.

   System services remain decoupled. Modifying one service should neither break other services nor affect the overall knowledge-base structure. This allows Valhalla to expand gradually through long-term use instead of requiring every capability to be designed up front.

7. **A system built primarily in natural language**

   Valhalla is built primarily in natural language. Its workflows, operational rules, service descriptions, knowledge-processing logic, and project-advancement processes are largely expressed in natural language, lowering the barrier to understanding and modifying the system.

   A small amount of structured language supplements this foundation for permission management, state constraints, interface contracts, and data validation—for example, Contracts and schemas. Python is used only in the few situations that require very high stability and determinism, such as startup self-tests and critical status checks.

   This design retains the readability and customizability of a natural-language system while adding structured constraints and engineering stability at critical points.

8. **A customizable design for interdisciplinary researchers**

   Valhalla was designed for interdisciplinary researchers, especially teams that must manage complex source material, build shared knowledge bases, and continuously advance papers, experiments, code, and project work.

   Natural-language construction, decoupled system services, and the five-layer knowledge-base architecture enable people outside computer science to understand Valhalla's operating logic and modify, extend, or customize the system for their own research settings.

   In other words, Valhalla aims to let research teams shape an agent's working environment, not merely use the agent.

9. **Delivered as a skill and directly involved in project advancement**

   Valhalla uses a skill as its primary runtime vehicle. The skill is neither merely system documentation nor simply a collection of prompts; it is the interface through which Valhalla enters the agent's working process.

   Through the skill, Valhalla injects knowledge-base structure, system services, permission constraints, workflows, and project rules into the agent's working context. The agent can then participate directly in project advancement using a local knowledge base. For example, it can ingest knowledge from existing materials, organize a review using entities and relationships, invoke project workflows to assist paper writing, draw on engineering entities to advance code implementation, or maintain knowledge-base structure through system services.

   Valhalla's functional boundary therefore extends beyond knowledge-base management. By organizing local knowledge bases, system services, and task workflows under a single skill system, it transforms a knowledge base from “a container that stores knowledge” into “the environment in which an agent advances a project.”

## Knowledge-Base System

The knowledge-base system is abstracted as a five-layer architecture.

1. **Layer 1: File Layer**

   The File layer consists of original files. Users may organize these source files freely according to project, person, topic, time, or any other useful scheme.

   To prevent uncontrolled disorder from automatic low-level file operations, Valhalla provides no system service that directly reorganizes original files at this layer. Users primarily maintain the File layer manually; the system only reads, recognizes, and registers its materials.

2. **Layer 2: Resource Layer / Abstract Source Layer**

   The Resource layer abstracts source files in the File layer into stable resource entries. A `resource_id` represents a unique content-version information object. No matter how a File-layer file is organized, moved, renamed, or reformatted, its `resource_id` remains the logical representative of that unique information in Valhalla.

   A `resource_id` is neither an original-file path nor a public-copy path. It is the stable identifier upper system layers use to reference source material.

   One `resource_id` may contain multiple representations, such as PDF, Markdown, TXT, OCR output, or extracted text. Each representation may in turn have multiple source copies in non-public Library directories. The Resource layer creates or binds a public copy for each representation. Upper structures reference only the `resource_id`; the Resource layer resolves it to a suitable readable representation, avoiding direct dependencies on file paths.

   `resource_registry.yaml` is the machine-authoritative Resource-layer registry; `resource_registry.md` is its synchronized human-readable projection. Routine registration may update Markdown incrementally. If names, paths, or states drift in bulk, lint corrects the Markdown projection solely from YAML. If the two conflict, YAML always takes precedence.

   The resource registry also stores a Resource-layer derived reverse index. `usage.referenced_by` records which entities in which registered knowledge bases reference the resource, and `reference_count` is computed from those back-references. Any operation that writes or updates `entity_resource_map.yaml` or `entity_registry.yaml`, changes the set of registered active knowledge bases or their paths, or changes a target root's aggregate state must update usage in `resource_registry.yaml` and `resource_registry.md` within the same operation. `sync_resource_usage` is reserved for legacy cleanup, batch correction, and manual maintenance. This reverse index is not an Entity master record and must not be used to generate `entity_id` values.

   This layer prevents identity drift as files are used, added, or removed. Different filenames, paths, and formats can express the same information; a preprint, final publication, revision, or file with material content additions or deletions must receive a different `resource_id`. Through `resource_id`, representation files, and public copies, the Resource layer decouples upper knowledge structures from lower file organization.

3. **Layer 3: Entity Layer / Knowledge-Item Layer**

   After a knowledge base defines its resource scope through a virtual resource collection, the LLM extracts knowledge entities from material within that scope.

   A virtual resource collection is not a new physical collection of files; it is a logical collection of `resource_id` values that determines which resources a knowledge base may use.

   Each knowledge base's `local_resources`, `required_resources`, and `excluded_resources` use paired files: YAML stores machine-authoritative membership, while Markdown stores a human-readable projection. YAML also preserves the user's admission input and membership state; Markdown displays the admission input and the Resource layer's current source path. Only YAML entries with `membership_status: active` participate in computing the virtual resource collection. Entries marked `pending_removal` become ineffective immediately and are removed in a confirmed lint batch.

   Material represented by one `resource_id` may yield multiple entities; a single entity may also derive from multiple `resource_id` values. Every entity has a unique `entity_id`.

   An `entity_id` is local to its knowledge base. The identifier for a new entity may be calculated only from the current knowledge base's `.registry/machine/entity_registry.yaml` and `entities/ent_*.md`; it must not be inferred from another knowledge base or from historical usage in `resource_registry.yaml`.

   In Valhalla, an Entity is not merely a keyword or label, but a curated knowledge-item object. It normally has an extensible content file that records the item's definition, explanation, provenance, evidence, and later additions.

4. **Layer 4: Relationship Layer**

   The Relationship layer represents relationships among entities within a knowledge base. Relationships may be typed to express different semantic connections, such as support, contradiction, inclusion, dependency, causation, comparison, equivalence, and extension.

   The purpose of this layer is not merely to connect entities, but to record an interpretable structure among knowledge items so that the system can further organize, inspect, and reason over knowledge.

5. **Layer 5: Knowledge Graph Layer**

   The Knowledge Graph layer constructs knowledge graphs from the Entity and Relationship layers. It can generate graph structures for different tasks, topics, or relationship types.

   It therefore does not store one fixed, canonical graph. Instead, it provides graph views for different scenarios. A support-based evidence graph, contradiction-based controversy graph, causation-based mechanism graph, or project-specific task graph can each be generated from the same underlying knowledge.

   For example, advancing a task might use a knowledge graph composed of “support + inclusion + dependency + causation + equivalence.”
   Reviewing a task result might instead use a graph composed of “contradiction + comparison.”

## Knowledge-Base Management System

Valhalla's knowledge-base management system is inspired by hybrid-kernel operating-system architecture and organizes an agent's operations on the knowledge-base system. It is not a conventional low-level operating system, but a lightweight runtime environment built on the skill mechanism. It maintains Valhalla's basic operating order and schedules system services.

In this architecture, `SKILL.md` is treated as Valhalla's `system kernel`. It is loaded whenever Valhalla starts, so it carries the fundamental responsibilities required for system operation. The current kernel implements three main capabilities: startup self-testing, safety constraints, and instruction routing. Startup self-testing verifies Valhalla's basic structure and operating conditions; safety constraints restrict high-risk operations; and the instruction `router` dispatches user input to the relevant system-service entry point.

`System services` use a unified execution process:

```text
router → contract → workflow
```

The `router` classifies the user's prompt, determines the operation type, and loads the corresponding `contract`.

A `contract` is the system service's eligibility-validation module. It checks current system state, permission constraints, risk level, and prerequisites to determine whether the operation may proceed. The system loads the corresponding `workflow` only after the Contract passes.

The `workflow` defines the system service's concrete procedure. It describes what the agent should do after validation: which files to read, which structures to modify, which results to produce, and how to report execution to the user.

A Valhalla system service is therefore not executed directly from a prompt. It follows an explicit controlled path:

```text
Classification → Validation → Execution
```

This design preserves the flexibility of natural-language workflows while adding state checks, permission constraints, and risk controls before critical operations, reducing the risk that unconstrained agent behavior will disorder system structure.

## Current Limitations and Future Improvements

### Current Limitations

Although Valhalla aims to be an agent working environment for interdisciplinary research teams, the current version remains an early prototype with several limitations.

1. **No remote collaboration yet**

   Valhalla currently operates primarily on a local file system and does not yet support remote access, real-time multi-user collaboration, or distributed synchronization. In team settings, it is presently best deployed on a dedicated computer that research-group members use in turn, or maintained centrally through a shared workstation.

   Concurrent writes and conflict resolution are not yet implemented, so the current version is better suited to one user or turn-taking than to multiple members or agents modifying the same knowledge base simultaneously.

2. **No permission-protection mechanism for knowledge-base directories**

   Valhalla's core data—including source files, resource registries, entity files, relationship tables, and graph files—is stored in local knowledge-base directories. The system does not yet provide fine-grained protection for those directories, such as per-member access, write, and delete permissions or operational auditing.

   In multi-user settings, Valhalla therefore still relies on the operating system, version-control tools, or human procedures to prevent accidental deletion, unintended changes, and unauthorized operations.

3. **No backup and rollback mechanism yet**

   Valhalla does not yet implement complete automatic backups, version snapshots, or rollback. System services directly modify local knowledge-base files such as registries, entity files, relationship tables, graph files, and logs. If an erroneous operation, ingestion, repair, or structural change occurs, the system cannot yet automatically restore the preceding state.

   This is especially important in an agent working environment because an agent may execute several operations in sequence. One error can propagate across multiple files and produce cascading structural problems. Future versions should add pre-operation snapshots, incremental backups, modification logs, diff inspection, and rollback recovery so that high-risk operations become reversible.

4. **No context-scheduling mechanism yet**

   Valhalla does not yet implement complete context scheduling. Once some files or Workflow content enter a prompt during operation, they are difficult to evict actively from the context window. Context usage can therefore grow continuously during long tasks, reducing the stability and scalability of later operations.

   Future versions need explicit mechanisms for loading, staging, compressing, and evicting context to improve sustained operation on complex tasks.

### Future Improvements

Despite these limitations, the current Valhalla version is fundamentally usable.

It already implements the core mechanisms of local knowledge-base organization, a five-layer knowledge architecture, a system kernel, system services, routing, Contract validation, and Workflow execution. It supports fundamental tasks such as resource registration, knowledge ingestion, Entity maintenance, Relationship construction, graph organization, and project advancement.

Valhalla's layered and decoupled design provides a strong foundation for continued evolution. New system capabilities can be added incrementally without disrupting the existing knowledge-base structure.

1. Add a remote-synchronization module so team members can collaborate through Valhalla from different devices.

2. Add a permission-management module to apply finer-grained access control to knowledge-base directories, system services, and high-risk operations.

3. Add backup and rollback modules that automatically create snapshots before writes and record file diffs, making erroneous operations traceable and reversible.

4. Add a context-scheduling module to manage runtime prompt content through loading, staging, compression, and eviction.

Valhalla's current shortcomings are therefore primarily engineering gaps at this stage of implementation rather than fundamental architectural limitations. As remote collaboration, permission management, backup and rollback, version control, and context scheduling are added, Valhalla can evolve from a locally usable single-machine project environment into an agent working platform that supports team collaboration.
