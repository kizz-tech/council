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
        self.assertEqual(report["version"], "0.1.0")
        self.assertEqual(report["locked_files"], 15)

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

    def test_generation_one_import_hashes(self) -> None:
        receipt = json.loads(
            (ROOT / "provenance/engineering-council/generation-1.json").read_text()
        )
        identity = receipt["import_identity"]
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
            previous_hash = digest(target)

            source = repo / "advisors/engineering-council/clean-boundary-architect.toml"
            source.write_text(source.read_text() + "\n# compatible test release\n")
            new_hash = digest(source)
            provenance_path = repo / "provenance/engineering-council/generation-1.json"
            provenance = json.loads(provenance_path.read_text())
            provenance["import_identity"]["advisors"]["clean_boundary_architect"] = new_hash
            provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
            self.run_repo_tool(repo, "lock", "--write")

            applied, _ = self.run_repo_tool(
                repo, "materialize", "--agent-root", str(agent_root), "--apply"
            )
            self.assertEqual(applied["status"], "applied")
            self.assertEqual(digest(target), new_hash)
            backups = list(agent_root.glob(".council-engineering-council-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(
                digest(backups[0] / "clean-boundary-architect.toml"), previous_hash
            )


if __name__ == "__main__":
    unittest.main()
