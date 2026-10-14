from urllib.parse import quote

from secret_history.detectors import CATEGORIES


def as_sarif(report):
    rules = [{"id": name, "name": category.replace(" ", ""), "shortDescription": {"text": category}}
             for name, category in CATEGORIES.items()]
    results = []
    for row in report["candidates"]:
        if row["status"] == "NON_SECRET":
            continue
        region = {"startLine": row["line_start"], "endLine": row["line_end"]}
        if len(row["components"]) == 1 and "column" in row["components"][0]:
            region["startColumn"] = row["components"][0]["column"]
        results.append({
            "ruleId": row["detector"], "level": "warning",
            "message": {"text": row["reason"] + "; value [REDACTED]; validity UNKNOWN"},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": quote(row["path"], safe="/", errors="surrogatepass")}, "region": region}}],
            "partialFingerprints": {"secretHistory/location-v1": row["fingerprint"]},
            "properties": {"commit_oid": row["commit_oid"], "status": row["status"], "location_in_reference_snapshot": row["location_in_reference_snapshot"]},
        })
    complete = report["coverage"]["complete_for_scope"]
    invocation = {"executionSuccessful": complete}
    if not complete:
        invocation["toolExecutionNotifications"] = [{"level": "warning", "message": {"text": "Scan coverage is incomplete. Inspect companion JSON coverage."}}]
    return {"$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json", "version": "2.1.0", "runs": [{
        "tool": {"driver": {"name": "secret-history", "version": report["scanner_version"], "rules": rules}},
        "invocations": [invocation], "results": results,
        "properties": {"reference_snapshot_oid": report["reference_snapshot_oid"], "scope": report["scope"]},
    }]}
