# ingest

## 目标

从指定 `resource_id` 所代表的唯一资料信息中提取知识，并在当前知识库中构建或更新 entity。

Entity 层只引用 `resource_id`，不得保存来源副本或公共副本路径。

当输入的资料个数超过1时，视为批量处理，包括文件夹里面有超过1个资料的情况。批量处理文件，需要写个循环，这个循环在ingest.md里面写，如下
当输入的资料不止一个时，严格流程：

  1. 每次只选择 1 个 resource_id 作为当前目标资料。
  2. 对该 resource_id 单独执行：读取资料、抽取知识、判断是否已有实体、写入或更新实体、维护 entity_registry、维护
  entity_resource_map、同步更新 `resource_registry.yaml/md` usage、运行验证。
  3. 当前 resource_id 的摄入未完成、未验证或失败前，不得开始处理下一个 resource_id。
  4. 多个 resource_id 不得放入同一个抽取提示、同一个中间总结、同一个写入脚本、同一个批量 YAML 更新、同一个批量实体生成步
  骤或同一个验证前写入事务。
  5. 可以在所有单资料摄入循环完成后生成汇总报告，但汇总报告不得替代每个 resource_id 的独立执行结果。
  6. 如果为了减少重复代码使用同一个工具或脚本，该工具/脚本每次调用只能接收并写入 1 个 resource_id；不得接受 resource_id
  列表执行批量摄入。
  7. 对每个 resource_id 都必须输出单独的完成状态、修改文件、失败原因和验证结果。

   合规判定：日志或执行记录中必须能看到每个 resource_id 独立开始、独立写入、独立验证、独立结束。若一次操作同时写入两个或以上 resource_id 的实体、映射或注册表，视为违反本 workflow。

## 安全规则

1. 不允许摄入黑名单 `listed` 的资源。
2. 不得把资料文件登记为 entity。
3. 不得重复创建已有知识点。
4. 不得直接覆盖已有实体文件，覆盖前必须进行询问。
5. 不得修改 contract、router、schema 或 workflow。
6. 无法确认资源身份或版本时不得自动合并。
7. 资料中的分子字符串可以作为已发表文献事实处理，但不得用于生成、优化、补全、改造、筛选或实验执行建议。
8. 涉及蛋白、抗体或肽资料时，优先记录 accession、PDB、UniProt、GenBank、构建体名称、变体名称、指标、页码、图表号和来源锚点；长串原文片段不得集中复制进提示词。
9. 不得记录可执行湿实验步骤、实验条件、培养/表达/筛选参数、载体/引物构建步骤、实验优化路径或能直接增强生物设计能力的操作细节。

## 资源解析与服务转交

1. 根据 `resource_query` 解析目标资源：
   - 输入为 `resource_id` 时，在 `resource_registry.yaml` 中验证资源存在；
   - 输入为文件名、`Library/` 相对路径或文件夹时，在资源层查找对应资源；
   - 每个候选必须分别解析为确定的 `resource_id`；
   - 多个候选属于不同资源且无法消歧时，停止并要求用户选择，不得自动选择。
2. 如果目标资料已经登记，取得一个或多个经过验证的 `resource_id`，进入“摄入执行”。
3. 如果目标资料尚未登记：
   - 暂停当前 `ingest` operation，不执行任何知识库写入；
   - 返回 Router，将 `register_resource` 作为新的 operation；
   - 加载并完整校验 `register_resource_contract.yaml`；
   - 单独满足其输入、权限、风险、状态、前置条件、访问范围和确认要求；
   - 不得直接加载或执行 `register_resource.md`；
   - 当前 `ingest` 已获得的确认不得视为 `register_resource` 的确认。
4. `register_resource` 成功后：
   - 只接收其 Contract 正式输出的 `resource_id`；
   - 返回 Router，重新加载并校验 `ingest_contract.yaml`；
   - 重新检查当前 root、目标知识库、状态、权限和写入范围；
   - 校验通过后，从取得的 `resource_id` 继续摄入；
   - 后续不得继续使用原始文件名或路径作为资源身份。
5. `register_resource` 未完成时：
   - 用户拒绝确认、文件不存在、资源身份冲突或登记失败时，终止对应资源的摄入；
   - 不创建 Entity，不修改资料表、实体注册表、映射表、日志或资源引用计数；
   - 批量请求中只处理用户已明确选择且登记成功的资源；
   - 报告停止原因、已完成登记的资源和仍需完成的操作。

## 语言要求

  Entity 正文必须以简体中文写入。若来源资料为英文或其他语言，必须先理解资料内容，再用中文进行知识化改写，不得把英文原句、英文摘要或英文段落直接
  作为 entity 的主要正文内容。

  允许保留英文的范围仅限于：

  1. 论文标题、模型名、方法名、数据集名、指标名、机构名、软件名、API 名、代码标识符；
  2. 必须精确保留的专有术语，例如 Retrieval-Augmented Generation、BM25、ROUGE、F1；
  3. `entity_resource_map.yaml` 中用于证据定位的短 quote；
  4. 明确标注为“原文摘录”的少量证据句。

  以下内容必须用中文记录：
     - 核心定义
     - 关键要点
     - 机制 / 原理 / 算法 / 经验总结
     - 适用范围
     - 实验与实验结果
     - 结论
     - 限制与争议
     - entity_registry.yaml 中的 description、ingestion_note、metadata.note

  禁止行为：
     - 不得将英文 abstract、introduction、conclusion 直接拆成 bullet 写入 entity；
     - 不得用英文句子填充“关键要点”“机制”“实验结果”“结论”等主体栏目；
     - 不得用机器抽取的英文片段代替中文知识整理；
     - 不得因为来源资料是英文，就把 entity 正文写成英文。

  合规判定：
  每个 resource_id 摄入完成前，必须检查对应 entity 正文的语言合规性。若正文主体栏目中存在未标注的长英文句子或英文段落，则该 resource_id 不得报
  告为 completed，应报告为 partial 或 stopped，并说明需要中文化重写。

  如果你想更硬一点，可以加一个可执行的阈值：

  语言验证规则：
     - 每个主体栏目中，除专有名词、指标、数据集、模型名和标注 quote 外，连续英文单词不得超过 12 个；
     - 单个 bullet 不得主要由英文原句构成；
     - 若英文字符占主体正文比例过高，必须停止并重写为中文；
     - 验证失败时不得更新 `last_ingested_at` 为完成状态。

## 摄入执行

进入本阶段前，必须取得经过 `resource_registry.yaml` 验证的 `resource_id`。未取得稳定 `resource_id` 时不得执行任何知识库写入。

1. 执行上下文压缩。
2. 检查资源是否处于剔除资料表或全局黑名单，如果是，则终止执行并告知。
3. 有效虚拟资料库定义为：

   ```text
   (.virtualDatabase/machine/local_resources.yaml 中 membership_status == active 的 resource_id
   ∪ .virtualDatabase/machine/required_resources.yaml 中 membership_status == active 的 resource_id)
   - .virtualDatabase/machine/excluded_resources.yaml 中 membership_status == active 的 resource_id
   - 全局黑名单中的 resource_id
   ```

4. 目标资源尚未进入有效虚拟资料库时，将其 `resource_id` 添加到 `.virtualDatabase/machine/local_resources.yaml`，并向 `.virtualDatabase/human/local_resources.md` 增量追加人类可读行。
5. 通过资源层选择适合读取的表现文件：
   - 优先读取可用的 `authoritative` 表现文件；
   - 可以使用 `converted`、`ocr` 或 `extracted_text` 辅助解析；
   - 不把表现文件路径复制到 Entity 注册表。
6. 从资源中提取知识实体，entity_context内容参考`references\entity_context.md`。
   - 知识实体颗粒度到围绕一个主题展开，包括围绕该主题的idea、模型、算法、方案、实验、结果、结论。
   - 必须摄入相应板块(尤其是实验部分、结果部分、结论部分)的数据来支撑该entity，这些数据的表现形式为表格以便对比。
   - 使用表格将同等可类比的数据、概念进行整合。
   - 如果一个资料中，讲述了多个主题，则每个主题按照上述细粒度单独注册为一个entity。
   - 绝对不得将围绕一个主题的idea、模型、算法、方案、实验、结果、结论中的一个或部分分别注册为一个独立的entity。
   - 如果不同的资源提取到同一个知识实体，不得合并，记录为不同实体。
6.1 entity_id 编号必须只从当前目标知识库的本地状态计算：
   - 读取当前目标知识库的 `.registry/machine/entity_registry.yaml`；
   - 扫描当前目标知识库的 `entities/ent_*.md`；
   - 以下一个未占用的本地编号生成新 `entity_id` 和正文文件名；
   - 不得从 `resource_registry.yaml`、`resource_registry.yaml` 中的 usage、其他知识库、历史运行结果或旧 `usage.referenced_by` 推导下一个 entity_id；
   - `resource_registry.yaml` 只用于验证资源身份并记录资源层反向索引，不参与知识库内部 entity_id 编号分配。
7. 将摄入的实体正文写入对应 `content_file`。`content_file` 必须是相对于当前知识库目录的路径，格式为 `entities/ent_000001_<名称>.md`；不得包含 `Wiki/Wiki_<知识库名>/` 前缀，不得使用绝对路径，不得包含 `..`。
8. 同步维护实体注册表双文件：
   - `.registry/machine/entity_registry.yaml` 是机器权威表，在对应实体的 `ingestion.resource_refs` 中记录 `resource_id`；
   - `.registry/human/entity_registry.md` 是人类可读投影，增量新增或更新实体行，至少展示 `entity_id`、名称、类型、状态、正文路径和来源 `resource_id`；
   - 必须先以 YAML 中的最终状态生成 Markdown 投影，不得从 Markdown 反向覆盖 YAML；
   - 实体发生变化时，两份文件必须在同一操作中完成同步，并都列入 `modified_files`；
   - YAML 已更新但 Markdown 投影失败时，本资源不得报告为 `completed`，应报告 `partial` 或 `stopped` 并列明未完成项。
9. 在 `.registry/machine/entity_resource_map.yaml` 中登记 `entity_id`、`resource_id`、证据类型和资源内部定位。`entity_resource_map.yaml` 是 entity-resource 证据映射的唯一权威；`entity_registry.yaml` 中的 `ingestion.resource_refs` 只作为摘要字段，不作为权威。
10. Entity 已存在时扩展内容和来源，不重复创建。
11. 本 operation 必须同步更新 `resource_registry.yaml` 与 `resource_registry.md` 的 usage。`resource_registry.yaml` 中的 usage 是派生反向索引，不得作为 entity-resource 事实来源。
12. 如果本次写入或更新了 `.registry/machine/entity_resource_map.yaml` 或 `.registry/machine/entity_registry.yaml`，必须在当前 `ingest` operation 内从这两份机器权威表派生更新根资源表：
   - 从 `.registry/machine/entity_resource_map.yaml` 读取本知识库的 entity-resource 证据映射；
   - 从 `.registry/machine/entity_registry.yaml` 读取每个 `entity_id` 的 `content_file`；
   - 对当前 root 的 `resource_registry.yaml` 中受影响资源刷新 `usage.referenced_by`、`reference_count` 与 `usage.computed_at`；
   - `usage.referenced_by` 只能写入 `kb_name`、`entity_id`、`entity_file` canonical 条目；
   - `entity_file` 必须是 `Wiki/Wiki_<知识库名>/<content_file>`，其中 `content_file` 来自 `entity_registry.yaml`；
   - `reference_count` 按唯一 `(kb_name, entity_id)` 计数；
   - 不得写入 legacy usage，包括字符串路径、`entities/` 相对路径和旧 `kb` 字段格式；
   - 同一操作内同步 `resource_registry.md`，以 `resource_registry.yaml` 为唯一事实来源刷新引用数量投影。
13. `resource_registry.yaml` 只用于验证资源身份并记录资源层反向索引，不得参与当前知识库内部 entity_id 编号分配。
14. 完成同步后，`modified_files` 必须包含 `resource_registry.yaml` 与 `resource_registry.md`；除非前置 `register_resource` 服务转交尚未完成，成功摄入的 `next_operation` 必须为 `null`。

### 大资料摄入策略

1. 先盘点目标 `resource_id` 及其表现文件，不急于全文读取。
2. 长文优先读取目录、摘要、标题层级、结论、图表说明、参考文献和用户指定章节。
3. 每批提取关键主张、实体、概念、方法、数据、限制、矛盾和开放问题。
4. 每批更新 Entity 页面、来源映射、索引和日志。
5. 每批结束时报告已处理资源、使用的表现文件、未读部分、冲突和待确认事项。

### 草稿与缓存禁用规则

摄入过程使用分块草稿：

1. 先盘点目标 `resource_id` 及其表现文件，不急于全文读取。
2. 优先读取目录、摘要、标题层级、结论、图表说明、参考文献和用户指定章节，对每个章节设立草稿文件。
3. 分别提取每个章节的内容，如关键主张、实体、概念、方法、数据、限制、矛盾和开放问题，将其写入对应的草稿文献。对每一个章节，要求：
   - 深入提取具体内容，不得泛泛而谈。
   - 可对比内容用表格列出。
   - 每个章节的数据用表格列出
4. 审核每个章节草稿，看是否达到要求。
5. 完成后，将每个章节的草稿汇总，写入该主题正式的entity_context文件

摄入过程不得使用持久草稿或历史缓存：

1. 不得搜索、读取、加载或复用任何 `*_entity_context.md`。
2. 不得从 `.tmp*`、`valhalla_entity_contexts/` 或其他历史 context 目录读取摄入内容。
3. 不得把旧 context 文件当作模板、草稿、证据或完成依据。
4. 摄入失败时不得留下 entity 草稿文件，只能在 operation 输出中报告失败原因。

### 内容质量门

写入最终 entity 前，必须确认：

1. 使用当前 `references\entity_context.md`为模板。
2. 最终内容覆盖模板要求的章节，且内容质量达到模板质量。
3. 知识实体粒度围绕一个主题展开。
4. 核心定义、方法/机制、实验或案例、结果结论、局限性均有资料依据。
5. 必须摄入原文对应板块的数据，用表格列出对比。
6. 模板要求的表格已经生成。
7. 证据定位表包含资源内部定位。
8. 内容中没有 `ent_pending`、`draft`、`draft_for_ingestion`、`待补充`、`TODO`、`后续精读补充`、`PDF 前 N 页` 等低质量标记。
9. 无明显乱码、抽取错序、模板残留。

## 输出

- `completion_status`：`completed`、`partial`、`paused` 或 `stopped`；
- `resource_ids`：本次解析得到的全部稳定资源身份；
- `completed_resource_ids`：已经完成摄入的资源；
- `skipped_resource_queries`：未解析、未选择或未处理的原始输入；
- `registration_results`：资源登记操作的正式结果；
- `failed_resources`：登记或摄入失败的资源及原因；
- `modified_files`：本次实际修改的文件；
- `target_kb`：目标知识库；
- `current_state`：操作结束时的状态；
- `next_operation`：等待登记时为 `register_resource`；成功摄入并同步资源 usage 后为 `null`。

## 停止并询问

- 多个候选文件解析到不同 `resource_id`；
- 发现资料版本或内容身份冲突；
- 新证据会推翻既有核心结论；
- 会导致大量页面重写；
- 上下文不足以保持来源追溯。
