# 新建知识库

## 输入

- 知识库名称。

## 创建结构

在当前 Valhalla root 下创建：

```text
Wiki/Wiki_<知识库名>/
    Wiki.md
    index.md
    log.md
    .virtualDatabase/
        machine/
            local_resources.yaml
            required_resources.yaml
            excluded_resources.yaml
        human/
            local_resources.md
            required_resources.md
            excluded_resources.md
    .registry/
        machine/
            entity_registry.yaml
            entity_resource_map.yaml
            relationship_registry.yaml
            knowledge_graph_registry.yaml
            conversation_entity_registry.yaml
            engineering_entity_registry.yaml
        human/
            entity_registry.md
            entity_resource_map.md
            relationship_registry.md
            knowledge_graph_registry.md
            conversation_entity_registry.md
            engineering_entity_registry.md
    entities/
    relationships/
        machine/
        human/
    knowledge_graph/
        machine/
        human/
    conversation_entities/
    engineering_entities/
```

## 初始化

- `Wiki.md`：写入知识库名称、用途、当前范围和入口链接。
- `index.md`：创建资料来源、实体、概念、问题和综合报告等空栏目。
- `log.md`：追加 `## [YYYY-MM-DD] create | <知识库名>`。
- 三张机器资料表写入 `.virtualDatabase/machine/`：`.virtualDatabase/machine/local_resources.yaml`、`.virtualDatabase/machine/required_resources.yaml`、`.virtualDatabase/machine/excluded_resources.yaml`。使用 `template/knowledge_base/resource_table_registry_template.yaml` 初始化，分别设置表名和用途。它们是机器权威成员表。
- 三张人类资料表写入 `.virtualDatabase/human/`：`.virtualDatabase/human/local_resources.md`、`.virtualDatabase/human/required_resources.md`、`.virtualDatabase/human/excluded_resources.md`。使用 `template/knowledge_base/resource_table_template.md` 初始化。它们是人类可读投影视图。
- `.registry/machine/entity_registry.yaml`：使用 `template/knowledge_base/entity/entity_registry_template.yaml` 创建空实体注册表。
- `.registry/human/entity_registry.md`：使用 `template/knowledge_base/entity/entity_registry_template.md` 创建人类可读摘要骨架，链接回 `.registry/machine/entity_registry.yaml`。
- `.registry/machine/entity_resource_map.yaml`：使用 `template/resource/entity_resource_map_template.yaml` 初始化。
- `.registry/human/entity_resource_map.md`：使用 `template/resource/entity_resource_map_template.md` 初始化。
- `.registry/machine/relationship_registry.yaml`：使用 `template/knowledge_base/relationship/relationship_registry_template.yaml` 初始化为空的 relationship fact 文件索引。
- `.registry/human/relationship_registry.md`：使用 `template/knowledge_base/relationship/relationship_registry_template.md` 初始化为空的人类可读 relationship fact 索引。
- `relationships/machine/`：存储按 `predicate_id` 分组的 relationship fact YAML 文件，使用 `template/knowledge_base/relationship/relationship_fact_file_template.yaml`。
- `relationships/human/`：存储对应 relationship fact 的人类可读 Markdown 投影，使用 `template/knowledge_base/relationship/relationship_fact_file_template.md`。
- `.registry/machine/knowledge_graph_registry.yaml`：使用 `template/knowledge_base/knowledge_graph/knowledge_graph_registry_template.yaml` 初始化为空的 graph fact 索引。
- `.registry/human/knowledge_graph_registry.md`：使用 `template/knowledge_base/knowledge_graph/knowledge_graph_registry_template.md` 初始化为空的人类可读 graph fact 索引。
- `knowledge_graph/machine/`：存储使用者确认后的 graph fact YAML 文件，使用 `template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.yaml`。
- `knowledge_graph/human/`：存储对应 graph fact 的人类可读 Markdown 投影，使用 `template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.md`。
- `.registry/machine/conversation_entity_registry.yaml` 和 `.registry/human/conversation_entity_registry.md`：使用 conversation entity 注册表模板初始化。
- `.registry/machine/engineering_entity_registry.yaml` 和 `.registry/human/engineering_entity_registry.md`：使用 engineering entity 注册表模板初始化；空注册表的 `entities` 必须为 `[]`。
- `entities/`、`conversation_entities/`、`engineering_entities/`：存储对应实体正文。
- 在当前 root 的 `wiki_registry.yaml` 中新增或更新条目：`kb_name`、`wiki_path: Wiki/Wiki_<知识库名>`、`status: active`、`created_at`、`updated_at`、`description`。
- 同步更新 `wiki_registry.md` 人类可读投影；发生冲突时以 `wiki_registry.yaml` 为准。

资料表、注册表、relationship fact 和 graph fact 的机器 YAML 与人类 Markdown 必须成对创建或同步。有效资料库只读取 YAML 中 `membership_status: active` 的条目。所有 Markdown 只是人类可读投影，不得反向覆盖 YAML。

除非用户明确要求“新建并启动”，否则不要启动该知识库。