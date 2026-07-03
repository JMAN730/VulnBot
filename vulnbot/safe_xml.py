"""Safe XML parsing helpers (SEC-6)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any


def parse_xml_string(text: str) -> Any:
    """Parse XML with defusedxml when available, else stdlib ElementTree."""
    try:
        from defusedxml.ElementTree import fromstring as safe_fromstring
    except ImportError:
        safe_fromstring = ET.fromstring
    return safe_fromstring(text)
