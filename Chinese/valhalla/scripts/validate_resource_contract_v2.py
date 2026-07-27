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


def validate_resource_registry_schema():
    schema = load_json("schema/resource_registry_schema.json")
    require(schema["properties"]["version"]["const"] == 2, "resource registry must be version 2")

    resource = schema["properties"]["resources"]["items"]
    required = set(resource["required"])
    require(
        {"resource_id", "identity", "representations", "lifecycle", "usage", "policy"} <= required,
        "resource entry is missing v2 identity or lifecycle sections",
    )

    properties = resource["properties"]
    require("primary_path" not in properties, "legacy primary_path must be removed")
    require("original_paths" not in properties, "legacy original_paths must be removed")
    require("duplicate_paths" not in properties, "legacy duplicate_paths must be removed")

    identity = properties["identity"]
    require(
        {"canonical_name", "aliases", "information_identity"} <= set(identity["required"]),
        "identity must define one canonical name, aliases, and information identity",
    )

    representation = properties["representations"]["items"]
    require(
        {"file_id", "representation_type", "source_copies", "public_copy", "sync_status"}
        <= set(representation["required"]),
        "representation must define files, source copies, public copy, and sync status",
    )

    usage = properties["usage"]
    referenced_by = usage["properties"]["referenced_by"]
    usage_ref = referenced_by["items"]
    require(
        usage_ref["type"] == "object",
        "usage.referenced_by entries must be structured objects, not legacy strings",
    )
    require(
        set(usage_ref["required"]) == {"kb_name", "entity_id", "entity_file"},
        "usage.referenced_by entries must require kb_name, entity_id, and entity_file",
    )
    require(
        usage_ref["additionalProperties"] is False,
        "usage.referenced_by entries must reject legacy or unknown fields",
    )
    usage_ref_properties = usage_ref["properties"]
    require(
        "kb" not in usage_ref_properties,
        "usage.referenced_by schema must reject legacy kb fields",
    )
    require(
        usage_ref_properties["kb_name"]["type"] == "string",
        "usage.referenced_by.kb_name must be a string",
    )
    require(
        usage_ref_properties["entity_id"]["pattern"] == "^ent_[0-9]{6}$",
        "usage.referenced_by.entity_id must be an entity id",
    )
    require(
        usage_ref_properties["entity_file"]["pattern"]
        == "^Wiki/Wiki_[^/\\\\]+/entities/ent_[0-9]{6}[^/]*\\.md$",
        "usage.referenced_by.entity_file must be a full Wiki entity path",
    )


def validate_templates():
    registry = load_yaml("template/resource/resource_registry_template.yaml")
    require(registry["version"] == 2, "resource registry template must be version 2")
    require(registry["registry"] == "resource_registry", "registry name is missing")

    human_registry = read_text("template/resource/resource_registry_template.md")
    require(
        human_registry.startswith("# resource_registry"),
        "human resource registry template must use the resource_registry name",
    )
    require(
        "`resource_registry.yaml`" in human_registry,
        "human resource registry must identify its YAML authority",
    )

    entry_text = read_text("template/resource/resource_entry_template.yaml")
    for token in (
        "canonical_name:",
        "aliases:",
        "representations:",
        "source_copies:",
        "public_copy:",
        "reference_count:",
        "blacklist_status:",
    ):
        require(token in entry_text, f"resource entry template is missing {token}")

    for legacy in ("primary_path:", "original_paths:", "duplicate_paths:"):
        require(legacy not in entry_text, f"resource entry template still contains {legacy}")


def validate_upper_layers_use_resource_ids():
    table_schema = load_json("schema/resource_table_schema.json")
    item = table_schema["properties"]["resources"]["items"]
    require(
        {
            "resource_id",
            "membership_status",
            "added_via",
            "added_at",
            "removed_at",
            "note",
        }
        == set(item["required"]),
        "machine resource tables must include membership state and input audit fields",
    )
    require("resource_path" not in item["properties"], "resource_path leaked above the resource layer")
    require(
        item["properties"]["membership_status"]["enum"] == ["active", "pending_removal"],
        "resource table membership states must be active and pending_removal",
    )
    require(
        len(item["allOf"]) == 2,
        "resource table schema must couple membership status to removed_at",
    )

    registry_template = load_yaml("template/knowledge_base/resource_table_registry_template.yaml")
    require(registry_template["table"]["version"] == 3, "machine resource table template must be version 3")
    require(registry_template["resources"] == [], "machine resource table template must start empty")

    entry_template = load_yaml("template/knowledge_base/resource_table_entry_template.yaml")[0]
    require(entry_template["membership_status"] == "active", "new resource membership must be active")
    require("added_via" in entry_template, "resource membership must preserve the user's original input")
    require(entry_template["removed_at"] is None, "active resource membership must not have removed_at")

    human_template = read_text("template/knowledge_base/resource_table_template.md")
    for token in (
        "人类可读投影视图",
        "加入时输入",
        "当前来源路径",
        "成员状态",
        "待清理",
    ):
        require(token in human_template, f"human resource table template is missing {token}")
    require("resources: []" not in human_template, "human resource table must not embed machine YAML")

    for relative_path in (
        "template/knowledge_base/resource_table_entry_template.yaml",
        "template/knowledge_base/resource_table_template.md",
        "workflows/kb/edit_resource_table.md",
    ):
        text = read_text(relative_path)
        require("resource_path" not in text, f"{relative_path} still uses resource_path")

    entity_paths = (
        "schema/entity_registry_schema.json",
        "schema/entity_resource_map_schema.json",
        "template/knowledge_base/entity/entity_entry_template.yaml",
        "template/resource/entity_resource_map_entry_template.yaml",
    )
    for relative_path in entity_paths:
        text = read_text(relative_path)
        for leaked_field in ("primary_path", "original_paths", "duplicate_paths", "source_copies", "public_copy"):
            require(leaked_field not in text, f"{leaked_field} leaked into {relative_path}")


def validate_dual_resource_table_workflow():
    create_workflow = read_text("workflows/kb/create_kb.md")
    for table_name in ("local_resources", "required_resources", "excluded_resources"):
        require(f"{table_name}.yaml" in create_workflow, f"create_kb must create {table_name}.yaml")
        require(f"{table_name}.md" in create_workflow, f"create_kb must create {table_name}.md")

    edit_workflow = read_text("workflows/kb/edit_resource_table.md")
    for token in (
        "YAML",
        "Markdown",
        "增量追加",
        "membership_status: active",
        "membership_status: pending_removal",
        "不完整重建",
        "removed_at",
    ):
        require(token in edit_workflow, f"edit resource table workflow is missing {token}")

    ingest_workflow = read_text("workflows/kb/ingest.md")
    require(
        "membership_status == active" in ingest_workflow,
        "effective corpus must only include active memberships",
    )

    lint_workflow = read_text("workflows/lint/lint.md")
    for token in (
        "pending_removal",
        "批量",
        "当前来源路径",
        "物理移除",
        "Markdown",
    ):
        require(token in lint_workflow, f"lint workflow is missing resource-table cleanup rule: {token}")

    edit_contract = load_yaml("contract/kb_operation/edit_resource_table_contract.yaml")
    outputs = set(
        edit_contract["operations"]["edit_resource_table"]["output"]["required"]
    )
    require(
        {"machine_table", "human_table", "membership_status"} <= outputs,
        "edit resource table contract must report both table files and membership status",
    )

    project_contract = load_yaml("contract/project_work/project_work_contract.yaml")
    allowed = project_contract["operations"]["project_work"]["access"]["read_scope"]["allowed"]
    for table_name in ("local_resources", "required_resources", "excluded_resources"):
        require(
            f"Wiki/Wiki_<知识库名>/.virtualDatabase/machine/{table_name}.yaml" in allowed,
            f"project work must read machine table {table_name}.yaml",
        )

    skill_text = read_text("SKILL.md")
    require(
        "YAML 资料表" in skill_text
        and "Markdown 人类投影" in skill_text
        and "membership_status: active" in skill_text,
        "top-level skill must describe dual resource tables and active membership authority",
    )


def validate_blacklist_contract():
    schema = load_json("schema/blacklist_registry_schema.json")
    schema_entry = schema["properties"]["entries"]["items"]
    require(
        {"blacklist_id", "resource_id", "matched_input"} <= set(schema_entry["required"]),
        "blacklist schema must bind the human input to a stable resource_id",
    )
    require(
        "resource_path" not in schema_entry["properties"],
        "blacklist schema must not use a path as stable identity",
    )

    template = load_yaml("template/resource_operation/blacklist_registry_template.yaml")
    entry = template["entries"][0]
    require("resource_id" in entry, "blacklist entry must bind a resource_id")
    require("matched_input" in entry, "blacklist entry must preserve the user's filename or path input")
    require("resource_path" not in entry, "resource_path must not be the blacklist identity")

    workflow = read_text("workflows/resource_operation/blacklist_operation.md")
    for token in (
        "文件名",
        "resource_id",
        "整个资源",
        "多个候选",
        "不得自动选择",
    ):
        require(token in workflow, f"blacklist workflow is missing rule: {token}")

    require(
        "所有文件副本移至" not in workflow,
        "blacklisting must not automatically move every source copy",
    )

    contract = load_yaml("contract/resource/blacklist_operation_contract.yaml")
    add_operation = contract["operations"]["add_blacklist"]
    require(
        "resource_query" in add_operation["input"]["required"],
        "blacklist contract must accept a human filename or path query",
    )
    require(
        "resource_path" not in add_operation["input"]["required"],
        "blacklist contract must not require a stable path identity",
    )


def validate_workflows():
    register_workflow = read_text("workflows/resource_operation/register_resource.md")
    for token in (
        "Library/",
        "resource_id",
        "canonical_name",
        "representations",
        "无法确认",
        "不得自动合并",
    ):
        require(token in register_workflow, f"register workflow is missing rule: {token}")

    ingest_workflow = read_text("workflows/kb/ingest.md")
    require(
        "resource_id" in ingest_workflow and "资料表" in ingest_workflow,
        "ingest must connect knowledge-base tables through resource_id",
    )

    for relative_path in (
        "SKILL.md",
        "references/system_overview.md",
        "workflows/root_operation/create_root.md",
        "workflows/resource_operation/register_resource.md",
        "contract/resource/register_resource_contract.yaml",
        "contract/kb_operation/edit_knowledge_graph_contract.yaml",
    ):
        text = read_text(relative_path)
        require(
            "文件副本映射表" not in text,
            f"legacy human registry name remains in {relative_path}",
        )

    create_root_workflow = read_text("workflows/root_operation/create_root.md")
    require(
        "resource_registry.md" in create_root_workflow,
        "create_root must initialize resource_registry.md",
    )

    skill_text = read_text("SKILL.md")
    require(
        "`resource_registry.yaml` 是资源层机器权威表" in skill_text
        and "`resource_registry.md`" in skill_text,
        "top-level skill must define YAML authority and Markdown projection",
    )

    lint_workflow = read_text("workflows/lint/lint.md")
    for token in (
        "resource_registry.md 批量同步",
        "以 `resource_registry.yaml` 为唯一事实来源",
        "不得从 Markdown 反向覆盖 YAML",
    ):
        require(token in lint_workflow, f"lint workflow is missing registry synchronization rule: {token}")


def validate_ascii_runtime_paths():
    create_root = read_text("workflows/root_operation/create_root.md")
    for token in ("orphan_resources.md", "Library/", "public_resources/"):
        require(token in create_root, f"create_root is missing ASCII runtime path: {token}")
    for legacy in ("孤儿索引.md", "公共资料库/"):
        require(legacy not in create_root, f"create_root still uses legacy runtime path: {legacy}")

    create_kb = read_text("workflows/kb/create_kb.md")
    runtime_tables = (
        ".virtualDatabase/machine/local_resources.yaml",
        ".virtualDatabase/human/local_resources.md",
        ".virtualDatabase/machine/required_resources.yaml",
        ".virtualDatabase/human/required_resources.md",
        ".virtualDatabase/machine/excluded_resources.yaml",
        ".virtualDatabase/human/excluded_resources.md",
    )
    for filename in runtime_tables:
        require(filename in create_kb, f"create_kb is missing ASCII resource table: {filename}")
    for legacy in (
        "本库资料表.yaml",
        "本库资料表.md",
        "必须资料表.yaml",
        "必须资料表.md",
        "剔除资料表.yaml",
        "剔除资料表.md",
    ):
        require(legacy not in create_kb, f"create_kb still uses legacy table filename: {legacy}")

    table_schema = load_json("schema/resource_table_schema.json")
    table_names = table_schema["properties"]["table"]["properties"]["name"]["enum"]
    require(
        table_names == ["local_resources", "required_resources", "excluded_resources"],
        "resource table names must use stable ASCII identifiers",
    )

    resource_schema = read_text("schema/resource_registry_schema.json")
    blacklist_schema = read_text("schema/blacklist_registry_schema.json")
    for schema_name, schema_text in (
        ("resource registry", resource_schema),
        ("blacklist registry", blacklist_schema),
    ):
        require("public_resources" in schema_text, f"{schema_name} schema is missing public_resources")
        require("公共资料库" not in schema_text, f"{schema_name} schema still uses the Chinese directory")

    runtime_contract_files = (
        "SKILL.md",
        "references/system_overview.md",
        "contract/project_work/project_work_contract.yaml",
        "contract/resource/blacklist_operation_contract.yaml",
        "contract/resource/register_resource_contract.yaml",
        "contract/kb_operation/edit_knowledge_graph_contract.yaml",
        "contract/kb_operation/edit_resource_table_contract.yaml",
        "workflows/kb/ingest.md",
        "workflows/kb/edit_resource_table.md",
        "workflows/project_work/project_work.md",
        "workflows/resource_operation/register_resource.md",
        "workflows/resource_operation/blacklist_operation.md",
        "workflows/lint/lint.md",
        "template/resource/resource_entry_template.yaml",
        "template/resource/resource_registry_template.md",
        "template/knowledge_base/resource_table_registry_template.yaml",
    )
    legacy_path_tokens = (
        "Library/公共资料库",
        "孤儿索引.md",
        "本库资料表.yaml",
        "本库资料表.md",
        "必须资料表.yaml",
        "必须资料表.md",
        "剔除资料表.yaml",
        "剔除资料表.md",
    )
    for relative_path in runtime_contract_files:
        text = read_text(relative_path)
        for legacy in legacy_path_tokens:
            require(legacy not in text, f"{relative_path} still uses runtime path {legacy}")


def validate_service_handoff_and_query_contract():
    skill = read_text("SKILL.md")
    for token in (
        "Workflow 需要执行其他 operation 时",
        "返回 Router",
        "确认不得继承",
        "只通过 Contract 声明的正式输出传递结果",
    ):
        require(token in skill, f"SKILL.md is missing service handoff rule: {token}")

    ingest = read_text("workflows/kb/ingest.md")
    require(
        "未登记时先执行 `register_resource`" not in ingest,
        "ingest must not directly execute register_resource",
    )
    for token in (
        "暂停当前 `ingest` operation",
        "返回 Router",
        "register_resource_contract.yaml",
        "重新加载并校验 `ingest_contract.yaml`",
        "不得直接加载或执行 `register_resource.md`",
        "未取得稳定 `resource_id` 时不得执行任何知识库写入",
    ):
        require(token in ingest, f"ingest handoff workflow is missing: {token}")

    ingest_contract = load_yaml("contract/kb_operation/ingest_contract.yaml")
    ingest_outputs = set(
        ingest_contract["operations"]["ingest"]["output"]["required"]
    )
    require(
        {
            "completion_status",
            "completed_resource_ids",
            "skipped_resource_queries",
            "registration_results",
            "failed_resources",
            "next_operation",
        }
        <= ingest_outputs,
        "ingest contract is missing handoff and partial-result outputs",
    )

    query_contract = load_yaml("contract/kb_operation/query_contract.yaml")
    query_operation = query_contract["operations"]["query"]
    require(
        "query_text" in query_operation["input"]["required"],
        "query contract must require query_text",
    )
    require(
        {"query_scope", "allow_network_search"}
        <= set(query_operation["input"]["optional"]),
        "query contract must define query scope and network-search control",
    )

    read_scope = query_operation["access"]["read_scope"]["allowed"]
    for required_path in (
        "Wiki/Wiki_<知识库名>/.registry/machine/entity_registry.yaml",
        "Wiki/Wiki_<知识库名>/entities/",
        "Wiki/Wiki_<知识库名>/.registry/machine/relationship_registry.yaml",
        "Wiki/Wiki_<知识库名>/.registry/machine/knowledge_graph_registry.yaml",
        "Wiki/Wiki_<知识库名>/knowledge_graph/",
        "Wiki/Wiki_<知识库名>/.registry/machine/conversation_entity_registry.yaml",
        "Wiki/Wiki_<知识库名>/conversation_entities/",
        "Wiki/Wiki_<知识库名>/.registry/machine/engineering_entity_registry.yaml",
        "Wiki/Wiki_<知识库名>/engineering_entities/",
        "Wiki/Wiki_<知识库名>/.virtualDatabase/machine/local_resources.yaml",
        "Wiki/Wiki_<知识库名>/.virtualDatabase/machine/required_resources.yaml",
        "Wiki/Wiki_<知识库名>/.virtualDatabase/machine/excluded_resources.yaml",
        "resource_registry.yaml",
        "blacklist_registry.yaml",
        "Library/public_resources/",
    ):
        require(
            required_path in read_scope,
            f"query contract read scope is missing: {required_path}",
        )

    require(
        {
            "answer",
            "target_kb",
            "knowledge_used",
            "source_records",
            "external_sources",
            "inferences",
            "conflicts",
            "uncertainty",
            "suggested_follow_up",
        }
        <= set(query_operation["output"]["required"]),
        "query contract is missing traceable query outputs",
    )

    query = read_text("workflows/kb/query.md")
    for token in (
        "membership_status == active",
        ".virtualDatabase/machine/excluded_resources.yaml",
        "blacklist_registry.yaml",
        "Library/public_resources/",
        "allow_network_search",
        "外部临时资料",
        "resource_id → entity_id → evidence_location → supported_claim",
    ):
        require(token in query, f"query workflow is missing: {token}")


def validate_antibody_design_ingest_is_decoupled():
    workflow = read_text("workflows/kb/antibody_design_ingest.md")
    forbidden_tokens = (
        "领域专用变体",
        "完整遵守 `ingest.md`",
        "workflows/kb/ingest.md",
    )
    for token in forbidden_tokens:
        require(
            token not in workflow,
            f"antibody_design_ingest workflow must be self-contained, found coupled token: {token}",
        )

    for token in (
        "自包含系统服务",
        "资源解析与服务转交",
        "register_resource_contract.yaml",
        "不得直接加载或执行 `register_resource.md`",
        "重新加载并校验 `antibody_design_ingest_contract.yaml`",
        "references/valhalla_entity_template_antibody_protein_design.md",
        "资料中的分子字符串可以作为已发表文献事实处理",
        "不得要求模型基于这些字符串生成、优化、补全、改造、筛选或设计新分子",
        "长串原文片段不得集中复制进提示词",
        "不得记录可执行湿实验步骤、实验条件、培养/表达/筛选参数、载体/引物构建步骤",
        "entity_resource_map.yaml",
        "usage.referenced_by",
        "reference_count",
        "next_operation",
    ):
        require(token in workflow, f"antibody_design_ingest workflow is missing self-contained rule: {token}")

    contract = load_yaml("contract/kb_operation/antibody_design_ingest_contract.yaml")
    operation = contract["operations"]["antibody_design_ingest"]
    read_scope = operation["access"]["read_scope"]["allowed"]
    require(
        "workflows/kb/ingest.md" not in read_scope,
        "antibody_design_ingest contract must not read workflows/kb/ingest.md",
    )
    require(
        "references/valhalla_entity_template_antibody_protein_design.md" in read_scope,
        "antibody_design_ingest contract must read the antibody design template",
    )


def validate_help_navigation():
    skill = read_text("SKILL.md")
    for token in (
        "Router 分类为 `help` 或 `ordinary_file_work` 时，不加载 Contract",
        "## Reference 与 Help",
        "不明确时，只显示帮助菜单",
        "references/system_overview.md",
        "references/command_reference.md",
        "references/bootstrap.md",
        "references/contract_format.md",
        "Help 只解释系统和导航文档，不执行业务 operation",
    ):
        require(token in skill, f"SKILL.md is missing help navigation rule: {token}")

    router = read_text("router/router.md")
    require("| `help` |" in router, "router is missing the help category")
    require(
        "不加载 Contract" in router and "Reference" in router,
        "help router entry must directly navigate references without a Contract",
    )

    command_reference = read_text("references/command_reference.md")
    for token in (
        "### Help 导航",
        "`help`",
        "系统概览",
        "命令与使用方法",
        "Bootstrap 启动过程",
        "Contract 格式与执行机制",
    ):
        require(
            token in command_reference,
            f"command reference is missing help documentation: {token}",
        )


def validate_command_and_knowledge_contract_closure():
    command_reference = read_text("references/command_reference.md")
    for operation in (
        "register_resource",
        "admin_enter",
        "admin_exit",
        "list_blacklist",
        "add_blacklist",
        "remove_blacklist",
        "lint_fix",
        "init_engineering_entities",
    ):
        require(
            f"`{operation}`" in command_reference,
            f"command reference is missing user-callable operation: {operation}",
        )

    ingest = read_text("workflows/kb/ingest.md")
    for token in (
        ".registry/machine/entity_registry.yaml",
        ".registry/human/entity_registry.md",
        "机器权威",
        "人类可读投影",
        "不得从 Markdown 反向覆盖 YAML",
    ):
        require(token in ingest, f"ingest entity registry sync is missing: {token}")

    ingest_contract = load_yaml("contract/kb_operation/ingest_contract.yaml")
    ingest_access = ingest_contract["operations"]["ingest"]["access"]
    read_allowed = ingest_access["read_scope"]["allowed"]
    write_allowed = ingest_access["write_scope"]["allowed"]
    for relative_path in (
        "Wiki/Wiki_<知识库名>/.registry/machine/entity_registry.yaml",
        "Wiki/Wiki_<知识库名>/.registry/human/entity_registry.md",
    ):
        require(relative_path in read_allowed, f"ingest read scope is missing: {relative_path}")
        require(relative_path in write_allowed, f"ingest write scope is missing: {relative_path}")

    relationship_registry_schema = load_json("schema/relationship_registry_schema.json")
    require(
        "relationship_fact_files" in relationship_registry_schema["properties"],
        "relationship registry must index relationship fact files",
    )
    require(
        "relationships" not in relationship_registry_schema["properties"],
        "relationship registry must not store all concrete relationship facts directly",
    )

    relationship_fact_schema = load_json("schema/relationship_fact_file_schema.json")
    relationship = relationship_fact_schema["properties"]["relationships"]["items"]
    relationship_required = set(relationship["required"])
    require(
        {
            "relationship_id",
            "subject_entity_id",
            "object_entity_id",
            "predicate",
            "evidence",
        }
        <= relationship_required,
        "relationship fact file must store concrete entity edges with evidence",
    )

    relate_contract = load_yaml("contract/kb_operation/relate_entities_contract.yaml")
    relate_access = relate_contract["operations"]["relate_entities"]["access"]
    for required_path in (
        "Wiki/Wiki_<知识库名>/.registry/machine/relationship_registry.yaml",
        "Wiki/Wiki_<知识库名>/.registry/human/relationship_registry.md",
        "Wiki/Wiki_<知识库名>/relationships/machine/*.yaml",
        "Wiki/Wiki_<知识库名>/relationships/human/*.md",
    ):
        require(
            required_path in relate_access["write_scope"]["allowed"],
            f"relate_entities write scope is missing: {required_path}",
        )

    relate_workflow = read_text("workflows/kb/relate_entities.md")
    for token in (
        "subject_entity_id",
        "object_entity_id",
        "predicate",
        "evidence",
        "relationships/machine/<predicate_id>.yaml",
        "relationships/human/<predicate_id>.md",
        ".registry/human/relationship_registry.md",
        "不调用 `edit_knowledge_graph`",
    ):
        require(token in relate_workflow, f"relate_entities fact workflow is missing: {token}")

    graph_registry_schema = load_json("schema/knowledge_graph_registry_schema.json")
    require("graphs" in graph_registry_schema["properties"], "graph registry must index graph fact files")

    graph_fact_schema = load_json("schema/knowledge_graph_fact_schema.json")
    for token in ("relationship_sources", "included_relationships", "included_entities", "provenance"):
        require(token in graph_fact_schema["properties"], f"graph fact schema is missing: {token}")

    graph_contract = load_yaml("contract/kb_operation/edit_knowledge_graph_contract.yaml")
    graph_access = graph_contract["operations"]["edit_knowledge_graph"]["access"]
    for required_path in (
        "Wiki/Wiki_*/.registry/machine/knowledge_graph_registry.yaml",
        "Wiki/Wiki_*/.registry/human/knowledge_graph_registry.md",
        "Wiki/Wiki_*/knowledge_graph/machine/*.yaml",
        "Wiki/Wiki_*/knowledge_graph/human/*.md",
    ):
        require(
            required_path in graph_access["write_scope"]["allowed"],
            f"edit_knowledge_graph write scope is missing: {required_path}",
        )

    for denied_path in (
        "Wiki/Wiki_*/.registry/machine/relationship_registry.yaml",
        "Wiki/Wiki_*/.registry/human/relationship_registry.md",
        "Wiki/Wiki_*/relationships/machine/*.yaml",
        "Wiki/Wiki_*/relationships/human/*.md",
    ):
        require(
            denied_path in graph_access["write_scope"]["denied"],
            f"edit_knowledge_graph must not write relationship facts: {denied_path}",
        )

    graph_workflow = read_text("workflows/kb/edit_knowledge_graph.md")
    for token in (
        "Graph fact 是使用者确认后的图事实",
        "relationships/machine/<predicate_id>.yaml",
        "knowledge_graph/machine/<graph_id>.yaml",
        "knowledge_graph/human/<graph_id>.md",
        "不得创建或修改关系事实",
    ):
        require(token in graph_workflow, f"graph fact workflow is missing: {token}")
def main():
    validate_resource_registry_schema()
    validate_templates()
    validate_upper_layers_use_resource_ids()
    validate_dual_resource_table_workflow()
    validate_blacklist_contract()
    validate_workflows()
    validate_ascii_runtime_paths()
    validate_service_handoff_and_query_contract()
    validate_antibody_design_ingest_is_decoupled()
    validate_help_navigation()
    validate_command_and_knowledge_contract_closure()
    print("PASS: resource contract v2 is synchronized")


if __name__ == "__main__":
    main()



