# resource_registry

> 本文件是 `resource_registry.yaml` 的人类可读投影视图。
> 资源身份、文件路径、同步状态、引用情况和黑名单状态均以对应权威注册表为准。
> 本文件不独立维护资源事实，与 `resource_registry.yaml` 同步；usage 反向索引只由 `sync_resource_usage` 重建。

## 基本信息

| 字段 | 值 |
| --- | --- |
| 资源注册表 | `resource_registry.yaml` |
| 注册表版本 | `2` |
| 最后更新时间 | `待填写` |
| 资源数量 | `0` |

## 资源摘要

| resource_id | 主名称 | 附属名称 | 类型 | 版本 | 生命周期 | 黑名单 | 引用数量 |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 文件明细

| resource_id | file_id | 表现类型 | 格式 | Library 来源副本 | 公共副本 | 同步状态 |
| --- | --- | --- | --- | --- | --- | --- |

## 字段说明

- 一个 `resource_id` 表示一份内容与版本均唯一的信息对象。
- 同一信息的 PDF、Markdown、TXT、OCR 或文本抽取文件可作为不同表现文件归入同一 `resource_id`。
- 预印本、正式版、修订版、实质性翻译或存在内容增删的版本必须使用不同 `resource_id`。
- “主名称”来自 `identity.canonical_name`；其他名称来自 `identity.aliases`。
- “Library 来源副本”只允许位于当前 root 的 `Library/` 下，并且不得位于 `Library/public_resources/`。
- “公共副本”必须位于 `Library/public_resources/<resource_id>/`。
- “黑名单”来自 `blacklist_registry.yaml` 的关联结果。
- “引用数量”由 `sync_resource_usage` 从 active 知识库的 `entity_resource_map.yaml` 与 `entity_registry.yaml` 派生计算。

## 备注

暂无。


