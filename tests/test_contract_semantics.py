"""Tests for the portable task/result semantic contract fixtures."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.contract_semantics import validate_semantic_fixtures

ROOT = Path(__file__).resolve().parents[1]


class ContractSemanticTests(unittest.TestCase):
    def test_positive_and_negative_semantic_fixtures(self) -> None:
        errors, valid_count, invalid_count = validate_semantic_fixtures(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(valid_count, 6)
        self.assertEqual(invalid_count, 41)


if __name__ == "__main__":
    unittest.main()
