# edit_resource_table workflow

## 目的

编辑当前知识库的 `local_resources`、`required_resources` 或 `excluded_resources`。

每张资料表由两个并行文件组成：

- `<资料表名称>.yaml`：机器权威成员表；
- `<资料表名称>.md`：人类可读投影视图。

知识库层以 `resource_id` 作为稳定身份。Markdown 同时显示用户加入时输入和资源层当前来源路径。

## 输入

```yaml
target_table: <local_resources | required_resources | excluded_resources>
action: <添加 | 删除 | 移除>
resource_query: <resource_id | 文件名 | Library 相对路径 | Library 文件夹>
note: <可选备注>
```

中文命令别名映射：

- “本库资料表” -> `local_resources`
- “必须资料表” -> `required_resources`
- “剔除资料表” -> `excluded_resources`

## 解析资源

1. 输入为合法 `resource_id` 时，直接在 `resource_registry.yaml` 中查找。
2. 输入为文件名、`Library/` 相对路径或文件夹时，只在资源层解析：
   - 匹配 `representations[*].source_copies`；
   - 匹配公共副本；
   - 匹配主名称和附属名称。
3. 多个候选属于不同资源时列出候选并请求用户确认，不得自动选择。
4. 未登记文件需要添加时，先执行 `register_resource`。
5. 保存用户原始 `resource_query` 到 `added_via.value`，保存解析方式到 `added_via.input_type`。

## 黑名单验证

检查该资料是否在黑名单中，如果是，则立即终止该过程，并询问用户是否继续其他文件的操作。

## 添加

1. 如果 YAML 中没有该 `resource_id`：
   - 在 `resources` 末尾增量追加条目；
   - 设置 `membership_status: active`；
   - 写入 `added_via`、`added_at`、`removed_at: null` 和备注。
2. 如果条目已经是 `active`：
   - 不重复添加；
   - 可按用户要求更新备注。
3. 如果条目是 `pending_removal`：
   - 恢复为 `membership_status: active`；
   - 将 `removed_at` 清空；
   - 用本次输入更新 `added_via` 和 `added_at`。
4. 从 `resource_registry.yaml` 取得主名称、当前来源路径、类型和版本。
5. 在 Markdown 表格末尾增量追加对应行；恢复条目时只更新原有行。
6. 只更新 Markdown 的计数和更新时间，不完整重建整个文件。
7. 不修改 `resource_registry.yaml` 或 `resource_registry.md`。资料表 membership 只影响有效资料库范围，不是 `usage.referenced_by` 的来源；resource usage 只由 `entity_resource_map.yaml` 与 `entity_registry.yaml` 派生。

## 删除或移除

1. 在 YAML 中定位该 `resource_id`。
2. 不立即物理删除条目：
   - 设置 `membership_status: pending_removal`；
   - 写入 `removed_at`。
3. 资源从状态修改完成时立即退出有效资料库计算。
4. Markdown 只更新对应行：
   - 成员状态显示为“待清理”；
   - 写入删除标记时间。
5. 不完整重建 Markdown，也不立即删除对应行。
6. 已经是 `pending_removal` 时不重复操作。
7. 不修改 `resource_registry.yaml` 或 `resource_registry.md`。待清理资料表条目不再参与有效资料库计算，但不会自动删除 provenance 映射；如 entity-resource 映射被其他 operation 修改，应由修改该映射的 operation 同步更新 usage。

## 当前来源路径投影

- 当前来源路径来自 `resource_registry.yaml` 的所有 `representations[*].source_copies[*].path`。
- 多个路径在 Markdown 单元格内以 `<br>` 分隔。
- 文件移动、改名或来源副本变化不修改 YAML 资料表成员身份。
- 路径投影漂移由 lint 批量刷新。

## 有效成员

只有以下条目参与知识库资料范围计算：

```text
membership_status == active
```

## 禁止行为

- 不得让 Markdown 成为成员身份权威来源；
- 不得让 `pending_removal` 条目继续参与有效资料库；
- 不得在普通删除操作中物理删除 YAML 条目；
- 不得因路径变化修改 `resource_id`；
- 不得在添加一条资料时完整重建 Markdown；
- 不得修改资源身份或文件映射；
- 不得移动或删除来源文件和公共副本。



