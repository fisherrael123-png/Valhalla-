# ingest_conversation

## 目的

将本次会话内容沉淀为 conversation entity，并登记到当前知识库的 `conversation_entity_registry.yaml` 中。

本 workflow 只负责执行摄入流程。  
权限、状态约束、前置条件和输出要求由 `ingest_conversation_contract.yaml` 负责。

## 输入

- 当前 Valhalla root
- 当前目标知识库
- 本次会话内容
- `Wiki/Wiki_<知识库名>/.registry/machine/conversation_entity_registry.yaml`
- `Wiki/Wiki_<知识库名>/conversation_entities/`

## 输出

- `ingest_conversation_report`
- `target_kb`

## 流程

1. 定位当前知识库目录

   进入：

   ```text
   Wiki/Wiki_<知识库名>/
    ```

2. 确认或创建 registry

   如果不存在：

   ```text
   conversation_entity_registry.yaml
   ```

   则按照：

   ```text
   template\knowledge_base\conversation\conversation_entity_registry_template.yaml
   template\knowledge_base\conversation\conversation_entity_registry_entry_template.yaml
   ```

   创建初始文件。

3. 提取本次会话主题

   从本次会话中提取：

   - 主要讨论对象
   - 可沉淀的知识点
   - 用户最终确认的设计决策
   - 需要长期保留的概念、结构、命名或规则

4. 匹配既有 conversation entity

   在 `conversation_entity_registry.yaml` 中查找：

   - `canonical_label`
   - `aliases`
   - `scope`
   - `summary`

   如果本次会话主题与既有实体一致，则复用原 `id`。
   不得为同一对话主题重复创建新实体。

5. 创建或更新 conversation entity

   如果是新实体：

   - 分配新的 `conv_ent_000001` 格式 ID
   - 在 `conversation_entity_registry.yaml` 中新增条目
   - 创建对应正文文件：

     ```text
     conversation_entities/conv_ent_000001_<对话实体名称>.md
     ```

   如果是既有实体：

   - 保持原 `id`
   - 更新 `updated_at`
   - 扩展 `resource_conversations`
   - 扩展或修订对应正文文件

6. 写入 conversation entity 正文文件

   正文文件至少包含：

   ```markdown
   # <对话实体名称>

   ## 简述

   ## 本次新增内容

   ## 已确认设计

   ## 待定问题

   ## 来源会话
   ```

7. 更新 registry

   更新：

   - `updated_at`
   - 对应 entity 的 `updated_at`
   - `resource_conversations`
   - `summary`
   - `scope`
   - `related_entities`
   - `tags`

   不得修改：

   - `.registry/machine/entity_registry.yaml`
   - `engineering_entity_registry.yaml`
   - `.registry/machine/relationship_registry.yaml`
   - `.registry/machine/knowledge_graph_registry.yaml`
   - 三张资料表

8. 追加日志

   在 `log.md` 追加：

   ```markdown
   ## [YYYY-MM-DD] ingest_conversation | <知识库名>

   - 写入或更新 conversation entity：<conv_ent_id> <canonical_label>
   - 正文文件：<content_file>
   ```

9. 输出报告

   输出 `ingest_conversation_report`，包含：

   ```yaml
   operation: ingest_conversation
   target_kb: <知识库名>
   created_entities:
     - <conv_ent_id>
   updated_entities:
     - <conv_ent_id>
   content_files:
     - conversation_entities/<文件名>.md
   registry: conversation_entity_registry.yaml
   status: success
    ```



