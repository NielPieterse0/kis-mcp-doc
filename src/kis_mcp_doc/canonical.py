from __future__ import annotations

import hashlib
import json
from pathlib import Path


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def resolve_repo_file(root: Path, locator: object) -> Path | None:
    root = Path(root).resolve()
    if not isinstance(locator, str) or not locator.startswith("repo:"):
        return None
    relative = locator[5:]
    if not relative:
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def normative_keywords_statement() -> str:
    return ('The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", '
            '"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" are to be '
            'interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14), '
            '[RFC2119](https://www.rfc-editor.org/rfc/rfc2119), and '
            '[RFC8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in all capitals.')


_CANONICAL_TEXT_SUFFIXES = frozenset({
    ".bat", ".cfg", ".cmd", ".css", ".html", ".ini", ".js", ".json", ".jsonc",
    ".jsx", ".md", ".ps1", ".py", ".sh", ".toml", ".ts", ".tsx", ".txt", ".xml",
    ".yaml", ".yml",
})
_CANONICAL_TEXT_NAMES = frozenset({".gitattributes", ".gitignore", ".nvmrc", "Dockerfile", "Makefile"})


def canonical_source_bytes(path: Path) -> bytes:
    path = Path(path)
    payload = path.read_bytes()
    if path.suffix.casefold() not in _CANONICAL_TEXT_SUFFIXES and path.name not in _CANONICAL_TEXT_NAMES:
        return payload
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
