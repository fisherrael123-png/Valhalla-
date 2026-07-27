# query

## 目标

基于当前活动知识库回答 `query_text`，保持来源可追溯，并明确区分知识库证据、网络资料和模型推断。

## 有效资料范围

1. 从三张 YAML 资料表和全局黑名单计算有效资源：

   ```text
   (.virtualDatabase/machine/local_resources.yaml 中 membership_status == active 的 resource_id
   ∪ .virtualDatabase/machine/required_resources.yaml 中 membership_status == active 的 resource_id)
   - .virtualDatabase/machine/excluded_resources.yaml 中 membership_status == active 的 resource_id
   - blacklist_registry.yaml 中 listed 的 resource_id
   ```

2. Markdown 资料表仅供人类查看，不决定资源成员身份。
3. 原始资料只能读取有效 `resource_id` 对应的 `Library/public_resources/` 公共表现文件。
4. 不得读取或引用剔除资料表、全局黑名单或失效成员中的资源。

## 查询流程

1. 解析 `query_text`、可选的 `query_scope` 和期望输出，确定本次问题边界。
2. 优先检索当前知识库的：
   - `.registry/machine/entity_registry.yaml` 和 `entities/`；
   - `.registry/machine/relationship_registry.yaml`；
   - `.registry/machine/knowledge_graph_registry.yaml` 和 `knowledge_graph/`；
   - `conversation_entity_registry.yaml` 和 `conversation_entities/`；
   - `engineering_entity_registry.yaml` 和 `engineering_entities/`。
3. 记录实际使用的 `entity_id`、关系和图谱。
4. 现有知识不足时，从有效资料范围内选择相关 `resource_id`，读取其可用公共表现文件。
5. 记录实际使用的 `resource_id`、表现类型和资源内部证据定位。
6. 知识库证据仍不足时：
   - 只有 `allow_network_search: true` 时才能搜索网络；
   - 未提供或为 `false` 时，先询问用户是否允许；
   - 网络搜索结果只作为外部临时资料；
   - 不得把网络结果描述为知识库已有知识。
7. 根据证据回答问题，并明确区分：
   - 知识库明确支持的结论；
   - 外部资料提供的信息；
   - 基于证据形成的推断；
   - 尚不确定或存在冲突的内容。
8. 用户未明确要求前，不修改或归档任何知识库文件。

## 停止或降级回答

出现以下情况时，不得生成确定性结论：

- 没有足够证据；
- 不同资源相互矛盾；
- 资源被排除或拉黑；
- 无法确认资源内容或版本；
- 来源定位不足；
- 问题超出当前知识库范围。

此时输出已经确认的内容、证据缺口、不确定性和建议的后续操作。

## query_report

至少输出：

- `answer`
- `target_kb`
- `knowledge_used`
- `source_records`
- `external_sources`
- `inferences`
- `conflicts`
- `uncertainty`
- `suggested_follow_up`

`source_records` 优先使用：

```text
resource_id → entity_id → evidence_location → supported_claim
```

不得只用文件名作为来源。网络资料必须记录在 `external_sources`，不得混入知识库来源记录。



