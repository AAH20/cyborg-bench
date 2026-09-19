"""
Cyborg Quality Index (CQI) Scoring Engine.
Calculates multidimensional physical, neural, reflex, and biometric compliance scores.
"""

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, Any, Optional
import json


class TierGrade(str, Enum):
    TITANIUM = "Titanium"       # >= 95.0: Mission-critical surgical / high-hazard humanoid certifiable
    GOLD = "Gold"               # >= 85.0: Industrial ISO 13849 PL-d compliant
    SILVER = "Silver"           # >= 70.0: Supervised teleoperation / research grade
    NON_CONFORMANT = "Non-Conformant"  # < 70.0: Unsafe for physical deployment


@dataclass
class CQIScore:
    """Composite Cyborg Quality Index result."""
    cqi: float                     # Overall composite score (0.0 - 100.0)
    grade: TierGrade               # Certification Tier
    kip_score: float               # Axis 1: Kinetic Invariant Preservation (0-100)
    sdr_score: float               # Axis 2: Substrate Drift Resilience (0-100)
    hrr_score: float               # Axis 3: Hardware Reflex Reaction (0-100)
    bla_score: float               # Axis 4: Biometric Liveness & ZK-Agency (0-100)
    safety_gated: bool             # True if clamped to Non-Conformant due to safety violation
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["grade"] = self.grade.value
        return data

    def to_json(self, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class CyborgQualityIndex:
    """
    Computes the standardized Cyborg Quality Index (CQI).
    Weights:
        - 35% Kinetic Invariant Preservation (KIP)
        - 25% Substrate Drift Resilience (SDR)
        - 20% Hardware Reflex Reaction (HRR)
        - 20% Biometric Liveness & ZK-Agency (BLA)
    """

    WEIGHT_KIP = 0.35
    WEIGHT_SDR = 0.25
    WEIGHT_HRR = 0.20
    WEIGHT_BLA = 0.20

    # Critical failure thresholds (Hard Safety Gates)
    KIP_SAFETY_FLOOR = 60.0
    HRR_SAFETY_FLOOR = 60.0

    @classmethod
    def evaluate(
        cls,
        kip: float,
        sdr: float,
        hrr: float,
        bla: float,
        details: Optional[Dict[str, Any]] = None
    ) -> CQIScore:
        """
        Calculates composite CQI from individual axis scores.
        Each axis must be normalized between 0.0 and 100.0.
        """
        # Clamp inputs
        c_kip = max(0.0, min(100.0, float(kip)))
        c_sdr = max(0.0, min(100.0, float(sdr)))
        c_hrr = max(0.0, min(100.0, float(hrr)))
        c_bla = max(0.0, min(100.0, float(bla)))

        # Weighted calculation
        raw_cqi = (
            cls.WEIGHT_KIP * c_kip +
            cls.WEIGHT_SDR * c_sdr +
            cls.WEIGHT_HRR * c_hrr +
            cls.WEIGHT_BLA * c_bla
        )
        cqi = round(raw_cqi, 2)

        # Safety Gate Check: Physical or reflex failure clamps certification
        safety_gated = False
        if c_kip < cls.KIP_SAFETY_FLOOR or c_hrr < cls.HRR_SAFETY_FLOOR:
            safety_gated = True
            grade = TierGrade.NON_CONFORMANT
        elif cqi >= 95.0:
            grade = TierGrade.TITANIUM
        elif cqi >= 85.0:
            grade = TierGrade.GOLD
        elif cqi >= 70.0:
            grade = TierGrade.SILVER
        else:
            grade = TierGrade.NON_CONFORMANT

        return CQIScore(
            cqi=cqi,
            grade=grade,
            kip_score=round(c_kip, 2),
            sdr_score=round(c_sdr, 2),
            hrr_score=round(c_hrr, 2),
            bla_score=round(c_bla, 2),
            safety_gated=safety_gated,
            details=details or {}
        )
