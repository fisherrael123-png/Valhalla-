# resource_registry

> This file is the human-readable projection of `resource_registry.yaml`.
> Resource identity, file paths, synchronization state, usage, and blacklist state are governed by the corresponding authoritative registries.
> This file does not independently maintain resource facts. Keep it synchronized with `resource_registry.yaml`; only `sync_resource_usage` rebuilds the reverse usage index.

## Basic Information

| Field | Value |
| --- | --- |
| Resource registry | `resource_registry.yaml` |
| Registry version | `2` |
| Last updated | `To be completed` |
| Resource count | `0` |

## Resource Summary

| resource_id | Canonical name | Aliases | Type | Version | Lifecycle | Blacklisted | Usage count |
| --- | --- | --- | --- | --- | --- | --- | --- |

## File Details

| resource_id | file_id | Representation type | Format | Library source copy | Public copy | Sync state |
| --- | --- | --- | --- | --- | --- | --- |

## Field Notes

- One `resource_id` identifies an information object with unique content and version.
- PDF, Markdown, TXT, OCR, or extracted-text files representing the same information may be grouped under one `resource_id` as different representation files.
- Preprints, published versions, revisions, substantive translations, or versions with material additions or deletions must use different `resource_id` values.
- The canonical name comes from `identity.canonical_name`; all other names come from `identity.aliases`.
- A Library source copy may exist only under the current root's `Library/` directory and must not be in `Library/public_resources/`.
- A public copy must be located under `Library/public_resources/<resource_id>/`.
- Blacklist status comes from the matching result in `blacklist_registry.yaml`.
- `sync_resource_usage` derives the usage count from `entity_resource_map.yaml` and `entity_registry.yaml` in active knowledge bases.

## Notes

None.
