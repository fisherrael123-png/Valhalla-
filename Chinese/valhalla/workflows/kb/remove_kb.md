# 注销知识库

## 目的

从当前 Valhalla root 的知识库注册表中注销一个知识库。资源层反向引用必须在本 operation 内同步清理。

本 workflow 修改：

- `wiki_registry.yaml`
- `wiki_registry.md`

本 workflow 不删除 `Wiki/Wiki_<知识库名>/`，不删除知识库内的 entities、registries、resource tables、relationships、knowledge_graph、conversation_entities 或 engineering_entities，也不修改 `Library/` 或 `Library/public_resources/`。

`entity_resource_map.yaml` 是 entity-resource 证据映射的唯一权威；`resource_registry.yaml` 中的 `usage.referenced_by` 是派生反向索引。本 workflow 必须在注销知识库后按 active KB 重建资源反向索引。

## 输入

- 知识库名称。

## inspect：注销前检查

1. 确认当前 Valhalla root 已知。
2. 确认系统状态为 `base`。
3. 确认当前知识库状态为 `idle`。
4. 读取当前 root 下的 `wiki_registry.yaml`；该 YAML 是知识库登记的机器权威表。
5. 按 `kb_name` 精确匹配目标知识库；不得用模糊匹配自动选择。
6. 如果没有匹配条目，停止并报告目标知识库未登记。
7. 如果匹配多个条目，停止并列出候选，不得自动选择。
8. 读取目标条目的 `wiki_path`，确认它是相对路径，位于当前 root 的 `Wiki/` 下，且不包含 `..`。
9. 读取 `resource_registry.yaml`，只读扫描每个资源的 `usage.referenced_by`，估算注销后会在本 operation 内清理的 stale usage。
10. 将以下 usage 条目列入 `resource_usage_cleanup_plan`：
    - 结构化条目中 `kb_name` 等于目标知识库；
    - 兼容旧格式的结构化条目中 `kb` 等于目标知识库；
    - 字符串路径以 `Wiki/Wiki_<知识库名>/entities/` 开头；
    - 旧相对路径格式 `entities/` 只有在可由目标 KB 的 `entity_resource_map.yaml` 证明时才列入目标 KB 清理计划，否则列入人工确认。
11. 预估清理后可能 `reference_count = 0` 的资源，列入 `orphan_candidate_resource_ids`；只报告，不删除资源。
13. 输出 `remove_kb_inspect_report`，必须列出：
    - 目标知识库名称；
    - 当前 root；
    - 将从 `wiki_registry.yaml` 删除的完整条目；
    - 将保留且不删除的 `Wiki/Wiki_<知识库名>/` 绝对路径；
    - 将由本 operation 清理 usage 的 `affected_resource_ids`；
    - 将由本 operation 删除的 usage 条目数量；
    - `orphan_candidate_resource_ids`；
    - `affected_paths`：
      - `wiki_registry.yaml`
      - `wiki_registry.md`
    - `next_operation: null`；
    - `confirmation_prompt`。
14. 没有用户明确确认前，不得写入任何文件。

## fix：确认后注销并同步 usage 清理

1. 重新读取 `wiki_registry.yaml`，再次按 `kb_name` 精确匹配目标条目。
2. 重新读取 `resource_registry.yaml`，再次生成只读 `resource_usage_cleanup_plan`。
3. 从 `wiki_registry.yaml` 的 `wikis` 列表中移除目标知识库条目。
4. 根据更新后的 `wiki_registry.yaml` 同步重建或增量更新 `wiki_registry.md`。发生冲突时以 YAML 为准。
5. 按更新后的 active KB，重新读取每个知识库的 `.registry/machine/entity_registry.yaml` 与 `.registry/machine/entity_resource_map.yaml`，重建 `resource_registry.yaml/md` 的 `usage.referenced_by`、`reference_count` 和 `usage.computed_at`，从而删除目标 KB 的 stale usage。
6. `usage.referenced_by` 只能写入 `kb_name`、`entity_id`、`entity_file` canonical 条目；`entity_file` 必须是 `Wiki/Wiki_<知识库名>/<content_file>`；不得写入 legacy usage，包括字符串路径、`entities/` 相对路径和旧 `kb` 字段格式。
7. `reference_count` 按唯一 `(kb_name, entity_id)` 计数。
8. 同一操作内同步 `resource_registry.md`，以 `resource_registry.yaml` 为唯一事实来源刷新引用数量投影。
9. 不删除任何 `resource_id`。`reference_count = 0` 的资源只在 `resource_usage_cleanup_report` 中列为 orphan candidate。
10. 不删除、移动或重命名 `Wiki/Wiki_<知识库名>/`。
11. 输出 `remove_kb_report`、`resource_usage_cleanup_report` 和 `next_operation: null`。

## 输出

- `remove_kb_inspect_report`：注销前只读检查摘要。
- `resource_usage_cleanup_plan`：拟从资源层移除的 usage 引用。
- `affected_resource_ids`：将修改 usage 的资源。
- `orphan_candidate_resource_ids`：清理后可能成为孤儿资源的资源。
- `remove_kb_report`：注销摘要。
- `removed_kb`：被注销的知识库名称。
- `removed_registry_entry`：从 `wiki_registry.yaml` 移除的完整条目。
- `resource_usage_cleanup_report`：实际删除的 usage 数量、受影响资源和 orphan candidates。
- `preserved_wiki_path`：保留的 Wiki 相对路径和绝对路径。
- `manual_cleanup_path`：用户如需手动删除时应处理的绝对路径。
- `modified_files`：应包含 `wiki_registry.yaml`、`wiki_registry.md`、`resource_registry.yaml`、`resource_registry.md`。
- `next_operation`：注销登记且 usage 同步完成后为 `null`。
- `current_state`：当前 root、`os_status` 与 `kb_status`。

## 禁止行为

- 不得删除、移动或重命名 `Wiki/Wiki_<知识库名>/`。
- 不得删除、移动或重命名目标知识库下的任何文件。
- 不得删除任何 `resource_id`。
- 不得修改 `Library/` 或 `Library/public_resources/`。
- 不得修改其他知识库的资料表、实体、关系或知识图谱。
- 不得在当前会话状态为 `kb:<name>` 时执行；必须先通过 `exit_kb` 回到 `idle`。
- 不得把用户对本操作的确认解释为删除目录、删除资源、改写 entity 正文或修改资料表的授权。
