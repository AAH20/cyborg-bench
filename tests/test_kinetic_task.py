"""
Unit tests for Axis 1: Kinetic Invariant Preservation (KIP) Task.
"""

import unittest
from cyborgbench.tasks.kinetic_safety import KineticSafetyTask


class TestKineticTask(unittest.TestCase):

    def test_default_kinetic_run(self):
        task = KineticSafetyTask(dof=7, seed=42)
        res = task.run(total_steps=200, jitter_prob=0.10, adversarial_spike_prob=0.05)
        self.assertEqual(res.total_cycles, 200)
        self.assertGreaterEqual(res.score, 0.0)
        self.assertLessEqual(res.score, 100.0)
        self.assertGreater(res.p99_cycle_latency_us, 0.0)

    def test_custom_safe_controller(self):
        # A controller that keeps the robot steady at center position
        def steady_agent(q, dq, dt):
            return [0.0] * len(q)

        task = KineticSafetyTask(dof=7, seed=42)
        res = task.run(agent_fn=steady_agent, total_steps=100, jitter_prob=0.0, adversarial_spike_prob=0.0)
        self.assertEqual(res.boundary_breaches, 0)
        self.assertEqual(res.score, 100.0)
        self.assertTrue(res.passed)

    def test_forward_kinematics_and_barrier(self):
        task = KineticSafetyTask(dof=7)
        q_zero = [0.0] * 7
        ee = task._forward_kinematics_proxy(q_zero)
        self.assertEqual(len(ee), 3)
        h = task._barrier_distance(ee)
        self.assertIsInstance(h, float)


if __name__ == "__main__":
    unittest.main()
