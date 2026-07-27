# 融合知识库

## 目的

把当前 Valhalla root 内用户显式指定的多个来源知识库，融合成一个新的目标知识库。

本 workflow 面向研究组成员。用户只需要知道：这是“融合知识库”的管理服务。系统内部会先只读审核来源知识库的 registry、虚拟资料表和正文内容，形成融合计划；用户确认后，才创建新的目标知识库并写入融合结果。

source KB 全程只读。不得修改、移动、删除或清理任何来源知识库文件。

## 输入

- 来源知识库列表。
- 目标知识库名称。

唯一支持的命令形态：

```text
融合知识库 <来源知识库列表> 为 <新知识库>
```

来源知识库之间可以使用英文逗号 `,`、中文逗号 `，` 或顿号 `、` 分隔。知识库名称必须精确匹配当前 root 的 `wiki_registry.yaml`。

不支持融合当前root全部知识库。以下输入必须停止并说明原因：

```text
融合当前root全部知识库为 <新知识库>
融合所有知识库
```

## 总体原则

1. 本操作不是 root 融合，不读取其他 root。
2. 本操作必须在 `admin` 状态下运行。
3. 本操作必须在 `idle` 知识库状态下运行。
4. 来源知识库必须全部登记在当前 root 的 `wiki_registry.yaml`。
5. 目标知识库必须是新知识库，`Wiki/Wiki_<新知识库>/` 不得已存在。
6. 本操作融合 `entity`、`relationship`、`conversation_entity` 和 `engineering_entity`。
7. 本操作不融合 `knowledge_graph`、`.registry/machine/knowledge_graph_registry.yaml` 或 `knowledge_graph/**`。
8. 本 operation 不修改 `Library/` 或 `Library/public_resources/`；目标 KB 产生的 resource usage 必须在当前 operation 内同步写入 `resource_registry.yaml/md`。
9. YAML 是机器权威表，Markdown 只是人类可读投影；发生冲突时以 YAML 为准。

## inspect：融合前审核

inspect 阶段只读，不得写入任何文件。

### 1. 解析输入

1. 解析来源知识库列表。
2. 去除空白项。
3. 精确匹配 `wiki_registry.yaml` 中的 `kb_name`。
4. 来源知识库少于 2 个时停止。
5. 任一来源知识库不存在或匹配多条时停止并列出候选。
6. 如果目标知识库名称已经登记，停止。
7. 如果 `Wiki/Wiki_<目标知识库名>/` 已存在，停止。
8. 如果用户请求“全部知识库”或“当前 root 全部知识库”，停止；必须显式列出来源知识库。

### 2. 读取来源范围

对每个来源知识库，只读读取：

- `.virtualDatabase/machine/local_resources.yaml`
- `.virtualDatabase/machine/required_resources.yaml`
- `.virtualDatabase/machine/excluded_resources.yaml`
- `.virtualDatabase/human/local_resources.md`
- `.virtualDatabase/human/required_resources.md`
- `.virtualDatabase/human/excluded_resources.md`
- `.registry/machine/entity_registry.yaml`
- `.registry/machine/entity_resource_map.yaml`
- `.registry/machine/relationship_registry.yaml`
- `.registry/machine/conversation_entity_registry.yaml`
- `.registry/machine/engineering_entity_registry.yaml`
- `entities/*.md`
- `relationships/machine/*.yaml`
- `relationships/human/*.md`
- `conversation_entities/*.md`
- `engineering_entities/*.md`

不得读取或写入来源知识库的 `knowledge_graph/**`。可读取 `resource_registry.yaml` 和 `resource_registry.md` 用于解析资源名称与资源是否存在，但本 operation 不得修改它们。

### 3. 审核 entity

从每个来源知识库的 `.registry/machine/entity_registry.yaml` 读取 entity 条目。

候选重复判断：

1. 先比较 `ingestion.resource_refs`。
2. 只有 `resource_id` 有交集的 entity 才进入自动重复候选。
3. 对候选读取 `content_file` 正文并对比内容。
4. `resource_id` 不同的 entity 默认不自动合并；除非用户在审核中明确指定。

每组重复候选生成 `entity_merge_decisions`。可选决策：

- `merge_content`：默认。生成一个新的目标 `ent_id`，合并 aliases、tags、`resource_refs`，整合正文，去除明显重复，保留冲突说明和来源追踪。
- `pick_one`：只迁移用户指定的来源 entity，其他候选不进入目标知识库，并写入报告。
- `append_content`：生成一个新的目标 `ent_id`，元数据合并去重，正文按来源知识库和来源 entity 分段直接拼接，不做语义改写。

不得为已经识别为重复候选的多个来源 entity 分配多个目标 entity。非重复 entity 逐个迁移并重新分配目标 `ent_id`。

inspect 阶段必须输出 `entity_id_map` 草案：

```text
<来源知识库>:<旧ent_id> -> <目标知识库>:<新ent_id 或 skipped>
```

### 4. 审核 conversation_entity

从每个来源知识库的 `.registry/machine/conversation_entity_registry.yaml` 读取 conversation entity。

候选重复判断键：

```text
canonical_label + scope + summary
```

每组候选生成 `conversation_merge_decisions`。可选决策：

- `merge_content`：默认。合并 aliases、tags、resource_conversations、summary、scope 和正文。
- `pick_one`：只迁移用户指定的来源 conversation_entity。
- `append_content`：按来源知识库和来源 conversation entity 分段拼接正文，不做语义改写。

目标 registry 中的 `related_entities` 必须通过 `entity_id_map` 重映射。引用未迁移对象时，省略该引用并写入报告。

### 5. 审核 engineering_entity

从每个来源知识库的 `.registry/machine/engineering_entity_registry.yaml` 读取 engineering entity。

候选重复判断键：

```text
canonical_label + scope + summary
```

每组候选生成 `engineering_merge_decisions`。可选决策：

- `merge_content`：默认。合并 aliases、tags、resource_refs、dependencies、summary、scope 和正文。
- `pick_one`：只迁移用户指定的来源 engineering_entity。
- `append_content`：按来源知识库和来源 engineering entity 分段拼接正文，不做语义改写。

目标 registry 中的 `related_entities`、`dependencies` 和仍然有效的 resource references 必须重映射或去重。引用未迁移对象时，省略该引用并写入报告。

### 6. 审核 relationship

relationship 必须在 entity 审核之后处理，因为 relationship 的 subject 和 object 建立在 entity 之上。

1. 使用 `entity_id_map` 草案重写每条 relationship 的 `subject_entity_id` 和 `object_entity_id`。
2. 如果 subject 或 object 没有进入目标知识库，该 relationship 不迁移，并写入跳过原因。
3. 重写后按以下键去重：

```text
subject_entity_id + object_entity_id + predicate.id + scope
```

4. 同键 relationship 合并为一条，evidence 合并去重。
5. subject、object、predicate 相同但 scope 不同时，保留为不同 relationship。
6. 输出 `relationship_fusion_plan`，列出新增、合并、跳过和待确认的 relationship。

### 7. 审核虚拟资料库

目标知识库只有一套全局虚拟资料表。

只读取 YAML 中 `membership_status: active` 的条目。

构造三个集合：

- 正向集合：所有来源知识库的 `local_resources.active` 和 `required_resources.active`。
- 证据集合：被迁移 entity、relationship、conversation_entity 或 engineering_entity 引用的资源。
- 排除集合：所有来源知识库的 `excluded_resources.active`。

目标写入规则草案：

- `required_resources`：所有来源知识库 active required 去重合并。
- `local_resources`：正向集合和证据集合去重合并。
- `excluded_resources`：只写入“只出现在排除集合，且没有出现在正向集合或证据集合中”的资源。

如果某个资源在一个来源知识库中被排除，但在另一个来源知识库中被使用，或者被迁移对象引用，则该资源不进入目标 `excluded_resources`。

必须输出 `excluded_but_used_resources`：

- `resource_id`
- 资源名称
- 哪些来源知识库排除了它
- 哪些来源知识库使用了它
- 哪些迁移对象引用了它
- 目标知识库最终放入哪张资料表

如果同一个来源知识库内部同时 active excluded 和 active local/required，报告为来源知识库资料表自相矛盾；不修复来源知识库；目标仍按正向集合和证据集合优先。

### 8. 输出 inspect 报告

输出 `fuse_kbs_inspect_report`，至少包含：

- 当前 root。
- 来源知识库名称和路径。
- 目标知识库名称和路径。
- 来源对象数量。
- entity 重复候选和默认决策。
- conversation_entity 重复候选和默认决策。
- engineering_entity 重复候选和默认决策。
- `relationship_fusion_plan`。
- 目标虚拟资料表草案。
- `excluded_but_used_resources`。
- 将写入的精确路径。
- 明确不会修改的来源知识库路径。
- 确认提示。

没有用户对本次 inspect 报告和融合计划的明确确认前，不得进入 fix。

## fix：确认后执行融合

只有用户明确确认 `fuse_kbs_inspect_report` 和 `fuse_kbs_plan` 后，才能执行本阶段。

### 1. 写入前复核

1. 重新读取 `wiki_registry.yaml`，确认来源知识库仍然存在。
2. 确认目标知识库名称仍未登记。
3. 确认 `Wiki/Wiki_<目标知识库名>/` 仍不存在。
4. 确认用户已完成所有 `merge_content`、`pick_one` 和 `append_content` 决策。
5. 确认 relationship 不依赖未完成的 entity 决策。

### 2. 创建目标知识库结构

按 `workflows/kb/create_kb.md` 的结构创建：

- `Wiki.md`
- `index.md`
- `log.md`
- `.virtualDatabase/machine/*.yaml`
- `.virtualDatabase/human/*.md`
- `.registry/machine/*.yaml`
- `.registry/human/*.md`
- `entities/`
- `relationships/machine/`
- `relationships/human/`
- `conversation_entities/`
- `engineering_entities/`

不创建或迁移 `knowledge_graph/**` 内容；只保留 create_kb 默认需要的空知识图谱 registry 和目录结构。

### 3. 写入目标 entity

1. 按确认后的 `entity_merge_decisions` 分配目标 `ent_id`。
2. 写入目标 `.registry/machine/entity_registry.yaml`。
3. 写入目标 `.registry/human/entity_registry.md`。
4. 写入目标 `entities/*.md` 正文。
5. 写入最终 `entity_id_map.yaml`。

### 4. 写入目标 conversation_entity

1. 按确认后的 `conversation_merge_decisions` 分配目标 `conv_ent_id`。
2. 重映射 `related_entities`。
3. 写入目标 `.registry/machine/conversation_entity_registry.yaml`。
4. 写入目标 `.registry/human/conversation_entity_registry.md`。
5. 写入目标 `conversation_entities/*.md`。
6. 写入最终 `conversation_id_map.yaml`。

### 5. 写入目标 engineering_entity

1. 按确认后的 `engineering_merge_decisions` 分配目标 `eng_ent_id`。
2. 重映射 `related_entities` 和 `dependencies`。
3. 写入目标 `.registry/machine/engineering_entity_registry.yaml`。
4. 写入目标 `.registry/human/engineering_entity_registry.md`。
5. 写入目标 `engineering_entities/*.md`。
6. 写入最终 `engineering_id_map.yaml`。

### 6. 写入目标 relationship

1. 使用最终 `entity_id_map` 重写 relationship。
2. 跳过 subject 或 object 未迁移的 relationship。
3. 按 `subject_entity_id + object_entity_id + predicate.id + scope` 去重。
4. 合并 evidence。
5. 写入 `relationships/machine/<predicate_id>.yaml`。
6. 写入 `relationships/human/<predicate_id>.md`。
7. 同步 `.registry/machine/relationship_registry.yaml` 和 `.registry/human/relationship_registry.md`。

### 7. 写入目标虚拟资料表

按 inspect 阶段确认的正向集合、证据集合和排除集合写入：

- `.virtualDatabase/machine/required_resources.yaml`
- `.virtualDatabase/human/required_resources.md`
- `.virtualDatabase/machine/local_resources.yaml`
- `.virtualDatabase/human/local_resources.md`
- `.virtualDatabase/machine/excluded_resources.yaml`
- `.virtualDatabase/human/excluded_resources.md`

`excluded_but_used_resources` 中的资源不得进入目标 `excluded_resources`。

### 8. 更新 root 知识库注册表

1. 在 `wiki_registry.yaml` 中新增目标知识库条目。
2. 同步更新 `wiki_registry.md`。
3. 不启动目标知识库，除非用户另行请求启动。

### 9. 写入审计目录

在目标知识库中写入：

```text
Wiki/Wiki_<目标知识库名>/.valhalla/imports/kb_fusion_<timestamp>/
  source_kbs.yaml
  fuse_kbs_plan.yaml
  entity_id_map.yaml
  conversation_id_map.yaml
  engineering_id_map.yaml
  relationship_fusion_plan.yaml
  excluded_but_used_resources.yaml
  execution_report.yaml
```

审计文件必须足以回答：

- 每个目标 entity、conversation_entity、engineering_entity 来自哪些来源对象。
- 每条目标 relationship 来自哪些来源 relationship。
- 哪些来源对象被 `pick_one` 跳过。
- 哪些资源原本被排除但在目标知识库中被使用。
- 哪些来源知识库保持只读。

### 10. 验证

写入后必须验证：

1. 目标知识库登记在 `wiki_registry.yaml` 和 `wiki_registry.md` 中。
2. 目标 registry 只包含目标 ID。
3. 每条 relationship 的 subject 和 object 都存在于目标 entity registry。
4. relationship registry 计数与 fact 文件一致。
5. conversation 和 engineering registry 的 `id_policy.next_id` 正确。
6. 虚拟资料表只引用当前 root `resource_registry.yaml` 中存在的 `resource_id`。
7. `excluded_but_used_resources.yaml` 与目标虚拟资料表结果一致。
8. 来源知识库文件未被修改。

9. 在当前 `fuse_kbs` operation 内，从当前 root 已登记 active KB 的 `.registry/machine/entity_resource_map.yaml` 与 `.registry/machine/entity_registry.yaml` 重建 `resource_registry.yaml/md` usage。
10. `usage.referenced_by` 只能写入 `kb_name`、`entity_id`、`entity_file` canonical 条目；`entity_file` 必须是 `Wiki/Wiki_<知识库名>/<content_file>`；`reference_count` 按唯一 `(kb_name, entity_id)` 计数；不得写入 legacy usage，包括字符串路径、`entities/` 相对路径和旧 `kb` 字段格式。
11. 同一操作内同步 `resource_registry.md`，以 `resource_registry.yaml` 为唯一事实来源刷新引用数量投影。

输出 `fuse_kbs_report`。

## 失败与中止

- inspect 阶段失败时，不写入任何文件。
- 用户未确认 inspect 报告时，不进入 fix。
- 去重决策不完整时，不进入 fix。
- relationship 依赖未完成 entity 决策时，不进入 fix。
- fix 阶段写入失败时，不回滚或修改来源知识库；必须报告目标路径、已写入文件、失败步骤、目标 registry 是否已写入和验证状态。

## 输出

- `fuse_kbs_inspect_report`：融合前审核报告。
- `fuse_kbs_plan`：确认前融合计划。
- `entity_merge_decisions`：entity 去重决策。
- `conversation_merge_decisions`：conversation_entity 去重决策。
- `engineering_merge_decisions`：engineering_entity 去重决策。
- `relationship_fusion_plan`：relationship 重写、合并和跳过计划。
- `excluded_but_used_resources`：原本被排除但目标知识库继续使用的资源清单。
- `fuse_kbs_report`：融合完成报告。
- `target_kb`：目标知识库名称和路径。
- `next_operation`：目标知识库登记且 usage 同步完成后为 `null`。
- `modified_files`：实际写入文件。
- `current_state`：当前 root、`os_status` 与 `kb_status`。

## 禁止行为

- 不得支持“融合当前 root 全部知识库”。
- 不得把 root 融合逻辑复用于知识库融合。
- 不得修改来源知识库。
- 不得删除来源知识库。
- 不得修改 `resource_registry.yaml` 或 `resource_registry.md` 的资源身份、表现文件、生命周期和 policy 字段；只能同步 usage 派生字段。
- 不得修改 `Library/` 或 `Library/public_resources/`。
- 不得迁移或融合知识图谱事实。
- 不得在知识库已激活时执行。
- 不得把用户对 inspect 的确认解释为删除、清理、启动知识库或修改来源知识库的授权。
