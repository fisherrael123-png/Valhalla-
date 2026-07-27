import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8-sig")


def load_json(relative_path):
    return json.loads(read_text(relative_path))


def load_yaml(relative_path):
    return yaml.safe_load(read_text(relative_path))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def require_file(relative_path):
    require((ROOT / relative_path).is_file(), f"missing file: {relative_path}")


def validate_version_markers():
    for relative_path in sorted(Path("contract").glob("**/*.yaml")):
        data = load_yaml(str(relative_path))
        require(
            data["contract"]["version"] == "0.5.11",
            f"{relative_path}: contract version must be 0.5.11",
        )


def validate_status_service():
    require_file("contract/status/status_contract.yaml")
    require_file("scripts/status.py")

    router = read_text("router/router.md")
    require("| `status` |" in router, "router must expose unified status operation")
    require(
        "`当前状态`" in router or "当前状态" in router,
        "router must route current status wording through status",
    )
    require(
        "contract\\status\\status_contract.yaml" in router,
        "router status entry must load status_contract.yaml",
    )

    command_reference = read_text("references/command_reference.md")
    require(
        "`status`" in command_reference and "系统状态" in command_reference and "知识库状态" in command_reference,
        "command reference must document unified status output",
    )


def validate_list_root_service():
    for relative_path in (
        "contract/kb_operation/list_root_contract.yaml",
        "workflows/kb/list_root.md",
        "schema/wiki_registry_schema.json",
        "template/root/wiki_registry_template.yaml",
        "template/root/wiki_registry_template.md",
    ):
        require_file(relative_path)

    router = read_text("router/router.md")
    require("| `list_root` |" in router, "router must expose list_root operation")
    require(
        "contract\\kb_operation\\list_root_contract.yaml" in router,
        "router list_root entry must load list_root_contract.yaml",
    )

    create_root = read_text("workflows/root_operation/create_root.md")
    require("wiki_registry.yaml" in create_root, "create_root must initialize wiki_registry.yaml")
    require("wiki_registry.md" in create_root, "create_root must initialize wiki_registry.md")

    create_kb = read_text("workflows/kb/create_kb.md")
    require("wiki_registry.yaml" in create_kb, "create_kb must update wiki_registry.yaml")
    require("wiki_registry.md" in create_kb, "create_kb must update wiki_registry.md")


def validate_remove_kb_service():
    require_file("contract/kb_operation/remove_kb_contract.yaml")
    require_file("workflows/kb/remove_kb.md")

    router = read_text("router/router.md")
    require("| `remove_kb` |" in router, "router must expose remove_kb operation")
    require(
        "contract\\kb_operation\\remove_kb_contract.yaml" in router,
        "router remove_kb entry must load remove_kb_contract.yaml",
    )

    command_reference = read_text("references/command_reference.md")
    require("`remove_kb`" in command_reference, "command reference must document remove_kb")
    require("不删除" in command_reference, "command reference must state remove_kb does not delete files")

    contract = load_yaml("contract/kb_operation/remove_kb_contract.yaml")
    operation = contract["operations"]["remove_kb"]
    require(
        operation["risk"]["confirmation_required"] is True,
        "remove_kb must require confirmation",
    )
    require(
        "idle" in operation["state_constraints"]["kb_status"]["allowed"],
        "remove_kb must run only when no knowledge base is active",
    )

    workflow = read_text("workflows/kb/remove_kb.md")
    for token in (
        "inspect",
        "fix",
        "wiki_registry.yaml",
        "wiki_registry.md",
        "不删除",
        "Wiki/Wiki_<知识库名>/",
        "resource_registry.yaml",
        "usage.referenced_by",
        "reference_count",
    ):
        require(token in workflow, f"remove_kb workflow must mention {token}")

    require("phases" in operation, "remove_kb must use inspect/fix phases")
    require(
        operation["phases"]["inspect"]["confirmation_required"] is False,
        "remove_kb inspect phase must be read-only without confirmation",
    )
    require(
        operation["phases"]["fix"]["confirmation_required"] is True,
        "remove_kb fix phase must require confirmation",
    )
    allowed_writes = operation["access"]["write_scope"]["allowed"]
    denied_writes = operation["access"]["write_scope"]["denied"]
    for token in ("resource_registry.yaml", "resource_registry.md"):
        require(token in allowed_writes, f"remove_kb write scope must allow {token} usage writes")
        require(token not in denied_writes, f"remove_kb write scope must not deny {token}")

    inspect_outputs = operation["phases"]["inspect"]["output"]["required"]
    for token in (
        "resource_usage_cleanup_plan",
        "affected_resource_ids",
        "orphan_candidate_resource_ids",
    ):
        require(token in inspect_outputs, f"remove_kb inspect output must include {token}")

    fix_outputs = operation["phases"]["fix"]["output"]["required"]
    require(
        "resource_usage_cleanup_report" in fix_outputs,
        "remove_kb fix output must include resource_usage_cleanup_report",
    )
    require("next_operation" in fix_outputs, "remove_kb fix output must include next_operation")


def validate_register_existing_kb_service():
    require_file("contract/kb_operation/register_existing_kb_contract.yaml")
    require_file("workflows/kb/register_existing_kb.md")

    router = read_text("router/router.md")
    require("| `register_existing_kb` |" in router, "router must expose register_existing_kb operation")
    require(
        "contract\\kb_operation\\register_existing_kb_contract.yaml" in router,
        "router register_existing_kb entry must load register_existing_kb_contract.yaml",
    )

    command_reference = read_text("references/command_reference.md")
    require(
        "`register_existing_kb`" in command_reference,
        "command reference must document register_existing_kb",
    )

    contract = load_yaml("contract/kb_operation/register_existing_kb_contract.yaml")
    operation = contract["operations"]["register_existing_kb"]
    require(
        operation["risk"]["level"] == "high",
        "register_existing_kb must be high risk",
    )
    require(
        "idle" in operation["state_constraints"]["kb_status"]["allowed"],
        "register_existing_kb must run only when no knowledge base is active",
    )
    require("phases" in operation, "register_existing_kb must use inspect/fix phases")
    require(
        operation["phases"]["fix"]["confirmation_required"] is True,
        "register_existing_kb fix phase must require confirmation",
    )

    workflow = read_text("workflows/kb/register_existing_kb.md")
    for token in (
        "wiki_registry.yaml",
        "wiki_registry.md",
        "Wiki/Wiki_<知识库名>/",
        "不创建目录",
        "不修改知识库内部文件",
        "resource_registry.yaml",
        "entity_resource_map.yaml",
        "usage.referenced_by",
        "reference_count",
    ):
        require(token in workflow, f"register_existing_kb workflow must mention {token}")

    allowed_reads = operation["access"]["read_scope"]["allowed"]
    allowed_writes = operation["access"]["write_scope"]["allowed"]
    denied_writes = operation["access"]["write_scope"]["denied"]
    for token in ("resource_registry.yaml", "resource_registry.md"):
        require(token in allowed_reads, f"register_existing_kb read scope must allow {token}")
        require(token in allowed_writes, f"register_existing_kb write scope must allow {token} usage writes")
        require(token not in denied_writes, f"register_existing_kb write scope must not deny {token}")

    precondition_ids = {item["id"] for item in operation["preconditions"]}
    require(
        "mapped_resource_ids_exist_in_resource_registry" in precondition_ids,
        "register_existing_kb must verify mapped resource ids exist in resource_registry",
    )

    inspect_outputs = operation["phases"]["inspect"]["output"]["required"]
    for token in (
        "resource_usage_sync_plan",
        "affected_resource_ids",
        "missing_resource_ids",
    ):
        require(token in inspect_outputs, f"register_existing_kb inspect output must include {token}")

    fix_outputs = operation["phases"]["fix"]["output"]["required"]
    require(
        "resource_usage_sync_report" in fix_outputs,
        "register_existing_kb fix output must include resource_usage_sync_report",
    )
    require("next_operation" in fix_outputs, "register_existing_kb fix output must include next_operation")


def validate_sync_resource_usage_service():
    require_file("contract/resource/sync_resource_usage_contract.yaml")
    require_file("workflows/resource_operation/sync_resource_usage.md")
    require_file("scripts/validate_resource_usage_canonical.py")

    router = read_text("router/router.md")
    require("| `sync_resource_usage` |" in router, "router must expose sync_resource_usage operation")
    require(
        "contract\\resource\\sync_resource_usage_contract.yaml" in router,
        "router sync_resource_usage entry must load sync_resource_usage_contract.yaml",
    )

    command_reference = read_text("references/command_reference.md")
    for token in (
        "`sync_resource_usage`",
        "同步resource usage",
        "清理历史resource usage",
    ):
        require(token in command_reference, f"command reference must document sync_resource_usage token: {token}")

    contract = load_yaml("contract/resource/sync_resource_usage_contract.yaml")
    operation = contract["operations"]["sync_resource_usage"]
    require(operation["risk"]["level"] == "high", "sync_resource_usage must be high risk")
    require(
        operation["risk"]["confirmation_required"] is False,
        "sync_resource_usage top-level confirmation must defer to phases",
    )
    require(
        {"base", "admin"} <= set(operation["state_constraints"]["os_status"]["allowed"]),
        "sync_resource_usage must be callable from base and admin os_status",
    )
    require(
        {"idle", "kb:<name>"} <= set(operation["state_constraints"]["kb_status"]["allowed"]),
        "sync_resource_usage must support idle and active-kb sessions",
    )
    require("phases" in operation, "sync_resource_usage must use inspect/fix phases")
    require(
        operation["phases"]["inspect"]["confirmation_required"] is False,
        "sync_resource_usage inspect phase must be read-only without confirmation",
    )
    require(
        operation["phases"]["fix"]["confirmation_required"] is True,
        "sync_resource_usage fix phase must require confirmation",
    )
    allowed_reads = operation["access"]["read_scope"]["allowed"]
    allowed_writes = operation["access"]["write_scope"]["allowed"]
    for token in ("wiki_registry.yaml", "resource_registry.yaml", "resource_registry.md"):
        require(token in allowed_reads, f"sync_resource_usage read scope must allow {token}")
    for token in ("resource_registry.yaml", "resource_registry.md"):
        require(token in allowed_writes, f"sync_resource_usage write scope must allow {token}")

    workflow = read_text("workflows/resource_operation/sync_resource_usage.md")
    for token in (
        "wiki_registry.yaml",
        "entity_registry.yaml",
        "entity_resource_map.yaml",
        "usage.referenced_by",
        "reference_count",
        "未注册知识库",
        "resource_registry.yaml",
        "resource_registry.md",
    ):
        require(token in workflow, f"sync_resource_usage workflow must mention {token}")

    for token in (
        "唯一权威",
        "派生反向索引",
        "`kb_name`、`entity_id`、`entity_file`",
        "旧字符串路径格式",
        "旧相对路径格式",
        "旧 `kb` 字段格式",
        "不得写入 legacy usage",
    ):
        require(token in workflow, f"sync_resource_usage workflow must define canonical usage rule: {token}")


def require_inline_resource_usage_sync(
    operation_name,
    contract_path,
    workflow_path,
    registry_tokens=("resource_registry.yaml", "resource_registry.md"),
):
    contract = load_yaml(contract_path)
    operation = contract["operations"][operation_name]
    workflow = read_text(workflow_path)

    top_outputs = set(operation["output"]["required"])
    require("next_operation" in top_outputs, f"{operation_name} output must include next_operation")
    if "phases" in operation:
        fix_outputs = set(operation["phases"]["fix"]["output"]["required"])
        require("next_operation" in fix_outputs, f"{operation_name} fix output must include next_operation")

    access = operation.get("access") or {}
    write_scope = access.get("write_scope") or {}
    allowed_writes = write_scope.get("allowed") or []
    denied_writes = write_scope.get("denied") or write_scope.get("forbidden") or []
    if write_scope:
        for token in registry_tokens:
            require(token in allowed_writes, f"{operation_name} write scope must allow {token}")
            require(token not in denied_writes, f"{operation_name} write scope must not deny {token}")

    for token in (
        "usage.referenced_by",
        "`kb_name`、`entity_id`、`entity_file`",
        "entity_resource_map.yaml",
        "entity_registry.yaml",
        "reference_count",
        "不得写入 legacy usage",
        "resource_registry.md",
        "next_operation",
        "null",
    ):
        require(token in workflow, f"{operation_name} workflow must define inline usage sync rule: {token}")
    require(
        "`sync_resource_usage`" not in workflow,
        f"{operation_name} workflow must not route usage sync to sync_resource_usage",
    )
    require(
        "sync_resource_usage_contract.yaml" not in workflow,
        f"{operation_name} workflow must not load sync_resource_usage_contract.yaml",
    )

    if operation_name == "lint":
        cleanup = operation["constraints"]["missing_entity_content_cleanup"]
        modified_files = cleanup["modified_files"]
        for token in ("resource_registry.yaml", "resource_registry.md"):
            require(
                any(token in str(item) for item in modified_files),
                f"lint missing_entity_content modified_files must include {token}",
            )
        separate_confirmation = "\n".join(operation["constraints"]["require_separate_confirmation_when"])
        require(
            "需要直接修改 resource_registry.yaml 的非 usage 字段" in separate_confirmation,
            "lint contract must distinguish resource_registry.yaml usage sync from non-usage changes",
        )


def require_ingest_inline_usage_sync():
    contract = load_yaml("contract/kb_operation/ingest_contract.yaml")
    operation = contract["operations"]["ingest"]
    write_scope = operation["access"]["write_scope"]
    allowed_writes = write_scope["allowed"]
    denied_writes = write_scope.get("denied", [])
    for token in ("resource_registry.yaml", "resource_registry.md"):
        require(token in allowed_writes, f"ingest write scope must allow {token}")
        require(token not in denied_writes, f"ingest write scope must not deny {token}")

    workflow = read_text("workflows/kb/ingest.md")
    for token in (
        "本 operation 必须同步更新 `resource_registry.yaml` 与 `resource_registry.md` 的 usage",
        ".registry/machine/entity_resource_map.yaml",
        ".registry/machine/entity_registry.yaml",
        "usage.referenced_by",
        "`kb_name`、`entity_id`、`entity_file`",
        "`reference_count` 按唯一 `(kb_name, entity_id)` 计数",
        "不得写入 legacy usage",
        "以 `resource_registry.yaml` 为唯一事实来源",
        "`next_operation` 必须为 `null`",
    ):
        require(token in workflow, f"ingest workflow must define inline usage sync rule: {token}")
    require(
        "`sync_resource_usage`" not in workflow,
        "ingest workflow must not route completed usage sync to sync_resource_usage",
    )


def validate_resource_usage_microkernel_handoffs():
    require_ingest_inline_usage_sync()
    for operation_name, contract_path, workflow_path in (
        (
            "antibody_design_ingest",
            "contract/kb_operation/antibody_design_ingest_contract.yaml",
            "workflows/kb/antibody_design_ingest.md",
        ),
        ("register_existing_kb", "contract/kb_operation/register_existing_kb_contract.yaml", "workflows/kb/register_existing_kb.md"),
        ("remove_kb", "contract/kb_operation/remove_kb_contract.yaml", "workflows/kb/remove_kb.md"),
        ("rename_kb", "contract/kb_operation/rename_kb_contract.yaml", "workflows/kb/rename_kb.md"),
        ("fuse_kbs", "contract/kb_operation/fuse_kbs_contract.yaml", "workflows/kb/fuse_kbs.md"),
        ("migrate_kb", "contract/kb_operation/migrate_kb_contract.yaml", "workflows/kb/migrate_kb.md"),
        ("lint", "contract/lint/lint_contract.yaml", "workflows/lint/lint.md"),
    ):
        require_inline_resource_usage_sync(operation_name, contract_path, workflow_path)

    root_contract = load_yaml("contract/valhalla_root_operation/root_operation_contract.yaml")
    fuse_roots = root_contract["operations"]["fuse_roots"]
    require("next_operation" in fuse_roots["output"]["required"], "fuse_roots output must include next_operation")
    fuse_roots_workflow = read_text("workflows/root_operation/fuse_roots.md")
    allowed_writes = fuse_roots["access"]["write_scope"]["allowed"]
    for token in (
        "target_root_path/resource_registry.yaml",
        "target_root_path/resource_registry.md",
    ):
        require(token in allowed_writes, f"fuse_roots write scope must allow {token}")
    for token in (
        "目标 root",
        "resource_registry.yaml/md",
        "usage.referenced_by",
        "`kb_name`、`entity_id`、`entity_file`",
        "entity_resource_map.yaml",
        "reference_count",
        "不得写入 legacy usage",
        "next_operation: null",
    ):
        require(token in fuse_roots_workflow, f"fuse_roots workflow must declare inline usage sync: {token}")
    require(
        "`sync_resource_usage`" not in fuse_roots_workflow,
        "fuse_roots workflow must not route usage sync to sync_resource_usage",
    )


def validate_resource_usage_canonical_workflows():
    required_tokens = (
        "usage.referenced_by",
        "`kb_name`、`entity_id`、`entity_file`",
        "entity_resource_map.yaml",
        "不得写入 legacy usage",
    )
    for relative_path in (
        "workflows/kb/ingest.md",
        "workflows/kb/antibody_design_ingest.md",
        "workflows/kb/fuse_kbs.md",
        "workflows/kb/migrate_kb.md",
        "workflows/kb/register_existing_kb.md",
        "workflows/kb/remove_kb.md",
        "workflows/kb/rename_kb.md",
        "workflows/lint/lint.md",
        "workflows/root_operation/fuse_roots.md",
        "workflows/resource_operation/sync_resource_usage.md",
    ):
        text = read_text(relative_path)
        for token in required_tokens:
            require(token in text, f"{relative_path} must define canonical usage rule: {token}")

    for relative_path in (
        "workflows/kb/edit_resource_table.md",
        "workflows/resource_operation/blacklist_operation.md",
    ):
        text = read_text(relative_path)
        require(
            "不修改 `usage.referenced_by`" in text or "不修改 `resource_registry.yaml`" in text,
            f"{relative_path} must not directly rebuild resource usage",
        )


def validate_ingest_entity_numbering_rule():
    ingest = read_text("workflows/kb/ingest.md")
    for token in (
        "entity_id 编号",
        ".registry/machine/entity_registry.yaml",
        "entities/ent_*.md",
        "不得从 `resource_registry.yaml`",
        "usage",
    ):
        require(token in ingest, f"ingest workflow must define local entity numbering rule token: {token}")


def validate_fuse_kbs_service():
    require_file("contract/kb_operation/fuse_kbs_contract.yaml")
    require_file("workflows/kb/fuse_kbs.md")

    router = read_text("router/router.md")
    require("| `fuse_kbs` |" in router, "router must expose fuse_kbs operation")
    require(
        "contract\\kb_operation\\fuse_kbs_contract.yaml" in router,
        "router fuse_kbs entry must load fuse_kbs_contract.yaml",
    )

    command_reference = read_text("references/command_reference.md")
    for token in (
        "`fuse_kbs`",
        "融合知识库",
        "不支持融合当前root全部知识库",
        "excluded_but_used_resources",
    ):
        require(token in command_reference, f"command reference must document fuse_kbs token: {token}")

    contract = load_yaml("contract/kb_operation/fuse_kbs_contract.yaml")
    operation = contract["operations"]["fuse_kbs"]
    require(
        operation["risk"]["level"] == "high",
        "fuse_kbs must be high risk",
    )
    require(
        operation["risk"]["confirmation_required"] is False,
        "fuse_kbs top-level confirmation must defer to phases",
    )
    require(
        "admin" in operation["state_constraints"]["os_status"]["allowed"],
        "fuse_kbs must require admin os_status",
    )
    require(
        "idle" in operation["state_constraints"]["kb_status"]["allowed"],
        "fuse_kbs must run only when no knowledge base is active",
    )
    require("phases" in operation, "fuse_kbs must use inspect/fix phases")
    require(
        operation["phases"]["inspect"]["confirmation_required"] is False,
        "fuse_kbs inspect phase must be read-only without confirmation",
    )
    require(
        operation["phases"]["fix"]["confirmation_required"] is True,
        "fuse_kbs fix phase must require confirmation",
    )
    require(
        "resource_registry.yaml" in operation["access"]["write_scope"]["allowed"],
        "fuse_kbs must allow root resource_registry.yaml usage writes",
    )
    require(
        "Library/" in operation["access"]["write_scope"]["denied"],
        "fuse_kbs must deny Library writes",
    )

    workflow = read_text("workflows/kb/fuse_kbs.md")
    for token in (
        "inspect",
        "fix",
        "融合知识库 <来源知识库列表> 为 <新知识库>",
        "不支持融合当前root全部知识库",
        "entity",
        "relationship",
        "conversation_entity",
        "engineering_entity",
        "knowledge_graph",
        "entity_id_map",
        "excluded_but_used_resources",
        "source KB 全程只读",
        "正向集合",
        "证据集合",
        "排除集合",
        "merge_content",
        "pick_one",
        "append_content",
    ):
        require(token in workflow, f"fuse_kbs workflow must mention {token}")


def validate_migrate_kb_service():
    require_file("contract/kb_operation/migrate_kb_contract.yaml")
    require_file("workflows/kb/migrate_kb.md")

    router = read_text("router/router.md")
    require("| `migrate_kb` |" in router, "router must expose migrate_kb operation")
    require(
        "contract\\kb_operation\\migrate_kb_contract.yaml" in router,
        "router migrate_kb entry must load migrate_kb_contract.yaml",
    )

    command_reference = read_text("references/command_reference.md")
    for token in (
        "`migrate_kb`",
        "迁移知识库",
        "目标 root 永远是当前 root",
        "新名称",
        "不会自动启动",
    ):
        require(token in command_reference, f"command reference must document migrate_kb token: {token}")

    contract = load_yaml("contract/kb_operation/migrate_kb_contract.yaml")
    operation = contract["operations"]["migrate_kb"]
    require(operation["risk"]["level"] == "high", "migrate_kb must be high risk")
    require(
        operation["risk"]["confirmation_required"] is False,
        "migrate_kb top-level confirmation must defer to phases",
    )
    require(
        "admin" in operation["state_constraints"]["os_status"]["allowed"],
        "migrate_kb must require admin os_status",
    )
    require(
        "idle" in operation["state_constraints"]["kb_status"]["allowed"],
        "migrate_kb must run only when no knowledge base is active",
    )
    require("phases" in operation, "migrate_kb must use inspect/fix phases")
    require(
        operation["phases"]["inspect"]["confirmation_required"] is False,
        "migrate_kb inspect phase must be read-only without confirmation",
    )
    require(
        operation["phases"]["fix"]["confirmation_required"] is True,
        "migrate_kb fix phase must require confirmation",
    )

    allowed_writes = operation["access"]["write_scope"]["allowed"]
    for token in (
        "resource_registry.yaml",
        "resource_registry.md",
        "wiki_registry.yaml",
        "wiki_registry.md",
        "Library/public_resources/<target_resource_id>/",
        "Wiki/Wiki_<target_kb_name>/",
    ):
        require(token in allowed_writes, f"migrate_kb write scope must allow {token}")

    denied_writes = operation["access"]["write_scope"]["denied"]
    for token in (
        "any source root file or directory",
        "any source KB file or directory",
        "blacklist_registry.yaml",
        "blacklist_registry.md",
        ".valhalla/kb_status.md",
    ):
        require(token in denied_writes, f"migrate_kb write scope must deny {token}")

    workflow = read_text("workflows/kb/migrate_kb.md")
    for token in (
        "inspect",
        "fix",
        "目标 root 永远是当前 root",
        "root2:ai工程",
        "新名称",
        "source root 全程只读",
        "resource_id_map",
        "reuse_current",
        "create_new",
        "blocked_identity_conflict",
        "blacklist_delta",
        "local_exclusions_added",
        "register_existing_kb",
        "migration_written_but_not_registered",
        "不会自动启动",
    ):
        require(token in workflow, f"migrate_kb workflow must mention {token}")


def validate_kb_layout_contract():
    create_kb = read_text("workflows/kb/create_kb.md")
    required_tokens = (
        ".registry/",
        ".registry/machine/",
        ".registry/human/",
        ".virtualDatabase/",
        ".virtualDatabase/machine/",
        ".virtualDatabase/human/",
    )
    for token in required_tokens:
        require(token in create_kb, f"create_kb must describe {token}")

    machine_registries = (
        "entity_registry",
        "entity_resource_map",
        "relationship_registry",
        "knowledge_graph_registry",
        "conversation_entity_registry",
        "engineering_entity_registry",
    )
    for name in machine_registries:
        require(
            f".registry/machine/{name}.yaml" in create_kb,
            f"create_kb must create machine registry {name}.yaml",
        )
        require(
            f".registry/human/{name}.md" in create_kb,
            f"create_kb must create human registry {name}.md",
        )

    for table_name in ("local_resources", "required_resources", "excluded_resources"):
        require(
            f".virtualDatabase/machine/{table_name}.yaml" in create_kb,
            f"create_kb must create machine table {table_name}.yaml",
        )
        require(
            f".virtualDatabase/human/{table_name}.md" in create_kb,
            f"create_kb must create human table {table_name}.md",
        )


def validate_templates_for_human_projection():
    human_templates = (
        "template/knowledge_base/entity/entity_registry_template.md",
        "template/resource/entity_resource_map_template.md",
        "template/knowledge_base/relationship/relationship_registry_template.md",
        "template/knowledge_base/relationship/relationship_fact_file_template.md",
        "template/knowledge_base/knowledge_graph/knowledge_graph_registry_template.md",
        "template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.md",
        "template/knowledge_base/conversation/conversation_entity_registry_template.md",
        "template/knowledge_base/engineering/engineering_entity_registry_template.md",
    )
    for relative_path in human_templates:
        require_file(relative_path)
        text = read_text(relative_path)
        require("YAML" in text, f"{relative_path} must name the YAML authority")
        require("人类可读" in text, f"{relative_path} must describe human-readable projection")


def validate_contract_paths():
    path_tokens = (
        ".registry/machine/entity_registry.yaml",
        ".registry/human/entity_registry.md",
        ".registry/machine/entity_resource_map.yaml",
        ".registry/human/entity_resource_map.md",
        ".registry/machine/relationship_registry.yaml",
        ".registry/human/relationship_registry.md",
        ".registry/machine/knowledge_graph_registry.yaml",
        ".registry/human/knowledge_graph_registry.md",
        ".registry/machine/conversation_entity_registry.yaml",
        ".registry/human/conversation_entity_registry.md",
        ".registry/machine/engineering_entity_registry.yaml",
        ".registry/human/engineering_entity_registry.md",
        ".virtualDatabase/machine/local_resources.yaml",
        ".virtualDatabase/human/local_resources.md",
        ".virtualDatabase/machine/required_resources.yaml",
        ".virtualDatabase/human/required_resources.md",
        ".virtualDatabase/machine/excluded_resources.yaml",
        ".virtualDatabase/human/excluded_resources.md",
    )

    checked_files = (
        "contract/project_work/project_work_contract.yaml",
        "contract/kb_operation/query_contract.yaml",
        "contract/kb_operation/ingest_contract.yaml",
        "contract/kb_operation/edit_resource_table_contract.yaml",
        "contract/kb_operation/relate_entities_contract.yaml",
        "contract/kb_operation/edit_knowledge_graph_contract.yaml",
        "contract/kb_operation/ingest_conversation_contract.yaml",
        "contract/kb_operation/ingest_engineering_contract.yaml",
        "workflows/project_work/project_work.md",
        "workflows/kb/query.md",
        "workflows/kb/ingest.md",
        "workflows/kb/edit_resource_table.md",
        "workflows/kb/relate_entities.md",
        "workflows/kb/edit_knowledge_graph.md",
        "workflows/kb/ingest_conversation.md",
        "workflows/kb/ingest_engineering_entity.md",
    )

    combined = "\n".join(read_text(relative_path) for relative_path in checked_files)
    for token in path_tokens:
        require(token in combined, f"runtime contract/workflow text is missing {token}")


def validate_relationship_and_graph_fact_layout():
    create_kb = read_text("workflows/kb/create_kb.md")
    for token in (
        "relationships/machine/",
        "relationships/human/",
        "knowledge_graph/machine/",
        "knowledge_graph/human/",
        "relationship_fact_file_template.yaml",
        "knowledge_graph_fact_template.yaml",
    ):
        require(token in create_kb, f"create_kb is missing fact layout token: {token}")

    for relative_path in (
        "template/knowledge_base/relationship/relationship_registry_template.yaml",
        "template/knowledge_base/relationship/relationship_registry_template.md",
        "template/knowledge_base/relationship/relationship_fact_file_template.yaml",
        "template/knowledge_base/relationship/relationship_fact_file_template.md",
        "template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.yaml",
        "template/knowledge_base/knowledge_graph/knowledge_graph_fact_template.md",
        "schema/relationship_fact_file_schema.json",
        "schema/knowledge_graph_registry_schema.json",
        "schema/knowledge_graph_fact_schema.json",
    ):
        require_file(relative_path)

    relate_contract = load_yaml("contract/kb_operation/relate_entities_contract.yaml")
    relate_allowed = relate_contract["operations"]["relate_entities"]["access"]["write_scope"]["allowed"]
    for token in (
        "Wiki/Wiki_<知识库名>/.registry/machine/relationship_registry.yaml",
        "Wiki/Wiki_<知识库名>/.registry/human/relationship_registry.md",
        "Wiki/Wiki_<知识库名>/relationships/machine/*.yaml",
        "Wiki/Wiki_<知识库名>/relationships/human/*.md",
    ):
        require(token in relate_allowed, f"relate_entities write scope is missing: {token}")

    graph_contract = load_yaml("contract/kb_operation/edit_knowledge_graph_contract.yaml")
    graph_allowed = graph_contract["operations"]["edit_knowledge_graph"]["access"]["write_scope"]["allowed"]
    for token in (
        "Wiki/Wiki_*/.registry/machine/knowledge_graph_registry.yaml",
        "Wiki/Wiki_*/.registry/human/knowledge_graph_registry.md",
        "Wiki/Wiki_*/knowledge_graph/machine/*.yaml",
        "Wiki/Wiki_*/knowledge_graph/human/*.md",
    ):
        require(token in graph_allowed, f"edit_knowledge_graph write scope is missing: {token}")

def main():
    validate_version_markers()
    validate_status_service()
    validate_list_root_service()
    validate_remove_kb_service()
    validate_register_existing_kb_service()
    validate_sync_resource_usage_service()
    validate_resource_usage_microkernel_handoffs()
    validate_resource_usage_canonical_workflows()
    validate_ingest_entity_numbering_rule()
    validate_fuse_kbs_service()
    validate_migrate_kb_service()
    validate_kb_layout_contract()
    validate_templates_for_human_projection()
    validate_contract_paths()
    validate_relationship_and_graph_fact_layout()
    print("PASS: Valhalla 0.5.11 structure is synchronized")


if __name__ == "__main__":
    main()
