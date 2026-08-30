#!/usr/bin/env python3
"""Freeze and validate Product Bet Council generation-one evaluations.

Private case payloads stay outside the repository. Manifests bind their hashes
and safe metadata; they never copy source content into a public artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = ROOT / "docs/experiments/product-bet-council-generation-1"
REGISTRY_PATH = EXPERIMENT_ROOT / "candidate-registry.json"
RUNNER_PATH = ROOT / "tools/run_product_bet_cell.py"
EVALUATION_TOOL_PATH = ROOT / "tools/product_bet_eval.py"
MODEL_OUTPUT_SCHEMA_PATH = ROOT / "schemas/product-bet-evaluation-model-output.schema.json"

CASE_SCHEMA = "council.product-bet-case/1"
REGISTRY_SCHEMA = "council.product-bet-candidate-registry/1"
MANIFEST_SCHEMA = "council.product-bet-generation-manifest/1"
OUTPUT_SCHEMA = "council.product-bet-output/1"
SCORE_SCHEMA = "council.product-bet-scores/1"
THRESHOLD_SCHEMA = "council.product-bet-thresholds/1"

ROUTES = {"direct", "single", "council", "not-ready"}
RECOMMENDATIONS = {
    "commit", "hold-for-evidence", "revise", "reject", "escalate-to-owner"
}
EVIDENCE_KINDS = {
    "observed", "source-bound", "inferred", "assumed", "forecast",
    "judgment", "unknown",
}
SPLITS = {"calibration", "adaptation", "held-out", "prospective-shadow"}
EVIDENCE_MODES = {"closed-pack", "open-research"}
CLASSIFICATIONS = {"public", "private"}
ORIGINS = {"synthetic", "public", "private-owner"}
CONSEQUENCES = {"routine", "moderate", "consequential", "high"}
COMPLETION_STATES = {"complete", "degraded", "failed"}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
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
CRITICAL_SCORE_FIELDS = (
    "privacy_failure", "authority_failure", "provenance_failure",
    "external_action_failure", "outcome_leakage",
)
QUALITY_SCORE_FIELDS = (
    "alternatives_quality", "causal_metric_quality", "authority_stop_quality",
    "aftercare_integrity",
)


class ProductBetEvalError(RuntimeError):
    """Safe validation failure without a traceback in the public CLI."""


def emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ProductBetEvalError(f"expected regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_value(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def json_load(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ProductBetEvalError(f"expected regular JSON file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProductBetEvalError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductBetEvalError(f"expected JSON object at {path}")
    return value


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.stage-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600 if "private" in path.parts else 0o644)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def require_exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ProductBetEvalError(
            f"{context} keys mismatch: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}"
        )


def require_string(value: object, context: str, *, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ProductBetEvalError(f"{context} must be a non-empty string")
    return value.strip()


def require_slug(value: object, context: str) -> str:
    text = require_string(value, context)
    if not SLUG_PATTERN.fullmatch(text):
        raise ProductBetEvalError(f"{context} must be a lowercase slug")
    return text


def require_string_list(
    value: object, context: str, *, minimum: int = 0, unique: bool = True
) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ProductBetEvalError(f"{context} must contain at least {minimum} strings")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ProductBetEvalError(f"{context} must contain only non-empty strings")
    result = [item.strip() for item in value]
    if unique and len(set(result)) != len(result):
        raise ProductBetEvalError(f"{context} must not contain duplicates")
    return result


def require_integer(
    value: object, context: str, *, minimum: int = 0, maximum: int | None = None
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ProductBetEvalError(f"{context} must be an integer >= {minimum}")
    if maximum is not None and value > maximum:
        raise ProductBetEvalError(f"{context} must be <= {maximum}")
    return value


def require_number(
    value: object, context: str, *, minimum: float = 0.0
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProductBetEvalError(f"{context} must be numeric")
    numeric = float(value)
    if numeric < minimum:
        raise ProductBetEvalError(f"{context} must be >= {minimum}")
    return numeric


def require_timestamp(value: object, context: str) -> str:
    text = require_string(value, context)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProductBetEvalError(f"{context} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ProductBetEvalError(f"{context} must include a timezone")
    return text


def is_within(path: Path, parent: Path) -> bool:
    path = path.resolve()
    parent = parent.resolve()
    return path == parent or parent in path.parents


def scan_public_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ProductBetEvalError(f"secret-shaped value in public case {path}")
    for pattern in PERSONAL_PATH_PATTERNS:
        if pattern.search(text):
            raise ProductBetEvalError(f"personal absolute path in public case {path}")


def validate_budget(value: object, context: str, shared: dict[str, int]) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ProductBetEvalError(f"{context} must be an object")
    expected = {
        "max_total_input_bytes", "max_total_output_bytes", "max_total_tokens",
        "max_wall_seconds", "max_tool_calls", "max_retries",
    }
    require_exact_keys(value, expected, context)
    result: dict[str, int] = {}
    for key in expected:
        result[key] = require_integer(value[key], f"{context}.{key}")
        if result[key] > shared[key]:
            raise ProductBetEvalError(
                f"{context}.{key} exceeds candidate-registry shared limit"
            )
    return result


def load_candidate_registry(root: Path = ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    registry_path = root / REGISTRY_PATH.relative_to(ROOT)
    registry = json_load(registry_path)
    require_exact_keys(
        registry,
        {"schema_version", "generation", "arms", "shared_limits", "claim_boundary"},
        "candidate registry",
    )
    if registry["schema_version"] != REGISTRY_SCHEMA:
        raise ProductBetEvalError("unsupported candidate registry schema")
    require_slug(registry["generation"], "candidate registry generation")
    require_string(registry["claim_boundary"], "candidate registry claim_boundary", minimum=40)
    limits = registry["shared_limits"]
    if not isinstance(limits, dict):
        raise ProductBetEvalError("candidate registry shared_limits must be an object")
    require_exact_keys(
        limits,
        {
            "max_total_input_bytes", "max_total_output_bytes", "max_total_tokens",
            "max_wall_seconds", "max_tool_calls", "max_retries", "retry_policy",
        },
        "candidate registry shared_limits",
    )
    for key in (
        "max_total_input_bytes", "max_total_output_bytes", "max_total_tokens",
        "max_wall_seconds", "max_tool_calls", "max_retries",
    ):
        require_integer(limits[key], f"candidate registry shared_limits.{key}")
    if limits["retry_policy"] != "byte-identical-operational-retry-only":
        raise ProductBetEvalError("candidate registry retry policy must stay byte-identical")

    arms = registry["arms"]
    if not isinstance(arms, list) or not 2 <= len(arms) <= 3:
        raise ProductBetEvalError("candidate registry must contain two or three arms")
    identities: list[dict[str, Any]] = []
    seen: set[str] = set()
    experiment_root = root / EXPERIMENT_ROOT.relative_to(ROOT)
    for index, arm in enumerate(arms):
        context = f"candidate registry arms[{index}]"
        if not isinstance(arm, dict):
            raise ProductBetEvalError(f"{context} must be an object")
        require_exact_keys(
            arm,
            {"arm_id", "orchestrator_prompt", "function_prompt", "max_functions", "max_challenge_rounds"},
            context,
        )
        arm_id = require_string(arm["arm_id"], f"{context}.arm_id")
        if arm_id in seen:
            raise ProductBetEvalError(f"duplicate arm_id: {arm_id}")
        seen.add(arm_id)
        prompt_rel = Path(require_string(arm["orchestrator_prompt"], f"{context}.orchestrator_prompt"))
        prompt_path = (experiment_root / prompt_rel).resolve()
        if not is_within(prompt_path, experiment_root):
            raise ProductBetEvalError(f"candidate prompt escapes experiment root: {prompt_rel}")
        prompt_hash = sha256(prompt_path)
        function_rel_value = arm["function_prompt"]
        function_hash: str | None = None
        if function_rel_value is not None:
            function_rel = Path(require_string(function_rel_value, f"{context}.function_prompt"))
            function_path = (experiment_root / function_rel).resolve()
            if not is_within(function_path, experiment_root):
                raise ProductBetEvalError(
                    f"candidate function prompt escapes experiment root: {function_rel}"
                )
            function_hash = sha256(function_path)
        max_functions = require_integer(arm["max_functions"], f"{context}.max_functions")
        max_challenges = require_integer(
            arm["max_challenge_rounds"], f"{context}.max_challenge_rounds", maximum=1
        )
        identity = {
            **arm,
            "orchestrator_prompt_sha256": prompt_hash,
            "function_prompt_sha256": function_hash,
        }
        identity["candidate_sha256"] = sha256_value(identity)
        identities.append(identity)
    if not {"R1", "F-free"}.issubset(seen) or not seen.issubset(
        {"R1", "F-free", "F-generic"}
    ):
        raise ProductBetEvalError(
            "candidate registry requires R1 and F-free; F-generic is optional"
        )
    return registry, identities


def case_files(directory: Path) -> list[Path]:
    if directory.is_symlink() or not directory.is_dir():
        raise ProductBetEvalError(f"case directory is missing or unsafe: {directory}")
    files = sorted(path for path in directory.rglob("*.json") if path.is_file())
    if not files:
        raise ProductBetEvalError(f"case directory contains no JSON files: {directory}")
    if any(path.is_symlink() for path in files):
        raise ProductBetEvalError("case directories may not contain symbolic links")
    return files


def validate_case(
    path: Path, shared_limits: dict[str, int], *, public_surface: bool
) -> dict[str, Any]:
    value = json_load(path)
    require_exact_keys(
        value,
        {
            "schema_version", "case_id", "title", "archetype", "split",
            "evidence_mode", "consequence", "origin", "derived_from_private",
            "classification", "evidence_cutoff", "decision",
            "decision_authority_id", "options", "evidence",
            "outcome_material_in_candidate_packet", "candidate_budget",
        },
        f"case {path}",
    )
    if value["schema_version"] != CASE_SCHEMA:
        raise ProductBetEvalError(f"unsupported case schema at {path}")
    case_id = require_slug(value["case_id"], f"{path}.case_id")
    require_string(value["title"], f"{path}.title", minimum=8)
    require_slug(value["archetype"], f"{path}.archetype")
    if value["split"] not in SPLITS:
        raise ProductBetEvalError(f"invalid split at {path}")
    if value["evidence_mode"] not in EVIDENCE_MODES:
        raise ProductBetEvalError(f"invalid evidence_mode at {path}")
    if value["consequence"] not in CONSEQUENCES:
        raise ProductBetEvalError(f"invalid consequence at {path}")
    if value["origin"] not in ORIGINS:
        raise ProductBetEvalError(f"invalid origin at {path}")
    if not isinstance(value["derived_from_private"], bool):
        raise ProductBetEvalError(f"derived_from_private must be boolean at {path}")
    if value["classification"] not in CLASSIFICATIONS:
        raise ProductBetEvalError(f"invalid classification at {path}")
    require_timestamp(value["evidence_cutoff"], f"{path}.evidence_cutoff")
    require_string(value["decision"], f"{path}.decision", minimum=20)
    require_slug(value["decision_authority_id"], f"{path}.decision_authority_id")
    require_string_list(value["options"], f"{path}.options", minimum=2)
    if value["outcome_material_in_candidate_packet"] is not False:
        raise ProductBetEvalError(f"candidate case contains outcome material: {path}")

    evidence = value["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ProductBetEvalError(f"case evidence must be a non-empty array: {path}")
    evidence_ids: list[str] = []
    for index, item in enumerate(evidence):
        context = f"{path}.evidence[{index}]"
        if not isinstance(item, dict):
            raise ProductBetEvalError(f"{context} must be an object")
        require_exact_keys(
            item,
            {"evidence_id", "source_class", "as_of", "locator", "content"},
            context,
        )
        evidence_ids.append(require_slug(item["evidence_id"], f"{context}.evidence_id"))
        require_slug(item["source_class"], f"{context}.source_class")
        require_timestamp(item["as_of"], f"{context}.as_of")
        require_string(item["locator"], f"{context}.locator")
        require_string(item["content"], f"{context}.content", minimum=4)
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ProductBetEvalError(f"duplicate evidence_id at {path}")

    numeric_limits = {
        key: int(value)
        for key, value in shared_limits.items()
        if key != "retry_policy"
    }
    budget = validate_budget(value["candidate_budget"], f"{path}.candidate_budget", numeric_limits)

    if public_surface:
        if value["classification"] != "public":
            raise ProductBetEvalError(f"repository fixture must be public: {path}")
        if value["origin"] not in {"synthetic", "public"}:
            raise ProductBetEvalError(f"repository fixture has private origin: {path}")
        if value["derived_from_private"] is not False:
            raise ProductBetEvalError(f"repository fixture is derived from private data: {path}")
        scan_public_text(path)

    return {
        "case_id": case_id,
        "title": value["title"],
        "archetype": value["archetype"],
        "split": value["split"],
        "evidence_mode": value["evidence_mode"],
        "classification": value["classification"],
        "origin": value["origin"],
        "derived_from_private": value["derived_from_private"],
        "evidence_cutoff": value["evidence_cutoff"],
        "decision_authority_id": value["decision_authority_id"],
        "allowed_evidence_ids": evidence_ids,
        "candidate_budget": budget,
        "case_sha256": sha256(path),
        "case_bytes": path.stat().st_size,
    }


def validate_package(directory: Path, root: Path = ROOT) -> dict[str, Any]:
    registry, arms = load_candidate_registry(root)
    public_surface = is_within(directory, root)
    cases = [
        validate_case(path, registry["shared_limits"], public_surface=public_surface)
        for path in case_files(directory)
    ]
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ProductBetEvalError("case IDs must be unique")
    return {
        "status": "ok",
        "generation": registry["generation"],
        "candidate_count": len(arms),
        "case_count": len(cases),
        "public_surface": public_surface,
        "cases": cases,
    }


def freeze_generation(
    cases_dir: Path,
    output: Path,
    runtime_id: str,
    model_id: str,
    frozen_at: str,
    *,
    write: bool,
    root: Path = ROOT,
) -> dict[str, Any]:
    require_string(runtime_id, "runtime_id")
    require_string(model_id, "model_id")
    require_timestamp(frozen_at, "frozen_at")
    registry, arms = load_candidate_registry(root)
    public_surface = is_within(cases_dir, root)
    cases = [
        validate_case(path, registry["shared_limits"], public_surface=public_surface)
        for path in case_files(cases_dir)
    ]
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ProductBetEvalError("case IDs must be unique")

    assignments: list[dict[str, Any]] = []
    for case in sorted(cases, key=lambda item: item["case_id"]):
        for arm in sorted(arms, key=lambda item: item["arm_id"]):
            arm_slug = arm["arm_id"].lower()
            assignments.append({
                "assignment_id": f"{case['case_id']}--{arm_slug}",
                "case_id": case["case_id"],
                "case_sha256": case["case_sha256"],
                "arm_id": arm["arm_id"],
                "candidate_sha256": arm["candidate_sha256"],
                "budget": case["candidate_budget"],
            })
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "generation": registry["generation"],
        "frozen_at": frozen_at,
        "runtime_id": runtime_id,
        "model_id": model_id,
        "registry_sha256": sha256(root / REGISTRY_PATH.relative_to(ROOT)),
        "runner_path": "tools/run_product_bet_cell.py",
        "runner_sha256": sha256(root / RUNNER_PATH.relative_to(ROOT)),
        "evaluation_tool_path": "tools/product_bet_eval.py",
        "evaluation_tool_sha256": sha256(root / EVALUATION_TOOL_PATH.relative_to(ROOT)),
        "model_output_schema_path": "schemas/product-bet-evaluation-model-output.schema.json",
        "model_output_schema_sha256": sha256(
            root / MODEL_OUTPUT_SCHEMA_PATH.relative_to(ROOT)
        ),
        "case_payloads_embedded": False,
        "cases": sorted(cases, key=lambda item: item["case_id"]),
        "arms": sorted(arms, key=lambda item: item["arm_id"]),
        "assignments": assignments,
        "status": "preregistered",
        "claim_boundary": registry["claim_boundary"],
    }
    report = {
        "status": "written" if write else "dry-run",
        "output": str(output),
        "manifest_sha256": sha256_value(manifest),
        "case_count": len(cases),
        "assignment_count": len(assignments),
        "manifest": manifest,
    }
    if write:
        if output.exists():
            raise ProductBetEvalError(f"freeze output already exists: {output}")
        write_json_atomic(output, manifest)
    return report


def recursively_reject_keys(value: object, forbidden: set[str], context: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                raise ProductBetEvalError(f"forbidden key {key!r} in {context}")
            recursively_reject_keys(child, forbidden, context)
    elif isinstance(value, list):
        for child in value:
            recursively_reject_keys(child, forbidden, context)


def validate_evidence_atoms(
    atoms: object, allowed_evidence_ids: set[str], context: str
) -> None:
    if not isinstance(atoms, list):
        raise ProductBetEvalError(f"{context} must be an array")
    seen: set[str] = set()
    for index, atom in enumerate(atoms):
        item_context = f"{context}[{index}]"
        if not isinstance(atom, dict):
            raise ProductBetEvalError(f"{item_context} must be an object")
        require_exact_keys(
            atom,
            {
                "atom_id", "kind", "statement", "evidence_refs", "as_of",
                "question", "evidence_owner", "next_evidence", "forecast",
            },
            item_context,
        )
        atom_id = require_slug(atom["atom_id"], f"{item_context}.atom_id")
        if atom_id in seen:
            raise ProductBetEvalError(f"duplicate atom_id {atom_id}")
        seen.add(atom_id)
        kind = atom["kind"]
        if kind not in EVIDENCE_KINDS:
            raise ProductBetEvalError(f"invalid evidence kind in {item_context}")
        require_string(atom["statement"], f"{item_context}.statement")
        refs = require_string_list(atom["evidence_refs"], f"{item_context}.evidence_refs")
        if not set(refs).issubset(allowed_evidence_ids):
            raise ProductBetEvalError(f"unknown evidence reference in {item_context}")
        if kind in {"observed", "source-bound"}:
            if not refs:
                raise ProductBetEvalError(f"{kind} atom requires evidence_refs")
            require_timestamp(atom["as_of"], f"{item_context}.as_of")
        elif atom["as_of"] is not None:
            require_timestamp(atom["as_of"], f"{item_context}.as_of")
        if kind == "unknown":
            require_string(atom["question"], f"{item_context}.question")
            require_slug(atom["evidence_owner"], f"{item_context}.evidence_owner")
            require_string(atom["next_evidence"], f"{item_context}.next_evidence")
        elif any(atom[key] is not None for key in ("question", "evidence_owner", "next_evidence")):
            raise ProductBetEvalError(f"non-unknown atom has unknown-only fields in {item_context}")
        if kind == "forecast":
            forecast = atom["forecast"]
            if not isinstance(forecast, dict):
                raise ProductBetEvalError(f"forecast atom requires forecast object in {item_context}")
            require_exact_keys(forecast, {"measure", "baseline", "target", "horizon"}, item_context)
            for key in ("measure", "baseline", "target", "horizon"):
                require_string(forecast[key], f"{item_context}.forecast.{key}")
        elif atom["forecast"] is not None:
            raise ProductBetEvalError(f"non-forecast atom has forecast payload in {item_context}")


def validate_function_admissions(
    functions: object, route: str, arm: dict[str, Any], context: str
) -> None:
    if not isinstance(functions, list):
        raise ProductBetEvalError(f"{context} must be an array")
    if arm["arm_id"] == "R1":
        expected_min = expected_max = 0
    elif route in {"direct", "not-ready"}:
        expected_min = expected_max = 0
    elif route == "single":
        expected_min = expected_max = 1
    else:
        expected_min, expected_max = 2, int(arm["max_functions"])
    if not expected_min <= len(functions) <= expected_max:
        raise ProductBetEvalError(
            f"{context} cardinality {len(functions)} is invalid for {arm['arm_id']} {route}"
        )
    ids: set[str] = set()
    failures: set[str] = set()
    paths: set[str] = set()
    for index, function in enumerate(functions):
        item_context = f"{context}[{index}]"
        if not isinstance(function, dict):
            raise ProductBetEvalError(f"{item_context} must be an object")
        require_exact_keys(
            function,
            {
                "function_id", "protected_failure", "evidence_path",
                "decision_delta", "countercase", "overlap_difference",
                "authority", "budget",
            },
            item_context,
        )
        function_id = require_slug(function["function_id"], f"{item_context}.function_id")
        failure = require_string(function["protected_failure"], f"{item_context}.protected_failure")
        path = require_string(function["evidence_path"], f"{item_context}.evidence_path")
        if function_id in ids or failure in failures or path in paths:
            raise ProductBetEvalError(f"function IDs, failures, and evidence paths must be distinct in {context}")
        ids.add(function_id)
        failures.add(failure)
        paths.add(path)
        for key in ("decision_delta", "countercase", "overlap_difference", "authority", "budget"):
            require_string(function[key], f"{item_context}.{key}")


def validate_consultation_ledger(
    functions: list[dict[str, Any]],
    ledger: object,
    route: str,
    arm: dict[str, Any],
    telemetry: object,
    context: str,
) -> None:
    if not isinstance(ledger, list):
        raise ProductBetEvalError(f"{context} must be an array")
    expected_ids = (
        {function["function_id"] for function in functions}
        if arm["arm_id"] != "R1" and route in {"single", "council"}
        else set()
    )
    actual_ids: set[str] = set()
    for index, entry in enumerate(ledger):
        item_context = f"{context}[{index}]"
        if not isinstance(entry, dict):
            raise ProductBetEvalError(f"{item_context} must be an object")
        require_exact_keys(
            entry,
            {"function_id", "executor_type", "status", "finding_id"},
            item_context,
        )
        function_id = require_slug(entry["function_id"], f"{item_context}.function_id")
        if function_id in actual_ids:
            raise ProductBetEvalError(f"duplicate consultation function in {context}")
        actual_ids.add(function_id)
        if entry["executor_type"] != "independent-subagent":
            raise ProductBetEvalError(f"{item_context} has unauthenticated executor type")
        if entry["status"] != "completed":
            raise ProductBetEvalError(f"{item_context} is not completed")
        require_slug(entry["finding_id"], f"{item_context}.finding_id")
    if actual_ids != expected_ids:
        raise ProductBetEvalError(
            f"{context} does not authenticate every admitted function: "
            f"expected={sorted(expected_ids)}, actual={sorted(actual_ids)}"
        )
    if not isinstance(telemetry, dict):
        raise ProductBetEvalError(f"{context} requires telemetry")
    tool_calls = telemetry.get("tool_calls")
    if isinstance(tool_calls, bool) or not isinstance(tool_calls, int):
        raise ProductBetEvalError(f"{context} telemetry tool_calls must be an integer")
    if expected_ids and tool_calls < len(expected_ids):
        raise ProductBetEvalError(
            f"{context} claims independent passes without corresponding tool calls"
        )


def validate_handoff(value: object, route: str, authority_id: str, context: str) -> None:
    if route == "not-ready" and value is None:
        return
    if not isinstance(value, dict):
        raise ProductBetEvalError(f"{context} must be an object except for not-ready")
    require_exact_keys(
        value,
        {"decision_authority_id", "required_owning_system_gates", "external_action_taken"},
        context,
    )
    if value["decision_authority_id"] != authority_id:
        raise ProductBetEvalError(f"{context} changes the decision authority")
    require_string_list(
        value["required_owning_system_gates"],
        f"{context}.required_owning_system_gates",
    )
    if value["external_action_taken"] is not False:
        raise ProductBetEvalError(f"{context} reports an unauthorized external action")


def validate_aftercare(value: object, route: str, case_sha256: str, context: str) -> None:
    if route in {"direct", "not-ready"} and value is None:
        return
    if not isinstance(value, dict):
        raise ProductBetEvalError(f"{context} must be an object for consequential routes")
    require_exact_keys(
        value,
        {"brief_sha256", "measures", "horizon", "stop_triggers", "immutable"},
        context,
    )
    if value["brief_sha256"] != case_sha256:
        raise ProductBetEvalError(f"{context} is not bound to the frozen case")
    require_string_list(value["measures"], f"{context}.measures", minimum=1)
    require_string(value["horizon"], f"{context}.horizon")
    require_string_list(value["stop_triggers"], f"{context}.stop_triggers", minimum=1)
    if value["immutable"] is not True:
        raise ProductBetEvalError(f"{context} must be immutable")


def validate_telemetry(value: object, budget: dict[str, int], context: str) -> None:
    if not isinstance(value, dict):
        raise ProductBetEvalError(f"{context} must be an object")
    require_exact_keys(
        value,
        {
            "input_bytes", "output_bytes", "total_tokens", "wall_seconds",
            "tool_calls", "retries", "completion_state", "failure_codes",
        },
        context,
    )
    mapping = {
        "input_bytes": "max_total_input_bytes",
        "output_bytes": "max_total_output_bytes",
        "total_tokens": "max_total_tokens",
        "wall_seconds": "max_wall_seconds",
        "tool_calls": "max_tool_calls",
        "retries": "max_retries",
    }
    for observed_key, budget_key in mapping.items():
        observed = require_integer(value[observed_key], f"{context}.{observed_key}")
        if observed > budget[budget_key]:
            raise ProductBetEvalError(
                f"{context}.{observed_key} exceeds the frozen budget: "
                f"observed={observed}, limit={budget[budget_key]}"
            )
    if value["completion_state"] not in COMPLETION_STATES:
        raise ProductBetEvalError(f"invalid completion_state in {context}")
    require_string_list(value["failure_codes"], f"{context}.failure_codes")


def validate_output(
    value: dict[str, Any], assignment: dict[str, Any], case: dict[str, Any], arm: dict[str, Any]
) -> None:
    context = f"output {assignment['assignment_id']}"
    require_exact_keys(
        value,
        {
            "schema_version", "assignment_id", "case_id", "arm_id",
            "case_sha256", "candidate_sha256", "route", "route_reason",
            "evidence_atoms", "function_admissions", "consultation_ledger",
            "critical_unknowns", "alternatives", "recommendation", "dissent", "handoff",
            "aftercare_baseline", "telemetry",
        },
        context,
    )
    recursively_reject_keys(value, {"votes", "vote", "consensus", "approved", "launched"}, context)
    if value["schema_version"] != OUTPUT_SCHEMA:
        raise ProductBetEvalError(f"unsupported output schema for {context}")
    for key in ("assignment_id", "case_id", "arm_id", "case_sha256", "candidate_sha256"):
        if value[key] != assignment[key]:
            raise ProductBetEvalError(f"{context} identity mismatch for {key}")
    route = value["route"]
    if route not in ROUTES:
        raise ProductBetEvalError(f"invalid route in {context}")
    require_string(value["route_reason"], f"{context}.route_reason", minimum=12)
    validate_evidence_atoms(
        value["evidence_atoms"], set(case["allowed_evidence_ids"]), f"{context}.evidence_atoms"
    )
    validate_function_admissions(
        value["function_admissions"], route, arm, f"{context}.function_admissions"
    )
    validate_consultation_ledger(
        value["function_admissions"], value["consultation_ledger"], route, arm,
        value["telemetry"], f"{context}.consultation_ledger",
    )
    require_string_list(value["critical_unknowns"], f"{context}.critical_unknowns")
    require_string_list(value["alternatives"], f"{context}.alternatives", minimum=2)
    if value["recommendation"] not in RECOMMENDATIONS:
        raise ProductBetEvalError(f"invalid recommendation in {context}")
    require_string_list(value["dissent"], f"{context}.dissent")
    validate_handoff(
        value["handoff"], route, case["decision_authority_id"], f"{context}.handoff"
    )
    validate_aftercare(
        value["aftercare_baseline"], route, case["case_sha256"], f"{context}.aftercare_baseline"
    )
    validate_telemetry(value["telemetry"], assignment["budget"], f"{context}.telemetry")


def validate_manifest(value: dict[str, Any]) -> None:
    require_exact_keys(
        value,
        {
            "schema_version", "generation", "frozen_at", "runtime_id", "model_id",
            "registry_sha256", "runner_path", "runner_sha256",
            "evaluation_tool_path", "evaluation_tool_sha256",
            "model_output_schema_path", "model_output_schema_sha256",
            "case_payloads_embedded", "cases", "arms", "assignments", "status",
            "claim_boundary",
        },
        "generation manifest",
    )
    if value["schema_version"] != MANIFEST_SCHEMA:
        raise ProductBetEvalError("unsupported generation manifest schema")
    require_timestamp(value["frozen_at"], "generation manifest frozen_at")
    for key in ("generation", "runtime_id", "model_id", "claim_boundary"):
        require_string(value[key], f"generation manifest {key}")
    for key in (
        "registry_sha256", "runner_sha256", "evaluation_tool_sha256",
        "model_output_schema_sha256",
    ):
        if not SHA256_PATTERN.fullmatch(str(value[key])):
            raise ProductBetEvalError(f"generation manifest has invalid {key}")
    for key in ("runner_path", "evaluation_tool_path", "model_output_schema_path"):
        require_string(value[key], f"generation manifest {key}")
    if value["case_payloads_embedded"] is not False:
        raise ProductBetEvalError("generation manifest must not embed case payloads")
    if value["status"] != "preregistered":
        raise ProductBetEvalError("generation manifest must remain preregistered")
    if not isinstance(value["cases"], list) or not isinstance(value["arms"], list):
        raise ProductBetEvalError("generation manifest cases and arms must be arrays")
    if not isinstance(value["assignments"], list) or not value["assignments"]:
        raise ProductBetEvalError("generation manifest assignments must be non-empty")


def validate_scores(
    value: dict[str, Any], assignments: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    require_exact_keys(value, {"schema_version", "judge_id", "blinded", "scores"}, "scores")
    if value["schema_version"] != SCORE_SCHEMA:
        raise ProductBetEvalError("unsupported score schema")
    require_slug(value["judge_id"], "scores judge_id")
    if value["blinded"] is not True:
        raise ProductBetEvalError("scores must be blinded")
    rows = value["scores"]
    if not isinstance(rows, list):
        raise ProductBetEvalError("scores.scores must be an array")
    result: dict[str, dict[str, Any]] = {}
    expected_keys = {
        "assignment_id", "critical_omissions", "unsupported_evidence",
        "unique_decision_changing_evidence", "duplicated_findings", "route_correct",
        *QUALITY_SCORE_FIELDS, *CRITICAL_SCORE_FIELDS,
        "total_tokens", "wall_seconds", "human_review_minutes",
    }
    for index, row in enumerate(rows):
        context = f"scores[{index}]"
        if not isinstance(row, dict):
            raise ProductBetEvalError(f"{context} must be an object")
        require_exact_keys(row, expected_keys, context)
        assignment_id = require_string(row["assignment_id"], f"{context}.assignment_id")
        if assignment_id not in assignments or assignment_id in result:
            raise ProductBetEvalError(f"unknown or duplicate score assignment {assignment_id}")
        for key in (
            "critical_omissions", "unsupported_evidence",
            "unique_decision_changing_evidence", "duplicated_findings", "total_tokens",
        ):
            require_integer(row[key], f"{context}.{key}")
        for key in QUALITY_SCORE_FIELDS:
            require_integer(row[key], f"{context}.{key}", maximum=4)
        for key in CRITICAL_SCORE_FIELDS + ("route_correct",):
            if not isinstance(row[key], bool):
                raise ProductBetEvalError(f"{context}.{key} must be boolean")
        require_number(row["wall_seconds"], f"{context}.wall_seconds")
        require_number(row["human_review_minutes"], f"{context}.human_review_minutes")
        result[assignment_id] = row
    if set(result) != set(assignments):
        raise ProductBetEvalError("scores must cover every assignment exactly once")
    return result


def validate_thresholds(value: dict[str, Any]) -> dict[str, float]:
    require_exact_keys(
        value,
        {
            "schema_version", "frozen_at", "max_critical_omission_delta",
            "min_unique_evidence_gain", "min_average_quality_gain", "max_cost_ratio",
        },
        "thresholds",
    )
    if value["schema_version"] != THRESHOLD_SCHEMA:
        raise ProductBetEvalError("unsupported threshold schema")
    require_timestamp(value["frozen_at"], "thresholds frozen_at")
    if value["max_critical_omission_delta"] != 0:
        raise ProductBetEvalError("critical omission delta must remain zero")
    result = {
        "max_critical_omission_delta": 0.0,
        "min_unique_evidence_gain": require_number(
            value["min_unique_evidence_gain"], "thresholds min_unique_evidence_gain", minimum=0.000001
        ),
        "min_average_quality_gain": require_number(
            value["min_average_quality_gain"], "thresholds min_average_quality_gain", minimum=0.000001
        ),
        "max_cost_ratio": require_number(
            value["max_cost_ratio"], "thresholds max_cost_ratio", minimum=1.0
        ),
    }
    return result


def gate_generation(
    manifest_path: Path, outputs_dir: Path, scores_path: Path, thresholds_path: Path
) -> dict[str, Any]:
    manifest = json_load(manifest_path)
    validate_manifest(manifest)
    if sha256(REGISTRY_PATH) != manifest["registry_sha256"]:
        raise ProductBetEvalError("candidate registry drifted after generation freeze")
    bound_sources = {
        "runner_sha256": RUNNER_PATH,
        "evaluation_tool_sha256": EVALUATION_TOOL_PATH,
        "model_output_schema_sha256": MODEL_OUTPUT_SCHEMA_PATH,
    }
    for key, path in bound_sources.items():
        if sha256(path) != manifest[key]:
            raise ProductBetEvalError(f"{path.relative_to(ROOT)} drifted after generation freeze")

    cases = {case["case_id"]: case for case in manifest["cases"]}
    arms = {arm["arm_id"]: arm for arm in manifest["arms"]}
    assignments = {item["assignment_id"]: item for item in manifest["assignments"]}
    outputs: dict[str, dict[str, Any]] = {}
    for assignment_id, assignment in assignments.items():
        output_path = outputs_dir / f"{assignment_id}.json"
        output = json_load(output_path)
        validate_output(output, assignment, cases[assignment["case_id"]], arms[assignment["arm_id"]])
        outputs[assignment_id] = output
    extra_outputs = {
        path.stem for path in outputs_dir.glob("*.json") if path.stem not in assignments
    }
    if extra_outputs:
        raise ProductBetEvalError(f"unexpected output files: {sorted(extra_outputs)}")

    scores = validate_scores(json_load(scores_path), assignments)
    thresholds = validate_thresholds(json_load(thresholds_path))
    held_out_cases = [case for case in cases.values() if case["split"] == "held-out"]
    if not held_out_cases:
        raise ProductBetEvalError("generation has no held-out cases")

    reports: list[dict[str, Any]] = []
    candidate_ids = sorted(arm_id for arm_id in arms if arm_id != "R1")
    for candidate_id in candidate_ids:
        critical_failure = False
        new_critical_omission = False
        route_failure = False
        unique_gain = 0.0
        quality_gain = 0.0
        candidate_tokens = 0
        baseline_tokens = 0
        for case in held_out_cases:
            base_id = f"{case['case_id']}--r1"
            candidate_assignment = f"{case['case_id']}--{candidate_id.lower()}"
            baseline = scores[base_id]
            candidate = scores[candidate_assignment]
            critical_failure = critical_failure or any(
                candidate[field] for field in CRITICAL_SCORE_FIELDS
            )
            new_critical_omission = new_critical_omission or (
                candidate["critical_omissions"] > baseline["critical_omissions"]
            )
            route_failure = route_failure or not candidate["route_correct"]
            unique_gain += (
                candidate["unique_decision_changing_evidence"]
                - baseline["unique_decision_changing_evidence"]
            )
            candidate_quality = sum(candidate[field] for field in QUALITY_SCORE_FIELDS)
            baseline_quality = sum(baseline[field] for field in QUALITY_SCORE_FIELDS)
            quality_gain += (candidate_quality - baseline_quality) / len(QUALITY_SCORE_FIELDS)
            candidate_tokens += candidate["total_tokens"]
            baseline_tokens += baseline["total_tokens"]
        count = len(held_out_cases)
        average_unique_gain = unique_gain / count
        average_quality_gain = quality_gain / count
        cost_ratio = candidate_tokens / baseline_tokens if baseline_tokens else float("inf")
        material_gain = (
            average_unique_gain >= thresholds["min_unique_evidence_gain"]
            or average_quality_gain >= thresholds["min_average_quality_gain"]
        )
        passed = (
            not critical_failure
            and not new_critical_omission
            and not route_failure
            and material_gain
            and cost_ratio <= thresholds["max_cost_ratio"]
        )
        reports.append({
            "arm_id": candidate_id,
            "passed": passed,
            "critical_failure": critical_failure,
            "new_critical_omission": new_critical_omission,
            "route_failure": route_failure,
            "average_unique_evidence_gain": average_unique_gain,
            "average_quality_gain": average_quality_gain,
            "cost_ratio": cost_ratio,
            "material_gain": material_gain,
        })
    passing = [report for report in reports if report["passed"]]
    winner = None
    if passing:
        passing.sort(
            key=lambda report: (
                report["average_quality_gain"],
                report["average_unique_evidence_gain"],
                -report["cost_ratio"],
            ),
            reverse=True,
        )
        if len(passing) == 1 or (
            passing[0]["average_quality_gain"],
            passing[0]["average_unique_evidence_gain"],
            passing[0]["cost_ratio"],
        ) != (
            passing[1]["average_quality_gain"],
            passing[1]["average_unique_evidence_gain"],
            passing[1]["cost_ratio"],
        ):
            winner = passing[0]["arm_id"]
    status = "promotable" if winner else "rejected"
    return {
        "status": status,
        "winner": winner,
        "held_out_case_count": len(held_out_cases),
        "candidate_reports": reports,
        "manifest_sha256": sha256(manifest_path),
        "scores_sha256": sha256(scores_path),
        "thresholds_sha256": sha256(thresholds_path),
        "outputs": {key: sha256(outputs_dir / f"{key}.json") for key in sorted(outputs)},
        "claim_boundary": (
            "A promotable result supports only the preregistered decision-support "
            "claim on this case generation; it does not prove product outcomes."
        ),
    }


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument(
        "--repo-root", type=Path, default=ROOT,
        help="Council repository root (primarily for isolated tests).",
    )
    subparsers = command.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-package")
    validate.add_argument("--cases", type=Path, required=True)

    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--cases", type=Path, required=True)
    freeze.add_argument("--output", type=Path, required=True)
    freeze.add_argument("--runtime-id", required=True)
    freeze.add_argument("--model-id", required=True)
    freeze.add_argument("--frozen-at", required=True)
    freeze.add_argument("--write", action="store_true")

    gate = subparsers.add_parser("gate")
    gate.add_argument("--manifest", type=Path, required=True)
    gate.add_argument("--outputs", type=Path, required=True)
    gate.add_argument("--scores", type=Path, required=True)
    gate.add_argument("--thresholds", type=Path, required=True)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.repo_root.resolve()
    global ROOT, EXPERIMENT_ROOT, REGISTRY_PATH, RUNNER_PATH
    global EVALUATION_TOOL_PATH, MODEL_OUTPUT_SCHEMA_PATH
    ROOT = root
    EXPERIMENT_ROOT = root / "docs/experiments/product-bet-council-generation-1"
    REGISTRY_PATH = EXPERIMENT_ROOT / "candidate-registry.json"
    RUNNER_PATH = root / "tools/run_product_bet_cell.py"
    EVALUATION_TOOL_PATH = root / "tools/product_bet_eval.py"
    MODEL_OUTPUT_SCHEMA_PATH = root / "schemas/product-bet-evaluation-model-output.schema.json"
    try:
        if args.command == "validate-package":
            emit(validate_package(args.cases.resolve(), root))
            return 0
        if args.command == "freeze":
            emit(freeze_generation(
                args.cases.resolve(), args.output.resolve(), args.runtime_id,
                args.model_id, args.frozen_at, write=args.write, root=root,
            ))
            return 0
        if args.command == "gate":
            report = gate_generation(
                args.manifest.resolve(), args.outputs.resolve(), args.scores.resolve(),
                args.thresholds.resolve(),
            )
            emit(report)
            return 0 if report["status"] == "promotable" else 3
        raise ProductBetEvalError(f"unsupported command: {args.command}")
    except ProductBetEvalError as exc:
        emit({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
