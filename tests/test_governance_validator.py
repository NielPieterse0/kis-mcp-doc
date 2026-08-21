from __future__ import annotations

import copy
from pathlib import Path

from kis_mcp_doc.governance import GovernanceRepository


ROOT = Path(__file__).resolve().parents[1]
MRD_ROOT = ROOT / "mrd" / "governance"


def repository() -> GovernanceRepository:
    return GovernanceRepository(ROOT, MRD_ROOT)


def test_stabilized_governance_mrds_validate() -> None:
    result = repository().validate()

    assert result["status"] == "valid", result["diagnostics"]
    assert set(result["checks"]) == {
        "classification",
        "layering",
        "dependencies",
        "provenance",
        "lifecycle",
        "schema",
    }
    assert all(value == "pass" for value in result["checks"].values())


def test_catalog_has_all_47_types_including_sem_dom() -> None:
    documents = repository().load()
    classification = documents["KIS-KNOW-SEM-REG-001"]
    catalog = classification["content"]["type_catalog"]

    assert len(catalog) == 47
    assert any(item["code"] == "SEM-DOM" for item in catalog)
    assert len({item["code"] for item in catalog}) == 47


def test_higher_authority_cannot_depend_on_lower_authority() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    classification = mutated["KIS-KNOW-SEM-REG-001"]
    classification["_mrd"]["dependencies"].append(
        {"mrd_id": "KIS-KNOW-WRK-STM-001", "relationship": "depends_on"}
    )

    result = repo.validate_documents(mutated)

    assert result["status"] == "invalid"
    assert "MRD_DEPENDENCY_LAYER_VIOLATION" in {
        item["code"] for item in result["diagnostics"]
    }


def test_dependency_cycles_fail() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    validation = mutated["KIS-KNOW-EVL-TST-001"]
    provenance = mutated["KIS-KNOW-CON-POL-001"]
    provenance["_mrd"]["dependencies"].append(
        {"mrd_id": validation["_mrd"]["id"], "relationship": "depends_on"}
    )

    result = repo.validate_documents(mutated)

    assert "MRD_DEPENDENCY_CYCLE" in {item["code"] for item in result["diagnostics"]}


def test_inferred_prescriptive_fact_is_rejected() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    mutated["KIS-KNOW-CON-POL-001"]["_mrd"]["provenance"]["fact_quality"] = "inferred"

    result = repo.validate_documents(mutated)

    assert "MRD_NORMATIVE_INFERENCE_PROHIBITED" in {
        item["code"] for item in result["diagnostics"]
    }


def test_repo_dependency_cannot_escape_repository_root() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    validation = mutated["KIS-KNOW-EVL-TST-001"]
    validation["_mrd"]["dependencies"][-1]["source"] = "repo:../../../AGENTS.md"

    result = repo.validate_documents(mutated)

    assert "MRD_DEPENDENCY_UNRESOLVED" in {
        item["code"] for item in result["diagnostics"]
    }


def test_governance_payload_shape_is_schema_locked() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    provenance = mutated["KIS-KNOW-CON-POL-001"]
    provenance["content"]["unexpected_governance_surface"] = True

    result = repo.validate_documents(mutated)

    assert "MRD_SCHEMA_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }


def test_generation_mode_is_not_a_core_envelope_field() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    mutated["KIS-KNOW-CON-POL-001"]["_mrd"]["generation_mode"] = "authored"

    result = repo.validate_documents(mutated)

    assert "MRD_SCHEMA_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }


def test_lifecycle_states_have_one_governance_owner() -> None:
    documents = repository().load()
    provenance = documents["KIS-KNOW-CON-POL-001"]["content"]
    lifecycle = documents["KIS-KNOW-WRK-STM-001"]["content"]

    assert all("statuses" not in item for item in provenance["record_modes"])
    assert all(item["states"] for item in lifecycle["lifecycles"])


def test_duplicate_rule_ids_fail_validation() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    duplicate = copy.deepcopy(
        mutated["KIS-KNOW-SEM-REG-001"]["content"]["rules"][0]
    )
    mutated["KIS-KNOW-CON-CTR-001"]["content"]["rules"].append(duplicate)

    result = repo.validate_documents(mutated)

    assert "MRD_RULE_ID_DUPLICATE" in {
        item["code"] for item in result["diagnostics"]
    }
