# Router

Router 只负责把用户请求映射到唯一业务分类；分组标题仅用于阅读导航，不是运行时分类。请求不明确或同时匹配多个分类时，停止并列出候选分类。

## 状态与导航

用于查看当前系统状态、当前知识库状态和帮助文档。此类操作通常只读；`help` 不加载 Contract。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `status` | 当前状态、当前 Valhalla 状态、状态 | `contract\status\status_contract.yaml` |
| `os_status` | 当前系统状态、os_status | `contract\status\os_status_contract.yaml` |
| `kb_status` | 当前知识库状态、当前激活了什么知识库、当前知识库 | `contract\status\kb_status_contract.yaml` |
| `help` | help、帮助、Valhalla怎么用、有哪些命令、系统是什么、bootstrap是什么、contract是什么 | 根据帮助主题读取 `SKILL.md` 的 Reference 与 Help 导航；不加载 Contract |

## Root 管理

用于查看、创建、登记、切换、移除或融合 Valhalla root。Root 级写操作影响范围大，通常需要 admin 和明确确认。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `list_roots` | 列出valhalla当前可用的root、列出root、查看root、root列表 | `contract\valhalla_root_operation\list_roots_contract.yaml` |
| `show_current_root` | 查询当前使用的valhalla root、当前root | `contract\valhalla_root_operation\show_current_root_contract.yaml` |
| `create_root` / `register_root` / `switch_root` / `remove_root` / `fuse_roots` | 创建、登记、切换、移除、融合、合并或整合 Valhalla root | `contract\valhalla_root_operation\root_operation_contract.yaml` |

## 知识库生命周期

用于当前 root 下知识库的列表、新建、登记、启动、退出、注销和改名。此类操作管理知识库本身，不负责资料语义加工。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `list_root` | 列出当前 root 下的知识库、当前 root 有哪些知识库、知识库列表 | `contract\kb_operation\list_root_contract.yaml` |
| `create_kb` | 新建知识库 | `contract\kb_operation\create_kb_contract.yaml` |
| `register_existing_kb` | 登记已有知识库、注册已有知识库、将已有 Wiki 登记为知识库、登记已有kb | `contract\kb_operation\register_existing_kb_contract.yaml` |
| `start_kb` | 启动或切换知识库 | `contract\kb_operation\start_kb_contract.yaml` |
| `exit_kb` | 退出当前知识库 | `contract\kb_operation\exit_kb_contract.yaml` |
| `remove_kb` | 删除知识库、移除知识库、注销知识库、从当前 root 移除知识库 | `contract\kb_operation\remove_kb_contract.yaml` |
| `rename_kb` | 修改知识库名称、重命名知识库、知识库改名、把知识库<旧名称>改名为<新名称> | `contract\kb_operation\rename_kb_contract.yaml` |

## 跨知识库维护

用于知识库融合和跨 root 知识库迁移。此类操作会重写大量 registry、资源映射或目标知识库内容，必须先 inspect 再确认 fix。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `fuse_kbs` | 融合知识库、合并知识库、整合知识库、融合知识库<来源列表>为<新知识库>；不支持融合当前root全部知识库 | `contract\kb_operation\fuse_kbs_contract.yaml` |
| `migrate_kb` | 迁移知识库、复制另一个root的知识库、从root迁移知识库；目标 root 永远是当前 root | `contract\kb_operation\migrate_kb_contract.yaml` |

## 资源与资料表

用于登记资料、修改知识库资料表和维护全局黑名单。资源身份以 `resource_id` 为准，资料表只引用资源身份。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `register_resource` | 将资料文件登记到resource_registry | `contract\resource\register_resource_contract.yaml` |
| `edit_resource_table` | 修改资料表 | `contract\kb_operation\edit_resource_table_contract.yaml` |
| `blacklist_operation` | 添加或删除黑名单 | `contract\resource\blacklist_operation_contract.yaml` |
| `sync_resource_usage` | 同步resource usage、清理历史resource usage、重建资源引用索引 | `contract\resource\sync_resource_usage_contract.yaml` |

## 知识加工与项目工作

用于摄入资料、查询知识库、整理实体关系、维护知识图谱，以及用知识库推进论文、代码、实验、综述、方案、报告或工程任务。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `ingest` | 摄入资料 | `contract\kb_operation\ingest_contract.yaml` |
| `query` | 针对当前启动的知识库提问 | `contract\kb_operation\query_contract.yaml` |
| `relate_entities` | 总结、整理本知识库中的entity之间的关系 | `contract\kb_operation\relate_entities_contract.yaml` |
| `edit_knowledge_graph` | 构建、整理、修改本知识库中entity之间的知识图谱 | `contract\kb_operation\edit_knowledge_graph_contract.yaml` |
| `ingest_conversation` | 摄入对话/对话归档 | `contract\kb_operation\ingest_conversation_contract.yaml` |
| `ingest_engineering` | 摄入工程经验/工程经验归档 | `contract\kb_operation\ingest_engineering_contract.yaml` |
| `project_work` | 使用知识库推进论文、代码、实验、综述、方案、报告或工程任务 | `contract\project_work\project_work_contract.yaml` |

## 管理、检查与普通文件任务

用于进入或退出 admin、检查知识库、修复检查问题，以及识别非 Valhalla 普通任务。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `admin_operation` | 进入/退出管理状态 | `contract\status\admin_operation_contract.yaml` |
| `lint` / `lint_fix` | 检查、深度检查知识库、检查所有知识库，或修复已列出的检查问题 | `contract\lint\lint_contract.yaml` |
| `ordinary_file_work` | 请求与 Valhalla 无关 | 不进入 Valhalla 工作流；按普通文件任务处理 |

帮助主题不明确时只显示帮助菜单，不一次加载全部 Reference。需要查询有哪些命令时，读取 `references\command_reference.md`。需要系统概念时，读取 `references\system_overview.md`。
