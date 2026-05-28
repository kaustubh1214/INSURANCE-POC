"""
PII Masker — strips Personally Identifiable Information before any AI/LLM call.
MANDATORY: all text going to an LLM must pass through this first.

Masks:
- Full names → [NAME_REDACTED]
- Aadhaar numbers → XXXX-XXXX-XXXX
- PAN numbers → XXXXX####X
- Phone numbers → +91XXXXXXX####
- Email addresses → [EMAIL_REDACTED]
- Dates of birth → [DOB_REDACTED]
- Street addresses → [ADDRESS_REDACTED]
"""
import hashlib
import re


# ---------------------------------------------------------------------------
# Regex Patterns
# ---------------------------------------------------------------------------
PATTERNS = {
    "aadhaar": (
        re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
        "XXXX-XXXX-XXXX",
    ),
    "pan": (
        re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
        "XXXXX####X",
    ),
    "phone_in": (
        re.compile(r"(\+91[\s-]?)?[6-9]\d{9}"),
        "+91XXXXXXX####",
    ),
    "email": (
        re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        "[EMAIL_REDACTED]",
    ),
    "dob_slash": (
        re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
        "[DOB_REDACTED]",
    ),
    "dob_dash": (
        re.compile(r"\b\d{1,2}-\d{1,2}-\d{2,4}\b"),
        "[DOB_REDACTED]",
    ),
}


def mask_pii(text: str) -> str:
    """
    Apply all PII masking patterns to the given text.

    Args:
        text: Raw text that may contain PII

    Returns:
        Text with PII replaced by safe placeholders

    Example:
        mask_pii("Patient John Doe, Aadhaar: 1234 5678 9012, email: john@example.com")
        → "Patient John Doe, Aadhaar: XXXX-XXXX-XXXX, email: [EMAIL_REDACTED]"
    """
    if not text:
        return text

    masked = text
    for pattern_name, (pattern, replacement) in PATTERNS.items():
        masked = pattern.sub(replacement, masked)

    return masked


def hash_prompt(text: str) -> str:
    """
    Generate SHA-256 hash of text for audit logging.
    Used to detect duplicate prompts without storing raw PII.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mask_dict(data: dict) -> dict:
    """
    Recursively mask PII in a dictionary.
    Use before logging or sending structured data to AI.
    """
    if not data:
        return data

    masked = {}
    PII_FIELD_NAMES = {
        "name", "full_name", "email", "phone", "aadhaar", "aadhaar_number",
        "pan", "pan_number", "dob", "date_of_birth", "address",
        "address_line1", "address_line2",
    }

    for key, value in data.items():
        if key.lower() in PII_FIELD_NAMES:
            masked[key] = "[REDACTED]"
        elif isinstance(value, str):
            masked[key] = mask_pii(value)
        elif isinstance(value, dict):
            masked[key] = mask_dict(value)
        elif isinstance(value, list):
            masked[key] = [
                mask_dict(item) if isinstance(item, dict) else
                mask_pii(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            masked[key] = value

    return masked
