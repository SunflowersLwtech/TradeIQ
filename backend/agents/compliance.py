# Post-generation compliance filter (Design Doc Section 14)
import re

BLOCKLIST = {"guaranteed", "moon", "easy money", "get rich", "sure thing"}
DISCLAIMER = "📊 Analysis by TradeIQ | Not financial advice"


def check_compliance(text: str) -> tuple[bool, list[str]]:
    """Return (passed, list of violations)."""
    violations = []
    lower = text.lower()
    for word in BLOCKLIST:
        if word in lower:
            violations.append(f"Blocklisted term: {word}")
    if re.search(r"\b(will (hit|reach|go to)|price (will|going to))\b", lower):
        violations.append("Prediction language detected")
    return (len(violations) == 0, violations)


def append_disclaimer(text: str) -> str:
    return f"{text}\n\n{DISCLAIMER}"
