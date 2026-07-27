# blacklist_operation workflow

## 目的

维护 Valhalla root 级全局资源黑名单。

拉黑对象始终是整个资源（`resource_id`）。该资源下的 PDF、Markdown、TXT、OCR、文本抽取文件以及所有来源副本和公共副本同时受到限制。

用户不需要知道 `resource_id`，可以输入资料文件名或 `Library/` 相对路径；系统负责解析并在写入前确认稳定资源身份。

## 输入

### list_blacklist

无必需输入。

### add_blacklist

必需：

- `resource_query`：资料文件名或 `Library/` 相对路径；
- `reason`：加入黑名单的原因。

可选：

- `evidence`：证据链接、说明或审查记录；
- `note`：补充说明。

### remove_blacklist

必需：

- `blacklist_id`。

可选：

- `reason`；
- `evidence`；
- `note`。

## 前置检查

1. 读取当前 Valhalla root。
2. 读取 `resource_registry.yaml` 和 `blacklist_registry.yaml`。
3. `blacklist_registry.yaml` 不存在时，使用对应模板初始化。
4. 根据 contract 检查 operation 和 `admin` 状态约束。

## 文件名到 resource_id 的解析

1. 优先把输入作为 `Library/` 相对路径精确匹配 `source_copies.path`。
2. 未精确匹配时，把输入作为文件名，匹配：
   - `source_copies.local_name`；
   - `source_copies.path` 的末级文件名；
   - 必要时匹配资源附属名称中 `type: filename` 的条目。
3. 多个文件匹配但全部属于同一 `resource_id` 时，解析为该资源。
4. 多个候选属于不同 `resource_id` 时：
   - 显示每个候选的 `resource_id`、主名称、版本、文件路径和格式；
   - 请求用户确认；
   - 不得自动选择。
5. 文件存在但尚未登记时：
   - 先执行 `register_resource`；
   - 注册时仍必须遵守唯一信息和版本边界；
   - 完成后再继续拉黑。
6. 没有候选时停止，不得创建无法关联资源身份的黑名单条目。

文件名或路径只是人类输入和审计记录，不是黑名单的稳定身份。

## list_blacklist 流程

1. 读取 `blacklist_registry.yaml`。
2. 筛选 `status: listed`。
3. 输出：
   - `blacklist_id`
   - `resource_id`
   - 资源主名称
   - 用户原始输入
   - 原因
   - 加入日期

## add_blacklist 流程

1. 按上述规则将 `resource_query` 解析为唯一 `resource_id`。
2. 检查该 `resource_id` 是否已有黑名单条目。
3. 已处于 `listed` 时：
   - 不重复添加；
   - 可追加证据或备注；
   - 更新 `updated_at`。
4. 已有 `removed` 条目时：
   - 恢复为 `listed`；
   - 写入新的原因、证据和日期。
5. 没有条目时：
   - 创建 `blacklist_id`；
   - 写入 `resource_id`；
   - 在 `matched_input` 保存用户输入和解析出的来源路径；
   - 保存资源主名称和版本身份快照。
6. 将 `resource_registry.yaml` 对应资源的 `policy.blacklist_status` 更新为 `listed`，并写入 `blacklist_id`。
7. 对所有知识库的 `.virtualDatabase/machine/local_resources.yaml` 和 `.virtualDatabase/machine/required_resources.yaml`：
   - 将对应 active 条目标记为 `pending_removal`；
   - 写入 `removed_at`；
   - 在同名 Markdown 中将对应行增量标记为“待清理”；
   - 不立即完整重建 Markdown，也不物理删除 YAML 条目。
8. 该 `resource_id` 立即退出所有有效资料集合，报告受影响知识库。
9. 不修改 `usage.referenced_by`、`reference_count` 或 `entity_resource_map.yaml`；黑名单状态不删除历史 provenance。`entity_resource_map.yaml` 是 entity-resource 证据映射的唯一权威，`resource_registry.yaml` usage 只是由 `sync_resource_usage` 可重建的派生反向索引。
10. 同步 `resource_registry.md` 中该资源的黑名单状态投影。
11. 禁止该资源参与摄入、引用、实体更新、关系构建、图谱构建和报告生成。
12. 写回注册表并输出报告。

拉黑本身不得自动移动或删除来源副本，也不得自动删除公共副本。物理移动或删除必须作为独立高风险操作再次请求用户确认。

## remove_blacklist 流程

1. 根据 `blacklist_id` 查找条目。
2. 不存在时停止并报告。
3. 存在时将其标记为 `removed`，记录移除原因、依据和日期。
4. 将资源注册表中的黑名单投影更新为 `not_listed`。
5. 同步 `resource_registry.md` 中该资源的黑名单状态投影。
6. 移除黑名单不自动恢复各知识库引用；恢复使用必须重新审查并显式编辑资料表。

## 输出格式

### blacklist_list_report

```markdown
| blacklist_id | resource_id | 主名称 | 用户输入 | reason | listed_at |
| --- | --- | --- | --- | --- | --- |
```

### blacklist_add_report

必须包括：

- 操作结果；
- `blacklist_id`；
- `resource_id`；
- 资源主名称；
- 用户原始输入；
- 解析出的来源路径；
- 影响的知识库；
- 未执行任何物理移动或删除的说明。

### blacklist_remove_report

必须包括：

- `blacklist_id`；
- `resource_id`；
- 移除原因和日期；
- 不会自动恢复知识库引用的说明。



