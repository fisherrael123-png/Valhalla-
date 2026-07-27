# register_resource Workflow

## Purpose

Register a non-public file under the current Valhalla root's `Library/` as a Resource-layer object.

One `resource_id` represents a unique content-version information object. A filename, file path, or file format is not a resource identity.

## Input

Required:

- `resource_query`: A filename, directory name, or `Library/`-relative path specified by the user.

Optional:

- `canonical_name`: Canonical resource name;
- `aliases`: Alternate names;
- `information_identity`: Type, version, edition, language, publication date, DOI, or URL;
- `representation_type`: Defaults to `authoritative`;
- `note`.

## Path Constraints

1. The source file must be under the current root's `Library/`.
2. The source file must not be under `Library/public_resources/`.
3. The registry stores only paths relative to the current root.
4. Absolute paths, paths outside the root, and traversal paths containing `..` are prohibited.
5. One representation file may register multiple `source_copies`.
6. A public copy must be under `Library/public_resources/<resource_id>/`.

## Resource-Identity Rules

### May Share One resource_id

- Different formats of the same information, such as PDF, Markdown, and TXT;
- OCR output, extracted text, or format conversions;
- Copies with different filenames but identical content;
- Copies of the same material in different non-public `Library/` directories.

### Must Use Different resource_id Values

- A preprint and a formally published version;
- An initial edition and a revision;
- An original work and a translation containing material new information;
- An abridged version and the full text;
- Different releases of a dataset;
- Different releases or snapshots of code;
- Materials with material additions or deletions.

Similar titles, authors, or filenames alone do not prove that resources are identical. If content and version identity cannot be confirmed, do not merge automatically; preserve them as separate resources or ask the user to decide.

## Naming Rules

1. Every resource must have exactly one `identity.canonical_name`.
2. Record all other names under `identity.aliases`.
3. A filename may be an alternate-name candidate but must not automatically replace the canonical name.
4. Changes to canonical or alternate names do not change `resource_id`.
5. The canonical name must not also appear among the aliases.

## Execution Process

1. Resolve `resource_query` within non-public directories under the current root's `Library/`.
2. If there is no candidate file, stop and report that none was found.
3. If multiple candidates exist, compare paths, SHA-256 hashes, formats, and information identities:
   - Continue if every candidate points to the same registered `resource_id`;
   - If candidates point to different resources or identity is unclear, list them and ask the user to choose;
   - Do not select automatically.
4. Calculate each source file's SHA-256 and search existing `source_copies`, public copies, and information identities in `resource_registry.yaml`.
5. Classify the input as:
   - An already registered source copy;
   - A new source copy of an existing resource;
   - A new representation of an existing resource;
   - A new unique information object.
6. For a new resource, assign a new `resource_id` and determine one `canonical_name`.
7. For a new representation, assign a new `file_id` and add it to `representations`.
8. For converted, OCR, or extracted-text files, set `derived_from` to the source representation within the same resource.
9. Create or locate the public copy under `Library/public_resources/<resource_id>/`.
10. Update the SHA-256 hash, existence state, and `sync_status`.
11. Recalculate `usage` and the blacklist-association projection.
12. Write `resource_registry.yaml`.
13. Synchronize `resource_registry.md` incrementally. If the projection is severely damaged, rebuild it completely from `resource_registry.yaml`.
14. Validate the Resource schema, path boundaries, name uniqueness, `file_id` values, and derivation relationships.

## Prohibited Actions

- Do not merge different versions or different information content under one `resource_id`.
- Do not register a public copy as a source copy.
- Do not allow the Entity, Relationship, or Graph layer to store source-copy or public-copy paths directly.
- Do not infer that two files are the same resource from an identical filename alone.
- Do not overwrite an existing public copy without user confirmation.

## Output

- `resource_id`
- `canonical_name`
- New or reused `file_id`
- Source-copy path
- Public-copy path
- Modified files
- Identity conflicts requiring user confirmation
