# Valhalla Tutorial 05

> Intended audience: Users who have completed Valhalla Tutorials 01, 02, 03, and 04—the minimum requirement is Tutorial 01—and want to develop only `basic system services`  
>
> Learning objective: Understand how to customize Valhalla to meet user requirements  
>
> Estimated time: 5–10 minutes

## Beginner Valhalla Development

Valhalla is a completely open system that can be customized to meet user needs.

Valhalla was designed for interdisciplinary researchers. Its natural-language construction allows users without a computer-science background to customize it easily.

This beginner development guide is intended for users who want to develop only `basic system services`, but that already covers most development scenarios.

## Self-Evolving Development

Now for the exciting part: `self-bootstrapping development` is one of Valhalla's defining features.

The standard `self-bootstrapping development` process is:

1. `Start Valhalla`. For example, in Codex CLI with Valhalla installed, enter `$valhalla` to invoke the system explicitly.
2. Describe the development requirement. For example: `I want a new system service—or a new function—whose purpose is XXXX. Please propose an implementation plan.`

   The LLM reviews the Valhalla system. Because Valhalla has a simple architecture, an explicit process, and clear boundaries—`microkernel + five-layer encapsulation`—the LLM can follow existing structures and design a complete `Router + Contract + Workflow` system-service plan.
3. Review the plan. If anything is unclear, the LLM asks questions. For example, when a functional component has several possible implementations, the LLM asks you to choose one.
4. Once the plan is finalized, instruct the LLM to implement or execute it. The LLM creates the new system service or function. You can then find its trigger prompt in the Router and begin using it.

The `fuse roots` function added in Valhalla 0.5.10—previously described as Valhalla's most complex function—was developed entirely through this `self-bootstrapping development` model. Because it is a system-level function, designing its plan required an understanding of Valhalla's architectural details.

For ordinary application development, you usually need only to `state the requirement` and `review the plan`.

One real internal-testing example involved a tester who was neither a developer nor a computer specialist. The tester wanted ingested knowledge to account for their own research direction and requested: `My research project is XXX. I need a new function that considers the relationship between my project and the source material during ingestion.` Through `self-bootstrapping development`, a specialized `ingest` function with its own trigger prompt was quickly added to the system.
