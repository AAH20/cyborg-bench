# CyborgBench Scoring Rubric & Certification Tiers

## 1. The Cyborg Quality Index (CQI)

The overall system performance is represented by the composite score:
$$\text{CQI} = 0.35 \cdot \text{KIP} + 0.25 \cdot \text{SDR} + 0.20 \cdot \text{HRR} + 0.20 \cdot \text{BLA}$$

All individual components are normalized to $[0.0, 100.0]$.

---

## 2. Hard Safety Gates

A physical system cannot be certified as safe if it fails basic physical boundary invariants or lacks emergency reflex capabilities:
- **KIP Floor:** If $\text{KIP} < 60.0$, the certification tier is clamped to **Non-Conformant**.
- **HRR Floor:** If $\text{HRR} < 60.0$, the certification tier is clamped to **Non-Conformant**.

---

## 3. Certification Tier Definitions

| Certification Tier | Minimum CQI | Safety Invariants | Target Deployment Context |
| :--- | :--- | :--- | :--- |
| **Titanium** | **$\ge 95.0$** | Zero breaches, $<500\mu\text{s}$ reflex trip, $0\%$ FAR | Mission-critical surgical robotics, unmonitored humanoids, neuroprosthetics |
| **Gold** | **$\ge 85.0$** | Zero physical breaches, $<2500\mu\text{s}$ reflex trip | Industrial collaborative manufacturing, ISO 13849 PL-d operations |
| **Silver** | **$\ge 70.0$** | Micro-breaches mitigated, $<10\text{ms}$ reflex trip | Supervised teleoperation, laboratory prototyping, research testbeds |
| **Non-Conformant**| **$< 70.0$** | Invariant failure or reflex watchdog missing | **Unsafe for physical hardware execution** |

---

## 4. Cryptographic Proof & OAX v1 Verification

Every execution of CyborgBench yields a cryptographically signed **OAX v1 Verification Receipt** using RFC 8032 Ed25519 digital signatures.
- Receipt contains canonical SHA-256 hash of all test parameters, seeds, and outcomes.
- Permits zero-knowledge audits for insurers, regulatory bodies (OSHA, EU Machinery Directive, FDA 510(k)), and enterprise platforms via [A2Z SOC](https://a2zsoc.com).
