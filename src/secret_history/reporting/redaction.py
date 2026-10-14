import hashlib

from secret_history.detectors import github, google, slack


def safe_path(path, values=()):
    masked = path
    for value in sorted(set(values), key=len, reverse=True):
        if value:
            masked = masked.replace(value, "[REDACTED]")
    for pattern in (github.PATTERN, google.PATTERN, slack.PATTERN):
        masked = pattern.sub("[REDACTED]", masked)
    if masked != path:
        digest = hashlib.sha256(path.encode("utf-8", "surrogatepass")).hexdigest()[:16]
        return masked + "~" + digest
    return path
