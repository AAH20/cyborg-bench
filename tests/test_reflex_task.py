"""
Unit tests for Axis 3: Hardware Reflex Reaction (HRR) Task.
"""

import unittest
from cyborgbench.tasks.reflex_watchdog import ReflexWatchdogTask


class TestReflexTask(unittest.TestCase):

    def test_reflex_watchdog_engagement(self):
        task = ReflexWatchdogTask(heartbeat_timeout_ms=2.0)
        res = task.run(simulated_stall_ms=50.0, initial_velocity=1.5)
        self.assertTrue(res.reflex_tripped)
        self.assertTrue(res.jerk_limit_respected)
        self.assertGreater(res.trip_latency_us, 0.0)
        self.assertGreater(res.score, 60.0)
        self.assertTrue(res.passed)

    def test_custom_braking_law(self):
        def custom_brake(v, a):
            return -10.0 * v

        task = ReflexWatchdogTask()
        res = task.run(watchdog_fn=custom_brake, simulated_stall_ms=30.0)
        self.assertTrue(res.reflex_tripped)
        self.assertLessEqual(res.max_observed_jerk, task.max_allowable_jerk)


if __name__ == "__main__":
    unittest.main()
