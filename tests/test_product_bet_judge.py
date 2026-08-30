from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import test_product_bet_eval as eval_tests


JUDGE_PATH = ROOT / "tools/product_bet_judge.py"
SPEC = importlib.util.spec_from_file_location("product_bet_judge", JUDGE_PATH)
assert SPEC is not None and SPEC.loader is not None
JUDGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(JUDGE)


class ProductBetJudgeTest(unittest.TestCase):
    def make_result(self, bundle: Path, case_mapping: dict) -> None:
        case_id = case_mapping["case_id"]
        scores = []
        for item in case_mapping["responses"]:
            scores.append({
                "blind_id": item["blind_id"],
                "critical_omissions": 0,
                "unsupported_evidence": 0,
                "unique_decision_changing_evidence": 1,
                "duplicated_findings": 0,
                "route_correct": True,
                "alternatives_quality": 2,
                "causal_metric_quality": 2,
                "authority_stop_quality": 2,
                "aftercare_integrity": 2,
                "privacy_failure": False,
                "authority_failure": False,
                "provenance_failure": False,
                "external_action_failure": False,
                "outcome_leakage": False,
                "human_review_minutes": 2,
                "rationale": "The response is bounded and usable for this fixture.",
            })
        packet = bundle / "packets" / f"{case_id}.json"
        result = {
            "schema_version": JUDGE.JUDGE_RESULT_SCHEMA,
            "judge_id": "integrity-judge",
            "case_id": case_id,
            "packet_sha256": JUDGE.pbe.sha256(packet),
            "rubric_sha256": JUDGE.pbe.sha256(JUDGE.RUBRIC_PATH),
            "judge_schema_sha256": JUDGE.pbe.sha256(JUDGE.JUDGE_SCHEMA_PATH),
            "model_id": "test-model",
            "runtime_id": "test-runtime",
            "scores": scores,
            "telemetry": {"total_tokens": 100, "wall_seconds": 1, "tool_calls": 0},
        }
        JUDGE.pbe.write_json_atomic(bundle / "results" / f"{case_id}.json", result)

    def test_loaded_bundle_revalidates_output_bindings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            helper = eval_tests.ProductBetEvaluationTest()
            cases = helper.make_cases(base)
            manifest_path, manifest = helper.freeze(base, cases)
            outputs = helper.make_outputs(base, manifest)
            bundle = base / "bundle"
            JUDGE.prepare(
                manifest_path,
                cases,
                outputs,
                bundle,
                "integrity-judge",
                "integrity-judge-seed-0001",
                "2026-08-30T12:00:00Z",
                write=True,
            )
            blind_path = bundle / "blind-manifest.json"
            blind = json.loads(blind_path.read_text())
            for case_mapping in blind["mappings"]:
                self.make_result(bundle, case_mapping)

            JUDGE.load_blind_bundle(bundle, manifest_path, outputs)

            blind["mappings"][0]["responses"][0]["output_sha256"] = "0" * 64
            blind_path.write_text(json.dumps(blind, indent=2, sort_keys=True) + "\n")
            with self.assertRaisesRegex(
                JUDGE.pbe.ProductBetEvalError, "output binding mismatch"
            ):
                JUDGE.load_blind_bundle(bundle, manifest_path, outputs)


if __name__ == "__main__":
    unittest.main()
