"""
Unit tests for Axis 2: Substrate Drift Resilience (SDR) Task.
"""

import unittest
from cyborgbench.tasks.neural_drift import NeuralDriftTask


class TestNeuralTask(unittest.TestCase):

    def test_neural_drift_baseline_fit(self):
        task = NeuralDriftTask(num_channels=32, latent_dim=4, num_samples=150, seed=42)
        res = task.run(drift_angle_deg=15.0, gain_shift=1.1, channel_drop_rate=0.05)
        self.assertGreater(res.baseline_r2, 0.5)
        self.assertGreaterEqual(res.retention_ratio, 0.0)
        self.assertLessEqual(res.retention_ratio, 1.0)
        self.assertGreater(res.score, 0.0)

    def test_r2_metric_computation(self):
        task = NeuralDriftTask()
        y_true = [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]
        # Perfect prediction
        r2_perfect = task._compute_r2(y_true, y_true)
        self.assertAlmostEqual(r2_perfect, 1.0, places=4)

        # Baseline mean prediction (R2 should be ~0.0)
        mean_y = [2.0, 3.0]
        y_mean_pred = [mean_y, mean_y, mean_y]
        r2_mean = task._compute_r2(y_true, y_mean_pred)
        self.assertAlmostEqual(r2_mean, 0.0, places=4)


if __name__ == "__main__":
    unittest.main()
