"""VulnBot Skill Dispatcher: match user intents to appropriate Skills."""

from __future__ import annotations

from typing import Any, Optional

from vulnbot.skills.loader import list_core_skills, list_specialized_skills, load_skill_by_name

SKILL_INTENT_MAP: dict[str, list[str]] = {
    # Core skills
    "penetration test|pentest|full workflow|end to end test|authorized test": ["pentest-flow"],
    "information gathering|recon|reconnaissance|port scan|scan ports|subdomain": ["recon"],
    "vulnerability discovery|vulnerability scan|vulnerability|find vulnerabilities": [
        "vuln-discovery"
    ],
    "exploit|exploitation|poc|proof of concept": ["exploitation"],
    "post-exploitation|post exploitation|internal discovery": ["post-exploitation"],
    "report|generate report|write report|findings report": ["reporting"],
    "waf bypass|bypass waf|firewall bypass": ["waf-bypass"],
    # Specialized skills
    "web pentest|web test|website test|web application test": ["web-pentest"],
    "android|apk|mobile app test|app pentest": ["android-pentest"],
    "reverse|signature recovery|burp replay|js signature|client reverse|request chain|replay|signature": [
        "client-reverse"
    ],
    "packet capture|frida|jadx|hook|ssl pinning|scrcpy": ["client-reverse"],
    "browser signature|anti-bot|antibot|token generation|cookie redirect": ["client-reverse"],
    "advanced web|injection|sql injection|xss|ssrf|ssti|xxe|command injection|deserialization|rce|remote code execution": [
        "web-security-advanced"
    ],
    "cors|graphql|websocket|oauth|request smuggling|jwt|csrf|prototype pollution": [
        "web-security-advanced"
    ],
    "authentication vulnerability|logic vulnerability|access control|idor|payment logic|file upload|path traversal": [
        "web-security-advanced"
    ],
    "ai security|mcp security|prompt injection|tool abuse|agent security|model security": [
        "ai-mcp-security"
    ],
    "ai pentest|llm security|large language model security|prompt injection|tool abuse": [
        "ai-mcp-security"
    ],
    "mcp poisoning|skills supply chain|role escape|data leakage|prompt leakage": [
        "ai-mcp-security"
    ],
    "intranet pentest|lateral movement|privilege escalation|persistence|tunnel|proxy|domain pentest|ad attack": [
        "intranet-pentest-advanced"
    ],
    "adcs|exchange|sharepoint|mimikatz|kerberoasting|dcsync|pth": [
        "intranet-pentest-advanced"
    ],
    "credential theft|bloodhound|frp|chisel|ligolo|amsi bypass": [
        "intranet-pentest-advanced"
    ],
    "tool|command|encode|decode|reverse shell|password attack|hashcat": ["pentest-tools"],
    "sqlmap|nmap|nuclei|ffuf|burp|impacket|crackmapexec": ["pentest-tools"],
    "quick reference|payload|bypass reminder|quick validation|checklist": ["rapid-checklist"],
    "payload list|bypass|quick lookup|cheat sheet|quick recall": ["rapid-checklist"],
    # SecKnowledge: practical CTF/SRC/Web+AI security testing knowledge base
    "src|vulnerability research|bug bounty|edusrc|cnvd": ["secknowledge-skill"],
    "wooyun|l1-l4|gaarm|owasp wstg|owasp llm|owasp asi": ["secknowledge-skill"],
    "practical security testing|security testing knowledge base|web+ai|web ai security|ai application security testing": [
        "secknowledge-skill"
    ],
    "ctf src|ctf vulnerability research|ctf integrated pentest|ctf ai|ctf mcp|ctf agent": [
        "secknowledge-skill"
    ],
    # Crypto toolkit
    "encoding|decoding|base64|base32|hex|url encoding|encrypt|decrypt|hash": ["crypto-toolkit"],
    "md5|sha|aes|des|rsa|jwt|rot13|caesar|morse|rail fence": ["crypto-toolkit"],
    "base64 decode|base64 encode|hex decode|url decode|unicode decode|html decode": [
        "crypto-toolkit"
    ],
    "cryptography|crypto|cipher|decrypt|encrypt|encode|decode": ["crypto-toolkit"],
    "morse code|caesar cipher|vigenere|bacon cipher|base58": ["crypto-toolkit"],
    # CTF specialized skills
    "ctf|capture the flag|flag|weak comparison|space bypass|regex bypass|rce|code audit|eval bypass|highlight_file": [
        "ctf-web"
    ],
    "0e|md5 bypass|preg_match bypass|type bypass|type juggling|weak typing": ["ctf-web"],
    "echo output|blind rce|command execution bypass|php code audit|ssti injection": ["ctf-web"],
    "rsa attack|small exponent|common modulus|wiener|coppersmith|padding oracle": [
        "ctf-crypto"
    ],
    "ecc attack|small subgroup|discrete logarithm|ecdsa|ed25519|pohlig-hellman": [
        "ctf-crypto"
    ],
    "lfsr|lcg|prng|mt19937|random prediction|stream cipher": ["ctf-crypto"],
    "lwe|lattice attack|lll|cvp|svp|lattice reduction": ["ctf-crypto"],
    "classic cipher|vigenere|caesar|rail fence|substitution cipher|frequency analysis": [
        "ctf-crypto"
    ],
    "pyjail|python sandbox|jail escape|sandbox_escape|python jail": ["ctf-misc"],
    "bashjail|bash sandbox|restricted shell|rbash escape": ["ctf-misc"],
    "encoding chain|multi-layer encoding|misc|stego|steganography": ["ctf-misc"],
    "ctfd|flag platform|flag submission|challenge download": ["ctf-misc"],
    # OSINT specialized skill
    "social engineering|osint|author tracking|person tracking|target profile|persona profile": [
        "osint-recon"
    ],
    "cross-platform|username search|identity correlation|github tracking|bilibili tracking": [
        "osint-recon"
    ],
    "full recon|deep recon|complete information gathering|comprehensive recon|deep collection|collect baseline information": [
        "osint-recon"
    ],
}


class SkillDispatcher:
    """Dispatches user input to the most appropriate Skill."""

    def dispatch(self, user_input: str) -> Optional[dict[str, Any]]:
        """Match user input to a Skill and load it.

        Args:
            user_input: Natural language input from the user.

        Returns:
            Loaded skill dict, or None if no match found.
        """
        input_lower = user_input.lower()

        scores: dict[str, float] = {}

        for pattern, skill_names in SKILL_INTENT_MAP.items():
            keywords = pattern.split("|")
            match_count = sum(1 for kw in keywords if kw in input_lower)
            if match_count > 0:
                for skill_name in skill_names:
                    score = match_count / len(keywords)
                    skill = load_skill_by_name(skill_name)
                    if skill and skill.get("format") == "directory":
                        score *= 1.5
                    scores[skill_name] = scores.get(skill_name, 0) + score

        if not scores:
            return load_skill_by_name("pentest-flow")

        best_skill_name = max(scores, key=scores.get)  # type: ignore[arg-type]
        return load_skill_by_name(best_skill_name)

    def list_all_skills(self) -> list[dict[str, str]]:
        """List all available skills with name and description."""
        skills = []
        for name in list_core_skills():
            skill = load_skill_by_name(name)
            if skill:
                skills.append(
                    {
                        "name": skill["name"],
                        "description": skill.get("description", ""),
                        "type": "core",
                        "format": skill.get("format", "flat"),
                        "references": str(len(skill.get("references", []))),
                    }
                )
        for name in list_specialized_skills():
            skill = load_skill_by_name(name)
            if skill:
                skills.append(
                    {
                        "name": skill["name"],
                        "description": skill.get("description", ""),
                        "type": "specialized",
                        "format": skill.get("format", "flat"),
                        "references": str(len(skill.get("references", []))),
                    }
                )
        return skills
