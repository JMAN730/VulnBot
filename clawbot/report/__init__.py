"""ClawBot Report Module - structured report generation with vulnerability verification."""

from clawbot.report.filter import ReportContentFilter, filter_report_content
from clawbot.report.generator import (
    generate_persistent_cycle_report,
    generate_report,
    generate_report_from_file,
)
from clawbot.report.poc_builder import generate_pocs, generate_single_poc
from clawbot.report.verifier import (
    PoCGenerator,
    VerificationResult,
    VerificationStatus,
    VerifiedFinding,
    VerifierExecutor,
    VulnerabilityVerifier,
)

__all__ = [
    # Generator
    "generate_report",
    "generate_report_from_file",
    "generate_persistent_cycle_report",
    # Verifier
    "VulnerabilityVerifier",
    "VerifiedFinding",
    "VerificationStatus",
    "VerificationResult",
    "PoCGenerator",
    "VerifierExecutor",
    # Filter
    "ReportContentFilter",
    "filter_report_content",
    # PoC
    "generate_pocs",
    "generate_single_poc",
]
