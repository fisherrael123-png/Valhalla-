# 登记 Valhalla root

用于把已有 Valhalla root 加入注册表，不创建或改写 root 内容。

1. 将路径解析为绝对路径。
2. 按 root 判定标准检查目录。
3. 读取 root 注册表。
4. 在root 注册表中添加别名、路径和 `last_used_at`。
5. 除非用户明确要求切换，否则不改变 `current_root`。



