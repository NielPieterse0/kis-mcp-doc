import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "tooling" / "windows-runtime.json"
VERIFY = ROOT / "scripts" / "verify.ps1"
PREFLIGHT = ROOT / "scripts" / "runtime-preflight.ps1"


def test_windows_runtime_policy_is_fail_closed_and_portable():
    policy = json.loads(POLICY.read_text(encoding="utf-8-sig"))
    assert policy["platform"] == "windows"
    assert policy["python"]["require_authenticode"] is True
    assert policy["python"]["trusted_publisher_subject_contains"] == "Python Software Foundation"
    assert policy["uv"]["allow_managed_python"] is False
    assert policy["uv"]["allow_python_downloads"] is False
    assert policy["security"] == {
        "defender_exclusions_allowed": False,
        "smart_app_control_bypass_allowed": False,
        "execution_policy_weakening_allowed": False,
    }
    serialized = json.dumps(policy).lower()
    assert "c:\\users\\" not in serialized
    assert "python311\\python.exe" not in serialized


def test_preflight_rejects_uv_managed_python_and_requires_signature():
    text = PREFLIGHT.read_text(encoding="utf-8-sig")
    assert "forbidden_path_fragments" in text
    assert "Get-AuthenticodeSignature" in text
    assert "SignatureStatus]::Valid" in text
    assert "COMPLIANT_SYSTEM_PYTHON_NOT_FOUND" in text


def test_canonical_verification_disables_uv_python_management():
    text = VERIFY.read_text(encoding="utf-8-sig")
    assert "runtime-preflight.ps1" in text
    assert "$env:UV_PYTHON" in text
    assert "--no-managed-python" in text
    assert "--no-python-downloads" in text
    assert ".venv\\Scripts\\python.exe" in text
