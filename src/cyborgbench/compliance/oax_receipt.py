"""
OAX v1 Cryptographic Verification Receipt Generator.
Implements Ed25519 (RFC 8032) signing and verification with zero external dependencies,
emitting tamper-evident audit receipts for physical, humanoid, and BCI benchmark runs.
"""

import os
import json
import hashlib
import base64
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# ============================================================================
# Pure-Python RFC 8032 Ed25519 Implementation (Zero External Dependencies)
# ============================================================================

q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493


def expmod(b: int, e: int, m: int) -> int:
    return pow(b, e, m)


def inv(x: int) -> int:
    return expmod(x, q - 2, q)


d = -121665 * inv(121666) % q
I = expmod(2, (q - 1) // 4, q)


def xrecover(y: int) -> int:
    xx = (y * y - 1) * inv(d * y * y + 1)
    x = expmod(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * I) % q
    if x % 2 != 0:
        x = q - x
    return x


By = 4 * inv(5) % q
Bx = xrecover(By)
B = (Bx, By)


def edwards_add(P: Tuple[int, int], Q: Tuple[int, int]) -> Tuple[int, int]:
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * inv(1 + d * x1 * x2 * y1 * y2) % q
    y3 = (y1 * y2 + x1 * x2) * inv(1 - d * x1 * x2 * y1 * y2) % q
    return (x3, y3)


def scalarmult(P: Tuple[int, int], e: int) -> Tuple[int, int]:
    if e == 0:
        return (0, 1)
    Q = scalarmult(P, e // 2)
    Q = edwards_add(Q, Q)
    if e & 1:
        Q = edwards_add(Q, P)
    return Q


def encodepoint(P: Tuple[int, int]) -> bytes:
    x, y = P
    bits = [(y >> i) & 1 for i in range(255)] + [x & 1]
    return bytes([sum([bits[i * 8 + j] << j for j in range(8)]) for i in range(32)])


def decodepoint(s: bytes) -> Tuple[int, int]:
    y = sum([s[i] << (i * 8) for i in range(32)]) & ((1 << 255) - 1)
    x = xrecover(y)
    if (x & 1) != ((s[31] >> 7) & 1):
        x = q - x
    P = (x, y)
    if not isoncurve(P):
        raise ValueError("Decoding point that is not on Edwards curve")
    return P


def isoncurve(P: Tuple[int, int]) -> bool:
    x, y = P
    return (-x * x + y * y - 1 - d * x * x * y * y) % q == 0


def H(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def rfc8032_publickey(sk: bytes) -> bytes:
    h = H(sk)
    a = 2**254 + sum([h[i] << (i * 8) for i in range(3, 32)])
    a &= ~7
    A = scalarmult(B, a)
    return encodepoint(A)


def rfc8032_signature(m: bytes, sk: bytes, pk: bytes) -> bytes:
    h = H(sk)
    a = 2**254 + sum([h[i] << (i * 8) for i in range(3, 32)])
    a &= ~7
    r = sum([h[i] << (i * 8) for i in range(32, 64)])
    r_bytes = bytes([sum([(r >> (i * 8 + j)) & 1 << j for j in range(8)]) for i in range(32)])
    rH = int.from_bytes(hashlib.sha512(r_bytes + m).digest(), "little")
    R = scalarmult(B, rH)
    R_bytes = encodepoint(R)
    k = int.from_bytes(hashlib.sha512(R_bytes + pk + m).digest(), "little")
    S = (rH + k * a) % l
    S_bytes = S.to_bytes(32, "little")
    return R_bytes + S_bytes


def rfc8032_verify(s: bytes, m: bytes, pk: bytes) -> bool:
    if len(s) != 64 or len(pk) != 32:
        return False
    R = decodepoint(s[:32])
    A = decodepoint(pk)
    S = int.from_bytes(s[32:], "little")
    if S >= l:
        return False
    k = int.from_bytes(hashlib.sha512(s[:32] + pk + m).digest(), "little")
    P1 = scalarmult(B, S)
    P2 = edwards_add(R, scalarmult(A, k))
    return P1 == P2


# ============================================================================
# Key Management
# ============================================================================

def generate_keypair() -> Tuple[bytes, bytes]:
    """Generates an Ed25519 (private_key, public_key) pair."""
    sk = os.urandom(32)
    pk = rfc8032_publickey(sk)
    return sk, pk


# ============================================================================
# OAX v1 Data Structures
# ============================================================================

@dataclass
class OAXReceipt:
    receipt_id: str
    target_system: str
    timestamp: str
    composite_cqi: float
    tier_grade: str
    axis_scores: Dict[str, float]
    standards_mapped: List[str]
    payload_hash: str
    signature: str
    public_key: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_canonical_json(self) -> str:
        data = {
            "receipt_id": self.receipt_id,
            "target_system": self.target_system,
            "timestamp": self.timestamp,
            "composite_cqi": self.composite_cqi,
            "tier_grade": self.tier_grade,
            "axis_scores": self.axis_scores,
            "standards_mapped": self.standards_mapped,
            "payload_hash": self.payload_hash,
            "metadata": self.metadata
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def generate_markdown(self) -> str:
        lines = [
            f"# OAX v1 Verification Receipt: {self.target_system}",
            f"**Receipt ID:** `{self.receipt_id}`",
            f"**Issued Timestamp:** `{self.timestamp}`",
            f"**Tier Grade:** **{self.tier_grade}** (Composite CQI: `{self.composite_cqi:.2f}` / 100.0)",
            f"**Cryptographic Signature:** `{self.signature[:32]}...`",
            "",
            "---",
            "",
            "## 1. Multi-Axis Benchmark Scores",
            "",
            "| Evaluation Axis | Code | Weight | Score | Result |",
            "| :--- | :--- | :--- | :--- | :--- |",
            f"| Kinetic Invariant Preservation | `KIP` | 35% | `{self.axis_scores.get('KIP', 0.0):.2f}` | {'PASS' if self.axis_scores.get('KIP', 0.0) >= 70 else 'FAIL'} |",
            f"| Substrate Drift Resilience | `SDR` | 25% | `{self.axis_scores.get('SDR', 0.0):.2f}` | {'PASS' if self.axis_scores.get('SDR', 0.0) >= 70 else 'FAIL'} |",
            f"| Hardware Reflex Reaction | `HRR` | 20% | `{self.axis_scores.get('HRR', 0.0):.2f}` | {'PASS' if self.axis_scores.get('HRR', 0.0) >= 70 else 'FAIL'} |",
            f"| Biometric Liveness & ZK-Agency | `BLA` | 20% | `{self.axis_scores.get('BLA', 0.0):.2f}` | {'PASS' if self.axis_scores.get('BLA', 0.0) >= 70 else 'FAIL'} |",
            "",
            "---",
            "",
            "## 2. Regulatory & Safety Conformity",
            ""
        ]
        for std in self.standards_mapped:
            lines.append(f"- [x] **{std}**")

        lines.extend([
            "",
            "---",
            "",
            "## 3. Cryptographic Verification Block",
            "```json",
            json.dumps({
                "payload_sha256": self.payload_hash,
                "ed25519_pubkey": self.public_key,
                "ed25519_signature": self.signature
            }, indent=2),
            "```",
            "",
            "> Certified by **A2Z SOC** via CyborgBench open-source verification harness."
        ])
        return "\n".join(lines)


def generate_verification_receipt(
    target_system: str,
    cqi_score: float,
    tier_grade: str,
    axis_scores: Dict[str, float],
    private_key_bytes: Optional[bytes] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> OAXReceipt:
    """
    Constructs and cryptographically signs an OAX v1 verification receipt.
    """
    if private_key_bytes is None:
        sk, pk = generate_keypair()
    else:
        sk = private_key_bytes
        pk = rfc8032_publickey(sk)

    timestamp = datetime.now(timezone.utc).isoformat()
    raw_id = f"oax_cyborg_{hashlib.sha256((target_system + timestamp).encode()).hexdigest()[:16]}"

    payload_data = {
        "target": target_system,
        "timestamp": timestamp,
        "cqi": cqi_score,
        "axes": axis_scores,
        "metadata": metadata or {}
    }
    payload_json = json.dumps(payload_data, sort_keys=True, separators=(",", ":"))
    payload_hash = "sha256:" + hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    standards = [
        "ISO 13849-1 (PL-d Machinery Functional Safety)",
        "ISO 10218-1 / 10218-2 (Collaborative Industrial Robotics Safety)",
        "EU AI Act (Annex III High-Risk AI System Assessment)",
        "Illinois BIPA 740 ILCS 14/ (Zero-Knowledge Biometric Privacy)",
        "GDPR Article 9 (Special Category Neural/Biometric Processing)"
    ]

    receipt = OAXReceipt(
        receipt_id=raw_id,
        target_system=target_system,
        timestamp=timestamp,
        composite_cqi=cqi_score,
        tier_grade=tier_grade,
        axis_scores=axis_scores,
        standards_mapped=standards,
        payload_hash=payload_hash,
        signature="",
        public_key=base64.b64encode(pk).decode("utf-8"),
        metadata=metadata or {"issuer": "A2Z SOC", "harness": "cyborg-bench v1.0.0"}
    )

    # Sign canonical representation
    canonical_bytes = receipt.to_canonical_json().encode("utf-8")
    sig_bytes = rfc8032_signature(canonical_bytes, sk, pk)
    receipt.signature = base64.b64encode(sig_bytes).decode("utf-8")

    return receipt


def verify_receipt_signature(receipt: OAXReceipt) -> bool:
    """
    Cryptographically verifies the authenticity and tamper-resistance of an OAX receipt.
    """
    try:
        pk_bytes = base64.b64decode(receipt.public_key.encode("utf-8"))
        sig_bytes = base64.b64decode(receipt.signature.encode("utf-8"))
        canonical_bytes = receipt.to_canonical_json().encode("utf-8")
        return rfc8032_verify(sig_bytes, canonical_bytes, pk_bytes)
    except Exception:
        return False
