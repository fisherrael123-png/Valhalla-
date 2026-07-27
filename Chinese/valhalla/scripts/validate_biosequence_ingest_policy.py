from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

POLICY_FILES = [
    ROOT / "workflows" / "kb" / "ingest.md",
    ROOT / "workflows" / "kb" / "antibody_design_ingest.md",
    ROOT / "references" / "valhalla_entity_template_antibody_protein_design.md",
]

FORBIDDEN_FRAGMENTS = [
    "允许摄入公开来源中的蛋白、肽、抗体、VHH、CDR、domain、motif 和修饰序列",
    "不准摄入蛋白质序列",
    "blocked_biosequence_ingest_policy",
    "若资料的核心内容依赖必须逐字读取或转写生物序列，必须停止该资源摄入",
]

REQUIRED_FRAGMENTS = [
    "资料中的分子字符串可以作为已发表文献事实处理",
    "不得要求模型基于这些字符串生成、优化、补全、改造、筛选或设计新分子",
    "长串原文片段不得集中复制进提示词",
    "不得记录可执行湿实验步骤、实验条件、培养/表达/筛选参数、载体/引物构建步骤",
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    combined = []
    for path in POLICY_FILES:
        require(path.exists(), f"policy file missing: {path.relative_to(ROOT)}")
        combined.append(path.read_text(encoding="utf-8-sig"))
    policy_text = "\n".join(combined)

    for fragment in FORBIDDEN_FRAGMENTS:
        require(fragment not in policy_text, f"forbidden legacy biosequence policy remains: {fragment}")

    for fragment in REQUIRED_FRAGMENTS:
        require(fragment in policy_text, f"required biosequence policy missing: {fragment}")

    print("PASS: biosequence ingest policy preserves literature facts and blocks design/operation use")


if __name__ == "__main__":
    main()
