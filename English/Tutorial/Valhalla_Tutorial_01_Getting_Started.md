# Valhalla Tutorial 01

> Intended audience: First-time Valhalla users  
>
> Learning objective: Complete the full workflow—from creating a knowledge base to using knowledge to advance a project—through natural-language instructions  
>
> Estimated time: 30–40 minutes

## 1. Understanding Valhalla

Valhalla is a local research knowledge base and project workspace operated by Codex.

Valhalla draws on the overall architecture of database systems and is divided into a knowledge-base system and a knowledge-base operating system.

The knowledge-base system stores knowledge, while the knowledge-base operating system manages and uses the knowledge stored in that system.

Valhalla does more than store files. Agents such as Codex can use the knowledge in the knowledge-base system to answer questions, compare approaches, design experiments, assist with paper writing, and advance coding tasks.

## 2. What Beginners Do Not Need to Learn

When you first start using Valhalla, you do not need to:

- Understand Valhalla's system architecture.
- Understand internal mechanisms such as the Router, Contract, and Workflow.
- Manually modify system files to satisfy customization requirements.
- Learn Python commands.

You only need to describe your goal in a Codex conversation.

In practice, explicitly invoking the skill with `$valhalla` once is generally enough to keep using the system throughout the session. You may nevertheless begin each request with `$valhalla` to make it clear that you want to use Valhalla.

For example:

```text
$valhalla current status
```

## 3. Three Terms to Know Before You Begin

### 3.1 Root

A Root is the top-level folder of a complete Valhalla workspace. It contains source material, knowledge bases, and system records.

One Root folder is one complete `knowledge-base system`.

A computer may register multiple roots, but only one is used at a time.

### 3.2 Knowledge Base

A `knowledge base` is a core concept in the knowledge-base system.

Source material in one knowledge-base system may support multiple projects or research directions. The knowledge extracted from that material therefore needs to be organized. Each knowledge base provides knowledge support for a corresponding project.

### 3.3 State

Valhalla has two sets of states that are easy to confuse.

**System state:**

- `base`: Normal state for routine queries and project work.
- `admin`: Administrative state for root management, inspection, blacklist maintenance, and similar tasks.

This state mechanism prevents highly consequential commands from being triggered casually.

**Session state:**

- `idle`: No knowledge base is currently active.
- `kb:<name>`: A knowledge base is active.

Building, managing, or using a knowledge base requires a target. The session state selects that target knowledge base.

The most common state for everyday use is `base + kb:<name>`.

## 4. Installing Valhalla

Although the provided Valhalla package is already a complete skill, Valhalla is not an ordinary skill. It is closer to an AI operating system delivered through a skill. Because it is large, simply placing it in Codex's skill directory is not recommended and may not automatically install it as a Codex skill.

The standard method is to use Codex's `Skill Creator`.

Enter:

```text
$skill-creator Install <path-to-the-Valhalla-package> as a skill
```

This completes the installation.

## 5. First Use: Build a Minimal Knowledge-Base System

Send the following commands one at a time. Do not send them all at once.

### Step 1: Start Valhalla and Initialize the System

Enter:

```text
$valhalla
```

This starts Valhalla. If this is the first start in the current session, Valhalla runs a self-check to verify system integrity.

### Step 2: Inspect the Current State

```text
current status
```

Pay attention to three items in the response:

1. Whether a current root exists.
2. Whether the system state is `base`.
3. Whether a knowledge base is active.

If the system reports that no root exists, do not edit files yourself. Say:

```text
Please explain what is currently missing and what I should do next. Do not modify any files yet.
```

### Step 3: Create a Root

Original source material is extremely valuable and forms the foundation of every knowledge base. Because Valhalla is an AIOS and may sometimes behave unpredictably, it does not provide operations that modify original source material. This protects source files from uncontrolled changes.

Create a root as follows:

1. Create and name a folder in the desired location. This folder will be the Valhalla root.
2. Enter Valhalla's administrative state by entering `enter admin` or `enter administrative state`. Root operations are highly consequential, so they require admin state to prevent accidental activation.
3. Create the root by entering `create root, <root-folder-path>`. You may also assign an alias: `create root, <root-folder-path>, <root-alias>`.
4. Inspect the current state again. If the current root is not the intended root, enter `list all roots` to see every root registered on the computer, then enter `switch root, <target-root-alias>` to switch to and activate the target root.

### Step 4: Create a Knowledge Base

Once the root has been selected, the knowledge-base system on which you are operating has also been selected. The next step is to create a knowledge base within it.

Enter:

```text
create knowledge base <knowledge-base-name>
```

You can also try several related operations.

Inspect the current knowledge base:

```text
$valhalla current knowledge base
```

If you do not know which knowledge bases are available, ask the system to list them:

```text
$valhalla Please list the existing knowledge bases.
```

After these first four steps, you have created a knowledge-base system and an empty knowledge base within it.

### Step 5: Start a Knowledge Base

You can now begin managing the empty knowledge base. First, start the target knowledge base:

```text
$valhalla start knowledge base <knowledge-base-name>
```

After it starts successfully, the session state should become something like:

```text
kb:drug-design
```

Enter `current status` or `knowledge-base status` to verify it.

“Starting a knowledge base” does not mean opening a folder. It tells the system that subsequent operations should target this knowledge base by default.

### Step 6: Ingest Source Material

`Ingest` is one of Valhalla's core instructions and is relatively complex. This tutorial does not yet explain its internal execution logic; it only explains what the operation does.

Using a set of source files directly to advance a project or research effort would amount to a rather unnatural “files advance the project” workflow. The normal workflow is for `knowledge to advance the project`.

Knowledge must first be extracted from files and then used to advance the project.

`Ingest` is the process that extracts knowledge from files.

The standard ingestion procedure is:

1. Prepare the files.

   The current root contains a `Library` folder for original source material. As explained above, Valhalla intentionally provides no operations that modify this location; manage it manually for safety.

   The Library contains a special folder named `public_resources`. The system uses it to store public backup copies. Users must not modify anything in this folder.

   You may organize and store source material elsewhere in the Library however you prefer, but do not modify `public_resources`.

2. Confirm the target knowledge base.

   Enter `current status` or `knowledge-base status` and confirm that the intended knowledge base is active.

   This step is optional but strongly recommended. Valhalla does not yet have a reliable rollback mechanism. A rollback feature could be implemented by changing the relevant Workflow, but the base version of Valhalla does not currently provide one.

   Beginners should proceed cautiously while learning the system.

3. Ingest a file.

   Select the file to ingest from the Library and copy its path.

   Enter `ingest <file-path>` to complete the ingestion operation.

4. Inspect the ingestion results.

   Enter `list knowledge items` or `all entities` to inspect every knowledge item ingested from source material into the current knowledge base.

### Step 7: Build Higher-Level Knowledge Structures (Optional)

1. Build Relationships.

   Knowledge items do not exist in isolation; they are connected, and those connections are also knowledge.

   Enter `summarize relationships among knowledge items` to build Relationships among all knowledge items in the current knowledge base.

   Enter `show relationships` or `show <relationship-type> relationships` to inspect them.

2. Build a Knowledge Graph.

   Relationships among knowledge items can be organized into Knowledge Graphs. Because many kinds of Relationships may exist, different Graphs can be built for different needs.

   Enter `build a knowledge graph from <relationship-type> relationships` to construct the requested Knowledge Graph.

### Step 8: Query the Knowledge Base

Querying is effectively a default operation, so you do not have to explicitly enter `query`. Including it nevertheless makes the request more reliable.

```text
$valhalla query What are the main research topics in the current knowledge base? List them by topic and identify the information sources.
```

Better questions usually specify:

- What you want to know.
- Whether the answer should be a table, outline, or short essay.
- Whether sources must be listed.
- Whether web access is allowed when knowledge-base evidence is insufficient.

Example:

```text
$valhalla query
Question: What molecular-generation methods are present in the current knowledge base?
Output: Use a table to compare their methods, inputs, outputs, strengths, and limitations.
Sources: Use only the current knowledge base and list the supporting evidence.
If evidence is insufficient: Tell me explicitly; do not search the web automatically.
```

### Step 9: Ingest a Conversation

`Ingest conversation` is a special ingestion operation.

Queries and discussions with Valhalla about knowledge in the knowledge base also produce knowledge. That knowledge should not be discarded.

Ingesting and storing the knowledge items from the current conversation allows knowledge to accumulate over time.

After the conversation is complete, enter `ingest conversation` to ingest its knowledge items.

Note: Knowledge items ingested from a conversation and those ingested from Library files are different Entity types.

### Step 10: Use the Knowledge Base to Advance a Task

Queries help you understand knowledge; project work produces deliverables.

```text
$valhalla Advance the following task using the current knowledge base:
Objective: Design an experiment comparing Model A and Model B.
Output: Research hypotheses, variables, data, procedure, evaluation metrics, risks, and success criteria.
Requirements: Identify the supporting knowledge-base evidence and the information that is still missing.
```

By default, project-work results appear only in the response and are not automatically written back to the knowledge base.

### Step 11: Ingest Engineering Experience

`Ingest engineering experience` is another special ingestion operation.

Engineering experience is also knowledge and should not be discarded.

This operation extracts and stores knowledge items from engineering work so that experience can accumulate.

After the engineering task is complete, enter `ingest engineering experience` to ingest knowledge items from the current project-work session.

Note: Knowledge items derived from engineering experience, conversations, and Library files are three distinct Entity types.

### Step 12: Exit the Knowledge Base

```text
$valhalla exit knowledge base
```

After you exit, the session state returns to `idle`.

You have now completed your first full Valhalla workflow.
