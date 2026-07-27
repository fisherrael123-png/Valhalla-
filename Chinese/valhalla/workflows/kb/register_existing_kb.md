# 登记已有知识库

## 目的

把当前 Valhalla root 下已经存在的 `Wiki/Wiki_<知识库名>/` 目录登记到 root 级 `wiki_registry.yaml`，同步 `wiki_registry.md`，并根据该知识库现有的 entity-resource 映射验证资源身份。资源层反向索引必须在本 operation 内同步维护。

本 workflow 会修改：

- `wiki_registry.yaml`
- `wiki_registry.md`

本 workflow 不创建目录、不移动目录、不修改知识库内部文件、不启动知识库、不修复损坏结构。

`entity_resource_map.yaml` 是 entity-resource 证据映射的唯一权威；`resource_registry.yaml` 中的 `usage.referenced_by` 是从它派生的反向索引。本 workflow 必须同步写 usage；写入 usage 时只能使用 `kb_name`、`entity_id`、`entity_file` canonical 条目，不得写入 legacy usage。

## 输入

- 知识库名称。

## inspect：登记前检查

1. 确认当前 Valhalla root 已知。
2. 确认系统状态为 `base`。
3. 确认当前知识库状态为 `idle`。
4. 读取 `wiki_registry.yaml`，以 YAML 为机器权威表。
5. 按 `kb_name` 精确匹配输入名称；如果已经登记，停止。
6. 确认目录存在：`Wiki/Wiki_<知识库名>/`。
7. 确认目录位于当前 root 的 `Wiki/` 下，且路径不包含 `..`。
8. 确认最低结构存在：
   - `Wiki.md`
   - `index.md`
   - `log.md`
   - `.virtualDatabase/machine/local_resources.yaml`
   - `.virtualDatabase/machine/required_resources.yaml`
   - `.virtualDatabase/machine/excluded_resources.yaml`
   - `.registry/machine/entity_registry.yaml`
   - `.registry/machine/entity_resource_map.yaml`
9. 读取目标知识库的 `.registry/machine/entity_registry.yaml` 和 `.registry/machine/entity_resource_map.yaml`。
10. 从 `entity_resource_map.yaml` 提取唯一 `(resource_id, entity_id)`。
11. 用 `entity_registry.yaml` 为每个 `entity_id` 查找 `content_file`。`content_file` 必须是相对于知识库目录的 `entities/` 路径；不合规时报告并停止。
12. 读取当前 root 的 `resource_registry.yaml`。
13. 检查每个映射中的 `resource_id` 是否存在于 `resource_registry.yaml`。
14. 如果存在缺失资源，输出 `missing_resource_ids` 并停止；不得自动伪造资源条目。
15. 生成 `resource_usage_sync_plan`：
   - 登记成功后必须在当前 `register_existing_kb` operation 内同步 `resource_registry.yaml/md` usage；
   - 从已登记 active KB 的 `entity_resource_map.yaml` 和 `entity_registry.yaml` 统一重建 usage；
   - 已存在的 legacy usage 不视为完成状态，必须在本 operation 内迁移或清理；
   - `affected_paths` 必须包含 `resource_registry.yaml` 与 `resource_registry.md`。
16. 不检查、不修复、不重写知识库内部标题或内容。
17. 输出 `register_existing_kb_inspect_report`，必须列出将修改：
   - `wiki_registry.yaml`
   - `wiki_registry.md`
18. 明确不会修改：
   - `Wiki/Wiki_<知识库名>/**`
   - `Library/`
   - `Library/public_resources/`
   - 其他知识库目录
19. 请求用户确认。没有明确确认前，不得写入任何文件。

## fix：确认后登记

1. 重新确认目标目录存在。
2. 重新确认 `wiki_registry.yaml` 中没有同名 `kb_name`。
3. 重新读取 `entity_registry.yaml`、`entity_resource_map.yaml` 和 `resource_registry.yaml`。
4. 再次确认所有映射中的 `resource_id` 都存在于 `resource_registry.yaml`。
5. 向 `wiki_registry.yaml` 的 `wikis` 追加条目：
   - `kb_name: <知识库名>`
   - `wiki_path: Wiki/Wiki_<知识库名>`
   - `status: active`
   - `created_at: <当天日期>`
   - `updated_at: <当天日期>`
   - `description: <知识库名>`
6. 以 `wiki_registry.yaml` 为准重建或同步 `wiki_registry.md` 表格。
7. 从当前 root 已登记 active KB 的 `.registry/machine/entity_resource_map.yaml` 与 `.registry/machine/entity_registry.yaml` 派生更新 `resource_registry.yaml/md` 的 `usage.referenced_by`、`reference_count` 和 `usage.computed_at`。
8. `usage.referenced_by` 只能写入 `kb_name`、`entity_id`、`entity_file` canonical 条目；`entity_file` 必须是 `Wiki/Wiki_<知识库名>/<content_file>`；不得写入 legacy usage，包括字符串路径、`entities/` 相对路径和旧 `kb` 字段格式。
9. `reference_count` 按唯一 `(kb_name, entity_id)` 计数。
10. 同一操作内同步 `resource_registry.md`，以 `resource_registry.yaml` 为唯一事实来源刷新引用数量投影。
11. 不修改目标 Wiki 目录内任何文件。
12. 输出 `register_existing_kb_report`、`resource_usage_sync_report` 和 `next_operation: null`。

## 输出

- `register_existing_kb_inspect_report`
- `resource_usage_sync_plan`
- `affected_resource_ids`
- `missing_resource_ids`
- `register_existing_kb_report`
- `registered_kb`
- `resource_usage_sync_report`
- `next_operation`
- `modified_files`
- `current_state`

## 禁止行为

- 不得创建 `Wiki/Wiki_<知识库名>/`。
- 不得修改 `Wiki/Wiki_<知识库名>/**`。
- 不得启动知识库。
- 不得修复内部结构。
- 不得删除任何文件。
- 不得删除任何 `resource_id`。
- 不得修改 `Library/` 或 `Library/public_resources/`。
- 不得模糊匹配知识库名称。
- 不得把缺失 `resource_id` 自动创建为资源条目。
