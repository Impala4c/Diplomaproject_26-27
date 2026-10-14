from collections import Counter
from math import log2

from secret_history.candidates.aws import Candidate, ID_FIELD, SECRET_FIELD


def entropy(value: str) -> float:
    if not value:
        return 0.0
    return -sum((count / len(value)) * log2(count / len(value)) for count in Counter(value).values())


def numeric_features(candidate: Candidate) -> dict[str, int | float]:
    values = {b.name: b.value for b in candidate.bindings}
    result: dict[str, int | float] = {
        "has_id": int(ID_FIELD in values),
        "has_secret": int(SECRET_FIELD in values),
        "line_distance": max(b.line for b in candidate.bindings) - min(b.line for b in candidate.bindings),
        "commented_bindings": sum(b.commented for b in candidate.bindings),
        "ambiguous": int(candidate.ambiguous),
    }
    for name, label in ((ID_FIELD, "id"), (SECRET_FIELD, "secret")):
        value = values.get(name, "")
        result[f"{label}_length"] = len(value)
        result[f"{label}_entropy"] = round(entropy(value), 4)
    return result
