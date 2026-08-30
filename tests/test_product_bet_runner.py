from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/run_product_bet_cell.py"
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("run_product_bet_cell", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class ProductBetRunnerTest(unittest.TestCase):
    def test_parse_usage_does_not_double_count_reasoning(self) -> None:
        events = [
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": json.dumps({"ok": True})},
            },
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 50,
                    "output_tokens": 20,
                    "reasoning_output_tokens": 7,
                },
            },
        ]
        _, usage, _ = RUNNER.parse_codex_jsonl(
            "\n".join(json.dumps(event) for event in events)
        )
        self.assertEqual(usage["input_tokens"] + usage["output_tokens"], 120)
        self.assertNotEqual(
            usage["input_tokens"]
            + usage["output_tokens"]
            + usage["reasoning_output_tokens"],
            120,
        )

    def test_failure_categories_are_safe_and_specific(self) -> None:
        self.assertEqual(RUNNER.failure_category("exceeds the frozen budget"), "budget")
        self.assertEqual(RUNNER.failure_category("failed with exit code 1"), "execution")
        self.assertEqual(RUNNER.failure_category("final JSON is invalid"), "structured-output")
        self.assertEqual(RUNNER.failure_category("unknown evidence reference"), "semantic-validation")


if __name__ == "__main__":
    unittest.main()
