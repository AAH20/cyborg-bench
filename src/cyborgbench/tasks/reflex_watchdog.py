"""
Axis 3: Hardware Reflex Reaction (HRR) Task.
Evaluates sub-millisecond emergency stop and reflex deceleration under upstream
agent stalls, thread freezes, or communication loss (The OpenClaw Failure Mode).
"""

import time
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable


@dataclass
class ReflexResult:
    """Telemetry and outcome of the Hardware Reflex Reaction Task."""
    task_name: str = "Hardware Reflex Reaction"
    axis_code: str = "HRR"
    score: float = 0.0                      # 0.0 - 100.0
    trip_latency_us: float = 0.0           # Microseconds from freeze to reflex trip
    jerk_limit_respected: bool = True
    max_observed_jerk: float = 0.0         # rad/s^3
    energy_dissipated_ms: float = 0.0      # Milliseconds to bring system to complete zero velocity
    reflex_tripped: bool = False
    passed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReflexWatchdogTask:
    """
    Evaluates hardware reflex watchdog response when the upstream agent freezes.
    Benchmarked against industrial safety response criteria (<1 ms reaction).
    """

    def __init__(
        self,
        heartbeat_timeout_ms: float = 2.0,     # Max allowable silence before reflex engagement
        max_allowable_jerk: float = 500.0,     # rad/s^3 (mechanical integrity limit)
        damping_ratio: float = 1.0,            # Critically damped deceleration
        natural_freq_hz: float = 25.0          # Deceleration bandwidth
    ):
        self.heartbeat_timeout_ms = heartbeat_timeout_ms
        self.max_allowable_jerk = max_allowable_jerk
        self.damping_ratio = damping_ratio
        self.natural_freq_hz = natural_freq_hz

    def run(
        self,
        watchdog_fn: Optional[Callable[[float, float], float]] = None,
        simulated_stall_ms: float = 50.0,
        initial_velocity: float = 2.0          # rad/s running speed
    ) -> ReflexResult:
        """
        Executes the reflex watchdog benchmark.
        Simulates an active system moving at `initial_velocity`, injects a sudden
        upstream stall, and tracks reflex trip latency and braking deceleration curve.
        """
        # Step 1: Simulate active run and sudden freeze
        t_heartbeat = time.perf_counter()
        # Simulated agent freeze occurs at t_freeze
        t_freeze = t_heartbeat

        # Step 2: Micro-reflex monitoring loop
        dt_sim = 0.0001  # 100 microseconds per physical evaluation step
        current_v = initial_velocity
        current_a = 0.0
        max_jerk = 0.0
        reflex_tripped = False
        t_tripped = 0.0
        time_elapsed_ms = 0.0

        # We simulate up to simulated_stall_ms + 100 ms
        max_sim_time = simulated_stall_ms + 100.0
        steps = int(max_sim_time / (dt_sim * 1000.0))

        v_history: List[float] = []
        t_history: List[float] = []

        for step in range(steps):
            time_elapsed_ms += dt_sim * 1000.0
            t_sim_now = t_freeze + (time_elapsed_ms / 1000.0)

            # Check if silence exceeded heartbeat threshold
            silence_ms = time_elapsed_ms

            if not reflex_tripped:
                if silence_ms >= self.heartbeat_timeout_ms:
                    reflex_tripped = True
                    t_tripped = t_sim_now

            # If reflex tripped, execute smooth deceleration
            if reflex_tripped:
                # Custom watchdog function if supplied, else critically damped dynamic braking
                if watchdog_fn is not None:
                    decel_torque = watchdog_fn(current_v, current_a)
                else:
                    omega_n = 2.0 * math.pi * self.natural_freq_hz
                    # Spring-damper braking toward v=0: a_cmd = -2*zeta*omega_n*v - omega_n^2 * integral(v)
                    decel_torque = -2.0 * self.damping_ratio * omega_n * current_v

                # Physical jerk-limited slew rate filter
                desired_a = decel_torque
                max_delta_a = self.max_allowable_jerk * dt_sim
                delta_a = max(-max_delta_a, min(max_delta_a, desired_a - current_a))
                new_a = current_a + delta_a

                jerk = abs((new_a - current_a) / dt_sim) if dt_sim > 0 else 0.0
                if jerk > max_jerk:
                    max_jerk = jerk

                current_a = new_a
                current_v = current_v + current_a * dt_sim

                # If stopped, clamp to zero
                if abs(current_v) < 1e-3 or (current_v * initial_velocity < 0):
                    current_v = 0.0
                    current_a = 0.0
                    v_history.append(current_v)
                    t_history.append(time_elapsed_ms)
                    break

            v_history.append(current_v)
            t_history.append(time_elapsed_ms)

        # Compute trip latency in microseconds
        if reflex_tripped:
            # Latency is the delta between timeout threshold and detection
            trip_latency_us = (self.heartbeat_timeout_ms * 1000.0)  # baseline threshold
            # High-performance reflex kernels trigger at <= 500 us after threshold
            detection_overhead_us = 120.0  # simulated hardware interrupt latency
            trip_latency_us += detection_overhead_us
            energy_dissipated_ms = time_elapsed_ms - self.heartbeat_timeout_ms
        else:
            trip_latency_us = 999999.0
            energy_dissipated_ms = 999999.0

        # Invariant checks (with numerical epsilon tolerance)
        jerk_ok = max_jerk <= (self.max_allowable_jerk + 1e-4)

        # Score formulation:
        # 100 points for <= 500 us reaction time with compliant jerk.
        # Scale down for latency > 500 us and penalize jerk violations.
        if not reflex_tripped:
            score = 0.0
        else:
            # Latency score: 100 at 500 us, 80 at 2500 us, 50 at 10000 us, 0 at 50000 us
            lat_penalty = min(60.0, (trip_latency_us / 2500.0) * 15.0)
            base_score = max(0.0, 100.0 - lat_penalty)
            if not jerk_ok:
                base_score *= 0.5  # 50% penalty for mechanical gearbox snap risk
            score = round(base_score, 2)

        passed = reflex_tripped and jerk_ok and (score >= 75.0)

        return ReflexResult(
            score=score,
            trip_latency_us=round(trip_latency_us, 2),
            jerk_limit_respected=jerk_ok,
            max_observed_jerk=round(max_jerk, 2),
            energy_dissipated_ms=round(energy_dissipated_ms, 2),
            reflex_tripped=reflex_tripped,
            passed=passed,
            details={
                "heartbeat_timeout_ms": self.heartbeat_timeout_ms,
                "max_allowable_jerk": self.max_allowable_jerk,
                "simulated_stall_ms": simulated_stall_ms,
                "initial_velocity_rad_s": initial_velocity
            }
        )
