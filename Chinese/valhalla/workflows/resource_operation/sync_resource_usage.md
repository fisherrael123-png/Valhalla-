# 同步 resource usage

## 目的

以目标 root 的 `wiki_registry.yaml` 为已登记知识库权威，从已登记知识库的 `entity_registry.yaml` 与 `entity_resource_map.yaml` 重建 `resource_registry.yaml` 的 `usage.referenced_by` 与 `reference_count`，并清理指向未注册知识库的历史 usage。目标 root 默认是当前 root；当 root 级融合等服务转交时，可以显式传入 `target_root_path`。

本 workflow 是资源 usage 反向索引的唯一维护服务，用于历史遗留清理、资源反向索引校正，以及其他业务 operation 完成后通过 Router 转交的 usage 同步。它不登记知识库、不注销知识库、不修改任何知识库内容、不删除资源、不修改 `Library/`。

`entity_resource_map.yaml` 是 entity-resource 证据映射的唯一权威；`resource_registry.yaml` 中的 usage 只是可重建的派生反向索引，不得作为 entity-resource 事实来源。

## usage 条目格式

同步后的 `usage.referenced_by` 只能使用 canonical 结构化条目，字段为 `kb_name`、`entity_id`、`entity_file`：

```yaml
kb_name: <知识库名>
entity_id: <entity_id>
entity_file: Wiki/Wiki_<知识库名>/<content_file>
```

`reference_count` 按唯一 `(kb_name, entity_id)` 计数。`resource_registry.yaml` 只作为资源层反向索引，不参与 entity_id 编号。

禁止写入 legacy usage，包括：

- 旧字符串路径格式：`Wiki/Wiki_<知识库名>/entities/<entity_file>.md`
- 旧相对路径格式：`entities/<entity_file>.md`
- 旧 `kb` 字段格式：

```yaml
kb: <知识库名>
entity_id: <entity_id>
```

inspect 阶段可以识别上述 legacy usage 以便迁移；fix 阶段不得写入 legacy usage。

## inspect：只读扫描

1. 确认当前 Valhalla root 已知。
2. 确认系统状态为 `base` 或 `admin`。
3. 确认当前知识库状态为 `idle` 或 `kb:<name>`。
4. 解析目标 root：
   - 未提供 `target_root_path` 时，目标 root 为当前 root；
   - 提供 `target_root_path` 时，必须是调用方在正式输出中传入的精确目标 root 路径，且本 operation 不得根据文件名或目录名自行推断授权。
5. 读取目标 root 的 `wiki_registry.yaml`，取得已登记且 active 的知识库列表。
6. 如果输入了 `target_kb_name`，只处理该知识库；该名称必须存在于目标 root 的 `wiki_registry.yaml`。
7. 对每个目标知识库读取：
   - `Wiki/Wiki_<知识库名>/.registry/machine/entity_registry.yaml`
   - `Wiki/Wiki_<知识库名>/.registry/machine/entity_resource_map.yaml`
8. 从 `entity_resource_map.yaml` 提取唯一 `(resource_id, entity_id)`。
9. 用 `entity_registry.yaml` 查找每个 `entity_id` 的 `content_file`。
10. 如果 `content_file` 不是合法的 `entities/` 相对路径，报告并停止；不得猜测路径。
11. 读取目标 root 的 `resource_registry.yaml`。
12. 检查所有映射中的 `resource_id` 是否存在于 `resource_registry.yaml`。
13. 如果存在缺失资源，输出 `missing_resource_ids` 并停止；不得创建资源条目。
14. 生成 `target_usage_index`：
    - 每个资源对应从已登记知识库推导出的结构化 usage 条目；
    - 每个条目包含 `kb_name`、`entity_id`、`entity_file`。
15. 扫描目标 root `resource_registry.yaml` 的 `usage.referenced_by`：
    - canonical 条目中 `kb_name` 指向未注册知识库的条目列入 `stale_usage_entries`；
    - 旧字符串路径格式中 `Wiki/Wiki_<未注册知识库>/entities/` 也列入 stale；
    - 旧相对路径格式 `entities/` 必须与 active KB 的 `entity_resource_map.yaml` 和 `entity_registry.yaml` 匹配后才能迁移，否则列入 stale 或人工确认；
    - 旧 `kb` 字段格式中 `kb` 指向未注册知识库的条目列入 stale，指向 active KB 的条目只作为迁移输入；
    - 已注册知识库中缺失的目标条目列入 `missing_usage_entries`；
    - 已注册知识库中重复的 `(kb_name, entity_id)` 列入重复清理计划。
16. 输出 `sync_resource_usage_inspect_report`，必须列出：
    - 已登记知识库数量；
    - 扫描的知识库名称；
    - 扫描到的 entity 数量；
    - 扫描到的 entity-resource 映射数量；
    - `stale_usage_entries` 数量；
    - `missing_usage_entries` 数量；
    - `affected_resource_ids`；
    - `missing_resource_ids`；
    - 目标 root；
    - 将修改的 `affected_paths`：
      - `resource_registry.yaml`
      - `resource_registry.md`
    - `confirmation_prompt`。
17. inspect 阶段不得写入任何文件。

## fix：确认后同步

1. 重新执行 inspect 的读取与索引生成步骤，确保目标状态未漂移。
2. 如果出现新的 `missing_resource_ids`，停止，不写入。
3. 对每个受影响资源：
   - 删除指向未注册知识库的 `usage.referenced_by`；
   - 删除重复的 `(kb_name, entity_id)`；
   - 补齐已登记知识库中缺失的结构化 usage；
   - 将 active KB 的 legacy usage 迁移为 canonical usage；
   - 不保留任何 legacy usage；不能由 `entity_resource_map.yaml` 证明的 legacy usage 必须删除或列入人工确认。
4. 将受影响资源的 `reference_count` 更新为唯一 `(kb_name, entity_id)` 的数量。
5. 更新 `usage.computed_at`。
6. 同步 `resource_registry.md`：
   - 刷新受影响资源的引用数量；
   - 刷新引用摘要；
   - 如 Markdown 丢失或结构严重损坏，可按 `resource_registry.yaml` 完整重建。
7. 不修改 `wiki_registry.yaml` 或 `wiki_registry.md`。
8. 不修改任何 `Wiki/Wiki_<知识库名>/**`。
9. 不删除任何 `resource_id`。
10. 输出 `sync_resource_usage_report`。

## 输出

- `sync_resource_usage_inspect_report`
- `target_usage_index`
- `stale_usage_entries`
- `missing_usage_entries`
- `affected_resource_ids`
- `missing_resource_ids`
- `sync_resource_usage_report`
- `modified_files`
- `current_state`

## 禁止行为

- 不得修改 `wiki_registry.yaml` 或 `wiki_registry.md`。
- 不得修改任何知识库目录或 entity 正文。
- 不得创建、删除、移动或重命名资源文件。
- 不得删除 `resource_registry.yaml` 中的资源条目。
- 不得修改 `Library/` 或 `Library/public_resources/`。
- 不得从 `resource_registry.yaml` 推导 entity_id 编号。
