# 列出当前 root 下的知识库

1. 确认当前 Valhalla root 已知。
2. 读取 root 下的 `wiki_registry.yaml`；若文件不存在或为空，不扫描推断并报告“当前 root 尚未登记知识库”。
3. 同步读取 `wiki_registry.md` 作为人类可读投影；冲突时以 `wiki_registry.yaml` 为准。
4. 列出每个知识库的 `kb_name`、`wiki_path`、`status`、`created_at`、`updated_at`、`description`。
5. 若 `wiki_path` 指向的目录不存在，在结果中标记为 `missing_path`，但不自动删除登记项。
6. 输出 `list_root_report`，包含当前 root、知识库数量、登记项和缺失路径。

本 operation 只读，不创建、删除或修复任何知识库。
