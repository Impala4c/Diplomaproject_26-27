import re

from secret_history.baselines.aws_rules import Decision
from secret_history.detectors.common import extract_tokens, nonsecret


PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9_.-]{10,}|github_pat_[A-Za-z0-9_]{10,})(?![A-Za-z0-9_])")
CLASSIC = re.compile(r"gh[pousr]_[A-Za-z0-9]{36}\Z")
FINE_GRAINED = re.compile(r"github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}\Z")
STATELESS = re.compile(r"ghs_[A-Za-z0-9]+_[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\Z")
PUBLIC_EXAMPLES = frozenset({"YOUR-TOKEN"})
PLACEHOLDERS = frozenset({"your_github_token", "your_token_here", "<your-token>", "replace_me", "changeme"})


def extract(text):
    return extract_tokens(text, "github", PATTERN, ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"))


def classify(candidate):
    value = candidate.bindings[0].value
    return nonsecret(value, PLACEHOLDERS, PUBLIC_EXAMPLES) or Decision(
        "SUSPECTED_SECRET" if any(pattern.fullmatch(value) for pattern in (CLASSIC, FINE_GRAINED, STATELESS)) else "UNCERTAIN",
        "github_token_shape_without_online_validation",
    )
