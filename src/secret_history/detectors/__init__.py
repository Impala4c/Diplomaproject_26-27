from pathlib import PurePosixPath

from secret_history.baselines.aws_rules import classify_aws
from secret_history.candidates.aws import extract_aws
from secret_history.detectors import github, google, pem, slack


DETECTORS = {"github": github, "pem": pem, "slack": slack, "google": google}
ALL = ("aws", *DETECTORS)
CATEGORIES = {"aws": "AWS credentials", "github": "GitHub token", "pem": "PEM private key", "slack": "Slack token", "google": "Google API key"}
RULES_VERSION = "multi-provider-v1"


def is_env_path(path):
    name = PurePosixPath(path).name
    return name == ".env" or name.startswith(".env.")


def selected_detectors(selection):
    names = ALL if selection == "all" else tuple(selection.split(",")) if isinstance(selection, str) else tuple(selection)
    if not names or any(name not in ALL for name in names):
        raise ValueError("Unknown detector selection.")
    return tuple(name for name in ALL if name in names)


def extract(text, path, selection):
    candidates, warnings = [], []
    for name in selection:
        if name == "aws":
            found, issues = extract_aws(text) if is_env_path(path) else ([], [])
        else:
            found, issues = DETECTORS[name].extract(text)
        candidates.extend(found)
        warnings.extend(issues)
    return candidates, warnings


def classify(candidate):
    return classify_aws(candidate) if candidate.detector == "aws" else DETECTORS[candidate.detector].classify(candidate)
