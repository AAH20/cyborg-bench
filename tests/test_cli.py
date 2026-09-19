"""
Unit and integration tests for CyborgBench CLI commands.
"""

import unittest
import tempfile
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(REPO_ROOT, "src")


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.env = os.environ.copy()
        existing_pythonpath = self.env.get("PYTHONPATH", "")
        self.env["PYTHONPATH"] = f"{SRC_PATH}:{existing_pythonpath}" if existing_pythonpath else SRC_PATH

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "cyborgbench.cli", "--help"],
            capture_output=True,
            text=True,
            env=self.env
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("The Apex Benchmark Suite", result.stdout)

    def test_cli_leaderboard(self):
        result = subprocess.run(
            [sys.executable, "-m", "cyborgbench.cli", "leaderboard"],
            capture_output=True,
            text=True,
            env=self.env
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("CyborgBench Apex Leaderboard", result.stdout)
        self.assertIn("Titanium", result.stdout)

    def test_cli_run_and_audit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_report = os.path.join(tmpdir, "report.json")
            # 1. Run benchmark
            run_cmd = subprocess.run(
                [
                    sys.executable, "-m", "cyborgbench.cli", "run",
                    "--suite", "all",
                    "--steps", "50",
                    "--output", json_report
                ],
                capture_output=True,
                text=True,
                env=self.env
            )
            self.assertEqual(run_cmd.returncode, 0, f"Run error: {run_cmd.stderr}")
            self.assertTrue(os.path.exists(json_report))

            # 2. Audit receipt
            audit_cmd = subprocess.run(
                [sys.executable, "-m", "cyborgbench.cli", "audit", json_report],
                capture_output=True,
                text=True,
                env=self.env
            )
            self.assertEqual(audit_cmd.returncode, 0, f"Audit error: {audit_cmd.stderr}")
            self.assertIn("VERIFICATION SUCCESS", audit_cmd.stdout)


if __name__ == "__main__":
    unittest.main()
