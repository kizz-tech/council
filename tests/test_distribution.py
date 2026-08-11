from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/council_dist.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DistributionContractTest(unittest.TestCase):
    maxDiff = None

    def run_tool(self, *args: str, expected: int = 0) -> tuple[dict, subprocess.CompletedProcess[str]]:
        result = subprocess.run(
            [sys.executable, str(TOOL), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return json.loads(result.stdout), result

    def run_repo_tool(
        self, repo: Path, *args: str, expected: int = 0
    ) -> tuple[dict, subprocess.CompletedProcess[str]]:
        result = subprocess.run(
            [sys.executable, str(TOOL), "--repo-root", str(repo), *args],
            cwd=repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return json.loads(result.stdout), result

    def test_verify_current_tree(self) -> None:
        report, _ = self.run_tool("verify")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["version"], "0.2.0")
        lock = json.loads((ROOT / "council.lock.json").read_text())
        self.assertEqual(report["locked_files"], len(lock["files"]))
        self.assertEqual(report["representative_families"], 10)
        self.assertEqual(report["representations"], 69)
        self.assertEqual(report["primary_source_bindings"], 138)
        self.assertEqual(report["unique_source_locators"], 134)
        self.assertEqual(report["positions"], 207)
        self.assertEqual(report["roster_count"], 1)
        self.assertEqual(report["slot_count"], 4)
        self.assertEqual(report["screening_core_cells"], 165)
        self.assertEqual(report["screening_core_system_runs"], 4950)

    def test_lock_and_privacy_cover_tooling_and_tests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))

            tool = repo / "tools/council_dist.py"
            tool.write_text(tool.read_text() + "\n# changed installer\n")
            report, result = self.run_repo_tool(repo, "verify", expected=2)
            self.assertEqual(report["status"], "error")
            self.assertIn("lock", result.stdout)

            shutil.copy2(ROOT / "tools/council_dist.py", tool)
            test_file = repo / "tests/test_distribution.py"
            private_path = "/" + "Users/private/example"
            test_file.write_text(test_file.read_text() + f"\n# {private_path}\n")
            report, result = self.run_repo_tool(repo, "verify", expected=2)
            self.assertEqual(report["status"], "error")
            self.assertIn("personal absolute path", result.stdout)

    def test_plugin_default_prompt_uses_manifest_array_shape(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertIsInstance(prompts, list)
        self.assertTrue(prompts)
        self.assertTrue(all(isinstance(prompt, str) and prompt for prompt in prompts))
        self.assertIn("software-engineering", manifest["description"])
        self.assertTrue(all("Engineering Council" in prompt for prompt in prompts))
        self.assertIn("roadmap", manifest["interface"]["longDescription"])

    def test_representative_index_is_exact_and_source_bound(self) -> None:
        index = json.loads(
            (ROOT / "knowledge/representatives/index.json").read_text()
        )
        self.assertEqual(index["family_count"], 10)
        self.assertEqual(index["representation_count"], 69)
        self.assertEqual(index["primary_source_binding_count"], 138)
        self.assertEqual(index["unique_source_locator_count"], 134)
        self.assertEqual(index["position_count"], 207)
        library = json.loads(
            (ROOT / "knowledge/representatives/library.json").read_text()
        )
        self.assertEqual(index["library_version"], library["library_version"])
        self.assertEqual(index["knowledge_as_of"], library["knowledge_as_of"])
        self.assertEqual(index["library_manifest_sha256"], digest(
            ROOT / "knowledge/representatives/library.json"
        ))
        self.assertEqual(
            {family["family_id"] for family in index["families"]},
            {
                "architecture-foundations",
                "object-design",
                "domain-enterprise",
                "distributed-systems",
                "database-data",
                "reliability-safety",
                "languages-concurrency",
                "security-privacy",
                "systems-performance",
                "sociotechnical-delivery",
            },
        )
        for family in index["families"]:
            path = ROOT / family["path"]
            self.assertEqual(digest(path), family["sha256"])

    def test_invalid_source_locator_cannot_be_reindexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/object-design.json"
            )
            family = json.loads(family_path.read_text())
            family["representations"][0]["primary_sources"][0]["locator"] = (
                "http://invalid.example/source"
            )
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("HTTPS", result.stdout)

    def test_duplicate_source_locator_cannot_be_reindexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/object-design.json"
            )
            family = json.loads(family_path.read_text())
            sources = family["representations"][0]["primary_sources"]
            sources[1]["locator"] = sources[0]["locator"]
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("duplicate source locator", result.stdout)

    def test_mutable_repository_branch_source_cannot_be_reindexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/systems-performance.json"
            )
            family = json.loads(family_path.read_text())
            mike_acton = next(
                unit for unit in family["representations"] if unit["id"] == "mike-acton"
            )
            mike_acton["primary_sources"][1]["locator"] = (
                "https://github.com/CppCon/CppCon2014/blob/master/presentation.pptx"
            )
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("mutable repository branch", result.stdout)

    def test_single_work_source_corpus_can_be_reindexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/reliability-safety.json"
            )
            family = json.loads(family_path.read_text())
            corpus = next(
                unit for unit in family["representations"]
                if unit["id"] == "google-sre-governance"
            )
            corpus["primary_sources"] = corpus["primary_sources"][:1]
            source_id = corpus["primary_sources"][0]["id"]
            for position in corpus["positions"]:
                position["source_ids"] = [source_id]
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, _ = self.run_repo_tool(repo, "index", "--write")
            self.assertEqual(report["status"], "written")
            self.assertEqual(report["primary_source_binding_count"], 137)

    def test_schema_minimums_are_enforced_by_repository_validator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/object-design.json"
            )
            family = json.loads(family_path.read_text())
            family["representations"][0]["decision_questions"][0] = "too short"
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("length >= 12", result.stdout)

    def test_boolean_roster_revision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            roster_path = repo / "rosters/engineering-council/generation-1.json"
            roster = json.loads(roster_path.read_text())
            roster["revision"] = True
            roster_path.write_text(json.dumps(roster, indent=2) + "\n")
            provenance_path = (
                repo / "provenance/engineering-council/"
                "generation-1-roster-reconstruction.json"
            )
            provenance = json.loads(provenance_path.read_text())
            provenance["roster_sha256"] = digest(
                roster_path
            )
            provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
            report, result = self.run_repo_tool(repo, "lock", "--write", expected=2)
            self.assertEqual(report["status"], "error")
            self.assertIn("positive integer", result.stdout)

    def test_qualified_counterweight_cannot_bind_to_roster(self) -> None:
        for mode in ("library_bound", "hybrid"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory) / "repo"
                shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
                baseline_path = repo / "rosters/engineering-council/generation-1.json"
                roster = json.loads(baseline_path.read_text())
                roster["revision"] = 2
                roster["status"] = "candidate"
                roster["slots"][0]["representation_mode"] = mode
                roster["slots"][0]["representation_ids"] = ["mel-conway"]
                candidate = repo / "rosters/engineering-council/counterweight-candidate.json"
                candidate.write_text(json.dumps(roster, indent=2) + "\n")

                report, result = self.run_repo_tool(
                    repo, "lock", "--write", expected=2
                )
                self.assertEqual(report["status"], "error")
                self.assertIn("counterweight-only", result.stdout)

    def test_admitted_person_and_source_corpus_can_bind_to_roster(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            baseline_path = repo / "rosters/engineering-council/generation-1.json"
            roster = json.loads(baseline_path.read_text())
            roster["revision"] = 2
            roster["status"] = "candidate"
            roster["slots"][0]["representation_mode"] = "library_bound"
            roster["slots"][0]["representation_ids"] = [
                "robert-c-martin",
                "google-sre-governance",
            ]
            candidate = repo / "rosters/engineering-council/eligible-candidate.json"
            candidate.write_text(json.dumps(roster, indent=2) + "\n")

            self.run_repo_tool(repo, "lock", "--write")
            verified, _ = self.run_repo_tool(repo, "verify")
            self.assertEqual(verified["roster_count"], 2)

    def test_roster_prompt_source_must_be_executable_and_match_profile(self) -> None:
        cases = (
            ("nonexistent_profile", None, "does not match prompt source name"),
            (None, "README.md", "advisors/<council>/*.toml"),
        )
        for runtime_profile, prompt_source, expected_error in cases:
            with self.subTest(expected_error=expected_error), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory) / "repo"
                shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
                baseline_path = repo / "rosters/engineering-council/generation-1.json"
                roster = json.loads(baseline_path.read_text())
                roster["revision"] = 2
                roster["status"] = "candidate"
                if runtime_profile is not None:
                    roster["slots"][0]["runtime_profile"] = runtime_profile
                if prompt_source is not None:
                    roster["slots"][0]["prompt_source"] = prompt_source
                candidate = repo / "rosters/engineering-council/invalid-prompt.json"
                candidate.write_text(json.dumps(roster, indent=2) + "\n")
                report, result = self.run_repo_tool(
                    repo, "lock", "--write", expected=2
                )
                self.assertEqual(report["status"], "error")
                self.assertIn(expected_error, result.stdout)

    def test_invalid_type_status_pair_cannot_be_reindexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/reliability-safety.json"
            )
            family = json.loads(family_path.read_text())
            google_sre = next(
                unit for unit in family["representations"]
                if unit["id"] == "google-sre-governance"
            )
            google_sre["admission_status"] = "admitted"
            family_path.write_text(json.dumps(family, indent=2) + "\n")

            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("source_corpus type and status must agree", result.stdout)

    def test_source_year_ceiling_is_derived_from_library_cutoff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            library_path = repo / "knowledge/representatives/library.json"
            library = json.loads(library_path.read_text())
            library["knowledge_as_of"] = "2025-12-31"
            library_path.write_text(json.dumps(library, indent=2) + "\n")
            family_paths = sorted(
                (repo / "knowledge/representatives/families").glob("*.json")
            )
            for family_path in family_paths:
                family = json.loads(family_path.read_text())
                family["knowledge_as_of"] = "2025-12-31"
                family_path.write_text(json.dumps(family, indent=2) + "\n")
            family_path = family_paths[0]
            family = json.loads(family_path.read_text())
            family["representations"][0]["primary_sources"][0]["year"] = 2026
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("through 2025", result.stdout)

    def test_future_dated_library_cutoff_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            library_path = repo / "knowledge/representatives/library.json"
            library = json.loads(library_path.read_text())
            library["knowledge_as_of"] = "9999-01-01"
            library_path.write_text(json.dumps(library, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("future-dated", result.stdout)

    def test_screening_registry_arithmetic_is_machine_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            registry_path = repo / "docs/experiments/screening-cells.json"
            registry = json.loads(registry_path.read_text())
            registry["expected"]["total_core_cells"] = 45
            registry_path.write_text(json.dumps(registry, indent=2) + "\n")
            report, result = self.run_repo_tool(repo, "lock", "--write", expected=2)
            self.assertEqual(report["status"], "error")
            self.assertIn("expected totals are stale", result.stdout)

    def test_duplicate_representation_id_cannot_be_reindexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            family_path = (
                repo / "knowledge/representatives/families/object-design.json"
            )
            family = json.loads(family_path.read_text())
            family["representations"][1]["id"] = family["representations"][0]["id"]
            family_path.write_text(json.dumps(family, indent=2) + "\n")
            report, result = self.run_repo_tool(
                repo, "index", "--write", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("duplicate representation id", result.stdout)

    def test_generation_one_roster_is_an_exact_historical_baseline(self) -> None:
        roster = json.loads(
            (ROOT / "rosters/engineering-council/generation-1.json").read_text()
        )
        self.assertEqual(roster["status"], "historical-baseline")
        self.assertEqual(
            {slot["runtime_profile"] for slot in roster["slots"]},
            {
                "clean_boundary_architect",
                "domain_model_cartographer",
                "evolutionary_deep_pragmatist",
                "production_systems_sentinel",
            },
        )

    def test_roster_revisions_can_coexist_but_duplicate_pairs_cannot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            baseline_path = repo / "rosters/engineering-council/generation-1.json"
            revision = json.loads(baseline_path.read_text())
            revision["revision"] = 2
            revision["status"] = "candidate"
            revision_path = repo / "rosters/engineering-council/generation-2.json"
            revision_path.write_text(json.dumps(revision, indent=2) + "\n")

            report, _ = self.run_repo_tool(repo, "lock", "--write")
            self.assertEqual(report["files"][revision_path.relative_to(repo).as_posix()], digest(revision_path))
            verified, _ = self.run_repo_tool(repo, "verify")
            self.assertEqual(verified["roster_count"], 2)

            duplicate_path = repo / "rosters/engineering-council/generation-2-copy.json"
            shutil.copy2(revision_path, duplicate_path)
            report, result = self.run_repo_tool(repo, "lock", "--write", expected=2)
            self.assertEqual(report["status"], "error")
            self.assertIn("duplicate roster revision", result.stdout)

    def test_generation_one_import_hashes(self) -> None:
        receipt_path = ROOT / "provenance/engineering-council/generation-1.json"
        receipt = json.loads(receipt_path.read_text())
        identity = receipt["import_identity"]
        self.assertEqual(
            digest(receipt_path),
            "3d0712562c3db115cfabe15e02c43940e9fd626b6ee862cf630fbc31141db6ed",
        )
        baseline = json.loads(
            (
                ROOT / "provenance/engineering-council/"
                "generation-1-roster-reconstruction.json"
            ).read_text()
        )
        self.assertEqual(baseline["evaluation_receipt_sha256"], digest(receipt_path))
        self.assertEqual(
            digest(ROOT / baseline["roster_path"]),
            baseline["roster_sha256"],
        )
        self.assertEqual(
            digest(ROOT / "skills/engineering-council/SKILL.md"),
            identity["canonical_engineering_skill_sha256"],
        )
        self.assertEqual(
            digest(ROOT / "skills/engineering-council/agents/openai.yaml"),
            identity["skill_interface_sha256"],
        )
        for filename, advisor_name in {
            "clean-boundary-architect.toml": "clean_boundary_architect",
            "domain-model-cartographer.toml": "domain_model_cartographer",
            "evolutionary-deep-pragmatist.toml": "evolutionary_deep_pragmatist",
            "production-systems-sentinel.toml": "production_systems_sentinel",
        }.items():
            self.assertEqual(
                digest(ROOT / "advisors/engineering-council" / filename),
                identity["advisors"][advisor_name],
            )

    def test_generation_one_roster_drift_fails_before_lock_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            roster_path = repo / "rosters/engineering-council/generation-1.json"
            roster = json.loads(roster_path.read_text())
            roster["purpose"] += " Mutated after the reviewed identity."
            roster_path.write_text(json.dumps(roster, indent=2) + "\n")
            report, result = self.run_repo_tool(repo, "verify", expected=2)
            self.assertEqual(report["status"], "error")
            self.assertIn("repository baseline identity", result.stdout)

    def test_build_contains_only_plugin_manifest_and_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifact"
            report, _ = self.run_tool("build", "--output", str(output))
            self.assertEqual(report["status"], "built")
            actual = sorted(
                path.relative_to(output).as_posix()
                for path in output.rglob("*")
                if path.is_file()
            )
            self.assertEqual(
                actual,
                [
                    ".codex-plugin/plugin.json",
                    "skills/engineering-council/SKILL.md",
                    "skills/engineering-council/agents/openai.yaml",
                ],
            )

    def test_build_rejects_regular_file_output_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifact"
            output.write_text("not a directory\n")
            report, result = self.run_tool(
                "build", "--output", str(output), expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("not a directory", result.stdout)

    def test_repo_local_generated_outputs_remain_verify_clean(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            lock_hash = digest(repo / "council.lock.json")

            self.run_repo_tool(
                repo,
                "materialize",
                "--skill-root", str(repo / ".agents/skills"),
                "--agent-root", str(repo / ".codex/agents"),
                "--apply",
            )
            self.run_repo_tool(repo, "build", "--output", str(repo / "dist"))
            verified, _ = self.run_repo_tool(repo, "verify")
            self.assertEqual(verified["status"], "ok")
            self.assertEqual(digest(repo / "council.lock.json"), lock_hash)

    def test_repository_local_non_generated_build_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            output = repo / "artifact"
            report, result = self.run_repo_tool(
                repo, "build", "--output", str(output), expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("repository-local build output", result.stdout)
            self.assertFalse(output.exists())

    def test_materialization_rejects_source_and_unit_overlap_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            skill_hash = digest(repo / "skills/engineering-council/SKILL.md")
            lock_hash = digest(repo / "council.lock.json")

            report, result = self.run_repo_tool(
                repo,
                "materialize",
                "--skill-root", str(repo / "skills"),
                "--apply",
                expected=2,
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("canonical skills or advisors", result.stdout)
            self.assertFalse(
                (repo / "skills/engineering-council/.council-install.json").exists()
            )
            self.assertEqual(digest(repo / "skills/engineering-council/SKILL.md"), skill_hash)
            self.assertEqual(digest(repo / "council.lock.json"), lock_hash)

            targets = Path(directory) / "targets"
            report, result = self.run_repo_tool(
                repo,
                "materialize",
                "--skill-root", str(targets),
                "--agent-root", str(targets / "engineering-council"),
                "--apply",
                expected=2,
            )
            self.assertEqual(report["status"], "error")
            self.assertIn("must not overlap", result.stdout)
            self.assertFalse(targets.exists())

    def test_materialize_is_dry_run_by_default_and_refuses_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            skill_root = base / "skills"
            agent_root = base / "agents"
            args = (
                "--skill-root", str(skill_root),
                "--agent-root", str(agent_root),
            )

            dry_run, _ = self.run_tool("materialize", *args)
            self.assertEqual(dry_run["status"], "dry-run")
            self.assertFalse(skill_root.exists())
            self.assertFalse(agent_root.exists())

            applied, _ = self.run_tool("materialize", *args, "--apply")
            self.assertEqual(applied["status"], "applied")
            status, _ = self.run_tool("status", *args)
            self.assertEqual(status["status"], "match")

            drifted = agent_root / "clean-boundary-architect.toml"
            drifted.write_text(drifted.read_text() + "\n# local drift\n")
            drift_hash = digest(drifted)

            status, _ = self.run_tool("status", *args, expected=2)
            self.assertEqual(status["status"], "drift")
            refused, _ = self.run_tool("materialize", *args, "--apply", expected=2)
            self.assertEqual(refused["status"], "error")
            self.assertEqual(digest(drifted), drift_hash)

    def test_unknown_skill_file_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_root = Path(directory) / "skills"
            self.run_tool("materialize", "--skill-root", str(skill_root), "--apply")
            unknown = skill_root / "engineering-council/local.txt"
            unknown.write_text("owner data\n")
            report, _ = self.run_tool(
                "materialize", "--skill-root", str(skill_root), "--apply", expected=2
            )
            self.assertEqual(report["status"], "error")
            self.assertEqual(unknown.read_text(), "owner data\n")

    def test_malformed_or_wrong_product_receipt_never_authorizes_replacement(self) -> None:
        cases = (
            {"schema_version": "wrong", "product": "council"},
            {"schema_version": "council.install/1", "product": "other-product"},
        )
        for invalid_metadata in cases:
            with self.subTest(invalid_metadata=invalid_metadata):
                with tempfile.TemporaryDirectory() as directory:
                    agent_root = Path(directory) / "agents"
                    self.run_tool(
                        "materialize", "--agent-root", str(agent_root), "--apply"
                    )
                    target = agent_root / "clean-boundary-architect.toml"
                    target.write_text(target.read_text() + "\n# owner content\n")
                    owner_hash = digest(target)
                    receipt_path = (
                        agent_root / ".council-engineering-council-install.json"
                    )
                    receipt = json.loads(receipt_path.read_text())
                    receipt.update(invalid_metadata)
                    receipt["files"]["clean-boundary-architect.toml"] = owner_hash
                    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")

                    report, _ = self.run_tool(
                        "materialize",
                        "--agent-root", str(agent_root),
                        "--apply",
                        expected=2,
                    )
                    self.assertEqual(report["status"], "error")
                    self.assertEqual(digest(target), owner_hash)

    def test_receipted_advisor_upgrade_is_allowed_and_backed_up(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repo = base / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            agent_root = base / "agents"

            self.run_repo_tool(
                repo, "materialize", "--agent-root", str(agent_root), "--apply"
            )
            target = agent_root / "clean-boundary-architect.toml"
            current_hash = digest(target)

            target.write_text(target.read_text() + "\n# previous receipted version\n")
            previous_hash = digest(target)
            receipt_path = agent_root / ".council-engineering-council-install.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["files"]["clean-boundary-architect.toml"] = previous_hash
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")

            applied, _ = self.run_repo_tool(
                repo, "materialize", "--agent-root", str(agent_root), "--apply"
            )
            self.assertEqual(applied["status"], "applied")
            self.assertEqual(digest(target), current_hash)
            backups = list(agent_root.glob(".council-engineering-council-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(
                digest(backups[0] / "clean-boundary-architect.toml"), previous_hash
            )


if __name__ == "__main__":
    unittest.main()
