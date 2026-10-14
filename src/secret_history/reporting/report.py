import csv
import hashlib
import io
import json

from secret_history.baselines.aws_rules import Decision
from secret_history.candidates.aws import Candidate
from secret_history.features.aws import numeric_features
from secret_history.detectors import CATEGORIES
from secret_history.reporting.redaction import safe_path


FINGERPRINT_SCHEME = "location-v1"


def fingerprint(record: dict) -> str:
    components = [{"field": item["field"], "line": item["line"], "masked_value": item["masked_value"]}
                  for item in record["components"]]
    for component, item in zip(components, record["components"]):
        if "column" in item:
            component["column"] = item["column"]
    if any(item["masked_value"] not in ("[REDACTED]", "[EMPTY]") for item in components):
        raise ValueError("Fingerprint requires fully masked values.")
    payload = {
        "scheme": FINGERPRINT_SCHEME,
        "path": record["path"],
        "commit_oid": record["commit_oid"],
        "line_start": record["line_start"],
        "line_end": record["line_end"],
        "components": sorted(components, key=lambda item: (item["line"], item["field"])),
    }
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def candidate_record(candidate: Candidate, decision: Decision, path: str, commit_oid: str) -> dict:
    record = {
        "path": safe_path(path, (b.value for b in candidate.bindings)),
        "commit_oid": commit_oid,
        "category": CATEGORIES[candidate.detector],
        "detector": candidate.detector,
        "kind": candidate.kind,
        "line_start": min(b.line for b in candidate.bindings),
        "line_end": max(b.end_line or b.line for b in candidate.bindings),
        "components": [{"field": b.name, "line": b.line, "masked_value": "[REDACTED]" if b.value else "[EMPTY]"}
                       for b in candidate.bindings],
        "status": decision.status,
        "reason": decision.reason,
        "activity_status": "UNKNOWN",
        "features": numeric_features(candidate) if candidate.detector == "aws" else {"length": sum(len(b.value) for b in candidate.bindings)},
    }
    for component, binding in zip(record["components"], candidate.bindings):
        if binding.column is not None:
            component["column"] = binding.column
    record["fingerprint"] = fingerprint(record)
    return record


def as_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=True, indent=2) + "\n"


def as_csv(report: dict) -> str:
    stream = io.StringIO(newline="")
    columns = ["path_json", "commit_oid", "blob_oid", "line_start", "line_end", "kind", "status", "reason",
               "fingerprint", "commits_json", "absent_from_reference_env", "activity_status",
               "components_json"]
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    for row in report["candidates"]:
        writer.writerow({
            "path_json": json.dumps(row["path"], ensure_ascii=True),
            "commit_oid": row["commit_oid"],
            "blob_oid": row["blob_oid"], "line_start": row["line_start"], "line_end": row["line_end"],
            "kind": row["kind"], "status": row["status"], "reason": row["reason"],
            "fingerprint": row["fingerprint"], "commits_json": json.dumps(row["commits"]),
            "absent_from_reference_env": row["absent_from_reference_env"],
            "activity_status": row["activity_status"], "components_json": json.dumps(row["components"]),
        })
    return stream.getvalue()
