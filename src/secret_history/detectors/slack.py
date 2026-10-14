import re

from secret_history.baselines.aws_rules import Decision
from secret_history.detectors.common import extract_tokens, nonsecret


PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?:xox[baprs]-[A-Za-z0-9-]{10,}|xapp-[A-Za-z0-9-]{10,})(?![A-Za-z0-9_-])")
TOKEN = re.compile(r"(?:xoxb-\d{8,15}-\d{8,15}-[A-Za-z0-9]{20,}|xoxp-\d{8,15}-\d{8,15}-\d{8,15}-[A-Za-z0-9]{20,}|xapp-\d+-[A-Za-z0-9]+-\d+-[A-Za-z0-9]{20,})\Z")
PUBLIC_EXAMPLES = frozenset({"xoxb-XXXXXXXXXXXX-TTTTTTTTTTTTTT"})
PLACEHOLDERS = frozenset({"your_slack_token", "your_token_here", "<your-slack-token>", "replace_me", "changeme"})


def extract(text):
    return extract_tokens(text, "slack", PATTERN, ("SLACK_TOKEN", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "SLACK_APP_TOKEN"))


def classify(candidate):
    value = candidate.bindings[0].value
    return nonsecret(value, PLACEHOLDERS, PUBLIC_EXAMPLES) or Decision(
        "SUSPECTED_SECRET" if TOKEN.fullmatch(value) else "UNCERTAIN", "slack_token_shape_without_online_validation"
    )
