"""Clean raw LLM output into report-ready Markdown."""

from __future__ import annotations

import re
from typing import Optional


class ReportContentFilter:
    """Extract clean report text from raw model output."""

    TOOL_CALL_PATTERNS = [
        re.compile(r"<tool_call>.*?</tool_call>", re.DOTALL | re.IGNORECASE),
        re.compile(r"TOOL_CALL\s*:.*?(?=\n\n|\Z)", re.DOTALL | re.IGNORECASE),
        re.compile(r"tool\s*=>\s*\w+.*?(?=\n\n|\Z)", re.DOTALL | re.IGNORECASE),
        re.compile(r"python_execute\s*\(.*?\)", re.DOTALL | re.IGNORECASE),
        re.compile(r"nmap_scan\s*\(.*?\)", re.DOTALL | re.IGNORECASE),
        re.compile(r"fetch\s*\(.*?\)", re.DOTALL | re.IGNORECASE),
        re.compile(r"^\s*\w+_tool\s*\(.*?\)\s*$", re.MULTILINE | re.IGNORECASE),
        re.compile(r"tool_call\s*[:=].*?(?=\n\n|\Z)", re.DOTALL | re.IGNORECASE),
    ]

    ROUND_MARKERS = [
        re.compile(r"--\s*Cycle\s*\d+\s*\|\s*Round\s*\d+\s*--", re.DOTALL),
        re.compile(r"--\s*Round\s*\d+\s*--", re.DOTALL),
        re.compile(r"Round\s*\d+\s*/\s*\d+", re.IGNORECASE),
        re.compile(r"Cycle\s*\d+", re.IGNORECASE),
    ]

    THINK_PATTERNS = [
        re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE),
        re.compile(r"<thinking>.*?</thinking>", re.DOTALL | re.IGNORECASE),
        re.compile(r"```thinking.*?```", re.DOTALL | re.IGNORECASE),
        re.compile(r"##\s*Thinking\s*", re.IGNORECASE),
        re.compile(r"###\s*Reasoning\s*", re.IGNORECASE),
    ]

    PYTHON_CODE_PATTERNS = [
        re.compile(r"```python\s*\n.*?```", re.DOTALL | re.IGNORECASE),
        re.compile(r"```\s*\n(import|from|print|with|def |class ).*?```", re.DOTALL | re.IGNORECASE),
        re.compile(r"^\s*print\s*\(.*?\)\s*$", re.MULTILINE),
        re.compile(r"^\s*(import|from)\s+[\w.]+.*$", re.MULTILINE),
        re.compile(r"^\s*with\s+open\s*\(.*$", re.MULTILINE),
    ]

    DEBUG_PATTERNS = [
        re.compile(r"^\s*--.*--\s*$", re.MULTILINE),
        re.compile(r"^\s*\[=\]+\s*$", re.MULTILINE),
        re.compile(r"tool call|tool_call|tool result", re.IGNORECASE),
        re.compile(r"\[LLM\s+[A-Z_]+\]", re.IGNORECASE),
        re.compile(r"\[debug\].*?$", re.MULTILINE | re.IGNORECASE),
    ]

    PHASE_PATTERNS = [
        re.compile(r"phase\s+change\s*[-=]>\s*\w+", re.IGNORECASE),
        re.compile(r"entering\s+\w+\s+phase", re.IGNORECASE),
        re.compile(r"current\s+phase:\s*\w+", re.IGNORECASE),
    ]

    @classmethod
    def filter(cls, content: str) -> str:
        """Filter content and keep only clean report Markdown."""
        if not content:
            return ""
        result = content
        result = cls._remove_tool_calls(result)
        result = cls._remove_round_markers(result)
        result = cls._remove_think_tags(result)
        result = cls._remove_python_code(result)
        result = cls._remove_debug_output(result)
        result = cls._remove_phase_markers(result)
        result = cls._cleanup_whitespace(result)
        return result.strip()

    @classmethod
    def _remove_tool_calls(cls, content: str) -> str:
        """Remove tool-call markup and inline tool invocations."""
        result = content
        for pattern in cls.TOOL_CALL_PATTERNS:
            result = pattern.sub("", result)
        lines = []
        skip_block = False
        for line in result.splitlines():
            lowered = line.lower()
            if "tool_call" in lowered or "tool call" in lowered:
                skip_block = True
                continue
            if skip_block and not line.strip():
                skip_block = False
                continue
            if not skip_block:
                lines.append(line)
        return "\n".join(lines)

    @classmethod
    def _remove_round_markers(cls, content: str) -> str:
        """Remove loop and round markers."""
        result = content
        for pattern in cls.ROUND_MARKERS:
            result = pattern.sub("", result)
        return result

    @classmethod
    def _remove_think_tags(cls, content: str) -> str:
        """Remove model reasoning tags and thinking sections."""
        result = content
        for pattern in cls.THINK_PATTERNS:
            result = pattern.sub("", result)
        return result

    @classmethod
    def _remove_python_code(cls, content: str) -> str:
        """Remove raw Python execution blocks from model output."""
        result = content
        for pattern in cls.PYTHON_CODE_PATTERNS:
            result = pattern.sub("", result)

        filtered_lines = []
        in_code_block = False
        for line in result.splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                filtered_lines.append(line)
                continue
            if in_code_block:
                filtered_lines.append(line)
                continue
            if re.match(r"^(response|result|data)\s*=", stripped):
                continue
            if re.match(r"^(print|open|requests\.)\s*\(", stripped):
                continue
            filtered_lines.append(line)
        return "\n".join(filtered_lines)

    @classmethod
    def _remove_debug_output(cls, content: str) -> str:
        """Remove debug markers and tool-result prefixes."""
        result = content
        for pattern in cls.DEBUG_PATTERNS:
            result = pattern.sub("", result)
        result = re.sub(r"\[result\]\s*:?\s*", "", result, flags=re.IGNORECASE)
        result = re.sub(r"\[output\]\s*:?\s*", "", result, flags=re.IGNORECASE)
        return result

    @classmethod
    def _remove_phase_markers(cls, content: str) -> str:
        """Remove phase-transition markers."""
        result = content
        for pattern in cls.PHASE_PATTERNS:
            result = pattern.sub("", result)
        return result

    @classmethod
    def _cleanup_whitespace(cls, content: str) -> str:
        """Normalize excess blank lines and trailing spaces."""
        result = re.sub(r"\n{3,}", "\n\n", content)
        result = "\n".join(line.rstrip() for line in result.splitlines())
        return result.strip()

    @classmethod
    def is_pure_markdown(cls, content: str) -> bool:
        """Return whether content appears free of execution noise."""
        noise_patterns = [
            r"tool_call",
            r"TOOL_CALL",
            r"<think>",
            r"python_execute",
            r"--\s*Round",
            r"--\s*Cycle",
            r"\[LLM\s+",
        ]
        return not any(re.search(pattern, content, re.IGNORECASE) for pattern in noise_patterns)


def filter_report_content(content: str) -> str:
    """Filter report content to clean Markdown."""
    return ReportContentFilter.filter(content)


def deduplicate_report_findings(findings: list, threshold: float = 0.75) -> list:
    """Deduplicate report findings using semantic similarity."""
    from vulnbot.agent.finding_similarity import deduplicate_findings

    return deduplicate_findings(findings, threshold=threshold)


def extract_findings_section(content: str) -> Optional[str]:
    """Extract the findings section from a Markdown report."""
    patterns = [
        r"(##\s*Findings\s*\n[\s\S]*?)(?=##|\Z)",
        r"(##\s*Detailed Findings\s*\n[\s\S]*?)(?=##|\Z)",
        r"(##\s*Vulnerabilities\s*\n[\s\S]*?)(?=##|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def remove_unverified_findings(content: str) -> str:
    """Remove report sections and lines marked as unverified."""
    result = re.sub(
        r"(###\s*\[[^\]]*\]\s*[^\n]*unverified[^\n]*\n[\s\S]*?)(?=###|\Z)",
        "",
        content,
        flags=re.IGNORECASE,
    )
    lines = []
    skip_section = False
    for line in result.splitlines():
        lower = line.lower()
        if "[unverified]" in lower and line.strip().startswith("###"):
            skip_section = True
            continue
        if skip_section and line.strip().startswith("###"):
            skip_section = False
        if not skip_section and "[unverified]" not in lower:
            lines.append(line)
    return "\n".join(lines)
