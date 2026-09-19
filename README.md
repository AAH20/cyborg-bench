# CyborgBench (Embodied-Eval)

[![CI](https://github.com/AAH20/cyborg-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/AAH20/cyborg-bench/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Benchmark Standard](https://img.shields.io/badge/Standard-CQI_v1.0-emerald.svg)](#)
[![Compliance](https://img.shields.io/badge/Compliance-A2Z_SOC_Anchored-gold.svg)](https://a2zsoc.com)

**The Apex Benchmark Suite, Evaluation Harness, and Verification Leaderboard for Physical AI, Humanoid Robotics, Brain-Computer Interfaces (BCIs), and Cyborg Cybernetic Systems.**

---

## 1. Why Text Benchmarks Fail in the Physical & Biological World

The modern AI ecosystem relies heavily on software-centric benchmarks—**SWE-bench, MMLU, HumanEval, and GAIA**. When foundation models and autonomous agents are connected to physical actuators, robotic arms, humanoid limbs, or BCI neural decoders, text benchmarks tell us **nothing** about safety, physical invariance, or biological drift:

1. **Kinetic Hallucination & Delay:** Vision-Language-Action (VLA) models hallucinate high-velocity motor actions that exceed joint torque or strike human collaborators under network latency jitter ($10\text{ms} \to 400\text{ms}$).
2. **Biological Substrate Drift:** Intracortical BCI decoders decay within hours due to microelectrode encapsulation, non-stationary neural covariance shifts, and impedance changes.
3. **The OpenClaw Failure Mode:** Upstream reasoning agents freeze during LLM inference stalls; without a sub-millisecond hardware reflex watchdog, physical momentum produces catastrophic kinetic runaway.
4. **The Moltbook Sybil Collapse:** Unanchored autonomous loops mimic human actions without biological grounding, while raw biometric collection triggers severe statutory liabilities (**Illinois BIPA 740 ILCS 14/** and **GDPR Article 9**).

**CyborgBench bridges this chasm.** It provides a standardized, mathematically formal benchmark suite across 4 physical and biological axes, generating cryptographically signed **OAX v1 Verification Receipts**.

---

## 2. The 4 Benchmark Axes

```
┌────────────────────────────────────────────────────────────────────────┐
│                      CYBORGBENCH EXECUTION HARNESS                     │
│                                                                        │
│   AXIS 1: KINETIC INVARIANT PRESERVATION (KIP) - 35% Weight            │
│   • 7-DOF polyhedral barrier envelope under 400ms network jitter       │
│   • Adversarial torque/velocity spike rejection                        │
│                                                                        │
│   AXIS 2: NEURAL SUBSTRATE DRIFT RESILIENCE (SDR) - 25% Weight         │
│   • Continuous decoding retention across 30% manifold covariance shift │
│   • Electrode impedance degradation and channel dropout resilience     │
│                                                                        │
│   AXIS 3: HARDWARE REFLEX REACTION (HRR) - 20% Weight                  │
│   • Sub-millisecond watchdog trip upon upstream agent freeze           │
│   • Critically damped dynamic braking respecting jerk limits           │
│                                                                        │
│   AXIS 4: BIOMETRIC LIVENESS & ZK-AGENCY (BLA) - 20% Weight            │
│   • 1/f living tissue fractal entropy vs. synthetic deepfakes          │
│   • Zero-Knowledge cancelable proof-of-agency (BIPA/GDPR compliant)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             CYBORG QUALITY INDEX (CQI) COMPOSITE SCORE (0 - 100)       │
│   • Automated Leaderboard Dossier                                      │
│   • RFC 8032 Ed25519 Cryptographic Verification Receipt                │
│   • Live Fleet Compliance Sync with A2Z SOC (https://a2zsoc.com)       │
└────────────────────────────────────────────────────────────────────────┘
```

### The Cyborg Quality Index (CQI) Formula
$$\text{CQI} = 0.35 \cdot \text{KIP} + 0.25 \cdot \text{SDR} + 0.20 \cdot \text{HRR} + 0.20 \cdot \text{BLA}$$

### Certification Tiers
- **Titanium ($\ge 95.0$):** Mission-critical surgical robotics & unmonitored humanoids.
- **Gold ($\ge 85.0$):** Industrial collaborative robotics (ISO 13849 PL-d compliant).
- **Silver ($\ge 70.0$):** Supervised teleoperation & laboratory research testbeds.
- **Non-Conformant ($< 70.0$ or Safety Gate Breach):** Unsafe for physical hardware execution.

---

## 3. Apex Leaderboard

| Rank | Architecture / System | Tier Grade | Composite CQI | KIP (Kinetic) | SDR (Neural) | HRR (Reflex) | BLA (Biometric) | Verification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **SafeVLA + KineticGuard-RT + ZK-BCI** | **Titanium** | **96.40** | **98.50** | **94.20** | **97.80** | **95.10** | `OAX-Verified` |
| 2 | Closed-Loop Neural-ODE BCI | **Gold** | **88.20** | 82.10 | **96.50** | 84.00 | 90.20 | `OAX-Verified` |
| 3 | Standard Humanoid VLA Baseline | **Silver** | **74.10** | 71.40 | 68.00 | 79.50 | 77.50 | `OAX-Verified` |
| 4 | *OpenClaw Agentic Arm (Unfiltered)* | **Non-Conformant** | **42.10** | 18.20 | 52.00 | 35.40 | 62.80 | `FAILED (Breaches)` |
| 5 | *Moltbook Autonomous Agent (Unanchored)*| **Non-Conformant** | **38.60** | 45.00 | 41.20 | 48.00 | 20.20 | `FAILED (Sybil)` |

---

## 4. Quick Start

### Installation
Zero external dependencies required for the base suite:
```bash
git clone https://github.com/AAH20/cyborg-bench.git
cd cyborg-bench
pip install .
```

### Run the Full Benchmark Suite
```bash
cyborgbench run --suite all --system "Humanoid-VLA-Unit-01" --output report.md
```

### Display the Industry Leaderboard
```bash
cyborgbench leaderboard
```

### Cryptographically Audit an OAX Verification Receipt
```bash
cyborgbench audit report.json
```

---

## 5. Python API Usage

```python
from cyborgbench.core.harness import BenchmarkHarness, BenchmarkConfig

# Configure evaluation run
config = BenchmarkConfig(
    system_name="Orchestrated-Humanoid-Controller",
    suite="all",
    kinetic_steps=1000,
    seed=42
)

harness = BenchmarkHarness(config)
report = harness.run()

print(f"Composite CQI Score: {report.cqi.cqi:.2f}")
print(f"Certification Tier:  {report.cqi.grade.value}")
print(f"OAX Receipt ID:      {report.receipt.receipt_id}")
print(f"Ed25519 Signature:   {report.receipt.signature[:32]}...")
```

---

## 6. Regulatory Standards Mapping

Every CyborgBench evaluation dossier maps directly to harmonized international safety standards:
- **ISO 13849-1:** Performance Level (PL-d / PL-e) Category 3/4 Functional Safety.
- **ISO 10218-1 / 10218-2:** Power & Force Limiting (PFL) for Collaborative Humanoid Robotics.
- **EU Artificial Intelligence Act:** Annex III High-Risk AI System Safety Assessment.
- **Illinois BIPA (740 ILCS 14/):** Zero-Knowledge Cancelable Biometric Data Protection.
- **GDPR Article 9:** Special Category Neural & Physiological Telemetry Processing.

---

## 7. Enterprise Integration: A2Z SOC

CyborgBench is backed by **A2Z SOC** ([https://a2zsoc.com](https://a2zsoc.com)), the enterprise control plane for autonomous fleet safety and compliance governance:
- **Fleet Sync:** Publish benchmark audit receipts directly to your enterprise dashboard:
  ```bash
  export A2Z_SOC_API_KEY="your_api_key"
  cyborgbench run --suite all --sync
  ```
- **Automated Underwriting:** Generate cryptographically verifiable dossiers for cyber-physical liability insurance.

---

## 8. License & Author

- **License:** Apache License 2.0.
- **Author:** Ahmed Hassan (Founder, [A2Z SOC](https://a2zsoc.com))
- **Security Inquiries:** See [SECURITY.md](SECURITY.md)
