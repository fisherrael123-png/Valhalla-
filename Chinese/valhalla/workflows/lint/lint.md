# lint workflow

## 阶段一：检查

### 1. 解析目标

根据 `scope` 定位检查目标：

* `current_kb`：读取当前状态，定位当前知识库。
* `named_kb`：定位 `Wiki/Wiki_<kb_name>/`。
* `all_kbs`：枚举 `Wiki/Wiki_*/`。
* `root`：检查当前 Valhalla root。
* `file`：检查 `target_path` 及其直接引用。

目标不明确时，只读探测，不写入。

### 2. 检查

检查root
检查知识库，模板规则见`schema`

### 3. 深度检查

若 `depth = deep`，额外检查：

* 重复实体候选。
* 孤儿资源。即已经登记在 `resource_registry.yaml` 中，但 `usage.reference_count = 0`，本 root 下的 `orphan_resources.md` 记录对应 `resource_id`。
* 资料表是否只包含有效 `resource_id`，不得包含来源副本或公共副本路径。
* 来源副本是否全部位于当前 root 的 `Library/` 非公共目录。
* 公共副本是否位于 `Library/public_resources/<resource_id>/`。
* 每个资源是否只有一个主名称，附属名称是否重复。
* 每个资源是否至少有一个 `authoritative` 表现文件。
* 黑名单条目是否绑定有效 `resource_id`，以及资源层黑名单投影是否一致。
* `resource_registry.yaml` 与 `resource_registry.md` 是否成对存在。
* `resource_registry.md` 中的资源、表现文件、当前路径、同步状态、引用数量和黑名单状态是否与 YAML 一致。
* 三张 YAML 机器资料表是否都有同名 Markdown 人类投影。
* YAML 与 Markdown 中的 `resource_id`、成员状态和加入时输入是否一致。
* 同一张 YAML 资料表中是否重复登记同一个 `resource_id`。
* Markdown 中的主名称、当前来源路径、类型和版本是否与 `resource_registry.yaml` 一致。
* `pending_removal` 条目是否已经退出有效资料库，并等待批量物理清理。
* 有来源但无正文的实体。
* 有正文但无来源的实体。
* 正文引用与 resource map 不一致。
* relationship 中的 registry 外 entity。
* graph 中的 registry 外节点或边。
* index 遗漏已有文件入口。
* 多知识库之间的资料状态冲突。

深度检查中的语义判断问题只报告，不自动修复。

### 3.1 缺失 entity context 检查

当 `depth = deep` 且目标是当前知识库或指定知识库时，必须检查普通 entity 注册表：

1. 读取目标知识库的 `.registry/machine/entity_registry.yaml`。
2. 对每个 entity 读取 `content_file`。
3. `content_file` 必须是相对于知识库目录的 `entities/` 路径，不得是绝对路径，不得包含 `..`。
4. 如果 `content_file` 合法但目标正文文件不存在，输出 `missing_entity_content_file` 问题。
5. 每个问题必须包含：
   - `issue_id`：`missing_entity_content_file:<entity_id>`；
   - `issue_type`：`missing_entity_content_file`；
   - `entity_id`、`canonical_name`、`content_file`；
   - 缺失正文的绝对预期路径；
   - `fixable: true`；
   - `requires_confirmation: false`；
   - `affected_paths`：
     - `.registry/machine/entity_registry.yaml`
     - `.registry/human/entity_registry.md`
     - `.registry/machine/entity_resource_map.yaml`
     - `.registry/human/entity_resource_map.md`

该检查不读取或改写缺失正文内容，不猜测缺失 entity context。

### 4. 输出 lint_report

每个问题必须包含唯一 `issue_id`，并标记：

- `fixable`：是否允许自动修复；
- `requires_confirmation`：是否需要单独确认；
- `affected_paths`：可能修改的精确路径。

同时输出 `fixable_issue_ids`，供确认后的 fix phase 选择。未进入本次 `lint_report` 的问题不得在 fix phase 中处理。

---

## 阶段二：确认后修复

### 1. 进入条件

只有用户在看到 `lint_report` 后明确确认，才进入修复阶段。

如果用户选择部分修复，只修复指定问题。

### 2. 修复前筛选

只修复同时满足以下条件的问题：

* 已在本次 `lint_report` 中列出。
* 用户已确认。
* 不涉及删除、移动、合并、拆分或正文改写。
* 不改变资料有效范围。
* 不改变实体、关系、图谱语义。
* 不修改 resource_registry 的资料身份。

### 3. 生成修复计划

高风险修复：

* 删除文件。
* 移动文件。
* 合并实体。
* 拆分实体。
* 重写正文。
* 总结资料内容。
* 修改资料表收录范围。
* 修改剔除资料表语义内容。
* 修改 resource_registry 资料身份。
* 判断资料真伪。
* 判断资料是否应进入黑名单。
* 修改知识图谱语义关系。
* 改变 relationship 方向。
* 改变 entity_id、relationship_id 或 graph_id。
* 推断缺失来源。
* 判断两个实体是否同义。

这些问题只能进入人工确认才能被列入修复计划。

### 4. 执行修复

对每个修复项：

1. 读取目标文件当前内容。
2. 记录修改前状态。
3. 执行单项修复。
4. 写回文件。
5. 立即验证。
6. 若失败，尝试回滚。
7. 记录结果。

一项失败不得扩大修改范围。

### 4.1 资料表批量整理

只有用户在 lint_report 后确认修复，才执行以下批量操作：

1. 汇总三张 YAML 资料表中的所有 `pending_removal` 条目。
2. 确认这些条目已经不参与任何有效资料库计算。
3. 从 YAML 机器表中物理移除这些墓碑条目。
4. 从同名 Markdown 中删除对应“待清理”行。
5. 根据剩余 YAML active 条目批量核对 Markdown：
   - 补齐缺失行；
   - 移除没有 YAML 成员的孤立行；
   - 保留 YAML 中的“加入时输入”；
   - 从 `resource_registry.yaml` 刷新主名称、当前来源路径、类型和版本；
   - 同步成员状态、加入时间、删除标记时间和备注。
6. 更新 Markdown 的 active 数量、待清理数量和最后更新时间。
7. 更新 YAML 的 `updated_at`。
8. 如果发现同一 YAML 中有重复 `resource_id`，只报告冲突；除非能够证明条目审计信息一致且用户确认，否则不得自动合并。

该批量整理只清理资料表成员墓碑和投影视图，不删除任何资料文件、公共副本、`resource_id` 或 Resource Registry 条目。

### 4.2 resource_registry.md 批量同步

只有用户在 lint_report 后确认修复，才执行：

1. 以 `resource_registry.yaml` 为唯一事实来源。
2. 补齐 Markdown 缺失的资源摘要和表现文件行。
3. 删除 Markdown 中不存在于 YAML 的孤立行。
4. 刷新主名称、附属名称、类型、版本、生命周期、引用数量和黑名单状态。
5. 刷新来源副本、公共副本、表现类型、格式和同步状态。
6. 更新资源数量和最后更新时间。
7. 如果 Markdown 缺失或结构严重损坏，根据 YAML 完整重建。

不得从 Markdown 反向覆盖 YAML。
不得在本步骤重建或改写 `resource_registry.yaml` 的 `usage.referenced_by`、`usage.reference_count` 或 `usage.computed_at`；只有会改变 entity-resource 映射的修复步骤才能同步重建 usage。

### 4.3 缺失 entity context 登记清理

只有用户在 `lint_report` 后确认修复 `missing_entity_content_file`，才执行本清理。

对每个已确认的 `missing_entity_content_file:<entity_id>`：

1. 重新读取目标知识库的 `.registry/machine/entity_registry.yaml`。
2. 确认该 issue 已在本次 `lint_report` 中列出，且 `fixable: true`、`requires_confirmation: false`。
3. 从 `.registry/machine/entity_registry.yaml` 删除该 `entity_id` 的 entity 条目。
4. 从 `.registry/machine/entity_resource_map.yaml` 删除所有指向该 `entity_id` 的映射。
5. 根据更新后的 YAML 重建：
   - `.registry/human/entity_registry.md`
   - `.registry/human/entity_resource_map.md`
6. 在当前 `lint` operation 内，以当前 root 的已登记 active 知识库为范围，重新读取每个知识库的 `.registry/machine/entity_registry.yaml` 和 `.registry/machine/entity_resource_map.yaml`，以 `entity_resource_map.yaml` 为 entity-resource 证据映射权威重建 `resource_registry.yaml/md` usage。
7. `usage.referenced_by` 只能写入 `kb_name`、`entity_id`、`entity_file` canonical 条目；`entity_file` 必须是 `Wiki/Wiki_<知识库名>/<content_file>`；`reference_count` 按唯一 `(kb_name, entity_id)` 计数；不得写入 legacy usage，包括字符串路径、`entities/` 相对路径和旧 `kb` 字段格式。
8. 同一操作内同步 `resource_registry.md`，以 `resource_registry.yaml` 为唯一事实来源刷新引用数量投影。
9. 输出移除的 `entity_id`、移除的 `map_id`、保留但缺失的原正文路径、修改文件列表和 `next_operation: null`。

本清理不得：

* 删除、移动或重命名 `entities/` 下的任何文件。
* 修改 `resource_registry.yaml` 或 `resource_registry.md` 的非 usage 字段。
* 修改资料表、relationship、knowledge graph、conversation entity 或 engineering entity。
* 重新生成、补写或总结缺失的 entity context。

### 5. 修复后复检

对被修改文件执行最小复检：

* 文件是否存在。
* YAML 是否可解析。
* Markdown 链接是否可解析。
* registry 是否仍能找到对应文件。
* 三张 YAML 与三张 Markdown 是否成对存在。
* 如果修复改变了 entity-resource 映射，则必须确认 `resource_registry.yaml/md` usage 已同步完成。
* YAML active 成员集合是否与 Markdown active 行一致。
* 是否已清除本次确认范围内的全部 `pending_removal` 条目。
* 本次确认的 `missing_entity_content_file` 是否已经从 entity registry 和 entity resource map 中清除。
* entity_resource_map 中是否仍存在指向已删除 entity_id 的映射。
* 保留的 entity_resource_map 与 entity_registry 是否足以重建 resource usage。
* 原问题是否消失。
* 是否产生新的直接错误。

### 5. 输出 lint_fix_report



