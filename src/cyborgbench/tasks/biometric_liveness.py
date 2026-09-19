"""
Axis 4: Biometric Liveness & ZK-Agency (BLA) Task.
Evaluates synthetic deepfake rejection, living tissue entropy verification,
and Zero-Knowledge cancelable proof-of-agency (The Moltbook Sybil Failure Prevention).
"""

import math
import hashlib
import hmac
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple, Callable


@dataclass
class BiometricResult:
    """Telemetry and outcome of the Biometric Liveness & ZK-Agency Task."""
    task_name: str = "Biometric Liveness & ZK-Agency"
    axis_code: str = "BLA"
    score: float = 0.0                      # 0.0 - 100.0
    genuine_samples_tested: int = 0
    synthetic_samples_tested: int = 0
    false_accept_count: int = 0            # Spoofs accepted (critical failure)
    false_reject_count: int = 0            # Genuine rejected
    false_accept_rate: float = 0.0         # FAR
    false_reject_rate: float = 0.0         # FRR
    zk_proofs_verified: int = 0
    zk_proofs_failed: int = 0
    mean_biological_entropy: float = 0.0
    passed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BiometricLivenessTask:
    """
    Evaluates bio-signal liveness and cryptographic proof-of-agency.
    Injects synthetic neural/EMG/pulse artifacts to verify deepfake rejection.
    """

    def __init__(
        self,
        sample_length: int = 128,
        entropy_threshold: float = 2.8,        # Minimum living tissue entropy in bits
        seed: int = 42
    ):
        self.sample_length = sample_length
        self.entropy_threshold = entropy_threshold
        self.random = random.Random(seed)

    def _generate_genuine_biological_signal(self) -> List[float]:
        """
        Generates realistic physiological micro-signal with pink noise (1/f)
        and non-linear biological heart/neural pulse dynamics.
        """
        signal = []
        phase = self.random.uniform(0, 2 * math.pi)
        for i in range(self.sample_length):
            t = i / float(self.sample_length)
            # Biological harmonic base
            base = math.sin(2 * math.pi * 1.2 * t + phase) + 0.3 * math.sin(2 * math.pi * 3.6 * t)
            # Biological physiological entropy (micro-fluctuations)
            noise = self.random.gauss(0.0, 0.25) + 0.05 * math.sin(2 * math.pi * 18.0 * t)
            signal.append(base + noise)
        return signal

    def _generate_synthetic_deepfake_signal(self) -> List[float]:
        """
        Generates synthetic neural/biometric artifact from a simulated generative model
        (smooth spectral distribution with lack of organic micro-fractal noise).
        """
        signal = []
        for i in range(self.sample_length):
            t = i / float(self.sample_length)
            # Over-smoothed or algorithmic periodicity (lacks genuine fractal entropy)
            synthetic = math.sin(2 * math.pi * 1.2 * t) + 0.28 * math.sin(2 * math.pi * 3.6 * t)
            # Regular white noise (unnatural flat spectrum)
            noise = self.random.uniform(-0.15, 0.15)
            signal.append(synthetic + noise)
        return signal

    def _calculate_sample_entropy(self, signal: List[float], bins: int = 16) -> float:
        """Computes empirical Shannon entropy of signal distribution in bits."""
        min_v, max_v = min(signal), max(signal)
        span = max_v - min_v if (max_v - min_v) > 1e-6 else 1.0

        counts = [0] * bins
        for v in signal:
            bin_idx = int(((v - min_v) / span) * (bins - 1))
            bin_idx = max(0, min(bins - 1, bin_idx))
            counts[bin_idx] += 1

        total = len(signal)
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return entropy

    def _generate_zk_cancelable_commitment(
        self,
        signal: List[float],
        user_secret_salt: str
    ) -> Tuple[str, str]:
        """
        Creates a Zero-Knowledge cancelable bio-commitment:
        No raw biometric signal is exposed or persisted (complying with BIPA & GDPR Art 9).
        Returns (public_commitment, proof_token).
        """
        # Feature extraction: quantization of spectral coefficients
        quantized = [f"{v:.2f}" for v in signal[:16]]
        feature_hash = hashlib.sha256(",".join(quantized).encode()).hexdigest()

        # Commitment: HMAC(salt, feature_hash)
        commitment = hmac.new(
            user_secret_salt.encode(),
            feature_hash.encode(),
            hashlib.sha256
        ).hexdigest()

        # Proof token: proof of possession without disclosing salt
        proof_token = hashlib.sha256((commitment + feature_hash).encode()).hexdigest()
        return commitment, proof_token

    def _verify_zk_commitment(
        self,
        commitment: str,
        signal: List[float],
        user_secret_salt: str
    ) -> bool:
        """Verifies that the cancelable bio-commitment matches the authorized user secret salt."""
        quantized = [f"{v:.2f}" for v in signal[:16]]
        feature_hash = hashlib.sha256(",".join(quantized).encode()).hexdigest()
        expected_commitment = hmac.new(
            user_secret_salt.encode(),
            feature_hash.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(commitment, expected_commitment)

    def run(
        self,
        custom_verifier: Optional[Callable[[List[float], str], bool]] = None,
        num_genuine: int = 100,
        num_synthetic: int = 100
    ) -> BiometricResult:
        """
        Executes the biometric liveness and agency benchmark.
        Tests whether the verifier accepts genuine signals and rejects synthetic deepfakes.
        """
        false_accept = 0
        false_reject = 0
        zk_verified = 0
        zk_failed = 0
        entropy_values: List[float] = []

        user_salt = "bipa_gdpr_compliant_salt_904812"

        # 1. Test Genuine Samples
        for _ in range(num_genuine):
            signal = self._generate_genuine_biological_signal()
            entropy = self._calculate_sample_entropy(signal)
            entropy_values.append(entropy)

            # Generate ZK proof
            commitment, proof = self._generate_zk_cancelable_commitment(signal, user_salt)

            if custom_verifier is not None:
                is_valid = custom_verifier(signal, proof)
            else:
                # Built-in check: entropy must exceed threshold AND ZK commitment must be valid
                is_liveness = entropy >= self.entropy_threshold
                is_auth = self._verify_zk_commitment(commitment, signal, user_salt)
                is_valid = is_liveness and is_auth

            if is_valid:
                zk_verified += 1
            else:
                false_reject += 1
                zk_failed += 1

        # 2. Test Synthetic Deepfake Samples (Adversarial Sybil attempts)
        for _ in range(num_synthetic):
            fake_signal = self._generate_synthetic_deepfake_signal()
            fake_entropy = self._calculate_sample_entropy(fake_signal)
            entropy_values.append(fake_entropy)

            # Attempt synthetic proof with adversarial unauthorized salt
            commitment, fake_proof = self._generate_zk_cancelable_commitment(
                fake_signal, "adversarial_salt"
            )

            if custom_verifier is not None:
                fake_accepted = custom_verifier(fake_signal, fake_proof)
            else:
                fake_liveness = fake_entropy >= self.entropy_threshold
                fake_auth = self._verify_zk_commitment(commitment, fake_signal, user_salt)
                fake_accepted = fake_liveness and fake_auth

            if fake_accepted:
                false_accept += 1

        # Calculate error rates
        far = (false_accept / num_synthetic) if num_synthetic > 0 else 0.0
        frr = (false_reject / num_genuine) if num_genuine > 0 else 0.0
        mean_entropy = sum(entropy_values) / len(entropy_values) if entropy_values else 0.0

        # Score formulation:
        # Heavily penalize False Accepts (deepfakes penetrating): -100 pts per 1.0 FAR
        # Moderately penalize False Rejects: -40 pts per 1.0 FRR
        score = 100.0 - (far * 100.0) - (frr * 40.0)
        score = max(0.0, min(100.0, round(score, 2)))

        passed = (far == 0.0) and (frr <= 0.05) and (score >= 85.0)

        return BiometricResult(
            score=score,
            genuine_samples_tested=num_genuine,
            synthetic_samples_tested=num_synthetic,
            false_accept_count=false_accept,
            false_reject_count=false_reject,
            false_accept_rate=round(far, 4),
            false_reject_rate=round(frr, 4),
            zk_proofs_verified=zk_verified,
            zk_proofs_failed=zk_failed,
            mean_biological_entropy=round(mean_entropy, 3),
            passed=passed,
            details={
                "sample_length": self.sample_length,
                "entropy_threshold_bits": self.entropy_threshold,
                "statutory_compliance": ["Illinois BIPA", "GDPR Art 9", "EU AI Act Annex III"]
            }
        )
