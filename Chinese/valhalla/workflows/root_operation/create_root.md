# 创建 Valhalla root

输入：

- root 路径。
- 可选别名。

流程：

1. 将 root 路径解析为绝对路径。
2. 如果目标路径已存在且非空，先列出将创建或补齐的 Valhalla 文件和文件夹，并请求确认。
3. 创建或补齐最小 root 结构：

    ```text
    .valhalla/
        kb_status.md
    resource_registry.yaml
    resource_registry.md
    wiki_registry.yaml
    wiki_registry.md
    orphan_resources.md
    blacklist_registry.yaml
    Library/
        public_resources/
    Wiki/
    ```

4. 将 `.valhalla/kb_status.md` 依照`template\kb_status_template.yaml`初始化为 `idle`，保持本轮 root 管理会话。
5. 使用 version 2 模板初始化空 `resource_registry.yaml`、`resource_registry.md`、索引文件和黑名单日志。`resource_registry.yaml` 是资源层权威文件，`resource_registry.md` 是与它同步的人类可读投影视图。
6. 使用 `template/root/wiki_registry_template.yaml` 和 `template/root/wiki_registry_template.md` 初始化 `wiki_registry.yaml` 与 `wiki_registry.md`。`wiki_registry.yaml` 是当前 root 下所有知识库的机器权威索引，`wiki_registry.md` 是人类可读投影。
7. 资源层以下的文件路径只允许保存在 `resource_registry.yaml`；知识库资料表、Entity、Relationship 和 Graph 层只引用 `resource_id`。
8. 如果 root 注册表不存在，创建空注册表。
9. 将该 root 登记到注册表；如果提供别名，使用该别名；否则根据文件夹名生成别名。
10. 将注册表的 `current_root` 设置为该 root。
11. 回复 root 路径、别名、已创建文件和当前状态。



