import re
from typing import Dict, List


URGENT_WORDS = [
    "urgent", "immediately", "asap", "now", "right away",
    "quickly", "promptly", "without delay"
]

SECRECY_WORDS = [
    "confidential", "secret", "private", "discreet",
    "do not tell", "keep this between us"
]

FINANCIAL_WORDS = [
    "transfer", "payment", "bank", "account", "invoice",
    "wire", "funds", "transaction", "gift card"
]

IMPERSONATION_WORDS = [
    "ceo", "director", "manager", "boss", "i need you",
    "on behalf of", "this is to instruct", "kindly handle"
]

CREDENTIAL_WORDS = [
    "password", "login", "verify", "otp", "code", "credentials"
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def domain_from_email(email: str) -> str:
    if "@" not in email:
        return ""
    return email.split("@")[-1].strip().lower()


def count_matches(text: str, keyword_list: List[str]) -> List[str]:
    found = []
    for word in keyword_list:
        if word in text:
            found.append(word)
    return found


def analyze_email(sender_email: str, subject: str, body: str, expected_domain: str = "") -> Dict:
    combined_text = clean_text(f"{subject} {body}")
    score = 0
    triggered = []

    urgent_hits = count_matches(combined_text, URGENT_WORDS)
    secrecy_hits = count_matches(combined_text, SECRECY_WORDS)
    financial_hits = count_matches(combined_text, FINANCIAL_WORDS)
    impersonation_hits = count_matches(combined_text, IMPERSONATION_WORDS)
    credential_hits = count_matches(combined_text, CREDENTIAL_WORDS)

    if urgent_hits:
        score += 10
        triggered.append(f"Urgency indicators detected: {', '.join(urgent_hits[:4])}")

    if secrecy_hits:
        score += 10
        triggered.append(f"Secrecy indicators detected: {', '.join(secrecy_hits[:4])}")

    if financial_hits:
        score += 15
        triggered.append(f"Financial request indicators detected: {', '.join(financial_hits[:4])}")

    if impersonation_hits:
        score += 15
        triggered.append(f"Authority or impersonation language detected: {', '.join(impersonation_hits[:4])}")

    if credential_hits:
        score += 15
        triggered.append(f"Credential related indicators detected: {', '.join(credential_hits[:4])}")

    sender_domain = domain_from_email(sender_email)
    if expected_domain and sender_domain and sender_domain != expected_domain.lower():
        score += 20
        triggered.append(
            f"Sender domain mismatch detected. Sender domain is '{sender_domain}' but expected domain is '{expected_domain.lower()}'."
        )

    exclamation_count = body.count("!")
    if exclamation_count >= 3:
        score += 5
        triggered.append("Excessive punctuation detected, which may indicate pressure tactics.")

    if len(body.split()) < 8:
        score += 5
        triggered.append("Very short message body detected, which may hide context or intent.")

    suspicious_phrases = [
        "kindly do the needful",
        "send it now",
        "i need this done",
        "keep this confidential",
        "purchase gift cards",
        "reply urgently"
    ]

    phrase_hits = count_matches(combined_text, suspicious_phrases)
    if phrase_hits:
        score += 10
        triggered.append(f"Suspicious scam style phrases detected: {', '.join(phrase_hits[:4])}")

    return {
        "score": min(score, 100),
        "sender_domain": sender_domain,
        "triggered_indicators": triggered,
        "urgent_hits": urgent_hits,
        "secrecy_hits": secrecy_hits,
        "financial_hits": financial_hits,
        "impersonation_hits": impersonation_hits,
        "credential_hits": credential_hits,
    }