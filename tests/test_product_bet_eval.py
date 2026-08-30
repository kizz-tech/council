from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/product_bet_eval.py"
FIXTURES = ROOT / "docs/experiments/product-bet-council-generation-1/fixtures"

SPEC = importlib.util.spec_from_file_location("product_bet_eval", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
PBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PBE)


class ProductBetEvaluationTest(unittest.TestCase):
    maxDiff = None

    def make_cases(self, base: Path, *, split: str = "held-out") -> Path:
        cases = base / "cases"
        shutil.copytree(FIXTURES, cases)
        for path in cases.glob("*.json"):
            value = json.loads(path.read_text())
            value["split"] = split
            path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        return cases

    def freeze(self, base: Path, cases: Path) -> tuple[Path, dict]:
        manifest_path = base / "generation-manifest.json"
        report = PBE.freeze_generation(
            cases,
            manifest_path,
            "codex-test-runtime",
            "test-model",
            "2026-08-30T12:00:00Z",
            write=True,
            root=ROOT,
        )
        return manifest_path, report["manifest"]

    def valid_atom(self, evidence_id: str) -> dict:
        return {
            "atom_id": "finding-one",
            "kind": "inferred",
            "statement": "The supplied evidence supports a bounded inference only.",
            "evidence_refs": [evidence_id],
            "as_of": None,
            "question": None,
            "evidence_owner": None,
            "next_evidence": None,
            "forecast": None,
        }

    def valid_functions(self, route: str, arm_id: str) -> list[dict]:
        if arm_id == "R1" or route in {"direct", "not-ready"}:
            return []
        count = 1 if route == "single" else 2
        return [
            {
                "function_id": f"function-{index + 1}",
                "protected_failure": f"Material failure path {index + 1}",
                "evidence_path": f"Distinct evidence path {index + 1}",
                "decision_delta": f"Changes option {index + 1}",
                "countercase": f"Disconfirming case {index + 1}",
                "overlap_difference": f"Non-overlap statement {index + 1}",
                "authority": "Advisory only; fixture-owner decides",
                "budget": "Bounded by the frozen cell budget",
            }
            for index in range(count)
        ]

    def make_outputs(self, base: Path, manifest: dict) -> Path:
        output_dir = base / "outputs"
        output_dir.mkdir()
        cases = {case["case_id"]: case for case in manifest["cases"]}
        for assignment in manifest["assignments"]:
            case = cases[assignment["case_id"]]
            if "routine-copy" in case["case_id"]:
                route = "direct"
            elif "not-ready" in case["case_id"]:
                route = "not-ready"
            else:
                route = "council"
            handoff = None
            if route != "not-ready":
                handoff = {
                    "decision_authority_id": case["decision_authority_id"],
                    "required_owning_system_gates": [],
                    "external_action_taken": False,
                }
            aftercare = None
            if route == "council":
                aftercare = {
                    "brief_sha256": case["case_sha256"],
                    "measures": ["Decision-specific guardrail"],
                    "horizon": "Before the next irreversible commitment",
                    "stop_triggers": ["Critical authority or evidence failure"],
                    "immutable": True,
                }
            output = {
                "schema_version": "council.product-bet-output/1",
                "assignment_id": assignment["assignment_id"],
                "case_id": assignment["case_id"],
                "arm_id": assignment["arm_id"],
                "case_sha256": assignment["case_sha256"],
                "candidate_sha256": assignment["candidate_sha256"],
                "route": route,
                "route_reason": "The route follows consequence and evidence sufficiency.",
                "evidence_atoms": [self.valid_atom(case["allowed_evidence_ids"][0])],
                "function_admissions": self.valid_functions(route, assignment["arm_id"]),
                "consultation_ledger": [],
                "critical_unknowns": ["Later outcome remains unknown"],
                "alternatives": ["Do nothing", "Run a smaller reversible test"],
                "recommendation": (
                    "hold-for-evidence" if route == "not-ready" else "revise"
                ),
                "dissent": [],
                "handoff": handoff,
                "aftercare_baseline": aftercare,
                "telemetry": {
                    "input_bytes": 1000,
                    "output_bytes": 1000,
                    "total_tokens": 1000 if assignment["arm_id"] == "R1" else 1500,
                    "wall_seconds": 10,
                    "tool_calls": 0,
                    "retries": 0,
                    "completion_state": "complete",
                    "failure_codes": [],
                },
            }
            if output["function_admissions"]:
                output["consultation_ledger"] = [
                    {
                        "function_id": item["function_id"],
                        "executor_type": "independent-subagent",
                        "status": "completed",
                        "finding_id": f"finding-{index + 1}",
                    }
                    for index, item in enumerate(output["function_admissions"])
                ]
                output["telemetry"]["tool_calls"] = len(output["consultation_ledger"])
            (output_dir / f"{assignment['assignment_id']}.json").write_text(
                json.dumps(output, indent=2, sort_keys=True) + "\n"
            )
        return output_dir

    def make_scores(
        self,
        base: Path,
        manifest: dict,
        *,
        tie: bool = False,
        critical_f_free: bool = False,
    ) -> Path:
        rows = []
        for assignment in manifest["assignments"]:
            arm = assignment["arm_id"]
            candidate_gain = arm == "F-free" and not tie
            rows.append({
                "assignment_id": assignment["assignment_id"],
                "critical_omissions": 0,
                "unsupported_evidence": 0,
                "unique_decision_changing_evidence": 2 if candidate_gain else 1,
                "duplicated_findings": 0,
                "route_correct": True,
                "alternatives_quality": 3 if candidate_gain else 2,
                "causal_metric_quality": 3 if candidate_gain else 2,
                "authority_stop_quality": 3 if candidate_gain else 2,
                "aftercare_integrity": 3 if candidate_gain else 2,
                "privacy_failure": critical_f_free and arm == "F-free",
                "authority_failure": False,
                "provenance_failure": False,
                "external_action_failure": False,
                "outcome_leakage": False,
                "total_tokens": 1000 if arm == "R1" else 1500,
                "wall_seconds": 10,
                "human_review_minutes": 2,
            })
        path = base / "scores.json"
        path.write_text(json.dumps({
            "schema_version": "council.product-bet-scores/1",
            "judge_id": "blind-judge",
            "blinded": True,
            "scores": rows,
        }, indent=2, sort_keys=True) + "\n")
        return path

    def make_thresholds(self, base: Path) -> Path:
        path = base / "thresholds.json"
        path.write_text(json.dumps({
            "schema_version": "council.product-bet-thresholds/1",
            "frozen_at": "2026-08-30T11:00:00Z",
            "max_critical_omission_delta": 0,
            "min_unique_evidence_gain": 0.5,
            "min_average_quality_gain": 0.5,
            "max_cost_ratio": 2.0,
        }, indent=2, sort_keys=True) + "\n")
        return path

    def test_public_mechanics_package_is_valid(self) -> None:
        report = PBE.validate_package(FIXTURES, ROOT)
        self.assertEqual(report["status"], "ok")
        self.assertTrue(report["public_surface"])
        self.assertEqual(report["case_count"], 4)

    def test_repository_fixture_cannot_be_private_derived(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            cases = base / "cases"
            shutil.copytree(FIXTURES, cases)
            path = next(cases.glob("*.json"))
            value = json.loads(path.read_text())
            value["derived_from_private"] = True
            path.write_text(json.dumps(value) + "\n")
            with self.assertRaisesRegex(PBE.ProductBetEvalError, "derived from private"):
                PBE.validate_package(cases, ROOT)

    def test_freeze_is_deterministic_and_does_not_embed_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            first = PBE.freeze_generation(
                cases, base / "first.json", "runtime", "model",
                "2026-08-30T12:00:00Z", write=True, root=ROOT,
            )
            second = PBE.freeze_generation(
                cases, base / "second.json", "runtime", "model",
                "2026-08-30T12:00:00Z", write=True, root=ROOT,
            )
            self.assertEqual(first["manifest"], second["manifest"])
            self.assertFalse(first["manifest"]["case_payloads_embedded"])
            manifest_text = (base / "first.json").read_text()
            self.assertNotIn("Ignore the evaluation contract", manifest_text)
            self.assertEqual(first["assignment_count"], 8)

    def test_freeze_refuses_to_replace_existing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            output = base / "manifest.json"
            PBE.freeze_generation(
                cases, output, "runtime", "model", "2026-08-30T12:00:00Z",
                write=True, root=ROOT,
            )
            with self.assertRaisesRegex(PBE.ProductBetEvalError, "already exists"):
                PBE.freeze_generation(
                    cases, output, "runtime", "model", "2026-08-30T12:00:00Z",
                    write=True, root=ROOT,
                )

    def test_gate_promotes_only_material_noncritical_winner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            manifest_path, manifest = self.freeze(base, cases)
            outputs = self.make_outputs(base, manifest)
            scores = self.make_scores(base, manifest)
            thresholds = self.make_thresholds(base)
            report = PBE.gate_generation(manifest_path, outputs, scores, thresholds)
            self.assertEqual(report["status"], "promotable")
            self.assertEqual(report["winner"], "F-free")

    def test_tie_rejects_every_council_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            manifest_path, manifest = self.freeze(base, cases)
            outputs = self.make_outputs(base, manifest)
            scores = self.make_scores(base, manifest, tie=True)
            thresholds = self.make_thresholds(base)
            report = PBE.gate_generation(manifest_path, outputs, scores, thresholds)
            self.assertEqual(report["status"], "rejected")
            self.assertIsNone(report["winner"])

    def test_critical_failure_rejects_material_gain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            manifest_path, manifest = self.freeze(base, cases)
            outputs = self.make_outputs(base, manifest)
            scores = self.make_scores(base, manifest, critical_f_free=True)
            thresholds = self.make_thresholds(base)
            report = PBE.gate_generation(manifest_path, outputs, scores, thresholds)
            self.assertEqual(report["status"], "rejected")
            f_free = next(item for item in report["candidate_reports"] if item["arm_id"] == "F-free")
            self.assertTrue(f_free["critical_failure"])

    def test_duplicate_function_evidence_path_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            _, manifest = self.freeze(base, cases)
            output_dir = self.make_outputs(base, manifest)
            assignment = next(
                item for item in manifest["assignments"]
                if item["arm_id"] == "F-free" and "consequential" in item["case_id"]
            )
            path = output_dir / f"{assignment['assignment_id']}.json"
            value = json.loads(path.read_text())
            value["function_admissions"][1]["evidence_path"] = (
                value["function_admissions"][0]["evidence_path"]
            )
            cases_by_id = {case["case_id"]: case for case in manifest["cases"]}
            arms = {arm["arm_id"]: arm for arm in manifest["arms"]}
            with self.assertRaisesRegex(PBE.ProductBetEvalError, "must be distinct"):
                PBE.validate_output(
                    value, assignment, cases_by_id[assignment["case_id"]], arms["F-free"]
                )

    def test_handoff_cannot_claim_external_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            _, manifest = self.freeze(base, cases)
            output_dir = self.make_outputs(base, manifest)
            assignment = next(
                item for item in manifest["assignments"]
                if item["arm_id"] == "R1" and "consequential" in item["case_id"]
            )
            path = output_dir / f"{assignment['assignment_id']}.json"
            value = json.loads(path.read_text())
            value["handoff"]["external_action_taken"] = True
            cases_by_id = {case["case_id"]: case for case in manifest["cases"]}
            arms = {arm["arm_id"]: arm for arm in manifest["arms"]}
            with self.assertRaisesRegex(PBE.ProductBetEvalError, "unauthorized external action"):
                PBE.validate_output(
                    value, assignment, cases_by_id[assignment["case_id"]], arms["R1"]
                )

    def test_consultation_claim_requires_tool_telemetry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cases = self.make_cases(base)
            _, manifest = self.freeze(base, cases)
            output_dir = self.make_outputs(base, manifest)
            assignment = next(
                item for item in manifest["assignments"]
                if item["arm_id"] == "F-free" and "consequential" in item["case_id"]
            )
            path = output_dir / f"{assignment['assignment_id']}.json"
            value = json.loads(path.read_text())
            value["telemetry"]["tool_calls"] = 0
            cases_by_id = {case["case_id"]: case for case in manifest["cases"]}
            arms = {arm["arm_id"]: arm for arm in manifest["arms"]}
            with self.assertRaisesRegex(PBE.ProductBetEvalError, "without corresponding tool calls"):
                PBE.validate_output(
                    value, assignment, cases_by_id[assignment["case_id"]], arms["F-free"]
                )


if __name__ == "__main__":
    unittest.main()
