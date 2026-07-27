# edit_knowledge_graph workflow

## 目的

根据用户确认的图谱需求，基于已有 entity fact 和 relationship fact 生成或修改 graph fact。

Graph fact 是使用者确认后的图事实：它记录用户决定把哪些关系类型、关系事实和实体组织为一张图。Graph fact 只能组合、筛选、确认已有 relationship fact，不得创建或修改 entity fact 或 relationship fact。

机器 YAML 是权威数据，human Markdown 是人类可读审阅投影；Markdown 不得反向覆盖 YAML。

## 工作流程

### 1. 确定图谱需求

根据用户请求确定 graph fact 的目的、名称、关系类型范围和选择规则。例如：用户决定制作一张由 A、B、C 三种类型关系组成的图。

用户未明确确认图谱范围时，只输出待确认问题，不写入 graph fact。

### 2. 定位当前知识库

确认以下路径：

- `Wiki/Wiki_<知识库名>/.registry/machine/entity_registry.yaml`
- `Wiki/Wiki_<知识库名>/.registry/machine/relationship_registry.yaml`
- `Wiki/Wiki_<知识库名>/.registry/human/relationship_registry.md`
- `Wiki/Wiki_<知识库名>/relationships/machine/*.yaml`
- `Wiki/Wiki_<知识库名>/relationships/human/*.md`
- `Wiki/Wiki_<知识库名>/.registry/machine/knowledge_graph_registry.yaml`
- `Wiki/Wiki_<知识库名>/.registry/human/knowledge_graph_registry.md`
- `Wiki/Wiki_<知识库名>/knowledge_graph/machine/`
- `Wiki/Wiki_<知识库名>/knowledge_graph/human/`

缺少 `knowledge_graph/machine/` 或 `knowledge_graph/human/` 时可以创建。缺少图谱登记表时可用对应模板初始化。

### 3. 读取事实来源

- `.registry/machine/entity_registry.yaml` 是节点事实来源。
- `.registry/machine/relationship_registry.yaml` 是 relationship fact 文件索引。
- `relationships/machine/<predicate_id>.yaml` 是对应关系类型下的边事实来源。

Graph fact 必须引用已存在的 `entity_id` 和 `relationship_id`。不得创建或修改关系事实，也不得把 graph fact 文件当作第二份关系注册表。

### 4. 创建或修改 graph fact

机器权威文件位于 `knowledge_graph/machine/<graph_id>.yaml`，使用：

`template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.yaml`

人类审阅投影位于 `knowledge_graph/human/<graph_id>.md`，使用：

`template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.md`

Graph fact 至少记录：

- `graph_id`、名称、目的、状态、创建者和更新时间；
- 用户确认的 `relationship_sources`；
- `included_relationships`；
- `included_entities`；
- `selection_rule`；
- `layout` 和展示说明；
- `provenance.authority_note`。

### 5. 一致性校验

写入前检查：

- `graph_id`、machine 路径和 human 路径唯一；
- graph registry 登记项与 graph fact 文件的 `graph_id` 一致；
- `relationship_sources` 中的每个 `predicate_id` 存在于 `.registry/machine/relationship_registry.yaml`；
- `relationship_sources.fact_file` 指向存在的 `relationships/machine/<predicate_id>.yaml`；
- `included_relationships` 全部存在于对应 relationship fact 文件；
- `included_entities` 全部存在于 `.registry/machine/entity_registry.yaml`；
- `included_entities` 与 `included_relationships` 的 subject/object entity 至少一致，不得遗漏已纳入边的端点；
- graph fact 没有混入新的 entity 或 relationship 事实。

校验失败时不得发布修改，并在报告中说明。

### 6. 同步 registry 与 human 投影

创建或修改 graph fact 时，同步写入：

- `knowledge_graph/machine/<graph_id>.yaml`
- `knowledge_graph/human/<graph_id>.md`
- `.registry/machine/knowledge_graph_registry.yaml`
- `.registry/human/knowledge_graph_registry.md`

`.registry/machine/knowledge_graph_registry.yaml` 只索引 graph fact，不保存完整节点和边事实。

`.registry/human/knowledge_graph_registry.md` 和 `knowledge_graph/human/<graph_id>.md` 是人类可读审阅投影，不得反向覆盖 YAML。

### 7. 输出

输出 `edit_knowledge_graph_report`，包含操作类型、目标知识库、创建或修改的 `graph_id`、用户确认的关系类型、包含的 relationship/entity 数量、修改文件、使用的 relationship fact 文件、跳过内容和待确认问题。

## 约束

- `.registry/machine/knowledge_graph_registry.yaml` 是 graph fact 索引层。
- `knowledge_graph/machine/*.yaml` 是 graph fact 机器权威层。
- `knowledge_graph/human/*.md` 是 graph fact 人类审阅投影。
- `.registry/machine/entity_registry.yaml` 是节点事实层。
- `relationships/machine/*.yaml` 是关系事实层。
- Graph fact 不得创建或修改关系事实。
- 不得修改资料表、实体注册表、实体正文、relationship registry 或 relationship fact 文件。