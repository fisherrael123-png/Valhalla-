# Start a Knowledge Base

1. Confirm that the target Wiki exists.
2. Write the following to `.valhalla/kb_status.md`:

   ```yaml
   kb_status: kb:<name>
   target_wiki_path: Wiki/Wiki_<name>
   ```

   Both fields must use the same knowledge-base name.
3. Reply with `"<knowledge-base-name>"` and report `current_state` and the target Wiki path.
