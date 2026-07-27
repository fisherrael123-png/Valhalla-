# Contract 统一格式

## 运行顺序

```text
Router
  → 加载 Contract
  → Dispatch 选择唯一 operation
  → 校验 operation 资格
  → 校验通过后加载 executor
  → 执行并检查 output
```

未匹配或同时匹配多个 operation 时停止，不加载 executor。

## 跨服务转交

Workflow 需要执行其他 operation 时，只能提出服务转交：

1. 暂停当前 operation，不直接加载目标 workflow。
2. 将目标 operation 返回 Router。
3. 加载并完整校验目标 Contract。
4. 当前 operation 的确认不得继承给目标 operation。
5. 服务之间只传递目标 Contract 声明的正式输出。
6. 恢复原 operation 前，重新加载并校验原 Contract。
7. 目标 operation 失败、被拒绝或输出不完整时，不得恢复原 operation。

## 顶层结构

```yaml
contract:
  name: example_contract
  version: "0.5.11"
  status: active
  purpose: "说明 Contract 的职责。"

operations:
  example:
    intent: "说明该 operation 的执行意图。"
    input:
      required: []
      optional: []
      pattern:
        canonical: "标准输入形式。"
        examples:
          - "示例输入"
        unsupported:
          - "不支持的输入"
    permissions:
      read: true
      write: false
    risk:
      level: low
      confirmation_required: false
    state_constraints: {}
    preconditions: []
    access:
      read_scope:
        allowed:
          - Wiki/Wiki_<知识库名>/
        denied: []
      write_scope:
        allowed:
          - user_explicit_target_paths
        denied:
          - Library/
        no_target_path_policy: "用户未指定目标路径时，先确认精确写入范围。"
      restrictions:
        - "只读取有效资料库。"
    executor:
      type: workflow
      paths:
        - workflows/example.md
      load_after_validation: true
    output:
      required: []
    constraints:
      must_not:
        - "跳过校验。"
```

Contract 顶层只能包含 `contract`、`dispatch`、`operations`。`contract` 元数据只能包含 `name`、`version`、`status`、`purpose`；`version` 必须是 `"0.5.11"`，`status` 可省略，存在时只能是 `active` 或 `deprecated`。

Operation 只能包含 `intent`、`input`、`permissions`、`risk`、`state_constraints`、`preconditions`、`access`、`executor`、`output`、`constraints`、`phases`。未知字段必须视为格式错误。

`input` 必须包含 `required` 和 `optional` 两个列表；可选 `pattern` 只能包含 `canonical`、`compatible`、`path_form`、`examples`、`unsupported`。

`access` 可以为空对象，也可以包含 `read_scope`、`write_scope`、`restrictions`。`read_scope` 和 `write_scope` 必须包含 `allowed` 列表；可选 `denied` / `forbidden` 必须是列表；可选策略字段 `no_target_path_policy`、`knowledge_base_write_policy` 必须是字符串。

`constraints` 是正式字段，可为对象或列表，用于保存不可压缩到 `risk`、`access` 或 `preconditions` 的执行约束。

## Dispatch

只有包含多个 operation 的 Contract 才能定义 `dispatch`：

```yaml
dispatch:
  required: true
  fallback: clarify
  on_ambiguous: clarify
  operations:
    create_item:
      triggers:
        - 创建条目
    remove_item:
      triggers:
        - 删除条目
```

`dispatch.operations` 必须与 `operations` 一一对应。未匹配或多重匹配都必须澄清。

## Executor

Workflow executor：

```yaml
executor:
  type: workflow
  paths:
    - workflows/example.md
  section: inspect
  load_after_validation: true
```

`section` 可选，常用于同一 workflow 文件内的 phased operation。Workflow executor 只能包含 `type`、`paths`、`section`、`load_after_validation`。

Command executor：

```yaml
executor:
  type: command
  command:
    - python
    - scripts/example.py
```

Command executor 只能包含 `type` 和 `command`，不得包含 `paths`、`section` 或 `load_after_validation`。

## 阶段操作

阶段操作不在 operation 顶层定义 executor，而是在每个 phase 中分别定义：

```yaml
phases:
  inspect:
    order: 1
    permissions:
      read: true
      write: false
    confirmation_required: false
    executor:
      type: workflow
      paths:
        - workflows/lint/lint.md
      section: inspect
      load_after_validation: true
    output:
      required:
        - lint_report

  fix:
    order: 2
    permissions:
      read: true
      write: true
    confirmation_required: true
    depends_on:
      phase: inspect
      required_outputs:
        - lint_report
    input:
      required:
        - user_confirmed
      optional: []
    constraints:
      - selected_issues_must_exist_in_lint_report
    executor:
      type: workflow
      paths:
        - workflows/lint/lint.md
      section: fix
      load_after_validation: true
    output:
      required:
        - lint_fix_report
```

每个 phase 必须单独完成资格和确认检查。

Phase 只能包含 `order`、`permissions`、`confirmation_required`、`depends_on`、`input`、`constraints`、`executor`、`output`。`depends_on` 只能包含 `phase` 和 `required_outputs`。

格式约束以 `scripts/validate_contract_format.py` 为机器权威；修改 Contract 字段前，先更新本文档和 validator，再更新具体 Contract。


