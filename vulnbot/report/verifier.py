"""Validate findings before they are included in reports."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from vulnbot.agent.context import VulnerabilityFinding


class VerificationStatus(str, Enum):
    """Verification lifecycle status."""

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class VerificationResult(str, Enum):
    """Detailed verification result."""

    VULN_CONFIRMED = "vuln_confirmed"
    SENSITIVE_DATA_EXPOSED = "sensitive_data"
    SECURITY_BYPASS = "security_bypass"
    FALSE_POSITIVE = "false_positive"
    NO_RESPONSE_DIFF = "no_response_diff"
    PARAM_INVALID = "param_invalid"
    NORMAL_RESPONSE = "normal_response"
    TIMEOUT = "timeout"
    ERROR_403_404 = "error_403_404"


@dataclass
class VerifiedFinding:
    """A finding plus its verification evidence."""

    original_finding: VulnerabilityFinding
    status: VerificationStatus = VerificationStatus.PENDING
    result: Optional[VerificationResult] = None
    poc_code: Optional[str] = None
    poc_output: Optional[str] = None
    poc_executed_at: Optional[str] = None
    verified_description: str = ""
    verified_evidence: str = ""
    verified_severity: str = ""
    rejection_reason: str = ""
    verified_by: str = "verifier_module"
    verified_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PoCGenerator:
    """Generate runnable Python proof-of-concept scripts."""

    @classmethod
    def generate_poc(
        cls,
        finding: VulnerabilityFinding,
        target: str,
        baseline_len: int = 0,
    ) -> str:
        """Generate PoC code for a finding."""
        vuln_type = (finding.vuln_type or finding.title or "").lower()
        payload = cls._guess_payload(finding)
        safe_target = target.replace("\\", "\\\\").replace('"', '\\"')
        safe_payload = payload.replace("\\", "\\\\").replace('"', '\\"')

        if "sql" in vuln_type or "sqli" in vuln_type:
            return f'''import requests

target = "{safe_target}"
payload = "{safe_payload or "' OR '1'='1"}"
baseline_len = {baseline_len}

try:
    response = requests.get(target, params={{"q": payload}}, timeout=10, verify=False)
    body = response.text.lower()
    errors = ["sql syntax", "mysql", "postgres", "sqlite", "ora-", "odbc", "syntax error"]
    for marker in errors:
        if marker in body:
            print(f"[CONFIRMED] SQL injection indicator detected: {{marker}}")
            print(f"[INFO] Response status: {{response.status_code}}")
            raise SystemExit(0)
    if baseline_len and abs(len(response.content) - baseline_len) > max(200, baseline_len * 0.2):
        print(f"[POSSIBLE] Response length differs: {{len(response.content)}} vs baseline {{baseline_len}}")
    else:
        print("[REJECTED] No SQL injection indicators detected")
except requests.Timeout:
    print("[REJECTED] Request timed out")
except Exception as exc:
    print(f"[ERROR] Request failed: {{exc}}")
'''

        if "xss" in vuln_type or "cross_site" in vuln_type:
            return f'''import requests

target = "{safe_target}"
payload = "{safe_payload or "<script>alert(1)</script>"}"

try:
    response = requests.get(target, params={{"q": payload}}, timeout=10, verify=False)
    if payload in response.text:
        print("[CONFIRMED] XSS payload is reflected in the response")
        print(f"[INFO] Reflected payload: {{payload}}")
    else:
        print("[REJECTED] XSS payload was not reflected")
except requests.Timeout:
    print("[REJECTED] Request timed out")
except Exception as exc:
    print(f"[ERROR] Request failed: {{exc}}")
'''

        if "command" in vuln_type or "rce" in vuln_type:
            return f'''import requests

target = "{safe_target}"
payload = "{safe_payload or ";id"}"

try:
    response = requests.get(target, params={{"cmd": payload}}, timeout=10, verify=False)
    body = response.text.lower()
    for marker in ("uid=", "gid=", "groups=", "root:", "www-data"):
        if marker in body:
            print(f"[CONFIRMED] Command execution indicator detected: {{marker}}")
            raise SystemExit(0)
    print("[REJECTED] No command execution indicators detected")
except requests.Timeout:
    print("[REJECTED] Request timed out")
except Exception as exc:
    print(f"[ERROR] Request failed: {{exc}}")
'''

        if "lfi" in vuln_type or "file" in vuln_type or "path traversal" in vuln_type:
            return f'''import requests

target = "{safe_target}"
payload = "{safe_payload or "../../../../etc/passwd"}"

try:
    response = requests.get(target, params={{"file": payload}}, timeout=10, verify=False)
    body = response.text.lower()
    for marker in ("root:x:", "daemon:x:", "[boot loader]", "/bin/bash"):
        if marker in body:
            print(f"[CONFIRMED] Local file disclosure indicator detected: {{marker}}")
            raise SystemExit(0)
    print("[REJECTED] No local file disclosure indicators detected")
except requests.Timeout:
    print("[REJECTED] Request timed out")
except Exception as exc:
    print(f"[ERROR] Request failed: {{exc}}")
'''

        return cls._generic_template().format(
            target=safe_target,
            payload=safe_payload,
            baseline_len=baseline_len,
        )

    @classmethod
    def _generic_template(cls) -> str:
        """Generate a generic PoC template."""
        return '''import requests

target = "{target}"
payload = "{payload}"
baseline_len = {baseline_len}

try:
    print(f"[*] Testing target: {{target}}")
    response = requests.get(target, timeout=10, verify=False)
    print(f"[*] Response status: {{response.status_code}}")
    print(f"[*] Response length: {{len(response.content)}}")
    print("[INFO] Generic template used; add issue-specific validation if needed")
except requests.Timeout:
    print("[REJECTED] Request timed out")
except Exception as exc:
    print(f"[ERROR] Request failed: {{exc}}")
'''

    @classmethod
    def _guess_payload(cls, finding: VulnerabilityFinding) -> str:
        """Guess a starter payload from finding type and evidence."""
        text = f"{finding.title} {finding.description} {finding.evidence}".lower()
        if "sql" in text:
            return "' OR '1'='1"
        if "xss" in text:
            return "<script>alert(1)</script>"
        if "command" in text or "rce" in text:
            return ";id"
        if "lfi" in text or "path traversal" in text or "file" in text:
            return "../../../../etc/passwd"
        return ""


class VerifierExecutor:
    """Execute PoC scripts and classify their output."""

    PYTHON_CMD = "python"

    @classmethod
    def execute_poc(cls, poc_code: str, timeout: int = 30) -> tuple[int, str]:
        """Execute PoC code in a temporary Python file."""
        temp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as handle:
                handle.write(poc_code)
                temp_path = Path(handle.name)

            result = subprocess.run(
                [cls.PYTHON_CMD, str(temp_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = (result.stdout or "") + (result.stderr or "")
            return result.returncode, output
        except subprocess.TimeoutExpired:
            return -1, "[TIMEOUT] PoC execution timed out"
        except FileNotFoundError:
            return -2, f"[ERROR] Python interpreter not found: {cls.PYTHON_CMD}"
        except Exception as exc:
            return -3, f"[ERROR] Execution failed: {exc}"
        finally:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    @classmethod
    def parse_result(cls, output: str, returncode: int) -> VerificationResult:
        """Parse PoC output into a verification result."""
        output_lower = output.lower()

        if returncode == -1 or "timeout" in output_lower:
            return VerificationResult.TIMEOUT
        if "403" in output or "404" in output:
            return VerificationResult.ERROR_403_404
        if "[error]" in output_lower and "[confirmed]" not in output_lower:
            return VerificationResult.FALSE_POSITIVE
        if "[confirmed]" in output_lower:
            if "sensitive" in output_lower or "disclosure" in output_lower:
                return VerificationResult.SENSITIVE_DATA_EXPOSED
            if "bypass" in output_lower:
                return VerificationResult.SECURITY_BYPASS
            return VerificationResult.VULN_CONFIRMED
        if "[rejected]" in output_lower:
            return VerificationResult.FALSE_POSITIVE
        if "[possible]" in output_lower and "diff" in output_lower:
            return VerificationResult.NO_RESPONSE_DIFF
        if "normal response" in output_lower:
            return VerificationResult.NORMAL_RESPONSE
        return VerificationResult.FALSE_POSITIVE


class VulnerabilityVerifier:
    """Main verification workflow."""

    def __init__(self, target: str, baseline_len: int = 0) -> None:
        self.target = target
        self.baseline_len = baseline_len
        self.verified_findings: list[VerifiedFinding] = []
        self.rejected_findings: list[VerifiedFinding] = []

    def verify(self, finding: VulnerabilityFinding) -> VerifiedFinding:
        """Verify one finding and store the classified result."""
        verified = VerifiedFinding(original_finding=finding)
        poc_code = PoCGenerator.generate_poc(
            finding,
            target=self.target,
            baseline_len=self.baseline_len,
        )
        verified.poc_code = poc_code

        returncode, output = VerifierExecutor.execute_poc(poc_code)
        verified.poc_output = output
        verified.poc_executed_at = datetime.now().isoformat()

        result = VerifierExecutor.parse_result(output, returncode)
        verified.result = result

        if result in {
            VerificationResult.VULN_CONFIRMED,
            VerificationResult.SENSITIVE_DATA_EXPOSED,
            VerificationResult.SECURITY_BYPASS,
        }:
            verified.status = VerificationStatus.VERIFIED
            self._build_verified_finding(verified, output)
            self.verified_findings.append(verified)
        else:
            verified.status = VerificationStatus.REJECTED
            self._build_rejected_finding(verified, result)
            self.rejected_findings.append(verified)

        return verified

    def verify_batch(self, findings: list[VulnerabilityFinding]) -> list[VerifiedFinding]:
        """Verify findings and return only verified entries."""
        verified_results: list[VerifiedFinding] = []
        for finding in findings:
            result = self.verify(finding)
            if result.status == VerificationStatus.VERIFIED:
                verified_results.append(result)
        return verified_results

    def _build_verified_finding(self, vf: VerifiedFinding, output: str) -> None:
        """Populate English verified finding details."""
        original = vf.original_finding
        confirmation_lines = [
            line for line in output.splitlines() if "[CONFIRMED]" in line or "[POSSIBLE]" in line
        ]
        vf.verified_description = (
            f"PoC verification confirmed the finding. Original description: {original.description}"
            if original.description
            else "PoC verification confirmed the finding."
        )
        vf.verified_evidence = "\n".join(confirmation_lines) or output[:500]
        vf.verified_severity = original.severity

    def _build_rejected_finding(
        self,
        vf: VerifiedFinding,
        result: VerificationResult,
    ) -> None:
        """Populate English rejection details."""
        reasons = {
            VerificationResult.FALSE_POSITIVE: "PoC execution did not detect vulnerability indicators.",
            VerificationResult.NO_RESPONSE_DIFF: "The response did not differ enough to support the hypothesis.",
            VerificationResult.PARAM_INVALID: "The parameter appears invalid and the hypothesis could not be verified.",
            VerificationResult.NORMAL_RESPONSE: "The target returned normal behavior.",
            VerificationResult.TIMEOUT: "PoC execution timed out.",
            VerificationResult.ERROR_403_404: "The request was rejected or the resource was not found.",
        }
        vf.rejection_reason = reasons.get(result, f"Verification failed: {result.value}")
        print(
            f"[VERIFIER] Excluding finding: {vf.original_finding.title} | "
            f"Reason: {vf.rejection_reason}"
        )

    def get_verified_report_findings(self) -> list[VulnerabilityFinding]:
        """Return verified findings converted back to report-ready objects."""
        report_findings: list[VulnerabilityFinding] = []
        for vf in self.verified_findings:
            if vf.status != VerificationStatus.VERIFIED:
                continue
            original = vf.original_finding
            original.verified = True
            original.description = vf.verified_description or original.description
            original.evidence = vf.verified_evidence or original.evidence
            if vf.verified_severity:
                original.severity = vf.verified_severity
            report_findings.append(original)
        return report_findings

    def get_summary(self) -> dict[str, Any]:
        """Return verification counters."""
        return {
            "verified": len(self.verified_findings),
            "rejected": len(self.rejected_findings),
            "total": len(self.verified_findings) + len(self.rejected_findings),
            "verified_titles": [vf.original_finding.title for vf in self.verified_findings],
            "rejected_titles": [vf.original_finding.title for vf in self.rejected_findings],
        }
