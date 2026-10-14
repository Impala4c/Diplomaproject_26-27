
from dataclasses import dataclass, field
import re

ID_FIELD = "AWS_ACCESS_KEY_ID"
SECRET_FIELD = "AWS_SECRET_ACCESS_KEY"
ASSIGNMENT = re.compile(
    r"^\s*(?P<comment>#\s*)?(?:export\s+)?"
    r"(?P<name>AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY)\s*=\s*(?P<rhs>.*)$"
)


@dataclass(frozen=True)
class Binding:
    name: str
    value: str = field(repr=False)
    line: int
    commented: bool = False
    end_line: int | None = None
    column: int | None = None


@dataclass(frozen=True)
class Candidate:
    bindings: tuple[Binding, ...]
    ambiguous: bool = False
    context: str = field(default="", repr=False)
    detector: str = "aws"

    @property
    def kind(self) -> str:
        if self.detector != "aws":
            return self.detector
        return "aws_pair" if len(self.bindings) == 2 else "aws_component"


@dataclass(frozen=True)
class ParseWarning:
    line: int
    reason: str


def parse_value(rhs: str) -> str | None:
    rhs = rhs.strip()
    if not rhs or rhs.startswith("#"):
        return ""
    if rhs[0] in "\"'":
        quote = rhs[0]
        end = rhs.find(quote, 1)
        if end < 0:
            return None
        tail = rhs[end + 1:].strip()
        value = rhs[1:end]
        if (tail and not tail.startswith("#")) or "\\" in value:
            return None
        return value
    value = re.split(r"\s+#", rhs, maxsplit=1)[0].strip()
    if any(char.isspace() for char in value) or "\\" in value:
        return None
    return value


def extract_aws(text: str) -> tuple[list[Candidate], list[ParseWarning]]:
    bindings: list[Binding] = []
    warnings: list[ParseWarning] = []
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        match = ASSIGNMENT.match(line)
        if not match:
            continue
        value = parse_value(match["rhs"])
        if value is None:
            warnings.append(ParseWarning(number, "unsupported_env_assignment"))
        else:
            bindings.append(Binding(match["name"], value, number, bool(match["comment"])))

    def candidate(group: tuple[Binding, ...], ambiguous: bool = False) -> Candidate:
        start, end = min(b.line for b in group), max(b.line for b in group)
        context = "\n".join(lines[max(0, start - 3):end + 2])
        return Candidate(group, ambiguous, context)

    ids = [b for b in bindings if b.name == ID_FIELD]
    secrets = [b for b in bindings if b.name == SECRET_FIELD]
    if len(ids) == len(secrets) == 1 and not warnings:
        mixed = ids[0].commented != secrets[0].commented
        return [candidate((ids[0], secrets[0]), mixed)], warnings
    ambiguous = len(ids) > 1 or len(secrets) > 1 or bool(warnings)
    return [candidate((binding,), ambiguous) for binding in bindings], warnings
