# workflows/kb/ingest_engineering_entity.md

## 目的

将工程实现相关内容沉淀为 engineering entity，并登记到当前知识库的 `engineering_entity_registry.yaml` 中。

## 输出

- `ingest_engineering_entity_report`
- `target_kb`

## 流程

1. 定位当前知识库目录

2. 确认 engineering entity 基础结构

   如果不存在：

   ```text
   engineering_entity_registry.yaml
   engineering_entities/
   ```

   初始化时只使用 `template\knowledge_base\engineering\engineering_entity_registry_template.yaml` 创建空注册表，并创建 `engineering_entities/` 目录。空注册表的 `entities` 必须为 `[]`，不得在初始化阶段写入示例实体。

   `template\knowledge_base\engineering\engineering_entity_registry_entry_template.yaml` 只用于创建或更新具体 engineering entity，不得用于初始化整个注册表。

3. 提取工程经验

   主要是最近推进项目的经验

4. 判断是否已有实体

   在 `engineering_entity_registry.yaml` 中根据以下字段查找既有实体：

   - `canonical_label`
   - `aliases`
   - `category`
   - `scope`
   - `resource_refs.files.path`

   如果已经存在同一工程对象，不得重复创建新实体。

5. 创建或更新 engineering entity

   如果是新实体：

   - 分配新的 `eng_ent_000001` 格式 ID
   - 读取 `engineering_entity_registry_entry_template.yaml`
   - 替换 ID、日期、名称、分类、正文路径和其他实际字段
   - 将完成替换的条目追加到 `engineering_entity_registry.yaml` 的 `entities`
   - 更新 registry 的 `id_policy.next_id` 和 `updated_at`
   - 创建正文文件：

     ```text
     engineering_entities/eng_ent_000001_<工程实体名称>.md
     ```

   如果是既有实体：

   - 保持原 `id`
   - 更新 `updated_at`
   - 扩展 `resource_refs`
   - 修订对应正文文件

   写入正式注册表前，禁止将 `<...>`、`YYYY-MM-DD` 或其他模板占位符原样保存。存在未替换占位符时停止写入并报告缺失信息。

6. 写入正文文件

    模板`template\knowledge_base\engineering\engineering_entity_content_template.md`

7. 更新 registry

   更新：

   - `updated_at`
   - 对应 entity 的 `updated_at`
   - `summary`
   - `scope`
   - `resource_refs`
   - `related_entities`
   - `dependencies`
   - `tags`

   不得修改：

   - `.registry/machine/entity_registry.yaml`
   - `conversation_entity_registry.yaml`
   - `.registry/machine/relationship_registry.yaml`
   - `.registry/machine/knowledge_graph_registry.yaml`
   - 三张资料表

8. 追加日志

   在 `log.md` 追加：

   ```markdown
   ## [YYYY-MM-DD] ingest_engineering_entity | <知识库名>

   - 写入或更新 engineering entity：<eng_ent_id> <canonical_label>
   - 正文文件：<content_file>
   ```

9. 输出报告

   输出：

   ```yaml
   operation: ingest_engineering_entity
   target_kb: <知识库名>
   created_entities:
     - <eng_ent_id>
   updated_entities:
     - <eng_ent_id>
   content_files:
     - engineering_entities/<文件名>.md
   registry: engineering_entity_registry.yaml
   status: success
   ```



