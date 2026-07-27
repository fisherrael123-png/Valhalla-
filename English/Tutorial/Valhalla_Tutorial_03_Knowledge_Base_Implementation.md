# Valhalla Tutorial 03

> Intended audience: Users who have completed Valhalla Tutorials 01 and 02 and understand the five-layer architecture of Valhalla's knowledge-base system  
>
> Learning objective: Understand the architecture of a knowledge base  
>
> Estimated time: 30–40 minutes

## The Relationship Between a Knowledge Base and a Knowledge-Base System

Be careful to distinguish these two concepts:

- A knowledge base is a collection of knowledge in a specific field.
- A knowledge-base system is a collection of knowledge bases. This arrangement allows knowledge bases to share Resource files within the system, avoiding the waste and management burden of maintaining a separate copy of every Resource file for each knowledge base.

## Knowledge-Base Architecture

Recall the five-layer architecture of the knowledge-base system:

| Five-Layer Architecture |
| --- |
| Graph Layer |
| Relationship Layer |
| Entity / Knowledge-Item Layer |
| Resource Layer |
| File Layer |

Each layer provides services to the layer above it and encapsulates its own implementation.

Upper layers use lower-layer capabilities through interlayer interfaces, while lower layers do not need to know how upper-layer services are implemented.

A knowledge base also follows this five-layer structure. However, all knowledge bases within one knowledge-base system share the Resource Layer and File Layer, while each builds its own Entity, Relationship, and Graph Layers.

## Knowledge-Base File Structure

`A useful way to learn Valhalla's standard commands quickly is to inspect .codex/skills/valhalla/router/router.md under the Codex installation directory.`

### Select a Root

One root represents one knowledge-base system and is implemented as a folder.

After Valhalla starts, enter `status` to inspect the current state, including the root currently in use.

You may also enter `root list`, `all roots`, or `list all roots` to inspect the roots registered with the system.

When using Valhalla for the first time, enter `create root <root-path> <root-alias>` to create a root.

To activate a target root, enter `switch root <root-path-or-root-alias>`.

After activating the target root, it is strongly recommended that you enter `status` again to verify the state.

### Root File Structure

After selecting a root, enter `create knowledge base <knowledge-base-name>` to create a knowledge base.

Open the root folder. You will see the following structure:

```text
    .valhalla/
        kb_status.md
    resource_registry.yaml
    resource_registry.md
    wiki_registry.yaml
    wiki_registry.md
    orphan_resources.md
    blacklist_registry.yaml
    Library/
        public_resources/
    Wiki/
```

`Library/` is the File Layer of the knowledge-base system. All original source files must be placed here. The `public_resources/` subfolder contains source backups managed by the system; users must not modify this folder.

`resource_registry.yaml` is the primary component of the Resource Layer. It registers material in `Library/` under unique `resource_id` values for use by upper layers. There may be multiple copies of a source file in the Library, so they require a unified identifier to prevent confusion when called by upper layers.

`resource_registry.md` is the human-readable projection of `resource_registry.yaml`. The same convention is used throughout the system: when files share the same base name, YAML is machine-readable authority and Markdown is the human-readable projection.

`blacklist_registry.yaml` is another component of the Resource Layer. It is the global Resource blacklist for the current root.

The `Wiki/` folder stores knowledge bases. The upper three layers of the knowledge-base system—Entity, Relationship, and Knowledge Graph—are constructed here.

`Wiki/` contains subfolders named `Wiki_<knowledge-base-name>`. Each subfolder is a knowledge base within this knowledge-base system.

### Knowledge-Base File Structure

Open `Wiki_<knowledge-base-name>`. You will see:

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

The `.registry/` directory stores registries for the corresponding layers so that they can be inspected.

#### Resource Layer

Each knowledge base uses a virtual Resource-layer mechanism.

`.virtualDatabase/` is the knowledge base's virtual Resource layer.

A knowledge base is built on the root's Resource Layer, but it usually does not need every Resource in the root. Three Resource tables define which root-level Resources the knowledge base uses:

- `local_resources.yaml`: The local Resource table. It records the knowledge base's general Resource scope. These Resources may or may not be used during project work.
- `required_resources.yaml`: The required Resource table. It records Resources that must be consulted during project work.
- `excluded_resources.yaml`: The excluded Resource table. It records Resources that must be excluded during project work.

The virtual Resource collection is:

```text
virtualDatabase = local_resources ∪ required_resources - excluded_resources - blacklist
```

You may modify these three Resource tables manually through instructions.

#### Entity Layer

The Entity Layer has three parts: `entities/`, `conversation_entities/`, and `engineering_entities/`. All three store knowledge items.

`entities/` is the primary storage location for Entities. These Entities come from Resources in the Resource Layer and represent knowledge items extracted by the `ingest` instruction.

`conversation_entities/` stores supporting Entities derived from conversations between the user and Valhalla. They do not have Resource-layer support.

After a user starts a knowledge base and queries or discusses it with Valhalla, the conversation itself contains knowledge. That knowledge should not be discarded; it should be stored in `conversation_entities/`.

Like `conversation_entities/`, `engineering_entities/` stores engineering experience as knowledge items without Resource-layer support.

#### Relationship Layer

`relationships/` stores Relationships among Entities, such as `supports`, `equivalent to`, and `contradicts`. You can customize the Relationship types that Valhalla should search for across knowledge items. The relevant method is introduced in a later development tutorial.

Do not be intimidated by the phrase “development tutorial.” Thanks to the layered encapsulation of the knowledge-base system and the microkernel-oriented architecture of the knowledge-base operating system, Valhalla's development process is remarkably simple.

In most cases, you do not even need to write files yourself when developing Valhalla. If writing is necessary, Valhalla's natural-language construction makes the process accessible without a technical barrier.

#### Graph Layer

`knowledge_graph/` stores knowledge-topology Graphs whose nodes represent knowledge items and whose edges represent Relationships.

This layer extends the Relationship Layer and can store Graphs built from particular Relationships. For example, a Graph composed entirely of contradictions can be used to validate a plan.

## A Third Look at the `Ingest` Operation

Now that you understand the layered implementation of a knowledge base, we can revisit the details of `ingest`:

**File-layer operation:** The input is a filename or file path. Valhalla first confirms that the file exists in the current root's Library. If it does not exist, the operation returns an error.

**Resource-layer operation:** If the file exists, Valhalla verifies that it is registered in the Resource Layer and has a unique `resource_id`. If it is not registered, Valhalla registers it and assigns a `resource_id`.

After the file obtains a `resource_id`, Valhalla checks whether that Resource is in the current knowledge base's virtual Resource collection. If not, it adds the `resource_id` to that collection.

**Entity-layer operation:** Once the source enters the current knowledge base's Resource Layer, Valhalla uses the Resource to construct Knowledge Entities by extracting its knowledge items in the Entity Layer.

As a general rule, a Valhalla operation—also called a system service under microkernel conventions—operates independently on only one layer of the knowledge-base system. This decouples the layers and prevents a change from propagating into unrelated parts of the system.

For convenience, however, Valhalla integrates several operations into `ingest`. Otherwise, every source would require the user to perform `Resource registration`, `admission to the virtual Resource collection`, and `knowledge ingestion` manually, and most users would probably give up.

This is why `ingest` is described as a relatively complex operation. It is not the most complex operation, however. The most complex currently is `fuse roots`, which can combine different knowledge-base systems to support knowledge sharing and collaboration among multiple people.

The separate step-by-step operations also exist. If you want to try them, consult the Router and execute the steps yourself. This is useful for understanding the layered encapsulation of Valhalla's knowledge-base system.

### Summary

This chapter has revealed the implementation behind knowledge-base creation. It showed how the abstract `five-layer architecture` of the `knowledge-base system` described in the previous chapter is realized through the Library, `resource_registry`, and Wiki.
