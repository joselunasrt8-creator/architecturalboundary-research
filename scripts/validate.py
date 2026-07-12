#!/usr/bin/env python3
"""Validate the research-first repository topology deterministically."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - restricted local environments only
    sys.path.insert(0, str(ROOT))
    from tools.jsonschema_fallback import Draft202012Validator

REQUIRED_TOP_LEVEL = [
    "analysis", "ci", "datasets", "docs", "evidence", "figures", "investigations",
    "papers", "protocol", "registry", "releases", "schemas", "scripts", "validation",
]
REQUIRED_PATHS = [
    "README.md", "ROADMAP.md", "LICENSE", "CONTRIBUTING.md", "CITATION.cff", "REPRODUCIBILITY.md", "MOVES.md",
    "ci/README.md", "ci/validate.yml", ".github/workflows/validate.yml",
    "docs/README.md", "docs/methodology.md", "docs/research_pipeline.md", "docs/glossary.md", "docs/figures/.gitkeep",
    "protocol/README.md", "protocol/changelog.md", "protocol/protocol-v1/README.md", "protocol/protocol-v1/protocol.md",
    "protocol/protocol-v1/terminology.md", "protocol/protocol-v1/decision_rules.md",
    "protocol/protocol-v1/schemas/README.md", "protocol/protocol-v1/templates/README.md",
    "papers/paper-0-protocol/README.md", "papers/paper-b1/README.md", "papers/paper-b2/main.tex",
    "datasets/README.md", "datasets/canonical/README.md", "datasets/comparative/README.md", "datasets/exports/README.md",
    "scripts/build_dataset.py", "scripts/build_report.py", "scripts/check_registry.py", "scripts/build_papers.py",
]
INVESTIGATIONS = ["investigations/template", "investigations/b1-three-system-pilot", "investigations/b2-governance-cohort"]
INVESTIGATION_ITEMS = [
    "README.md", "preregistration.md", "literature/README.md", "bor/README.md", "srf/README.md",
    "der/README.md", "msr/README.md", "dataset/README.md", "analysis/README.md", "results/README.md",
    "figures/README.md", "artifacts/README.md",
]
SCHEMAS = [
    "schemas/bor.schema.json", "schemas/srf.schema.json", "schemas/der.schema.json",
    "schemas/msr.schema.json", "schemas/dataset.schema.json", "schemas/investigation.schema.json",
]
REGISTRIES = [
    "registry/architectural_boundaries.json", "registry/investigations.json", "registry/terminology.json",
    "registry/classifications.json", "registry/protocol_versions.json", "registry/retained_classifications.json",
    "registry/candidate_invariants.json",
]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
TEX_INPUT = re.compile(r"\\(?:input|include|bibliography)\{([^}]+)\}")
PAPER_TEMPLATE = ROOT / "papers" / "_template"
STANDARD_PAPER_REQUIRED = ["README.md", "main.tex", "references.bib", "sections"]
LEGACY_PAPER_STRUCTURE_EXEMPTIONS = {"paper-0-protocol", "paper-b2"}


def require_path(relative: str) -> None:
    if not (ROOT / relative).exists():
        raise SystemExit(f"missing required path: {relative}")


def require_json(relative: str) -> object:
    require_path(relative)
    with (ROOT / relative).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if relative.endswith(".schema.json") and "$schema" not in data:
        raise SystemExit(f"schema missing $schema key: {relative}")
    return data


def validate_yaml_syntax() -> None:
    yaml_files = [*ROOT.rglob("*.yml"), *ROOT.rglob("*.yaml"), *ROOT.rglob("*.cff")]
    try:
        import yaml  # type: ignore
    except Exception:
        # Deterministic fallback: reject tabs and obviously empty structural files.
        for path in yaml_files:
            text = path.read_text(encoding="utf-8")
            if "\t" in text:
                raise SystemExit(f"YAML-like file contains tab indentation: {path.relative_to(ROOT)}")
        return
    for path in yaml_files:
        with path.open(encoding="utf-8") as handle:
            yaml.safe_load(handle)


def validate_markdown_links() -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                raise SystemExit(f"broken Markdown link in {path.relative_to(ROOT)}: {match.group(1)}")


def validate_latex_inputs() -> None:
    for path in ROOT.rglob("*.tex"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw in TEX_INPUT.findall(text):
            candidates = [path.parent / raw]
            if not Path(raw).suffix:
                candidates.extend([path.parent / f"{raw}.tex", path.parent / f"{raw}.bib"])
            if not any(candidate.exists() for candidate in candidates):
                raise SystemExit(f"broken LaTeX reference in {path.relative_to(ROOT)}: {raw}")



def validate_repository_first_paper_template() -> None:
    for relative in [
        "README.md",
        "main.tex",
        "references.bib",
        "sections/abstract.tex",
        "sections/introduction.tex",
        "sections/methodology.tex",
        "sections/evidence.tex",
        "sections/analysis.tex",
        "sections/conclusion.tex",
    ]:
        candidate = PAPER_TEMPLATE / relative
        if not candidate.exists():
            raise SystemExit(f"paper template missing required path: {candidate.relative_to(ROOT)}")
    readme = (PAPER_TEMPLATE / "README.md").read_text(encoding="utf-8")
    required_phrases = ["repository is the canonical source", "Overleaf", "main.tex", "references.bib", "sections/"]
    for phrase in required_phrases:
        if phrase not in readme:
            raise SystemExit(f"paper template README missing repository-first guidance: {phrase}")


def validate_standard_paper_structure() -> None:
    for main_tex in sorted((ROOT / "papers").rglob("main.tex")):
        paper_dir = main_tex.parent
        relative_parts = paper_dir.relative_to(ROOT / "papers").parts
        if any(part.startswith((".", "_")) for part in relative_parts):
            continue
        if paper_dir.name in LEGACY_PAPER_STRUCTURE_EXEMPTIONS:
            continue
        for required in STANDARD_PAPER_REQUIRED:
            candidate = paper_dir / required
            if not candidate.exists():
                raise SystemExit(f"standard paper structure missing {required}: {paper_dir.relative_to(ROOT)}")
        section_files = sorted((paper_dir / "sections").glob("*.tex"))
        if not section_files:
            raise SystemExit(f"standard paper structure requires section files: {(paper_dir / 'sections').relative_to(ROOT)}")

def validate_registered_paths() -> None:
    for relative in ["registry/investigations.json", "registry/protocol_versions.json"]:
        data = require_json(relative)
        key = "investigations" if "investigations" in data else "protocol_versions"
        for item in data[key]:
            registered = item.get("path")
            if not registered or not (ROOT / registered).exists():
                raise SystemExit(f"{relative} references missing path: {registered}")


def validate_bor_schemas() -> None:
    schema = require_json("schemas/bor.schema.json")
    validator = Draft202012Validator(schema)
    for path in sorted((ROOT / "investigations/b2-governance-cohort/bor").glob("*.bor.json")):
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
        if errors:
            detail = "; ".join(error.message for error in errors)
            raise SystemExit(f"BOR schema validation failed for {path.relative_to(ROOT)}: {detail}")



def validate_srf_registry() -> None:
    bor_dir = ROOT / "investigations/b2-governance-cohort/bor"
    srf_dir = ROOT / "investigations/b2-governance-cohort/srf"
    schema = require_json("schemas/srf.schema.json")
    validator = Draft202012Validator(schema)

    bor_records: dict[str, tuple[Path, set[str]]] = {}
    for path in sorted(bor_dir.glob("*.bor.json")):
        data = require_json(str(path.relative_to(ROOT)))
        if not isinstance(data, dict):
            raise SystemExit(f"BOR must be an object: {path.relative_to(ROOT)}")
        bor_id = data.get("id")
        if not isinstance(bor_id, str) or not bor_id:
            raise SystemExit(f"BOR missing id: {path.relative_to(ROOT)}")
        observations = data.get("observations")
        if not isinstance(observations, list):
            raise SystemExit(f"BOR observations must be a list: {path.relative_to(ROOT)}")
        observation_ids = set()
        for observation in observations:
            if not isinstance(observation, dict) or not isinstance(observation.get("observation_id"), str):
                raise SystemExit(f"BOR observation missing id: {path.relative_to(ROOT)}")
            observation_id = observation["observation_id"]
            if observation_id in observation_ids:
                raise SystemExit(f"duplicate BOR observation id in {path.relative_to(ROOT)}: {observation_id}")
            observation_ids.add(observation_id)
        if bor_id in bor_records:
            raise SystemExit(f"duplicate BOR id: {bor_id}")
        bor_records[bor_id] = (path, observation_ids)

    srf_paths = sorted(srf_dir.glob("*.srf.json"))
    if len(srf_paths) != len(bor_records):
        raise SystemExit(f"expected exactly one SRF per BOR: {len(bor_records)} BORs, {len(srf_paths)} SRFs")

    srf_ids: set[str] = set()
    surface_ids: set[str] = set()
    bor_to_srf: dict[str, str] = {}
    for path in srf_paths:
        data = require_json(str(path.relative_to(ROOT)))
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
        if errors:
            detail = "; ".join(error.message for error in errors)
            raise SystemExit(f"SRF schema validation failed for {path.relative_to(ROOT)}: {detail}")
        if not isinstance(data, dict):
            raise SystemExit(f"SRF must be an object: {path.relative_to(ROOT)}")
        srf_id = data["id"]
        if srf_id in srf_ids:
            raise SystemExit(f"duplicate SRF id: {srf_id}")
        srf_ids.add(srf_id)

        bor_reference = data["bor_reference"]
        bor_id = bor_reference["bor_id"]
        bor_path = ROOT / bor_reference["path"]
        if bor_id not in bor_records:
            raise SystemExit(f"{path.relative_to(ROOT)} references unknown BOR id: {bor_id}")
        expected_path, observation_ids = bor_records[bor_id]
        if bor_path != expected_path:
            raise SystemExit(f"{path.relative_to(ROOT)} references wrong BOR path for {bor_id}: {bor_reference['path']}")
        if bor_id in bor_to_srf:
            raise SystemExit(f"BOR referenced by multiple SRFs: {bor_id}")
        bor_to_srf[bor_id] = srf_id

        for category, entries in data["surfaces"].items():
            if not isinstance(entries, list):
                raise SystemExit(f"SRF surface category must be a list: {path.relative_to(ROOT)} {category}")
            for entry in entries:
                entry_id = entry["id"]
                if entry_id in surface_ids:
                    raise SystemExit(f"duplicate SRF surface id: {entry_id}")
                surface_ids.add(entry_id)
                for observation_ref in entry["observation_refs"]:
                    if observation_ref not in observation_ids:
                        raise SystemExit(
                            f"{path.relative_to(ROOT)} references missing BOR observation for {bor_id}: {observation_ref}"
                        )

    missing = sorted(set(bor_records) - set(bor_to_srf))
    if missing:
        raise SystemExit(f"BORs missing SRF records: {', '.join(missing)}")



def validate_json_object_against_schema(data: object, schema_relative: str, source_relative: str) -> None:
    """Validate one JSON object against a repository schema with deterministic errors."""
    schema = require_json(schema_relative)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise SystemExit(f"{source_relative} schema validation failed: {detail}")


def markdown_heading_slugs(path: Path) -> set[str]:
    slugs: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        heading = stripped.lstrip("#").strip().lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", heading)
        slug = re.sub(r"[\s-]+", "-", slug).strip("-")
        if slug:
            slugs.add(slug)
    return slugs


def is_allowed_derivation_source(relative: Path) -> bool:
    parts = relative.parts
    if parts and parts[0] == "protocol":
        return True
    return len(parts) >= 3 and parts[0] == "investigations" and parts[2] == "preregistration"


def resolve_repo_file(reference: str, *, purpose: str, allowed_derivation_source: bool = False) -> Path:
    """Resolve a repository-relative file reference and reject host-dependent paths."""
    raw_path, fragment = reference.split("#", 1) if "#" in reference else (reference, "")
    if not raw_path:
        raise SystemExit(f"{purpose} reference is empty")
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise SystemExit(f"{purpose} reference must be repository-relative: {reference}")
    if ".." in candidate.parts:
        raise SystemExit(f"{purpose} reference escapes repository: {reference}")
    resolved = (ROOT / candidate).resolve()
    try:
        relative = resolved.relative_to(ROOT.resolve())
    except ValueError:
        raise SystemExit(f"{purpose} reference escapes repository: {reference}") from None
    if allowed_derivation_source and not is_allowed_derivation_source(relative):
        raise SystemExit(f"{purpose} reference is not an allowed protocol or preregistration source: {reference}")
    if not resolved.exists():
        raise SystemExit(f"{purpose} reference does not exist: {reference}")
    if not resolved.is_file():
        raise SystemExit(f"{purpose} reference is not a file: {reference}")
    if fragment:
        if resolved.suffix.lower() != ".md":
            raise SystemExit(f"{purpose} fragment references require a Markdown file: {reference}")
        if fragment not in markdown_heading_slugs(resolved):
            raise SystemExit(f"{purpose} fragment does not resolve to a Markdown heading: {reference}")
    return resolved


def load_validated_srf(path: Path) -> dict[str, object]:
    """Load an SRF only after validating it against the canonical SRF schema."""
    relative = str(path.relative_to(ROOT))
    data = require_json(relative)
    if not isinstance(data, dict):
        raise SystemExit(f"SRF must be an object: {relative}")
    validate_json_object_against_schema(data, "schemas/srf.schema.json", relative)
    return data


def srf_records_for(investigation_dir: Path) -> dict[str, tuple[dict[str, object], Path]]:
    """Collect schema-valid SRF records for one investigation by ID."""
    records: dict[str, tuple[dict[str, object], Path]] = {}
    srf_dir = investigation_dir / "srf"
    for path in sorted(srf_dir.glob("*.srf.json")):
        data = load_validated_srf(path)
        srf_id = data["id"]
        if not isinstance(srf_id, str):
            raise SystemExit(f"SRF id must be a string: {path.relative_to(ROOT)}")
        if srf_id in records:
            raise SystemExit(f"duplicate SRF id: {srf_id}")
        records[srf_id] = (data, path)
    return records


def collect_selected_srf_lineage(
    der: dict[str, object],
    srf_records: dict[str, tuple[dict[str, object], Path]],
    der_relative: str,
) -> tuple[set[str], set[str], set[Path]]:
    """Collect only surfaces and observations reachable through declared source SRFs."""
    selected_surface_ids: set[str] = set()
    selected_observation_refs: set[str] = set()
    selected_srf_paths: set[Path] = set()
    for srf_id in der["source_srf_ids"]:
        if srf_id not in srf_records:
            raise SystemExit(f"{der_relative} references unknown SRF id: {srf_id}")
        srf, srf_path = srf_records[srf_id]
        if srf.get("investigation_id") != der["investigation_id"]:
            raise SystemExit(f"{der_relative} references SRF from a different investigation: {srf_id}")
        selected_srf_paths.add(srf_path.resolve())
        surfaces = srf["surfaces"]
        if not isinstance(surfaces, dict):
            raise SystemExit(f"SRF surfaces must be an object: {srf_path.relative_to(ROOT)}")
        for entries in surfaces.values():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                surface_id = entry.get("id")
                if isinstance(surface_id, str) and surface_id:
                    selected_surface_ids.add(surface_id)
                refs = entry.get("observation_refs")
                if isinstance(refs, list):
                    selected_observation_refs.update(ref for ref in refs if isinstance(ref, str) and ref)
    return selected_surface_ids, selected_observation_refs, selected_srf_paths


def validate_der_provenance(
    der: dict[str, object],
    selected_srf_paths: set[Path],
    derivation_source: Path,
    der_relative: str,
) -> None:
    provenance = der["provenance"]
    if not isinstance(provenance, dict):
        raise SystemExit(f"{der_relative} provenance must be an object")
    created_from = provenance["created_from"]
    resolved = {resolve_repo_file(ref, purpose="DER provenance") for ref in created_from}
    required = {path.resolve() for path in selected_srf_paths}
    required.add(derivation_source.resolve())
    missing = sorted(str(path.relative_to(ROOT)) for path in required - resolved)
    if missing:
        raise SystemExit(f"{der_relative} provenance missing required source(s): {', '.join(missing)}")
    unrelated = sorted(str(path.relative_to(ROOT)) for path in resolved - required)
    if unrelated:
        raise SystemExit(f"{der_relative} provenance contains unrelated source(s): {', '.join(unrelated)}")


def validate_der_contract() -> None:
    """Validate DER files when present without treating absent DERs as completed execution."""
    for investigation_dir in sorted((ROOT / "investigations").iterdir()):
        if not investigation_dir.is_dir():
            continue
        der_dir = investigation_dir / "der"
        if not der_dir.is_dir():
            continue
        der_paths = sorted(der_dir.glob("*.der.json"))
        if not der_paths:
            continue

        srf_records = srf_records_for(investigation_dir)
        der_ids: set[str] = set()
        der_source_srf_ids: set[str] = set()
        for path in der_paths:
            der_relative = str(path.relative_to(ROOT))
            data = require_json(der_relative)
            if not isinstance(data, dict):
                raise SystemExit(f"DER must be an object: {der_relative}")
            validate_json_object_against_schema(data, "schemas/der.schema.json", der_relative)

            der_id = data["id"]
            if der_id in der_ids:
                raise SystemExit(f"duplicate DER id in {investigation_dir.relative_to(ROOT)}: {der_id}")
            der_ids.add(der_id)

            expected_investigation = investigation_dir.name
            if data["investigation_id"] != expected_investigation:
                raise SystemExit(f"{der_relative} investigation_id does not match directory: {data['investigation_id']}")

            selected_surfaces, selected_observations, selected_srf_paths = collect_selected_srf_lineage(
                data, srf_records, der_relative
            )
            for surface_id in data["source_surface_ids"]:
                if surface_id not in selected_surfaces:
                    raise SystemExit(f"{der_relative} references undeclared SRF surface id: {surface_id}")

            for observation_ref in data["source_observation_refs"]:
                if observation_ref not in selected_observations:
                    raise SystemExit(f"{der_relative} references undeclared SRF observation ref: {observation_ref}")

            source_reference = data["derivation_rule"]["derivation_source_reference"]
            derivation_source = resolve_repo_file(
                source_reference,
                purpose="DER derivation source",
                allowed_derivation_source=True,
            )
            validate_der_provenance(data, selected_srf_paths, derivation_source, der_relative)
            der_source_srf_ids.update(data["source_srf_ids"])

        if investigation_dir.name == "b2-governance-cohort":
            missing_der = sorted(set(srf_records) - der_source_srf_ids)
            if missing_der:
                raise SystemExit(
                    f"B2 DER execution incomplete; missing DER source SRF id(s): {', '.join(missing_der)}"
                )



B2_REFERENCE_DETERMINATIONS = {
    "der-b2-aws-iam-request-context-policy-evaluation-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "satisfied",
    },
    "der-b2-cedar-amazon-verified-permissions-policy-store-evaluation-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "satisfied",
    },
    "der-b2-envoy-ext-authz-external-authorization-boundary": {
        "I4.m_R": "unavailable",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "unavailable",
        "I4.m_LE": "satisfied",
    },
    "der-b2-google-zanzibar-relation-tuple-check-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "unavailable",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "unavailable",
    },
    "der-b2-hashicorp-vault-authenticated-path-policy-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "satisfied",
    },
    "der-b2-istio-authorizationpolicy-workload-action-order-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "satisfied",
    },
    "der-b2-kubernetes-rbac-admission-api-server-admission-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "satisfied",
    },
    "der-b2-open-policy-agent-gatekeeper-admission-audit-enforcement-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "satisfied",
        "I4.m_E": "satisfied",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "satisfied",
    },
    "der-b2-openfga-authorization-model-version-boundary": {
        "I4.m_R": "satisfied",
        "I4.m_L": "unavailable",
        "I4.m_E": "unavailable",
        "I4.m_RL": "satisfied",
        "I4.m_LE": "unavailable",
    },
}

DETERMINATION_RESULT = {
    "satisfied": ("observed", 1),
    "not_satisfied": ("observed", 0),
    "unavailable": ("missing", None),
}


def b2_measurement_rules() -> set[str]:
    registration = require_json("investigations/b2-governance-cohort/preregistration/i1_i5_registration.json")
    if not isinstance(registration, dict):
        raise SystemExit("B2 I1-I5 registration must be an object")
    vector = registration.get("measurement_vector")
    if not isinstance(vector, dict) or vector.get("id") != "I4":
        raise SystemExit("B2 measurement vector I4 is not registered")
    components = vector.get("components")
    if not isinstance(components, list):
        raise SystemExit("B2 measurement vector components must be a list")
    rules: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            raise SystemExit("B2 measurement vector component must be an object")
        name = component.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit("B2 measurement vector component missing name")
        if component.get("type") != "boolean_or_missing":
            raise SystemExit(f"B2 measurement rule has unsupported type: {name}")
        rules.add(f"I4.{name}")
    expected = {"I4.m_R", "I4.m_L", "I4.m_E", "I4.m_RL", "I4.m_LE"}
    if rules != expected:
        raise SystemExit(f"B2 measurement rules do not match registered I4 components: {sorted(rules)}")
    return rules


def b2_measurement_conditions() -> dict[str, str]:
    registration = require_json("investigations/b2-governance-cohort/preregistration/i1_i5_registration.json")
    if not isinstance(registration, dict):
        raise SystemExit("B2 I1-I5 registration must be an object")
    vector = registration.get("measurement_vector")
    if not isinstance(vector, dict):
        raise SystemExit("B2 measurement vector I4 is not registered")
    components = vector.get("components")
    if not isinstance(components, list):
        raise SystemExit("B2 measurement vector components must be a list")
    conditions: dict[str, str] = {}
    for component in components:
        if not isinstance(component, dict):
            raise SystemExit("B2 measurement vector component must be an object")
        name = component.get("name")
        meaning = component.get("meaning")
        if isinstance(name, str) and isinstance(meaning, str) and meaning:
            conditions[f"I4.{name}"] = meaning
    return conditions


def der_records_for(investigation_dir: Path) -> dict[str, tuple[dict[str, object], Path]]:
    records: dict[str, tuple[dict[str, object], Path]] = {}
    for path in sorted((investigation_dir / "der").glob("*.der.json")):
        relative = str(path.relative_to(ROOT))
        data = require_json(relative)
        if not isinstance(data, dict):
            raise SystemExit(f"DER must be an object: {relative}")
        validate_json_object_against_schema(data, "schemas/der.schema.json", relative)
        der_id = data["id"]
        if not isinstance(der_id, str):
            raise SystemExit(f"DER id must be a string: {relative}")
        if der_id in records:
            raise SystemExit(f"duplicate DER id in {investigation_dir.relative_to(ROOT)}: {der_id}")
        records[der_id] = (data, path)
    return records


def validate_msr_contract() -> None:
    """Validate B2 MSR files as bounded DER-derived measurement records."""
    rules = b2_measurement_rules()
    conditions = b2_measurement_conditions()
    required_measurements = {rule.split(".", 1)[1] for rule in rules}
    for investigation_dir in sorted((ROOT / "investigations").iterdir()):
        if not investigation_dir.is_dir():
            continue
        msr_dir = investigation_dir / "msr"
        if not msr_dir.is_dir():
            continue
        msr_paths = sorted(msr_dir.glob("*.msr.json"))
        if not msr_paths:
            continue
        der_records = der_records_for(investigation_dir)
        srf_records = srf_records_for(investigation_dir)
        msr_ids: set[str] = set()
        for path in msr_paths:
            msr_relative = str(path.relative_to(ROOT))
            msr = require_json(msr_relative)
            if not isinstance(msr, dict):
                raise SystemExit(f"MSR must be an object: {msr_relative}")
            validate_json_object_against_schema(msr, "schemas/msr.schema.json", msr_relative)
            if msr["id"] in msr_ids:
                raise SystemExit(f"duplicate MSR id in {investigation_dir.relative_to(ROOT)}: {msr['id']}")
            msr_ids.add(msr["id"])
            if msr["investigation_id"] != investigation_dir.name:
                raise SystemExit(f"{msr_relative} investigation_id does not match directory: {msr['investigation_id']}")

            declared_der_ids = set(msr["source_der_ids"])
            for der_id in declared_der_ids:
                if der_id not in der_records:
                    raise SystemExit(f"{msr_relative} references missing DER id: {der_id}")
                der, _ = der_records[der_id]
                if der.get("investigation_id") != msr["investigation_id"]:
                    raise SystemExit(f"{msr_relative} references DER from another investigation: {der_id}")
                expected_srf_id = f"srf-b2-{msr['system_id']}"
                if der.get("source_srf_ids") != [expected_srf_id]:
                    raise SystemExit(f"{msr_relative} references DER from another system: {der_id}")

            seen_measurements: set[str] = set()
            for entry in msr["measurements"]:
                mid = entry["measurement_id"]
                if mid in seen_measurements:
                    raise SystemExit(f"{msr_relative} contains duplicate measurement: {mid}")
                seen_measurements.add(mid)
                if entry["rule_id"] not in rules or entry["rule_id"] != f"I4.{mid}":
                    raise SystemExit(f"{msr_relative} uses unknown measurement rule: {entry['rule_id']}")
                if entry["allowed_domain"] != [0, 1, None]:
                    raise SystemExit(f"{msr_relative} has invalid value domain for {mid}")
                if entry["status"] == "missing" and entry["value"] is not None:
                    raise SystemExit(f"{msr_relative} missing measurement has non-null value: {mid}")
                if entry["status"] == "observed" and entry["value"] not in (0, 1):
                    raise SystemExit(f"{msr_relative} observed measurement has invalid value: {mid}")
                basis = entry["basis"]
                if basis["source_der_id"] not in entry["source_der_ids"]:
                    raise SystemExit(f"{msr_relative} measurement basis uses undeclared DER: {mid}")
                if basis["registered_condition"] != conditions[entry["rule_id"]]:
                    raise SystemExit(f"{msr_relative} measurement basis does not match registered condition: {mid}")
                expected_status, expected_value = DETERMINATION_RESULT[basis["determination"]]
                if entry["status"] != expected_status or entry["value"] != expected_value:
                    raise SystemExit(f"{msr_relative} measurement result conflicts with basis determination: {mid}")
                reference_expected = B2_REFERENCE_DETERMINATIONS.get(basis["source_der_id"], {}).get(entry["rule_id"])
                if reference_expected is not None and basis["determination"] != reference_expected:
                    raise SystemExit(f"{msr_relative} measurement determination conflicts with canonical reference execution: {mid}")
                entry_der_ids = set(entry["source_der_ids"])
                if not entry_der_ids <= declared_der_ids:
                    raise SystemExit(f"{msr_relative} measurement uses undeclared DER: {mid}")
                selected_observations: set[str] = set()
                for der_id in entry_der_ids:
                    der = der_records[der_id][0]
                    _surfaces, observations, _paths = collect_selected_srf_lineage(der, srf_records, msr_relative)
                    selected_observations.update(observations)
                for ref in entry["evidence_trace_refs"]:
                    if ref not in selected_observations:
                        raise SystemExit(f"{msr_relative} evidence trace is outside declared DER lineage: {ref}")

            missing = sorted(required_measurements - seen_measurements)
            if missing:
                raise SystemExit(f"{msr_relative} missing required measurement(s): {', '.join(missing)}")

            provenance = msr["provenance"]
            resolved = {resolve_repo_file(ref, purpose="MSR provenance") for ref in provenance["created_from"]}
            required = {der_records[der_id][1].resolve() for der_id in declared_der_ids}
            registry_path = resolve_repo_file(msr["measurement_registry_ref"]["path"], purpose="MSR measurement registry")
            required.add(registry_path.resolve())
            missing_sources = sorted(str(item.relative_to(ROOT)) for item in required - resolved)
            if missing_sources:
                raise SystemExit(f"{msr_relative} provenance missing required source(s): {', '.join(missing_sources)}")

def validate_move_ledger() -> None:
    require_path("MOVES.md")
    text = (ROOT / "MOVES.md").read_text(encoding="utf-8")
    required_destinations = ["papers/paper-b2/main.tex", "papers/paper-b2/references.bib"]
    for destination in required_destinations:
        if destination not in text:
            raise SystemExit(f"MOVES.md missing destination: {destination}")


def main() -> None:
    for relative in REQUIRED_TOP_LEVEL:
        if not (ROOT / relative).is_dir():
            raise SystemExit(f"missing required top-level directory: {relative}")
    for relative in REQUIRED_PATHS:
        require_path(relative)
    for base in INVESTIGATIONS:
        for item in INVESTIGATION_ITEMS:
            require_path(f"{base}/{item}")
    for relative in [*SCHEMAS, *REGISTRIES]:
        require_json(relative)
    validate_yaml_syntax()
    validate_bor_schemas()
    validate_srf_registry()
    validate_der_contract()
    validate_msr_contract()
    subprocess.run(["python3", "scripts/build_dataset.py", "--check"], cwd=ROOT, check=True)
    validate_registered_paths()
    validate_markdown_links()
    validate_latex_inputs()
    validate_repository_first_paper_template()
    validate_standard_paper_structure()
    validate_move_ledger()
    subprocess.run(["python3", "scripts/check_registry.py"], cwd=ROOT, check=True)
    publication_build = subprocess.run(["python3", "scripts/build_papers.py"], cwd=ROOT)
    if publication_build.returncode == 2:
        print("publication validation unavailable: missing TeX toolchain")
    elif publication_build.returncode != 0:
        raise SystemExit(f"publication validation failed with exit code {publication_build.returncode}")
    print("repository topology validation passed")


if __name__ == "__main__":
    main()
