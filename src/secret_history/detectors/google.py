import re

from secret_history.baselines.aws_rules import Decision
from secret_history.detectors.common import extract_tokens, nonsecret


PATTERN = re.compile(r"(?<![A-Za-z0-9_])AIza[A-Za-z0-9_-]{10,}(?![A-Za-z0-9_-])")
KEY = re.compile(r"AIza[A-Za-z0-9_-]{35}\Z")
PUBLIC_EXAMPLES = frozenset({"YOUR_API_KEY"})
PLACEHOLDERS = frozenset({"your_google_api_key", "<your_api_key>", "replace_me", "changeme"})


def extract(text):
    return extract_tokens(text, "google", PATTERN, ("GOOGLE_API_KEY", "GOOGLE_MAPS_API_KEY", "GEMINI_API_KEY"))


def classify(candidate):
    value = candidate.bindings[0].value
    return nonsecret(value, PLACEHOLDERS, PUBLIC_EXAMPLES) or Decision(
        "UNCERTAIN", "google_api_key_requires_usage_and_restriction_review" if KEY.fullmatch(value) else "unexpected_google_api_key_format"
    )
