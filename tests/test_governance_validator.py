from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from kis_mcp_doc.governance import GovernanceRepository


ROOT = Path(__file__).resolve().parents[1]
MRD_ROOT = ROOT / "prescriptives" / "mrd-specification"


def repository() -> GovernanceRepository:
    return GovernanceRepository(ROOT, MRD_ROOT)


def test_stabilized_governance_mrds_validate() -> None:
    result = repository().validate()

    assert result["status"] == "valid", result["diagnostics"]
    assert set(result["checks"]) == {
        "classification",
        "applicability",
        "ownership",
        "layering",
        "dependencies",
        "provenance",
        "lifecycle",
        "schema",
    }
    assert all(value == "pass" for value in result["checks"].values())


def test_catalog_has_all_47_types_including_sem_dom() -> None:
    documents = repository().load()
    classification = documents["urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617"]
    catalog = classification["content"]["type_catalog"]

    assert len(catalog) == 47
    assert any(item["code"] == "SEM-DOM" for item in catalog)
    assert len({item["code"] for item in catalog}) == 47


def test_higher_authority_cannot_depend_on_lower_authority() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    classification = mutated["urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617"]
    classification["_mrd"]["dependencies"].append(
        {"mrd_id": "urn:uuid:ddc10bf4-e6ea-5b3a-958e-464af2fa9fd1", "relationship": "depends_on"}
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
    validation = mutated["urn:uuid:361b074c-ddf6-5dcf-9031-dbb4ed306abf"]
    provenance = mutated["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"]
    provenance["_mrd"]["dependencies"].append(
        {"mrd_id": validation["_mrd"]["id"], "relationship": "depends_on"}
    )

    result = repo.validate_documents(mutated)

    assert "MRD_DEPENDENCY_CYCLE" in {item["code"] for item in result["diagnostics"]}


def test_inferred_prescriptive_fact_is_rejected() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    mutated["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"]["_mrd"]["provenance"]["fact_quality"] = "inferred"

    result = repo.validate_documents(mutated)

    assert "MRD_NORMATIVE_INFERENCE_PROHIBITED" in {
        item["code"] for item in result["diagnostics"]
    }


def test_repo_dependency_cannot_escape_repository_root() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    validation = mutated["urn:uuid:361b074c-ddf6-5dcf-9031-dbb4ed306abf"]
    repo_dependency = next(
        dependency for dependency in validation["_mrd"]["dependencies"] if "source" in dependency
    )
    repo_dependency["source"] = "repo:../../../AGENTS.md"

    result = repo.validate_documents(mutated)

    assert "MRD_DEPENDENCY_UNRESOLVED" in {
        item["code"] for item in result["diagnostics"]
    }


def test_governance_payload_shape_is_schema_locked() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    provenance = mutated["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"]
    provenance["content"]["unexpected_governance_surface"] = True

    result = repo.validate_documents(mutated)

    assert "MRD_SCHEMA_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }


def test_generation_mode_is_not_a_core_envelope_field() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    mutated["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"]["_mrd"]["generation_mode"] = "authored"

    result = repo.validate_documents(mutated)

    assert "MRD_SCHEMA_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }


def test_lifecycle_states_have_one_governance_owner() -> None:
    documents = repository().load()
    provenance = documents["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"]["content"]
    lifecycle = documents["urn:uuid:ddc10bf4-e6ea-5b3a-958e-464af2fa9fd1"]["content"]

    assert all("statuses" not in item for item in provenance["record_modes"])
    assert all(item["states"] for item in lifecycle["lifecycles"])


def test_duplicate_rule_ids_fail_validation() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    duplicate = copy.deepcopy(
        mutated["urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617"]["content"]["rules"][0]
    )
    mutated["urn:uuid:7eab1930-3cdf-58ee-8a6e-9d9519a17fba"]["content"]["rules"].append(duplicate)

    result = repo.validate_documents(mutated)

    assert "MRD_RULE_ID_DUPLICATE" in {
        item["code"] for item in result["diagnostics"]
    }


def test_repo_provenance_hash_mismatch_is_rejected() -> None:
    repo = repository()
    documents = repo.load()
    mutated = copy.deepcopy(documents)
    target = mutated["urn:uuid:361b074c-ddf6-5dcf-9031-dbb4ed306abf"]
    sources = target["_mrd"]["provenance"]["sources"]
    sources.append(
        {
            "source_id": "LOCAL-SCHEMA",
            "kind": "repo_path",
            "role": "validation_contract",
            "locator": "repo:contracts/mrd/v1/mrd.schema.json",
            "revision": None,
            "sha256": "0" * 64,
        }
    )
    from kis_mcp_doc.governance import canonical_hash

    target["_mrd"]["provenance"]["source_fingerprint"] = "sha256:" + canonical_hash(sources)
    result = repo.validate_documents(mutated)

    assert "MRD_SOURCE_HASH_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_class_catalog_must_cover_12_unique_classes() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    classification = mutated["urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617"]
    classification["content"]["classes"][-1]["code"] = "EVD"

    result = repo.validate_documents(mutated)

    assert "MRD_CLASS_CATALOG_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_layer_catalog_must_be_exactly_l0_through_l5() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    layering = mutated["urn:uuid:8a9346a9-0c83-5fa4-a91d-2de6ca3d57a9"]
    layering["content"]["layers"][-1]["code"] = "L4"

    result = repo.validate_documents(mutated)

    assert "MRD_LAYER_CATALOG_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_lifecycle_record_modes_must_match_provenance_vocabulary() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    lifecycle = mutated["urn:uuid:ddc10bf4-e6ea-5b3a-958e-464af2fa9fd1"]
    lifecycle["content"]["lifecycles"][-1]["record_mode"] = "synthetic"

    result = repo.validate_documents(mutated)

    assert "MRD_RECORD_MODE_CATALOG_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_validation_reason_code_contract_cannot_drift() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    validation = mutated["urn:uuid:361b074c-ddf6-5dcf-9031-dbb4ed306abf"]
    validation["content"]["reason_codes"].append("MRD_FAKE_REASON")

    result = repo.validate_documents(mutated)

    assert "MRD_VALIDATION_CONTRACT_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_meta_records_require_derived_fact_quality() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    target = mutated["urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617"]
    target["_mrd"]["class"] = "META"
    target["_mrd"]["type"] = "IDX"
    target["_mrd"]["record_mode"] = "meta"
    target["_mrd"]["status"] = "generated"
    target["_mrd"]["provenance"]["fact_quality"] = "direct"

    result = repo.validate_documents(mutated)

    assert "MRD_META_FACT_QUALITY_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }


def test_public_governance_profile_composes_envelope_and_content() -> None:
    schemas = [
        json.loads((ROOT / "contracts/mrd/v1/mrd.schema.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "contracts/mrd-specification/v1/content.schema.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "contracts/mrd-specification/v1/governance-mrd.schema.json").read_text(encoding="utf-8")),
    ]
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas
    )
    validator = Draft202012Validator(schemas[-1], registry=registry)
    document = copy.deepcopy(repository().load()["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"])
    document["content"]["unexpected_governance_surface"] = True

    assert list(validator.iter_errors(document))


def test_structural_failure_short_circuits_semantic_validation() -> None:
    repo = repository()
    documents = copy.deepcopy(repo.load())
    documents["urn:uuid:a1d99a79-5c7c-56b4-9fda-6c56f54e7ee8"]["content"] = []

    result = repo.validate_documents(documents)

    assert result["status"] == "invalid"
    assert {item["code"] for item in result["diagnostics"]} == {"MRD_SCHEMA_INVALID"}


def test_applicability_covers_catalog_exactly_once() -> None:
    documents = repository().load()
    catalog = documents["urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617"]["content"]["type_catalog"]
    applicability = documents["urn:uuid:6673613f-70e0-5004-aba9-103da53e5040"]["content"]["type_applicability"]

    expected = {(item["class"], item["type"], item["code"]) for item in catalog}
    actual = {(item["class"], item["type"], item["code"]) for item in applicability}
    assert len(applicability) == 47
    assert len(actual) == 47
    assert actual == expected


def test_applicability_catalog_drift_is_rejected() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    applicability = mutated["urn:uuid:6673613f-70e0-5004-aba9-103da53e5040"]["content"]["type_applicability"]
    applicability[-1] = copy.deepcopy(applicability[-2])

    result = repo.validate_documents(mutated)
    assert "MRD_APPLICABILITY_CATALOG_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }




def test_enforcement_mode_contract_drift_is_rejected() -> None:
    repo = repository()
    mutated = copy.deepcopy(repo.load())
    modes = mutated["urn:uuid:361b074c-ddf6-5dcf-9031-dbb4ed306abf"]["content"]["enforcement_modes"]
    modes[-1]["mode"] = modes[-2]["mode"]

    result = repo.validate_documents(mutated)
    assert "MRD_ENFORCEMENT_BINDING_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }
