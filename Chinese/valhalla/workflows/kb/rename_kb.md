# 修改知识库名称

## 目的

把当前 Valhalla root 下一个已登记知识库从旧名称改为新名称。

本 workflow 面向普通研究组成员。用户只需要知道：这是“改知识库名字”的服务。系统内部会同步知识库列表、知识库文件夹名称和知识库自己的标题。

## 输入

- 旧知识库名称。
- 新知识库名称。

## inspect：改名前检查

1. 确认当前 Valhalla root 已知。
2. 确认当前系统状态为 `base`。
3. 确认当前知识库状态为 `idle`。如果当前处于 `kb:<name>`，停止并提示用户先退出知识库。
4. 读取当前 root 下的 `wiki_registry.yaml`；该 YAML 是机器权威表。
5. 按 `kb_name` 精确匹配旧知识库名称；不得模糊匹配。
6. 如果旧知识库不存在，停止并报告。
7. 如果旧知识库匹配多个条目，停止并列出候选。
8. 确认新知识库名称不在 `wiki_registry.yaml` 中。
9. 确认旧目录存在：`Wiki/Wiki_<旧知识库名称>/`。
10. 确认目标目录不存在：`Wiki/Wiki_<新知识库名称>/`。
11. 确认旧目录和新目录都位于当前 root 的 `Wiki/` 下，且路径不包含 `..`。
12. 输出 `rename_kb_inspect_report`，列出：
    - 当前 root；
    - 旧知识库名称；
    - 新知识库名称；
    - 旧目录相对路径和绝对路径；
    - 新目录相对路径和绝对路径；
    - 将修改的文件范围；
    - 明确不会修改的范围。
13. 向用户请求确认。没有明确确认前，不得改名、移动目录或写入任何文件。

## 确认时必须列出

将修改：

- `wiki_registry.yaml`
- `wiki_registry.md`
- `Wiki/Wiki_<旧知识库名称>/` 将移动为 `Wiki/Wiki_<新知识库名称>/`
- 新目录内的知识库标题、索引标题、日志标题
- 新目录内机器注册表中的知识库名称字段
- 新目录内人类可读投影中的知识库名称说明

不会修改：

- `resource_registry.md`
- `resource_registry.yaml`
- `Library/`
- `Library/public_resources/`
- 其他知识库目录
- 原始资料文件
- public resource 副本
- entity 正文内容中的学术知识内容

## fix：确认后执行改名

只有用户明确确认 inspect 报告后，才能执行本阶段。

1. 再次确认旧目录存在、新目录不存在。
2. 将目录 `Wiki/Wiki_<旧知识库名称>/` 移动为 `Wiki/Wiki_<新知识库名称>/`。
3. 改名导致的 `usage.referenced_by.entity_file` 与 `kb_name` 变化必须在本 operation 内同步写入 `resource_registry.yaml/md`。
4. 修改 `wiki_registry.yaml` 中旧知识库条目：
   - `kb_name` 改为新知识库名称；
   - `wiki_path` 改为 `Wiki/Wiki_<新知识库名称>`；
   - `updated_at` 改为当天日期；
   - `description` 如果原本等于旧知识库名称，则改为新知识库名称；否则保留原描述。
5. 按 `wiki_registry.yaml` 同步更新 `wiki_registry.md`：
   - 找到旧知识库对应的表格行；
   - 将第一列 `kb_name` 改为新知识库名称；
   - 将第二列 `wiki_path` 改为 `Wiki/Wiki_<新知识库名称>`；
   - 保留 `created_at`；
   - 将 `updated_at` 改为当天日期；
   - 如果 `description` 原本等于旧知识库名称，则改为新知识库名称；
   - 如果 `description` 是其他说明文字，则保留；
   - 其他知识库行不得修改；
   - 如果 `wiki_registry.yaml` 和 `wiki_registry.md` 冲突，以 `wiki_registry.yaml` 为准重建这一行。
6. 在新目录中更新以下入口文件：
   - `Wiki.md`：标题和用途描述中的知识库名称改为新名称；
   - `index.md`：第一行标题改为新名称；
   - `log.md`：第一行标题改为新名称，并追加一条 `rename | <旧名称> -> <新名称>` 日志。
7. 在新目录中更新机器 YAML 的知识库名称字段：
   - `.virtualDatabase/machine/local_resources.yaml`
   - `.virtualDatabase/machine/required_resources.yaml`
   - `.virtualDatabase/machine/excluded_resources.yaml`
   - `.registry/machine/entity_registry.yaml`
   - `.registry/machine/entity_resource_map.yaml`
   - `.registry/machine/relationship_registry.yaml`
   - `.registry/machine/knowledge_graph_registry.yaml`
   - `.registry/machine/conversation_entity_registry.yaml`
   - `.registry/machine/engineering_entity_registry.yaml`
8. 如果存在 relationship fact 或 knowledge graph fact 文件，只更新其中表示所属知识库的 `kb` 字段，不改事实内容。
9. 更新对应的人类可读 Markdown 投影中的“知识库：<旧名称>”为“知识库：<新名称>”。
10. 不改历史 note、历史日志、资源加入说明中的旧名称；这些属于审计记录，可以保留。
11. 从改名后的 active KB `.registry/machine/entity_resource_map.yaml` 与 `.registry/machine/entity_registry.yaml` 派生更新 `resource_registry.yaml/md` 的 `usage.referenced_by`、`reference_count` 和 `usage.computed_at`。
12. `usage.referenced_by` 只能写入 `kb_name`、`entity_id`、`entity_file` canonical 条目；`entity_file` 必须是 `Wiki/Wiki_<知识库名>/<content_file>`；`reference_count` 按唯一 `(kb_name, entity_id)` 计数；不得写入 legacy usage，包括字符串路径、`entities/` 相对路径和旧 `kb` 字段格式。
13. 同一操作内同步 `resource_registry.md`，以 `resource_registry.yaml` 为唯一事实来源刷新引用数量投影。
15. 输出 `rename_kb_report`。

## 输出

- `rename_kb_inspect_report`：改名前检查报告；
- `rename_kb_report`：改名完成报告；
- `renamed_kb`：旧名称、新名称；
- `moved_paths`：旧目录和新目录；
- `next_operation`：改名且 usage 同步完成后为 `null`；
- `modified_files`：实际修改过的文件；
- `current_state`：当前 root、`os_status` 与 `kb_status`。

## 禁止行为

- 不得删除任何资料文件。
- 不得修改 `resource_registry.yaml` 或 `resource_registry.md` 的资源身份、表现文件、生命周期和 policy 字段；只能同步 usage 派生字段。
- 不得修改 `Library/` 或 `Library/public_resources/`。
- 不得修改其他知识库。
- 不得在知识库已激活时执行。
- 不得用模糊匹配自动选择知识库。
- 不得把用户对改名的确认解释为删除、清理、摄入或重建知识库的授权。
