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
    validate_registered_paths()
    validate_markdown_links()
    validate_latex_inputs()
    validate_repository_first_paper_template()
    validate_standard_paper_structure()
    validate_move_ledger()
    subprocess.run(["python3", "scripts/check_registry.py"], cwd=ROOT, check=True)
    publication_build = subprocess.run(["python3", "scripts/build_papers.py"], cwd=ROOT)
    if publication_build.returncode != 0:
        raise SystemExit(f"publication validation failed with exit code {publication_build.returncode}")
    print("repository topology validation passed")


if __name__ == "__main__":
    main()
