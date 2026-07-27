# relate_entities workflow

## 目的

总结、整理当前知识库中已有 entity 之间的关系，并将确认后的具体关系事实写入按 `predicate.id` 分组的 relationship fact 文件。

relationship fact 是实体之间的边事实；`.registry/machine/relationship_registry.yaml` 只索引 relationship fact 文件，不承载完整关系事实。

机器 YAML 是权威数据，human Markdown 是人类可读审阅投影；Markdown 不得反向覆盖 YAML。

## 输入

- 用户提出的关系整理请求。
- 当前知识库的 `.registry/machine/entity_registry.yaml`。
- 当前知识库的 `.registry/machine/entity_resource_map.yaml`。
- 当前知识库的 `.registry/machine/relationship_registry.yaml`。
- 当前知识库的 `.registry/human/relationship_registry.md`。
- 相关 entity 指向的内容文件。
- 必要时读取有效虚拟资料库中的来源资料。

## 工作流程

### 1. 确定范围

根据用户请求确定 entity 范围。用户未指定范围时，整理当前知识库中已有 entity 之间证据明确的显著关系。

不得凭空创建不存在的 entity。

### 2. 读取实体与证据

读取 `.registry/machine/entity_registry.yaml`，确认相关 entity 的：

- `entity_id`
- 名称和别名
- 类型和状态
- 内容文件路径
- `ingestion.resource_refs`

读取相关 entity 正文和 `.registry/machine/entity_resource_map.yaml`，建立可追溯证据链。必要时读取对应公共表现文件，但不得将文件路径写入关系事实作为稳定身份。

### 3. 形成候选关系

每条候选关系至少包含：

- `subject_entity_id`：主体 entity；
- `object_entity_id`：客体 entity；
- `predicate`：谓词 ID、英文名、中文名、方向、层级和机制；
- `description`：关系说明；
- `confidence` 和可选 `weight`；
- `evidence.resource_refs`；
- `evidence.entity_resource_map_refs`；
- `evidence.evidence_note`；
- `scope`：适用范围、条件和限制。

不得仅凭名称相似建立关系，不得把资料文件、章节或资源作为关系节点。

### 4. 按 predicate 定位 relationship fact 文件

以 `predicate.id` 为分组键定位或创建：

- `relationships/machine/<predicate_id>.yaml`
- `relationships/human/<predicate_id>.md`

使用：

- fact 文件模板：`template/knowledge_base/relationship/relationship_fact_file_template.yaml`
- human fact 投影模板：`template/knowledge_base/relationship/relationship_fact_file_template.md`
- fact Schema：`schema/relationship_fact_file_schema.json`

同一个 fact 文件内所有 relationship 的 `predicate.id` 必须与文件级 `predicate_id` 一致。

### 5. 检查既有关系

以 `subject_entity_id + object_entity_id + predicate.id + scope` 作为语义去重键，在对应 `relationships/machine/<predicate_id>.yaml` 中检查：

- 已存在同一关系时，只补充证据、说明、范围或更新时间；
- 方向相反且谓词有方向性时，不得自动视为同一关系；
- 证据冲突或范围不一致时，保留候选并在报告中要求确认；
- 不得重复登记同一关系事实。

### 6. 写入 relationship fact 与投影

为新关系分配唯一 `relationship_id`，将新增或更新后的完整事实写入对应 `relationships/machine/<predicate_id>.yaml`。

同步更新对应 `relationships/human/<predicate_id>.md`，供人类审阅该类型下的关系事实。

同步更新：

- `.registry/machine/relationship_registry.yaml`
- `.registry/human/relationship_registry.md`

`.registry/machine/relationship_registry.yaml` 只登记 `predicate_id`、名称、machine fact 文件路径、human fact 文件路径、关系数量、状态和更新时间。

写入前必须确认主体和客体均存在于当前 `.registry/machine/entity_registry.yaml`，所有 `resource_id` 和 `entity_resource_map` 引用均存在。

本 operation 不调用 `edit_knowledge_graph`，不写入 `.registry/machine/knowledge_graph_registry.yaml`、`.registry/human/knowledge_graph_registry.md` 或 `knowledge_graph/**`。用户后续要求创建或更新图谱 fact 时，必须返回 Router，单独校验并确认 `edit_knowledge_graph`。

### 7. 输出报告

输出 `relate_entities_report`，至少包含：

- 本次读取的 entity 数量；
- 新增、更新和跳过的关系数量；
- 每条关系的 `relationship_id`、主体、客体和谓词；
- 影响的 `relationships/machine/<predicate_id>.yaml` 与 `relationships/human/<predicate_id>.md`；
- 同步更新的 relationship registry machine/human 文件；
- 证据引用；
- 跳过原因和待确认问题；
- 是否建议后续单独执行 `edit_knowledge_graph`。

## 约束

- 不得修改 `.registry/machine/entity_registry.yaml` 或 `.registry/human/entity_registry.md`。
- 不得新建 entity。
- 不得修改资料表、资源注册表或实体正文。
- 不得写入知识图谱 registry 或 graph fact 文件。
- 关系节点只能是当前 `.registry/machine/entity_registry.yaml` 中存在的 entity。
- 所有关系必须能追溯到 entity 内容文件或来源资料。
- 不确定的关系只能写入报告中的候选关系部分。