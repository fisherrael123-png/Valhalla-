# 切换 Valhalla root 工作流

1. 根据别名或路径在默认Root注册表：
   - Windows: `%USERPROFILE%\.codex\valhalla\roots.json`
   - macOS/Linux: `~/.codex/valhalla/roots.json`
   中查找目标 root。
2. 确认目标 root 存在并符合 root 判定标准。
3. 更新注册表的 `current_root` 和目标条目的 `last_used_at`。
4. 不修改目标 root 内部的 `.valhalla/kb_status.md`。
5. 回复新的目标root(也是新的默认 root)，以及该 root 内当前知识库状态。



