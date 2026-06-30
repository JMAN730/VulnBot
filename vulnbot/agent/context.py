"""VulnBot session context management - track pentest state across turns."""

from __future__ import annotations

import json
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, PrivateAttr, field_validator


class PentestPhase(str, Enum):
    """Penetration test phases."""

    IDLE = "Idle"
    RECON = "Recon"
    VULN_DISCOVERY = "Vulnerability Discovery"
    EXPLOITATION = "Exploitation"
    POST_EXPLOITATION = "Post-Exploitation"
    REPORTING = "Reporting"


LEGACY_PHASE_VALUES = {
    "\u5c31\u7eea": PentestPhase.IDLE,
    "\u4fe1\u606f\u6536\u96c6": PentestPhase.RECON,
    "\u6f0f\u6d1e\u53d1\u73b0": PentestPhase.VULN_DISCOVERY,
    "\u6f0f\u6d1e\u5229\u7528": PentestPhase.EXPLOITATION,
    "\u540e\u6e17\u900f": PentestPhase.POST_EXPLOITATION,
    "\u62a5\u544a\u751f\u6210": PentestPhase.REPORTING,
}


class VulnerabilityFinding(BaseModel):
    """A single vulnerability finding."""

    title: str = Field(description="Vulnerability title")
    severity: str = Field(default="Medium", description="Critical/High/Medium/Low/Info")
    vuln_type: str = Field(default="", description="Vulnerability type (SQLi, XSS, RCE, etc.)")
    description: str = Field(default="", description="Detailed description")
    evidence: str = Field(default="", description="Proof/evidence of the finding")
    cve: Optional[str] = Field(default=None, description="Associated CVE ID")
    remediation: str = Field(default="", description="Fix recommendation")
    poc_script: Optional[str] = Field(default=None, description="Generated PoC script path")
    evidence_level: str = Field(default="L1", description="L1-L4 evidence strength")
    lifecycle_status: str = Field(
        default="candidate",
        description="candidate/pending_verification/verified/rejected/needs_manual_review",
    )

    verified: bool = Field(default=False, description="Whether the finding was verified by PoC")
    verification_status: str = Field(
        default="pending", description="Verification status: pending/verified/rejected"
    )
    verified_at: Optional[str] = Field(default=None, description="Verification timestamp")
    verification_note: str = Field(default="", description="Verification note or rejection reason")

    finding_id: str = Field(default="", description="Unique finding identifier: vuln_type + target + location")

    def model_post_init(self, *args, **kwargs) -> None:
        # Vulnerability completeness validation.
        # If severity is High/Critical but evidence, vuln_type, remediation are all empty,
        # this is a placeholder finding - warn but allow it.
        if self.severity in ("Critical", "High"):
            if not self.evidence and not self.vuln_type and not self.remediation:
                self.title = f"[UNVERIFIED] {self.title}"
                self.description = (
                    "(This finding is missing verification evidence, vuln_type, and remediation. "
                    "The LLM reported it without concrete test results; add evidence before "
                    "treating it as a formal vulnerability.)"
                    + (f" {self.description}" if self.description else "")
                )

        if not self.finding_id:
            self.finding_id = self._generate_finding_id()
        self._sync_status_fields()

    def _sync_status_fields(self) -> None:
        """Keep lifecycle and evidence metadata consistent with verification state."""
        if self.verified or self.verification_status == "verified":
            self.verified = True
            self.verification_status = "verified"
            self.lifecycle_status = "verified"
            if self.evidence_level in ("", "L1", "L2", "L3"):
                self.evidence_level = "L4"
            return

        if self.verification_status == "rejected":
            self.verified = False
            self.lifecycle_status = "rejected"
            if self.evidence_level in ("", "L1", "L2"):
                self.evidence_level = "L3"
            return

        self.verified = False
        self.verification_status = "pending"
        if self.lifecycle_status == "needs_manual_review":
            if self.evidence_level in ("", "L1"):
                self.evidence_level = "L2"
            return
        if self.lifecycle_status == "candidate":
            self.evidence_level = self.evidence_level or "L1"
            return
        if self.evidence_level in ("", "L1"):
            self.lifecycle_status = "candidate"
            self.evidence_level = "L1"
        else:
            self.lifecycle_status = "pending_verification"

    def mark_manual_review(self, note: str = "", evidence_level: str = "L2") -> None:
        """Mark a finding as requiring manual review."""
        self.verified = False
        self.verification_status = "pending"
        self.lifecycle_status = "needs_manual_review"
        self.evidence_level = evidence_level
        if note:
            self.verification_note = note

    def _generate_finding_id(self) -> str:
        """Generate unique vulnerability identifier for deduplication.

        Key improvement: also checks the evidence field (populated by Layer 2
        auto-detection) in addition to description, since auto-detected findings
        put URLs/paths in evidence, not description.
        """
        location = ""
        # Try description first, then evidence (Layer 2 auto-findings put URLs there)
        for field in (self.description, self.evidence):
            if not field:
                continue
            url_match = re.search(r'https?://[^\s<>"\')\]]+', field)
            if url_match:
                location = url_match.group(0)
                break
            path_match = re.search(r'/[^\s<>"\')\]]+', field)
            if path_match:
                location = path_match.group(0)
                break

        # Use vuln_type as dedup key; fall back to title when type is missing.
        dedup_base = self.vuln_type.strip() or re.sub(r"\W+", "_", self.title.lower()).strip("_")
        if location:
            return f"{dedup_base}_{location}"[:50]
        return dedup_base[:50]

    def mark_verified(self, note: str = "", evidence_level: str = "L4") -> None:
        """Mark the finding as verified."""
        from datetime import datetime

        self.verified = True
        self.verification_status = "verified"
        self.lifecycle_status = "verified"
        self.evidence_level = evidence_level
        self.verified_at = datetime.now().isoformat()
        self.verification_note = note

    def mark_rejected(self, reason: str, evidence_level: str = "L3") -> None:
        """Mark the finding as rejected as a false positive."""
        from datetime import datetime

        self.verified = False
        self.verification_status = "rejected"
        self.lifecycle_status = "rejected"
        self.evidence_level = evidence_level
        self.verified_at = datetime.now().isoformat()
        self.verification_note = reason


class StepStatus(str, Enum):
    """Step execution status."""

    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    INFO = "info"


class StepRecord(BaseModel):
    """Structured record for one penetration-testing step."""

    phase: PentestPhase = Field(description="Phase")
    round: int = Field(default=0, description="Round number")
    action: str = Field(default="", description="Executed action, such as port scan or vuln probe")
    target: str = Field(default="", description="Target, such as IP, URL, or path")
    result: str = Field(default="", description="Execution result summary")
    status: StepStatus = Field(default=StepStatus.INFO, description="Execution status")
    detail: str = Field(default="", description="Optional detailed information")

    def to_summary(self) -> str:
        """Render a readable summary line."""
        status_icon = {
            StepStatus.SUCCESS: "[+]",
            StepStatus.FAILURE: "[-]",
            StepStatus.SKIPPED: "[skip]",
            StepStatus.INFO: "[*]",
        }.get(self.status, "")

        result = self.result[:60] + ("..." if len(self.result) > 60 else "")
        return f"{status_icon} Round {self.round}: {self.action} -> {result}"

    def to_brief(self) -> str:
        """Render a short list-friendly summary."""
        return f"{self.action}: {self.result}"[:80]


class TaskConstraints(BaseModel):
    """Structured hard constraints for an autonomous pentest task."""

    allowed_ports: list[int] = Field(default_factory=list)
    blocked_ports: list[int] = Field(default_factory=list)
    allowed_hosts: list[str] = Field(default_factory=list)
    blocked_hosts: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    blocked_paths: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    strict_mode: bool = Field(default=False)

    def is_empty(self) -> bool:
        return not any(
            [
                self.allowed_ports,
                self.blocked_ports,
                self.allowed_hosts,
                self.blocked_hosts,
                self.allowed_paths,
                self.blocked_paths,
                self.allowed_actions,
                self.blocked_actions,
                self.notes,
                self.strict_mode,
            ]
        )

    def to_prompt_block(self) -> str:
        """Render constraints into a stable prompt block for every round."""
        if self.is_empty():
            return ""

        lines = ["## Current Task Constraints"]
        if self.allowed_ports:
            lines.append(f"- Only test ports: {', '.join(str(p) for p in self.allowed_ports)}")
        if self.blocked_ports:
            lines.append(f"- Blocked ports: {', '.join(str(p) for p in self.blocked_ports)}")
        if self.allowed_hosts:
            lines.append(f"- Only test hosts: {', '.join(self.allowed_hosts)}")
        if self.blocked_hosts:
            lines.append(f"- Blocked hosts: {', '.join(self.blocked_hosts)}")
        if self.allowed_paths:
            lines.append(f"- Only test paths: {', '.join(self.allowed_paths)}")
        if self.blocked_paths:
            lines.append(f"- Blocked paths: {', '.join(self.blocked_paths)}")
        if self.allowed_actions:
            lines.append(f"- Only allowed actions: {', '.join(self.allowed_actions)}")
        if self.blocked_actions:
            lines.append(f"- Blocked actions: {', '.join(self.blocked_actions)}")
        if self.notes:
            lines.append(f"- Other limits: {'; '.join(self.notes)}")
        if self.strict_mode:
            lines.append("- Strict mode: only record out-of-scope items; do not actively test or execute tools.")
        return "\n".join(lines)


class ConstraintViolationEvent(BaseModel):
    """Structured audit event for a blocked constraint violation."""

    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    kind: str = Field(default="constraint_violation")
    code: str = Field(default="", description="Stable violation code")
    severity: str = Field(default="medium", description="low | medium | high")
    source: str = Field(default="", description="command | phase | tool")
    action: str = Field(default="", description="Normalized action name")
    tool_name: str = Field(default="", description="Tool name when source=tool")
    phase: str = Field(default="", description="Current phase label")
    summary: str = Field(default="", description="Human-readable summary")
    detail: str = Field(default="", description="Detailed diagnostic message")


class SessionState(BaseModel):
    """Full session state for a pentest engagement."""

    target: Optional[str] = None
    phase: PentestPhase = PentestPhase.IDLE
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resume_summary: str = Field(default="", description="Historical summary injected on resume")
    resume_meta: dict[str, Any] = Field(default_factory=dict, description="Resume metadata")
    task_constraints: TaskConstraints = Field(default_factory=TaskConstraints)
    constraint_violations: list[str] = Field(default_factory=list)
    constraint_violation_events: list[ConstraintViolationEvent] = Field(default_factory=list)
    findings: list[VulnerabilityFinding] = Field(default_factory=list)
    recon_data: dict[str, Any] = Field(default_factory=dict)
    # Raw step log kept for backward compatibility.
    executed_steps: list[str] = Field(default_factory=list)
    # Structured step records used for readable summaries.
    step_records: list[StepRecord] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    # Confirmed facts vs unverified assumptions are critical for CTF reasoning.
    confirmed_facts: list[str] = Field(default_factory=list, description="Facts verified by tools")
    unverified_assumptions: list[str] = Field(
        default_factory=list, description="Assumptions used in reasoning but not verified"
    )
    # Recon dimension completion tracking prevents premature [DONE] in info gathering.
    recon_dimensions_completed: dict[str, bool] = Field(
        default_factory=lambda: {
            "server": False,
            "website": False,
            "domain": False,
            "personnel": False,
        },
        description="Four-dimension recon completion tracking",
    )
    recon_dimension4_active: bool = Field(default=False, description="Whether personnel recon is active")

    # Finding deduplication tracking.
    _finding_ids_cache: set[str] = PrivateAttr(default_factory=set)

    semantic_dedup_threshold: float = Field(
        default=0.75, description="Semantic deduplication similarity threshold (0-1)"
    )

    @field_validator("phase", mode="before")
    @classmethod
    def _normalize_phase(cls, value: Any) -> Any:
        """Accept legacy saved phase labels while storing English labels."""
        if isinstance(value, PentestPhase):
            return value
        if isinstance(value, str):
            return LEGACY_PHASE_VALUES.get(value, value)
        return value

    def add_finding(self, finding: VulnerabilityFinding) -> bool:
        """Add a vulnerability finding with deduplication.

        Deduplication uses two layers:
            1. Exact finding_id match.
            2. Semantic similarity match, keeping the finding with stronger evidence.

        Returns:
            True if finding was added, False if duplicate (skipped).
        """
        if hasattr(finding, "_sync_status_fields"):
            finding._sync_status_fields()
        if not finding.finding_id:
            finding.finding_id = finding._generate_finding_id()

        if finding.finding_id in self._finding_ids_cache:
            print(f"[DEDUP] Skipping duplicate finding: {finding.title} (ID: {finding.finding_id})")
            return False

        from vulnbot.agent.finding_similarity import (
            _evidence_strength,
            finding_similarity,
        )

        for idx, existing in enumerate(self.findings):
            if finding_similarity(finding, existing) >= self.semantic_dedup_threshold:
                if _evidence_strength(finding) > _evidence_strength(existing):
                    print(
                        f"[DEDUP-SEM] Replacing semantically duplicate finding with stronger "
                        f"evidence: {finding.title} replaces {existing.title}"
                    )
                    self._finding_ids_cache.discard(existing.finding_id)
                    self._finding_ids_cache.add(finding.finding_id)
                    self.findings[idx] = finding
                else:
                    print(f"[DEDUP-SEM] Skipping semantically duplicate finding: {finding.title}")
                return False

        self._finding_ids_cache.add(finding.finding_id)
        self.findings.append(finding)
        return True

    def get_verified_findings(self) -> list[VulnerabilityFinding]:
        """Get verified findings."""
        return [f for f in self.findings if f.verified]

    def get_rejected_findings(self) -> list[VulnerabilityFinding]:
        """Get rejected findings."""
        return [f for f in self.findings if f.verification_status == "rejected"]

    def get_pending_findings(self) -> list[VulnerabilityFinding]:
        """Get findings pending verification."""
        return [f for f in self.findings if f.verification_status == "pending"]

    def get_candidate_findings(self) -> list[VulnerabilityFinding]:
        """Get findings that are still low-confidence candidates."""
        return [f for f in self.findings if f.lifecycle_status == "candidate"]

    def get_pending_verification_findings(self) -> list[VulnerabilityFinding]:
        """Get findings that have some evidence but still need verification."""
        return [f for f in self.findings if f.lifecycle_status == "pending_verification"]

    def get_manual_review_findings(self) -> list[VulnerabilityFinding]:
        """Get findings that require explicit or implicit manual review."""
        return [
            f
            for f in self.findings
            if (
                f.lifecycle_status == "needs_manual_review"
                or (
                    not f.verified
                    and f.verification_status != "rejected"
                    and f.severity in {"Critical", "High"}
                    and f.lifecycle_status in {"candidate", "pending_verification"}
                )
            )
        ]

    def add_recon_subdomain(self, subdomain: str) -> None:
        """Record a discovered subdomain into recon_data['subdomains'].

        The LLM can call this via python_execute when it discovers subdomains
        during the domain recon phase. Subdomains are displayed in report attack
        surface summaries.
        """
        if "subdomains" not in self.recon_data:
            self.recon_data["subdomains"] = []
        if subdomain and subdomain not in self.recon_data["subdomains"]:
            self.recon_data["subdomains"].append(subdomain)

    def add_constraint_violation(self, message: str) -> None:
        """Record a constraint violation audit event."""
        if not message:
            return
        if message not in self.constraint_violations:
            self.constraint_violations.append(message)
        elif self.constraint_violations and self.constraint_violations[-1] != message:
            self.constraint_violations.append(message)

        self.constraint_violations = self.constraint_violations[-20:]

    def add_constraint_violation_event(
        self,
        *,
        source: str,
        action: str = "",
        tool_name: str = "",
        code: str = "",
        severity: str = "medium",
        summary: str,
        detail: str = "",
    ) -> None:
        """Record a structured constraint violation audit event."""
        event = ConstraintViolationEvent(
            source=source,
            action=action,
            tool_name=tool_name,
            code=code,
            severity=severity,
            phase=self.phase.value if hasattr(self.phase, "value") else str(self.phase),
            summary=summary,
            detail=detail or summary,
        )
        self.constraint_violation_events.append(event)
        self.constraint_violation_events = self.constraint_violation_events[-20:]
        self.add_constraint_violation(summary)

    def add_step(
        self,
        step: str,
        action: str = "",
        target: str = "",
        result: str = "",
        status: StepStatus = StepStatus.INFO,
        detail: str = "",
    ) -> None:
        """Record an executed step.

        Args:
            step: Original step string (for backward compatibility).
            action: Short action description (e.g. "port scan", "vulnerability probe").
            target: Target of the action (e.g. "192.168.1.1:80", "/admin/login").
            result: Brief result summary (e.g. "found 22 open ports").
            status: Execution status.
            detail: Optional detailed information.
        """
        # Keep raw steps for backward compatibility and avoid consecutive duplicates.
        if not self.executed_steps or self.executed_steps[-1] != step:
            self.executed_steps.append(step)
        # Note: step_records creation removed earlier was restored below for summaries.

        if action:
            record = StepRecord(
                phase=self.phase,
                round=len(self.executed_steps),
                action=action,
                target=target,
                result=result or step[:60],
                status=status,
                detail=detail,
            )
            self.step_records.append(record)

    def get_step_summary(self) -> dict[str, Any]:
        """Generate an attack-path summary.

        Returns:
            Step summary grouped by phase, including key findings.
        """
        if self.step_records:
            return self._build_step_summary_from_records()

        if self.executed_steps:
            return self._parse_raw_steps()

        return {"total_steps": 0, "phases": {}, "key_findings": []}

    def _build_step_summary_from_records(self) -> dict[str, Any]:
        """Build a summary from structured step records."""
        phases: dict[str, list[StepRecord]] = {}
        for record in self.step_records:
            phase_name = record.phase.value
            if phase_name not in phases:
                phases[phase_name] = []
            phases[phase_name].append(record)

        phase_summaries = {}
        for phase_name, records in phases.items():
            phase_summaries[phase_name] = {
                "count": len(records),
                "actions": list(set(r.action for r in records)),
                "success_count": len([r for r in records if r.status == StepStatus.SUCCESS]),
                "failure_count": len([r for r in records if r.status == StepStatus.FAILURE]),
                "key_results": [r.to_brief() for r in records if r.status == StepStatus.SUCCESS][
                    :5
                ],
            }

        key_findings = [
            r.to_brief() for r in self.step_records if r.status == StepStatus.SUCCESS and r.result
        ][:10]

        return {
            "total_steps": len(self.step_records),
            "phases": phase_summaries,
            "key_findings": key_findings,
        }

    def _parse_raw_steps(self) -> dict[str, Any]:
        """Parse readable summaries from raw executed_steps as a compatibility fallback."""
        import re

        DISCOVERY_KEYWORDS = [
            "found",
            "discovered",
            "vulnerability",
            "port",
            "service",
            "path",
            "leak",
            "confirmed",
            "verified",
            "success",
            "connected",
            "accessible",
            "CVE",
            "flag",
            "sensitive",
        ]
        FAILURE_KEYWORDS = [
            "failed",
            "failure",
            "error",
            "timeout",
            "refused",
            "blocked",
            "unable",
            "404",
            "502",
            "503",
            "not found",
            "connection failed",
        ]

        phases: dict[str, dict] = {}
        key_findings: list[str] = []
        total_steps = len(self.executed_steps)

        for i, step in enumerate(self.executed_steps):
            round_match = re.search(r"Round\s*(\d+)", step)
            int(round_match.group(1)) if round_match else i + 1

            lowered_step = step.lower()
            has_failure = any(kw in lowered_step for kw in FAILURE_KEYWORDS)
            has_discovery = any(kw.lower() in lowered_step for kw in DISCOVERY_KEYWORDS)

            if has_discovery and not has_failure:
                status = StepStatus.SUCCESS
            elif has_failure:
                status = StepStatus.FAILURE
            else:
                status = StepStatus.INFO

            action = self._extract_action(step)

            result = self._extract_result(step)

            phase = self._guess_phase(step)

            if phase not in phases:
                phases[phase] = {
                    "count": 0,
                    "actions": set(),
                    "success_count": 0,
                    "failure_count": 0,
                    "key_results": [],
                }

            phases[phase]["count"] += 1
            if action:
                phases[phase]["actions"].add(action)
            if status == StepStatus.SUCCESS:
                phases[phase]["success_count"] += 1
                if result:
                    phases[phase]["key_results"].append(f"{action}: {result}" if action else result)
            elif status == StepStatus.FAILURE:
                phases[phase]["failure_count"] += 1

            if status == StepStatus.SUCCESS and result:
                key_findings.append(f"{action}: {result}" if action else result)

        phase_summaries = {}
        for phase_name, data in phases.items():
            phase_summaries[phase_name] = {
                "count": data["count"],
                "actions": list(data["actions"])[:5],
                "success_count": data["success_count"],
                "failure_count": data["failure_count"],
                "key_results": data["key_results"][:5],
            }

        return {
            "total_steps": total_steps,
            "phases": phase_summaries,
            "key_findings": key_findings[:10],
        }

    def get_constraints_prompt_block(self) -> str:
        """Return a stable prompt block for current task constraints."""
        return self.task_constraints.to_prompt_block()

    def _extract_action(self, step: str) -> str:
        """Extract a short action description from step text."""
        import re

        action_patterns = [
            r"attempt(?:ed|ing)?[^\s,.;]+",
            r"test(?:ed|ing)?[^\s,.;]+",
            r"scan(?:ned|ning)?[^\s,.;]+",
            r"probe(?:d|ing)?[^\s,.;]+",
            r"enumerat(?:ed|ing|e)[^\s,.;]+",
            r"verif(?:ied|y|ying)[^\s,.;]+",
            r"exploit(?:ed|ing)?[^\s,.;]+",
            r"check(?:ed|ing)?[^\s,.;]+",
            r"analyz(?:ed|ing|e)[^\s,.;]+",
            r"access(?:ed|ing)?[^\s,.;]+",
            r"connect(?:ed|ing)?[^\s,.;]+",
        ]
        for pattern in action_patterns:
            match = re.search(pattern, step, flags=re.IGNORECASE)
            if match:
                action = match.group(0)[:20]
                return action

        clean = re.sub(r"Round\s*\d+:", "", step)
        clean = re.sub(r"<think>.*?</think>", "", clean)
        clean = clean.strip()[:40]
        return clean if clean else "executed step"

    def _extract_result(self, step: str) -> str:
        """Extract a result summary from step text."""
        import re

        discovery_patterns = [
            r"found[^\s,.;]+",
            r"discovered[^\s,.;]+",
            r"confirmed[^\s,.;]+",
            r"verified[^\s,.;]+",
            r"vulnerability[^\s,.;]+",
            r"port[^\s,.;]+",
            r"path[^\s,.;]+",
            r"connected[^\s,.;]+",
            r"returned[^\s,.;]+",
            r"accessible[^\s,.;]+",
            r"success[^\s,.;]+",
        ]
        for pattern in discovery_patterns:
            match = re.search(pattern, step, flags=re.IGNORECASE)
            if match:
                result = match.group(0)[:50]
                result = re.sub(r"<think>.*?</think>", "", result)
                return result.strip()

        failure_patterns = [
            r"failed[^\s,.;]+",
            r"failure[^\s,.;]+",
            r"error[^\s,.;]+",
            r"timeout[^\s,.;]+",
            r"refused[^\s,.;]+",
            r"blocked[^\s,.;]+",
            r"unable[^\s,.;]+",
            r"404[^\s,.;]+",
        ]
        for pattern in failure_patterns:
            match = re.search(pattern, step, flags=re.IGNORECASE)
            if match:
                return match.group(0)[:50]

        return ""

    def _guess_phase(self, step: str) -> str:
        """Guess the phase from step content."""
        lowered_step = step.lower()
        if "phase transition" in lowered_step or "entered" in lowered_step:
            if "recon" in lowered_step or "reconnaissance" in lowered_step:
                return PentestPhase.RECON.value
            if "vulnerability discovery" in lowered_step or "vulnerability probe" in lowered_step:
                return PentestPhase.VULN_DISCOVERY.value
            if "exploitation" in lowered_step or "exploit" in lowered_step:
                return PentestPhase.EXPLOITATION.value
            if "report" in lowered_step:
                return PentestPhase.REPORTING.value

        recon_keywords = ["port", "service", "fingerprint", "architecture", "waf", "directory", "subdomain", "whois"]
        vuln_keywords = ["vulnerability", "injection", "xss", "sql", "csrf", "ssti", "probe"]
        exploit_keywords = ["exploit", "poc", "verify", "verified"]

        for kw in exploit_keywords:
            if kw in lowered_step:
                return PentestPhase.EXPLOITATION.value

        for kw in vuln_keywords:
            if kw in lowered_step:
                return PentestPhase.VULN_DISCOVERY.value

        for kw in recon_keywords:
            if kw in lowered_step:
                return PentestPhase.RECON.value

        return self.phase.value

    def add_note(self, note: str) -> None:
        """Add a session note, filtering out code/symbol-heavy noise."""
        import re as _re

        # Reject notes that are primarily code/symbols; these pollute evidence extraction
        # and create fake URLs/paths in findings.
        word_chars = _re.findall(r"[A-Za-z0-9_]", note)
        code_symbols = _re.findall(
            r"[{}()=+*/<>\-\\[\\]|;|import |def |return |print\(|requests\.|socket\.|re\.|sys\.]",
            note,
        )
        if len(note) > 20 and len(code_symbols) > max(len(word_chars) * 0.5, 8):
            # Too much code, skip it
            return
        # Reject very short notes that are just code symbols or numbers
        if len(note) < 5 or note in ("---", "**", ">>>", "..."):
            return
        self.notes.append(note)

    def add_confirmed_fact(self, fact: str) -> None:
        """Add a confirmed fact (verified by tool output)."""
        if fact and fact not in self.confirmed_facts:
            self.confirmed_facts.append(fact)

    def add_assumption(self, assumption: str) -> None:
        """Add an unverified assumption."""
        if assumption and assumption not in self.unverified_assumptions:
            self.unverified_assumptions.append(assumption)

    def mark_recon_dimension(self, dimension: str) -> None:
        """Mark a recon dimension as completed.

        Args:
            dimension: One of 'server', 'website', 'domain', 'personnel'
        """
        if dimension in self.recon_dimensions_completed:
            self.recon_dimensions_completed[dimension] = True

    def has_prior_recon(self) -> bool:
        """Whether this restored session already holds meaningful recon.

        True when recon_data contains real assets in any known category, or
        when the phase has already advanced past Recon. Used to decide whether
        a resumed run should reuse recon instead of re-scanning.
        """
        recon_categories = (
            "network_services",
            "network_scans",
            "subdomains",
            "paths",
            "params",
            "ports",
            "services",
        )
        for category in recon_categories:
            value = self.recon_data.get(category)
            if isinstance(value, list) and value:
                return True
        return self.phase in (
            PentestPhase.VULN_DISCOVERY,
            PentestPhase.EXPLOITATION,
            PentestPhase.POST_EXPLOITATION,
            PentestPhase.REPORTING,
        )

    def mark_recon_complete_from_data(self) -> None:
        """Mark the core recon dimensions complete when reusing prior recon.

        Sets server/website/domain so is_recon_complete() is satisfied without
        forcing fresh recon rounds. Personnel (dimension 4) is left untouched
        because is_recon_complete() only checks it when recon_dimension4_active.
        """
        for dimension in ("server", "website", "domain"):
            if dimension in self.recon_dimensions_completed:
                self.recon_dimensions_completed[dimension] = True

    def is_recon_complete(self) -> bool:
        """Check if all active recon dimensions have been completed at least once.

        Dimension 4 (personnel) is only checked if it's been activated.
        """
        for dim, completed in self.recon_dimensions_completed.items():
            if dim == "personnel" and not self.recon_dimension4_active:
                continue  # Skip inactive dimension 4
            if not completed:
                return False
        return True

    def get_recon_status_text(self) -> str:
        """Get a human-readable recon dimension completion status."""
        parts = []
        dim_names = {
            "server": "Dimension 1 (Server)",
            "website": "Dimension 2 (Website)",
            "domain": "Dimension 3 (Domain)",
            "personnel": "Dimension 4 (Personnel)",
        }
        for dim, completed in self.recon_dimensions_completed.items():
            if dim == "personnel" and not self.recon_dimension4_active:
                continue  # Skip inactive dimension 4
            name = dim_names.get(dim, dim)
            parts.append(f"{'[x]' if completed else '[ ]'} {name}")
        incomplete = [
            dim
            for dim, done in self.recon_dimensions_completed.items()
            if (dim != "personnel" or self.recon_dimension4_active) and not done
        ]
        status = " | ".join(parts)
        if incomplete:
            status += f"\n-> {len(incomplete)} dimensions remain unchecked; continue recon and do not mark [DONE]."
        return status

    def advance_phase(self, phase: PentestPhase) -> None:
        """Move to a new phase."""
        old_phase = self.phase
        self.phase = phase
        self.add_step(
            step=f"Phase transition -> {phase.value}",
            action="Phase transition",
            target=f"{old_phase.value} -> {phase.value}",
            result=f"Entered {phase.value} phase",
            status=StepStatus.INFO,
        )

    def save(self, path: Optional[Path] = None) -> Path:
        """Save session state to JSON file."""
        if path is None:
            from vulnbot.config.settings import SESSIONS_DIR

            safe_target = (self.target or "unknown").replace("/", "_").replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = SESSIONS_DIR / f"{timestamp}_{safe_target}.json"

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, path: Path) -> "SessionState":
        """Load session state from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


class ContextManager:
    """Manages conversation context and session state."""

    def __init__(self, max_history: int = 200) -> None:
        self.max_history = max_history
        self.messages: list[dict[str, str]] = []
        self.state = SessionState()

    def add_user_message(self, content: str) -> None:
        """Add a user message to context."""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to context."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_system_message(self, content: str) -> None:
        """Add a system message (inserted at beginning)."""
        # System messages are handled separately in the API call
        pass

    def get_messages(self) -> list[dict[str, str]]:
        """Get conversation messages for API call."""
        return self.messages.copy()

    def reset(self) -> None:
        """Reset context and session state."""
        self.messages = []
        self.state = SessionState()

    def _trim(self) -> None:
        """Trim old messages to stay within limit.

        Instead of blindly dropping old messages, we compress them
        into a summary to preserve key discoveries for multi-round loops.
        """
        if len(self.messages) <= self.max_history:
            return

        # Keep the most recent 70% of messages intact
        keep_count = int(self.max_history * 0.7)
        recent = self.messages[-keep_count:]
        old = self.messages[:-keep_count]

        # Compress old messages into a summary instead of discarding
        summary = self._compress_messages(old)

        self.messages = []
        if summary:
            self.messages.append(
                {
                    "role": "system",
                    "content": f"[Previous conversation summary]\n{summary}",
                }
            )
        self.messages.extend(recent)

    @staticmethod
    def _compress_messages(messages: list[dict[str, str]]) -> str:
        """Compress a list of messages into a concise summary.

        Extracts key findings, tool results, and discoveries from the
        conversation history so the LLM doesn't completely lose context.
        """
        key_parts = []

        for msg in messages:
            content = msg.get("content", "")
            # Extract tool call/result information; these contain actual findings.
            if "Tool call:" in content or "Tool result:" in content:
                key_parts.append(content[:300])

            # Extract lines that look like findings/discoveries
            for line in content.split("\n"):
                stripped = line.strip()
                if any(
                    marker in stripped
                    for marker in [
                        "[+]",
                        "[!]",
                        "[-]",
                        "found",
                        "discovered",
                        "vulnerability",
                        "flag",
                        "CVE",
                        "port",
                        "open",
                        "service",
                        "path",
                        "leak",
                        "injection",
                        "Status:",
                        "Headers:",
                        "Body",
                        # Negative/failure markers are critical for avoiding repeated CTF attempts.
                        "failed",
                        "invalid",
                        "not found",
                        "same response",
                        "blocked",
                        "unsuccessful",
                        "does not exist",
                        "error",
                        "404",
                        "timeout",
                        # Confirmed fact markers are verified by actual tool output.
                        "verified",
                        "confirmed",
                        # Assumption markers are things the LLM assumed but did not verify.
                        "assumption",
                        "should",
                        "possibly",
                        "inferred",
                        "guessed",
                        "estimated",
                    ]
                ):
                    key_parts.append(stripped[:200])

        if not key_parts:
            return ""

        # Limit total summary size to avoid context bloat
        summary = "\n".join(key_parts)
        if len(summary) > 3000:
            summary = summary[:3000] + "\n...(more history omitted)"

        return summary

    def trim_messages(self, max_messages: int = 20) -> None:
        """Forcefully trim conversation history to a specific size.

        Used when context overflow causes repeated LLM errors.
        """
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
