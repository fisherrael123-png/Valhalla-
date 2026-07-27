from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

POLICY_FILES = [
    ROOT / "workflows" / "kb" / "ingest.md",
    ROOT / "workflows" / "kb" / "antibody_design_ingest.md",
    ROOT / "references" / "valhalla_entity_template_antibody_protein_design.md",
]

FORBIDDEN_FRAGMENTS = [
    "Publicly sourced protein, peptide, antibody, VHH, CDR, domain, motif, and modified sequences may be ingested",
    "Protein sequences must not be ingested",
    "blocked_biosequence_ingest_policy",
    "If a Resource's core content requires verbatim reading or transcription of a biological sequence, stop ingesting that Resource",
]

REQUIRED_FRAGMENTS = [
    "Molecular strings in source material may be recorded as facts from published literature",
    "must not be used to generate, optimize, complete, modify, screen, or recommend experimental execution",
    "Do not copy long source passages into a prompt in bulk",
    "Do not record executable wet-lab procedures, experimental conditions, culture/expression/screening parameters, vector or primer construction steps",
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
