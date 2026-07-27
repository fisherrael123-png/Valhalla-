# 移除 Valhalla root

1. 根据路径定位注册表条目。
2. 只从注册表移除条目，不删除 root 文件夹。
3. 如果移除的是 `current_root`，将 `current_root` 设为 `null`，除非用户指定新的默认 root。
4. 回复被移除的注册表条目和当前默认 root。



