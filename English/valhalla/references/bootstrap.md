# Bootstrap Process

When Valhalla starts for the first time in the current session, it runs `python bootstrap.py` and performs the following steps in order:

1. Run the system self-test, verify or rebuild `~/.codex/valhalla/os_status.json` and `roots.json`, and reset the system state to `base`.
2. Verify that every Contract conforms to the unified 0.5.11 format and validate executor reference paths.
3. Validate resource-layer Contracts, status structures, and the Entity path contract.
4. Load `router/router.md` so that the Router content enters the current session context.
5. Display the current system state, current root, and current knowledge-base state.
6. Report that initialization is complete.

Bootstrap handles only initialization, self-testing, state reset, and Router loading. It does not automatically parse the user's request, load a business Contract, or execute a specific Workflow.
