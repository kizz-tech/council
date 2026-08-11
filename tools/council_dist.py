#!/usr/bin/env python3
"""Verify, build, inspect, and materialize Council distribution surfaces.

The repository is always the source of truth. Installed targets are one-way
derivatives. This tool refuses unknown drift and never reverse-syncs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = Path(".codex-plugin/plugin.json")
LOCK_PATH = Path("council.lock.json")
SKILL_PATH = Path("skills/engineering-council")
ADVISOR_PATH = Path("advisors/engineering-council")
PROVENANCE_PATH = Path("provenance/engineering-council/generation-1.json")
ROSTER_RECONSTRUCTION_PATH = Path(
    "provenance/engineering-council/generation-1-roster-reconstruction.json"
)
GENERATION_ONE_ROSTER_PATH = Path("rosters/engineering-council/generation-1.json")
REPRESENTATIVE_FAMILY_PATH = Path("knowledge/representatives/families")
REPRESENTATIVE_LIBRARY_PATH = Path("knowledge/representatives/library.json")
REPRESENTATIVE_INDEX_PATH = Path("knowledge/representatives/index.json")
ROSTER_PATH = Path("rosters")
REPRESENTATIVE_SCHEMA_PATH = Path("schemas/representative.schema.json")
ROSTER_SCHEMA_PATH = Path("schemas/roster.schema.json")
SCREENING_CELL_REGISTRY_PATH = Path("docs/experiments/screening-cells.json")
GENERATION_ONE_PROVENANCE_SHA256 = (
    "3d0712562c3db115cfabe15e02c43940e9fd626b6ee862cf630fbc31141db6ed"
)

REPRESENTATION_KEYS = {
    "id", "name", "representation_type", "admission_status", "lens",
    "decision_functions", "lineage_ids", "primary_sources", "positions",
    "decision_questions", "counterweights", "misuse_risks",
    "evidence_boundary", "confidence",
}
SOURCE_KEYS = {"id", "title", "year", "locator", "evidence_locator"}
POSITION_KEYS = {"statement", "source_ids", "scope"}
COUNTERWEIGHT_KEYS = {"relation", "target_or_position"}
COUNTERWEIGHT_RELATIONS = {
    "challenged-by", "bounded-by", "counterbalances", "competes-with", "gap",
}

EXPECTED_ADVISORS = {
    "clean-boundary-architect.toml": "clean_boundary_architect",
    "domain-model-cartographer.toml": "domain_model_cartographer",
    "evolutionary-deep-pragmatist.toml": "evolutionary_deep_pragmatist",
    "production-systems-sentinel.toml": "production_systems_sentinel",
}

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |PGP )?PRIVATE KEY-----"),
)
PERSONAL_PATH_PATTERNS = (
    re.compile(re.escape("/" + "Users/")),
    re.compile(re.escape("C:" + "\\Users\\"), re.IGNORECASE),
)
MUTABLE_SOURCE_LOCATOR_PATTERNS = (
    re.compile(r"^https://github\.com/[^/]+/[^/]+/blob/(?:main|master)/"),
)
GENERATED_REPOSITORY_ROOTS = (
    Path(".agents"),
    Path(".codex/agents"),
    Path(".council-local"),
    Path("dist"),
    Path("build"),
    Path(".pytest_cache"),
    Path(".idea"),
    Path(".vscode"),
)
MATERIALIZATION_REPOSITORY_ROOTS = (
    Path(".agents"),
    Path(".codex/agents"),
    Path(".council-local"),
)
BUILD_REPOSITORY_ROOTS = (Path("dist"), Path("build"))


class CouncilError(RuntimeError):
    """A safe, user-facing validation or materialization failure."""


@dataclass(frozen=True)
class TargetFile:
    source: Path
    target: Path
    receipt_key: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CouncilError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CouncilError(f"expected JSON object at {path}")
    return value


def json_text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def emit(value: object) -> None:
    print(json_text(value), end="")


def regular_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise CouncilError(f"missing directory: {root}")
    return sorted(path for path in root.rglob("*") if path.is_file())


def path_within(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def paths_overlap(left: Path, right: Path) -> bool:
    return path_within(left, right) or path_within(right, left)


def relative_within(relative: Path, parent: Path) -> bool:
    return relative == parent or parent in relative.parents


def ignored_repository_source(relative: Path) -> bool:
    if any(relative_within(relative, ignored) for ignored in GENERATED_REPOSITORY_ROOTS):
        return True
    if any(
        part == ".git"
        or part == "__pycache__"
        or ".council-backup-" in part
        or ".council-stage-" in part
        for part in relative.parts
    ):
        return True
    if relative.suffix == ".pyc" or relative.name == ".DS_Store":
        return True
    if relative.name == ".env" or (
        relative.name.startswith(".env.") and relative.name != ".env.example"
    ):
        return True
    return False


def repository_source_files(root: Path) -> list[Path]:
    """Return every versioned source candidate except the self-referential lock."""
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative == LOCK_PATH:
            continue
        if ignored_repository_source(relative):
            continue
        paths.append(path)
    return sorted(paths)


def component_paths(root: Path) -> list[Path]:
    return repository_source_files(root)


def plugin_version(root: Path) -> str:
    manifest = json_load(root / PLUGIN_PATH)
    version = manifest.get("version")
    if not isinstance(version, str):
        raise CouncilError("plugin version must be a string")
    return version


def build_lock(root: Path) -> dict:
    return {
        "schema_version": "council.lock/1",
        "product_version": plugin_version(root),
        "files": {
            path.relative_to(root).as_posix(): sha256(path)
            for path in component_paths(root)
        },
    }


def parse_skill_frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise CouncilError(f"missing YAML frontmatter: {path}")
    header = match.group(1)
    name_match = re.search(r"^name:\s*([^\n]+)$", header, re.MULTILINE)
    if not name_match or not re.search(r"^description:\s*", header, re.MULTILINE):
        raise CouncilError(f"skill frontmatter requires name and description: {path}")
    return name_match.group(1).strip().strip('"\''), text


def validate_plugin(root: Path) -> dict:
    manifest = json_load(root / PLUGIN_PATH)
    required = ("name", "version", "description", "author", "skills", "interface")
    missing = [key for key in required if key not in manifest]
    if missing:
        raise CouncilError(f"plugin manifest missing fields: {', '.join(missing)}")
    if manifest["name"] != "council":
        raise CouncilError("plugin name must remain 'council' before an explicit rename decision")
    if not re.fullmatch(
        r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)",
        manifest["version"],
    ):
        raise CouncilError(f"plugin version is not strict SemVer: {manifest['version']!r}")
    if manifest["skills"] != "./skills/":
        raise CouncilError("plugin skills path must be './skills/'")
    if not isinstance(manifest["author"], dict) or not manifest["author"].get("name"):
        raise CouncilError("plugin author.name is required")
    interface = manifest["interface"]
    if not isinstance(interface, dict):
        raise CouncilError("plugin interface must be an object")
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not interface.get(key):
            raise CouncilError(f"plugin interface.{key} is required")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(item, str) for item in capabilities
    ):
        raise CouncilError("plugin interface.capabilities must be a string array")
    default_prompt = interface.get("defaultPrompt")
    if (
        not isinstance(default_prompt, list)
        or not default_prompt
        or len(default_prompt) > 3
        or not all(
        isinstance(item, str) and item.strip() for item in default_prompt
        )
        or any(len(item) > 128 for item in default_prompt)
    ):
        raise CouncilError(
            "plugin interface.defaultPrompt must contain 1-3 non-empty strings "
            "of at most 128 characters"
        )
    return manifest


def validate_skill(root: Path) -> None:
    skill_file = root / SKILL_PATH / "SKILL.md"
    name, text = parse_skill_frontmatter(skill_file)
    if name != "engineering-council":
        raise CouncilError(f"unexpected skill name: {name!r}")
    for advisor_name in EXPECTED_ADVISORS.values():
        if f"`{advisor_name}`" not in text:
            raise CouncilError(f"skill does not declare advisor {advisor_name}")
    metadata = root / SKILL_PATH / "agents/openai.yaml"
    metadata_text = metadata.read_text(encoding="utf-8")
    for field in ("display_name:", "short_description:", "default_prompt:"):
        if field not in metadata_text:
            raise CouncilError(f"skill metadata missing {field} in {metadata}")


def validate_advisors(root: Path) -> dict[str, str]:
    identities: dict[str, str] = {}
    directory = root / ADVISOR_PATH
    actual_tomls = {path.name for path in directory.glob("*.toml")}
    if actual_tomls != set(EXPECTED_ADVISORS):
        raise CouncilError(
            "advisor file set mismatch: "
            f"expected {sorted(EXPECTED_ADVISORS)}, found {sorted(actual_tomls)}"
        )
    for filename, expected_name in EXPECTED_ADVISORS.items():
        path = directory / filename
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise CouncilError(f"invalid advisor TOML at {path}: {exc}") from exc
        for field in ("name", "description", "developer_instructions"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                raise CouncilError(f"advisor {filename} missing non-empty {field}")
        if data["name"] != expected_name:
            raise CouncilError(f"advisor {filename} has unexpected name {data['name']!r}")
        if data.get("sandbox_mode") != "read-only":
            raise CouncilError(f"advisor {filename} must remain read-only")
        identities[expected_name] = sha256(path)
    return identities


def public_surface_files(root: Path) -> Iterable[Path]:
    yield from repository_source_files(root)
    lock = root / LOCK_PATH
    if lock.is_file():
        yield lock


def validate_public_surface(root: Path) -> None:
    findings: list[str] = []
    for path in public_surface_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PERSONAL_PATH_PATTERNS:
            if pattern.search(text):
                findings.append(f"personal absolute path in {path.relative_to(root)}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"secret-shaped value in {path.relative_to(root)}")
    if findings:
        raise CouncilError("public-surface scan failed: " + "; ".join(findings))


def validate_provenance(root: Path) -> None:
    actual_provenance_hash = sha256(root / PROVENANCE_PATH)
    if actual_provenance_hash != GENERATION_ONE_PROVENANCE_SHA256:
        raise CouncilError(
            "generation-one evaluation receipt is immutable: "
            f"expected {GENERATION_ONE_PROVENANCE_SHA256}, "
            f"found {actual_provenance_hash}"
        )
    provenance = json_load(root / PROVENANCE_PATH)
    imports = provenance.get("import_identity")
    if not isinstance(imports, dict):
        raise CouncilError("provenance import_identity is required")
    expected_skill_hash = imports.get("canonical_engineering_skill_sha256")
    actual_skill_hash = sha256(root / SKILL_PATH / "SKILL.md")
    if expected_skill_hash != actual_skill_hash:
        raise CouncilError(
            "imported skill differs from generation-one identity: "
            f"expected {expected_skill_hash}, found {actual_skill_hash}"
        )
    expected_interface_hash = imports.get("skill_interface_sha256")
    actual_interface_hash = sha256(root / SKILL_PATH / "agents/openai.yaml")
    if expected_interface_hash != actual_interface_hash:
        raise CouncilError("imported skill interface differs from generation-one identity")
    expected_advisors = imports.get("advisors")
    if not isinstance(expected_advisors, dict):
        raise CouncilError("provenance advisor import hashes are required")
    actual_advisors = validate_advisors(root)
    if expected_advisors != actual_advisors:
        raise CouncilError("imported advisor hashes differ from generation-one identity")
    baseline = json_load(root / ROSTER_RECONSTRUCTION_PATH)
    require_keys(
        baseline,
        {
            "schema_version", "generation", "evaluation_receipt_path",
            "evaluation_receipt_sha256", "roster_path", "roster_sha256",
            "status", "claim_boundary",
        },
        str(ROSTER_RECONSTRUCTION_PATH),
    )
    if baseline["schema_version"] != "council.provenance-link/1":
        raise CouncilError("roster reconstruction sidecar has unsupported schema_version")
    if baseline["generation"] != provenance.get("generation"):
        raise CouncilError("roster reconstruction generation must match its receipt")
    if baseline["evaluation_receipt_path"] != PROVENANCE_PATH.as_posix():
        raise CouncilError("roster reconstruction points to an unexpected receipt path")
    if baseline["evaluation_receipt_sha256"] != actual_provenance_hash:
        raise CouncilError("roster reconstruction receipt hash does not match")
    if baseline["roster_path"] != GENERATION_ONE_ROSTER_PATH.as_posix():
        raise CouncilError("generation-one provenance points to an unexpected roster path")
    if baseline["status"] != "reconstructed-post-evaluation-baseline":
        raise CouncilError("generation-one roster identity must disclose reconstruction status")
    require_string(
        baseline["claim_boundary"],
        f"{ROSTER_RECONSTRUCTION_PATH}.claim_boundary",
        minimum=30,
    )
    actual_roster_hash = sha256(root / GENERATION_ONE_ROSTER_PATH)
    if baseline["roster_sha256"] != actual_roster_hash:
        raise CouncilError(
            "generation-one roster differs from its repository baseline identity"
        )


def require_keys(value: dict, expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise CouncilError(
            f"{context} key mismatch; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def require_string(value: object, context: str, *, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise CouncilError(f"{context} must be a string of length >= {minimum}")
    return value


def require_slug(value: object, context: str) -> str:
    text = require_string(value, context)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", text):
        raise CouncilError(f"{context} must be a lowercase kebab-case identifier")
    return text


def require_string_list(
    value: object,
    context: str,
    *,
    exact: int | None = None,
    minimum: int = 1,
    item_minimum: int = 3,
    slugs: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        raise CouncilError(f"{context} must be an array")
    if exact is not None and len(value) != exact:
        raise CouncilError(f"{context} must contain exactly {exact} items")
    if exact is None and len(value) < minimum:
        raise CouncilError(f"{context} must contain at least {minimum} items")
    items = [
        require_slug(item, f"{context}[{index}]")
        if slugs
        else require_string(item, f"{context}[{index}]", minimum=item_minimum)
        for index, item in enumerate(value)
    ]
    if len(set(items)) != len(items):
        raise CouncilError(f"{context} contains duplicate values")
    return items


def validate_representative_unit(
    value: object, context: str, *, max_source_year: int
) -> tuple[str, str, str]:
    if not isinstance(value, dict):
        raise CouncilError(f"{context} must be an object")
    require_keys(value, REPRESENTATION_KEYS, context)
    representation_id = require_slug(value["id"], f"{context}.id")
    require_string(value["name"], f"{context}.name", minimum=2)
    representation_type = value["representation_type"]
    if representation_type not in {
        "person", "joint_authors", "school", "functional_lens", "source_corpus",
    }:
        raise CouncilError(f"{context}.representation_type is unsupported")
    admission_status = value["admission_status"]
    if admission_status not in {"admitted", "qualified_counterweight", "source_corpus"}:
        raise CouncilError(f"{context}.admission_status is unsupported")
    if (representation_type == "source_corpus") != (admission_status == "source_corpus"):
        raise CouncilError(f"{context} source_corpus type and status must agree")
    require_string(value["lens"], f"{context}.lens", minimum=20)
    require_string_list(
        value["decision_functions"], f"{context}.decision_functions", slugs=True
    )
    require_string_list(value["lineage_ids"], f"{context}.lineage_ids", slugs=True)

    sources = value["primary_sources"]
    if not isinstance(sources, list) or not sources:
        raise CouncilError(f"{context}.primary_sources must be non-empty")
    if representation_type != "source_corpus" and len(sources) != 2:
        raise CouncilError(
            f"{context}.primary_sources must contain exactly 2 sources "
            "unless representation_type is source_corpus"
        )
    source_ids: set[str] = set()
    source_locators: set[str] = set()
    for index, source in enumerate(sources):
        source_context = f"{context}.primary_sources[{index}]"
        if not isinstance(source, dict):
            raise CouncilError(f"{source_context} must be an object")
        require_keys(source, SOURCE_KEYS, source_context)
        source_id = require_slug(source["id"], f"{source_context}.id")
        if source_id in source_ids:
            raise CouncilError(f"{context} contains duplicate source id {source_id!r}")
        source_ids.add(source_id)
        require_string(source["title"], f"{source_context}.title", minimum=3)
        year = source["year"]
        if (
            not isinstance(year, int)
            or isinstance(year, bool)
            or not 1940 <= year <= max_source_year
        ):
            raise CouncilError(
                f"{source_context}.year must be from 1940 through {max_source_year}"
            )
        locator = require_string(source["locator"], f"{source_context}.locator")
        if not locator.startswith("https://"):
            raise CouncilError(f"{source_context}.locator must use HTTPS")
        if locator in source_locators:
            raise CouncilError(f"{context} contains duplicate source locator {locator!r}")
        source_locators.add(locator)
        if any(pattern.search(locator) for pattern in MUTABLE_SOURCE_LOCATOR_PATTERNS):
            raise CouncilError(
                f"{source_context}.locator uses a mutable repository branch; "
                "pin an immutable commit"
            )
        require_string(source["evidence_locator"], f"{source_context}.evidence_locator", minimum=8)

    positions = value["positions"]
    if not isinstance(positions, list) or len(positions) != 3:
        raise CouncilError(f"{context}.positions must contain exactly 3 positions")
    for index, position in enumerate(positions):
        position_context = f"{context}.positions[{index}]"
        if not isinstance(position, dict):
            raise CouncilError(f"{position_context} must be an object")
        require_keys(position, POSITION_KEYS, position_context)
        require_string(position["statement"], f"{position_context}.statement", minimum=20)
        references = require_string_list(
            position["source_ids"], f"{position_context}.source_ids", slugs=True
        )
        if set(references) - source_ids:
            raise CouncilError(f"{position_context}.source_ids contains an unknown source")
        require_string(position["scope"], f"{position_context}.scope", minimum=8)

    require_string_list(
        value["decision_questions"],
        f"{context}.decision_questions",
        exact=3,
        item_minimum=12,
    )
    counterweights = value["counterweights"]
    if not isinstance(counterweights, list) or not counterweights:
        raise CouncilError(f"{context}.counterweights must be non-empty")
    for index, counterweight in enumerate(counterweights):
        counterweight_context = f"{context}.counterweights[{index}]"
        if not isinstance(counterweight, dict):
            raise CouncilError(f"{counterweight_context} must be an object")
        require_keys(counterweight, COUNTERWEIGHT_KEYS, counterweight_context)
        if counterweight["relation"] not in COUNTERWEIGHT_RELATIONS:
            raise CouncilError(f"{counterweight_context}.relation is unsupported")
        require_string(
            counterweight["target_or_position"],
            f"{counterweight_context}.target_or_position",
            minimum=12,
        )
    require_string_list(
        value["misuse_risks"],
        f"{context}.misuse_risks",
        exact=2,
        item_minimum=12,
    )
    require_string(value["evidence_boundary"], f"{context}.evidence_boundary", minimum=30)
    if value["confidence"] not in {"high", "medium", "limited"}:
        raise CouncilError(f"{context}.confidence must be high, medium, or limited")
    return representation_id, representation_type, admission_status


def load_representative_library_manifest(root: Path) -> tuple[dict, date]:
    manifest = json_load(root / REPRESENTATIVE_LIBRARY_PATH)
    require_keys(
        manifest,
        {"schema_version", "library_version", "knowledge_as_of", "families"},
        str(REPRESENTATIVE_LIBRARY_PATH),
    )
    if manifest["schema_version"] != "council.representative-library/1":
        raise CouncilError("representative library manifest has unsupported schema_version")
    library_version = require_string(
        manifest["library_version"],
        f"{REPRESENTATIVE_LIBRARY_PATH}.library_version",
    )
    if library_version != plugin_version(root):
        raise CouncilError("representative library version must match the product version")
    cutoff_text = require_string(
        manifest["knowledge_as_of"],
        f"{REPRESENTATIVE_LIBRARY_PATH}.knowledge_as_of",
    )
    try:
        cutoff = date.fromisoformat(cutoff_text)
    except ValueError as exc:
        raise CouncilError("representative library knowledge_as_of must be an ISO date") from exc
    if cutoff > date.today():
        raise CouncilError("representative library knowledge_as_of cannot be future-dated")
    families = require_string_list(
        manifest["families"],
        f"{REPRESENTATIVE_LIBRARY_PATH}.families",
        slugs=True,
    )
    if families != sorted(families):
        raise CouncilError("representative library families must be sorted")
    return manifest, cutoff


def representative_family_files(root: Path, expected_family_ids: set[str]) -> list[Path]:
    directory = root / REPRESENTATIVE_FAMILY_PATH
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    family_ids = {path.stem for path in files}
    if family_ids != expected_family_ids:
        raise CouncilError(
            "representative family set mismatch: "
            f"expected {sorted(expected_family_ids)}, "
            f"found {sorted(family_ids)}"
        )
    return files


def build_representative_index(
    root: Path, manifest: dict, cutoff: date
) -> tuple[dict, dict[str, dict[str, str]]]:
    family_rows: list[dict] = []
    representation_metadata: dict[str, dict[str, str]] = {}
    source_binding_count = 0
    unique_locators: set[str] = set()
    position_count = 0
    required = {"schema_version", "family_id", "knowledge_as_of", "representations"}
    optional = {
        "rejected_candidates", "saturation", "open_gaps", "shared_lineages",
        "contradictions",
    }
    expected_family_ids = set(manifest["families"])
    for path in representative_family_files(root, expected_family_ids):
        relative = path.relative_to(root)
        family = json_load(path)
        missing = required - set(family)
        unexpected = set(family) - required - optional
        if missing or unexpected:
            raise CouncilError(
                f"{relative} top-level key mismatch; missing={sorted(missing)}, "
                f"extra={sorted(unexpected)}"
            )
        if family["schema_version"] != "council.representative-family/1":
            raise CouncilError(f"{relative} has unsupported schema_version")
        if family["family_id"] != path.stem:
            raise CouncilError(f"{relative} family_id must match its filename")
        if family["knowledge_as_of"] != cutoff.isoformat():
            raise CouncilError(f"{relative} knowledge_as_of must match the research cutoff")
        representations = family["representations"]
        if not isinstance(representations, list) or not representations:
            raise CouncilError(f"{relative}.representations must be a non-empty array")
        for index, representation in enumerate(representations):
            representation_id, representation_type, admission_status = (
                validate_representative_unit(
                    representation,
                    f"{relative}.representations[{index}]",
                    max_source_year=cutoff.year,
                )
            )
            if representation_id in representation_metadata:
                raise CouncilError(f"duplicate representation id {representation_id!r}")
            representation_metadata[representation_id] = {
                "representation_type": representation_type,
                "admission_status": admission_status,
            }
            source_binding_count += len(representation["primary_sources"])
            unique_locators.update(
                source["locator"] for source in representation["primary_sources"]
            )
            position_count += len(representation["positions"])
        family_rows.append({
            "family_id": path.stem,
            "path": relative.as_posix(),
            "representation_count": len(representations),
            "sha256": sha256(path),
        })
    index = {
        "schema_version": "council.representative-index/1",
        "library_version": manifest["library_version"],
        "library_manifest_sha256": sha256(root / REPRESENTATIVE_LIBRARY_PATH),
        "knowledge_as_of": cutoff.isoformat(),
        "family_count": len(family_rows),
        "representation_count": len(representation_metadata),
        "primary_source_binding_count": source_binding_count,
        "unique_source_locator_count": len(unique_locators),
        "position_count": position_count,
        "families": family_rows,
    }
    return index, representation_metadata


def validate_representative_library(
    root: Path, *, check_index: bool = True
) -> tuple[dict, dict[str, dict[str, str]]]:
    for schema_path in (REPRESENTATIVE_SCHEMA_PATH, ROSTER_SCHEMA_PATH):
        schema = json_load(root / schema_path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise CouncilError(f"unsupported JSON Schema declaration at {schema_path}")
    manifest, cutoff = load_representative_library_manifest(root)
    current_index, representation_metadata = build_representative_index(
        root, manifest, cutoff
    )
    if check_index and json_load(root / REPRESENTATIVE_INDEX_PATH) != current_index:
        raise CouncilError(
            "knowledge/representatives/index.json is stale; "
            "review changes, then run index --write"
        )
    return current_index, representation_metadata


def validate_roster_prompt_source(
    root: Path, prompt_source_value: object, runtime_profile: str, context: str
) -> None:
    prompt_source_text = require_string(
        prompt_source_value, f"{context}.prompt_source", minimum=3
    )
    relative = Path(prompt_source_text)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or len(relative.parts) < 3
        or relative.parts[0] != "advisors"
        or relative.suffix != ".toml"
    ):
        raise CouncilError(
            f"{context}.prompt_source must be an advisors/<council>/*.toml file"
        )
    prompt_source = (root / relative).resolve()
    if not prompt_source.is_file() or root.resolve() not in prompt_source.parents:
        raise CouncilError(f"{context}.prompt_source must resolve inside the repository")
    try:
        prompt = tomllib.loads(prompt_source.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise CouncilError(f"invalid roster prompt TOML at {relative}: {exc}") from exc
    for field in ("name", "description", "developer_instructions"):
        require_string(prompt.get(field), f"{context}.prompt_source.{field}")
    if prompt["name"] != runtime_profile:
        raise CouncilError(
            f"{context}.runtime_profile {runtime_profile!r} does not match "
            f"prompt source name {prompt['name']!r}"
        )
    if prompt.get("sandbox_mode") != "read-only":
        raise CouncilError(f"{context}.prompt_source must declare sandbox_mode = 'read-only'")


def validate_rosters(
    root: Path, representation_metadata: dict[str, dict[str, str]]
) -> dict:
    roster_files = sorted((root / ROSTER_PATH).rglob("*.json"))
    if not roster_files:
        raise CouncilError("at least one roster JSON is required")
    roster_revisions: set[tuple[str, int]] = set()
    slot_count = 0
    expected_top = {
        "schema_version", "roster_id", "revision", "status", "domain", "purpose",
        "source_generation", "slots", "independence_claim", "known_limits",
    }
    required_slot = {
        "slot_id", "runtime_profile", "representation_mode", "decision_function",
        "lineage_cluster", "prompt_source",
    }
    for path in roster_files:
        relative = path.relative_to(root)
        roster = json_load(path)
        require_keys(roster, expected_top, str(relative))
        if roster["schema_version"] != "council.roster/1":
            raise CouncilError(f"{relative} has unsupported schema_version")
        roster_id = require_slug(roster["roster_id"], f"{relative}.roster_id")
        if (
            not isinstance(roster["revision"], int)
            or isinstance(roster["revision"], bool)
            or roster["revision"] < 1
        ):
            raise CouncilError(f"{relative}.revision must be a positive integer")
        roster_revision = (roster_id, roster["revision"])
        if roster_revision in roster_revisions:
            raise CouncilError(
                f"duplicate roster revision {roster_id!r} revision {roster['revision']}"
            )
        roster_revisions.add(roster_revision)
        if roster["status"] not in {"historical-baseline", "candidate", "retired"}:
            raise CouncilError(f"{relative}.status is unsupported")
        require_string(roster["domain"], f"{relative}.domain", minimum=3)
        require_string(roster["purpose"], f"{relative}.purpose", minimum=20)
        require_string(
            roster["source_generation"],
            f"{relative}.source_generation",
            minimum=3,
        )
        slots = roster["slots"]
        if not isinstance(slots, list) or not slots:
            raise CouncilError(f"{relative}.slots must be non-empty")
        local_slots: set[str] = set()
        for index, slot in enumerate(slots):
            context = f"{relative}.slots[{index}]"
            if not isinstance(slot, dict):
                raise CouncilError(f"{context} must be an object")
            allowed = required_slot | {"representation_ids"}
            missing = required_slot - set(slot)
            extra = set(slot) - allowed
            if missing or extra:
                raise CouncilError(
                    f"{context} key mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
                )
            slot_id = require_slug(slot["slot_id"], f"{context}.slot_id")
            if slot_id in local_slots:
                raise CouncilError(f"duplicate slot id {slot_id!r} in {relative}")
            local_slots.add(slot_id)
            profile = require_string(slot["runtime_profile"], f"{context}.runtime_profile")
            if not re.fullmatch(r"[a-z0-9_]+", profile):
                raise CouncilError(f"{context}.runtime_profile must be snake_case")
            mode = slot["representation_mode"]
            if mode not in {"functional_lens", "library_bound", "hybrid"}:
                raise CouncilError(f"{context}.representation_mode is unsupported")
            bound_ids = slot.get("representation_ids", [])
            if mode == "functional_lens" and bound_ids:
                raise CouncilError(f"{context} functional_lens must not bind library identities")
            if mode != "functional_lens":
                references = require_string_list(
                    bound_ids, f"{context}.representation_ids", slugs=True
                )
                unknown = set(references) - set(representation_metadata)
                if unknown:
                    raise CouncilError(f"{context} references unknown ids {sorted(unknown)}")
                for representation_id in references:
                    if (
                        representation_metadata[representation_id]["admission_status"]
                        == "qualified_counterweight"
                    ):
                        raise CouncilError(
                            f"{context}.representation_ids contains counterweight-only "
                            f"representation {representation_id!r}; a qualified_counterweight "
                            "cannot be bound to a roster slot"
                        )
            require_string(
                slot["decision_function"],
                f"{context}.decision_function",
                minimum=8,
            )
            require_string(
                slot["lineage_cluster"],
                f"{context}.lineage_cluster",
                minimum=3,
            )
            validate_roster_prompt_source(
                root, slot["prompt_source"], profile, context
            )
        slot_count += len(slots)
        independence = roster["independence_claim"]
        if not isinstance(independence, dict):
            raise CouncilError(f"{relative}.independence_claim must be an object")
        require_keys(
            independence, {"lineage", "runtime", "outcome"},
            f"{relative}.independence_claim",
        )
        for key in ("lineage", "runtime", "outcome"):
            require_string(independence[key], f"{relative}.independence_claim.{key}", minimum=8)
        require_string_list(
            roster["known_limits"],
            f"{relative}.known_limits",
            item_minimum=12,
        )
        if roster_revision == ("engineering-council-generation-1", 1):
            profiles = {slot["runtime_profile"] for slot in slots}
            if roster["status"] != "historical-baseline" or len(slots) != 4:
                raise CouncilError("generation-one roster must remain a four-slot historical baseline")
            if profiles != set(EXPECTED_ADVISORS.values()):
                raise CouncilError("generation-one roster differs from the frozen advisor set")
    return {"roster_count": len(roster_files), "slot_count": slot_count}


def validate_screening_cell_registry(root: Path) -> dict:
    registry = json_load(root / SCREENING_CELL_REGISTRY_PATH)
    require_keys(
        registry,
        {
            "schema_version", "model_configuration_count", "packs_per_cell",
            "runs_per_pack", "cell_families", "incumbent_baseline", "expected",
        },
        str(SCREENING_CELL_REGISTRY_PATH),
    )
    if registry["schema_version"] != "council.screening-cells/1":
        raise CouncilError("screening cell registry has unsupported schema_version")
    for key in ("model_configuration_count", "packs_per_cell", "runs_per_pack"):
        value = registry[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise CouncilError(f"screening cell registry {key} must be positive")
    families = registry["cell_families"]
    if not isinstance(families, list) or not families:
        raise CouncilError("screening cell registry cell_families must be non-empty")
    by_id: dict[str, dict] = {}
    cells_per_model = 0
    family_keys = {"id", "applicability", "n", "groupings", "rounds"}
    for index, family in enumerate(families):
        context = f"{SCREENING_CELL_REGISTRY_PATH}.cell_families[{index}]"
        if not isinstance(family, dict):
            raise CouncilError(f"{context} must be an object")
        require_keys(family, family_keys, context)
        family_id = require_string(family["id"], f"{context}.id")
        if family_id in by_id:
            raise CouncilError(f"duplicate screening cell family {family_id!r}")
        by_id[family_id] = family
        if family["applicability"] != "each-model-configuration":
            raise CouncilError(f"{context}.applicability is unsupported")
        n_values = family["n"]
        rounds = family["rounds"]
        if (
            not isinstance(n_values, list)
            or not n_values
            or any(
                not isinstance(value, int) or isinstance(value, bool) or value < 1
                for value in n_values
            )
            or len(set(n_values)) != len(n_values)
        ):
            raise CouncilError(f"{context}.n must contain unique positive integers")
        if (
            not isinstance(rounds, list)
            or not rounds
            or any(
                not isinstance(value, int)
                or isinstance(value, bool)
                or value not in {0, 1, 2}
                for value in rounds
            )
            or len(set(rounds)) != len(rounds)
        ):
            raise CouncilError(f"{context}.rounds must contain unique values from 0, 1, 2")
        groupings = require_string_list(
            family["groupings"], f"{context}.groupings", slugs=True
        )
        cells_per_model += len(n_values) * len(rounds) * len(groupings)
    if set(by_id) != {"T0", "T1", "T2", "T3-breadth", "T3-paired-counterweight"}:
        raise CouncilError("screening cell registry must declare the five core families")
    for baseline_id in ("T0", "T1"):
        baseline = by_id[baseline_id]
        if baseline["n"] != [1] or baseline["rounds"] != [0]:
            raise CouncilError(f"{baseline_id} must remain a one-state, round-zero baseline")
    if by_id["T2"]["rounds"] != [0]:
        raise CouncilError("T2 must remain a round-zero independent ensemble")

    incumbent = registry["incumbent_baseline"]
    require_keys(incumbent, {"id", "applicability", "cell_count"}, "incumbent_baseline")
    if (
        incumbent["id"] != "G-1"
        or incumbent["applicability"]
        != "one-exact-incumbent-model-configuration-only"
        or incumbent["cell_count"] != 1
    ):
        raise CouncilError("G-1 must be one exact incumbent-only baseline cell")
    cross_configuration_cells = cells_per_model * registry["model_configuration_count"]
    total_core_cells = cross_configuration_cells + incumbent["cell_count"]
    total_core_system_runs = (
        total_core_cells * registry["packs_per_cell"] * registry["runs_per_pack"]
    )
    calculated = {
        "cells_per_model_configuration": cells_per_model,
        "cross_configuration_cells": cross_configuration_cells,
        "incumbent_baseline_cells": incumbent["cell_count"],
        "total_core_cells": total_core_cells,
        "total_core_system_runs": total_core_system_runs,
    }
    require_keys(registry["expected"], set(calculated), "screening cell expected totals")
    if registry["expected"] != calculated:
        raise CouncilError(
            f"screening cell expected totals are stale; calculated {calculated}"
        )
    return {
        "screening_core_cells": total_core_cells,
        "screening_core_system_runs": total_core_system_runs,
    }


def verify(root: Path, *, check_lock: bool = True) -> dict:
    manifest = validate_plugin(root)
    validate_skill(root)
    advisor_hashes = validate_advisors(root)
    validate_provenance(root)
    representative_index, representation_metadata = validate_representative_library(root)
    roster_report = validate_rosters(root, representation_metadata)
    screening_report = validate_screening_cell_registry(root)
    validate_public_surface(root)
    current_lock = build_lock(root)
    if check_lock:
        stored_lock = json_load(root / LOCK_PATH)
        if stored_lock != current_lock:
            raise CouncilError("council.lock.json is stale; review changes, then run lock --write")
    return {
        "status": "ok",
        "product": manifest["name"],
        "version": manifest["version"],
        "skill_sha256": sha256(root / SKILL_PATH / "SKILL.md"),
        "advisor_sha256": advisor_hashes,
        "representative_families": representative_index["family_count"],
        "representations": representative_index["representation_count"],
        "primary_source_bindings": representative_index["primary_source_binding_count"],
        "unique_source_locators": representative_index["unique_source_locator_count"],
        "positions": representative_index["position_count"],
        **roster_report,
        **screening_report,
        "locked_files": len(current_lock["files"]),
    }


def artifact_files(root: Path) -> list[Path]:
    paths = [root / PLUGIN_PATH]
    paths.extend(regular_files(root / "skills"))
    return sorted(paths)


def build_artifact(root: Path, output: Path) -> dict:
    root = root.resolve()
    output = output.resolve()
    canonical_roots = ((root / "skills").resolve(), (root / "advisors").resolve())
    if any(paths_overlap(output, source_root) for source_root in canonical_roots):
        raise CouncilError("build output must not overlap canonical skills or advisors")
    if path_within(root, output):
        raise CouncilError("build output must not contain the canonical repository")
    if path_within(output, root) and not any(
        path_within(output, (root / allowed).resolve())
        for allowed in BUILD_REPOSITORY_ROOTS
    ):
        raise CouncilError(
            "repository-local build output must be under dist/ or build/"
        )
    verification = verify(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not output.is_dir():
        raise CouncilError(f"build output is not a directory: {output}")
    if output.exists() and any(output.iterdir()):
        raise CouncilError(f"build output must be absent or empty: {output}")
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.council-stage-", dir=output.parent))
    try:
        built: dict[str, str] = {}
        for source in artifact_files(root):
            relative = source.relative_to(root)
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            built[relative.as_posix()] = sha256(target)
        if output.exists():
            output.rmdir()
        os.replace(stage, output)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {
        "status": "built",
        "product": verification["product"],
        "version": verification["version"],
        "output": str(output),
        "files": built,
    }


def skill_targets(root: Path, skill_root: Path) -> list[TargetFile]:
    source_root = root / SKILL_PATH
    target_root = skill_root / "engineering-council"
    return [
        TargetFile(source=source, target=target_root / source.relative_to(source_root),
                   receipt_key=source.relative_to(source_root).as_posix())
        for source in regular_files(source_root)
    ]


def advisor_targets(root: Path, agent_root: Path) -> list[TargetFile]:
    source_root = root / ADVISOR_PATH
    return [
        TargetFile(source=source_root / filename, target=agent_root / filename,
                   receipt_key=filename)
        for filename in sorted(EXPECTED_ADVISORS)
    ]


def target_status(files: list[TargetFile]) -> list[dict]:
    result: list[dict] = []
    for item in files:
        expected = sha256(item.source)
        if not item.target.exists():
            state, actual = "missing", None
        elif not item.target.is_file():
            state, actual = "drift", "not-a-file"
        else:
            actual = sha256(item.target)
            state = "match" if actual == expected else "drift"
        result.append({
            "path": str(item.target),
            "state": state,
            "expected_sha256": expected,
            "actual_sha256": actual,
        })
    return result


def status_report(root: Path, skill_roots: list[Path], agent_roots: list[Path]) -> dict:
    verify(root)
    targets: list[dict] = []
    for skill_root in skill_roots:
        targets.extend(target_status(skill_targets(root, skill_root.resolve())))
    for agent_root in agent_roots:
        targets.extend(target_status(advisor_targets(root, agent_root.resolve())))
    if not targets:
        raise CouncilError("status requires at least one --skill-root or --agent-root")
    return {
        "status": "match" if all(item["state"] == "match" for item in targets) else "drift",
        "targets": targets,
    }


def receipt_component(path: Path) -> str:
    if path.name == ".council-install.json":
        return "skills/engineering-council"
    if path.name == ".council-engineering-council-install.json":
        return "advisors/engineering-council"
    raise CouncilError(f"unrecognized installation receipt path: {path}")


def receipt_hashes(path: Path, expected_keys: set[str]) -> dict[str, str]:
    if not path.is_file():
        return {}
    receipt = json_load(path)
    expected_metadata = {
        "schema_version": "council.install/1",
        "product": "council",
        "component": receipt_component(path),
    }
    for key, expected in expected_metadata.items():
        if receipt.get(key) != expected:
            raise CouncilError(
                f"invalid installation receipt {key} at {path}: "
                f"expected {expected!r}, found {receipt.get(key)!r}"
            )
    version = receipt.get("version")
    if not isinstance(version, str) or not re.fullmatch(
        r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version
    ):
        raise CouncilError(f"invalid installation receipt version at {path}")
    files = receipt.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(key, str)
        and isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value)
        for key, value in files.items()
    ):
        raise CouncilError(f"invalid installation receipt: {path}")
    if set(files) != expected_keys:
        raise CouncilError(f"installation receipt file set mismatch at {path}")
    return files


def materialization_plan(files: list[TargetFile], receipt_path: Path) -> list[dict]:
    previous = receipt_hashes(receipt_path, {item.receipt_key for item in files})
    plan: list[dict] = []
    for item in files:
        expected = sha256(item.source)
        if not item.target.exists():
            action, actual = "create", None
        elif not item.target.is_file():
            action, actual = "refuse-drift", "not-a-file"
        else:
            actual = sha256(item.target)
            if actual == expected:
                action = "keep"
            elif previous.get(item.receipt_key) == actual:
                action = "replace-receipted-version"
            else:
                action = "refuse-drift"
        plan.append({
            "path": str(item.target),
            "key": item.receipt_key,
            "action": action,
            "expected_sha256": expected,
            "actual_sha256": actual,
        })
    return plan


def receipt_value(root: Path, files: list[TargetFile], receipt_path: Path) -> dict:
    return {
        "schema_version": "council.install/1",
        "product": "council",
        "component": receipt_component(receipt_path),
        "version": plugin_version(root),
        "files": {item.receipt_key: sha256(item.source) for item in files},
    }


def write_json_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.stage-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json_text(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def unknown_skill_files(files: list[TargetFile], receipt_path: Path) -> list[str]:
    target_root = receipt_path.parent
    if not target_root.is_dir():
        return []
    expected = {item.target.resolve() for item in files}
    allowed = expected | {receipt_path.resolve()}
    return sorted(
        str(path)
        for path in target_root.rglob("*")
        if path.is_file() and path.resolve() not in allowed
    )


def apply_skill_unit(root: Path, files: list[TargetFile], receipt_path: Path) -> str | None:
    target_root = receipt_path.parent
    target_parent = target_root.parent
    target_parent.mkdir(parents=True, exist_ok=True)
    plan = materialization_plan(files, receipt_path)
    extras = unknown_skill_files(files, receipt_path)
    if extras or any(item["action"] == "refuse-drift" for item in plan):
        raise CouncilError(f"skill target has unknown drift: {extras or plan}")
    if all(item["action"] == "keep" for item in plan):
        write_json_atomic(receipt_path, receipt_value(root, files, receipt_path))
        return None

    stage = Path(tempfile.mkdtemp(prefix=".engineering-council.council-stage-", dir=target_parent))
    backup: Path | None = None
    try:
        for item in files:
            relative = Path(item.receipt_key)
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item.source, destination)
        write_json_atomic(
            stage / receipt_path.name, receipt_value(root, files, receipt_path)
        )
        if target_root.exists():
            backup = target_parent / f".engineering-council.council-backup-{time.time_ns()}"
            os.replace(target_root, backup)
        try:
            os.replace(stage, target_root)
        except Exception:
            if backup is not None and backup.exists() and not target_root.exists():
                os.replace(backup, target_root)
            raise
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return str(backup) if backup else None


def apply_advisor_unit(root: Path, files: list[TargetFile], receipt_path: Path) -> str | None:
    agent_root = receipt_path.parent
    agent_root.mkdir(parents=True, exist_ok=True)
    plan = materialization_plan(files, receipt_path)
    if any(item["action"] == "refuse-drift" for item in plan):
        raise CouncilError(f"advisor target has unknown drift: {plan}")
    if all(item["action"] == "keep" for item in plan):
        write_json_atomic(receipt_path, receipt_value(root, files, receipt_path))
        return None

    stage = Path(tempfile.mkdtemp(prefix=".council-agents-stage-", dir=agent_root))
    backup: Path | None = None
    moved_existing: list[tuple[Path, Path]] = []
    installed: list[Path] = []
    previous_receipt: Path | None = None
    try:
        for item in files:
            shutil.copy2(item.source, stage / item.target.name)
        existing = [item for item in files if item.target.exists()]
        if existing or receipt_path.exists():
            backup = agent_root / f".council-engineering-council-backup-{time.time_ns()}"
            backup.mkdir()
            for item in existing:
                destination = backup / item.target.name
                os.replace(item.target, destination)
                moved_existing.append((destination, item.target))
            if receipt_path.exists():
                previous_receipt = backup / receipt_path.name
                os.replace(receipt_path, previous_receipt)
        for item in files:
            os.replace(stage / item.target.name, item.target)
            installed.append(item.target)
        write_json_atomic(receipt_path, receipt_value(root, files, receipt_path))
    except Exception:
        receipt_path.unlink(missing_ok=True)
        for path in installed:
            path.unlink(missing_ok=True)
        for source, destination in reversed(moved_existing):
            if source.exists():
                os.replace(source, destination)
        if previous_receipt is not None and previous_receipt.exists():
            os.replace(previous_receipt, receipt_path)
        if backup is not None and backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return str(backup) if backup else None


def materialize(
    root: Path,
    skill_roots: list[Path],
    agent_roots: list[Path],
    *,
    apply: bool,
) -> dict:
    root = root.resolve()
    verification = verify(root)
    units: list[tuple[str, list[TargetFile], Path]] = []
    for skill_root in skill_roots:
        resolved = skill_root.resolve()
        files = skill_targets(root, resolved)
        units.append(("skill", files, resolved / "engineering-council/.council-install.json"))
    for agent_root in agent_roots:
        resolved = agent_root.resolve()
        files = advisor_targets(root, resolved)
        units.append(("advisors", files, resolved / ".council-engineering-council-install.json"))
    if not units:
        raise CouncilError("materialize requires at least one --skill-root or --agent-root")

    canonical_roots = ((root / "skills").resolve(), (root / "advisors").resolve())
    unit_roots = [receipt_path.parent.resolve() for _, _, receipt_path in units]
    for unit_root in unit_roots:
        if any(paths_overlap(unit_root, source_root) for source_root in canonical_roots):
            raise CouncilError(
                "materialization target must not overlap canonical skills or advisors"
            )
        if path_within(root, unit_root):
            raise CouncilError(
                "materialization target must not contain the canonical repository"
            )
        if path_within(unit_root, root) and not any(
            path_within(unit_root, (root / allowed).resolve())
            for allowed in MATERIALIZATION_REPOSITORY_ROOTS
        ):
            raise CouncilError(
                "repository-local materialization target must be under "
                ".agents/, .codex/agents/, or .council-local/"
            )
    for index, left in enumerate(unit_roots):
        for right in unit_roots[index + 1:]:
            if paths_overlap(left, right):
                raise CouncilError(
                    "materialization units must not overlap or contain one another"
                )

    plans: list[dict] = []
    for kind, files, receipt_path in units:
        plan = materialization_plan(files, receipt_path)
        extras = unknown_skill_files(files, receipt_path) if kind == "skill" else []
        plans.append({
            "kind": kind,
            "receipt": str(receipt_path),
            "files": plan,
            "unknown_extra_files": extras,
        })
    if any(
        unit["unknown_extra_files"]
        or any(item["action"] == "refuse-drift" for item in unit["files"])
        for unit in plans
    ):
        raise CouncilError("materialization refused because a target has unknown drift")

    backups: list[str] = []
    if apply:
        for kind, files, receipt_path in units:
            backup = (
                apply_skill_unit(root, files, receipt_path)
                if kind == "skill"
                else apply_advisor_unit(root, files, receipt_path)
            )
            if backup:
                backups.append(backup)
    return {
        "status": "applied" if apply else "dry-run",
        "version": verification["version"],
        "units": plans,
        "backups": backups,
        "cross_target_atomic": False,
    }


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("--repo-root", type=Path, default=ROOT,
                         help="Council repository root (primarily for isolated tests).")
    subparsers = command.add_subparsers(dest="command", required=True)

    subparsers.add_parser("verify", help="Validate canonical source and lock without writing.")

    lock = subparsers.add_parser("lock", help="Regenerate the canonical component lock.")
    lock.add_argument("--write", action="store_true", help="Required acknowledgement for the write.")

    index = subparsers.add_parser(
        "index", help="Regenerate the representative-library index."
    )
    index.add_argument("--write", action="store_true", help="Required acknowledgement for the write.")

    build = subparsers.add_parser("build", help="Build an allowlisted plugin artifact.")
    build.add_argument("--output", type=Path, required=True)

    status = subparsers.add_parser("status", help="Compare canonical source with installed targets.")
    status.add_argument("--skill-root", type=Path, action="append", default=[])
    status.add_argument("--agent-root", type=Path, action="append", default=[])

    install = subparsers.add_parser("materialize", help="Plan or apply one-way target materialization.")
    install.add_argument("--skill-root", type=Path, action="append", default=[])
    install.add_argument("--agent-root", type=Path, action="append", default=[])
    install.add_argument("--apply", action="store_true", help="Apply the otherwise read-only plan.")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.repo_root.resolve()
    try:
        if args.command == "verify":
            emit(verify(root))
            return 0
        if args.command == "lock":
            if not args.write:
                raise CouncilError("lock is read-only unless --write is supplied")
            verify(root, check_lock=False)
            value = build_lock(root)
            write_json_atomic(root / LOCK_PATH, value)
            emit({"status": "written", "path": str(root / LOCK_PATH), **value})
            return 0
        if args.command == "index":
            if not args.write:
                raise CouncilError("index is read-only unless --write is supplied")
            value, _ = validate_representative_library(root, check_index=False)
            write_json_atomic(root / REPRESENTATIVE_INDEX_PATH, value)
            emit({
                "status": "written",
                "path": str(root / REPRESENTATIVE_INDEX_PATH),
                **value,
            })
            return 0
        if args.command == "build":
            emit(build_artifact(root, args.output))
            return 0
        if args.command == "status":
            report = status_report(root, args.skill_root, args.agent_root)
            emit(report)
            return 0 if report["status"] == "match" else 2
        if args.command == "materialize":
            emit(materialize(root, args.skill_root, args.agent_root, apply=args.apply))
            return 0
        raise CouncilError(f"unsupported command: {args.command}")
    except CouncilError as exc:
        emit({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
