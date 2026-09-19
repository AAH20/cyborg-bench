"""
CyborgBench (Embodied-Eval)
The Apex Benchmark Suite & Verification Harness for Physical AI, Humanoid Robotics, BCIs & Cyborg Cybernetics.
"""

__version__ = "1.0.0"
__author__ = "Ahmed Hassan (A2Z SOC)"

from cyborgbench.core.scoring import CyborgQualityIndex, CQIScore, TierGrade
from cyborgbench.core.harness import BenchmarkHarness, BenchmarkConfig, BenchmarkReport
from cyborgbench.compliance.oax_receipt import (
    OAXReceipt,
    generate_verification_receipt,
    verify_receipt_signature,
)
from cyborgbench.compliance.a2zsoc_bridge import A2ZSOCBridge

__all__ = [
    "CyborgQualityIndex",
    "CQIScore",
    "TierGrade",
    "BenchmarkHarness",
    "BenchmarkConfig",
    "BenchmarkReport",
    "OAXReceipt",
    "generate_verification_receipt",
    "verify_receipt_signature",
    "A2ZSOCBridge",
]
