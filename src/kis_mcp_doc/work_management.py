from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .governance import canonical_hash, canonical_source_bytes


class WorkManagementRepository:
    def __init__(self, root: Path, mrd_root: Path | None = None) -> None:
        self.root = Path(root).resolve()
        self.mrd_root = (mrd_root or self.root / "mrd" / "work-management").resolve()
        self.schema_path = self.root / "contracts" / "mrd" / "v1" / "mrd.schema.json"

    def load(self) -> dict[str, dict[str, Any]]:
        docs: dict[str, dict[str, Any]] = {}
        for path in sorted(self.mrd_root.glob("*.mrd.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            doc_id = doc.get("_mrd", {}).get("id")
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError(f"MRD missing stable id: {path}")
            if doc_id in docs:
                raise ValueError(f"duplicate MRD id: {doc_id}")
            docs[doc_id] = doc
        return docs

    def validate(self) -> dict[str, Any]:
        diagnostics: list[dict[str, str]] = []
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            docs = self.load()
        except Exception as error:
            return {"status":"invalid","diagnostics":[{"code":"WORK_MRD_LOAD_INVALID","message":str(error)}]}
        for doc_id, doc in docs.items():
            for error in sorted(validator.iter_errors(doc), key=lambda e: tuple(str(x) for x in e.absolute_path)):
                diagnostics.append({"code":"WORK_MRD_SCHEMA_INVALID","message":f"{doc_id}: {error.message}"})
        ids=set(docs)
        for doc_id,doc in docs.items():
            for dep in doc["_mrd"]["dependencies"]:
                if "mrd_id" in dep and dep["mrd_id"] not in ids:
                    diagnostics.append({"code":"WORK_MRD_DEPENDENCY_UNRESOLVED","message":f"{doc_id}: {dep['mrd_id']}"})
                if "source" in dep:
                    rel=dep["source"][5:]
                    if not (self.root/rel).is_file():
                        diagnostics.append({"code":"WORK_MRD_SOURCE_UNRESOLVED","message":f"{doc_id}: {rel}"})
            sources=doc["_mrd"]["provenance"]["sources"]
            expected="sha256:"+canonical_hash(sources)
            if doc["_mrd"]["provenance"]["source_fingerprint"] != expected:
                diagnostics.append({"code":"WORK_MRD_FINGERPRINT_MISMATCH","message":doc_id})
            for source in sources:
                if source["kind"]=="repo_path":
                    path=self.root/source["locator"][5:]
                    if not path.is_file() or hashlib.sha256(canonical_source_bytes(path)).hexdigest()!=source.get("sha256"):
                        diagnostics.append({"code":"WORK_MRD_SOURCE_HASH_MISMATCH","message":f"{doc_id}: {source['locator']}"})
        return {"status":"invalid" if diagnostics else "valid","diagnostics":diagnostics}


def _page_name(index: int, doc: dict[str, Any]) -> str:
    slug="-".join(x for x in ''.join(c.lower() if c.isalnum() else '-' for c in doc['_mrd']['title']).split('-') if x)
    return f"{index:03d}-{slug}.md"


def _inline_value(value: Any) -> str | None:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
        return ", ".join(str(item) for item in value) if value else "None"
    return None


def _item_label(item: dict[str, Any], index: int) -> str:
    for key in ("name", "label", "title", "id", "token", "code", "operation_id", "rule_id"):
        value = item.get(key)
        if isinstance(value, (str, int)) and str(value):
            return str(value).replace("_", " ")
    if "order" in item:
        return f"Step {item['order']}"
    return f"Item {index}"


def _render_value(value: Any, *, level: int = 3) -> list[str]:
    if isinstance(value, str):
        return [value, ""]
    inline = _inline_value(value)
    if inline is not None:
        return [inline, ""]
    if isinstance(value, list):
        if not value:
            return ["None.", ""]
        if all(isinstance(item, str) for item in value):
            return [*(f"- {item}" for item in value), ""]
        if all(isinstance(item, dict) for item in value):
            lines: list[str] = []
            for index, item in enumerate(value, start=1):
                lines.extend([f"{'#' * min(level, 6)} {_item_label(item, index)}", ""])
                for key, nested in item.items():
                    if key in {"name", "label", "title"}:
                        continue
                    label = key.replace("_", " ").capitalize()
                    nested_inline = _inline_value(nested)
                    if nested_inline is not None:
                        lines.extend([f"**{label}:** {nested_inline}", ""])
                    else:
                        lines.extend([f"{'#' * min(level + 1, 6)} {label}", ""])
                        lines.extend(_render_value(nested, level=level + 2))
            return lines
        return ["- " + str(item) for item in value] + [""]
    if isinstance(value, dict):
        lines = []
        for key, nested in value.items():
            label = key.replace("_", " ").capitalize()
            nested_inline = _inline_value(nested)
            if nested_inline is not None:
                lines.extend([f"**{label}:** {nested_inline}", ""])
            else:
                lines.extend([f"{'#' * min(level, 6)} {label}", ""])
                lines.extend(_render_value(nested, level=level + 1))
        return lines
    return [str(value), ""]


def render_document(doc: dict[str, Any]) -> str:
    content=doc["content"]
    lines=["<!-- GENERATED — DO NOT EDIT -->",f"# {doc['_mrd']['title']}","",'<div id="enable-section-numbers" />',"","[Specification](001-specification.md) | [Documentation index](000-index.md)",""]
    purpose=content.get("purpose")
    if purpose: lines.extend([purpose,""])
    for key,value in content.items():
        if key=="purpose": continue
        lines.extend([f"## {key.replace('_',' ').capitalize()}",""])
        lines.extend(_render_value(value))
    lines.extend(["## Source and authority","",f"This page projects `{doc['_mrd']['id']}` version `{doc['_mrd']['version']}`. The MRD is authoritative; this generated page has no write-back authority.",""])
    return "\n".join(lines)


def build_work_management_spec(repo: WorkManagementRepository, output: Path, *, replace: bool=False) -> dict[str, Any]:
    validation=repo.validate()
    if validation["status"]!="valid": raise ValueError(f"work-management MRDs invalid: {validation['diagnostics']}")
    docs=list(repo.load().values())
    output=Path(output)
    staging=Path(tempfile.mkdtemp(prefix=f".{output.name}.",suffix=".tmp",dir=output.parent))
    try:
        pages=[]
        for i,doc in enumerate(docs,2):
            name=_page_name(i,doc); text=render_document(doc); (staging/name).write_text(text,encoding="utf-8"); pages.append((name,doc))
        index=["<!-- GENERATED — DO NOT EDIT -->","# KIS Work Management Specification — documentation index","","The validated Work Management MRDs are authoritative. These pages are deterministic review projections.","","## Specification pages","","- [Specification](001-specification.md)"]+[f"- [{d['_mrd']['title']}]({n})" for n,d in pages]+["","## Traceability","","- [Build manifest](manifest.json)",""]
        (staging/'000-index.md').write_text("\n".join(index),encoding='utf-8')
        root=["<!-- GENERATED — DO NOT EDIT -->","# KIS Work Management Specification","",'<div id="enable-section-numbers" />',"","Governed operating specification for work intake, state, selection, delivery, reconciliation, and GitHub Project integration.","",'The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and "OPTIONAL" are normative when they appear in all capitals.',"","## Overview","","Work Management separates command authority from evidence. It governs work-item semantics, lifecycle state, deterministic selection, provider reconciliation, delivery evidence, and closeout while keeping repository change governance authoritative for governed change facts.","","The specification is generated from seven prescriptive MRDs harvested from the pinned `kis-mcp` implementation contracts. Live GitHub Project evidence that could not be observed remains explicitly unavailable rather than inferred.","","## Detailed specification",""]+[f"- [{d['_mrd']['title']}]({n})" for n,d in pages]+["","## Traceability","","See the [documentation index](000-index.md) and [build manifest](manifest.json) for source identities and hashes.",""]
        spec="\n".join(root); (staging/'001-specification.md').write_text(spec,encoding='utf-8'); (staging/'specification.md').write_text(spec,encoding='utf-8')
        files=[]
        for path in sorted(staging.rglob('*')):
            if path.is_file():
                b=path.read_bytes(); files.append({'path':path.relative_to(staging).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
        mrds=[]
        for path in sorted(repo.mrd_root.glob('*.mrd.json')):
            b=canonical_source_bytes(path); d=json.loads(path.read_text(encoding='utf-8')); mrds.append({'id':d['_mrd']['id'],'path':path.relative_to(repo.root).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'version':d['_mrd']['version']})
        manifest={'contract':{'name':'kis-work-management-spec-build','version':1},'specification':{'title':'KIS Work Management Specification','version':'1.0.0','status':'draft','layout_profile':'mcp-spec'},'inputs':{'mrds':mrds,'source_set_sha256':canonical_hash(mrds)},'validation':validation,'files':files,'bundle_sha256':canonical_hash(files)}
        (staging/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        if output.exists():
            if not replace: raise FileExistsError(output)
            shutil.rmtree(output)
        output.parent.mkdir(parents=True,exist_ok=True); staging.replace(output); return manifest
    except Exception:
        shutil.rmtree(staging,ignore_errors=True); raise


def verify_work_management_spec(repo: WorkManagementRepository, output: Path) -> dict[str, Any]:
    output=Path(output)
    if not (output/'manifest.json').is_file(): return {'status':'invalid','diagnostics':[{'code':'WORK_GENERATED_MANIFEST_MISSING','message':'manifest.json missing'}]}
    temp=output.parent/(output.name+'.verify.tmp')
    if temp.exists(): shutil.rmtree(temp)
    try:
        build_work_management_spec(repo,temp)
        expected={p.relative_to(temp).as_posix():canonical_source_bytes(p) for p in temp.rglob('*') if p.is_file()}
        actual={p.relative_to(output).as_posix():canonical_source_bytes(p) for p in output.rglob('*') if p.is_file()}
        if expected!=actual: return {'status':'invalid','diagnostics':[{'code':'WORK_GENERATED_DRIFT','message':'generated Work Management specification differs from deterministic current output'}]}
        return {'status':'valid','diagnostics':[]}
    finally:
        shutil.rmtree(temp,ignore_errors=True)
