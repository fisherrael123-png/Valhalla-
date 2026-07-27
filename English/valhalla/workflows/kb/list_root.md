# List Knowledge Bases Under the Current Root

1. Confirm that the current Valhalla root is known.
2. Read `wiki_registry.yaml` under the root. If the file is missing or empty, do not infer entries by scanning; report `No knowledge bases are registered under the current root`.
3. Also read `wiki_registry.md` as the human-readable projection. If the files conflict, `wiki_registry.yaml` takes precedence.
4. List each knowledge base's `kb_name`, `wiki_path`, `status`, `created_at`, `updated_at`, and `description`.
5. If the directory referenced by `wiki_path` does not exist, mark it `missing_path` in the result, but do not automatically remove the registry entry.
6. Output `list_root_report`, including the current root, number of knowledge bases, registered entries, and missing paths.

This operation is read-only. It does not create, delete, or repair any knowledge base.
