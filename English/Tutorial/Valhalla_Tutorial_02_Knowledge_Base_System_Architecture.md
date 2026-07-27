# Valhalla Tutorial 02

> Intended audience: Users who have completed Valhalla Tutorial 01 and have a general understanding of Valhalla  
>
> Learning objective: Understand the structure of the knowledge-base system and the boundaries of selected operations, laying a foundation for later Valhalla customization  
>
> Estimated time: 30–40 minutes

## Knowledge-Base System Architecture

### Architecture Overview

Although the entire knowledge-base system is implemented within a single root folder, Valhalla organizes it into a five-layer architecture based on the characteristics of knowledge:

| Five-Layer Architecture |
| --- |
| Graph Layer |
| Relationship Layer |
| Entity / Knowledge-Item Layer |
| Resource Layer |
| File Layer |

Each layer provides services to the layer above it and encapsulates its own implementation.

Upper layers use lower-layer capabilities through interlayer interfaces, while lower layers do not need to know how upper-layer services are implemented.

Through this layered structure, Valhalla decouples low-level file organization, Resource identity management, knowledge Entity extraction, Entity Relationship modeling, and Graph-view construction. This improves system stability, maintainability, and extensibility.

### Functions of Each Layer

1. **File Layer:** This layer is implemented by the `Library` folder under the root and stores original source material.

   Because this is the foundation of the knowledge-base system's five-layer architecture, Valhalla does not provide operations that modify this layer.

   Later tutorials will show that it is very easy to create operations that users need in Valhalla—I call them `system services`. Nevertheless, I strongly advise against creating modification operations for the File Layer.

   The `public_resources` subfolder inside `Library` stores copies of original source material created by Resource-layer operations. Users must not modify this folder. Its purpose is explained later.

   Apart from `public_resources`, users may organize folders within `Library` however they prefer.

   For example, material from different fields can be stored in different folders. If multiple people use the same Valhalla system, each person may create a personal folder within the Library and organize their own source-material collection there.

   The current version is still a test prototype, so collaborators need to take turns when using it. A Valhalla system designed specifically for teamwork is expected to be released later.

2. **Resource Layer:** This layer organizes the original source material in the File Layer.

   File-layer material may include duplicate files at different paths, different formats, or different names for the same file. These inconsistencies are unfriendly to upper-layer operations.

   The Resource Layer therefore organizes original files into `Resources` for use by upper layers.

   For example:

   The same paper, `a`, may exist as both PDF and Word versions, and the versions may have different names. Consequently, `aaa.pdf` and `ddef.doc` may actually represent the same paper.

   Calling original files directly would create uncontrolled confusion. The Resource Layer instead organizes `aaa.pdf` and `ddef.doc` into one `Resource`, represented by a unique `resource_id`.

   You can inspect this information in `resource_registry.md` under the root folder.

3. **Entity / Knowledge-Item Layer:** This layer stores `knowledge items` extracted from `Resources` in the Resource Layer.

   Original source files alone cannot help you; knowledge can. Buying many books and placing them on a shelf does not increase your knowledge. You have to read them and understand the ideas they contain.

   I refer to a knowledge item as an `Entity`, `Knowledge Entity`, or `entity`.

   One important fact is that **one source file may contain multiple Entities, while the same Entity may be supported by multiple sources.**

   This creates a network between `Entities` and `Resources`. Without an Entity Layer, allowing higher layers to call Resources directly would create serious confusion.

   The Entity Layer assigns each knowledge item a unique `entity_id` for use by upper layers and registers it in `entity_registry`.

   `entity_registry` primarily records a short description of the Entity, the `Resources` from which it was derived, and a `content_file` link.

   The `content_file` contains a more detailed description of the Entity, avoiding the need to reread every `Resource` repeatedly.

   You can inspect the Entity Layer through `entity_registry.md`. This file is located in the `.registry/human/` folder of a knowledge-base directory (`Wiki_<knowledge-base-name>`) under the root's `Wiki` folder.

   This shows that the Entity Layer is already partitioned by knowledge-base scope. This mechanism is explained in detail later; for now, a general understanding is sufficient.

   The main reason for this partitioning is the previously described network between `Entities` and `Resources`. Network complexity grows rapidly. Extracting Entities uniformly across the entire Resource Layer would require an enormous amount of work. Each knowledge base therefore uses a mechanism called the `virtual resource collection` to define a smaller Resource set and builds its Entity–Resource network only within that dedicated subset.

4. **Relationship Layer:** This layer stores Relationships among `Entities`.

   A `Relationship` between Entities is also knowledge and should be stored for later reuse.

   To inspect all Relationships among Entities in a knowledge base, open `relationship_registry.md` in the `.registry/human/` folder of its `Wiki_<knowledge-base-name>` directory under the root's `Wiki` folder.

5. **Graph Layer:** This layer stores Graphs built from different `Relationships`.

   Graph structures can associate knowledge quickly, avoiding the cost and loss of AI attention caused by broad searches.

   Edges representing Relationships are sufficient to construct a Graph, but different Relationship scopes can produce different Graphs.

   These Graphs serve different purposes. For reasoning tasks, Graphs built from positive Relationships such as support and derivation are especially important. For review tasks, Graphs built from opposing Relationships such as contradiction are more useful.

   To inspect all constructed Graphs in a knowledge base, open `knowledge_graph_registry.md` in the `.registry/human/` folder of its `Wiki_<knowledge-base-name>` directory under the root's `Wiki` folder.

### Summary

| Five-Layer Architecture |
| --- |
| Graph Layer |
| Relationship Layer |
| Entity / Knowledge-Item Layer |
| Resource Layer |
| File Layer |

Viewed from the top down:

At the top is the Knowledge Graph in the `Graph Layer`. Its vertices are Knowledge Entities, and its edges are Relationships between the Knowledge Entities represented by the vertices at either end. A Knowledge Graph is drawn from edges selected according to particular Relationship properties.

The next layer is the `Relationship Layer`. Relationships represent connections among Knowledge Entities and determine the Graphs above them. A `Graph` can be used to locate a `Relationship`.

Below that is the `Entity Layer`. A `Relationship` can be used to locate an `Entity`. Although the theoretical lookup chain is “Graph → Relationship → Entity,” Graph construction directly links the corresponding Entities to Graph nodes to improve lookup speed.

The penultimate `Resource Layer` lets the system locate corresponding `Resources` from an `Entity`.

At the bottom, the `File Layer` lets the system locate corresponding `Files` from a `Resource`.

Starting from a top-level Graph, the system can therefore trace information layer by layer down to the underlying files. Encapsulation and decoupling between layers allow Valhalla to load only the source material needed for a task and make the system easier to extend because the impact of a modification remains confined to its own layer.

## Revisiting the Ingest Operation

Tutorial 01 introduced the Ingest operation without explaining what happens behind the scenes. We can now describe its mechanism in terms of the knowledge-base system's architecture.

The general command is `ingest <file-path>`, and its output is an `Entity`.

The input to `ingest` is therefore in the `File Layer`, while its output is in the `Entity Layer`.

In other words, **the Ingest operation spans three layers of the knowledge-base system**. It is one of the few cross-layer operations in Valhalla.

Importantly, `ingest` cannot jump directly from the `File Layer` to the `Entity Layer`; it must pass through a Resource-layer operation.

The approximate ingestion process is:

1. Use `<file-path>` to determine whether the file has already been registered in the Resource Layer. If it has not, register it, assign a unique `resource_id`, and create a backup under the Library's `public_resources`.
2. After obtaining the file's `resource_id`, move the operation into the `Resource Layer`. Valhalla checks whether the Resource belongs to the target knowledge base's `virtual resource collection`. The target is the currently active knowledge base, which can be inspected with `current status`. The virtual resource collection is a subset of all Resources in the root and is used specifically to construct the target knowledge base's Resource Layer. If the Resource is absent, add it to the target knowledge base's virtual resource collection.
3. Once the Resource is confirmed to be in the target knowledge base's virtual resource collection, that knowledge base's `Resource Layer` is ready. The LLM then interprets the Resource, extracts Knowledge Entities, and registers and stores them in the `Entity Layer`.
