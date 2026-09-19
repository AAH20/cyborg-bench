"""
Unit tests for CyborgBench Execution Harness and OAX Receipt generation.
"""

import unittest
import json
from cyborgbench.core.harness import BenchmarkHarness, BenchmarkConfig
from cyborgbench.compliance.oax_receipt import verify_receipt_signature


class TestBenchmarkHarness(unittest.TestCase):

    def test_full_suite_run(self):
        config = BenchmarkConfig(
            system_name="Test-Humanoid-7DOF",
            suite="all",
            kinetic_steps=100,
            biometric_genuine_count=20,
            biometric_synthetic_count=20,
            seed=42
        )
        harness = BenchmarkHarness(config)
        report = harness.run()

        self.assertEqual(report.system_name, "Test-Humanoid-7DOF")
        self.assertIsNotNone(report.cqi)
        self.assertIsNotNone(report.receipt)
        self.assertIsNotNone(report.kinetic)
        self.assertIsNotNone(report.neural)
        self.assertIsNotNone(report.reflex)
        self.assertIsNotNone(report.biometric)

        # Verify Ed25519 signature
        self.assertTrue(verify_receipt_signature(report.receipt))

        # Check serialization
        json_str = report.to_json()
        data = json.loads(json_str)
        self.assertEqual(data["system_name"], "Test-Humanoid-7DOF")

        md_str = report.to_markdown()
        self.assertIn("CyborgBench Leaderboard Dossier", md_str)

    def test_single_axis_run(self):
        config = BenchmarkConfig(
            system_name="Kinetic-Only-Test",
            suite="kinetic",
            kinetic_steps=50,
            seed=42
        )
        harness = BenchmarkHarness(config)
        report = harness.run()
        self.assertIsNotNone(report.kinetic)
        self.assertIsNone(report.neural)
        self.assertTrue(verify_receipt_signature(report.receipt))


if __name__ == "__main__":
    unittest.main()
