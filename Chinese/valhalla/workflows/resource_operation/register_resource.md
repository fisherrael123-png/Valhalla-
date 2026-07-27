# register_resource workflow

## 目的

将当前 Valhalla root 的 `Library/` 中某个非公共文件登记为资源层对象。

一个 `resource_id` 表示一份内容与版本均唯一的信息对象。文件名、文件路径和文件格式都不是资源身份。

## 输入

必需：

- `resource_query`：用户指定的文件名、文件夹名或 `Library/` 相对路径。

可选：

- `canonical_name`：资源主名称；
- `aliases`：附属名称；
- `information_identity`：类型、版本、版次、语言、发布日期、DOI 或 URL；
- `representation_type`：默认 `authoritative`；
- `note`。

## 路径约束

1. 来源文件必须位于当前 root 的 `Library/` 下。
2. 来源文件不得位于 `Library/public_resources/`。
3. 注册表只保存相对于当前 root 的路径。
4. 禁止绝对路径、root 外路径和包含 `..` 的越界路径。
5. 同一表现文件可以登记多个 `source_copies`。
6. 公共副本必须位于 `Library/public_resources/<resource_id>/`。

## 资源身份判定

### 可归入同一 resource_id

- 同一信息的 PDF、Markdown、TXT 等不同格式；
- OCR、文本抽取或格式转换结果；
- 文件名不同但内容相同的副本；
- `Library/` 不同非公共文件夹中的同一资料副本。

### 必须使用不同 resource_id

- 预印本与正式发表版本；
- 初版与修订版；
- 原文与包含实质新信息的翻译；
- 摘要版与全文版；
- 数据集不同发布版本；
- 代码不同 release 或快照；
- 内容存在实质增删的资料。

仅标题、作者或文件名相似不能证明资源相同。无法确认内容与版本一致时，不得自动合并，必须保留为不同资源或请求用户确认。

## 名称规则

1. 每个资源必须有且只有一个 `identity.canonical_name`。
2. 其他名称登记在 `identity.aliases`。
3. 文件名可以成为附属名称候选，但不能自动取代主名称。
4. 主名称和附属名称变化均不改变 `resource_id`。
5. 主名称不得重复出现在附属名称中。

## 执行流程

1. 在当前 root 的 `Library/` 非公共目录中解析 `resource_query`。
2. 如果没有候选文件，停止并报告未找到。
3. 如果存在多个候选，比较路径、SHA-256、格式及信息身份：
   - 多个候选均指向同一已登记 `resource_id` 时继续；
   - 候选指向不同资源或无法判断时，列出候选并请求用户确认；
   - 不得自动选择。
4. 计算来源文件 SHA-256，搜索 `resource_registry.yaml` 中已有的 `source_copies`、公共副本和信息身份。
5. 判定是：
   - 已登记来源副本；
   - 已有资源的新来源副本；
   - 已有资源的新表现文件；
   - 一份新的唯一信息对象。
6. 新资源分配新的 `resource_id`，并确定一个 `canonical_name`。
7. 新表现文件分配新的 `file_id`，写入 `representations`。
8. 对转换、OCR 或文本抽取文件，通过 `derived_from` 指向同一资源内的来源表现文件。
9. 创建或查找 `Library/public_resources/<resource_id>/` 下的公共副本。
10. 更新 SHA-256、存在状态与 `sync_status`。
11. 重新计算 `usage` 和黑名单关联投影。
12. 写回 `resource_registry.yaml`。
13. 增量同步 `resource_registry.md`；若投影严重损坏，则根据 `resource_registry.yaml` 完整重建。
14. 执行资源 schema、路径边界、名称唯一性、file_id 和派生关系校验。

## 禁止行为

- 不得把不同版本或不同信息内容合并为同一 `resource_id`。
- 不得把公共副本登记为来源副本。
- 不得让 Entity、Relationship 或 Graph 层直接保存来源副本或公共副本路径。
- 不得仅凭相同文件名自动认定为同一资源。
- 不得在用户未确认时覆盖已有公共副本。

## 输出

- `resource_id`
- `canonical_name`
- 新增或复用的 `file_id`
- 来源副本路径
- 公共副本路径
- 修改文件
- 需要用户确认的身份冲突



