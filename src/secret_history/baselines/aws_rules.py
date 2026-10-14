
from dataclasses import dataclass
import re

from secret_history.candidates.aws import Candidate, ID_FIELD, SECRET_FIELD

RULES_VERSION = "aws-env-v1"
ACCESS_ID = re.compile(r"AKIA[A-Z0-9]{16}\Z")
TEMPORARY_ID = re.compile(r"ASIA[A-Z0-9]{16}\Z")
SECRET_VALUE = re.compile(r"[A-Za-z0-9/+=]{40}\Z")
REFERENCE = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*|\{[A-Za-z_][A-Za-z0-9_]*\})\Z")
AWS_EXAMPLE = ("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
PLACEHOLDERS = frozenset({
    "your_access_key_here", "your_secret_key_here", "your_access_key_id",
    "your_secret_access_key", "<aws_access_key_id>", "<aws_secret_access_key>",
    "<your_access_key_id>", "<your_secret_access_key>", "changeme", "replace_me",
})


@dataclass(frozen=True)
class Decision:
    status: str
    reason: str


def nonliteral_reason(value: str) -> str | None:
    if not value:
        return "empty_value"
    if REFERENCE.fullmatch(value):
        return "environment_reference"
    if value.casefold() in PLACEHOLDERS:
        return "explicit_placeholder"
    return None


def classify_aws(candidate: Candidate) -> Decision:
    if candidate.ambiguous:
        return Decision("UNCERTAIN", "ambiguous_bindings")
    values = {binding.name: binding.value for binding in candidate.bindings}
    identifier = values.get(ID_FIELD)
    secret = values.get(SECRET_FIELD)
    if (identifier, secret) == AWS_EXAMPLE:
        return Decision("NON_SECRET", "exact_aws_documentation_example")
    reasons = [nonliteral_reason(b.value) for b in candidate.bindings]
    if all(reasons):
        return Decision("NON_SECRET", "only_empty_placeholders_or_references")
    if identifier and TEMPORARY_ID.fullmatch(identifier):
        return Decision("UNCERTAIN", "temporary_credentials_out_of_scope")
    if secret is not None and not nonliteral_reason(secret):
        if not SECRET_VALUE.fullmatch(secret):
            return Decision("UNCERTAIN", "unexpected_secret_format")
        if identifier and ACCESS_ID.fullmatch(identifier):
            return Decision("SUSPECTED_SECRET", "literal_aws_pair")
        if identifier is None or nonliteral_reason(identifier):
            return Decision("SUSPECTED_SECRET", "secret_component_without_literal_id")
        return Decision("UNCERTAIN", "unexpected_access_id_format")
    if identifier and ACCESS_ID.fullmatch(identifier):
        return Decision("INCOMPLETE", "access_id_without_secret_value")
    return Decision("UNCERTAIN", "unexpected_access_id_format")
