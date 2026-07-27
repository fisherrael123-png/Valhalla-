# Valhalla Tutorial 04

> Intended audience: Users who have completed Valhalla Tutorials 01, 02, and 03 and understand both the five-layer architecture of Valhalla's knowledge-base system and its implementation  
>
> Learning objective: Understand the architecture of the knowledge-base operating system  
>
> Estimated time: 30–40 minutes

## The Relationship Between the Knowledge-Base System and the Knowledge-Base Operating System

Valhalla's knowledge-base system and knowledge-base operating system draw on the concepts of database systems and database management systems.

One point must be emphasized: `Valhalla is not merely a knowledge base. A knowledge base is only one part of Valhalla, which is an integrated AI workspace.`

Be careful to distinguish these two concepts:

- The knowledge-base system is the file system that organizes knowledge bases.
- The knowledge-base operating system is the operating system that uses the knowledge-base system.

As an analogy, the knowledge-base system is the hard drive in your personal computer, and its knowledge bases are the drive's partitions, such as C:, D:, and E:. The knowledge-base operating system is Windows or Linux.

An ordinary `personal knowledge base` resembles a database system that only manages stored files. Valhalla resembles an operating system that uses those files to perform work and other activities.

## Introduction to Operating-System Kernel Architectures

In operating-system design, the kernel maintains fundamental capabilities required for system operation, such as process management, memory management, access control, device access, and system calls. Depending on how system functionality is organized around the kernel, architectures are commonly described as `monolithic kernels`, `microkernels`, or `hybrid kernels`.

A `monolithic kernel` tends to place substantial system functionality inside the kernel. This shortens system-call paths and can improve execution efficiency, but it can also produce a large kernel and tight coupling among modules.

A `microkernel` minimizes the kernel and retains only essential scheduling, communication, and permission mechanisms. File systems, drivers, networking, and other functions run as user-space services. This architecture has clear module boundaries and is easier to maintain, although communication and scheduling among services may introduce additional overhead.

A `hybrid kernel` can be understood as a compromise between the two. It neither attempts to place every function in the kernel nor moves every service entirely outside it. Instead, core mechanisms remain in the kernel according to stability, performance, access-control, and maintenance requirements, while extensible, replaceable, task-specific functionality is organized as system services. This preserves operating order and critical control capabilities without concentrating all functionality in one enormous core.

## Architecture of Valhalla's Knowledge-Base Operating System

Valhalla's knowledge-base operating system primarily follows a microkernel model.

### Runtime Loading Model

A characteristic of a microkernel operating system is that the `operating-system kernel` remains resident in memory while other components do not. When a function is required, the kernel loads the relevant program code into memory. Code loaded temporarily to perform a particular function is generally called a `system service`.

Windows operating systems released in the twenty-first century use this kind of microkernel-oriented architecture. If you open Windows Task Manager and sort processes by name, processes categorized as `Windows processes` are `system services`.

When the Valhalla skill is invoked, the contents of `SKILL.md` are loaded into context. Other parts of the skill are loaded and executed only when the functions for which they are responsible are invoked.

A skill's `progressive disclosure` closely resembles the `on-demand loading` of system services in a microkernel architecture. `SKILL.md` remains resident like an `operating-system kernel`, while other skill components are `loaded on demand`, just as microkernel system services are.

The difference is that an operating-system service can be removed from memory immediately after completing its task, freeing memory for other programs. A skill component loaded on demand remains in the context until the session restarts or the context is compacted.

This suggests a `new perspective on LLMs`: treat the LLM as a powerful CPU and the context window as memory, together forming useful virtual computer hardware. Valhalla is the operating system running on that virtual hardware.

### Valhalla's Knowledge-Base Operating System

#### Operating-System Kernel

The operating-system kernel is implemented by the skill's `SKILL.md` file. Its primary functions include startup self-checks, Router loading, safety constraints, and prompt routing.

`SKILL.md` is constructed almost entirely in natural language. The exception is the bootstrap startup program. Because bootstrap has the narrow, stability-sensitive responsibility of validating system integrity and loading the Router, it is written in Python.

#### System Services

Outside the kernel, Valhalla implements specific functions through mutually independent system services.

The standard execution path of one system service is:

```text
prompt input → router → contract → workflow
```

| Issue an instruction | Select the system service | Verify that the current environment permits execution | Execute the system service |
| --- | --- | --- | --- |
| prompt input | router | contract | workflow |

#### Inspecting System Services Through the Router

The best way to understand system services is to inspect the Router.

As noted earlier, Valhalla is primarily constructed in natural language, and the Router is no exception. You can find `router.md` in the `router` subfolder of the Valhalla skill.

The following example is the `Knowledge-Base Lifecycle` section of the Router from `Valhalla 0.5.10b`.

The purpose of these system services is: `List, create, register, start, exit, unregister, and rename knowledge bases under the current root. These operations manage knowledge bases themselves; they do not perform semantic processing of source material.`

`Category`: The type of system service.

`Trigger conditions`: The prompts that can invoke the system service.

`Load`: The entry point of the system service. Loading it begins the subsequent process.

| Category | Trigger conditions | Load |
| --- | --- | --- |
| `list_root` | list knowledge bases under the current root; which knowledge bases are in the current root; knowledge-base list | `contract\kb_operation\list_root_contract.yaml` |
| `create_kb` | create a knowledge base | `contract\kb_operation\create_kb_contract.yaml` |
| `register_existing_kb` | register an existing knowledge base; register an existing Wiki as a knowledge base; register an existing KB | `contract\kb_operation\register_existing_kb_contract.yaml` |
| `start_kb` | start or switch the knowledge base | `contract\kb_operation\start_kb_contract.yaml` |
| `exit_kb` | exit the current knowledge base | `contract\kb_operation\exit_kb_contract.yaml` |
| `remove_kb` | delete, remove, or unregister a knowledge base; remove a knowledge base from the current root | `contract\kb_operation\remove_kb_contract.yaml` |
| `rename_kb` | change or rename a knowledge base; rename knowledge base `<old-name>` to `<new-name>` | `contract\kb_operation\rename_kb_contract.yaml` |

#### From Contract to Workflow

A `Contract` contains a series of qualification checks. Using `create_kb_contract.yaml` as an example, the most important checks include:

1. Input validation:

```text
    input:
        required:
        - kb_name
        optional: []
        pattern:
            canonical: create kb <kb_name>
            examples:
            - create knowledge base test-kb
            - create a knowledge base named test-kb
            - create kb test-kb
```

This determines the parameters in the input instruction. Here, the parameter is `<kb_name>`.

2. Read and write permissions:

```text
   permissions:
      read: true
      write: true
```

3. Risk level:

```text
risk:
      level: high
      confirmation_required: true
```

The available risk levels are `low`, `medium`, and `high`.

When the level is `high`, the safety rules in `SKILL.md`—the kernel—require confirmation.

When the risk level is `low`, `confirmation_required` can still impose a local confirmation requirement.

If you find repeated confirmations for `ingest` inconvenient, you can change the risk configuration for `ingest` and `register_resource` to:

```text
risk:
      level: low
      confirmation_required: false
```

This removes the repeated confirmation requirement.

4. State requirements:

```text
    state_constraints:
      os_status:
        allowed:
        - base
        on_denied: Refuse create_kb: this operation can run only in base state.
      kb_status:
        allowed:
        - idle
        on_denied: Refuse create_kb: this operation can run only in idle state.
```

Valhalla checks whether the current state satisfies these requirements.

`os_status` has two states: `base` and `admin`. Enter `enter admin` or `enter administrative state` to change `os_status` to `admin`; enter `exit admin` or `exit administrative state` to return to `base`.

Some highly consequential instructions require additional caution and are therefore available only in admin state.

In `codex --yolo` mode, the system may sometimes bypass the explicit `os_status` switch and automatically perform the `enter administrative state` operation. It still requires your explicit confirmation before execution. This reflects a characteristic of an AIOS: its behavior is not always completely stable.

`kb_status` also has two forms: `idle` and `kb:<kb_name>`. `idle` means that no knowledge base is active. `kb:<kb_name>` means that the named knowledge base is active.

Enter `start knowledge base <kb_name>`—for example, `start knowledge base test-kb`—to start a knowledge base named `test-kb`.

The purpose of `kb_status` is to set the active knowledge base as the target for knowledge-base operations.

5. Workflow entry point:

```text
executor:
      type: workflow
      paths:
      - workflows/kb/create_kb.md
      load_after_validation: true
```

After the preceding qualification checks pass, Valhalla loads `workflows/kb/create_kb.md` and executes the system service.
