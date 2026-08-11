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
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = Path(".codex-plugin/plugin.json")
LOCK_PATH = Path("council.lock.json")
SKILL_PATH = Path("skills/engineering-council")
ADVISOR_PATH = Path("advisors/engineering-council")
PROVENANCE_PATH = Path("provenance/engineering-council/generation-1.json")

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


def repository_source_files(root: Path) -> list[Path]:
    """Return every versioned source candidate except the self-referential lock."""
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative == LOCK_PATH:
            continue
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if path.suffix == ".pyc" or path.name == ".DS_Store":
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


def verify(root: Path, *, check_lock: bool = True) -> dict:
    manifest = validate_plugin(root)
    validate_skill(root)
    advisor_hashes = validate_advisors(root)
    validate_provenance(root)
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
        "locked_files": len(current_lock["files"]),
    }


def artifact_files(root: Path) -> list[Path]:
    paths = [root / PLUGIN_PATH]
    paths.extend(regular_files(root / "skills"))
    return sorted(paths)


def build_artifact(root: Path, output: Path) -> dict:
    verification = verify(root)
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and any(output.iterdir()):
        raise CouncilError(f"build output must be absent or empty: {output}")
    if output.exists() and not output.is_dir():
        raise CouncilError(f"build output is not a directory: {output}")
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
