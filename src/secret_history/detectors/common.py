import re

from secret_history.baselines.aws_rules import Decision, REFERENCE
from secret_history.candidates.aws import Binding, Candidate, ParseWarning, parse_value


TEMPLATE_REFERENCE = re.compile(r"\$\{\{\s*[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\s*\}\}\Z")


def extract_tokens(text, detector, pattern, fields):
    candidates = []
    warnings = []
    spans = []
    for match in pattern.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        column = match.start() - text.rfind("\n", 0, match.start())
        candidates.append(Candidate((Binding(detector, match[0], line, column=column),), detector=detector))
        spans.append((match.start(), match.end()))
    assignment = re.compile(r"^\s*(?:#\s*)?(?:export\s+)?(?:" + "|".join(fields) + r")\s*[:=]\s*(.*)$", re.I)
    offset = 0
    for line, content in enumerate(text.splitlines(keepends=True), 1):
        match = assignment.match(content.rstrip("\r\n"))
        if match and not any(start < offset + len(content) and end > offset for start, end in spans):
            rhs = match[1].rstrip(",;").strip()
            value = rhs if TEMPLATE_REFERENCE.fullmatch(rhs) else parse_value(rhs)
            if value is None:
                warnings.append(ParseWarning(line, "unsupported_token_assignment"))
            else:
                candidates.append(Candidate((Binding(detector, value, line, column=match.start(1) + 1),), detector=detector))
        offset += len(content)
    return sorted(candidates, key=lambda c: (c.bindings[0].line, c.bindings[0].column)), warnings


def nonsecret(value, placeholders, examples):
    if value in examples:
        return Decision("NON_SECRET", "exact_public_documentation_example")
    if not value or REFERENCE.fullmatch(value) or TEMPLATE_REFERENCE.fullmatch(value) or value.casefold() in placeholders:
        return Decision("NON_SECRET", "empty_placeholder_or_reference")
    return None
