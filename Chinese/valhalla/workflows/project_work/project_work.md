# project_work workflow

## 目的

使用指定知识库推进一个具体项目任务，例如论文、代码、实验、综述、方案、报告或工程实现。

本 workflow 只负责项目产出，不直接维护知识库底层注册表。  
若发现需要新增实体、扩展实体、修正关系或补充工程总结，应在报告中提出后续操作建议。

## 写入边界

- 读取知识库不等于获得修改知识库的权限。
- 不修改 Wiki、资料表、资源注册表、实体、关系、知识图谱、对话实体或工程实体。
- 只修改用户明确指定的项目文件，以及完成这些目标文件所必需的配套文件。
- 用户没有指定目标路径时，默认只在回复中生成项目产物。
- 如需创建或修改未明确指定的文件，先列出拟写入的精确路径并获得用户确认。
- 若项目结果值得沉淀，只在报告中建议调用 `ingest_conversation` 或 `ingest_engineering`，不得在本 workflow 中直接写回知识库。

## 流程

1. 确认使用哪些知识
   根据 `project_goal` 检索并读取相关内容：

   * `.registry/machine/entity_registry.yaml`
   * `.registry/human/entity_registry.md`
   * `entities/`
   * `.registry/machine/entity_resource_map.yaml`
   * `.registry/human/entity_resource_map.md`
   * `.registry/machine/relationship_registry.yaml`
   * `.registry/human/relationship_registry.md`
   * `.registry/machine/knowledge_graph_registry.yaml`
   * `.registry/human/knowledge_graph_registry.md`
   * `knowledge_graph/`
   * `.registry/machine/conversation_entity_registry.yaml`
   * `.registry/human/conversation_entity_registry.md`
   * `conversation_entities/`
   * `.registry/machine/engineering_entity_registry.yaml`
   * `.registry/human/engineering_entity_registry.md`
   * `engineering_entities/`
   * 有效资料范围内的公共资料副本

   有效资料范围必须从三张 YAML 机器资料表计算：

   ```text
   (.virtualDatabase/machine/local_resources.yaml 中 active 的 resource_id
   ∪ .virtualDatabase/machine/required_resources.yaml 中 active 的 resource_id)
   - .virtualDatabase/machine/excluded_resources.yaml 中 active 的 resource_id
   - 全局黑名单中的 resource_id
   ```

   同名 Markdown 资料表只用于人类查看，不作为成员身份判断依据。

2. 建立项目工作上下文

    整理本次项目的工作上下文，至少包括：

    * 项目目标；
    * 项目类型；
    * 已知背景；
    * 可用资料；
    * 关键实体；
    * 关键关系；
    * 已有工程总结或对话总结；
    * 用户约束；
    * 当前缺口；
    * 本次可完成的范围。

    如果发现资料不足，不要伪造内容,询问是否搜索网络资料进行补充。

3. 根据这些知识制定项目推进计划

    示例：

    论文任务：

    * 明确论点；
    * 整理论据；
    * 搭建章节结构；
    * 补充引用；
    * 生成或修改正文。

    代码任务：

    * 明确功能目标；
    * 确认相关工程实体；
    * 定位目标文件；
    * 设计修改方案；
    * 生成补丁或代码说明。

    实验任务：

    * 明确实验问题；
    * 整理变量与对照；
    * 设计实验流程；
    * 规划记录方式；
    * 输出实验方案或分析模板。

    报告或综述任务：

    * 明确主题；
    * 聚合相关实体；
    * 整理资料脉络；
    * 形成结构化草稿；
    * 标注来源和不确定点。

4. 审核项目推进计划。如果有缺陷，返回上一步根据审核意见修改。`制定计划-审核计划`循环不得超过 5 次；超过 5 次时停止并询问用户。
5. 根据项目推进计划生成或修改项目产物。写入前再次核对目标路径和知识库只读边界。
6. 输出 `project_work_report`。

## project_work_report

报告至少包括：

- `project_goal`：本次项目目标。
- `completion_status`：完成、部分完成或阻塞。
- `target_kb`：本次使用的知识库。
- `knowledge_used`：使用的关键知识，包括相关 `entity_id`。
- `source_records`：来源记录，优先按 `resource_id -> entity_id -> 支持的结论或产物` 表示。
- `created_files`：本次创建的文件；没有则明确写“无”。
- `modified_files`：本次修改的文件；没有则明确写“无”。
- `unresolved_questions`：仍未解决的问题、证据缺口和不确定项。
- `suggested_knowledge_writeback`：建议后续沉淀的知识，以及建议使用的摄入操作；没有则明确写“无”。

不得只记录文件名作为来源。存在稳定身份时，必须记录 `resource_id` 和相关 `entity_id`。



