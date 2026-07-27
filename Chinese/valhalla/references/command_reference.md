# 命令参考

使用本文件帮助研究组成员了解可以怎样调用 Valhalla，并帮助 Codex 将用户请求映射到最新 Router 中的分类和 contract。

组员不需要记住内部分类名。优先使用“组员常用命令”中的自然说法；只要意思明确，Codex 应按对应分类处理。分类不确定时，先参考本文件；仍不确定时，回到 `router.md` 的触发条件和加载目标判断。

## 风险等级约定

| 风险等级 | 含义 | 默认处理 |
|---|---|---|
| `low` | 只读、状态查询、普通问答，或不进入 Valhalla 写入流程。 | 可直接执行；如目标不明则询问。 |
| `medium` | 会有写操作，但目标明确、操作明确。 | 可直接执行；如目标不明则询问。 |
| `high` | 涉及大范围图谱重建、跨知识库或全局维护，这类目标不定，操作结果不定的写操作，以及root类创建切换等。 | 必须到明确确认后再操作。 |

## 状态模型

Valhalla 系统只有2类状态：

- `base`：一般状态，只能执行非管理操作。
- `admin`：管理状态，可以执行管理操作。

## 会话状态

会话只有2类状态：

- `idle`：空闲状态，当前没有任何启动的知识库。
- `kb:<name>`：名为 <name> 的知识库处于活动状态，一些操作会默认以该知识库为对象。

## 基本原则

- 整个指令的执行过程是`router`→`contract`→`workflow`
- `router`是指令分类器，并加载对应类型的操作入口`contract`文件
- `contract`是状态检验器，它会查验当前的系统状态和会话状态，只有满足要求时，才会加载实际工作用的`workflow`，并会给这个操作附加一个风险等级。它就像一个安检关口，需要获得权限的个体才能通过。
- `workflow`是实际工作流。

## 组员常用命令

### Help 导航

Help 是只读文档导航入口，不加载 Contract，也不执行系统服务。

| 想了解什么 | 可以这样说 | Router 分类 | 读取 |
|---|---|---|---|
| 查看帮助菜单 | `help`、`帮助`、`Valhalla 帮助` | `help` | 不读取全部 Reference，只显示四类帮助菜单。 |
| 系统概览 | `系统介绍`、`Valhalla 是什么`、`系统原理` | `help` | `references/system_overview.md` |
| 命令与使用方法 | `命令帮助`、`有哪些命令`、`怎么使用` | `help` | `references/command_reference.md` |
| Bootstrap 启动过程 | `启动帮助`、`bootstrap 是什么` | `help` | `references/bootstrap.md` |
| Contract 格式与执行机制 | `Contract 帮助`、`Contract 格式` | `help` | `references/contract_format.md` |

### 查看状态和选择知识库

| 想做什么 | 可以这样说 | Router 分类 | 风险等级 | 结果 |
|---|---|---|---|---|
| 查看当前完整状态 | `当前Valhalla`、`当前状态`、`状态` | `status` | `low` | 同时报告系统状态和当前知识库状态。 |
| 只查看当前系统状态 | `当前系统状态`、`os_status` | `os_status` | `low` | 报告当前 Valhalla root 和系统状态。 |
| 查看当前 root | `当前root`、`当前使用的Valhalla root` | `show_current_root` | `low` | 只报告当前使用的 Valhalla root。 |
| 查看当前知识库 | `当前知识库`、`当前激活了什么知识库` | `kb_status` | `low` | 报告当前是否处于某个知识库状态。 |
| 列出当前 root 下的知识库 | `当前root有哪些知识库`、`知识库列表`、`列出当前root下的知识库` | `list_root` | `low` | 读取 `wiki_registry.yaml` 并列出当前 root 下登记的知识库。 |
| 新建知识库 | `新建知识库-<知识库名>`、`创建知识库 <知识库名>` | `create_kb` | `high` | 创建新的 Wiki 文件夹和知识库脚手架。 |
| 登记已有知识库目录 | `登记已有知识库 <知识库名>`、`注册已有知识库 <知识库名>` | `register_existing_kb` | `high` | 将已存在且结构合格的 `Wiki/Wiki_<知识库名>/` 加入 `wiki_registry.yaml/md`，验证该 KB 的 `entity_resource_map.yaml` 引用资源存在，并转交 `sync_resource_usage` 补齐 `resource_registry.yaml/md` 中的 usage 反向引用；不创建目录、不修改目录内容、不启动知识库。 |
| 启动或切换知识库 | `启动知识库-<知识库名>`、`切换知识库 <知识库名>` | `start_kb` | `medium` | 将目标知识库设为当前活动知识库。 |
| 退出当前知识库 | `退出知识库`、`停止使用当前知识库` | `exit_kb` | `medium` | 退出当前知识库状态。 |
| 删除或注销知识库 | `删除知识库 <知识库名>`、`注销知识库 <知识库名>` | `remove_kb` | `high` | 从当前 root 的知识库注册表注销该知识库，并转交 `sync_resource_usage` 清理 `resource_registry.yaml/md` 中指向该 KB 的 usage 反向引用；不删除 `Wiki/Wiki_<知识库名>/` 目录。 |
| 修改知识库名称 | `重命名知识库 <旧名称> 为 <新名称>`、`修改知识库名称，把 <旧名称> 改成 <新名称>` | `rename_kb` | `high` | 修改知识库显示名称、登记名称和 Wiki 文件夹名称；完成后转交 `sync_resource_usage` 刷新 usage 反向索引；执行前必须退出当前知识库并确认影响范围。 |
| 融合多个知识库 | `融合知识库 A, B, C 为 新综合库`、`合并知识库 A，B 为 新综合库` | `fuse_kbs` | `high` | 需 admin 且 idle。只支持显式来源知识库列表，不支持融合当前root全部知识库。先只读审核 entity、relationship、conversation、engineering 和资料表冲突；确认后创建新目标知识库并转交 `sync_resource_usage`。报告 `excluded_but_used_resources`。 |
| 迁移外部 root 的知识库 | `迁移知识库 root2:ai工程`、`迁移知识库 root2:ai工程 新名称 ai工程迁移版`、`迁移知识库 E:\valhallaroot2\Wiki\Wiki_ai工程` | `migrate_kb` | `high` | 需 admin 且 idle。目标 root 永远是当前 root。来源知识库必须登记在已登记的非当前 root 中；路径输入必须精确匹配已登记 KB 路径。确认后复制 KB、重写 `resource_id`、补齐公共资料、把来源黑名单差异写入迁移后 KB 的剔除资料表，最终登记后转交 `sync_resource_usage`；不会自动启动。 |

### Root 管理

Root 是整个 Valhalla 系统的总文件夹。普通组员通常只需要查看当前 root；创建、登记、切换、移除 root 属于维护操作。

| 想做什么 | 可以这样说 | Router 分类 | 风险等级 | 结果 |
|---|---|---|---|---|
| 列出所有 root | `列出Valhalla`、`列出root`、`root列表` | `list_roots` | `low` | 列出当前登记的 Valhalla root。 |
| 创建 Valhalla root | `创建Valhalla <路径> [别名]`、`初始化Valhalla <路径> [别名]` | `create_root` | `high` | 创建 root 结构，并按 contract 要求登记。 |
| 登记已有 root | `登记Valhalla <别名> <路径>` | `register_root` | `high` | 将已有 root 加入 root 注册表。 |
| 切换默认 root | `切换Valhalla <别名或路径>` | `switch_root` | `high` | 切换当前默认 Valhalla root。 |
| 移除 root 登记 | `移除Valhalla <别名或路径>`、`忘记Valhalla <别名或路径>` | `remove_root` | `high` | 从 root 注册表移除条目；不代表删除文件夹。 |
| 融合多个 root | `将来源 <来源root1>, <来源root2> 融合为 <新root路径> [别名 <新root别名>]`、`合并root <新root路径> 来源 <来源root列表>` | `fuse_roots` | `high` | 只读审计多个来源 root，解决资源身份、黑名单和 KB 命名决策后，创建新的派生 root；不修改来源 root。未提供别名时进入 `post_fusion_registration`，执行末尾询问是否登记新 root。 |

### 查询和整理知识

| 想做什么 | 可以这样说 | Router 分类 | 风险等级 | 结果 |
|---|---|---|---|---|
| 向当前知识库提问 | `查询 <问题>`、`问当前知识库 <问题>` | `query` | `low` | 使用当前活动知识库回答，记录知识库来源、外部来源、推断与不确定性；知识库证据不足时，仅在用户允许后搜索网络。 |
| 登记资源 | `登记资源 <文件名或Library相对路径>`、`注册资源 <路径>` | `register_resource` | `high` | 为 Library 非公共目录中的资料建立稳定 `resource_id`，同步资源 YAML/Markdown 注册表并生成或绑定公共副本。 |
| 同步资源 usage | `同步resource usage`、`清理历史resource usage`、`重建资源引用索引` | `sync_resource_usage` | `high` | 需 base 或 admin，可在 idle 或 kb:<name> 状态运行。以目标 root 的 `wiki_registry.yaml` 中已登记 KB 为准，从各 KB 的 `entity_registry.yaml` 和 `entity_resource_map.yaml` 重建 `resource_registry.yaml/md` 的 usage 反向索引，并清理历史 stale usage。 |
| 摄入资料 | `摄入 <路径>`、`把 <路径> 放进当前知识库` | `ingest` | `high` | 将资料总结为 entity，写入正文，同步 `.registry/machine/entity_registry.yaml` 与 `.registry/human/entity_registry.md`，并登记来源映射。 |
| 整理实体关系 | `整理实体关系`、`总结本知识库中的entity关系` | `relate_entities` | `high` | 分析并将确认后的实体间关系事实写入 `.registry/machine/relationship_registry.yaml`；图谱只投影这些关系。 |
| 构建或修改知识图谱 | `更新知识图谱`、`重建知识图谱`、`整理知识图谱` | `edit_knowledge_graph` | `high` | 构建、整理或修改当前知识库的知识图谱。 |
| 摄入对话归档 | `摄入对话`、`归档本轮对话`、`摄入这个对话总结` | `ingest_conversation` | `high` | 将对话总结整合为 conversation entities。 |
| 摄入工程经验 | `摄入工程经验`、`归档工程经验`、`记录这次工程经验` | `ingest_engineering` | `high` | 将工程经验整合为 engineering entities。 |
| 初始化工程实体结构 | `初始化工程实体结构`、`创建工程实体注册表` | `init_engineering_entities` | `medium` | 仅创建空的 engineering entity 注册表和目录，不写入示例实体。 |

### 资料表操作

资料表操作统一进入 `edit_resource_table`。用户不需要知道三张表的内部结构，只需要说明表名、动作和路径或名称。

每张资料表包含同名 YAML 和 Markdown：YAML 是机器权威成员表，Markdown 展示主名称、加入时输入和当前来源路径。添加资料时增量追加；删除资料时立即标记为待清理并退出有效资料库，后续由 lint 批量清理。

| 想做什么 | 可以这样说 | Router 分类 | 风险等级 | 结果 |
|---|---|---|---|---|
| 加入本库资料表 | `本库资料表，添加 <路径>` | `edit_resource_table` | `medium` | 将资料纳入当前知识库可用范围。 |
| 移出本库资料表 | `本库资料表，删除 <路径>` | `edit_resource_table` | `medium` | 从当前知识库资料范围移除该资料。 |
| 标记必须资料 | `必须资料表，添加 <路径>` | `edit_resource_table` | `medium` | 标记当前知识库必须考虑该资料。 |
| 取消必须资料 | `必须资料表，删除 <路径>` | `edit_resource_table` | `medium` | 取消必须使用标记。 |
| 排除资料 | `剔除资料表，添加 <路径>` | `edit_resource_table` | `medium` | 标记当前知识库不应使用该资料。 |
| 取消排除资料 | `剔除资料表，删除 <路径>` | `edit_resource_table` | `medium` | 从剔除表中移除该资料。 |
| 查看或解释资料表 | `查看资料表`、`解释当前资料范围` | `edit_resource_table` 或 `query` | `low` | 若只读解释，按 query/只读处理；若修改，进入 `edit_resource_table` 且风险升为 `medium`。 |

### 管理和检查

| 想做什么 | 可以这样说 | Router 分类 | 风险等级 | 结果 |
|---|---|---|---|---|
| 进入管理状态 | `激活管理状态`、`进入管理状态` | `admin_operation` → `admin_enter` | `medium` | 进入 admin 状态。 |
| 退出管理状态 | `结束管理状态`、`退出管理状态` | `admin_operation` → `admin_exit` | `medium` | 退出 admin 状态，回到普通状态。 |
| 查看黑名单 | `查看黑名单`、`列出黑名单资料` | `blacklist_operation` → `list_blacklist` | `low` | 只读列出全局黑名单资源。 |
| 加入黑名单 | `黑名单，添加 <路径或名称>` | `blacklist_operation` → `add_blacklist` | `high` | 将解析到的整个 `resource_id` 加入黑名单。 |
| 移出黑名单 | `黑名单，删除 <blacklist_id>` | `blacklist_operation` → `remove_blacklist` | `high` | 从黑名单移除指定条目。 |
| 检查知识库 | `检查 <知识库名>`、`检查当前知识库` | `lint` | `high` | 检查结构、链接、资料表、索引和注册表问题。 |
| 深度检查知识库 | `深度检查 <知识库名>`、`检查所有知识库` | `lint` | `high` | 执行更大范围或更深层的检查，包括报告缺失 entity context 的登记项。 |
| 修复检查问题 | `修复检查问题 <范围>` | `lint_fix` | `high` | 按已列出的问题或明确范围修复；涉及高风险项时先确认。缺失 entity context 登记清理可用 `修复检查问题 missing_entity_content_file`。 |

缺失 entity context 的推荐流程：

```text
进入管理状态
深度检查 <知识库名>
修复检查问题 missing_entity_content_file
```

该流程只在确认后清理 `entity_registry` 和 `entity_resource_map` 登记信息，不删除文件、不修改 `resource_registry.yaml`、不重建缺失正文。

### 推进项目

`project_work` 用于“用知识库帮助完成一个实际任务”，例如写论文段落、设计实验、整理综述、制定方案、推进代码或分析结果。默认只读取知识库，不自动写回。

| 想做什么 | 可以这样说 | Router 分类 | 风险等级 | 结果 |
|---|---|---|---|---|
| 用当前知识库推进任务 | `基于当前知识库推进：<任务>` | `project_work` | `medium` | 将当前知识库内容转化为任务上下文，并生成任务产物。 |
| 写论文或综述 | `参考当前知识库，帮我写/改 <论文段落或综述内容>` | `project_work` | `medium` | 输出论证结构、草稿、证据和待补引用。 |
| 设计实验或方案 | `参考当前知识库，设计 <实验/方案>` | `project_work` | `medium` | 输出目标、假设、变量、步骤、风险和判据。 |
| 推进代码或工程实现 | `参考当前知识库，实现/修改 <代码任务>` | `project_work` | `medium` | 提取需求、约束、接口、测试点或实现方案。 |
| 归档项目推进结果 | `归档本轮项目推进结果`、`把这次项目决策写回 Valhalla` | `ingest_engineering` 或 `ingest_conversation` | `high` | 只有用户明确要求归档时，才写回知识库；工程经验走 `ingest_engineering`，对话或决策总结走 `ingest_conversation`。 |

## Router 分类映射

Router 只负责根据用户意图选择分类。业务分类加载对应 Contract；`help` 和 `ordinary_file_work` 按 Router 声明直接处理。
Router 不直接执行 workflow，不直接修改文件，不绕过业务 Contract 的状态检查和风险等级判断。

| Router 分类              | 触发说法                                          | 风险等级     | 加载                                                                 |
| ---------------------- | --------------------------------------------- | -------- | ------------------------------------------------------------------ |
| `status`               | 当前 Valhalla、当前状态、状态、查看 Valhalla 状态        | `low`    | `contract\status\status_contract.yaml`                          |
| `os_status`            | 当前系统状态、os_status        | `low`    | `contract\status\os_status_contract.yaml`                          |
| `show_current_root`    | 当前 root、当前使用的 Valhalla root、现在用的是哪个 root      | `low`    | `contract\valhalla_root_operation\show_current_root_contract.yaml` |
| `kb_status`            | 当前知识库、当前激活了什么知识库、当前 KB 状态                     | `low`    | `contract\status\kb_status_contract.yaml`                          |
| `list_roots`           | 列出 Valhalla、列出 root、root 列表、有哪些 Valhalla root | `low`    | `contract\valhalla_root_operation\list_roots_contract.yaml`        |
| `list_root`            | 当前 root 有哪些知识库、知识库列表、列出当前 root 下的知识库 | `low`    | `contract\kb_operation\list_root_contract.yaml`        |
| `create_root`          | 创建 Valhalla、初始化 Valhalla、创建 Valhalla root     | `high`   | `contract\valhalla_root_operation\root_operation_contract.yaml`    |
| `register_root`        | 登记 Valhalla、登记已有 root、注册 Valhalla root        | `high`   | `contract\valhalla_root_operation\root_operation_contract.yaml`    |
| `switch_root`          | 切换 Valhalla、切换 root、使用另一个 Valhalla root       | `high`   | `contract\valhalla_root_operation\root_operation_contract.yaml`    |
| `remove_root`          | 移除 Valhalla、忘记 Valhalla、删除 root 登记、移除 root 登记 | `high`   | `contract\valhalla_root_operation\root_operation_contract.yaml`    |
| `fuse_roots`           | 融合 root、合并 root、整合 root、将来源 root 融合为新 root | `high`   | `contract\valhalla_root_operation\root_operation_contract.yaml`    |
| `create_kb`            | 新建知识库、创建知识库、新建 Wiki、创建 Wiki                   | `high`   | `contract\kb_operation\create_kb_contract.yaml`                    |
| `register_existing_kb` | 登记已有知识库、注册已有知识库、将已有 Wiki 登记为知识库          | `high`   | `contract\kb_operation\register_existing_kb_contract.yaml`         |
| `start_kb`             | 启动知识库、切换知识库、进入知识库、使用某个知识库                     | `medium` | `contract\kb_operation\start_kb_contract.yaml`                     |
| `exit_kb`              | 退出知识库、停止使用当前知识库、关闭当前知识库                       | `medium` | `contract\kb_operation\exit_kb_contract.yaml`                      |
| `remove_kb`            | 删除知识库、移除知识库、注销知识库、从当前 root 移除知识库             | `high`   | `contract\kb_operation\remove_kb_contract.yaml`                    |
| `rename_kb`            | 修改知识库名称、重命名知识库、知识库改名、把知识库改成另一个名字       | `high`   | `contract\kb_operation\rename_kb_contract.yaml`                    |
| `fuse_kbs`             | 融合知识库、合并知识库、整合知识库、融合知识库 A, B 为 新综合库；不支持融合当前root全部知识库 | `high`   | `contract\kb_operation\fuse_kbs_contract.yaml`                     |
| `migrate_kb`           | 迁移知识库、复制另一个 root 的知识库、从 root 迁移知识库；可用 `新名称` 解决目标命名冲突 | `high`   | `contract\kb_operation\migrate_kb_contract.yaml`                   |
| `query`                | 查询、问当前知识库、根据当前知识库回答、解释当前知识库内容                 | `low`    | `contract\kb_operation\query_contract.yaml`                        |
| `project_work`         | 基于当前知识库推进任务、参考知识库写论文、改综述、设计实验、制定方案、推进代码、分析结果  | `medium` | `contract\project_work\project_work_contract.yaml`                 |
| `edit_resource_table`    | 修改本库资料表、修改必须资料表、修改剔除资料表、添加资料、删除资料、排除资料、取消排除资料 | `medium` | `contract\kb_operation\edit_resource_table_contract.yaml`            |
| `register_resource`      | 登记资源、注册资源、将 Library 中的资料登记为资源                       | `high`   | `contract\resource\register_resource_contract.yaml`                 |
| `sync_resource_usage`    | 同步resource usage、清理历史resource usage、重建资源引用索引           | `high`   | `contract\resource\sync_resource_usage_contract.yaml`               |
| `ingest`               | 摄入资料、把资料放进当前知识库、总结资料为 entity、导入资料             | `high`   | `contract\kb_operation\ingest_contract.yaml`                       |
| `relate_entities`      | 整理实体关系、总结 entity 关系、分析知识点关系、建立实体关系            | `high`   | `contract\kb_operation\relate_entities_contract.yaml`              |
| `edit_knowledge_graph` | 更新知识图谱、重建知识图谱、整理知识图谱、修改知识图谱                   | `high`   | `contract\kb_operation\edit_knowledge_graph_contract.yaml`         |
| `ingest_conversation`  | 摄入对话、归档本轮对话、摄入这个对话总结、把对话写回知识库                 | `high`   | `contract\kb_operation\ingest_conversation_contract.yaml`          |
| `ingest_engineering`   | 摄入工程经验、归档工程经验、记录这次工程经验、把工程踩坑写回知识库             | `high`   | `contract\kb_operation\ingest_engineering_contract.yaml`           |
| `init_engineering_entities` | 初始化工程实体结构、创建工程实体注册表                           | `medium` | `contract\kb_operation\ingest_engineering_contract.yaml`           |
| `admin_operation`      | 激活管理状态、进入管理状态、结束管理状态、退出管理状态；分派到 `admin_enter` 或 `admin_exit` | `medium` | `contract\status\admin_operation_contract.yaml`                    |
| `blacklist_operation`  | 查看、添加或删除黑名单；分派到 `list_blacklist`、`add_blacklist` 或 `remove_blacklist` | `low/high` | `contract\resource\blacklist_operation_contract.yaml`                |
| `lint` / `lint_fix`    | 检查知识库、深度检查知识库、检查所有知识库，或在检查后修复已确认问题 | `high`   | `contract\lint\lint_contract.yaml`                         |
| `help`                 | help、帮助、系统介绍、命令帮助、启动帮助、Contract 帮助             | `low`    | 按主题读取 `SKILL.md` 指定的 Reference；不加载 Contract                  |
| `ordinary_file_work`   | 与 Valhalla 无关的普通文件任务、普通改写、普通总结、普通代码或文档处理      | `low`    | 不进入 Valhalla 工作流                                                   |



