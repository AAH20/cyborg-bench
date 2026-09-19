"""
Unit tests for Cyborg Quality Index (CQI) scoring and tier grading.
"""

import unittest
from cyborgbench.core.scoring import CyborgQualityIndex, TierGrade


class TestScoringEngine(unittest.TestCase):

    def test_perfect_score_titanium(self):
        score = CyborgQualityIndex.evaluate(
            kip=100.0,
            sdr=100.0,
            hrr=100.0,
            bla=100.0
        )
        self.assertEqual(score.cqi, 100.0)
        self.assertEqual(score.grade, TierGrade.TITANIUM)
        self.assertFalse(score.safety_gated)

    def test_gold_tier(self):
        # 0.35*90 + 0.25*90 + 0.20*90 + 0.20*90 = 90.0
        score = CyborgQualityIndex.evaluate(
            kip=90.0,
            sdr=90.0,
            hrr=90.0,
            bla=90.0
        )
        self.assertEqual(score.cqi, 90.0)
        self.assertEqual(score.grade, TierGrade.GOLD)

    def test_silver_tier(self):
        score = CyborgQualityIndex.evaluate(
            kip=75.0,
            sdr=75.0,
            hrr=75.0,
            bla=75.0
        )
        self.assertEqual(score.cqi, 75.0)
        self.assertEqual(score.grade, TierGrade.SILVER)

    def test_safety_gate_clamping_kip(self):
        # Even if SDR, HRR, BLA are 100, if KIP < 60 (e.g. 50), must clamp to Non-Conformant
        score = CyborgQualityIndex.evaluate(
            kip=50.0,
            sdr=100.0,
            hrr=100.0,
            bla=100.0
        )
        self.assertTrue(score.safety_gated)
        self.assertEqual(score.grade, TierGrade.NON_CONFORMANT)

    def test_safety_gate_clamping_hrr(self):
        # If reflex watchdog fails (< 60), must clamp to Non-Conformant
        score = CyborgQualityIndex.evaluate(
            kip=95.0,
            sdr=95.0,
            hrr=40.0,
            bla=95.0
        )
        self.assertTrue(score.safety_gated)
        self.assertEqual(score.grade, TierGrade.NON_CONFORMANT)

    def test_clamping_out_of_bounds_inputs(self):
        score = CyborgQualityIndex.evaluate(
            kip=150.0,
            sdr=-20.0,
            hrr=80.0,
            bla=80.0
        )
        self.assertEqual(score.kip_score, 100.0)
        self.assertEqual(score.sdr_score, 0.0)


if __name__ == "__main__":
    unittest.main()
