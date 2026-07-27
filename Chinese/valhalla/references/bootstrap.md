# Bootstrap 过程

  Valhalla 在当前会话中首次启动时运行 `python bootstrap.py`，依次完成：

  1. 运行系统自检脚本，检查或重建 `~/.codex/valhalla/os_status.json` 和 `roots.json`，并将系统状态重置为 `base`。
  2. 验证全部 Contract 是否符合 0.5.11 统一格式，并检查 executor 引用路径。
  3. 验证资源层 Contract、状态结构和 Entity 路径契约。
  4. 加载 `router/router.md`，使 Router 内容进入当前会话上下文。
  5. 输出当前系统状态、当前 root 和当前知识库状态。
  6. 报告初始化完成。

  Bootstrap 只负责初始化、自检、状态复位和加载 Router，不会自动解析用户请求、加载业务 contract 或执行具体 workflow。



