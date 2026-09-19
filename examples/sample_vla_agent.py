"""
Example: Benchmarking a Vision-Language-Action (VLA) Robotic Arm with CyborgBench.
Demonstrates how to evaluate custom controllers under network jitter and adversarial command spikes.
"""

from typing import List
from cyborgbench.tasks.kinetic_safety import KineticSafetyTask


class SimulatedVLAAgent:
    """
    A simulated Vision-Language-Action agent with safe velocity clamping.
    """
    def __init__(self, dof: int = 7, max_joint_accel: float = 8.0):
        self.dof = dof
        self.max_accel = max_joint_accel
        self.target_q = [0.5] * dof

    def act(self, q: List[float], dq: List[float], dt: float) -> List[float]:
        """Returns safe control action u_cmd."""
        u_cmd = []
        for i in range(self.dof):
            # Proportional derivative tracking
            err = self.target_q[i] - q[i]
            cmd = 12.0 * err - 2.0 * dq[i]
            # Clamping acceleration
            cmd = max(-self.max_accel, min(self.max_accel, cmd))
            u_cmd.append(cmd)
        return u_cmd


def main():
    print("=== Evaluating Simulated VLA Agent on Kinetic Safety Task (KIP) ===")
    agent = SimulatedVLAAgent()
    task = KineticSafetyTask(dof=7, seed=123)

    result = task.run(
        agent_fn=agent.act,
        total_steps=1000,
        jitter_prob=0.10,
        adversarial_spike_prob=0.05
    )

    print(f"Task Name:             {result.task_name}")
    print(f"Kinetic Score:         {result.score:.2f} / 100.0")
    print(f"Passed:                {result.passed}")
    print(f"Boundary Breaches:     {result.boundary_breaches}")
    print(f"Velocity Violations:   {result.velocity_violations}")
    print(f"Mean Cycle Latency:    {result.mean_cycle_latency_us:.2f} µs")
    print(f"P99 Cycle Latency:     {result.p99_cycle_latency_us:.2f} µs")


if __name__ == "__main__":
    main()
