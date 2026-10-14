import base64
import binascii
import hashlib
import re

from secret_history.baselines.aws_rules import Decision
from secret_history.candidates.aws import Binding, Candidate


BEGIN = re.compile(r"(?m)^[ \t]*-----BEGIN ((?:RSA |EC |DSA |ENCRYPTED |OPENSSH )?PRIVATE KEY)-----[ \t]*\r?$")
PLACEHOLDERS = frozenset({"...", "<private key>", "<your private key>", "your_private_key_here",
                          "<synthetic_body_not_a_valid_private_key>"})
RFC7468_FIGURE12_BODY_SHA256 = "4da7fdf4c2621d8da655561b9480d4c41ba6d13b6854ca2143b3155506b9ea59"


def extract(text):
    candidates = []
    starts = list(BEGIN.finditer(text))
    for index, match in enumerate(starts):
        boundary = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        end_pattern = re.compile(r"(?m)^[ \t]*-----END " + re.escape(match[1]) + r"-----[ \t]*\r?$")
        end = end_pattern.search(text, match.end(), boundary)
        stop = end.end() if end else boundary
        line = text.count("\n", 0, match.start()) + 1
        end_line = text.count("\n", 0, stop) + 1
        binding = Binding("pem", text[match.start():stop], line, end_line=end_line, column=1)
        candidates.append(Candidate((binding,), ambiguous=end is None, detector="pem"))
    return candidates, []


def classify(candidate):
    value = candidate.bindings[0].value
    if candidate.ambiguous:
        return Decision("UNCERTAIN", "unterminated_private_key_block")
    lines = value.strip().splitlines()
    body = "".join(line.strip() for line in lines[1:-1])
    if lines[0].strip() == "-----BEGIN PRIVATE KEY-----" and hashlib.sha256(body.encode("utf-8")).hexdigest() == RFC7468_FIGURE12_BODY_SHA256:
        return Decision("NON_SECRET", "exact_rfc7468_figure12_public_example")
    if body.casefold() in PLACEHOLDERS:
        return Decision("NON_SECRET", "explicit_pem_placeholder")
    try:
        decoded = base64.b64decode(body, validate=True)
    except (ValueError, binascii.Error):
        decoded = b""
    if decoded.startswith(b"\x30") or decoded.startswith(b"openssh-key-v1\0"):
        return Decision("SUSPECTED_SECRET", "private_key_envelope_without_cryptographic_validation")
    return Decision("UNCERTAIN", "private_key_envelope_unrecognized_body")
