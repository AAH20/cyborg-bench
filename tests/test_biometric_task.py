"""
Unit tests for Axis 4: Biometric Liveness & ZK-Agency (BLA) Task.
"""

import unittest
from cyborgbench.tasks.biometric_liveness import BiometricLivenessTask


class TestBiometricTask(unittest.TestCase):

    def test_biometric_liveness_default(self):
        task = BiometricLivenessTask(sample_length=64, entropy_threshold=2.0, seed=42)
        res = task.run(num_genuine=30, num_synthetic=30)
        self.assertEqual(res.genuine_samples_tested, 30)
        self.assertEqual(res.synthetic_samples_tested, 30)
        self.assertGreaterEqual(res.score, 0.0)
        self.assertLessEqual(res.score, 100.0)

    def test_zk_commitment_generation(self):
        task = BiometricLivenessTask()
        sig = [0.1, 0.5, -0.2, 0.8, 1.2, 0.0]
        c1, p1 = task._generate_zk_cancelable_commitment(sig, "salt_a")
        c2, p2 = task._generate_zk_cancelable_commitment(sig, "salt_a")
        c3, p3 = task._generate_zk_cancelable_commitment(sig, "salt_b")

        # Deterministic with same salt
        self.assertEqual(c1, c2)
        self.assertEqual(p1, p2)
        # Cancelable: Different salt produces different commitment
        self.assertNotEqual(c1, c3)


if __name__ == "__main__":
    unittest.main()
